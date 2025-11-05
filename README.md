# Migración a MongoDB de acuerdo a Casos de Uso

## Requisitos 
### Instalar MongoDB Database Tools
Para Ubuntu/Debian
```bash
wget https://fastdl.mongodb.org/tools/db/mongodb-database-tools-ubuntu2204-x86_64-100.9.4.deb
sudo dpkg -i mongodb-database-tools-ubuntu2204-x86_64-100.9.4.deb

# Verificar instalación
mongoimport --version
```

### Instalar pymongo (para reestructuración)
```bash
pip install pymongo
```

---

## 1. Análisis Exploratorio de Datos

Ejecutar el siguiente comando:
```bash
python3 analisis_exploratorio.py
```
 
### Salida Esperada
El script generará un informe detallado con:
- Análisis de identificadores (_id)
- Formatos de fechas detectados
- Estructura de documentos (Client, Contract, Product)
- Estadísticas de contenido (Movies, Series)
- Problemas de calidad de datos
- Recomendaciones para limpieza

**Total de documentos**: 15,807

---

## 2. Importación de Datos a MongoDB

### 2.1 Conversión a Array JSON Válido
**Problema**: Los JSON originales contienen múltiples objetos separados (NDJSON)

**Solución**: Convertir a formato JSON array válido

```bash
cd ~/ruta_a_los_datos/
python3 convertir_json.py
```

Este script creará una carpeta `datafiles_converted/` con archivos JSON válidos listos para importar.

### 2.2 Importar con mongoimport
Utilizar mongoimport para importar todos los JSON convertidos:

```bash
cd ~/ruta_a_los_datos/datafiles_converted/

for file in *.json; do
    echo "Importando $file..."
    mongoimport --db streamit_db --collection invoices --file "$file" --jsonArray
done
```

**Salida esperada**:
```bash
Importando dump011_16.json...
2025-10-30T15:21:48.811+0100	connected to: mongodb://localhost/
2025-10-30T15:21:49.184+0100	1386 document(s) imported successfully. 0 document(s) failed to import.
Importando dump012_16.json...
2025-10-30T15:21:49.215+0100	connected to: mongodb://localhost/
2025-10-30T15:21:49.586+0100	1370 document(s) imported successfully. 0 document(s) failed to import.
...
```

---

## 3. Limpieza y Normalización de Datos

### Ejecutar Script de Limpieza

Usar `mongosh` desde terminal o la shell de MongoDB Compass:

```bash
# Cambiar a la base de datos
use streamit_db

# Copiar y pegar TODO el contenido del archivo PO22_05_07_1_limpieza.txt
```

Al presionar ENTER se ejecutará el script completo.

### Salida Esperada

```bash
=== INICIANDO LIMPIEZA DE FECHAS ===
✓ Campo 'charge date' normalizado a ISODate
✓ Campo 'dump date' normalizado a ISODate
✓ Campo 'billing' normalizado a ISODate
✓ Campo 'Client.Birth date' normalizado a ISODate
✓ Campos de fechas en 'contract' normalizados a ISODate

=== CORRIGIENDO TIPOS DE DATOS MIXTOS ===
✓ Campo 'Client.Surname' normalizado a tipo string
✓ Campo 'TOTAL' normalizado a tipo float

=== NORMALIZANDO NOMBRES DE CAMPOS ===
✓ Campos de nivel superior renombrados a camelCase
✓ Campos en 'Client' renombrados a camelCase
✓ Campos en 'contract' renombrados a camelCase
✓ Campos en 'contract.product' renombrados a camelCase
✓ Campos en 'Movies' renombrados a camelCase
✓ Campos en 'Series' renombrados a camelCase

=== LIMPIANDO Y NORMALIZANDO STRINGS ===
✓ Campos de texto en 'Client' limpiados (trim y lowercase en email)
✓ Campos de texto en 'contract' limpiados

=== CONVIRTIENDO CAMPOS NUMÉRICOS ===
✓ Campos numéricos en 'contract.product' convertidos a double
✓ Campos 'viewingPct' convertidos a decimal (0-1)

=== AGREGANDO CAMPOS CALCULADOS ===
✓ Campo 'Client.age' calculado y agregado
✓ Campo 'contentStats' agregado con estadísticas de contenido
✓ Metadatos de limpieza agregados

=== CREANDO ÍNDICES ===
✓ Índice creado en 'Client.customerCode'
✓ Índice creado en 'contract.contractId'
✓ Índice creado en 'chargeDate'
✓ Índice creado en 'billing'
✓ Índice compuesto creado en 'Client.customerCode' y 'chargeDate'
✓ Índice creado en 'Client.email'

=== EJECUTANDO VALIDACIONES FINALES ===
Documentos con fechas nulas críticas: 15807
Documentos con total no numérico: 0
Documentos con Surname en array: 0

✅ LIMPIEZA COMPLETADA
Total de documentos en la colección: 15807

=== FIN DEL PROCESO DE LIMPIEZA ===
```

### Transformaciones Realizadas

1. **Normalización de Fechas**: Conversión a ISODate
2. **Corrección de Tipos**: Surname a string, Total a double
3. **camelCase**: Estandarización de nombres de campos
4. **Limpieza de Strings**: Trim y lowercase en emails
5. **Campos Calculados**: Edad, contentStats, metadatos
6. **Índices**: 6 índices para optimización de consultas

---

## 4. Reestructuración del Modelo de Datos

### Objetivo

Transformar el modelo desde una colección única con redundancia hacia un **modelo normalizado** con tres colecciones especializadas:

1. **movies**: Catálogo de películas (4,914 películas únicas)
2. **series**: Catálogo de series (80 series únicas)
3. **invoices_restructured**: Facturas con referencias a contenido

### Beneficios de la Reestructuración

- ✅ **59.7% de reducción** de almacenamiento (87.61 MB → 35.32 MB)
- ✅ **Eliminación de redundancia**: Datos de películas/series almacenados una sola vez
- ✅ **Consistencia**: Una única versión de verdad por cada contenido
- ✅ **Consultas eficientes**: Índices especializados por colección
- ✅ **Análisis facilitado**: Catálogo separado para estudios de contenido
- ✅ **Escalabilidad**: Nuevo contenido no aumenta facturas existentes

### Ejecutar Script de Reestructuración

```bash
# Asegurarse de tener el script Python
python3 PO22_05_07_2_reestructuracion.py
```

### Salida Esperada

```bash
================================================================================
                      REESTRUCTURACIÓN DEL MODELO DE DATOS                      
================================================================================

🗑️  Limpiando colecciones destino...
   ✓ Colecciones limpias

🎬 PASO 1: EXTRAYENDO PELÍCULAS
--------------------------------------------------------------------------------
   Procesando factura 1000/11403...
   Procesando factura 2000/11403...
   ...

✅ Películas únicas encontradas: 4914
   Insertando en colección 'movies'...
✅ 4914 películas insertadas

📺 PASO 2: EXTRAYENDO SERIES Y TEMPORADAS
--------------------------------------------------------------------------------
   Procesando factura 1000/12671...
   ...

✅ Series únicas encontradas: 80
   Insertando en colección 'series'...
✅ 80 series insertadas

🧾 PASO 3: REESTRUCTURANDO FACTURAS
--------------------------------------------------------------------------------
   Procesando factura 1000/15807...
   ...

✅ 15807 facturas reestructuradas

🔍 PASO 4: CREANDO ÍNDICES
--------------------------------------------------------------------------------
   Creando índices en 'movies'...
   ✓ 4 índices creados en 'movies'
   Creando índices en 'series'...
   ✓ 2 índices creados en 'series'
   Creando índices en 'invoices_restructured'...
   ✓ 7 índices creados en 'invoices_restructured'

================================================================================
                          RESUMEN DE REESTRUCTURACIÓN                           
================================================================================

💾 OPTIMIZACIÓN DE ALMACENAMIENTO:
   • Tamaño original: 87.61 MB
   • Tamaño nuevo: 35.32 MB
   • Reducción: 59.7%

📊 ESTADÍSTICAS:
   • Películas únicas: 4,914
   • Series únicas: 80
   • Facturas reestructuradas: 15,807

🎯 BENEFICIOS:
   ✓ Eliminación de redundancia
   ✓ Modelo normalizado y escalable
   ✓ Consultas más eficientes
   ✓ Facilita análisis de contenido
   ✓ Preparado para métricas de consumo

⏱️  Tiempo total: 10.49 segundos

================================================================================
                    REESTRUCTURACIÓN COMPLETADA EXITOSAMENTE                    
================================================================================
```

### Estructura del Nuevo Modelo

#### Colección: movies
```json
{
  "_id": ObjectId("..."),
  "title": "The Shawshank Redemption",
  "details": {
    "year": 1994,
    "country": "USA",
    "color": "Color",
    "aspectRatio": 1.85,
    "contentRating": "R",
    "budget": 25000000,
    "gross": 28341469,
    "director": {
      "name": "Frank Darabont",
      "facebookLikes": 32000
    },
    "cast": {
      "facebookLikes": 164000,
      "stars": [
        { "name": "Tim Robbins", "facebookLikes": 40000 },
        { "name": "Morgan Freeman", "facebookLikes": 124000 }
      ]
    },
    "language": "English",
    "genres": ["Drama"],
    "keywords": ["prison", "friendship", "hope"],
    "facesInPoster": 2,
    "imdbScore": 9.3,
    "imdbLink": "http://www.imdb.com/title/tt0111161/",
    "criticReviews": 88,
    "userReviews": 1238,
    "votedUsers": 1689764,
    "facebookLikes": 93735,
    "duration": 142
  },
  "_metadata": {
    "createdAt": ISODate("2024-10-30T..."),
    "version": "1.0"
  }
}
```

#### Colección: series
```json
{
  "_id": ObjectId("..."),
  "title": "Breaking Bad",
  "totalSeasons": 5,
  "totalEpisodes": 62,
  "avgDuration": 47,
  "_metadata": {
    "createdAt": ISODate("2024-10-30T..."),
    "version": "1.0"
  }
}
```

#### Colección: invoices_restructured
```json
{
  "_id": ObjectId("..."),
  "client": {
    "customerCode": "CUST001",
    "name": "John",
    "surname": "Doe",
    "email": "john.doe@email.com",
    "phone": "+34600000000",
    "dni": "12345678A",
    "birthDate": ISODate("1990-01-15"),
    "age": 34
  },
  "contract": {
    "contractId": "CNT001",
    "startDate": ISODate("2016-01-01"),
    "endDate": ISODate("2017-01-01"),
    "address": "Calle Principal 123",
    "zip": "28001",
    "town": "Madrid",
    "country": "Spain",
    "product": {
      "reference": "PREMIUM",
      "type": "Subscription",
      "monthlyFee": 19.99,
      "costPerDay": 0.0,
      "costPerMinute": 0.0,
      "costPerContent": 0.0,
      "zapping": true,
      "promotion": "Welcome50"
    }
  },
  "billing": ISODate("2016-11-01"),
  "chargeDate": ISODate("2017-05-03"),
  "dumpDate": ISODate("2016-10-14"),
  "total": 245.67,
  "contentStats": {
    "totalMovies": 5,
    "totalSeries": 7,
    "totalContent": 12
  },
  "movies": [
    {
      "movieId": ObjectId("..."),
      "date": ISODate("2016-11-15"),
      "time": "20:30",
      "viewingPct": 0.85,
      "license": {
        "type": "Standard",
        "cost": 0.0
      }
    }
  ],
  "series": [
    {
      "seriesId": ObjectId("..."),
      "season": 3,
      "episode": 7,
      "date": ISODate("2016-11-20"),
      "time": "21:00",
      "viewingPct": 1.0,
      "license": {
        "type": "Premium",
        "cost": 0.0
      }
    }
  ],
  "_metadata": {
    "restructuredAt": ISODate("2024-10-30T..."),
    "version": "2.0"
  }
}
```

### Índices Creados

#### Movies (4 índices)
- `title` (único): Búsqueda por título
- `details.genres`: Filtrado por género
- `details.year`: Ordenamiento por año
- `details.director.name`: Búsqueda por director

#### Series (2 índices)
- `title` (único): Búsqueda por título
- `totalSeasons`: Filtrado por número de temporadas

#### Invoices Restructured (7 índices)
- `client.customerCode`: Búsqueda por cliente
- `contract.contractId`: Búsqueda por contrato
- `chargeDate`: Consultas temporales
- `billing`: Agrupaciones por período
- `movies.movieId`: Análisis de películas consumidas
- `series.seriesId`: Análisis de series consumidas
- `[client.customerCode, chargeDate]`: Consultas combinadas (compuesto)

---

## 5. Verificación en MongoDB Compass

Después de completar la reestructuración, verificar en MongoDB Compass:

1. **Base de datos**: `streamit_db`
2. **Colecciones**:
   - `invoices` (original): 15,807 documentos
   - `movies`: 4,914 documentos
   - `series`: 80 documentos
   - `invoices_restructured`: 15,807 documentos

---

## 6. Validación de Esquemas (Schema Validation)

### Objetivo

Implementar **JSON Schema Validation** en MongoDB para garantizar la integridad y consistencia de los datos en las tres colecciones del modelo normalizado. Esta capa de validación actúa como firewall de datos, rechazando automáticamente inserciones o actualizaciones que no cumplan con las reglas de negocio establecidas.

### Beneficios de la Validación

- ✅ **Integridad de Datos**: Garantiza que todos los documentos cumplan con el formato esperado
- ✅ **Prevención de Errores**: Detecta problemas antes de que lleguen a la base de datos
- ✅ **Documentación Viva**: El esquema sirve como documentación técnica actualizada
- ✅ **Validación Automática**: Sin necesidad de validación manual en código de aplicación
- ✅ **Mensajes Descriptivos**: Errores claros que facilitan la depuración
- ✅ **Restricciones de Negocio**: Implementa reglas como "edad mínima 18 años"

### Ejecutar Script de Validación

Usar `mongosh` desde terminal o la shell de MongoDB Compass:

```bash
# Cambiar a la base de datos
use streamit_db

# Copiar y pegar TODO el contenido del archivo PO22_05_07_3_schema_validation.txt
```

### Salida Esperada

```bash
================================================================================
             IMPLEMENTACIÓN DE ESQUEMAS DE VALIDACIÓN - STREAMIT DB
================================================================================

📽️  PASO 1: Creando esquema de validación para 'movies'...

✅ Esquema de 'movies' aplicado correctamente
   • Título obligatorio y único
   • Año entre 1888-2030
   • Duración 1-600 minutos
   • IMDB score 0-10
   • Géneros únicos (máx. 10)
   • Validación estricta de tipos

📺 PASO 2: Creando esquema de validación para 'series'...

✅ Esquema de 'series' aplicado correctamente
   • Título obligatorio y único
   • 1-100 temporadas
   • 1-10000 episodios totales
   • Duración promedio 1-600 minutos
   • Validación estricta de tipos

🧾 PASO 3: Creando esquema de validación para 'invoices_restructured'...

✅ Esquema de 'invoices_restructured' aplicado correctamente
   • Código cliente: 2 letras + 6 dígitos
   • DNI español: 8 dígitos + letra
   • Email en minúsculas
   • Edad 18-120 años
   • Referencias a movies y series
   • Viewing % entre 0-100
   • Validación estricta de tipos

🔐 PASO 4: Aplicando restricciones de unicidad...

✅ Índice único en 'movies.title'
✅ Índice único en 'series.title'
✅ Índice único en 'customer + billing'

================================================================================
                            PRUEBAS DE VALIDACIÓN
================================================================================

🧪 Ejecutando pruebas de validación...

Test 1: Película con año inválido (1800)...
✅ ÉXITO: Año inválido rechazado correctamente
Test 2: Serie con 0 temporadas...
✅ ÉXITO: 0 temporadas rechazado correctamente
Test 3: Factura con email inválido...
✅ ÉXITO: Email inválido rechazado correctamente
Test 4: Factura con viewingPct > 100...
✅ ÉXITO: viewingPct > 100 rechazado correctamente
Test 5: Cliente con edad menor de 18 años...
✅ ÉXITO: Edad < 18 rechazada correctamente

================================================================================
                          RESUMEN DE IMPLEMENTACIÓN
================================================================================

📋 ESQUEMAS APLICADOS:
   ✅ movies: ACTIVO
   ✅ series: ACTIVO
   ✅ invoices_restructured: ACTIVO

🔐 RESTRICCIONES DE UNICIDAD:
   ✅ movies.title (único)
   ✅ series.title (único)
   ✅ customer + billing (combinación única)

🧪 RESULTADOS DE PRUEBAS:
   ✅ Pruebas exitosas: 5
   ❌ Pruebas fallidas: 0
   📊 Total: 5

✨ REGLAS DE CONSISTENCIA IMPLEMENTADAS:
   • Películas:
     - Título obligatorio (1-200 caracteres)
     - Año entre 1888-2030
     - Duración 1-600 minutos
     - IMDB score 0-10
     - Géneros únicos (máximo 10)
     - Validación de enlaces IMDB

   • Series:
     - Título obligatorio (1-200 caracteres)
     - 1-100 temporadas
     - 1-10000 episodios totales
     - Duración promedio 1-600 minutos

   • Facturas:
     - Código cliente: formato AB123456
     - DNI español: 8 dígitos + letra
     - Email válido en minúsculas
     - Edad 18-120 años
     - Viewing % entre 0-100
     - Referencias válidas a movies/series
     - Fechas coherentes (birthDate < hoy)
     - Productos con tipos válidos
     - Importes >= 0

⚙️  CONFIGURACIÓN:
   • Validation Level: STRICT
   • Validation Action: ERROR
   • Additional Properties: FALSE

================================================================================
              ✅ ESQUEMAS DE VALIDACIÓN IMPLEMENTADOS EXITOSAMENTE
================================================================================

📊 ESTADÍSTICAS DE COLECCIONES:
   • movies: 4,914 documentos
   • series: 80 documentos
   • invoices_restructured: 15,807 documentos
```

### Reglas de Validación por Colección

#### 📽️ Movies

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| `title` | string | 1-200 caracteres, único | Título de la película |
| `details.year` | int | 1888-2030 | Año de producción |
| `details.duration` | int | 1-600 minutos | Duración de la película |
| `details.imdbScore` | double | 0-10 | Puntuación IMDB |
| `details.genres` | array | Máx. 10, únicos | Géneros de la película |
| `details.budget` | decimal | >= 0 | Presupuesto en dólares |
| `details.gross` | decimal | >= 0 | Recaudación bruta |
| `details.imdbLink` | string | Patrón IMDB válido | Enlace a IMDB |
| `details.director.name` | string | Máx. 150 caracteres | Nombre del director |
| `details.cast.stars` | array | Máx. 50 actores | Lista de actores principales |

#### 📺 Series

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| `title` | string | 1-200 caracteres, único | Título de la serie |
| `totalSeasons` | int | 1-100 | Número total de temporadas |
| `totalEpisodes` | int | 1-10000 | Número total de episodios |
| `avgDuration` | int | 1-600 minutos | Duración promedio por episodio |

#### 🧾 Invoices Restructured

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| `client.customerCode` | string | Patrón: `[A-Z]{2}[0-9]{6}` | Código cliente (ej: AB123456) |
| `client.email` | string | Patrón email válido, lowercase | Email del cliente |
| `client.dni` | string | Patrón: `[0-9]{8}[A-Z]` | DNI español (ej: 12345678A) |
| `client.phone` | long | 9-12 dígitos | Teléfono del cliente |
| `client.age` | int | 18-120 años | Edad del cliente |
| `client.birthDate` | date | Fecha en el pasado | Fecha de nacimiento |
| `contract.contractId` | string | Patrón: `C[0-9]{8}` | ID de contrato (ej: C12345678) |
| `contract.product.reference` | string | Formato: `TIPO-MODALIDAD` | Referencia del producto |
| `contract.product.type` | string | Enum: BASIC, STANDARD, PREMIUM, ENTERPRISE | Tipo de producto |
| `movies[].viewingPct` | int/double | 0-100 | Porcentaje visto |
| `series[].season` | int | >= 1 | Número de temporada |
| `series[].episode` | int | >= 1 | Número de episodio |
| `total` | decimal | >= 0 | Total de la factura |

### Patrones de Validación Implementados

#### Formato de Código de Cliente
```regex
^[A-Z]{2}[0-9]{6}$
```
- 2 letras mayúsculas
- 6 dígitos numéricos
- Ejemplo válido: `AB123456`
- Ejemplo inválido: `ab123456`, `ABC123456`, `A123456`

#### Formato de DNI Español
```regex
^[0-9]{8}[A-Z]$
```
- 8 dígitos numéricos
- 1 letra mayúscula
- Ejemplo válido: `12345678A`
- Ejemplo inválido: `1234567A`, `12345678a`, `12345678AB`

#### Formato de Email
```regex
^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$
```
- Debe contener @
- Dominio válido con TLD
- Todo en minúsculas
- Ejemplo válido: `user@example.com`
- Ejemplo inválido: `User@Example.com`, `userexample.com`

#### Formato de ID de Contrato
```regex
^C[0-9]{8}$
```
- Comienza con 'C'
- 8 dígitos numéricos
- Ejemplo válido: `C12345678`
- Ejemplo inválido: `12345678`, `c12345678`, `C1234567`

#### Formato de Hora
```regex
^([0-1][0-9]|2[0-3]):[0-5][0-9]$
```
- Formato 24 horas: HH:MM
- Ejemplo válido: `14:30`, `09:15`
- Ejemplo inválido: `25:00`, `14:70`, `2:30`

#### Formato de Referencia de Producto
```regex
^(BASIC|STANDARD|PREMIUM|ENTERPRISE)-(MONTHLY|DAILY|PPM|PPC)$
```
- Tipo: BASIC, STANDARD, PREMIUM, ENTERPRISE
- Modalidad: MONTHLY, DAILY, PPM (Pay Per Minute), PPC (Pay Per Content)
- Ejemplo válido: `PREMIUM-MONTHLY`, `BASIC-DAILY`
- Ejemplo inválido: `premium-monthly`, `BASIC`, `STANDARD-YEARLY`

### Restricciones de Unicidad

#### Índices Únicos Simples
1. **movies.title**: Evita películas duplicadas
2. **series.title**: Evita series duplicadas

#### Índice Único Compuesto
**invoices_restructured**: `[client.customerCode, billing]`
- Garantiza que un cliente solo tenga una factura por período de facturación
- Previene duplicación de facturas para el mismo cliente en el mismo mes

### Configuración de Validación

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| `validationLevel` | `strict` | Aplica validación a todos los inserts y updates |
| `validationAction` | `error` | Rechaza documentos inválidos con error |
| `additionalProperties` | `false` | No permite campos no definidos en el esquema |

### Pruebas de Validación Incluidas

El script ejecuta automáticamente 5 pruebas para verificar que las validaciones funcionan correctamente:

1. ✅ **Película con año inválido (1800)**: Rechazado (año < 1888)
2. ✅ **Serie con 0 temporadas**: Rechazado (mínimo 1)
3. ✅ **Factura con email sin @**: Rechazado (patrón inválido)
4. ✅ **Factura con viewingPct > 100**: Rechazado (máximo 100)
5. ✅ **Cliente con edad < 18**: Rechazado (mínimo 18 años)

### Ejemplos de Validación

#### ✅ Inserción Válida - Película
```javascript
db.movies.insertOne({
  title: "Inception",
  details: {
    year: 2010,
    duration: 148,
    country: "USA",
    imdbScore: 8.8,
    genres: ["Action", "Sci-Fi", "Thriller"],
    director: {
      name: "Christopher Nolan",
      facebookLikes: 50000
    }
  },
  _metadata: {
    createdAt: new Date(),
    version: "1.0"
  }
});
```

#### ❌ Inserción Inválida - Película
```javascript
db.movies.insertOne({
  title: "Old Movie",
  details: {
    year: 1800,  // ❌ Error: año < 1888
    duration: 90
  }
});

// Error retornado:
// Document failed validation
// year: must be >= 1888
```

#### ✅ Inserción Válida - Factura
```javascript
db.invoices_restructured.insertOne({
  client: {
    customerCode: "AB123456",
    name: "John",
    surname: "Doe",
    email: "john.doe@example.com",
    phone: NumberLong("600123456"),
    dni: "12345678A",
    birthDate: new Date("1990-01-15"),
    age: 34
  },
  contract: {
    contractId: "C12345678",
    startDate: new Date("2024-01-01"),
    product: {
      reference: "PREMIUM-MONTHLY",
      type: "PREMIUM"
    }
  },
  billing: new Date("2024-11-01"),
  chargeDate: new Date("2024-11-05"),
  dumpDate: new Date("2024-11-01"),
  total: NumberDecimal("19.99"),
  _metadata: {
    restructuredAt: new Date(),
    version: "2.0"
  }
});
```

#### ❌ Inserción Inválida - Factura
```javascript
db.invoices_restructured.insertOne({
  client: {
    customerCode: "abc123",  // ❌ Error: debe ser AB123456
    email: "invalid.email",  // ❌ Error: sin @
    dni: "1234567A",         // ❌ Error: solo 7 dígitos
    age: 16                  // ❌ Error: menor de 18
  },
  // ... resto de campos
});

// Errores retornados:
// customerCode: must match pattern ^[A-Z]{2}[0-9]{6}$
// email: must match email pattern
// dni: must match pattern ^[0-9]{8}[A-Z]$
// age: must be >= 18
```

### Verificación de Esquemas

#### Ver esquema de una colección
```javascript
db.getCollectionInfos({name: "movies"})[0].options.validator;
```

#### Listar colecciones con validación activa
```javascript
db.getCollectionInfos().forEach(function(coll) {
  if (coll.options.validator) {
    print(coll.name + " tiene validación activa");
  }
});
```

#### Ver nivel de validación
```javascript
db.getCollectionInfos({name: "movies"})[0].options.validationLevel;
// Retorna: "strict"
```

### Mantenimiento de Esquemas

#### Desactivar validación temporalmente
```javascript
db.runCommand({
  collMod: "movies",
  validationLevel: "off"
});
```

#### Reactivar validación
```javascript
db.runCommand({
  collMod: "movies",
  validationLevel: "strict"
});
```

#### Modificar esquema existente
```javascript
db.runCommand({
  collMod: "movies",
  validator: {
    $jsonSchema: {
      // Nuevo esquema actualizado
    }
  }
});
```

#### Eliminar validación completamente
```javascript
db.runCommand({
  collMod: "movies",
  validator: {}
});
```

---