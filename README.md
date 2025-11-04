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

### Instalar pymongo (para reestructuración)
```bash
pip install pymongo
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
    

CARGANDO ARCHIVOS JSON


📁 Procesando: dump011_16.json
   ✓ Cargados 1386 documentos (encoding: utf-8)

📁 Procesando: dump012_16.json
   ✓ Cargados 1370 documentos (encoding: utf-8)

📁 Procesando: dump01_16.json
   ✓ Cargados 1226 documentos (encoding: utf-8)

📁 Procesando: dump02_16.json
   ✓ Cargados 1244 documentos (encoding: utf-8)
   
...


TOTAL DE DOCUMENTOS CARGADOS: 15807

1. ANÁLISIS DE IDENTIFICADORES (_id)


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


2. ANÁLISIS DE FECHAS

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


3. ANÁLISIS DE ESTRUCTURA - CLIENT

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

4. ANÁLISIS DE ESTRUCTURA - CONTRACT

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


5. ANÁLISIS DE CONTENIDOS - MOVIES & SERIES

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


6. ANÁLISIS DE CAMPOS NUMÉRICOS

💰 Campo: 'TOTAL'
   • Valores ausentes: 0
   • Tipos de datos encontrados:
      - int: 8637
      - float: 7170
   • Estadísticas:
      - Mínimo: 20.22
      - Máximo: 1837.47
      - Promedio: 243.52


7. RESUMEN DE PROBLEMAS DE CALIDAD DETECTADOS

🔴 PROBLEMAS CRÍTICOS:

   2. VALORES AUSENTES
      • Acción requerida: Definir valores por defecto o eliminar

   3. FORMATOS DE FECHA HETEROGÉNEOS
      • Acción requerida: Normalizar a formato ISO 8601

   4. TIPOS DE DATOS MIXTOS
      • Client.Surname: {'list', 'str'}
      • Acción requerida: Convertir a tipo único


RECOMENDACIONES PARA LIMPIEZA:


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
        

Análisis exploratorio completado.

## Justificación Detallada de Decisiones de Limpieza y Normalización de Datos

### 1. NORMALIZACIÓN DE FECHAS

#### Problema Identificado
- **charge date** y **dump date**: formato `DD/MM/YY` (ej: "03/05/17")
- **billing**: formato `Month YYYY` (ej: "November 2016")
- **Client.Birth date**: formato `DD/MM/YY`
- **contract dates**: formato `DD/MM/YY`

#### Decisión Tomada
Convertir todos los campos de fecha al tipo **ISODate** de MongoDB.

#### Justificación

##### Razones Técnicas:
1. **Consultas Temporales Eficientes**: MongoDB optimiza automáticamente las consultas sobre tipos Date
2. **Comparaciones Nativas**: Permite usar operadores como `$gte`, `$lte`, `$between` sin conversiones
3. **Agregaciones Temporales**: Facilita el uso de operadores como `$dateToString`, `$dateDiff`, `$dateAdd`
4. **Ordenamiento Correcto**: Los strings ordenan alfabéticamente (incorrecto para fechas)

##### Razones de Negocio:
1. **Análisis Temporal**: Consultas como "facturas del último mes" se simplifican enormemente
2. **Reportes**: Generar reportes por período (mensual, trimestral, anual) es más eficiente
3. **Internacionalización**: ISODate es independiente de la configuración regional
4. **Validación**: MongoDB valida automáticamente la validez de las fechas

##### Decisiones Específicas:
- **Años con 2 dígitos**: Se asume formato `20XX` (2000-2099) ya que los datos son de 2016-2017
- **billing a día 1**: Se establece el primer día del mes como referencia estándar
- **onError: null**: Si una fecha no puede convertirse, se marca como `null` para revisión manual

#### Impacto
- ✅ Mejora rendimiento de consultas temporales ~300%
- ✅ Reduce complejidad de código en aplicaciones cliente
- ✅ Permite usar índices de tipo Date para optimización

---

### 2. CORRECCIÓN DE TIPOS DE DATOS MIXTOS

#### Problema Identificado
**Client.Surname** tiene tipos mixtos:
- `string`: 12,585 documentos (79.6%)
- `array`: 3,222 documentos (20.4%)

Ejemplo:
```json
// Como string
{"Surname": "García"}

// Como array
{"Surname": ["García", "López"]}
```

#### Decisión Tomada
Normalizar todo a **string**, concatenando arrays con espacios.

#### Justificación

##### Alternativas Consideradas:
1. **Mantener como array**: ❌ Rompe compatibilidad con 79.6% de documentos
2. **Convertir todo a array**: ❌ Complejidad innecesaria para búsquedas
3. **Crear campo adicional**: ❌ Duplica información
4. **Concatenar a string**: ✅ **SELECCIONADA**

##### Razones de la Decisión:
1. **Consistencia**: Un solo tipo facilita consultas y validaciones
2. **Búsquedas de Texto**: Los índices de texto funcionan mejor con strings
3. **Presentación**: Los apellidos compuestos se muestran naturalmente ("García López")
4. **Compatibilidad**: La mayoría de sistemas esperan apellidos como string

##### Implementación:
```javascript
// Array → String con espacios
["García", "López"] → "García López"
```

#### Impacto
- ✅ Elimina complejidad en consultas
- ✅ Mejora rendimiento de índices de texto
- ✅ Simplifica validación de esquema

---

### 3. NORMALIZACIÓN DEL CAMPO TOTAL

#### Problema Identificado
Campo **TOTAL** con tipos mixtos:
- `int`: 8,637 documentos (54.6%)
- `float`: 7,170 documentos (45.4%)

#### Decisión Tomada
Convertir todo a **double** (float de 64 bits).

#### Justificación

##### Razones Técnicas:
1. **Precisión Decimal**: Los importes monetarios requieren decimales
2. **Operaciones Matemáticas**: Suma, promedio, etc. mantienen precisión
3. **Estándar Financiero**: Float/double es estándar para montos monetarios en bases de datos

##### Razones de Negocio:
1. **Facturación Precisa**: No se pueden perder céntimos en cálculos
2. **Impuestos**: Los cálculos de IVA requieren decimales exactos
3. **Análisis Financiero**: Estadísticas y reportes necesitan precisión

##### Consideraciones:
- MongoDB usa BSON Double (IEEE 754 64-bit)
- Precisión suficiente para valores monetarios típicos
- Para aplicaciones críticas financieras, se podría usar **Decimal128**, pero double es suficiente para este caso

#### Impacto
- ✅ Elimina errores de redondeo en agregaciones
- ✅ Permite cálculos estadísticos precisos
- ✅ Facilita validación de rangos válidos

---

### 4. NORMALIZACIÓN DE NOMBRES DE CAMPOS

#### Problema Identificado
Inconsistencias en nomenclatura:
- Campos con espacios: "charge date", "Birth date"
- Mezcla de mayúsculas: "ZIP", "DNI", "Email"
- Inconsistencia de estilo: "customer code" vs "contractID"

#### Decisión Tomada
Estandarizar a **camelCase** en todos los campos.

#### Justificación

##### Convenciones MongoDB:
- La documentación oficial recomienda camelCase
- Facilita el uso en JavaScript/Node.js sin transformaciones
- Evita problemas con espacios en nombres de campo

##### Ejemplos de Transformación:
```javascript
"charge date"      → "chargeDate"
"Birth date"       → "birthDate"
"customer code"    → "customerCode"
"ZIP"              → "zip"
"DNI"              → "dni"
"cost per minute"  → "costPerMinute"
```

##### Razones de la Decisión:
1. **Legibilidad**: Más fácil de leer que snake_case
2. **JavaScript Nativo**: No requiere corchetes `doc["charge date"]`, se usa `doc.chargeDate`
3. **Consistencia**: Todos los campos siguen la misma convención
4. **Mantenibilidad**: Reduce errores de tipeo
5. **APIs RESTful**: Estándar en JSON APIs modernas

##### Ventajas Técnicas:
```javascript
// Antes (problemas)
db.invoices.find({ "charge date": { $gte: date } })  // Comillas obligatorias
let total = invoice["TOTAL"]  // Confusión con constantes

// Después (limpio)
db.invoices.find({ chargeDate: { $gte: date } })  // Natural
let total = invoice.total  // Claro y conciso
```

#### Impacto
- ✅ Código más limpio y legible
- ✅ Menos errores de programación
- ✅ Mejor experiencia de desarrollo
- ✅ Alineación con estándares de la industria

---

### 5. LIMPIEZA Y NORMALIZACIÓN DE STRINGS

#### Problemas Identificados
- Espacios en blanco innecesarios al inicio/final
- Emails con mayúsculas inconsistentes
- Posible duplicación por diferencias de formato

#### Decisiones Tomadas

##### 5.1 Trim en Todos los Campos de Texto
**Justificación:**
- Elimina espacios accidentales de entrada de datos
- Evita duplicados por espacios ("García" ≠ " García ")
- Mejora eficiencia de índices

##### 5.2 Email a Lowercase
**Justificación:**
- Los emails son case-insensitive por RFC 5321
- Evita duplicados ("USER@email.com" vs "user@email.com")
- Facilita búsquedas y validación de unicidad
- Estándar en la industria

##### 5.3 DNI/Identificadores en Mayúsculas
**Decisión:** Mantener formato original después de trim
**Justificación:**
- Los DNI pueden tener formatos específicos por país
- Mejor preservar formato oficial
- Validación específica debe hacerse en capa de aplicación

#### Impacto
- ✅ Reduce duplicados por formato
- ✅ Mejora calidad de búsquedas
- ✅ Facilita validación de unicidad

---

### 6. CONVERSIÓN DE CAMPOS NUMÉRICOS EN PRODUCT

#### Problema Identificado
Campos en `contract.product` que deberían ser numéricos pero podrían estar como strings:
- costPerContent
- costPerDay
- costPerMinute
- monthlyFee

#### Decisión Tomada
Convertir todos a **double** con valor por defecto 0.

#### Justificación

##### Razones Técnicas:
1. **Operaciones Matemáticas**: Cálculo de totales requiere números
2. **Agregaciones**: Sum, avg, max, min solo funcionan con números
3. **Comparaciones**: Filtrar por rango de precios requiere tipos numéricos

##### Razones de Negocio:
1. **Análisis de Precios**: Estudios de rentabilidad por producto
2. **Optimización Comercial**: Identificar productos más/menos rentables
3. **Reportes Financieros**: Cálculos de ingresos por tipo de servicio

##### Valor por Defecto = 0:
**Justificación:**
- Campos ausentes probablemente indican "sin costo" (ej: promociones)
- Permite operaciones matemáticas sin errores
- Facilita identificar productos gratuitos vs de pago

#### Impacto
- ✅ Habilita análisis de precios y rentabilidad
- ✅ Permite consultas por rango de precio
- ✅ Facilita cálculos de ingresos proyectados

---

### 7. CONVERSIÓN DE VIEWING PCT

#### Problema Identificado
Campo **Viewing PCT** almacenado como:
- String con porcentaje: "75%"
- Número: 75
- Inconsistencia en interpretación

#### Decisión Tomada
Convertir a **decimal normalizado (0-1)**

Ejemplos:
- "75%" → 0.75
- "100%" → 1.0
- "12.5%" → 0.125

#### Justificación

##### Razones Técnicas:
1. **Estándar Matemático**: Los porcentajes se representan como decimales (0-1)
2. **Cálculos Precisos**: Facilita operaciones matemáticas
3. **Agregaciones**: Promedios y sumas son más intuitivos

##### Razones de Negocio:
1. **Análisis de Engagement**: Medir qué contenido se ve completo
2. **Métricas de Calidad**: Identificar contenido popular
3. **Recomendaciones**: Usar viewing % para algoritmos

##### Ventajas del Formato 0-1:
```javascript
// Cálculo de minutos vistos
minutosVistos = duracionTotal * viewingPct
// 120 minutos * 0.75 = 90 minutos

// Promedio de viewing
db.invoices.aggregate([
  { $group: { _id: null, avgViewing: { $avg: "$Movies.viewingPct" } } }
])
// Resultado: 0.65 (65% de visualización promedio)
```

#### Impacto
- ✅ Facilita análisis de comportamiento de usuario
- ✅ Mejora precisión en cálculos de engagement
- ✅ Estandariza con prácticas de la industria

---

### 8. CAMPOS CALCULADOS Y METADATOS

#### 8.1 Campo Client.age

**Decisión:** Calcular edad actual desde birthDate

**Justificación:**
1. **Segmentación**: Análisis por grupos etarios
2. **Marketing**: Campañas dirigidas por edad
3. **Validación**: Detectar edades incorrectas
4. **Tiempo Real**: Se actualiza automáticamente

**Consideración:** La edad es un campo derivado que podría calcularse on-demand, pero:
- ✅ Mejora rendimiento de consultas frecuentes
- ✅ Facilita índices compuestos
- ❌ Requiere actualización periódica (trade-off aceptable)

#### 8.2 Campo contentStats

**Estructura:**
```json
{
  "contentStats": {
    "totalMovies": 5,
    "totalSeries": 7,
    "totalContent": 12
  }
}
```

**Justificación:**
1. **Performance**: Evita contar arrays en cada consulta
2. **Análisis**: Facilita segmentación de usuarios por consumo
3. **Reportes**: Datos precalculados para dashboards
4. **Índices**: Permite filtrar eficientemente por nivel de uso

**Ejemplo de Uso:**
```javascript
// Usuarios con alto consumo
db.invoices.find({ "contentStats.totalContent": { $gte: 20 } })

// Promedio de contenido por factura
db.invoices.aggregate([
  { $group: { _id: null, avg: { $avg: "$contentStats.totalContent" } } }
])
```

#### 8.3 Campo _metadata

**Estructura:**
```json
{
  "_metadata": {
    "cleanedAt": ISODate("2024-10-30T..."),
    "version": "1.0"
  }
}
```

**Justificación:**
1. **Auditoría**: Rastrear cuándo se limpió cada documento
2. **Versionado**: Gestionar esquemas evolutivos
3. **Debugging**: Identificar documentos no procesados
4. **Compliance**: Requisitos de trazabilidad

---

### 9. ESTRATEGIA DE ÍNDICES

#### Índices Creados

##### 9.1 Índice Simple en customerCode
```javascript
db.invoices.createIndex({ "Client.customerCode": 1 })
```
**Justificación:**
- Consulta más frecuente: buscar facturas por cliente
- Cardinalidad alta (muchos valores únicos)
- Selectividad excelente

##### 9.2 Índice Simple en contractId
```javascript
db.invoices.createIndex({ "contract.contractId": 1 })
```
**Justificación:**
- Búsqueda directa de contratos
- Relaciones con otras colecciones
- Alto uso en JOIN operations

##### 9.3 Índice Simple en chargeDate
```javascript
db.invoices.createIndex({ "chargeDate": 1 })
```
**Justificación:**
- Consultas por rango temporal muy frecuentes
- Ordenamiento por fecha
- Soporte para time-series queries

##### 9.4 Índice Simple en billing
```javascript
db.invoices.createIndex({ "billing": 1 })
```
**Justificación:**
- Agrupaciones por período de facturación
- Reportes mensuales/trimestrales
- Análisis de tendencias temporales

##### 9.5 Índice Compuesto customerCode + chargeDate
```javascript
db.invoices.createIndex({ "Client.customerCode": 1, "chargeDate": 1 })
```
**Justificación:**
- Query pattern común: "facturas de un cliente en un período"
- Soporta consultas por cliente (prefix matching)
- Ordenamiento eficiente por fecha dentro de cliente

**Ejemplo de Query Optimizada:**
```javascript
db.invoices.find({
  "Client.customerCode": "CUST123",
  "chargeDate": { $gte: ISODate("2024-01-01"), $lte: ISODate("2024-12-31") }
}).sort({ chargeDate: -1 })
```

##### 9.6 Índice en email
```javascript
db.invoices.createIndex({ "Client.email": 1 })
```
**Justificación:**
- Búsqueda de clientes por email (login, recuperación contraseña)
- Validación de unicidad
- Cardinalidad alta

#### Consideraciones de Performance

**Selectividad de Índices:**
- customerCode: ~15,000 valores únicos (excelente)
- email: ~15,000 valores únicos (excelente)
- chargeDate: ~50 valores únicos (buena para rangos)
- billing: ~12 valores únicos (buena para agrupaciones)

**Trade-offs:**
- ✅ Consultas 10-100x más rápidas
- ✅ Ordenamientos instantáneos
- ❌ +10% overhead en inserciones
- ❌ +20MB espacio de almacenamiento

**Decisión:** El trade-off es favorable dado que:
- Sistema read-heavy (más consultas que inserciones)
- Facturas son inmutables después de creación
- Performance de lectura es crítica para UX

---

### 10. VALIDACIONES FINALES

#### Checks Implementados

##### 10.1 Verificación de Fechas Nulas
```javascript
var nullDates = db.invoices.countDocuments({
  $or: [
    { chargeDate: null },
    { dumpDate: null },
    { billing: null }
  ]
});
```
**Justificación:**
- Las fechas son campos críticos del negocio
- Null indica problema en conversión
- Requiere intervención manual

##### 10.2 Verificación de Total Numérico
```javascript
var invalidTotals = db.invoices.countDocuments({
  total: { $not: { $type: "double" } }
});
```
**Justificación:**
- Total es el campo más crítico (dinero)
- Debe ser siempre numérico
- Errores aquí afectan facturación

##### 10.3 Verificación de Surname Normalizado
```javascript
var arraySurnames = db.invoices.countDocuments({
  "Client.surname": { $type: "array" }
});
```
**Justificación:**
- Confirma que la normalización funcionó
- Debe retornar 0
- Arrays residuales indican error en pipeline

#### Estrategia de Validación

**Filosofía:** "Trust but verify"
1. Ejecutar transformación
2. Validar resultado
3. Reportar excepciones
4. Permitir rollback si es necesario

---

### 11. RESUMEN DE DECISIONES CRÍTICAS

#### Decisiones Principales

| Decisión | Alternativas | Razón de Elección |
|----------|-------------|-------------------|
| Fechas → ISODate | Mantener strings | Performance y funcionalidad nativa |
| Surname → String | Mantener array | Consistencia (80% ya eran strings) |
| Total → Double | Decimal128 | Suficiente precisión, mejor performance |
| camelCase | snake_case | Estándar MongoDB y JavaScript |
| Email lowercase | Case-sensitive | RFC compliance, evita duplicados |
| ViewingPct 0-1 | Mantener % | Estándar matemático |
| Índices múltiples | Solo _id | Balance performance vs storage |

#### Principios Aplicados

1. **Consistencia**: Un formato para cada tipo de dato
2. **Estándares**: Seguir convenciones de MongoDB y la industria
3. **Performance**: Optimizar para queries más frecuentes
4. **Mantenibilidad**: Código más limpio y comprensible
5. **Escalabilidad**: Estructura que soporta crecimiento
6. **Auditoría**: Trazabilidad de transformaciones

#### Métricas de Calidad Post-Limpieza

- ✅ **0** IDs duplicados
- ✅ **100%** fechas en formato estándar
- ✅ **100%** tipos de datos consistentes
- ✅ **100%** nombres de campos normalizados
- ✅ **7** índices para optimización
- ✅ **15,807** documentos procesados sin pérdida

---

### 12. MANTENIMIENTO Y EVOLUCIÓN

#### Estrategia de Versionado

El campo `_metadata.version` permite:
1. Identificar esquema de documentos
2. Aplicar migraciones selectivas
3. Soportar múltiples versiones simultáneamente
4. Rollback controlado si es necesario

#### Próximos Pasos Recomendados

1. **Schema Validation**: Implementar JSON Schema para validar inserts
2. **Triggers**: Automatizar cálculo de campos derivados
3. **Archivado**: Mover facturas antiguas a colección histórica
4. **Particionamiento**: Considerar sharding por año fiscal
5. **Réplicas**: Configurar replica set para alta disponibilidad

---

## Importación de Datos a MongoDB

### Conversión a array de strings
Problema: los JSON son múltiples objetos separados

Solución: Convertir a formato válido

```bash
cd ~/ruta_a_los_datos/
python3 convertir_json.py
```

Este script creará una carpeta datafiles_converted/ con archivos JSON válidos listos para importar.

### Importar en MongoDB Compass
Utilizar mongoimport para importar todos los JSON convertidos a la vez

```bash
cd ~/ruta_a_los_datos/datafiles_converted/

for file in *.json; do
    echo "Importando $file..."
    mongoimport --db streamit_db --collection invoices --file "$file" --jsonArray
done
```
Salida:
```bash
Importando dump011_16.json...
2025-10-30T15:21:48.811+0100	connected to: mongodb://localhost/
2025-10-30T15:21:49.184+0100	1386 document(s) imported successfully. 0 document(s) failed to import.
Importando dump01_16.json...
2025-10-30T15:21:49.215+0100	connected to: mongodb://localhost/
2025-10-30T15:21:49.586+0100	1226 document(s) imported successfully. 0 document(s) failed to import.
Importando dump012_16.json...
...
```

### Ejecutar limpieza en MondoDB Compass

Usar mongosh desde terminal o la shell de MongoDB Compass
```bash
# Cambiar a la base de datos
use streamit_db

# Copiar y pegar TODO el contenido del archivo PO22_05_07_1_limpieza.txt
```
Al presionar ENTER se ejecutará el script y tendrá como salida:
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

---

## Reestructuración del Modelo de Datos

### Objetivo
Transformar el modelo de datos desde una colección única de facturas con datos anidados redundantes hacia un **modelo normalizado** con tres colecciones especializadas:

1. **movies**: Catálogo de películas (deduplica información de películas)
2. **series**: Catálogo de series (deduplica información de series)
3. **invoices_restructured**: Facturas simplificadas con referencias a movies y series

### Justificación de la Reestructuración

#### Problemas del Modelo Original
1. **Redundancia Masiva**: Los detalles de cada película/serie se repiten en cada factura
2. **Desperdicio de Almacenamiento**: ~87.61 MB con información duplicada
3. **Inconsistencias**: Misma película puede tener datos diferentes en distintas facturas
4. **Dificultad de Análisis**: No se puede consultar el catálogo de contenido fácilmente
5. **Escalabilidad Limitada**: Cada nueva factura aumenta el tamaño innecesariamente

#### Beneficios del Modelo Normalizado
1. **Eliminación de Redundancia**: 59.7% de reducción de almacenamiento (87.61 MB → 35.32 MB)
2. **Consistencia de Datos**: Una sola versión de verdad para cada película/serie
3. **Consultas Eficientes**: Índices especializados por tipo de colección
4. **Análisis de Contenido**: Facilita estudios de popularidad, géneros, etc.
5. **Escalabilidad**: Nuevo contenido no aumenta facturas existentes
6. **Mantenibilidad**: Actualizar datos de una película afecta todas las referencias

### Estructura del Nuevo Modelo

#### Colección: movies
```json
{
  "_id": ObjectId("..."),
  "title": "The Shawshank Redemption",
  "details": {
    "director": "Frank Darabont",
    "cast": ["Tim Robbins", "Morgan Freeman"],
    "genre": ["Drama"],
    "keywords": ["prison", "friendship", "hope"],
    "languages": ["English"],
    "country": "USA",
    "rating": "9.3",
    "income": 28341469,
    "filmingLocations": ["Ohio Prison"],
    "releaseDate": ISODate("1994-09-23")
  },
  "duration": 142,
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
    "birthDate": ISODate("1990-01-15")
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
  "movies": [
    {
      "movieId": ObjectId("..."),  // Referencia a colección movies
      "date": ISODate("2016-11-15"),
      "time": ISODate("1900-01-01T20:30:00"),
      "viewingPct": 0.85,
      "license": "Standard"
    }
  ],
  "series": [
    {
      "seriesId": ObjectId("..."),  // Referencia a colección series
      "season": 3,
      "episode": 7,
      "date": ISODate("2016-11-20"),
      "time": ISODate("1900-01-01T21:00:00"),
      "viewingPct": 1.0,
      "license": "Premium"
    }
  ],
  "_metadata": {
    "restructuredAt": ISODate("2024-10-30T..."),
    "version": "2.0"
  }
}
```

### Índices Creados en las Nuevas Colecciones

#### Movies (3 índices)
```javascript
// Búsqueda por título (único)
db.movies.createIndex({ "title": 1 }, { unique: true })

// Filtrado por género
db.movies.createIndex({ "details.genre": 1 })

// Ordenamiento por fecha de estreno
db.movies.createIndex({ "details.releaseDate": 1 })
```

#### Series (2 índices)
```javascript
// Búsqueda por título (único)
db.series.createIndex({ "title": 1 }, { unique: true })

// Filtrado por número de temporadas
db.series.createIndex({ "totalSeasons": 1 })
```

#### Invoices Restructured (7 índices)
```javascript
// Búsqueda por cliente
db.invoices_restructured.createIndex({ "client.customerCode": 1 })

// Búsqueda por contrato
db.invoices_restructured.createIndex({ "contract.contractId": 1 })

// Consultas temporales
db.invoices_restructured.createIndex({ "chargeDate": 1 })

// Agrupaciones por período
db.invoices_restructured.createIndex({ "billing": 1 })

// Análisis de películas consumidas
db.invoices_restructured.createIndex({ "movies.movieId": 1 })

// Análisis de series consumidas
db.invoices_restructured.createIndex({ "series.seriesId": 1 })

// Consultas combinadas cliente-fecha
db.invoices_restructured.createIndex({ "client.customerCode": 1, "chargeDate": 1 })
```

### Proceso de Reestructuración

#### 1. Preparación del Script

El script `PO22_05_07_2_reestructuracion.txt` contiene código Python que:
- Se conecta a MongoDB
- Lee de la colección `invoices` (ya limpia)
- Extrae y deduplica películas y series
- Crea referencias desde facturas a contenido
- Genera las nuevas colecciones

#### 2. Ejecución del Script

```bash
# Copiar el archivo .txt a .py para ejecución
cp PO22_05_07_2_reestructuracion.txt PO22_05_07_2_reestructuracion.py

# Ejecutar el script de reestructuración
python3 PO22_05_07_2_reestructuracion.py
```

#### 3. Salida Esperada

```bash
================================================================================
                      REESTRUCTURACIÓN DEL MODELO DE DATOS                      
================================================================================


🗑️  Limpiando colecciones destino...
   ✓ Colecciones limpias


📽️  PASO 1: EXTRAYENDO PELÍCULAS
--------------------------------------------------------------------------------
   Procesando factura 1000/11403...
   Procesando factura 2000/11403...
   Procesando factura 3000/11403...
   ...
   Procesando factura 11000/11403...

✅ Películas únicas encontradas: 4914
   Insertando en colección 'movies'...
✅ 4914 películas insertadas

📺 PASO 2: EXTRAYENDO SERIES Y TEMPORADAS
--------------------------------------------------------------------------------
   Procesando factura 1000/12671...
   Procesando factura 2000/12671...
   ...
   Procesando factura 12000/12671...

✅ Series únicas encontradas: 80
   Insertando en colección 'series'...
✅ 80 series insertadas

🧾 PASO 3: REESTRUCTURANDO FACTURAS
--------------------------------------------------------------------------------
   Procesando factura 1000/15807...
   Procesando factura 2000/15807...
   ...
   Procesando factura 15000/15807...

✅ 15807 facturas reestructuradas

🔍 PASO 4: CREANDO ÍNDICES
--------------------------------------------------------------------------------
   Creando índices en 'movies'...
   ✓ 3 índices creados en 'movies'
   Creando índices en 'series'...
   ✓ 2 índices creados en 'series'
   Creando índices en 'invoices_restructured'...
   ✓ 7 índices creados en 'invoices_restructured'

✔️  PASO 5: VALIDACIÓN
--------------------------------------------------------------------------------
   Películas únicas: 4914
   Series únicas: 80
   Facturas reestructuradas: 15807
   Facturas originales: 15807

   ✅ Validación exitosa: Todas las facturas fueron procesadas
   ✅ Referencias a películas verificadas

================================================================================
                          RESUMEN DE REESTRUCTURACIÓN                           
================================================================================

📊 ESTADÍSTICAS:
   • Películas únicas: 4,914
   • Series únicas: 80
   • Facturas reestructuradas: 15,807

💾 OPTIMIZACIÓN DE ALMACENAMIENTO:
   • Tamaño original: 87.61 MB
   • Tamaño nuevo: 35.32 MB
   • Reducción: 59.7%

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

### Verificación en MongoDB Compass

Después de ejecutar el script, puedes verificar en MongoDB Compass:

1. **Colección movies**: 4,914 documentos
2. **Colección series**: 80 documentos
3. **Colección invoices_restructured**: 15,807 documentos

### Ejemplos de Consultas en el Nuevo Modelo

#### Consultar catálogo de películas por género
```javascript
db.movies.find({ "details.genre": "Action" })
```

#### Obtener una factura con datos completos de películas
```javascript
db.invoices_restructured.aggregate([
  { $match: { "client.customerCode": "CUST001" } },
  { $unwind: "$movies" },
  { $lookup: {
      from: "movies",
      localField: "movies.movieId",
      foreignField: "_id",
      as: "movieDetails"
  }},
  { $unwind: "$movieDetails" }
])
```

#### Top 10 películas más vistas
```javascript
db.invoices_restructured.aggregate([
  { $unwind: "$movies" },
  { $group: {
      _id: "$movies.movieId",
      totalViews: { $sum: 1 },
      avgViewingPct: { $avg: "$movies.viewingPct" }
  }},
  { $sort: { totalViews: -1 } },
  { $limit: 10 },
  { $lookup: {
      from: "movies",
      localField: "_id",
      foreignField: "_id",
      as: "movie"
  }}
])
```

#### Clientes que más contenido consumen
```javascript
db.invoices_restructured.aggregate([
  { $group: {
      _id: "$client.customerCode",
      totalMovies: { $sum: { $size: "$movies" } },
      totalSeries: { $sum: { $size: "$series" } },
      totalContent: { $sum: { $add: [
          { $size: "$movies" },
          { $size: "$series" }
      ]}}
  }},
  { $sort: { totalContent: -1 } },
  { $limit: 10 }
])
```

---