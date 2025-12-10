# ❌ PROBLEMA IDENTIFICADO: Frontend no recibe campos MR/PM/RP

## 🔍 Diagnóstico

### Backend está funcionando correctamente ✅

El test confirma que el endpoint `/seat-chart/diputados/2024` **SÍ devuelve** los campos correctamente:

```json
{
  "party": "MORENA",
  "seats": 247,
  "color": "#8B2231",
  "percent": 42.49,
  "votes": 24286412,
  "mr": 160,    ✅
  "pm": 0,      ✅
  "rp": 87      ✅
}
```

### Frontend recibe datos incompletos ❌

Según los logs del navegador, el frontend recibe:

```json
{
  "party": "PAN",
  "seats": 54,
  "color": "#0055A5",
  "percent": 18,
  "votes": 10049424
  // ❌ Faltan: mr, pm, rp
}
```

## 🎯 Posibles causas

### 1. **El frontend está llamando a un endpoint diferente**
- Verifica en `script.js` línea 751 qué URL está usando
- Busca: `fetch(`, `axios.get(`, `$.ajax(`
- ¿Está llamando a `/seat-chart/` o a otro endpoint?

### 2. **Problema de caché del navegador**
- Los datos antiguos están cacheados
- **Solución rápida:** Hard refresh (Ctrl+Shift+R)
- **Solución permanente:** Verificar headers `Cache-Control`

### 3. **El frontend está usando datos de otra fuente**
- ¿Hay un localStorage o sessionStorage?
- ¿Hay datos pre-cargados en el HTML?

### 4. **Versión antigua del frontend**
- El código del frontend aún no está actualizado
- Necesita leer los nuevos campos del backend

## ✅ Acciones recomendadas

### Para el frontend:

1. **Hard refresh del navegador:**
   ```
   Ctrl + Shift + R (Windows/Linux)
   Cmd + Shift + R (Mac)
   ```

2. **Limpiar caché del navegador:**
   - Abrir DevTools (F12)
   - Ir a Network → Disable cache (checkbox)
   - Recargar página

3. **Verificar qué endpoint está llamando:**
   - En DevTools → Network
   - Filtrar por "seat-chart" o "diputados"
   - Ver qué URL se está llamando
   - Ver la respuesta completa (Response tab)

4. **Verificar el código JavaScript:**
   - Buscar en `script.js` o `ControlSidebar.js`
   - Encontrar donde se procesa `seat_chart`
   - Verificar que NO esté filtrando u omitiendo los campos `mr`, `pm`, `rp`

### Para debuggear:

En la consola del navegador, ejecuta:

```javascript
// Ver qué datos tiene realmente
console.log("seat_chart completo:", JSON.stringify(window.lastSeatChart || {}, null, 2));

// Hacer una petición manual
fetch('/seat-chart/diputados/2024?plan=vigente')
  .then(r => r.json())
  .then(data => {
    console.log("Respuesta directa del backend:");
    console.log(JSON.stringify(data.seats[0], null, 2));
  });
```

## 📋 Checklist

- [ ] Hard refresh del navegador (Ctrl+Shift+R)
- [ ] Verificar en Network DevTools qué endpoint se llama
- [ ] Verificar la respuesta completa en Network → Response tab
- [ ] Buscar en código JS si se están filtrando campos
- [ ] Verificar que no haya localStorage/sessionStorage con datos viejos
- [ ] Comprobar que el frontend esté leyendo la última versión

## 🚀 Una vez identificado el problema

Si el problema es caché:
- Hard refresh resolverá temporalmente
- Agregar `?v=timestamp` a las peticiones para forzar actualización

Si el problema es código frontend:
- Actualizar el código que procesa `seat_chart`
- Asegurarse de pasar `mr`, `pm`, `rp` a la tabla

Si el problema es endpoint diferente:
- Cambiar el frontend para que llame a `/seat-chart/diputados/{anio}`
- O actualizar el otro endpoint para incluir los campos
