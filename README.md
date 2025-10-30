# Migración a MongoDB de acuerdo a Casos de Uso

## Requisitos 
### Instalar MongoDB Database Tools
Para Ubuntu/Debian
```bash
wget https://fastdl.mong
odb.org/tools/db/mongodb-database-tools-ubuntu2204-x86_64-100.9.4.deb
sudo dpkg -i mongodb-database-tools-ubuntu2204-x86_64-100.9.4.deb

# Verificar instalación
mongoimport --version
```

## Análisis Exploratorio de Datos

Ejecutar el siguiente comando
```bash
python3 analisis_exploratorio.py
```
 
### Salida
╔══════════════════════════════════════════════════════════════════════════════╗
║                  ANÁLISIS EXPLORATORIO DE DATOS (EDA)                        ║
║                   Sistema de Facturas - MongoDB                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    
================================================================================
CARGANDO ARCHIVOS JSON
================================================================================

📁 Procesando: dump011_16.json
   ✓ Cargados 1386 documentos (encoding: utf-8)

📁 Procesando: dump012_16.json
   ✓ Cargados 1370 documentos (encoding: utf-8)

📁 Procesando: dump01_16.json
   ✓ Cargados 1226 documentos (encoding: utf-8)

📁 Procesando: dump02_16.json
   ✓ Cargados 1244 documentos (encoding: utf-8)

📁 Procesando: dump03_16.json
   ✓ Cargados 1253 documentos (encoding: utf-8)

📁 Procesando: dump04_16.json
   ✓ Cargados 1276 documentos (encoding: utf-8)

📁 Procesando: dump05_16.json
   ✓ Cargados 1294 documentos (encoding: utf-8)

📁 Procesando: dump06_16.json
   ✓ Cargados 1333 documentos (encoding: utf-8)

📁 Procesando: dump07_16.json
   ✓ Cargados 1330 documentos (encoding: utf-8)

📁 Procesando: dump08_16.json
   ✓ Cargados 1361 documentos (encoding: utf-8)

📁 Procesando: dump09_16.json
   ✓ Cargados 1366 documentos (encoding: utf-8)

📁 Procesando: dump10_16.json
   ✓ Cargados 1368 documentos (encoding: utf-8)

================================================================================
TOTAL DE DOCUMENTOS CARGADOS: 15807
================================================================================


================================================================================
1. ANÁLISIS DE IDENTIFICADORES (_id)
================================================================================

📊 Estadísticas de IDs:
   • Total de documentos: 15807
   • Documentos sin _id: 0
   • IDs únicos: 15807
   • IDs duplicados: 0

📋 Formatos de ID encontrados:
   • TLN/N/N/N: 144 documentos
   • NON/N/N/N: 141 documentos
   • ANN/N/N/N: 136 documentos
   • LSN/N/N/N: 134 documentos
   • BTN/N/N/N: 127 documentos
   • LBN/N/N/N: 126 documentos
   • AWN/N/N/N: 123 documentos
   • VEN/N/N/N: 121 documentos
   • BRN/N/N/N: 120 documentos
   • PWN/N/N/N: 119 documentos

================================================================================
2. ANÁLISIS DE FECHAS
================================================================================

📅 Campo: 'charge date'
   • Valores ausentes/nulos: 0
   • Formatos detectados: 1
   • Distribución de formatos:
      - DD/MM/YY: 15807 documentos
   • Ejemplos: ['03/05/17', '03/05/17', '03/05/17']

📅 Campo: 'dump date'
   • Valores ausentes/nulos: 0
   • Formatos detectados: 1
   • Distribución de formatos:
      - DD/MM/YY: 15807 documentos
   • Ejemplos: ['14/10/16', '14/10/16', '14/10/16']

📅 Campo: 'billing'
   • Valores ausentes/nulos: 0
   • Formatos detectados: 1
   • Distribución de formatos:
      - Month YYYY: 15807 documentos
   • Ejemplos: ['November 2016', 'November 2016', 'November 2016']

================================================================================
3. ANÁLISIS DE ESTRUCTURA - CLIENT
================================================================================

📊 Estadísticas de Client:
   • Documentos sin Client: 0
   • Campos únicos encontrados: 7

📋 Campos en Client:
   • Birth date
   • DNI
   • Email
   • Name
   • Phone
   • Surname
      ⚠️  PROBLEMA: Tipos mixtos detectados
         - str: 12585 documentos
         - list: 3222 documentos
   • customer code

================================================================================
4. ANÁLISIS DE ESTRUCTURA - CONTRACT
================================================================================

📊 Estadísticas de Contract:
   • Documentos sin contract: 0
   • Campos únicos en contract: 8
   • Documentos sin product: 0
   • Campos únicos en product: 8

📋 Campos en Contract:
   • ZIP
   • address
   • contract ID
   • country
   • end date
   • product
   • start date
   • town

📋 Campos en Product:
   • Reference
   • cost per content
   • cost per day
   • cost per minute
   • monthly fee
   • promotion
   • type
   • zapping

================================================================================
5. ANÁLISIS DE CONTENIDOS - MOVIES & SERIES
================================================================================

🎬 Estadísticas de Movies:
   • Documentos sin Movies: 4404
   • Total de películas: 65540
   • Promedio por documento: 5.75
   • Campos únicos: 6

📺 Estadísticas de Series:
   • Documentos sin Series: 3136
   • Total de series: 91368
   • Promedio por documento: 7.21
   • Campos únicos: 10

📋 Campos en Movies:
   • Date
   • Details
   • License
   • Time
   • Title
   • Viewing PCT

📋 Campos en Series:
   • Avg duration
   • Date
   • Episode
   • License
   • Season
   • Time
   • Title
   • Total Episodes
   • Total Seasons
   • Viewing PCT

================================================================================
6. ANÁLISIS DE CAMPOS NUMÉRICOS
================================================================================

💰 Campo: 'TOTAL'
   • Valores ausentes: 0
   • Tipos de datos encontrados:
      - int: 8637
      - float: 7170
   • Estadísticas:
      - Mínimo: 20.22
      - Máximo: 1837.47
      - Promedio: 243.52

================================================================================
7. RESUMEN DE PROBLEMAS DE CALIDAD DETECTADOS
================================================================================

🔴 PROBLEMAS CRÍTICOS:

   2. VALORES AUSENTES
      • Acción requerida: Definir valores por defecto o eliminar

   3. FORMATOS DE FECHA HETEROGÉNEOS
      • Acción requerida: Normalizar a formato ISO 8601

   4. TIPOS DE DATOS MIXTOS
      • Client.Surname: {'list', 'str'}
      • Acción requerida: Convertir a tipo único

================================================================================
RECOMENDACIONES PARA LIMPIEZA:
================================================================================

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
        

✅ Análisis exploratorio completado.
📄 Revisar este informe antes de proceder con la importación a MongoDB.

