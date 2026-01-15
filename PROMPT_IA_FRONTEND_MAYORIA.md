# 🤖 PROMPT PARA IA DEL FRONTEND

Copia y pega esto a tu IA del frontend:

---

## 🎯 INSTRUCCIONES PARA CORREGIR BOTONES DE MAYORÍA FORZADA

### **PROBLEMA:**
Los botones de "Forzar Mayoría" no funcionan porque:
1. Endpoint incorrecto para diputados
2. Falta parámetro `anio`

### **SOLUCIÓN:**

**1. Cambiar el endpoint de diputados:**
```javascript
// ❌ ANTES (Incorrecto)
const url = `${API_URL}/calcular/mayoria_forzada_diputados?...`

// ✅ DESPUÉS (Correcto)
const url = `${API_URL}/calcular/mayoria_forzada?...`
```

**2. Agregar parámetro `anio=2024`:**
```javascript
// Para DIPUTADOS
const url = `${API_URL}/calcular/mayoria_forzada?partido=${partido}&tipo_mayoria=${tipo}&plan=${plan}&aplicar_topes=true&anio=2024`;

// Para SENADO
const url = `${API_URL}/calcular/mayoria_forzada_senado?partido=${partido}&tipo_mayoria=${tipo}&plan=${plan}&aplicar_topes=true&anio=2024`;
```

---

## 📋 TABLA DE ENDPOINTS

| Cámara | Endpoint Correcto | Parámetros |
|--------|------------------|------------|
| **Diputados** | `/calcular/mayoria_forzada` | partido, tipo_mayoria, plan, aplicar_topes, **anio** |
| **Senado** | `/calcular/mayoria_forzada_senado` | partido, tipo_mayoria, plan, aplicar_topes, **anio** |

---

## 🔧 CÓDIGO COMPLETO PARA COPIAR

```javascript
const API_URL = 'https://back-electoral.onrender.com';

async function forzarMayoria(camara, partido, tipoMayoria) {
  // 1. Construir endpoint correcto
  const endpoint = camara === 'senado' 
    ? '/calcular/mayoria_forzada_senado'
    : '/calcular/mayoria_forzada';  // ⬅️ SIN _diputados
  
  // 2. Construir parámetros (incluir anio)
  const params = new URLSearchParams({
    partido: partido,
    tipo_mayoria: tipoMayoria,
    plan: 'vigente',
    aplicar_topes: 'true',
    anio: '2024'  // ⬅️ AGREGAR ESTO
  });
  
  const url = `${API_URL}${endpoint}?${params.toString()}`;
  
  console.log('[API] Llamando:', url);
  
  try {
    // 3. Hacer request
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    const data = await response.json();
    console.log('[API] Respuesta:', data);
    
    // 4. Verificar si es viable
    if (!data.viable) {
      alert(`⚠️ ${data.mensaje}`);
      return null;
    }
    
    // 5. Actualizar UI con seat_chart completo
    actualizarTablaPartidos(data.seat_chart);  // ← Ya viene completo
    actualizarSeatChart(data.seat_chart);
    actualizarKPIs(data.kpis);
    
    // 6. Mostrar mensaje de éxito
    const escanos = camara === 'senado' 
      ? data.senadores_obtenidos 
      : data.diputados_obtenidos;
    
    alert(`✅ ${partido} alcanza mayoría ${tipoMayoria} con ${data.votos_porcentaje}% de votos (${escanos} escaños)`);
    
    return data;
    
  } catch (error) {
    console.error('[API] Error:', error);
    alert(`❌ Error al calcular mayoría: ${error.message}`);
    return null;
  }
}

// EJEMPLO DE USO:
// forzarMayoria('diputados', 'MORENA', 'simple');
// forzarMayoria('senado', 'PAN', 'calificada');
```

---

## 📊 ESTRUCTURA DE RESPUESTA

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
    }
    // ... resto de partidos
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

## 🧪 TEST ANTES DE IMPLEMENTAR

Abre la consola del navegador y ejecuta:

```javascript
(async () => {
  const test = await fetch('https://back-electoral.onrender.com/calcular/mayoria_forzada?partido=MORENA&tipo_mayoria=simple&plan=vigente&aplicar_topes=true&anio=2024')
    .then(r => r.json());
  
  console.log('✅ Viable:', test.viable);
  console.log('📊 Escaños:', test.diputados_obtenidos);
  console.log('📈 Votos %:', test.votos_porcentaje);
  console.log('🎨 Partidos:', test.seat_chart.length);
  
  if (test.viable && test.seat_chart) {
    console.log('🎉 BACKEND FUNCIONANDO CORRECTAMENTE');
  }
})();
```

---

## ✅ CHECKLIST

- [ ] Cambiar `/calcular/mayoria_forzada_diputados` → `/calcular/mayoria_forzada`
- [ ] Agregar parámetro `anio: '2024'` en ambos endpoints
- [ ] Verificar que `seat_chart` se use directamente (ya viene completo)
- [ ] Manejar caso `viable: false` con `data.mensaje`
- [ ] Probar en consola antes de implementar

---

## 🎯 RESUMEN

**Cambios necesarios:**
1. Endpoint de diputados: Quitar `_diputados`
2. Agregar `anio=2024` a AMBOS endpoints
3. Usar `data.seat_chart` directamente (ya NO necesitas POST adicional)

**Eso es TODO.** El backend ya devuelve todo lo necesario. 🚀
