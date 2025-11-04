#!/usr/bin/env python3
"""
Script de Reestructuración del Modelo de Datos (VERSIÓN PARA DATOS LIMPIOS)
Lee desde la colección 'invoices' que ya fue limpiada con limpieza.txt
Transforma en tres colecciones especializadas:
- movies: Información de películas
- series: Información de series y temporadas
- invoices_restructured: Facturas simplificadas con referencias
"""

from pymongo import MongoClient, ASCENDING
from bson import ObjectId, Decimal128
from datetime import datetime
from collections import defaultdict

# Configuración de MongoDB
MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "streamit_db"  # ⚠️ Ajusta al nombre de tu base de datos
SOURCE_COLLECTION = "invoices"  # Ya limpia con camelCase
MOVIES_COLLECTION = "movies"
SERIES_COLLECTION = "series"
INVOICES_COLLECTION = "invoices_restructured"


class DataRestructurer:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DATABASE_NAME]
        self.invoices_source = self.db[SOURCE_COLLECTION]
        self.movies_collection = self.db[MOVIES_COLLECTION]
        self.series_collection = self.db[SERIES_COLLECTION]
        self.invoices_new = self.db[INVOICES_COLLECTION]
        
        # Diccionarios para mapear contenido original → ObjectId nuevo
        self.movies_map = {}
        self.series_map = {}
        
        print("=" * 80)
        print("REESTRUCTURACIÓN DEL MODELO DE DATOS".center(80))
        print("=" * 80)
        print()

    def normalize_string(self, text):
        """Normaliza strings: trim, capitalización consistente"""
        if not text:
            return ""
        
        text = str(text).strip()
        return ' '.join(word.capitalize() for word in text.split())

    def extract_movies(self):
        """Extrae y deduplica películas de las facturas"""
        print("\n📽️  PASO 1: EXTRAYENDO PELÍCULAS")
        print("-" * 80)
        
        movies_dict = {}
        
        # ⚠️ CAMBIO: Usar "Movies" con mayúscula (como está en los datos limpios)
        # Si después de la limpieza quedó en minúsculas, usar "movies"
        invoices = self.invoices_source.find({"Movies": {"$exists": True, "$ne": []}})
        total_invoices = self.invoices_source.count_documents({"Movies": {"$exists": True, "$ne": []}})
        
        processed = 0
        for invoice in invoices:
            processed += 1
            if processed % 1000 == 0:
                print(f"   Procesando factura {processed}/{total_invoices}...")
            
            # ⚠️ CAMBIO: Los campos ya están en camelCase
            for movie in invoice.get("Movies", []):
                title = self.normalize_string(movie.get("title", ""))
                
                if not title:
                    continue
                
                movie_key = title.lower()
                
                if movie_key not in movies_dict:
                    # ⚠️ CAMBIO: details ya está limpio y estructurado
                    details_raw = movie.get("details", {})
                    
                    # Parsear director y cast (mantener estructura original)
                    director_info = details_raw.get("director", {})
                    director_name = director_info.get("name", "") if isinstance(director_info, dict) else str(director_info)
                    
                    cast_list = []
                    cast_raw = details_raw.get("cast", {})
                    if isinstance(cast_raw, dict):
                        stars = cast_raw.get("stars", [])
                        if isinstance(stars, list):
                            for star in stars:
                                if isinstance(star, dict):
                                    cast_list.append(star.get("name", ""))
                                elif isinstance(star, str):
                                    cast_list.append(star)
                    
                    # Crear documento de película
                    movie_doc = {
                        "title": title,
                        "details": {
                            "director": self.normalize_string(director_name),
                            "cast": [self.normalize_string(name) for name in cast_list if name],
                            "genre": [self.normalize_string(g) for g in details_raw.get("genre", [])],
                            "keywords": [self.normalize_string(k) for k in details_raw.get("keywords", [])],
                            "languages": [self.normalize_string(lang) for lang in details_raw.get("languages", [])],
                            "country": self.normalize_string(details_raw.get("country", "")),
                            "rating": details_raw.get("rating", ""),
                            "income": details_raw.get("income", 0),  # Ya debería estar limpio
                            "filmingLocations": [self.normalize_string(loc) for loc in details_raw.get("filmingLocations", [])],
                            "releaseDate": details_raw.get("releaseDate")  # Ya debería ser ISODate
                        },
                        "duration": int(details_raw.get("duration", 0)) if details_raw.get("duration") else 0,
                        "_metadata": {
                            "createdAt": datetime.utcnow(),
                            "version": "1.0"
                        }
                    }
                    
                    movies_dict[movie_key] = movie_doc
        
        print(f"\n✅ Películas únicas encontradas: {len(movies_dict)}")
        
        # Insertar en la colección Movies
        if movies_dict:
            print("   Insertando en colección 'movies'...")
            result = self.movies_collection.insert_many(list(movies_dict.values()))
            
            # Mapear títulos → ObjectId
            for movie_key, movie_doc in movies_dict.items():
                movie_id = result.inserted_ids[list(movies_dict.keys()).index(movie_key)]
                self.movies_map[movie_key] = movie_id
            
            print(f"✅ {len(result.inserted_ids)} películas insertadas")
        
        return len(movies_dict)

    def extract_series(self):
        """Extrae y deduplica series de las facturas"""
        print("\n📺 PASO 2: EXTRAYENDO SERIES Y TEMPORADAS")
        print("-" * 80)
        
        series_dict = {}
        
        # ⚠️ CAMBIO: Usar "Series" con mayúscula
        invoices = self.invoices_source.find({"Series": {"$exists": True, "$ne": []}})
        total_invoices = self.invoices_source.count_documents({"Series": {"$exists": True, "$ne": []}})
        
        processed = 0
        for invoice in invoices:
            processed += 1
            if processed % 1000 == 0:
                print(f"   Procesando factura {processed}/{total_invoices}...")
            
            # ⚠️ CAMBIO: Los campos ya están en camelCase
            for series in invoice.get("Series", []):
                title = self.normalize_string(series.get("title", ""))
                
                if not title:
                    continue
                
                series_key = title.lower()
                
                if series_key not in series_dict:
                    # Crear documento de serie
                    series_doc = {
                        "title": title,
                        "totalSeasons": int(series.get("totalSeasons", 0)),
                        "totalEpisodes": int(series.get("totalEpisodes", 0)),
                        "avgDuration": int(series.get("avgDuration", 0)),
                        "_metadata": {
                            "createdAt": datetime.utcnow(),
                            "version": "1.0"
                        }
                    }
                    
                    series_dict[series_key] = series_doc
        
        print(f"\n✅ Series únicas encontradas: {len(series_dict)}")
        
        # Insertar en la colección Series
        if series_dict:
            print("   Insertando en colección 'series'...")
            result = self.series_collection.insert_many(list(series_dict.values()))
            
            # Mapear títulos → ObjectId
            for series_key, series_doc in series_dict.items():
                series_id = result.inserted_ids[list(series_dict.keys()).index(series_key)]
                self.series_map[series_key] = series_id
            
            print(f"✅ {len(result.inserted_ids)} series insertadas")
        
        return len(series_dict)

    def restructure_invoices(self):
        """Reestructura las facturas con referencias a Movies y Series"""
        print("\n🧾 PASO 3: REESTRUCTURANDO FACTURAS")
        print("-" * 80)
        
        invoices = self.invoices_source.find()
        total = self.invoices_source.count_documents({})
        
        batch = []
        batch_size = 500
        processed = 0
        
        for invoice in invoices:
            processed += 1
            
            if processed % 1000 == 0:
                print(f"   Procesando factura {processed}/{total}...")
            
            # ⚠️ CAMBIO: Los nombres de campos ya están en camelCase
            client_data = invoice.get("Client", {})
            contract_data = invoice.get("contract", {})
            product_data = contract_data.get("product", {})
            
            # Construir documento simplificado
            new_invoice = {
                "_id": invoice["_id"],
                "client": {
                    "customerCode": client_data.get("customerCode"),
                    "name": client_data.get("name"),
                    "surname": client_data.get("surname"),
                    "email": client_data.get("email"),
                    "phone": client_data.get("phone"),
                    "dni": client_data.get("dni"),
                    "birthDate": client_data.get("birthDate")
                },
                "contract": {
                    "contractId": contract_data.get("contractId"),
                    "startDate": contract_data.get("startDate"),
                    "endDate": contract_data.get("endDate"),
                    "address": contract_data.get("address"),
                    "zip": contract_data.get("zip"),
                    "town": contract_data.get("town"),
                    "country": contract_data.get("country"),
                    "product": {
                        "reference": product_data.get("reference"),
                        "type": product_data.get("type"),
                        "monthlyFee": product_data.get("monthlyFee"),
                        "costPerDay": product_data.get("costPerDay"),
                        "costPerMinute": product_data.get("costPerMinute"),
                        "costPerContent": product_data.get("costPerContent"),
                        "zapping": product_data.get("zapping", False),
                        "promotion": product_data.get("promotion", "")
                    }
                },
                "billing": invoice.get("billing"),
                "chargeDate": invoice.get("chargeDate"),
                "dumpDate": invoice.get("dumpDate"),
                "total": invoice.get("total"),
                "movies": [],
                "series": [],
                "_metadata": {
                    "restructuredAt": datetime.utcnow(),
                    "version": "2.0"
                }
            }
            
            # Agregar referencias a películas
            for movie in invoice.get("Movies", []):
                title = self.normalize_string(movie.get("title", ""))
                movie_key = title.lower()
                
                if movie_key in self.movies_map:
                    movie_ref = {
                        "movieId": self.movies_map[movie_key],
                        "date": movie.get("date"),  # Ya debería ser ISODate
                        "time": movie.get("time"),  # Ya debería estar limpio
                        "viewingPct": movie.get("viewingPct", 0.0),  # Ya debería ser decimal
                        "license": movie.get("license", "")
                    }
                    new_invoice["movies"].append(movie_ref)
            
            # Agregar referencias a series
            for series in invoice.get("Series", []):
                title = self.normalize_string(series.get("title", ""))
                series_key = title.lower()
                
                if series_key in self.series_map:
                    series_ref = {
                        "seriesId": self.series_map[series_key],
                        "season": int(series.get("season", 0)),
                        "episode": int(series.get("episode", 0)),
                        "date": series.get("date"),  # Ya debería ser ISODate
                        "time": series.get("time"),
                        "viewingPct": series.get("viewingPct", 0.0),
                        "license": series.get("license", "")
                    }
                    new_invoice["series"].append(series_ref)
            
            batch.append(new_invoice)
            
            # Insertar en lotes
            if len(batch) >= batch_size:
                self.invoices_new.insert_many(batch)
                batch = []
        
        # Insertar últimos documentos
        if batch:
            self.invoices_new.insert_many(batch)
        
        print(f"\n✅ {processed} facturas reestructuradas")

    def create_indexes(self):
        """Crea índices en las nuevas colecciones"""
        print("\n🔍 PASO 4: CREANDO ÍNDICES")
        print("-" * 80)
        
        # Índices en Movies
        print("   Creando índices en 'movies'...")
        self.movies_collection.create_index([("title", ASCENDING)], unique=True)
        self.movies_collection.create_index([("details.genre", ASCENDING)])
        self.movies_collection.create_index([("details.releaseDate", ASCENDING)])
        print("   ✓ 3 índices creados en 'movies'")
        
        # Índices en Series
        print("   Creando índices en 'series'...")
        self.series_collection.create_index([("title", ASCENDING)], unique=True)
        self.series_collection.create_index([("totalSeasons", ASCENDING)])
        print("   ✓ 2 índices creados en 'series'")
        
        # Índices en Invoices
        print("   Creando índices en 'invoices_restructured'...")
        self.invoices_new.create_index([("client.customerCode", ASCENDING)])
        self.invoices_new.create_index([("contract.contractId", ASCENDING)])
        self.invoices_new.create_index([("chargeDate", ASCENDING)])
        self.invoices_new.create_index([("billing", ASCENDING)])
        self.invoices_new.create_index([("movies.movieId", ASCENDING)])
        self.invoices_new.create_index([("series.seriesId", ASCENDING)])
        self.invoices_new.create_index([("client.customerCode", ASCENDING), ("chargeDate", ASCENDING)])
        print("   ✓ 7 índices creados en 'invoices_restructured'")

    def validate_restructuring(self):
        """Valida la reestructuración"""
        print("\n✔️  PASO 5: VALIDACIÓN")
        print("-" * 80)
        
        # Contar documentos
        movies_count = self.movies_collection.count_documents({})
        series_count = self.series_collection.count_documents({})
        invoices_count = self.invoices_new.count_documents({})
        original_count = self.invoices_source.count_documents({})
        
        print(f"   Películas únicas: {movies_count}")
        print(f"   Series únicas: {series_count}")
        print(f"   Facturas reestructuradas: {invoices_count}")
        print(f"   Facturas originales: {original_count}")
        
        if invoices_count == original_count:
            print("\n   ✅ Validación exitosa: Todas las facturas fueron procesadas")
        else:
            print(f"\n   ⚠️  Advertencia: Diferencia de {original_count - invoices_count} facturas")
        
        # Verificar referencias
        sample_invoice = self.invoices_new.find_one({"movies": {"$ne": []}})
        if sample_invoice:
            movie_id = sample_invoice["movies"][0]["movieId"]
            movie_exists = self.movies_collection.find_one({"_id": movie_id})
            
            if movie_exists:
                print("   ✅ Referencias a películas verificadas")
            else:
                print("   ⚠️  Error: Referencias rotas en películas")

    def generate_report(self):
        """Genera reporte final"""
        print("\n" + "=" * 80)
        print("RESUMEN DE REESTRUCTURACIÓN".center(80))
        print("=" * 80)
        
        movies_count = self.movies_collection.count_documents({})
        series_count = self.series_collection.count_documents({})
        invoices_count = self.invoices_new.count_documents({})
        
        # Calcular reducción de tamaño
        original_size = self.db.command("collstats", SOURCE_COLLECTION)["size"]
        new_size = (
            self.db.command("collstats", MOVIES_COLLECTION)["size"] +
            self.db.command("collstats", SERIES_COLLECTION)["size"] +
            self.db.command("collstats", INVOICES_COLLECTION)["size"]
        )
        
        reduction_pct = ((original_size - new_size) / original_size) * 100 if original_size > 0 else 0
        
        print(f"\n📊 ESTADÍSTICAS:")
        print(f"   • Películas únicas: {movies_count:,}")
        print(f"   • Series únicas: {series_count:,}")
        print(f"   • Facturas reestructuradas: {invoices_count:,}")
        print(f"\n💾 OPTIMIZACIÓN DE ALMACENAMIENTO:")
        print(f"   • Tamaño original: {original_size / 1024 / 1024:.2f} MB")
        print(f"   • Tamaño nuevo: {new_size / 1024 / 1024:.2f} MB")
        print(f"   • Reducción: {reduction_pct:.1f}%")
        
        print(f"\n🎯 BENEFICIOS:")
        print(f"   ✓ Eliminación de redundancia")
        print(f"   ✓ Modelo normalizado y escalable")
        print(f"   ✓ Consultas más eficientes")
        print(f"   ✓ Facilita análisis de contenido")
        print(f"   ✓ Preparado para métricas de consumo")

    def run(self):
        """Ejecuta el proceso completo de reestructuración"""
        start_time = datetime.now()
        
        try:
            # Verificar que la colección origen existe
            if SOURCE_COLLECTION not in self.db.list_collection_names():
                print(f"❌ ERROR: La colección '{SOURCE_COLLECTION}' no existe en la base de datos '{DATABASE_NAME}'")
                print("   Asegúrate de haber ejecutado el script de limpieza primero.")
                return
            
            # Limpiar colecciones destino si existen
            print("\n🗑️  Limpiando colecciones destino...")
            self.movies_collection.drop()
            self.series_collection.drop()
            self.invoices_new.drop()
            print("   ✓ Colecciones limpias\n")
            
            # Ejecutar pasos
            self.extract_movies()
            self.extract_series()
            self.restructure_invoices()
            self.create_indexes()
            self.validate_restructuring()
            self.generate_report()
            
            elapsed = datetime.now() - start_time
            print(f"\n⏱️  Tiempo total: {elapsed.total_seconds():.2f} segundos")
            print("\n" + "=" * 80)
            print("REESTRUCTURACIÓN COMPLETADA EXITOSAMENTE".center(80))
            print("=" * 80 + "\n")
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.client.close()


if __name__ == "__main__":
    restructurer = DataRestructurer()
    restructurer.run()