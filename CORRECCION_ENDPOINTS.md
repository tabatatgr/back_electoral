# ✅ CORRECCIÓN: Endpoints Correctos del Backend + Sistema Completo

## 🎯 PROBLEMA IDENTIFICADO Y RESUELTO

**Problema 1:** Frontend buscaba `/calcular/mayoria_forzada_diputados`  
**Solución:** El endpoint correcto es `/calcular/mayoria_forzada` (sin `_diputados`)

**Problema 2:** Endpoints solo devolvían configuración, NO el sistema completo  
**Solución:** Ahora ejecutan `procesar_diputados()` completo y devuelven `seat_chart` + `kpis` ✅

---

## ✅ ENDPOINTS CORRECTOS CON SISTEMA COMPLETO

### **1. Mayoría Forzada - DIPUTADOS**

**URL CORRECTA:**
```
GET https://back-electoral.onrender.com/calcular/mayoria_forzada
```

**Parámetros:**
```javascript
?partido=MORENA
&tipo_mayoria=simple        // o "calificada"
&plan=vigente
&aplicar_topes=true
&votos_base=null            // opcional
&anio=2024                  // 2018, 2021, 2024
```

**Respuesta COMPLETA (CON SEAT CHART):**
```javascript
const url = `https://back-electoral.onrender.com/calcular/mayoria_forzada?partido=MORENA&tipo_mayoria=simple&plan=vigente&aplicar_topes=true&anio=2024`;

const response = await fetch(url);
const data = await response.json();

console.log(data);
// {
//   "viable": true,
//   "diputados_necesarios": 251,      // Umbral mayoría simple
//   "diputados_obtenidos": 251,       // Alcanzado
//   "votos_porcentaje": 47.0,         // % necesario
//   "mr_asignados": 158,
//   "rp_asignados": 93,
//   
//   // 🔑 NUEVO: Seat chart completo con TODOS los partidos
//   "seat_chart": [
//     {
//       "party": "MORENA",
//       "seats": 251,
//       "mr_seats": 158,
//       "rp_seats": 93,
//       "votes_percent": 47.0,
//       "color": "#941B1E"
//     },
//     {
//       "party": "PAN",
//       "seats": 85,
//       "mr_seats": 42,
//       "rp_seats": 43,
//       "votes_percent": 18.5,
//       "color": "#0059B3"
//     },
//     // ... resto de partidos RECALCULADOS
//   ],
//   
//   // 🔑 NUEVO: KPIs completos
//   "kpis": {
//     "total_escanos": 500,
//     "gallagher": 8.45,
//     "ratio_promedio": 0.912,
//     "total_votos": 45678901
//   }
// }
```

---

### **2. Mayoría Forzada - SENADO**

**URL CORRECTA:**
```
GET https://back-electoral.onrender.com/calcular/mayoria_forzada_senado
```

**Parámetros:**
```javascript
?partido=MORENA
&tipo_mayoria=simple        // o "calificada"
&plan=vigente
&aplicar_topes=true
&anio=2024
```

**Respuesta COMPLETA:**
```javascript
const url = `https://back-electoral.onrender.com/calcular/mayoria_forzada_senado?partido=MORENA&tipo_mayoria=simple&plan=vigente&aplicar_topes=true&anio=2024`;

const response = await fetch(url);
const data = await response.json();

console.log(data);
// {
//   "viable": true,
//   "senadores_necesarios": 65,
//   "senadores_obtenidos": 70,
//   "votos_porcentaje": 45.0,
//   "estados_ganados": 24,
//   "mr_senadores": 48,
//   "pm_senadores": 10,
//   "rp_senadores": 12,
//   
//   // 🔑 NUEVO: Seat chart completo con TODOS los partidos
//   "seat_chart": [
//     {
//       "party": "MORENA",
//       "seats": 70,
//       "mr_seats": 48,
//       "pm_seats": 10,
//       "rp_seats": 12,
//       "votes_percent": 45.0,
//       "color": "#941B1E"
//     },
//     {
//       "party": "PAN",
//       "seats": 25,
//       "mr_seats": 8,
//       "pm_seats": 8,
//       "rp_seats": 9,
//       "votes_percent": 22.0,
//       "color": "#0059B3"
//     }
//     // ... resto de partidos
//   ],
//   
//   // 🔑 NUEVO: KPIs completos
//   "kpis": {
//     "total_escanos": 128,
//     "gallagher": 6.2,
//     "ratio_promedio": 0.95,
//     "total_votos": 38567234
//   }
// }
```

---

## 🔧 CAMBIOS NECESARIOS EN EL FRONTEND

### **ANTES (Incorrecto):**
```javascript
// ❌ Diputados (endpoint incorrecto)
const urlDiputados = `${API_URL}/calcular/mayoria_forzada_diputados?...`;

// ✅ Senado (ya estaba correcto)
const urlSenado = `${API_URL}/calcular/mayoria_forzada_senado?...`;
```

### **DESPUÉS (Correcto):**
```javascript
// ✅ Diputados - SIN _diputados al final
const urlDiputados = `${API_URL}/calcular/mayoria_forzada?partido=${partido}&tipo_mayoria=${tipo}&plan=${plan}&aplicar_topes=true&anio=2024`;

// ✅ Senado - con _senado
const urlSenado = `${API_URL}/calcular/mayoria_forzada_senado?partido=${partido}&tipo_mayoria=${tipo}&plan=${plan}&aplicar_topes=true&anio=2024`;
```

---

## 📝 FUNCIÓN HELPER ACTUALIZADA

```javascript
const API_URL = 'https://back-electoral.onrender.com';

async function calcularMayoriaForzada(camara, partido, tipoMayoria, plan = 'vigente') {
  // Determinar endpoint según cámara
  const endpoint = camara === 'senado' 
    ? '/calcular/mayoria_forzada_senado'
    : '/calcular/mayoria_forzada';  // ⬅️ DIPUTADOS sin sufijo
  
  // Construir query params
  const params = new URLSearchParams({
    partido: partido,
    tipo_mayoria: tipoMayoria,
    plan: plan,
    aplicar_topes: 'true',
    anio: '2024'
  });
  
  const url = `${API_URL}${endpoint}?${params.toString()}`;
  
  console.log('[API] Calling:', url);
  
  try {
    const response = await fetch(url);
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }
    
    const data = await response.json();
    console.log('[API] Response:', data);
    
    if (!data.viable) {
      alert(`⚠️ ${data.mensaje}`);
      return null;
    }
    
    // ✅ AHORA INCLUYE SEAT CHART Y KPIS COMPLETOS
    return data;
    
  } catch (error) {
    console.error('[API] Error:', error);
    throw error;
  }
}

// USO CON ACTUALIZACIÓN AUTOMÁTICA:
async function calcularYActualizar(camara, partido, tipoMayoria) {
  const result = await calcularMayoriaForzada(camara, partido, tipoMayoria, 'vigente');
  
  if (!result) return;  // No viable
  
  // ✅ Actualizar tabla con seat_chart completo
  actualizarTablaPartidos(result.seat_chart);
  
  // ✅ Actualizar seat chart visual
  renderizarSeatChart(result.seat_chart);
  
  // ✅ Actualizar KPIs
  mostrarKPIs(result.kpis);
  
  // ✅ Mostrar mensaje de éxito
  const escanos = camara === 'senado' ? result.senadores_obtenidos : result.diputados_obtenidos;
  alert(`✅ ${partido} alcanza mayoría ${tipoMayoria} con ${result.votos_porcentaje}% de votos (${escanos} escaños)`);
}
```

---

## 🧪 TEST RÁPIDO

**Copia esto en la consola del navegador:**

```javascript
(async () => {
  const API = 'https://back-electoral.onrender.com';
  
  console.log('🧪 Test 1: Mayoría Forzada DIPUTADOS');
  const test1 = await fetch(`${API}/calcular/mayoria_forzada?partido=MORENA&tipo_mayoria=simple&plan=vigente&aplicar_topes=true&anio=2024`)
    .then(r => r.json())
    .catch(e => ({ error: e.message }));
  console.log('✅ Diputados:', test1);
  console.log('   - Viable:', test1.viable);
  console.log('   - Escaños:', test1.diputados_obtenidos);
  console.log('   - Votos %:', test1.votos_porcentaje);
  console.log('   - Partidos en seat_chart:', test1.seat_chart?.length);
  
  console.log('\n🧪 Test 2: Mayoría Forzada SENADO');
  const test2 = await fetch(`${API}/calcular/mayoria_forzada_senado?partido=MORENA&tipo_mayoria=simple&plan=vigente&aplicar_topes=true&anio=2024`)
    .then(r => r.json())
    .catch(e => ({ error: e.message }));
  console.log('✅ Senado:', test2);
  console.log('   - Viable:', test2.viable);
  console.log('   - Escaños:', test2.senadores_obtenidos);
  console.log('   - Votos %:', test2.votos_porcentaje);
  console.log('   - Partidos en seat_chart:', test2.seat_chart?.length);
  
  if (test1.error || test2.error) {
    console.error('❌ Algún endpoint falló');
  } else if (!test1.seat_chart || !test2.seat_chart) {
    console.warn('⚠️ Falta seat_chart - verificar backend');
  } else {
    console.log('🎉 AMBOS ENDPOINTS FUNCIONAN CON SEAT CHART COMPLETO');
  }
})();
```

---

## 📊 DIFERENCIAS CLAVE

### **Antes (Solo Configuración):**
```json
{
  "viable": true,
  "mr_distritos_manuales": {...},
  "votos_custom": {...},
  "detalle": {...}
}
```
**Problema:** Requería POST manual a `/procesar/diputados` para ver resultados

### **Ahora (Sistema Completo):**
```json
{
  "viable": true,
  "diputados_obtenidos": 251,
  "votos_porcentaje": 47.0,
  
  "seat_chart": [...],  // ← TODOS los partidos
  "kpis": {...}         // ← Gallagher, ratio, etc.
}
```
**Ventaja:** Un solo request devuelve TODO lo necesario ✅

---

## 🎯 RESUMEN

| Cámara | Endpoint Correcto | ❌ Endpoint Incorrecto | Devuelve |
|--------|------------------|----------------------|----------|
| **Diputados** | `/calcular/mayoria_forzada` | `/calcular/mayoria_forzada_diputados` | `seat_chart` + `kpis` ✅ |
| **Senado** | `/calcular/mayoria_forzada_senado` | (ya estaba correcto) | `seat_chart` + `kpis` ✅ |

---

## 🚀 ACCIÓN INMEDIATA

**1. En tu código del frontend, busca:**
```javascript
'/calcular/mayoria_forzada_diputados'
```

**2. Reemplázalo por:**
```javascript
'/calcular/mayoria_forzada'
```

**3. Agrega parámetro `anio`:**
```javascript
`${API_URL}/calcular/mayoria_forzada?partido=${partido}&tipo_mayoria=${tipo}&plan=${plan}&aplicar_topes=true&anio=2024`
```

**4. Usa directamente el `seat_chart` de la respuesta:**
```javascript
const data = await fetch(url).then(r => r.json());

// Ya NO necesitas hacer POST /procesar/diputados
// El seat_chart ya viene completo:
actualizarTabla(data.seat_chart);
actualizarKPIs(data.kpis);
```

---

✅ **Con estos cambios:**
- Los botones funcionarán inmediatamente
- El sistema recalcula TODO automáticamente
- Devuelve seat_chart + KPIs completos
- No necesitas POST adicionales

