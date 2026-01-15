# ✅ ACTUALIZACIÓN: Endpoints de Mayoría Forzada con Seat Chart Completo

## 🎯 CAMBIOS IMPLEMENTADOS

Los endpoints `/calcular/mayoria_forzada` y `/calcular/mayoria_forzada_senado` ahora **EJECUTAN EL SISTEMA ELECTORAL COMPLETO** y devuelven:

✅ `seat_chart` completo con TODOS los partidos recalculados  
✅ `kpis` recalculados (Gallagher, ratio, total_votos)  
✅ Todos los partidos ajustados proporcionalmente  
✅ Listo para usar directamente en el frontend  

---

## 🔄 COMPORTAMIENTO NUEVO

### **Antes (solo configuración):**
```json
{
  "viable": true,
  "mr_distritos_manuales": {...},
  "votos_custom": {...},
  "detalle": {...}
}
```

### **Ahora (sistema completo ejecutado):**
```json
{
  "viable": true,
  "diputados_necesarios": 251,
  "diputados_obtenidos": 251,
  "votos_porcentaje": 47.0,
  "mr_asignados": 158,
  "rp_asignados": 93,
  
  "seat_chart": [
    {
      "party": "MORENA",
      "seats": 251,
      "mr_seats": 158,
      "rp_seats": 93,
      "votes_percent": 47.0,
      "color": "#941B1E"
    },
    {
      "party": "PAN",
      "seats": 85,
      "mr_seats": 42,
      "rp_seats": 43,
      "votes_percent": 18.5,
      "color": "#0059B3"
    },
    // ... resto de partidos RECALCULADOS
  ],
  
  "kpis": {
    "total_escanos": 500,
    "gallagher": 8.45,
    "ratio_promedio": 0.912,
    "total_votos": 45678901
  }
}
```

---

## 📡 ENDPOINTS ACTUALIZADOS

### **1. Mayoría Forzada - DIPUTADOS**

```
GET /calcular/mayoria_forzada
```

**Parámetros:**
- `partido` (string): MORENA, PAN, PRI, MC, PVEM, PT
- `tipo_mayoria` (string): "simple" o "calificada"
- `plan` (string): "vigente", "200_200_sin_topes", "240_160_sin_topes", etc.
- `aplicar_topes` (bool): true/false
- `votos_base` (string, opcional): JSON con distribución base
- `anio` (int): 2018, 2021, 2024

**Respuesta exitosa:**
```json
{
  "viable": true,
  "diputados_necesarios": 251,        // Umbral mayoría simple
  "diputados_obtenidos": 251,         // Alcanzado exactamente
  "votos_porcentaje": 47.0,           // % necesario
  "mr_asignados": 158,
  "rp_asignados": 93,
  "partido": "MORENA",
  "plan": "vigente",
  "tipo_mayoria": "simple",
  
  "seat_chart": [...],                // ← COMPLETO
  "kpis": {...},                      // ← COMPLETO
  
  "advertencias": [
    "Requiere votación alta (47.0%) - históricamente difícil de alcanzar"
  ],
  "metodo": "Redistritación geográfica realista (Hare + eficiencia 1.1)"
}
```

**Respuesta no viable (mayoría calificada con topes):**
```json
{
  "viable": false,
  "mensaje": "Mayoría calificada imposible con topes del 60%",
  "diputados_necesarios": 334,
  "max_posible": 300,
  "diputados_obtenidos": 0,
  "votos_porcentaje": null
}
```

---

### **2. Mayoría Forzada - SENADO**

```
GET /calcular/mayoria_forzada_senado
```

**Parámetros:**
- `partido` (string): MORENA, PAN, PRI, MC, PVEM, PT
- `tipo_mayoria` (string): "simple" o "calificada"
- `plan` (string): "vigente", "plan_a", "plan_c"
- `aplicar_topes` (bool): true/false
- `anio` (int): 2018, 2024

**Respuesta exitosa:**
```json
{
  "viable": true,
  "senadores_necesarios": 65,         // Umbral mayoría simple
  "senadores_obtenidos": 70,
  "votos_porcentaje": 45.0,
  "estados_ganados": 24,
  "mr_senadores": 48,
  "pm_senadores": 10,
  "rp_senadores": 12,
  "partido": "MORENA",
  "plan": "vigente",
  "tipo_mayoria": "simple",
  
  "seat_chart": [...],                // ← COMPLETO
  "kpis": {...},                      // ← COMPLETO
  
  "advertencias": [],
  "metodo": "Redistritación realista Senado"
}
```

---

## 🧮 ALGORITMO IMPLEMENTADO

### **Flujo Completo:**

```python
# PASO 1: Calcular configuración óptima
config = calcular_mayoria_forzada(
    partido="MORENA",
    tipo_mayoria="simple",
    mr_total=300,
    rp_total=100,
    aplicar_topes=True
)
# Retorna: votos_custom, mr_distritos_manuales, % necesario

# PASO 2: Ejecutar sistema electoral COMPLETO
resultado = procesar_diputados(
    anio=2024,
    plan="vigente",
    aplicar_topes=True,
    votos_custom=config['votos_custom'],          # ← Votos ajustados
    mr_distritos_manuales=config['mr_distritos_manuales']  # ← MR manual
)

# PASO 3: Extraer seat_chart completo
seat_chart = resultado['mayorias']['seat_chart']
# Contiene TODOS los partidos recalculados

# PASO 4: Devolver respuesta completa
return {
    "viable": True,
    "diputados_obtenidos": partido_data['seats'],
    "seat_chart": seat_chart,  # ← TODOS los partidos
    "kpis": resultado['mayorias']['kpis']  # ← KPIs completos
}
```

---

## 🧪 TESTS

### **Test 1: Mayoría Simple Diputados**

```bash
curl "https://back-electoral.onrender.com/calcular/mayoria_forzada?partido=MORENA&tipo_mayoria=simple&plan=vigente&aplicar_topes=true&anio=2024"
```

**Debe devolver:**
- `viable: true`
- `diputados_obtenidos: 251` (o más)
- `seat_chart` con 7-10 partidos
- `kpis.total_escanos: 500`

### **Test 2: Mayoría Simple Senado**

```bash
curl "https://back-electoral.onrender.com/calcular/mayoria_forzada_senado?partido=MORENA&tipo_mayoria=simple&plan=vigente&aplicar_topes=true&anio=2024"
```

**Debe devolver:**
- `viable: true`
- `senadores_obtenidos: 65` (o más)
- `seat_chart` con todos los partidos
- `kpis.total_escanos: 128`

### **Test 3: Mayoría Calificada con Topes (NO VIABLE)**

```bash
curl "https://back-electoral.onrender.com/calcular/mayoria_forzada?partido=PAN&tipo_mayoria=calificada&plan=vigente&aplicar_topes=true&anio=2024"
```

**Debe devolver:**
- `viable: false`
- `mensaje: "Mayoría calificada imposible con topes del 60%"`
- NO incluir `seat_chart`

---

## 📞 INTEGRACIÓN FRONTEND

### **Uso en JavaScript:**

```javascript
async function calcularYMostrarMayoria(camara, partido, tipoMayoria) {
  const endpoint = camara === 'senado' 
    ? '/calcular/mayoria_forzada_senado'
    : '/calcular/mayoria_forzada';
  
  const params = new URLSearchParams({
    partido: partido,
    tipo_mayoria: tipoMayoria,
    plan: 'vigente',
    aplicar_topes: 'true',
    anio: '2024'
  });
  
  const response = await fetch(`${API_URL}${endpoint}?${params}`);
  const data = await response.json();
  
  if (!data.viable) {
    alert(data.mensaje);
    return;
  }
  
  // ✅ Actualizar tabla directamente con seat_chart
  actualizarTablaPartidos(data.seat_chart);
  
  // ✅ Actualizar seat chart visual
  renderizarSeatChart(data.seat_chart);
  
  // ✅ Actualizar KPIs
  mostrarKPIs(data.kpis);
  
  // ✅ Mostrar resultado
  console.log(`${partido} alcanza mayoría ${tipoMayoria} con ${data.votos_porcentaje}% de votos`);
  console.log(`Escaños: ${data.diputados_obtenidos || data.senadores_obtenidos}`);
}
```

### **Sin Cambios Necesarios:**

El frontend ya existente puede consumir estos endpoints directamente:
- `seat_chart` tiene el mismo formato que `/procesar/diputados`
- `kpis` tiene el mismo formato
- Los datos son drop-in replacement

---

## ⚠️ CASOS ESPECIALES

### **1. Mayoría Calificada con Topes**

**Configuración:**
```
aplicar_topes=true
tipo_mayoria="calificada"
```

**Resultado:**
```json
{
  "viable": false,
  "mensaje": "Mayoría calificada (334 escaños) es IMPOSIBLE con topes del 8%. Requeriría 59.3% de votos (históricamente inalcanzable). Para usar mayoría calificada, DESACTIVE los topes (aplicar_topes=False)"
}
```

### **2. Votos Base Custom**

**Ejemplo:**
```bash
curl "https://back-electoral.onrender.com/calcular/mayoria_forzada?partido=PAN&tipo_mayoria=simple&plan=vigente&votos_base=%7B%22MORENA%22:30,%22PAN%22:35,%22PRI%22:20%7D"
```

El sistema redistribuye proporcionalmente desde esa base.

---

## 📊 ESTRUCTURA COMPLETA DE RESPUESTA

### **Diputados (Mayoría Simple Viable):**

```json
{
  "viable": true,
  "diputados_necesarios": 251,
  "diputados_obtenidos": 251,
  "votos_porcentaje": 47.0,
  "mr_asignados": 158,
  "rp_asignados": 93,
  "partido": "MORENA",
  "plan": "vigente",
  "tipo_mayoria": "simple",
  
  "seat_chart": [
    {
      "party": "MORENA",
      "seats": 251,
      "mr_seats": 158,
      "rp_seats": 93,
      "votes_percent": 47.0,
      "color": "#941B1E"
    },
    {
      "party": "PAN",
      "seats": 85,
      "mr_seats": 42,
      "rp_seats": 43,
      "votes_percent": 18.5,
      "color": "#0059B3"
    },
    {
      "party": "PRI",
      "seats": 64,
      "mr_seats": 30,
      "rp_seats": 34,
      "votes_percent": 14.3,
      "color": "#E20613"
    },
    {
      "party": "MC",
      "seats": 50,
      "mr_seats": 25,
      "rp_seats": 25,
      "votes_percent": 12.0,
      "color": "#FF6600"
    },
    {
      "party": "PVEM",
      "seats": 30,
      "mr_seats": 15,
      "rp_seats": 15,
      "votes_percent": 5.5,
      "color": "#00A651"
    },
    {
      "party": "PT",
      "seats": 20,
      "mr_seats": 10,
      "rp_seats": 10,
      "votes_percent": 2.7,
      "color": "#B8181B"
    }
  ],
  
  "kpis": {
    "total_escanos": 500,
    "gallagher": 8.45,
    "ratio_promedio": 0.912,
    "total_votos": 45678901,
    "partidos_con_escanos": 6,
    "sobrerrepresentacion_maxima": 7.8
  },
  
  "advertencias": [
    "Requiere votación alta (47.0%) - históricamente difícil de alcanzar"
  ],
  "metodo": "Redistritación geográfica realista (Hare + eficiencia 1.1)"
}
```

### **Senado (Mayoría Simple Viable):**

```json
{
  "viable": true,
  "senadores_necesarios": 65,
  "senadores_obtenidos": 70,
  "votos_porcentaje": 45.0,
  "estados_ganados": 24,
  "mr_senadores": 48,
  "pm_senadores": 10,
  "rp_senadores": 12,
  "partido": "MORENA",
  "plan": "vigente",
  "tipo_mayoria": "simple",
  
  "seat_chart": [
    {
      "party": "MORENA",
      "seats": 70,
      "mr_seats": 48,
      "pm_seats": 10,
      "rp_seats": 12,
      "votes_percent": 45.0,
      "color": "#941B1E"
    },
    {
      "party": "PAN",
      "seats": 25,
      "mr_seats": 8,
      "pm_seats": 8,
      "rp_seats": 9,
      "votes_percent": 22.0,
      "color": "#0059B3"
    }
    // ... resto de partidos
  ],
  
  "kpis": {
    "total_escanos": 128,
    "gallagher": 6.2,
    "ratio_promedio": 0.95,
    "total_votos": 38567234
  },
  
  "advertencias": [],
  "metodo": "Redistritación realista Senado"
}
```

---

## ✅ VENTAJAS

1. **Frontend no cambia:** Usa `seat_chart` como siempre
2. **Todo en un request:** No necesita POST adicional
3. **Datos completos:** KPIs, advertencias, método usado
4. **Manejo de errores:** Respuesta clara cuando no es viable
5. **Flexibilidad:** Soporta votos_base custom

---

## 🎯 RESUMEN

| Antes | Ahora |
|-------|-------|
| Solo configuración JSON | **Sistema completo ejecutado** |
| Requería POST manual | **Un solo GET** |
| Sin seat_chart | **Seat chart completo** |
| Sin KPIs | **KPIs recalculados** |
| Datos parciales | **Respuesta completa** |

---

✅ **Los endpoints ya están listos para usar con el frontend.**  
✅ **Devuelven exactamente lo que necesitas: `seat_chart` + `kpis` completos.**
