# 🎯 Guía Frontend - Mayoría Forzada con `solo_partido`

## 📋 Resumen Ejecutivo

El backend ahora soporta **mayorías forzadas** que permiten calcular el porcentaje de votos necesario para que un partido alcance:
- ✅ **Mayoría simple** (50% + 1 escaño)
- ✅ **Mayoría calificada** (67% de escaños)
- ✅ **Umbral personalizado** (cualquier número de escaños)

**CRÍTICO**: El parámetro `solo_partido` controla si el partido debe alcanzar la mayoría **solo** o **con su coalición**.

---

## 🚨 CAMBIO IMPORTANTE: Parámetro `solo_partido`

### ¿Qué hace `solo_partido`?

| Parámetro | Comportamiento | Ejemplo (MORENA) |
|-----------|---------------|------------------|
| `solo_partido=true` (DEFAULT) | Solo el partido objetivo alcanza la mayoría. Los partners de coalición quedan en **0 escaños**. | MORENA: 251+, PT: 0, PVEM: 0 |
| `solo_partido=false` | El partido + su coalición alcanza la mayoría juntos. | MORENA + PT + PVEM = 251+ |

### 🔄 Redistribución Proporcional de Votos

**IMPORTANTE**: Con `solo_partido=true`, los votos se redistribuyen **proporcionalmente** entre TODOS los partidos, no se pone a nadie en 0%.

**Ejemplo con MORENA mayoría simple (47.50%)**:

| Partido | Votos Base | Votos Ajustados | Cambio |
|---------|-----------|----------------|--------|
| MORENA | 42.49% | **47.50%** | +5.01% ⬆️ |
| PAN | 21.09% | **18.64%** | -2.45% ⬇️ |
| PRI | 17.24% | **15.23%** | -2.01% ⬇️ |
| MC | 11.50% | **10.16%** | -1.34% ⬇️ |
| PVEM | 5.75% | **5.08%** | -0.67% ⬇️ |
| PT | 3.83% | **3.38%** | -0.45% ⬇️ |

**✅ Todos los partidos bajan proporcionalmente** (según su tamaño original)  
**❌ Ningún partido llega a 0%**

---

## 🔧 Endpoints Disponibles

### 1️⃣ **Diputados - Mayoría Forzada**

**Endpoint**: `POST /calcular/mayoria_forzada`

**Parámetros obligatorios**:
```json
{
  "partido": "MORENA",           // Partido objetivo
  "tipo_mayoria": "simple",      // "simple", "calificada", "custom"
  "anio": 2024                   // Año electoral
}
```

**Parámetros opcionales**:
```json
{
  "mr_total": 300,               // Total MR (default: según plan vigente)
  "rp_total": 200,               // Total RP (default: según plan vigente)
  "aplicar_topes": true,         // Aplicar topes constitucionales
  "solo_partido": true,          // 🆕 IMPORTANTE: true = solo el partido
  "escanos_objetivo": null       // Solo si tipo_mayoria="custom"
}
```

**Ejemplo Request**:
```javascript
const response = await fetch('/calcular/mayoria_forzada', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    partido: 'MORENA',
    tipo_mayoria: 'simple',
    anio: 2024,
    solo_partido: true  // 🆕 MORENA debe alcanzar mayoría SOLO
  })
});
```

---

### 2️⃣ **Senado - Mayoría Forzada**

**Endpoint**: `POST /calcular/mayoria_forzada_senado`

**Parámetros** (iguales que Diputados):
```json
{
  "partido": "PAN",
  "tipo_mayoria": "calificada",
  "anio": 2024,
  "solo_partido": true
}
```

---

## 🎨 Implementación en el Frontend

### Paso 1: Agregar Toggle o Checkbox

```jsx
function MayoriaForzadaForm() {
  const [soloPartido, setSoloPartido] = useState(true); // DEFAULT: true
  const [partido, setPartido] = useState('MORENA');
  const [tipoMayoria, setTipoMayoria] = useState('simple');

  return (
    <div className="mayoria-forzada-form">
      {/* Selector de Partido */}
      <select value={partido} onChange={(e) => setPartido(e.target.value)}>
        <option value="MORENA">MORENA</option>
        <option value="PAN">PAN</option>
        <option value="PRI">PRI</option>
        <option value="MC">MC</option>
        <option value="PT">PT</option>
        <option value="PVEM">PVEM</option>
      </select>

      {/* Selector de Tipo de Mayoría */}
      <select value={tipoMayoria} onChange={(e) => setTipoMayoria(e.target.value)}>
        <option value="simple">Mayoría Simple (50% + 1)</option>
        <option value="calificada">Mayoría Calificada (67%)</option>
      </select>

      {/* 🆕 TOGGLE CRÍTICO: solo_partido */}
      <div className="solo-partido-toggle">
        <label>
          <input
            type="checkbox"
            checked={soloPartido}
            onChange={(e) => setSoloPartido(e.target.checked)}
          />
          <strong>Solo el partido</strong>
          <span className="tooltip">
            ℹ️ Si está activado, solo {partido} alcanzará la mayoría (coalición = 0 escaños).
            Si está desactivado, {partido} + su coalición alcanzarán la mayoría juntos.
          </span>
        </label>
      </div>

      <button onClick={() => calcularMayoria(partido, tipoMayoria, soloPartido)}>
        Calcular
      </button>
    </div>
  );
}
```

---

### Paso 2: Función para Enviar Request

```javascript
async function calcularMayoria(partido, tipoMayoria, soloPartido) {
  const payload = {
    partido: partido,
    tipo_mayoria: tipoMayoria,
    anio: 2024,
    solo_partido: soloPartido,  // 🆕 IMPORTANTE
    aplicar_topes: true
  };

  try {
    const response = await fetch('/calcular/mayoria_forzada', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (!response.ok) {
      // Manejar error
      console.error('Error:', data.detail);
      alert(`Error: ${data.detail}`);
      return;
    }

    // Mostrar resultados
    mostrarResultados(data);

  } catch (error) {
    console.error('Error de red:', error);
    alert('Error al conectar con el backend');
  }
}
```

---

### Paso 3: Mostrar Resultados y Actualizar Sliders

```javascript
function mostrarResultados(data) {
  if (!data.viable) {
    // No es viable alcanzar la mayoría
    alert(`❌ No es viable: ${data.razon}`);
    return;
  }

  // Es viable
  console.log('✅ Mayoría alcanzable');
  console.log(`📊 Votos necesarios: ${data.votos_necesarios}%`);
  console.log(`🗳️ MR distritos: ${data.mr_distritos}`);
  console.log(`📈 RP estimado: ${data.rp_estimado} escaños`);

  // Actualizar UI con los valores
  document.getElementById('votos-necesarios').innerText = 
    `${data.votos_necesarios.toFixed(2)}%`;
  
  document.getElementById('mr-distritos').innerText = 
    data.mr_distritos || 'N/A';
  
  document.getElementById('rp-escanos').innerText = 
    data.rp_estimado || 'N/A';
  
  // 🆕 ACTUALIZAR SLIDERS DE VOTOS (porcentajes de votos por partido)
  if (data.votos_custom) {
    for (const [partido, porcentaje] of Object.entries(data.votos_custom)) {
      const slider = document.getElementById(`slider-votos-${partido}`);
      if (slider) {
        slider.value = porcentaje;
        // Disparar evento de cambio para que se actualice la UI
        slider.dispatchEvent(new Event('input', { bubbles: true }));
      }
    }
  }
  
  // 🆕 ACTUALIZAR SLIDERS DE MR (distritos por partido)
  if (data.mr_distritos_manuales) {
    for (const [partido, distritos] of Object.entries(data.mr_distritos_manuales)) {
      const slider = document.getElementById(`slider-mr-${partido}`);
      if (slider) {
        slider.value = distritos;
        // Disparar evento de cambio para que se actualice la UI
        slider.dispatchEvent(new Event('input', { bubbles: true }));
      }
    }
  }
  
  // 🆕 ACTUALIZAR TABLA GEOGRÁFICA (distritos por estado)
  if (data.mr_distritos_por_estado) {
    // Opción 1: Si tienes un componente que maneja mr_distritos_por_estado directamente
    window.updateMrPorEstado(data.mr_distritos_por_estado);
    
    // Opción 2: Si tienes inputs individuales por estado y partido
    for (const [estadoId, partidos] of Object.entries(data.mr_distritos_por_estado)) {
      for (const [partido, distritos] of Object.entries(partidos)) {
        const input = document.querySelector(`[data-estado="${estadoId}"][data-partido="${partido}"]`);
        if (input) {
          input.value = distritos;
          input.dispatchEvent(new Event('change', { bubbles: true }));
        }
      }
    }
  }
}
```

---

## ✅ Checklist de Verificación Frontend

### 🔴 CRÍTICO - Funcionalidad Básica
- [ ] **Toggle/Checkbox para `solo_partido`** con default `true`
- [ ] **Selector de partido** (MORENA, PAN, PRI, MC, PT, PVEM)
- [ ] **Selector de tipo de mayoría** (simple, calificada)
- [ ] **Enviar parámetro `solo_partido` en el request**
- [ ] **Manejar respuesta `viable: false`** con mensaje de error
- [ ] **Mostrar `votos_necesarios`, `mr_distritos`, `rp_estimado`**
- [ ] **🆕 Actualizar sliders de votos** con `votos_custom` de la respuesta
- [ ] **🆕 Actualizar sliders de MR** con `mr_distritos_manuales` de la respuesta

### 🟡 IMPORTANTE - UX/UI
- [ ] **Tooltip explicativo** para `solo_partido`
- [ ] **Indicador visual** de coalición activa/inactiva
- [ ] **Mensaje claro** cuando mayoría calificada requiere quitar topes
- [ ] **Loading state** mientras se calcula
- [ ] **Validación**: No permitir `tipo_mayoria="custom"` sin `escanos_objetivo`
- [ ] **🆕 Animación visual** cuando se actualizan los sliders automáticamente
- [ ] **🆕 Botón "Aplicar Mayoría"** para confirmar cambios antes de actualizar sliders

### 🟢 OPCIONAL - Features Avanzadas
- [ ] **Comparación lado a lado**: solo_partido=true vs false
- [ ] **Gráfica visual** del porcentaje de votos necesario
- [ ] **Tabla de distribución** por estado/circunscripción
- [ ] **Guardar escenarios** de mayoría forzada
- [ ] **Exportar resultados** a CSV/JSON

---

## 🎯 Casos de Uso Comunes

### Caso 1: MORENA quiere mayoría simple SOLO (sin coalición)
```javascript
{
  "partido": "MORENA",
  "tipo_mayoria": "simple",
  "anio": 2024,
  "solo_partido": true  // ✅ PT y PVEM quedan en 0
}
```

**Resultado esperado**:
- MORENA: 251+ escaños
- PT: 0 escaños
- PVEM: 0 escaños

---

### Caso 2: PAN quiere mayoría calificada CON coalición
```javascript
{
  "partido": "PAN",
  "tipo_mayoria": "calificada",
  "anio": 2024,
  "solo_partido": false,  // ✅ PAN + PRI + PRD juntos
  "aplicar_topes": false  // Mayoría calificada requiere sin topes
}
```

**Resultado esperado**:
- PAN + PRI + PRD: 334+ escaños (juntos)

---

### Caso 3: MC quiere mayoría simple (sin coalición conocida)
```javascript
{
  "partido": "MC",
  "tipo_mayoria": "simple",
  "anio": 2024,
  "solo_partido": true  // No afecta, MC no tiene coalición
}
```

**Resultado esperado**:
- MC: 251+ escaños
- No hay redistribución de coalición (MC es independiente)

---

## 🚨 Validaciones Importantes

### 1. Mayoría Calificada CON Topes → NO VIABLE

Si el usuario intenta:
```javascript
{
  "tipo_mayoria": "calificada",
  "aplicar_topes": true  // ❌ CONFLICTO
}
```

**Backend responde**:
```json
{
  "viable": false,
  "razon": "Mayoría calificada (334 escaños) es IMPOSIBLE con topes del 8%. Requeriría 200.6% de votos (históricamente inalcanzable). Para usar mayoría calificada, DESACTIVE los topes (aplicar_topes=False)"
}
```

**Frontend debe**:
- Mostrar el mensaje de error
- Sugerir desactivar topes
- Opcional: Auto-desactivar topes cuando se selecciona "calificada"

---

### 2. Validar Partido Válido

```javascript
const PARTIDOS_VALIDOS = ['MORENA', 'PAN', 'PRI', 'MC', 'PT', 'PVEM', 'PRD'];

if (!PARTIDOS_VALIDOS.includes(partido)) {
  alert('Partido no válido');
  return;
}
```

---

### 3. Validar Año Electoral

```javascript
const ANIOS_VALIDOS = [2018, 2021, 2024];

if (!ANIOS_VALIDOS.includes(anio)) {
  alert('Año electoral no válido. Usar: 2018, 2021 o 2024');
  return;
}
```

---

## 📊 Estructura de Respuesta del Backend

### ✅ Respuesta Exitosa (viable: true)

```json
{
  "viable": true,
  "votos_necesarios": 47.50,
  "mr_distritos": 162,
  "rp_estimado": 95,
  "escanos_totales": 500,
  "umbral_objetivo": 251,
  "partido": "MORENA",
  "tipo_mayoria": "simple",
  "aplicar_topes": true,
  "solo_partido": true,
  "detalle": "MORENA necesita 47.50% de votos para alcanzar 251 escaños (mayoría simple)",
  
  // 🆕 IMPORTANTE: Valores para actualizar sliders del frontend
  "votos_custom": {
    "MORENA": 47.50,
    "PAN": 18.64,
    "PRI": 15.23,
    "MC": 10.16,
    "PVEM": 5.08,
    "PT": 3.38
  },
  "mr_distritos_manuales": {
    "MORENA": 162,
    "PAN": 60,
    "PRI": 46,
    "MC": 32,
    "PT": 0,
    "PVEM": 0
  },
  
  // 🆕 DISTRIBUCIÓN GEOGRÁFICA (tabla de distritos por estado)
  "mr_distritos_por_estado": {
    "1": {"MORENA": 2, "PAN": 1},  // Aguascalientes
    "2": {"MORENA": 4, "PAN": 3, "PRI": 1},  // Baja California
    "9": {"MORENA": 15, "PAN": 7, "PRI": 3, "MC": 2},  // CDMX
    "15": {"MORENA": 22, "PAN": 10, "PRI": 5, "MC": 3},  // Estado de México
    // ... 32 estados en total
  }
}
```

### ❌ Respuesta No Viable (viable: false)

```json
{
  "viable": false,
  "votos_necesarios": 0.0,
  "razon": "Mayoría calificada (334 escaños) es IMPOSIBLE con topes del 8%. Requeriría 200.6% de votos (históricamente inalcanzable). Para usar mayoría calificada, DESACTIVE los topes (aplicar_topes=False)",
  "sugerencia": "Desactivar topes de sobrerrepresentación",
  "partido": "MORENA",
  "tipo_mayoria": "calificada",
  "aplicar_topes": true
}
```

---

## 🎨 Ejemplo de UI Completa

```jsx
import React, { useState } from 'react';

function MayoriaForzadaCalculator() {
  const [partido, setPartido] = useState('MORENA');
  const [tipoMayoria, setTipoMayoria] = useState('simple');
  const [soloPartido, setSoloPartido] = useState(true);
  const [aplicarTopes, setAplicarTopes] = useState(true);
  const [resultado, setResultado] = useState(null);
  const [loading, setLoading] = useState(false);

  const calcular = async () => {
    setLoading(true);
    
    try {
      const response = await fetch('/calcular/mayoria_forzada', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          partido,
          tipo_mayoria: tipoMayoria,
          anio: 2024,
          solo_partido: soloPartido,
          aplicar_topes: aplicarTopes
        })
      });

      const data = await response.json();
      setResultado(data);
      
    } catch (error) {
      console.error('Error:', error);
      alert('Error al calcular');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mayoria-forzada-calculator">
      <h2>🎯 Calculadora de Mayoría Forzada</h2>

      {/* Selector de Partido */}
      <div className="form-group">
        <label>Partido:</label>
        <select value={partido} onChange={(e) => setPartido(e.target.value)}>
          <option value="MORENA">MORENA</option>
          <option value="PAN">PAN</option>
          <option value="PRI">PRI</option>
          <option value="MC">Movimiento Ciudadano</option>
          <option value="PT">PT</option>
          <option value="PVEM">PVEM</option>
        </select>
      </div>

      {/* Tipo de Mayoría */}
      <div className="form-group">
        <label>Tipo de Mayoría:</label>
        <select value={tipoMayoria} onChange={(e) => setTipoMayoria(e.target.value)}>
          <option value="simple">Mayoría Simple (50% + 1)</option>
          <option value="calificada">Mayoría Calificada (67%)</option>
        </select>
      </div>

      {/* Solo Partido Toggle */}
      <div className="form-group checkbox-group">
        <label>
          <input
            type="checkbox"
            checked={soloPartido}
            onChange={(e) => setSoloPartido(e.target.checked)}
          />
          <strong>Solo el partido (sin coalición)</strong>
        </label>
        <small className="help-text">
          {soloPartido 
            ? `✅ Solo ${partido} alcanzará la mayoría (coalición = 0 escaños)`
            : `⚠️ ${partido} + coalición alcanzarán la mayoría juntos`
          }
        </small>
      </div>

      {/* Aplicar Topes */}
      <div className="form-group checkbox-group">
        <label>
          <input
            type="checkbox"
            checked={aplicarTopes}
            onChange={(e) => setAplicarTopes(e.target.checked)}
          />
          Aplicar topes constitucionales
        </label>
        {tipoMayoria === 'calificada' && aplicarTopes && (
          <small className="warning">
            ⚠️ Mayoría calificada requiere desactivar topes
          </small>
        )}
      </div>

      {/* Botón Calcular */}
      <button 
        onClick={calcular} 
        disabled={loading}
        className="btn-primary"
      >
        {loading ? 'Calculando...' : 'Calcular Mayoría'}
      </button>

      {/* Resultados */}
      {resultado && (
        <div className={`resultado ${resultado.viable ? 'viable' : 'no-viable'}`}>
          {resultado.viable ? (
            <>
              <h3>✅ Mayoría Alcanzable</h3>
              <div className="resultado-detalle">
                <p><strong>Votos necesarios:</strong> {resultado.votos_necesarios.toFixed(2)}%</p>
                <p><strong>MR distritos:</strong> {resultado.mr_distritos}</p>
                <p><strong>RP estimado:</strong> ~{resultado.rp_estimado} escaños</p>
                <p><strong>Total:</strong> {resultado.umbral_objetivo}+ escaños</p>
              </div>
            </>
          ) : (
            <>
              <h3>❌ No Viable</h3>
              <p className="razon">{resultado.razon}</p>
              {resultado.sugerencia && (
                <p className="sugerencia">💡 {resultado.sugerencia}</p>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default MayoriaForzadaCalculator;
```

---

## 🧪 Tests Recomendados

### Test 1: MORENA mayoría simple solo_partido=true
```javascript
assert(response.partido === 'MORENA');
assert(response.viable === true);
assert(response.votos_necesarios < 50); // Debería ser ~47%
```

### Test 2: MORENA mayoría calificada con topes (debe fallar)
```javascript
assert(response.viable === false);
assert(response.razon.includes('IMPOSIBLE con topes'));
```

### Test 3: MC sin coalición
```javascript
assert(response.partido === 'MC');
assert(response.viable === true);
// MC no tiene coalición, solo_partido no afecta
```

---

## 📞 Contacto/Soporte

Si tienes dudas sobre la implementación:
1. Revisa esta guía
2. Consulta `DOCUMENTACION_API.md`
3. Prueba con Postman/curl los endpoints
4. Verifica logs del backend para debugging

---

## 🎯 Resumen Final

### ✅ LO MÁS IMPORTANTE:

1. **Agregar parámetro `solo_partido` a los requests** (default: `true`)
2. **Mostrar toggle/checkbox en UI** para que usuario controle este parámetro
3. **Manejar `viable: false`** mostrando `razon` al usuario
4. **Auto-sugerencia**: Si mayoría calificada + topes → sugerir quitar topes
5. **Validar partidos y años** antes de enviar request
6. **🆕 ACTUALIZAR SLIDERS**: Usar `votos_custom` y `mr_distritos_manuales` de la respuesta
7. **🆕 REDISTRIBUCIÓN PROPORCIONAL**: Los votos se ajustan proporcionalmente, NO se pone a nadie en 0%

### 📊 Comportamiento de los Votos:

**Con `solo_partido=true`**:
- El partido objetivo sube al porcentaje necesario
- TODOS los demás partidos **bajan proporcionalmente**
- Nadie llega a 0% de votos
- Los MR de coalición SÍ se anulan (0 distritos)

**Con `solo_partido=false`**:
- El partido + coalición alcanzan mayoría juntos
- Redistribución normal entre todos

**Con estos 7 puntos, la funcionalidad quedará 100% operativa.** 🚀
