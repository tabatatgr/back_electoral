# 🚨 URGENTE: Botones no funcionan - Corregir conexión Frontend → Backend

## PROBLEMA
Los badges de mayorías se ven bien (colores OK), pero los botones no hacen nada al darles click.

## DIAGNÓSTICO
Probablemente las peticiones `fetch()` NO están llegando al backend o tienen errores.

## SOLUCIÓN RÁPIDA

### 1. VERIFICAR URL DEL BACKEND

```javascript
// ✅ CORRECTO:
const API_URL = 'https://back-electoral.onrender.com';  // SIN slash final

// ❌ INCORRECTO:
const API_URL = 'https://back-electoral.onrender.com/';  // CON slash
const API_URL = 'http://localhost:8000';  // Solo funciona en local
```

### 2. AGREGAR LOGS EN CADA BOTÓN

```javascript
document.getElementById('btnCalcular').addEventListener('click', async () => {
  console.log('[CLICK] Botón presionado'); // ⬅️ Agregar esto
  
  const url = `${API_URL}/calcular/mayoria_forzada_senado?partido=MORENA&tipo_mayoria=simple&plan=vigente`;
  console.log('[FETCH] URL:', url); // ⬅️ Y esto
  
  try {
    const response = await fetch(url);
    console.log('[RESPONSE] Status:', response.status); // ⬅️ Y esto
    
    const data = await response.json();
    console.log('[DATA]', data); // ⬅️ Y esto
    
    // Mostrar resultado...
  } catch (error) {
    console.error('[ERROR]', error); // ⬅️ Y esto
    alert('Error: ' + error.message); // ⬅️ Mostrar error al usuario
  }
});
```

### 3. VERIFICAR ENDPOINTS CORRECTOS

**IMPORTANTE:** Todos los endpoints usan **UNDERSCORES** (_), NO guiones (-)

✅ **CORRECTO:**
```javascript
// GET
fetch(`${API_URL}/calcular/mayoria_forzada_senado?partido=MORENA&tipo_mayoria=simple&plan=vigente`)

// POST
fetch(`${API_URL}/procesar/diputados`, {
  method: 'POST',  // ⬅️ OBLIGATORIO para POST
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ anio: 2024, plan: 'vigente', aplicar_topes: true })
})
```

❌ **INCORRECTO:**
```javascript
fetch(`${API_URL}/calcular-mayoria-forzada-senado`)  // ❌ Guiones
fetch(`${API_URL}/procesar/diputados`)  // ❌ Falta method: 'POST'
```

### 4. TEST RÁPIDO EN CONSOLA

**Abre la consola del navegador (F12) y pega esto:**

```javascript
(async () => {
  const API = 'https://back-electoral.onrender.com';
  
  // Test 1: Backend despierto
  const test1 = await fetch(`${API}/`).then(r => r.json());
  console.log('✅ Backend:', test1);
  
  // Test 2: Mayoría forzada
  const test2 = await fetch(`${API}/calcular/mayoria_forzada_senado?partido=MORENA&tipo_mayoria=simple&plan=vigente`)
    .then(r => r.json());
  console.log('✅ Mayoría:', test2);
  
  console.log('🎉 BACKEND FUNCIONA');
})();
```

**Si este test funciona → El problema es cómo están escritos tus botones**  
**Si este test falla → Render está dormido (espera 30 segundos y reintenta)**

### 5. TEMPLATE BOTÓN FUNCIONANDO

```html
<button id="btnMayoria">Calcular Mayoría Forzada</button>
<div id="resultado"></div>

<script>
const API_URL = 'https://back-electoral.onrender.com';

document.getElementById('btnMayoria').addEventListener('click', async () => {
  console.log('🔘 Botón clickeado');
  
  const partido = 'MORENA';
  const tipo = 'simple'; // o 'calificada'
  const plan = 'vigente';
  
  const url = `${API_URL}/calcular/mayoria_forzada_senado?partido=${partido}&tipo_mayoria=${tipo}&plan=${plan}`;
  
  try {
    console.log('📡 Fetching:', url);
    
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    const data = await response.json();
    console.log('✅ Data:', data);
    
    // Mostrar resultado
    document.getElementById('resultado').innerHTML = `
      <div class="alert alert-success">
        <h3>Mayoría ${tipo === 'simple' ? 'Simple' : 'Calificada'}</h3>
        <p><strong>${data.votos_porcentaje}%</strong> de votos necesarios</p>
        <p>Ganar <strong>${data.estados_ganados}</strong> de 32 estados</p>
        <p>Obtendrás <strong>${data.senadores_obtenidos}</strong> senadores</p>
      </div>
    `;
  } catch (error) {
    console.error('❌ Error:', error);
    alert('Error: ' + error.message);
  }
});
</script>
```

## ENDPOINTS DISPONIBLES

| Endpoint | Método | Query Params | Body |
|----------|--------|-------------|------|
| `/procesar/diputados` | POST | - | `{ anio, plan, aplicar_topes }` |
| `/procesar/senado` | POST | - | `{ anio, plan, aplicar_topes }` |
| `/calcular/mayoria_forzada_senado` | GET | `partido, tipo_mayoria, plan` | - |
| `/generar/tabla_estados_senado` | GET | `partido, votos_porcentaje` | - |
| `/editar/estados_senado` | POST | - | `{ estados_manuales: {...} }` |

## ERRORES COMUNES

1. **"Failed to fetch"** → Render dormido (espera 30s)
2. **"CORS policy"** → Backend caído (visita https://back-electoral.onrender.com/)
3. **"404 Not Found"** → Endpoint mal escrito (verifica underscores)
4. **"422 Unprocessable"** → Parámetros incorrectos
5. **Botón no hace nada** → Falta `addEventListener` o ID incorrecto

## ARCHIVO COMPLETO DE DEBUGGING

Lee: `DEBUG_CONEXION_FRONTEND.md` para más detalles.

---

🚀 **CON ESTO DEBERÍAS PODER CORREGIR LA CONEXIÓN**
