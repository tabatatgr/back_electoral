# 🔧 DEBUG: Conexión Frontend → Backend

## 🚨 PROBLEMA REPORTADO
Los botones del frontend no funcionan. Las mayorías se muestran bien (colores OK), pero al mover botones o interactuar, no hay respuesta.

**Diagnóstico probable:** URLs incorrectas o CORS bloqueando peticiones.

---

## ✅ CHECKLIST DE VERIFICACIÓN

### 1️⃣ **Verificar URL del Backend**

**¿Qué URL estás usando en el frontend?**

❌ **INCORRECTO:**
```javascript
const API_URL = 'http://localhost:8000';  // ❌ Solo funciona en desarrollo local
const API_URL = 'https://back-electoral.onrender.com/';  // ❌ Slash final extra
```

✅ **CORRECTO:**
```javascript
// En producción (GitHub Pages)
const API_URL = 'https://back-electoral.onrender.com';

// En desarrollo local
const API_URL = 'http://localhost:8000';

// MEJOR: Detectar automáticamente
const API_URL = window.location.hostname === 'localhost' 
  ? 'http://localhost:8000' 
  : 'https://back-electoral.onrender.com';
```

---

### 2️⃣ **Verificar CORS en el Navegador**

Abre la **Consola del Navegador** (F12) y busca errores tipo:

```
❌ Access to fetch at 'https://back-electoral.onrender.com/...' 
   has been blocked by CORS policy
```

**Si ves este error:**

1. El backend YA tiene CORS configurado (ver `main.py` líneas 240-256)
2. Pero puede estar **dormido** (Render FREE se duerme después de 15 min)

**SOLUCIÓN:**
```javascript
// Agregar timeout y retry
async function fetchWithRetry(url, options, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      console.log(`[FETCH] Intentando: ${url}`);
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`[FETCH] Intento ${i + 1} falló:`, error);
      
      // Si es el último intento, lanzar error
      if (i === retries - 1) throw error;
      
      // Esperar antes de reintentar (Render tarda ~30s en despertar)
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  }
}

// Usar así:
const data = await fetchWithRetry(`${API_URL}/procesar/diputados`, {
  method: 'POST',
  body: JSON.stringify({ anio: 2024, plan: 'vigente' })
});
```

---

### 3️⃣ **Verificar Endpoints Correctos**

**ENDPOINTS QUE YA FUNCIONAN:**

| Funcionalidad | Método | Endpoint | Body |
|---------------|--------|----------|------|
| Procesar Diputados | POST | `/procesar/diputados` | `{ anio, plan, aplicar_topes, ... }` |
| Procesar Senado | POST | `/procesar/senado` | `{ anio, plan, aplicar_topes }` |
| Calcular Mayoría Forzada Senado | GET | `/calcular/mayoria_forzada_senado?partido=MORENA&tipo_mayoria=simple&plan=vigente` | - |
| Tabla Estados Senado | GET | `/generar/tabla_estados_senado?partido=MORENA&votos_porcentaje=52` | - |
| Editar Estados Manualmente | POST | `/editar/estados_senado` | `{ estados_manuales: {...} }` |

**ERRORES COMUNES:**

❌ **Endpoint mal escrito:**
```javascript
fetch(`${API_URL}/calcular-mayoria-forzada-senado`)  // ❌ Guiones en lugar de underscores
```

✅ **Correcto:**
```javascript
fetch(`${API_URL}/calcular/mayoria_forzada_senado?partido=MORENA&tipo_mayoria=simple&plan=vigente`)
```

❌ **Olvidar método POST:**
```javascript
fetch(`${API_URL}/procesar/diputados`)  // ❌ Default es GET
```

✅ **Correcto:**
```javascript
fetch(`${API_URL}/procesar/diputados`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ anio: 2024, plan: 'vigente', aplicar_topes: true })
})
```

---

### 4️⃣ **Verificar Parámetros Obligatorios**

**Endpoint `/procesar/diputados` (POST):**

```javascript
// MÍNIMO REQUERIDO:
{
  "anio": 2024,
  "plan": "vigente"
}

// COMPLETO (recomendado):
{
  "anio": 2024,
  "plan": "vigente",
  "aplicar_topes": true,
  "sistema": "mixto",
  "mr_seats": 300,
  "rp_seats": 100,
  "umbral": 0.03,
  "reparto_method": "hare",
  "usar_coaliciones": true
}
```

**Endpoint `/calcular/mayoria_forzada_senado` (GET):**

```javascript
// Query params OBLIGATORIOS:
?partido=MORENA
&tipo_mayoria=simple    // o "calificada"
&plan=vigente

// COMPLETO:
?partido=MORENA
&tipo_mayoria=simple
&plan=vigente
&aplicar_topes=true
&anio=2024
```

---

### 5️⃣ **Debugging con Console Logs**

Agrega estos logs en el frontend:

```javascript
// ANTES de hacer fetch
console.log('[DEBUG] URL completa:', `${API_URL}/procesar/diputados`);
console.log('[DEBUG] Body:', JSON.stringify(requestBody, null, 2));

// Después de fetch
fetch(url, options)
  .then(response => {
    console.log('[DEBUG] Status:', response.status);
    console.log('[DEBUG] Headers:', Object.fromEntries(response.headers.entries()));
    return response.json();
  })
  .then(data => {
    console.log('[DEBUG] Response data:', data);
    
    // Verificar que mayorias existe
    if (data.mayorias) {
      console.log('✅ Mayorías detectadas:', data.mayorias);
    } else {
      console.warn('⚠️ Response sin campo mayorias');
    }
  })
  .catch(error => {
    console.error('[ERROR]', error);
    alert(`Error: ${error.message}`);
  });
```

---

### 6️⃣ **Verificar que el Backend Responde**

**Test rápido desde el navegador:**

1. Abre la consola (F12)
2. Pega esto:

```javascript
fetch('https://back-electoral.onrender.com/')
  .then(r => r.json())
  .then(d => console.log('Backend responde:', d))
  .catch(e => console.error('Backend NO responde:', e));
```

**Respuesta esperada:**
```json
{
  "message": "Backend Electoral API v2.0",
  "status": "running"
}
```

**Si NO responde:**
- Render está dormido (espera 30-60 segundos)
- Render crasheó por falta de RAM
- URL incorrecta

---

### 7️⃣ **Ejemplo Completo Funcionando**

**Botón "Calcular Mayoría Forzada":**

```html
<button id="btnCalcularMayoria">Calcular Mayoría Forzada</button>
<div id="resultado"></div>

<script>
const API_URL = 'https://back-electoral.onrender.com';

document.getElementById('btnCalcularMayoria').addEventListener('click', async () => {
  console.log('[CLICK] Botón presionado');
  
  const partido = 'MORENA';
  const tipo = 'simple';
  const plan = 'vigente';
  
  const url = `${API_URL}/calcular/mayoria_forzada_senado?partido=${partido}&tipo_mayoria=${tipo}&plan=${plan}`;
  
  console.log('[FETCH] URL:', url);
  
  try {
    const response = await fetch(url);
    
    console.log('[RESPONSE] Status:', response.status);
    
    if (!response.ok) {
      throw new Error(`Error ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('[DATA]', data);
    
    // Mostrar resultado
    document.getElementById('resultado').innerHTML = `
      <div class="alert alert-success">
        <h3>Mayoría ${tipo === 'simple' ? 'Simple' : 'Calificada'}</h3>
        <p>Necesitas: <strong>${data.votos_porcentaje}%</strong> de votos</p>
        <p>Ganar: <strong>${data.estados_ganados}</strong> de 32 estados</p>
        <p>Obtendrás: <strong>${data.senadores_obtenidos}</strong> senadores</p>
      </div>
    `;
  } catch (error) {
    console.error('[ERROR]', error);
    document.getElementById('resultado').innerHTML = `
      <div class="alert alert-danger">
        Error: ${error.message}
      </div>
    `;
  }
});
</script>
```

---

### 8️⃣ **Verificar Response del Backend**

Cuando llamas a `/procesar/diputados`, **DEBES recibir esto:**

```json
{
  "tot": {
    "MORENA": 248,
    "PAN": 72,
    "PRI": 35,
    ...
  },
  "mayorias": {                    // ⬅️ ESTO DEBE EXISTIR
    "total_escanos": 400,
    "mayoria_simple": {
      "umbral": 201,
      "alcanzada": true,
      "partido": "MORENA",
      "escanos": 248,
      "es_coalicion": false
    },
    "mayoria_calificada": {
      "umbral": 267,
      "alcanzada": false,
      "partido": null,
      "escanos": 0,
      "es_coalicion": false
    }
  },
  "metadata": { ... },
  "kpis": { ... }
}
```

**Si `mayorias` NO existe:**
- Backend antiguo (necesita actualización)
- Error en el endpoint

---

## 🎯 SOLUCIÓN PASO A PASO

### **PASO 1: Verificar que Render está despierto**

```javascript
// Agregar esto al inicio de tu app
async function despertarBackend() {
  console.log('🔄 Despertando backend...');
  try {
    const response = await fetch('https://back-electoral.onrender.com/', {
      method: 'GET'
    });
    console.log('✅ Backend despierto');
  } catch (error) {
    console.warn('⚠️ Backend tardando en despertar, reintentando...');
    await new Promise(r => setTimeout(r, 3000));
    await despertarBackend();
  }
}

// Llamar al cargar la página
despertarBackend();
```

### **PASO 2: Crear función helper para fetch**

```javascript
async function callBackend(endpoint, method = 'GET', body = null) {
  const url = `https://back-electoral.onrender.com${endpoint}`;
  
  console.log(`[API] ${method} ${url}`);
  if (body) console.log('[API] Body:', body);
  
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json'
    }
  };
  
  if (body) {
    options.body = JSON.stringify(body);
  }
  
  try {
    const response = await fetch(url, options);
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('[API ERROR]', error);
    throw error;
  }
}

// Usar así:
const data = await callBackend('/procesar/diputados', 'POST', {
  anio: 2024,
  plan: 'vigente',
  aplicar_topes: true
});
```

### **PASO 3: Agregar Loading Indicator**

```javascript
function showLoading() {
  document.getElementById('btnCalcular').disabled = true;
  document.getElementById('btnCalcular').textContent = 'Calculando...';
}

function hideLoading() {
  document.getElementById('btnCalcular').disabled = false;
  document.getElementById('btnCalcular').textContent = 'Calcular';
}

// Usar:
document.getElementById('btnCalcular').addEventListener('click', async () => {
  showLoading();
  
  try {
    const data = await callBackend('/calcular/mayoria_forzada_senado?partido=MORENA&tipo_mayoria=simple&plan=vigente');
    mostrarResultado(data);
  } catch (error) {
    mostrarError(error.message);
  } finally {
    hideLoading();
  }
});
```

---

## 🚨 ERRORES MÁS COMUNES Y SOLUCIONES

### Error 1: "Failed to fetch"
**Causa:** Render dormido o URL incorrecta  
**Solución:** Esperar 30s y reintentar, verificar URL

### Error 2: "CORS policy"
**Causa:** Backend no responde o error 503  
**Solución:** Despertar Render visitando https://back-electoral.onrender.com/

### Error 3: "404 Not Found"
**Causa:** Endpoint mal escrito  
**Solución:** Verificar `/calcular/mayoria_forzada_senado` (con underscores, no guiones)

### Error 4: "422 Unprocessable Entity"
**Causa:** Parámetros incorrectos  
**Solución:** Verificar query params o body según endpoint

### Error 5: "Response sin mayorias"
**Causa:** Backend antiguo  
**Solución:** Hacer push del nuevo backend con mayorías incluidas

---

## ✅ TEST FINAL

**Copia esto en la consola del navegador:**

```javascript
(async () => {
  const API_URL = 'https://back-electoral.onrender.com';
  
  console.log('🧪 TEST 1: Backend despierto');
  const test1 = await fetch(`${API_URL}/`).then(r => r.json());
  console.log('✅ Test 1:', test1);
  
  console.log('🧪 TEST 2: Procesar Diputados');
  const test2 = await fetch(`${API_URL}/procesar/diputados`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ anio: 2024, plan: 'vigente', aplicar_topes: true })
  }).then(r => r.json());
  console.log('✅ Test 2 - Mayorías:', test2.mayorias);
  
  console.log('🧪 TEST 3: Mayoría Forzada');
  const test3 = await fetch(`${API_URL}/calcular/mayoria_forzada_senado?partido=MORENA&tipo_mayoria=simple&plan=vigente`)
    .then(r => r.json());
  console.log('✅ Test 3:', test3);
  
  console.log('🎉 TODOS LOS TESTS PASARON');
})();
```

**Si los 3 tests pasan → El backend funciona, el problema está en el frontend**  
**Si algún test falla → El problema es del backend (Render dormido o crasheado)**

---

## 📋 RESUMEN PARA TU IA DEL FRONT

**Dile esto a tu IA:**

> Los botones no funcionan. Necesito que:
> 
> 1. Verifiques la URL del backend: `https://back-electoral.onrender.com` (sin slash final)
> 2. Agregues `console.log()` antes y después de cada `fetch()`
> 3. Verifiques que los endpoints tengan UNDERSCORES: `/calcular/mayoria_forzada_senado`
> 4. Para POST, agregues `method: 'POST'` y `Content-Type: application/json`
> 5. Agregues manejo de errores con `.catch()`
> 6. Pruebes con el TEST FINAL que está en `DEBUG_CONEXION_FRONTEND.md`
> 
> El backend YA funciona (lo probamos en Postman). El problema es cómo el frontend hace las peticiones.

---

🚀 **Con esto, tu IA del front debería poder identificar y corregir el problema!**
