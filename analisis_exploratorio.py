#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis Exploratorio de Datos (EDA) - Sistema de Facturas
Autor: Análisis de Calidad de Datos
Fecha: 2024
Descripción: Script para identificar problemas de calidad en los datos antes de la importación
"""

import json
import os
from collections import defaultdict, Counter
from datetime import datetime
import re

class DataExplorer:
    def __init__(self, data_directory):
        self.data_directory = data_directory
        self.all_documents = []
        self.quality_issues = {
            'duplicados': [],
            'valores_ausentes': defaultdict(list),
            'formatos_fecha': defaultdict(set),
            'inconsistencias_estructura': [],
            'valores_anomalos': [],
            'tipos_datos_mixtos': defaultdict(set)
        }
    
    def parse_multi_json_file(self, content):
        """
        Parser personalizado para archivos con múltiples objetos JSON separados
        """
        documents = []
        
        # Estrategia 1: Intentar como array JSON estándar
        try:
            data = json.loads(content)
            if isinstance(data, list):
                return data
            else:
                return [data]
        except json.JSONDecodeError:
            pass
        
        # Estrategia 2: Separar por objetos JSON individuales
        # Buscar patrones de inicio de objeto JSON
        brace_count = 0
        current_obj = ""
        in_string = False
        escape_next = False
        
        for char in content:
            if escape_next:
                current_obj += char
                escape_next = False
                continue
                
            if char == '\\':
                escape_next = True
                current_obj += char
                continue
            
            if char == '"' and not escape_next:
                in_string = not in_string
            
            if not in_string:
                if char == '{':
                    if brace_count == 0:
                        current_obj = ""
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
            
            current_obj += char
            
            # Cuando cerramos un objeto completo
            if brace_count == 0 and current_obj.strip():
                try:
                    obj = json.loads(current_obj.strip())
                    documents.append(obj)
                    current_obj = ""
                except json.JSONDecodeError as e:
                    # Intentar limpiar y parsear de nuevo
                    cleaned = current_obj.strip()
                    if cleaned:
                        try:
                            obj = json.loads(cleaned)
                            documents.append(obj)
                        except:
                            pass
                    current_obj = ""
        
        return documents
    
    def load_all_files(self):
        """Carga todos los archivos JSON del directorio con manejo robusto"""
        print("=" * 80)
        print("CARGANDO ARCHIVOS JSON")
        print("=" * 80)
        
        json_files = sorted([f for f in os.listdir(self.data_directory) if f.endswith('.json')])
        
        # Lista de encodings a probar en orden
        encodings_to_try = ['utf-8', 'latin-1', 'iso-8859-1', 'windows-1252', 'cp1252']
        
        for filename in json_files:
            filepath = os.path.join(self.data_directory, filename)
            print(f"\n📁 Procesando: {filename}")
            
            content = None
            used_encoding = None
            
            # Intentar leer con diferentes encodings
            for encoding in encodings_to_try:
                try:
                    with open(filepath, 'r', encoding=encoding, errors='replace') as f:
                        content = f.read()
                        used_encoding = encoding
                        break
                except Exception as e:
                    continue
            
            if content is None:
                print(f"   ✗ ERROR: No se pudo leer el archivo con ningún encoding")
                continue
            
            # Parsear los documentos JSON
            try:
                documents = self.parse_multi_json_file(content)
                
                if documents:
                    self.all_documents.extend(documents)
                    print(f"   ✓ Cargados {len(documents)} documentos (encoding: {used_encoding})")
                else:
                    print(f"   ⚠️  No se encontraron documentos válidos en el archivo")
                    
            except Exception as e:
                print(f"   ✗ ERROR al parsear: {e}")
        
        print(f"\n{'='*80}")
        print(f"TOTAL DE DOCUMENTOS CARGADOS: {len(self.all_documents)}")
        print(f"{'='*80}\n")
        
    def analyze_ids(self):
        """Analiza los identificadores únicos"""
        print("\n" + "=" * 80)
        print("1. ANÁLISIS DE IDENTIFICADORES (_id)")
        print("=" * 80)
        
        ids = []
        ids_sin_campo = 0
        formatos_id = defaultdict(int)
        
        for idx, doc in enumerate(self.all_documents):
            if '_id' not in doc:
                ids_sin_campo += 1
                self.quality_issues['valores_ausentes']['_id'].append(idx)
            else:
                id_val = doc['_id']
                ids.append(id_val)
                
                # Analizar formato del ID
                if isinstance(id_val, str):
                    patron = re.sub(r'\d+', 'N', id_val)
                    formatos_id[patron] += 1
        
        # Detectar duplicados
        id_counts = Counter(ids)
        duplicados = {id_val: count for id_val, count in id_counts.items() if count > 1}
        
        print(f"\n📊 Estadísticas de IDs:")
        print(f"   • Total de documentos: {len(self.all_documents)}")
        print(f"   • Documentos sin _id: {ids_sin_campo}")
        print(f"   • IDs únicos: {len(set(ids))}")
        print(f"   • IDs duplicados: {len(duplicados)}")
        
        if duplicados:
            print(f"\n⚠️  PROBLEMA: IDs DUPLICADOS DETECTADOS")
            for id_val, count in list(duplicados.items())[:5]:
                print(f"      - '{id_val}': {count} veces")
                self.quality_issues['duplicados'].append(id_val)
            if len(duplicados) > 5:
                print(f"      ... y {len(duplicados) - 5} más")
        
        print(f"\n📋 Formatos de ID encontrados:")
        for patron, count in sorted(formatos_id.items(), key=lambda x: -x[1])[:10]:
            print(f"   • {patron}: {count} documentos")
    
    def analyze_dates(self):
        """Analiza todos los campos de fecha"""
        print("\n" + "=" * 80)
        print("2. ANÁLISIS DE FECHAS")
        print("=" * 80)
        
        date_fields = ['charge date', 'dump date', 'billing']
        
        for field in date_fields:
            print(f"\n📅 Campo: '{field}'")
            formatos = defaultdict(int)
            valores_ausentes = 0
            ejemplos = []
            
            for idx, doc in enumerate(self.all_documents):
                if field not in doc:
                    valores_ausentes += 1
                    self.quality_issues['valores_ausentes'][field].append(idx)
                else:
                    valor = doc[field]
                    if valor is None:
                        valores_ausentes += 1
                    else:
                        formato = self._detect_date_format(valor)
                        formatos[formato] += 1
                        self.quality_issues['formatos_fecha'][field].add(formato)
                        
                        if len(ejemplos) < 3:
                            ejemplos.append(valor)
            
            print(f"   • Valores ausentes/nulos: {valores_ausentes}")
            print(f"   • Formatos detectados: {len(formatos)}")
            
            if formatos:
                print(f"   • Distribución de formatos:")
                for formato, count in sorted(formatos.items(), key=lambda x: -x[1]):
                    print(f"      - {formato}: {count} documentos")
            
            if ejemplos:
                print(f"   • Ejemplos: {ejemplos}")
            
            if len(formatos) > 1:
                print(f"   ⚠️  PROBLEMA: Formatos de fecha heterogéneos")
    
    def analyze_client_structure(self):
        """Analiza la estructura del cliente"""
        print("\n" + "=" * 80)
        print("3. ANÁLISIS DE ESTRUCTURA - CLIENT")
        print("=" * 80)
        
        client_fields = set()
        field_types = defaultdict(lambda: defaultdict(int))
        missing_client = 0
        
        for idx, doc in enumerate(self.all_documents):
            if 'Client' not in doc:
                missing_client += 1
                self.quality_issues['valores_ausentes']['Client'].append(idx)
            elif doc['Client'] is None:
                missing_client += 1
            else:
                client = doc['Client']
                if isinstance(client, dict):
                    client_fields.update(client.keys())
                    
                    for key, value in client.items():
                        tipo = type(value).__name__
                        field_types[key][tipo] += 1
                else:
                    self.quality_issues['inconsistencias_estructura'].append(
                        f"Doc {idx}: 'Client' no es un diccionario: {type(client).__name__}"
                    )
        
        print(f"\n📊 Estadísticas de Client:")
        print(f"   • Documentos sin Client: {missing_client}")
        print(f"   • Campos únicos encontrados: {len(client_fields)}")
        
        print(f"\n📋 Campos en Client:")
        for field in sorted(client_fields):
            print(f"   • {field}")
            tipos = field_types[field]
            if len(tipos) > 1:
                print(f"      ⚠️  PROBLEMA: Tipos mixtos detectados")
                for tipo, count in tipos.items():
                    print(f"         - {tipo}: {count} documentos")
                self.quality_issues['tipos_datos_mixtos'][f'Client.{field}'].update(tipos.keys())
    
    def analyze_contract_structure(self):
        """Analiza la estructura del contrato"""
        print("\n" + "=" * 80)
        print("4. ANÁLISIS DE ESTRUCTURA - CONTRACT")
        print("=" * 80)
        
        contract_fields = set()
        product_fields = set()
        missing_contract = 0
        missing_product = 0
        
        for idx, doc in enumerate(self.all_documents):
            if 'contract' not in doc:
                missing_contract += 1
                self.quality_issues['valores_ausentes']['contract'].append(idx)
            elif doc['contract'] is None:
                missing_contract += 1
            else:
                contract = doc['contract']
                if isinstance(contract, dict):
                    contract_fields.update(contract.keys())
                    
                    if 'product' in contract:
                        product = contract['product']
                        if isinstance(product, dict):
                            product_fields.update(product.keys())
                        elif product is None:
                            missing_product += 1
                    else:
                        missing_product += 1
        
        print(f"\n📊 Estadísticas de Contract:")
        print(f"   • Documentos sin contract: {missing_contract}")
        print(f"   • Campos únicos en contract: {len(contract_fields)}")
        print(f"   • Documentos sin product: {missing_product}")
        print(f"   • Campos únicos en product: {len(product_fields)}")
        
        print(f"\n📋 Campos en Contract:")
        for field in sorted(contract_fields):
            print(f"   • {field}")
        
        if product_fields:
            print(f"\n📋 Campos en Product:")
            for field in sorted(product_fields):
                print(f"   • {field}")
    
    def analyze_movies_series(self):
        """Analiza la estructura de películas y series"""
        print("\n" + "=" * 80)
        print("5. ANÁLISIS DE CONTENIDOS - MOVIES & SERIES")
        print("=" * 80)
        
        total_movies = 0
        total_series = 0
        docs_sin_movies = 0
        docs_sin_series = 0
        
        movie_fields = set()
        series_fields = set()
        
        for idx, doc in enumerate(self.all_documents):
            if 'Movies' not in doc:
                docs_sin_movies += 1
            elif doc['Movies'] is None:
                docs_sin_movies += 1
            else:
                movies = doc['Movies']
                if isinstance(movies, list):
                    total_movies += len(movies)
                    for movie in movies:
                        if isinstance(movie, dict):
                            movie_fields.update(movie.keys())
            
            if 'Series' not in doc:
                docs_sin_series += 1
            elif doc['Series'] is None:
                docs_sin_series += 1
            else:
                series = doc['Series']
                if isinstance(series, list):
                    total_series += len(series)
                    for serie in series:
                        if isinstance(serie, dict):
                            series_fields.update(serie.keys())
        
        print(f"\n🎬 Estadísticas de Movies:")
        print(f"   • Documentos sin Movies: {docs_sin_movies}")
        print(f"   • Total de películas: {total_movies}")
        if (len(self.all_documents) - docs_sin_movies) > 0:
            print(f"   • Promedio por documento: {total_movies / (len(self.all_documents) - docs_sin_movies):.2f}")
        print(f"   • Campos únicos: {len(movie_fields)}")
        
        print(f"\n📺 Estadísticas de Series:")
        print(f"   • Documentos sin Series: {docs_sin_series}")
        print(f"   • Total de series: {total_series}")
        if (len(self.all_documents) - docs_sin_series) > 0:
            print(f"   • Promedio por documento: {total_series / (len(self.all_documents) - docs_sin_series):.2f}")
        print(f"   • Campos únicos: {len(series_fields)}")
        
        if movie_fields:
            print(f"\n📋 Campos en Movies:")
            for field in sorted(movie_fields):
                print(f"   • {field}")
        
        if series_fields:
            print(f"\n📋 Campos en Series:")
            for field in sorted(series_fields):
                print(f"   • {field}")
    
    def analyze_numeric_fields(self):
        """Analiza campos numéricos y detecta anomalías"""
        print("\n" + "=" * 80)
        print("6. ANÁLISIS DE CAMPOS NUMÉRICOS")
        print("=" * 80)
        
        numeric_fields = ['TOTAL']
        
        for field in numeric_fields:
            print(f"\n💰 Campo: '{field}'")
            valores = []
            tipos = defaultdict(int)
            ausentes = 0
            
            for idx, doc in enumerate(self.all_documents):
                if field not in doc:
                    ausentes += 1
                elif doc[field] is None:
                    ausentes += 1
                else:
                    valor = doc[field]
                    tipos[type(valor).__name__] += 1
                    
                    try:
                        num_val = float(valor)
                        valores.append(num_val)
                    except (ValueError, TypeError):
                        self.quality_issues['valores_anomalos'].append(
                            f"{field} en doc {idx}: valor no numérico '{valor}'"
                        )
            
            print(f"   • Valores ausentes: {ausentes}")
            print(f"   • Tipos de datos encontrados:")
            for tipo, count in tipos.items():
                print(f"      - {tipo}: {count}")
            
            if valores:
                print(f"   • Estadísticas:")
                print(f"      - Mínimo: {min(valores):.2f}")
                print(f"      - Máximo: {max(valores):.2f}")
                print(f"      - Promedio: {sum(valores)/len(valores):.2f}")
                
                negativos = [v for v in valores if v < 0]
                ceros = [v for v in valores if v == 0]
                
                if negativos:
                    print(f"   ⚠️  ADVERTENCIA: {len(negativos)} valores negativos")
                if ceros:
                    print(f"   ⚠️  ADVERTENCIA: {len(ceros)} valores en cero")
    
    def generate_summary_report(self):
        """Genera un resumen de problemas detectados"""
        print("\n" + "=" * 80)
        print("7. RESUMEN DE PROBLEMAS DE CALIDAD DETECTADOS")
        print("=" * 80)
        
        print("\n🔴 PROBLEMAS CRÍTICOS:")
        
        if self.quality_issues['duplicados']:
            print(f"\n   1. IDs DUPLICADOS")
            print(f"      • Total: {len(self.quality_issues['duplicados'])}")
            print(f"      • Acción requerida: Decidir estrategia de deduplicación")
        
        print(f"\n   2. VALORES AUSENTES")
        for field, docs in self.quality_issues['valores_ausentes'].items():
            if docs:
                print(f"      • {field}: {len(docs)} documentos")
        print(f"      • Acción requerida: Definir valores por defecto o eliminar")
        
        print(f"\n   3. FORMATOS DE FECHA HETEROGÉNEOS")
        for field, formatos in self.quality_issues['formatos_fecha'].items():
            if len(formatos) > 1:
                print(f"      • {field}: {len(formatos)} formatos diferentes")
                for fmt in formatos:
                    print(f"         - {fmt}")
        print(f"      • Acción requerida: Normalizar a formato ISO 8601")
        
        if self.quality_issues['tipos_datos_mixtos']:
            print(f"\n   4. TIPOS DE DATOS MIXTOS")
            for field, tipos in self.quality_issues['tipos_datos_mixtos'].items():
                print(f"      • {field}: {tipos}")
            print(f"      • Acción requerida: Convertir a tipo único")
        
        if self.quality_issues['inconsistencias_estructura']:
            print(f"\n   5. INCONSISTENCIAS ESTRUCTURALES")
            print(f"      • Total: {len(self.quality_issues['inconsistencias_estructura'])}")
            for issue in self.quality_issues['inconsistencias_estructura'][:5]:
                print(f"      • {issue}")
        
        if self.quality_issues['valores_anomalos']:
            print(f"\n   6. VALORES ANÓMALOS")
            print(f"      • Total: {len(self.quality_issues['valores_anomalos'])}")
            for anomaly in self.quality_issues['valores_anomalos'][:5]:
                print(f"      • {anomaly}")
        
        print("\n" + "=" * 80)
        print("RECOMENDACIONES PARA LIMPIEZA:")
        print("=" * 80)
        print("""
1. NORMALIZACIÓN DE FECHAS
   - Convertir todas las fechas a formato ISO 8601 (YYYY-MM-DD)
   - Usar $dateFromString con manejo de errores
   
2. GESTIÓN DE DUPLICADOS
   - Identificar criterio de unicidad real
   - Eliminar o consolidar duplicados
   
3. VALORES AUSENTES
   - Definir política de nulos por campo
   - Considerar valores por defecto cuando sea apropiado
   
4. NORMALIZACIÓN DE TIPOS
   - Convertir campos numéricos a números
   - Estandarizar strings (trim, lowercase donde aplique)
   
5. ESTRUCTURA DE DOCUMENTOS
   - Verificar anidamiento de objetos
   - Normalizar nombres de campos (camelCase vs snake_case)
        """)
    
    def _detect_date_format(self, date_value):
        """Detecta el formato de una fecha"""
        if not isinstance(date_value, str):
            return f"tipo_{type(date_value).__name__}"
        
        patterns = [
            (r'^\d{2}/\d{2}/\d{4}$', 'DD/MM/YYYY'),
            (r'^\d{2}/\d{2}/\d{2}$', 'DD/MM/YY'),
            (r'^\d{4}-\d{2}-\d{2}$', 'YYYY-MM-DD (ISO)'),
            (r'^[A-Za-z]+ \d{4}$', 'Month YYYY'),
            (r'^\d{2}/\d{2}/\d{2,4}$', 'DD/MM/YY(YY)'),
        ]
        
        for pattern, formato in patterns:
            if re.match(pattern, date_value):
                return formato
        
        return f"otro: '{date_value[:20]}...'" if len(date_value) > 20 else f"otro: '{date_value}'"
    
    def run_full_analysis(self):
        """Ejecuta el análisis completo"""
        self.load_all_files()
        
        if not self.all_documents:
            print("\n❌ No se pudieron cargar documentos. Verifica la ruta.")
            return
        
        self.analyze_ids()
        self.analyze_dates()
        self.analyze_client_structure()
        self.analyze_contract_structure()
        self.analyze_movies_series()
        self.analyze_numeric_fields()
        self.generate_summary_report()
        
        print("\n✅ Análisis exploratorio completado.")
        print(f"📄 Revisar este informe antes de proceder con la importación a MongoDB.\n")


if __name__ == "__main__":
    DATA_DIR = "./datafiles"
    
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                  ANÁLISIS EXPLORATORIO DE DATOS (EDA)                        ║
║                   Sistema de Facturas - MongoDB                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    explorer = DataExplorer(DATA_DIR)
    explorer.run_full_analysis()
