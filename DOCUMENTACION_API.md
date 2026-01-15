# 📚 API Electoral - Documentación Completa

## 🎯 Endpoints Implementados

### 🏛️ **SENADO**

#### 1. `GET /calcular/mayoria_forzada_senado`
Calcula la configuración necesaria para que un partido alcance mayoría en el Senado.

**Parámetros:**
- `partido` (string): Partido objetivo (MORENA, PAN, PRI, etc.)
- `tipo_mayoria` (string): "simple" o "calificada"
  - simple: >64 senadores (50%)
  - calificada: ≥86 senadores (66.67%, 2/3)
- `plan` (string): Plan electoral
  - `vigente`: 64 MR + 32 PM + 32 RP = 128 total
  - `plan_a`: 96 RP puro
  - `plan_c`: 64 MR+PM sin RP
- `aplicar_topes` (boolean): Si aplica el tope del 8% de sobrerrepresentación (default: true)
- `anio` (int): Año electoral (2024, 2018)

**Ejemplo:**
```bash
GET /calcular/mayoria_forzada_senado?partido=MORENA&tipo_mayoria=simple&plan=vigente&aplicar_topes=true&anio=2024
```

**Response:**
```json
{
  "viable": true,
  "partido": "MORENA",
  "tipo_mayoria": "simple",
  "plan": "vigente",
  "senadores_necesarios": 65,
  "total_senadores": 128,
  "senadores_obtenidos": 70,
  "senadores_mr": 48,
  "senadores_rp": 22,
  "estados_ganados": 24,
  "total_estados": 32,
  "votos_porcentaje": 52,
  "metodo": "hare_redistribucion"
}
```

---

#### 2. `GET /generar/tabla_estados_senado`
Genera tabla de estados con el partido ganador y distribución de votos.

**Parámetros:**
- `partido` (string): Partido objetivo
- `votos_porcentaje` (float): Porcentaje de votos a nivel nacional (30-70)
- `anio` (int): Año electoral (2024, 2018)
- `formato` (string): "json" o "csv" (default: json)

**Ejemplo:**
```bash
GET /generar/tabla_estados_senado?partido=MORENA&votos_porcentaje=45&anio=2024&formato=json
```

**Response JSON:**
```json
{
  "partido": "MORENA",
  "votos_porcentaje": 45,
  "total_estados": 22,
  "total_senadores_mr": 44,
  "estados": [
    {
      "ESTADO": "CDMX",
      "partido_ganador": "MORENA",
      "senadores_mr": 2,
      "VOTOS_PARTIDO": 2500000,
      "VOTOS_TOTAL": 4800000,
      "PORCENTAJE": 0.52
    }
  ]
}
```

---

#### 3. `POST /editar/estados_senado`
Procesa Senado con distribución manual de estados MR.

**Body (JSON):**
```json
{
  "anio": 2024,
  "plan": "vigente",
  "estados_manuales": {
    "MORENA": ["CDMX", "MEXICO", "VERACRUZ", "PUEBLA"],
    "PAN": ["GUANAJUATO", "JALISCO", "QUERETARO"],
    "PRI": ["COAHUILA", "DURANGO"]
  },
  "aplicar_topes": true,
  "usar_coaliciones": true
}
```

**Response:**
```json
{
  "tot": {
    "MORENA": 70,
    "PAN": 30,
    "PRI": 20,
    "...": "..."
  },
  "mayorias": {
    "total_escanos": 128,
    "mayoria_simple": {
      "umbral": 65,
      "alcanzada": true,
      "partido": "MORENA",
      "escanos": 70,
      "es_coalicion": false
    },
    "mayoria_calificada": {
      "umbral": 86,
      "alcanzada": false,
      "partido": null,
      "escanos": 0,
      "es_coalicion": false
    }
  },
  "estados_editados": {
    "MORENA": 4,
    "PAN": 3,
    "PRI": 2
  }
}
```

---

#### 4. `POST /exportar/escenario_senado`
Exporta un escenario de distribución de estados a CSV.

**Body (JSON):**
```json
{
  "nombre_escenario": "MORENA_Mayoria_2024",
  "estados_por_partido": {
    "MORENA": ["CDMX", "MEXICO", "VERACRUZ"],
    "PAN": ["GUANAJUATO", "JALISCO"]
  },
  "descripcion": "Escenario de mayoría simple MORENA"
}
```

**Response:**
Archivo CSV con formato:
```csv
# Escenario: MORENA_Mayoria_2024
# Descripción: Escenario de mayoría simple MORENA
# Fecha: 2026-01-15 14:30
# ---
estado,partido_ganador,senadores_mr
CDMX,MORENA,2
MEXICO,MORENA,2
...
```

---

#### 5. `POST /importar/escenario_senado`
Importa un escenario de distribución de estados desde CSV.

**Body (JSON):**
```json
{
  "csv_content": "# Escenario: Test\nestado,partido_ganador,senadores_mr\nCDMX,MORENA,2\n..."
}
```

**Response:**
```json
{
  "nombre_escenario": "Test",
  "descripcion": "...",
  "fecha": "2026-01-15 14:30",
  "estados_por_partido": {
    "MORENA": ["CDMX", "MEXICO"],
    "PAN": ["GUANAJUATO"]
  },
  "total_estados": 32,
  "partidos": ["MORENA", "PAN", "PRI"]
}
```

---

### 🏛️ **DIPUTADOS**

#### 6. `GET /calcular/mayoria_forzada`
Calcula la configuración necesaria para que un partido alcance mayoría en Diputados.

**Parámetros:**
- `partido` (string): Partido objetivo
- `tipo_mayoria` (string): "simple" o "calificada"
  - simple: >200 diputados (50%)
  - calificada: ≥267 diputados (66.67%, 2/3)
- `plan` (string): Plan electoral
  - `300_100_con_topes`: 300 MR + 100 RP con topes (vigente)
  - `300_100_sin_topes`: Sin topes del 8%
  - `200_200_sin_topes`: 200 MR + 200 RP
  - `240_160_sin_topes`: 240 MR + 160 RP
- `aplicar_topes` (boolean): Topes constitucionales (default: true)
- `votos_base` (JSON string, opcional): Votos base por partido

**Ejemplo:**
```bash
GET /calcular/mayoria_forzada?partido=MORENA&tipo_mayoria=simple&plan=300_100_con_topes
```

**Response:**
```json
{
  "viable": true,
  "partido": "MORENA",
  "tipo_mayoria": "simple",
  "diputados_necesarios": 201,
  "total_diputados": 400,
  "diputados_obtenidos": 210,
  "diputados_mr": 145,
  "diputados_rp": 65,
  "distritos_ganados": 145,
  "total_distritos": 300,
  "votos_porcentaje": 47,
  "metodo": "hare_redistribucion"
}
```

---

#### 7. `GET /generar/tabla_distritos_diputados`
Genera tabla de distritos con el partido ganador y distribución de votos.

**Parámetros:**
- `partido` (string): Partido objetivo
- `votos_porcentaje` (float): Porcentaje de votos (30-70)
- `anio` (int): Año electoral (2024, 2021, 2018)
- `mr_total` (int): Total de distritos MR (default: 300)
- `formato` (string): "json" o "csv"

**Ejemplo:**
```bash
GET /generar/tabla_distritos_diputados?partido=MORENA&votos_porcentaje=45&anio=2024
```

**Response:**
```json
{
  "partido": "MORENA",
  "votos_porcentaje": 45,
  "total_distritos": 145,
  "distribucion_por_estado": {
    "CDMX": 20,
    "MEXICO": 25,
    "...": "..."
  },
  "distritos": [
    {
      "ENTIDAD": "CDMX",
      "DISTRITO": 1,
      "partido_ganador": "MORENA",
      "votos_estimados": 125000
    }
  ]
}
```

---

#### 8. `POST /exportar/escenario_diputados`
Exporta un escenario de distribución de distritos MR a CSV.

**Body (JSON):**
```json
{
  "nombre_escenario": "MORENA_145MR_2024",
  "distritos_por_partido": {
    "MORENA": [
      {"entidad": "CDMX", "distrito": 1},
      {"entidad": "CDMX", "distrito": 2}
    ],
    "PAN": [
      {"entidad": "GUANAJUATO", "distrito": 1}
    ]
  },
  "descripcion": "Escenario mayoría simple MORENA con 145 MR"
}
```

**Response:**
Archivo CSV descargable

---

#### 9. `POST /importar/escenario_diputados`
Importa un escenario de distribución de distritos MR desde CSV.

**Body (JSON):**
```json
{
  "csv_content": "entidad,distrito,partido_ganador\nCDMX,1,MORENA\n..."
}
```

**Response:**
```json
{
  "nombre_escenario": "Importado",
  "descripcion": "...",
  "total_distritos": 145,
  "distritos_por_partido": {
    "MORENA": [
      {"entidad": "CDMX", "distrito": 1}
    ]
  },
  "partidos": ["MORENA", "PAN", "PRI"]
}
```

---

#### 10. `POST /procesar/diputados`
Procesa datos de diputados con todas las opciones y detección automática de mayorías.

**Response incluye:**
```json
{
  "tot": { "MORENA": 210, "PAN": 80, "...": "..." },
  "mayorias": {
    "total_escanos": 400,
    "mayoria_simple": {
      "umbral": 201,
      "alcanzada": true,
      "partido": "MORENA",
      "escanos": 210,
      "es_coalicion": false
    },
    "mayoria_calificada": {
      "umbral": 267,
      "alcanzada": false,
      "partido": null,
      "escanos": 0,
      "es_coalicion": false
    }
  }
}
```

---

#### 11. `POST /procesar/senado`
Procesa datos de senadores con todas las opciones y detección automática de mayorías.

**Response incluye mayorías** (igual que diputados)

---

## 🎨 Frontend - Uso de Colores

### Indicadores de Mayoría:

```javascript
// Función para determinar color según mayoría
function getColorMayoria(mayorias) {
  if (mayorias.mayoria_calificada.alcanzada) {
    return {
      color: '#0066CC',  // Azul
      badge: '🔵 Mayoría Calificada (2/3)',
      warning: mayorias.mayoria_calificada.es_coalicion ? '⚠️ Solo con coalición' : null
    };
  } else if (mayorias.mayoria_simple.alcanzada) {
    return {
      color: '#00AA00',  // Verde
      badge: '🟢 Mayoría Simple (>50%)',
      warning: mayorias.mayoria_simple.es_coalicion ? '⚠️ Solo con coalición' : null
    };
  } else {
    return {
      color: '#999999',  // Gris
      badge: '⚪ Sin mayoría',
      warning: '⚠️ Congreso/Senado dividido - Se requieren pactos'
    };
  }
}
```

### Ejemplos de UI:

```html
<!-- Mayoría Calificada -->
<div class="mayoria-badge calificada">
  <span class="icon">🔵</span>
  <span class="text">Mayoría Calificada</span>
  <span class="detail">MORENA - 270 escaños</span>
</div>

<!-- Mayoría Simple con Coalición -->
<div class="mayoria-badge simple coalicion">
  <span class="icon">🟢</span>
  <span class="text">Mayoría Simple</span>
  <span class="detail">MORENA+PT+PVEM - 210 escaños</span>
  <span class="warning">⚠️ Solo con coalición</span>
</div>

<!-- Sin Mayoría -->
<div class="mayoria-badge sin-mayoria">
  <span class="icon">⚪</span>
  <span class="text">Congreso Dividido</span>
  <span class="warning">Se requieren pactos</span>
</div>
```

---

## 🔧 Características Técnicas

### Método de Redistribución:
- **Hare con eficiencia geográfica 1.1** (10% extra por dispersión)
- Basado en población real de estados (Censo 2020 INEGI)
- Datos reales de votación 2024

### Umbrales Constitucionales:
- **Diputados**: 
  - Mayoría simple: >200 (50%)
  - Mayoría calificada: ≥267 (66.67%, 2/3)
  - Tope sobrerrepresentación: 58% (50% + 8%)
  
- **Senado**:
  - Mayoría simple: >64 (50% de 128)
  - Mayoría calificada: ≥86 (66.67%, 2/3)
  - Tope sobrerrepresentación: 58%

### Planes Electorales:

**Senado:**
- Vigente: 64 MR + 32 PM + 32 RP = 128
- Plan A: 96 RP puro
- Plan C: 64 MR+PM sin RP

**Diputados:**
- Vigente: 300 MR + 100 RP = 400
- Plan 200/200: 200 MR + 200 RP
- Plan 240/160: 240 MR + 160 RP

---

## 📊 Flujo de Trabajo Típico

### 1. Calcular Mayoría Forzada
```
GET /calcular/mayoria_forzada_senado?partido=MORENA&tipo_mayoria=simple
→ Obtiene configuración necesaria (ej: 52% votos, 24 estados)
```

### 2. Generar Tabla de Estados/Distritos
```
GET /generar/tabla_estados_senado?partido=MORENA&votos_porcentaje=52
→ Obtiene lista detallada de estados que ganaría
```

### 3. Editar Manualmente (opcional)
```
POST /editar/estados_senado
→ Ajustar estados específicos
```

### 4. Exportar Escenario
```
POST /exportar/escenario_senado
→ Guardar para uso futuro
```

### 5. Importar y Procesar
```
POST /importar/escenario_senado
POST /procesar/senado
→ Procesar con configuración guardada
```

---

## 🚀 Estado de Implementación

✅ **Completado:**
1. Motor de mayoría forzada realista para Senado
2. Detección automática de mayorías (Diputados y Senado)
3. Endpoints de generación de tablas
4. Endpoints de edición manual
5. Exportar/importar escenarios
6. Documentación completa

🎯 **Listo para producción**
