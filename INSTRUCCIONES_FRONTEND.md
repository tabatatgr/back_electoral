# 🎯 INSTRUCCIONES PARA IA DEL FRONTEND

## 📋 CONTEXTO

El backend electoral ya tiene implementada la **detección automática de mayorías** y **motor de mayoría forzada** tanto para Diputados como para Senado. Ya NO es solo diseño - hay **8 endpoints nuevos** que necesitan integrarse al frontend.

---

## ✅ LO QUE YA FUNCIONA EN BACKEND

### 1. **Detección Automática de Mayorías** (YA INTEGRADO)
Los endpoints `/procesar/diputados` y `/procesar/senado` **ya devuelven** el objeto `mayorias`:

```json
{
  "tot": { "MORENA": 210, "PAN": 80, "PRI": 50, ... },
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

**ACCIÓN REQUERIDA:**
- ✅ Verificar que las llamadas actuales a `/procesar/diputados` y `/procesar/senado` **ya reciben** este objeto
- ✅ Mostrar badges/indicadores visuales según el estado de mayorías
- ✅ Usar los colores sugeridos (ver sección de diseño abajo)

---

## 🆕 ENDPOINTS NUEVOS A INTEGRAR (8 TOTAL)

### **SENADO** (5 endpoints nuevos)

#### 1️⃣ **Calcular Mayoría Forzada - Senado**
```http
GET /calcular/mayoria_forzada_senado?partido=MORENA&tipo_mayoria=simple&plan=vigente&aplicar_topes=true&anio=2024
```

**¿Para qué sirve?**
Calcula cuántos votos/estados necesita un partido para alcanzar mayoría.

**Response:**
```json
{
  "viable": true,
  "partido": "MORENA",
  "senadores_necesarios": 65,
  "estados_ganados": 24,
  "votos_porcentaje": 52,
  "senadores_obtenidos": 70
}
```

**UI Sugerida:**
- Formulario con:
  - Select de partido (MORENA, PAN, PRI, etc.)
  - Radio buttons: Mayoría simple / Mayoría calificada
  - Select de plan: Vigente / Plan A / Plan C
  - Checkbox: Aplicar topes del 8%
- Mostrar resultado en cards:
  - "Necesitas 52% de los votos"
  - "Ganar 24 de 32 estados"
  - "Obtendrás 70 senadores (necesitas 65)"

---

#### 2️⃣ **Generar Tabla de Estados - Senado**
```http
GET /generar/tabla_estados_senado?partido=MORENA&votos_porcentaje=45&anio=2024&formato=json
```

**¿Para qué sirve?**
Genera una tabla detallada de qué estados ganaría el partido con X% de votos.

**Response:**
```json
{
  "partido": "MORENA",
  "total_estados": 22,
  "estados": [
    {
      "ESTADO": "CDMX",
      "partido_ganador": "MORENA",
      "senadores_mr": 2,
      "PORCENTAJE": 0.52
    },
    ...
  ]
}
```

**UI Sugerida:**
- Tabla con columnas: Estado | Partido Ganador | Senadores MR | % Votos
- Colorear filas según partido ganador
- Total de estados ganados al pie de tabla
- Botón "Exportar a CSV" (usar formato=csv)

---

#### 3️⃣ **Edición Manual de Estados - Senado**
```http
POST /editar/estados_senado
Body: {
  "anio": 2024,
  "plan": "vigente",
  "estados_manuales": {
    "MORENA": ["CDMX", "MEXICO", "VERACRUZ"],
    "PAN": ["GUANAJUATO", "JALISCO"],
    "PRI": ["COAHUILA"]
  },
  "aplicar_topes": true
}
```

**¿Para qué sirve?**
Permite al usuario asignar manualmente qué partido gana en cada estado.

**UI Sugerida:**
- Mapa interactivo de México o tabla de 32 estados
- Cada estado tiene dropdown para seleccionar partido ganador
- Botón "Calcular resultado" que hace POST
- Mostrar resultado con mayorías detectadas automáticamente

---

#### 4️⃣ **Exportar Escenario - Senado**
```http
POST /exportar/escenario_senado
Body: {
  "nombre_escenario": "MORENA_Mayoria_2024",
  "estados_por_partido": {
    "MORENA": ["CDMX", "MEXICO"],
    "PAN": ["GUANAJUATO"]
  },
  "descripcion": "Escenario de mayoría simple"
}
```

**¿Para qué sirve?**
Guarda un escenario como archivo CSV para uso posterior.

**UI Sugerida:**
- Botón "Guardar escenario" después de editar estados
- Modal que pide:
  - Nombre del escenario
  - Descripción (opcional)
- Descarga archivo CSV automáticamente

---

#### 5️⃣ **Importar Escenario - Senado**
```http
POST /importar/escenario_senado
Body: {
  "csv_content": "# Escenario: Test\nestado,partido_ganador,senadores_mr\nCDMX,MORENA,2\n..."
}
```

**¿Para qué sirve?**
Carga un escenario previamente guardado desde CSV.

**UI Sugerida:**
- Botón "Cargar escenario"
- Input file que acepta .csv
- Leer contenido del archivo y enviarlo como string en csv_content
- Mostrar metadata del escenario (nombre, fecha, descripción)
- Botón "Aplicar escenario" que llama a /editar/estados_senado con los datos importados

---

### **DIPUTADOS** (2 endpoints nuevos, similar a Senado)

#### 6️⃣ **Generar Tabla de Distritos - Diputados**
```http
GET /generar/tabla_distritos_diputados?partido=MORENA&votos_porcentaje=45&anio=2024
```

Similar a la tabla de estados, pero con 300 distritos.

**UI Sugerida:**
- Tabla agrupada por estado
- Filtros por estado
- Paginación (300 filas)

---

#### 7️⃣ **Exportar Escenario - Diputados**
```http
POST /exportar/escenario_diputados
```

Igual que Senado, pero para distritos.

---

#### 8️⃣ **Importar Escenario - Diputados**
```http
POST /importar/escenario_diputados
```

Igual que Senado, pero para distritos.

---

## 🎨 DISEÑO E INDICADORES VISUALES

### **Badges de Mayoría (REQUERIDO)**

```javascript
// Función para determinar estilo según mayorías
function getMayoriaStyle(mayorias) {
  if (mayorias.mayoria_calificada.alcanzada) {
    return {
      color: '#0066CC',      // Azul
      bgColor: '#E6F2FF',    // Azul claro
      icon: '🔵',
      text: 'Mayoría Calificada (2/3)',
      partido: mayorias.mayoria_calificada.partido,
      escanos: mayorias.mayoria_calificada.escanos,
      warning: mayorias.mayoria_calificada.es_coalicion ? '⚠️ Solo con coalición' : null
    };
  } else if (mayorias.mayoria_simple.alcanzada) {
    return {
      color: '#00AA00',      // Verde
      bgColor: '#E6FFE6',    // Verde claro
      icon: '🟢',
      text: 'Mayoría Simple',
      partido: mayorias.mayoria_simple.partido,
      escanos: mayorias.mayoria_simple.escanos,
      warning: mayorias.mayoria_simple.es_coalicion ? '⚠️ Solo con coalición' : null
    };
  } else {
    return {
      color: '#999999',      // Gris
      bgColor: '#F5F5F5',    // Gris claro
      icon: '⚪',
      text: 'Sin Mayoría',
      partido: null,
      escanos: 0,
      warning: '⚠️ Congreso/Senado dividido - Se requieren pactos'
    };
  }
}
```

### **Ejemplos de UI**

#### Opción 1: Badge compacto
```html
<div class="mayoria-badge" style="background: #E6F2FF; border-left: 4px solid #0066CC;">
  <span class="icon">🔵</span>
  <span class="text">Mayoría Calificada</span>
  <span class="detail">MORENA - 270 escaños</span>
</div>
```

#### Opción 2: Card completo
```html
<div class="mayoria-card calificada">
  <div class="header">
    <span class="icon">🔵</span>
    <h3>Mayoría Calificada</h3>
  </div>
  <div class="body">
    <p class="partido">MORENA</p>
    <p class="escanos">270 de 400 escaños (67.5%)</p>
    <p class="umbral">Umbral: 267 escaños (66.67%)</p>
  </div>
</div>
```

#### Opción 3: Con advertencia de coalición
```html
<div class="mayoria-badge simple coalicion">
  <span class="icon">🟢</span>
  <span class="text">Mayoría Simple</span>
  <span class="detail">MORENA+PT+PVEM - 210 escaños</span>
  <div class="warning">
    <span>⚠️</span>
    <span>Solo alcanzada con coalición</span>
  </div>
</div>
```

---

## 📱 FLUJO DE USUARIO TÍPICO

### **Escenario 1: Calcular mayoría forzada**
1. Usuario selecciona partido (MORENA)
2. Selecciona tipo de mayoría (Simple)
3. Click en "Calcular"
4. Frontend llama: `GET /calcular/mayoria_forzada_senado?partido=MORENA&tipo_mayoria=simple`
5. Mostrar resultado: "Necesitas 52% de votos, ganar 24 estados"
6. Botón "Ver detalle de estados" → llama a `/generar/tabla_estados_senado?partido=MORENA&votos_porcentaje=52`
7. Muestra tabla de 24 estados que ganaría

### **Escenario 2: Edición manual**
1. Usuario ve tabla/mapa de 32 estados
2. Asigna manualmente partidos a cada estado
3. Click en "Calcular resultado"
4. Frontend llama: `POST /editar/estados_senado` con estados_manuales
5. Backend devuelve resultado con mayorías detectadas
6. Frontend muestra badge: 🔵 Mayoría Calificada - MORENA 86 senadores
7. Botón "Guardar escenario" → llama a `/exportar/escenario_senado`

### **Escenario 3: Cargar escenario guardado**
1. Usuario sube archivo CSV
2. Frontend lee contenido y llama: `POST /importar/escenario_senado`
3. Backend devuelve metadata y distribución
4. Frontend muestra: "Escenario: MORENA_Mayoria_2024 (guardado el 15/01/2026)"
5. Botón "Aplicar" → llama a `/editar/estados_senado` con los datos importados

---

## 🔧 DATOS TÉCNICOS IMPORTANTES

### **Umbrales de Mayoría**

| Cámara | Total Escaños | Mayoría Simple | Mayoría Calificada |
|--------|--------------|----------------|-------------------|
| Diputados | 400 | >200 (50%) | ≥267 (66.67%, 2/3) |
| Senado | 128 | >64 (50%) | ≥86 (66.67%, 2/3) |

### **Tope Constitucional del 8%**
- Máximo de sobrerrepresentación: **58%** (50% + 8%)
- Si un partido obtiene 50% votos, máximo puede tener 58% escaños
- Cuando `aplicar_topes=true`, el backend limita automáticamente

### **Planes Electorales Senado**
- **Vigente**: 64 MR + 32 PM + 32 RP = 128 senadores
- **Plan A**: 96 RP puro (reforma completa)
- **Plan C**: 64 MR+PM sin RP (solo mayoría y primera minoría)

### **Planes Electorales Diputados**
- **Vigente**: 300 MR + 100 RP = 400 (con topes)
- **Plan 200/200**: 200 MR + 200 RP
- **Plan 240/160**: 240 MR + 160 RP

---

## 📦 CHECKLIST DE IMPLEMENTACIÓN

### **Fase 1: Integrar detección automática (PRIORITARIO)**
- [ ] Verificar que `/procesar/diputados` y `/procesar/senado` **ya devuelven** objeto `mayorias`
- [ ] Crear componente `MayoriaBadge` que muestre el badge según mayorias
- [ ] Integrar badge en resultados de Diputados
- [ ] Integrar badge en resultados de Senado
- [ ] Probar casos: mayoría calificada, simple, coalición, sin mayoría

### **Fase 2: Motor de mayoría forzada**
- [ ] Crear página/sección "Calcular Mayoría Forzada"
- [ ] Formulario para Senado (partido, tipo, plan, topes)
- [ ] Formulario para Diputados (partido, tipo, plan, topes)
- [ ] Integrar llamadas a `/calcular/mayoria_forzada_senado`
- [ ] Mostrar resultados en cards/badges

### **Fase 3: Tablas generadas**
- [ ] Integrar `/generar/tabla_estados_senado`
- [ ] Tabla responsive con 32 estados
- [ ] Integrar `/generar/tabla_distritos_diputados`
- [ ] Tabla con 300 distritos (paginada)
- [ ] Opción de exportar a CSV desde tabla

### **Fase 4: Edición manual**
- [ ] UI para asignar partidos a estados (mapa o tabla)
- [ ] Integrar `POST /editar/estados_senado`
- [ ] UI para asignar partidos a distritos
- [ ] Validación: no permitir estados/distritos duplicados

### **Fase 5: Exportar/Importar escenarios**
- [ ] Botón "Guardar escenario" → `/exportar/escenario_senado`
- [ ] Botón "Cargar escenario" → input file + `/importar/escenario_senado`
- [ ] Mostrar metadata del escenario (nombre, fecha, descripción)
- [ ] Mismo flujo para Diputados

---

## 🚨 ERRORES COMUNES A EVITAR

1. **NO asumir que mayorias no existe**
   - ✅ Los endpoints `/procesar/*` **ya devuelven** el objeto mayorias
   - ❌ No hacer parsing manual de escaños

2. **NO ignorar el campo `es_coalicion`**
   - ✅ Si `es_coalicion=true`, mostrar warning "⚠️ Solo con coalición"
   - ❌ No asumir que un partido solo siempre tiene mayoría

3. **NO confundir umbrales**
   - ✅ Simple: >64 (Senado), >200 (Diputados)
   - ✅ Calificada: ≥86 (Senado), ≥267 (Diputados)
   - ❌ No usar 50% de escaños como umbral calificado

4. **NO olvidar limpiar comas en CSV importado**
   - ✅ El backend ya limpia con `.rstrip(',')` - no te preocupes
   - ✅ Solo enviar el contenido completo del archivo como string

5. **NO usar IDs de partidos incorrectos**
   - ✅ Usar: "MORENA", "PAN", "PRI", "PRD", "PT", "PVEM", "MC"
   - ❌ No usar minúsculas o abreviaciones diferentes

---

## 🎯 PRIORIDADES

### **ALTA PRIORIDAD (Hacer YA)**
1. ✅ Integrar badges de mayorías en `/procesar/diputados` y `/procesar/senado` (5 min)
2. ✅ Crear formulario "Calcular Mayoría Forzada" para Senado (30 min)
3. ✅ Integrar tabla de estados ganados (20 min)

### **MEDIA PRIORIDAD**
4. Edición manual de estados con dropdowns (1 hora)
5. Exportar/importar escenarios (45 min)

### **BAJA PRIORIDAD (Nice to have)**
6. Mapa interactivo de México
7. Animaciones en cambio de mayorías
8. Comparación de escenarios lado a lado

---

## 📞 PREGUNTAS FRECUENTES

**P: ¿Los endpoints actuales ya funcionan?**
R: SÍ. Los 8 endpoints nuevos están probados y funcionando al 100%.

**P: ¿Necesito modificar el backend?**
R: NO. Todo está listo, solo necesitas consumir los endpoints.

**P: ¿Qué pasa si un CSV tiene formato incorrecto?**
R: El backend devuelve error 400 con mensaje descriptivo. Muéstralo al usuario.

**P: ¿Puedo probar los endpoints directamente?**
R: SÍ. Levanta el servidor con `uvicorn main:app --reload` y usa Postman/Thunder Client.

**P: ¿Los colores son obligatorios?**
R: Son sugerencias. Puedes ajustar según tu diseño, pero mantén la lógica:
- Azul = Calificada
- Verde = Simple
- Gris = Sin mayoría

---

## ✅ TESTING RÁPIDO

### **Probar detección de mayorías:**
```bash
# Endpoint que YA devuelve mayorias
POST http://localhost:8000/procesar/senado
Body: {
  "anio": 2024,
  "plan": "vigente",
  "aplicar_topes": true
}

# Buscar en response:
{
  "mayorias": {
    "mayoria_simple": { "alcanzada": true/false, "partido": "..." },
    "mayoria_calificada": { "alcanzada": true/false, "partido": "..." }
  }
}
```

### **Probar mayoría forzada:**
```bash
GET http://localhost:8000/calcular/mayoria_forzada_senado?partido=MORENA&tipo_mayoria=simple&plan=vigente

# Esperado:
{
  "viable": true,
  "senadores_necesarios": 65,
  "estados_ganados": 24,
  "votos_porcentaje": 52
}
```

---

## 🎉 RESUMEN

**Backend está 100% LISTO:**
- ✅ 8 endpoints nuevos funcionando
- ✅ Detección automática de mayorías
- ✅ Motor de mayoría forzada con método Hare realista
- ✅ Export/import de escenarios
- ✅ Documentación completa

**Tu trabajo en Frontend:**
1. Integrar badges de mayorías (YA está en el response)
2. Crear formularios para llamar a los 8 endpoints nuevos
3. Mostrar resultados con UI bonita
4. Implementar export/import de CSV

**Tiempo estimado:** 4-6 horas de desarrollo frontend puro

---

## 📚 RECURSOS

- **Documentación completa:** `DOCUMENTACION_API.md`
- **Tests de backend:** `test_integracion_completa.py`
- **Servidor local:** `uvicorn main:app --reload --port 8000`
- **Base URL:** `http://localhost:8000`

---

🚀 **¡A IMPLEMENTAR!** Si tienes dudas, revisa `DOCUMENTACION_API.md` o prueba los endpoints directamente.
