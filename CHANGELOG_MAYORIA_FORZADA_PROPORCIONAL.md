# 📝 Changelog - Mayoría Forzada: Redistribución Proporcional

**Fecha**: 19 de enero de 2026  
**Versión**: 2.0  
**Prioridad**: 🔴 ALTA

---

## 🎯 Cambios Implementados

### 1️⃣ **Redistribución Proporcional de Votos** ✅

**ANTES** ❌:
```python
# Ponía coalición en 0% y daba todo a oposición
PT: 3.83% → 0.00%
PVEM: 5.75% → 0.00%
PAN: 21.09% → 35.62%  # Recibía TODO
```

**AHORA** ✅:
```python
# Redistribución proporcional entre TODOS los partidos
MORENA: 42.49% → 47.50% (+5.01%)
PAN: 21.09% → 18.64% (-2.45%)
PRI: 17.24% → 15.23% (-2.01%)
MC: 11.50% → 10.16% (-1.34%)
PVEM: 5.75% → 5.08% (-0.67%)  # ✅ Baja pero NO llega a 0
PT: 3.83% → 3.38% (-0.45%)     # ✅ Baja pero NO llega a 0
```

**Ventaja**: Más realista - refleja una redistribución natural de votos, no una eliminación total de partidos.

---

### 2️⃣ **Actualización Automática de Sliders** 📊

La respuesta del backend ahora incluye:

```json
{
  "viable": true,
  "votos_necesarios": 47.50,
  
  // 🆕 Para actualizar sliders de votos
  "votos_custom": {
    "MORENA": 47.50,
    "PAN": 18.64,
    "PRI": 15.23,
    "MC": 10.16,
    "PVEM": 5.08,
    "PT": 3.38
  },
  
  // 🆕 Para actualizar sliders de MR
  "mr_distritos_manuales": {
    "MORENA": 162,
    "PAN": 60,
    "PRI": 46,
    "MC": 32,
    "PT": 0,      // Coalición se anula
    "PVEM": 0     // Coalición se anula
  }
}
```

**Frontend debe**:
1. Leer `votos_custom` y actualizar sliders de porcentaje de votos
2. Leer `mr_distritos_manuales` y actualizar tabla de distritos MR
3. Disparar eventos `input` para que se re-renderice la UI

---

## 📂 Archivos Modificados

### Backend
- ✅ `engine/calcular_mayoria_forzada_v2.py` (líneas 454-480)
  - Cambió lógica de redistribución de votos
  - Ahora distribuye proporcionalmente entre TODOS
  - Eliminó la lógica que ponía coalición en 0%

### Documentación
- ✅ `GUIA_FRONTEND_MAYORIA_FORZADA.md`
  - Agregada sección de redistribución proporcional
  - Agregadas instrucciones para actualizar sliders
  - Actualizado checklist con nuevos requisitos
  - Ejemplos de código para actualizar UI

---

## 🧪 Pruebas Realizadas

### Test 1: MORENA Mayoría Simple
```
✅ MORENA: 47.50% votos, 162 MR, ~95 RP = 251+ escaños
✅ PT: 3.38% (bajó de 3.83%, NO llegó a 0%)
✅ PVEM: 5.08% (bajó de 5.75%, NO llegó a 0%)
✅ Redistribución proporcional verificada
```

### Test 2: PAN Mayoría Simple
```
✅ PAN: 47.50% votos, 235 MR
✅ PRI (coalición): 11.20% (bajó de 17.24%, NO llegó a 0%)
✅ Todos los demás partidos bajaron proporcionalmente
```

### Test 3: MC Mayoría Simple (sin coalición)
```
✅ MC: 47.50% votos
✅ No hay partners de coalición que anular
✅ Todos los partidos bajan proporcionalmente
```

### Test 4: Mayoría Calificada sin topes
```
✅ MORENA: 63.00% votos, 212 MR
✅ Redistribución proporcional funciona igual
✅ PT y PVEM bajan pero no llegan a 0%
```

---

## 📋 Tareas para el Frontend

### 🔴 Crítico
- [ ] Actualizar sliders de votos con `data.votos_custom`
- [ ] Actualizar sliders de MR con `data.mr_distritos_manuales`
- [ ] Disparar eventos `input` después de actualizar sliders
- [ ] Verificar que el seat chart se actualiza correctamente

### 🟡 Importante
- [ ] Agregar animación visual cuando se actualizan sliders
- [ ] Mostrar tooltip explicando redistribución proporcional
- [ ] Botón "Aplicar Mayoría" para confirmar antes de actualizar

### 🟢 Opcional
- [ ] Mostrar tabla comparativa: votos antes vs después
- [ ] Gráfica de barras mostrando redistribución
- [ ] Highlight de partidos que bajaron/subieron

---

## 🎨 Ejemplo de Implementación Frontend

### JavaScript - Actualizar Sliders

```javascript
function aplicarMayoriaForzada(data) {
  if (!data.viable) {
    alert(`❌ ${data.razon}`);
    return;
  }

  // 1. Actualizar sliders de votos
  if (data.votos_custom) {
    Object.entries(data.votos_custom).forEach(([partido, porcentaje]) => {
      const slider = document.querySelector(`[data-partido="${partido}"][data-tipo="votos"]`);
      if (slider) {
        slider.value = porcentaje;
        slider.dispatchEvent(new Event('input', { bubbles: true }));
      }
    });
  }

  // 2. Actualizar tabla de MR
  if (data.mr_distritos_manuales) {
    Object.entries(data.mr_distritos_manuales).forEach(([partido, distritos]) => {
      const input = document.querySelector(`[data-partido="${partido}"][data-tipo="mr"]`);
      if (input) {
        input.value = distritos;
        input.dispatchEvent(new Event('change', { bubbles: true }));
      }
    });
  }

  // 3. Mostrar confirmación
  mostrarNotificacion(`✅ Mayoría forzada aplicada: ${data.partido} con ${data.votos_necesarios.toFixed(2)}%`);
}
```

### React - Ejemplo Completo

```jsx
const aplicarMayoriaForzada = (data) => {
  if (!data.viable) {
    setError(data.razon);
    return;
  }

  // Actualizar state de votos
  setVotosPorPartido(data.votos_custom);
  
  // Actualizar state de MR
  setMrPorPartido(data.mr_distritos_manuales);
  
  // Actualizar UI
  setResultadoMayoria({
    partido: data.partido,
    votos: data.votos_necesarios,
    mr: data.mr_distritos,
    rp: data.rp_estimado
  });
};
```

---

## 🚨 Breaking Changes

### ⚠️ Cambio en la estructura de votos

**ANTES**: Algunos partidos podían llegar a 0%
```json
{
  "votos_custom": {
    "MORENA": 47.50,
    "PT": 0.00,      // ❌ Llegaba a 0
    "PVEM": 0.00     // ❌ Llegaba a 0
  }
}
```

**AHORA**: Todos los partidos mantienen un porcentaje proporcional
```json
{
  "votos_custom": {
    "MORENA": 47.50,
    "PT": 3.38,      // ✅ Baja pero mantiene %
    "PVEM": 5.08     // ✅ Baja pero mantiene %
  }
}
```

**Impacto en Frontend**:
- NO afecta si ya procesabas `votos_custom` correctamente
- SÍ afecta si asumías que partidos de coalición llegarían a 0%

---

## ✅ Beneficios

1. **Más realista**: Refleja competencia electoral natural
2. **Mejor UX**: Usuarios ven redistribución clara y proporcional
3. **Consistencia**: Misma lógica en votos que en distritos MR
4. **Transparencia**: Fácil de explicar "todos bajan un poco proporcionalmente"

---

## 📞 Soporte

Si tienes dudas:
1. Revisa `GUIA_FRONTEND_MAYORIA_FORZADA.md`
2. Ejecuta `python test_todos_partidos_mayorias.py` para ver ejemplos
3. Consulta ejemplos de código en esta guía

---

## 🎯 Resumen de 30 Segundos

**Qué cambió**: Los votos ahora se redistribuyen **proporcionalmente** entre TODOS los partidos, en lugar de poner la coalición en 0% y darle todo a la oposición.

**Qué hacer**: 
1. Usar `data.votos_custom` para actualizar sliders de votos
2. Usar `data.mr_distritos_manuales` para actualizar tabla MR
3. Verificar que los sliders disparen eventos de actualización

**Urgencia**: 🔴 Alta - Afecta comportamiento visible al usuario
