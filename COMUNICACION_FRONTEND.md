# 📢 COMUNICACIÓN AL FRONTEND: Correcciones en Backend Electoral

## ✅ CAMBIOS IMPLEMENTADOS (17 Enero 2026)

### 1. **Sliders de Distritos MR AHORA FUNCIONAN** ✨

**ANTES (❌ ROTO):**
```javascript
// Frontend enviaba:
{
  "mr_distritos_manuales": '{"MORENA":51,"PAN":8,...}'
}

// Backend devolvía (REESCALADO):
{
  "seat_chart": {"MORENA": 247, "PAN": 32, ...}  // ❌ Ignoró valores!
}
```

**AHORA (✅ FUNCIONA):**
```javascript
// Frontend envía:
{
  "mr_distritos_manuales": '{"MORENA":51,"PAN":8,...}'
}

// Backend devuelve (EXACTO):
{
  "seat_chart": {"MORENA": 51, "PAN": 8, ...}  // ✅ Respeta valores!
}
```

**Acción Frontend:** ✅ **NO REQUIERE CAMBIOS** - Los sliders que ya tienes funcionarán automáticamente

---

### 2. **Tabla Geográfica Ahora Escala Correctamente** 📊

**ANTES (❌ ROTO):**
```javascript
// Con 60 MR total:
meta.distritos_por_estado:
{
  "AGUASCALIENTES": 300,  // ❌ Siempre 300!
  "BAJA CALIFORNIA": 300,
  ...
}
```

**AHORA (✅ FUNCIONA):**
```javascript
// Con 60 MR total:
meta.distritos_por_estado:
{
  "AGUASCALIENTES": 1,   // ✅ Escalado a 60 total
  "BAJA CALIFORNIA": 2,
  "JALISCO": 4,
  ...
  // Suma total = 60
}
```

**Acción Frontend:** ✅ **NO REQUIERE CAMBIOS** - La columna de totales se actualizará sola

---

### 3. **Límites por Estado Validados** 🛡️

**ANTES (❌ PROBLEMA):**
```javascript
// Con 60 MR, Campeche = 1 distrito escalado
meta.mr_por_estado:
{
  "CAMPECHE": {
    "MC": 1,
    "MORENA": 2  // ❌ Total = 3 > 1 (inválido!)
  }
}
```

**AHORA (✅ FUNCIONA):**
```javascript
// Con 60 MR, Campeche = 1 distrito escalado
meta.mr_por_estado:
{
  "CAMPECHE": {
    "MC": 1,     // ✅ Total = 1 (válido)
    "MORENA": 0
  }
}
```

**Acción Frontend:** ✅ **NO REQUIERE CAMBIOS** - Los datos ya vienen validados

---

### 4. **Sliders MICRO (por estado) AHORA FUNCIONAN** 🎯

**NUEVO:** Ahora puedes enviar ajustes estado por estado

**Cómo funciona:**

```javascript
// Frontend puede enviar:
{
  "mr_por_estado": {
    "14": {  // Jalisco (ID=14)
      "MORENA": 13,  // +1 distrito
      "PAN": 7       // -1 distrito
    }
    // Solo envías los estados que cambiaste!
  }
}

// Backend devuelve:
{
  "seat_chart": {
    "MORENA": 51,  // Total nacional actualizado
    "PAN": 32
  },
  "meta": {
    "mr_por_estado": {
      "JALISCO": {
        "MORENA": 13,  // ✅ Refleja tu cambio
        "PAN": 7
      },
      "AGUASCALIENTES": {...},  // Otros estados calculados
      ...
    }
  }
}
```

**Acción Frontend:** ⚠️ **OPCIONAL** - Si quieres implementar sliders por estado individual

---

## 🔧 PARÁMETROS DEL BACKEND (Sin cambios)

Los endpoints siguen aceptando los mismos parámetros:

### Opción 1: MR Totales (Sliders actuales)
```javascript
POST /procesar/diputados

{
  "anio": 2024,
  "plan": "vigente",
  "mr_distritos_manuales": '{"MORENA":51,"PAN":8,...}'  // ✅ Funciona ahora
}
```

### Opción 2: MR por Estado (Sliders micro - NUEVO)
```javascript
POST /procesar/diputados

{
  "anio": 2024,
  "plan": "vigente",
  "mr_por_estado": {
    "14": {"MORENA":13,"PAN":7},  // Jalisco
    "15": {"MORENA":23,"PAN":1}   // Estado de México
  }
}
```

**Nota:** Puedes usar **nombres** o **IDs** de estados (backend acepta ambos):
```javascript
// Con nombres (también funciona):
{
  "mr_por_estado": {
    "Jalisco": {"MORENA":13,"PAN":7},
    "México": {"MORENA":23,"PAN":1}
  }
}
```

---

## 📊 ESTRUCTURA DE RESPUESTA (Sin cambios)

La respuesta sigue teniendo la misma estructura:

```javascript
{
  "seat_chart": {
    "data": [
      {
        "partido": "MORENA",
        "mr": 51,        // ✅ Ahora respeta tus valores
        "rp": 87,
        "total": 138,
        "color": "#A4193D"
      },
      ...
    ]
  },
  "kpis": {...},
  "meta": {
    "mr_por_estado": {     // ✅ Ahora escala correctamente
      "AGUASCALIENTES": {"PAN": 2, "MORENA": 1, ...},
      "JALISCO": {"MORENA": 13, "PAN": 7, ...},  // ✅ Refleja cambios micro
      ...
    },
    "distritos_por_estado": {  // ✅ Ahora escala según plan
      "AGUASCALIENTES": 3,     // (o 1 si plan tiene 60 MR)
      "JALISCO": 20,           // (o 4 si plan tiene 60 MR)
      ...
    }
  }
}
```

---

## ✅ CHECKLIST PARA FRONTEND

### Verificaciones Básicas (Sin cambiar código)

1. **Test de sliders MR totales:**
   - Subir MORENA a 51 en sliders principales
   - Hacer POST con `mr_distritos_manuales`
   - Verificar que `seat_chart.data[].mr` devuelve 51 (no 247) ✅

2. **Test de tabla geográfica:**
   - Seleccionar plan con 60 MR (ej: "personalizado")
   - Verificar que `meta.distritos_por_estado` suma 60 (no 300) ✅
   - Verificar que ningún estado excede su límite ✅

3. **Test de consistencia:**
   - Para cada estado en `meta.mr_por_estado`
   - Sumar MR de todos los partidos
   - Verificar que ≤ `meta.distritos_por_estado[estado]` ✅

### Funcionalidad Nueva (Opcional)

4. **Sliders MICRO por estado:**
   - Implementar UI para ajustar Jalisco: MORENA +1, PAN -1
   - Enviar `mr_por_estado` con solo Jalisco
   - Verificar que `meta.mr_por_estado.JALISCO` refleja el cambio ✅

---

## 🚀 RECOMENDACIONES

### 1. **Validación Client-Side (Opcional)**

Puedes agregar validación en frontend antes de enviar:

```javascript
// Validar que sliders no excedan límites
function validarMRPorEstado(mrPorEstado, distritosPorEstado) {
  for (const [estado, partidos] of Object.entries(mrPorEstado)) {
    const total = Object.values(partidos).reduce((a, b) => a + b, 0);
    const limite = distritosPorEstado[estado];
    
    if (total > limite) {
      console.warn(`⚠️ ${estado}: ${total} MR > ${limite} distritos`);
      // Backend lo ajustará automáticamente, pero es mejor prevenirlo
    }
  }
}
```

### 2. **Mensajes de Usuario**

Si implementas sliders micro, considera mostrar:

```javascript
// Cuando usuario ajusta Jalisco:
"Jalisco: MORENA 12 → 13 (+1), PAN 8 → 7 (-1)"
"Recalculando totales nacionales..."
```

### 3. **Logs de Debugging**

El backend ahora devuelve logs útiles. Si ves problemas, revisa:

```javascript
// En respuesta del backend:
console.log(response.meta.trace);  // Logs de procesamiento

// Buscar mensajes como:
"✅ MR manuales del frontend (63) - NO se reescalarán"
"🎯 Sliders MICRO: 1 estados con ajustes manuales"
"🔧 AJUSTANDO CAMPECHE: 3 MR → 2 distritos"
```

---

## 🐛 PROBLEMAS CONOCIDOS RESUELTOS

### ❌ ANTES
1. Sliders de MR se reescalaban (51 → 247)
2. Tabla geográfica siempre mostraba 300 distritos
3. Estados podían exceder límites (MC=1+MORENA=2=3 en Campeche con límite 1)
4. Sliders por estado no funcionaban

### ✅ AHORA
1. ✅ Sliders de MR se respetan exactamente
2. ✅ Tabla geográfica escala según plan (60, 100, 200, 300)
3. ✅ Estados respetan límites automáticamente
4. ✅ Sliders por estado funcionales

---

## 📝 EJEMPLOS DE USO

### Ejemplo 1: Slider Global (Ya implementado)

```javascript
// Usuario mueve slider: MORENA 51 distritos
const payload = {
  anio: 2024,
  plan: "vigente",
  mr_distritos_manuales: JSON.stringify({
    MORENA: 51,
    PAN: 8,
    PRI: 1,
    MC: 2,
    PVEM: 1,
    PT: 0,
    PRD: 0
  })
};

// Backend devuelve exactamente 51 para MORENA ✅
```

### Ejemplo 2: Slider Micro - Jalisco (Nuevo opcional)

```javascript
// Usuario ajusta solo Jalisco en tabla geográfica
const payload = {
  anio: 2024,
  plan: "vigente",
  mr_por_estado: JSON.stringify({
    "14": {  // Jalisco
      MORENA: 13,  // +1
      PAN: 7       // -1
    }
  })
};

// Backend recalcula totales nacionales
// y devuelve Jalisco actualizado en meta.mr_por_estado ✅
```

---

## ⚡ PERFORMANCE

No hay cambios de performance significativos. Los ajustes son computacionalmente ligeros:

- Escalado de estados: O(32) - una pasada por 32 estados
- Validación de límites: O(32 * 7) - 32 estados × 7 partidos
- Sliders micro: O(1) - solo estados modificados

---

## 🔗 COMPATIBILIDAD

**Versiones anteriores del frontend:** ✅ **100% compatibles**

- Si no envías `mr_distritos_manuales` o `mr_por_estado`, todo funciona como antes
- Respuestas tienen la misma estructura
- Solo cambia el contenido (ahora correcto)

---

## 📞 SOPORTE

Si tienes problemas:

1. **Verificar logs del backend** (ahora más verbosos)
2. **Revisar tests:** `test_sliders_micro.py`, `test_mr_manuales_respetados.py`
3. **Consultar documentación:** `FIX_MR_MANUALES_REESCALADOS.md`

---

## 🎯 RESUMEN EJECUTIVO

**¿Necesita cambios el frontend?** 

**NO** para funcionalidad básica. Los sliders que ya tienes funcionarán correctamente ahora.

**SÍ (opcional)** si quieres implementar:
- Sliders por estado individual (micro-ajustes geográficos)
- Validación client-side de límites
- Mensajes de feedback más detallados

**Beneficios inmediatos sin cambios:**
1. ✅ Sliders MR respetan valores del usuario
2. ✅ Tabla geográfica escala correctamente
3. ✅ Datos siempre válidos (sin estados excediendo límites)
4. ✅ Totales y distribuciones consistentes

---

**Fecha:** 17 Enero 2026  
**Backend Version:** Compatible con todas las versiones de frontend  
**Breaking Changes:** Ninguno  
**Nuevas Features:** Sliders MICRO (opcional)
