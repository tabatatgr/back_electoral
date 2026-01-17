# 🐛 BUG CRÍTICO: Frontend enviando `mr_por_estado` con TODOS los valores en 0

## 📋 RESUMEN

Cuando ajustas distritos por estado usando las flechitas (↑↓), el **frontend está enviando correctamente la estructura de datos**, pero **con TODOS los valores en 0**.

## 🔍 EVIDENCIA DEL BUG

### Lo que el frontend DICE que envía:

```javascript
[STATES TABLE] 📡 Enviando distribución calculada desde estados: 
Object { MORENA: 43, PAN: 8, PRI: 0, MC: 0, PVEM: 1, PT: 0, PRD: 0 }

[STATES TABLE] 📊 Desglose por estado: 
Object { 
  AGUASCALIENTES: { PAN: 1, MORENA: 0, ... },
  "BAJA CALIFORNIA": { MORENA: 2, PAN: 0, ... },
  ...
}
```

### Lo que REALMENTE llega al backend:

```json
{
  "mr_distritos_manuales": "{\"MORENA\":0,\"PAN\":0,\"PRI\":0,\"MC\":0,\"PVEM\":0,\"PT\":0,\"PRD\":0}",
  "mr_por_estado": "{\"AGUASCALIENTES\":{\"PAN\":0,\"PRI\":0,\"PRD\":0,\"PVEM\":0,\"PT\":0,\"MC\":0,\"MORENA\":0},\"BAJA CALIFORNIA\":{\"PAN\":0,\"PRI\":0,\"PRD\":0,\"PVEM\":0,\"PT\":0,\"MC\":0,\"MORENA\":0},...}"
}
```

**TODOS LOS VALORES SON 0** ❌

## 🎯 CAUSA RAÍZ

El frontend está BORRANDO los valores de `mrPorEstado` justo antes de enviarlo al backend.

Mira este log del frontend:

```javascript
[DEBUG] 🔥 mrPorEstado ANTES de generar HTML: {
  "BAJA CALIFORNIA": {
    "PAN": 0,      // ← Debería ser 0
    "MORENA": 2    // ← ✅ CORRECTO
  },
  "CHIAPAS": {
    "MORENA": 2    // ← ✅ CORRECTO
  },
  ...
}
```

Pero luego:

```javascript
[MR SLIDERS] 📊 Totales calculados: 
Object { MC: 0, MORENA: 0, PAN: 0, PRD: 0, PRI: 0, PT: 0, PVEM: 0 }
                          ↑↑↑↑↑↑↑↑↑↑↑↑↑
                   TODOS EN 0 ❌
```

## 🔧 SOLUCIÓN REQUERIDA

### 1. Verificar `adjustStateDistrict()` en `ControlSidebar.js`

La función `adjustStateDistrict()` está actualizando `this.mrPorEstado` correctamente:

```javascript
[STATES TABLE] 📊 MORENA en BAJA CALIFORNIA: 1 → 2
[STATES TABLE] 🔥 Después del ajuste - MORENA en BAJA CALIFORNIA: 2 // ✅ CORRECTO
[STATES TABLE] 🔥 Estado completo BAJA CALIFORNIA: 
Object { PAN: 0, PRI: 0, PRD: 0, PVEM: 0, PT: 0, MC: 0, MORENA: 2 }  // ✅ CORRECTO
```

### 2. Verificar `sendManualDistribution()` o similar

Hay una función que:
1. **Lee** `this.mrPorEstado` (✅ tiene valores correctos)
2. **Calcula** totales por partido
3. **Envía** al backend

**EN ALGÚN PUNTO** entre leer y enviar, **se están borrando los valores**.

### 3. Buscar código que SOBRESCRIBA `mrPorEstado`

Probablemente hay algo como:

```javascript
// ❌ MAL - Esto borra los valores
this.mrPorEstado = {};
for (let estado in this.mrPorEstado) {
  for (let partido in PARTIDOS) {
    this.mrPorEstado[estado][partido] = 0;
  }
}
```

O algo que llame a `updateStatesTable()` con datos vacíos:

```javascript
// ❌ MAL - Esto regenera la tabla con 0s
this.updateStatesTable(datosVacíos);
```

## 🧪 PASOS PARA REPRODUCIR

1. Abrir DevTools → Console
2. Ir a la tabla geográfica
3. Hacer clic en ↑ de MORENA en BAJA CALIFORNIA
4. Ver en consola:
   ```
   [STATES TABLE] 📊 MORENA en BAJA CALIFORNIA: 1 → 2  ← ✅ Se actualiza
   [MR SLIDERS] 📊 Totales calculados: { MORENA: 0 }    ← ❌ Se borra
   ```
5. Ver en Network → Request body:
   ```json
   "mr_distritos_manuales": "{\"MORENA\":0,...}"  // ← ❌ TODO EN 0
   ```

## ✅ CÓMO DEBE FUNCIONAR

### Flujo correcto:

1. Usuario hace clic en ↑ MORENA en BAJA CALIFORNIA
2. `adjustStateDistrict()` actualiza:
   ```javascript
   this.mrPorEstado["BAJA CALIFORNIA"]["MORENA"] = 2
   ```
3. Se calcula totales:
   ```javascript
   const totales = { MORENA: 2, PAN: 0, ... }  // ← ✅ Suma correcta
   ```
4. Se envía al backend:
   ```json
   {
     "mr_distritos_manuales": "{\"MORENA\":2,...}",  // ← ✅ Valores correctos
     "mr_por_estado": "{\"BAJA CALIFORNIA\":{\"MORENA\":2},...}"  // ← ✅ Desglose correcto
   }
   ```

### Lo que está pasando:

1. ✅ `adjustStateDistrict()` actualiza correctamente
2. ❌ **ALGO** sobrescribe `this.mrPorEstado` con 0s
3. ❌ Se calcula totales con 0s
4. ❌ Se envía al backend con 0s

## 🔍 DÓNDE BUSCAR

### Archivos a revisar:

1. **`ControlSidebar.js`**:
   - Función `adjustStateDistrict()`
   - Función `sendManualDistribution()` o similar
   - Función `updateStatesTable()`
   - Event listeners de las flechitas

2. **`script.js`**:
   - Función `cargarSimulacion()`
   - Código que prepara el `body` del POST
   - Cualquier lugar que acceda a `sidebar.mrPorEstado`

### Código sospechoso:

```javascript
// ❌ BUSCAR ESTO (o similar):
this.mrPorEstado = this.initializeEmptyMrPorEstado();
this.mrPorEstado = {};
this.resetMrPorEstado();
Object.keys(this.mrPorEstado).forEach(estado => { ... = 0 });
```

## 📝 TESTS PARA VALIDAR LA CORRECCIÓN

Después de corregir el bug, verificar que:

### Test 1: Log de totales
```javascript
console.log("[TEST] Totales ANTES de enviar:", totales);
// Esperado: { MORENA: 45, PAN: 7, ... }
// NO: { MORENA: 0, PAN: 0, ... }
```

### Test 2: Body del request
```javascript
console.log("[TEST] Body completo:", JSON.parse(body.mr_por_estado));
// Esperado: { "BAJA CALIFORNIA": { "MORENA": 2 }, ... }
// NO: { "BAJA CALIFORNIA": { "MORENA": 0 }, ... }
```

### Test 3: Respuesta del backend
```javascript
// SI el backend recibe 0s, devolverá este error:
{
  "detail": "Error en mr_por_estado: todos los estados tienen 0 distritos. Verifica que el frontend esté enviando los valores correctos de la tabla geográfica."
}
```

## 🎯 ACCIÓN INMEDIATA

1. **BUSCAR** en `ControlSidebar.js` dónde se sobrescriben los valores de `mrPorEstado`
2. **ELIMINAR O COMENTAR** ese código
3. **PROBAR** ajustar un distrito y verificar que el backend NO devuelva el error
4. **VERIFICAR** que la respuesta del backend contenga los valores correctos

## 🔗 REFERENCIAS

- **Log completo del error**: Ver DevTools Console al hacer clic en flechitas
- **Request body**: Ver DevTools Network → Request Payload
- **Backend error**: Ver respuesta 400 con el mensaje de error descriptivo

---

**Fecha**: 17 Enero 2026  
**Autor**: Pablo (Backend Team)  
**Prioridad**: 🔴 CRÍTICA
