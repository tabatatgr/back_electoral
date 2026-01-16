# 📊 GUÍA COMPLETA: SLIDERS DE MR (MAYORÍA RELATIVA) - VERSIÓN FLEXIBLE

## 🎯 ¿Qué hace el sistema de sliders de MR?

El usuario puede **modificar manualmente cuántos distritos gana cada partido** (MR - Mayoría Relativa) para **CUALQUIER configuración electoral**:

- ✅ Diputados mexicanos (300 MR)
- ✅ Senadores (64 MR + 32 PM)
- ✅ Congresos locales (varía según estado)
- ✅ **Cualquier otro escenario que el usuario defina**

**Ejemplos de uso:**
> "¿Qué pasaría si MORENA ganara 180 de 300 distritos?"
> "Simulación con solo 100 escaños MR y 50 RP"
> "Congreso local con 25 MR y 15 RP"

---

## 📡 CÓMO ENVIAR LOS DATOS (GENÉRICO PARA CUALQUIER ESCENARIO)

### **Parámetros clave:**

```javascript
{
  "anio": 2024,
  "plan": "vigente",
  "mr_distritos_manuales": "{\"MORENA\":50,\"PAN\":30,\"PRI\":20}",  // ← Sliders del usuario
  
  // ⚠️ CRÍTICO: Especificar SIEMPRE estos parámetros
  "escanos_totales": 150,      // Total de escaños (MR + RP)
  "mr_seats": 100,             // Cuántos son de Mayoría Relativa
  "rp_seats": 50,              // Cuántos son de Representación Proporcional
  
  "aplicar_topes": true,
  "sobrerrepresentacion": 8,
  "usar_coaliciones": true
}
```

### **Cálculo del máximo permitido:**

```javascript
// El máximo de MR que el usuario puede asignar = mr_seats
const maxMR = config.mr_seats;  // Ej: 300 para Diputados, 100 para caso custom

const totalMR = Object.values(mrSliders).reduce((a, b) => a + b, 0);
if (totalMR > maxMR) {
  alert(`La suma de MR (${totalMR}) excede el máximo permitido (${maxMR})`);
  return;
}
```

---

## 🎨 COMPONENTE REACT GENÉRICO (FUNCIONA PARA CUALQUIER ESCENARIO)

```jsx
import React, { useState } from 'react';

function SlidersMRGenerico() {
  // Configuración del escenario (puede venir de props o estado global)
  const [config, setConfig] = useState({
    escanos_totales: 300,  // Total
    mr_seats: 100,         // MR disponibles
    rp_seats: 200,         // RP disponibles
    anio: 2024,
    plan: "custom"
  });

  const [mrValues, setMrValues] = useState({
    MORENA: 40,
    PAN: 30,
    PRI: 20,
    PVEM: 5,
    PT: 3,
    MC: 2,
    PRD: 0
  });

  const [loading, setLoading] = useState(false);
  const [resultado, setResultado] = useState(null);

  const totalMR = Object.values(mrValues).reduce((a, b) => a + b, 0);
  const maxMR = config.mr_seats;  // ← Dinámico según configuración
  const excedeLimite = totalMR > maxMR;

  const handleSliderChange = (partido, nuevoValor) => {
    setMrValues({
      ...mrValues,
      [partido]: parseInt(nuevoValor)
    });
  };

  const simularEscenario = async () => {
    if (excedeLimite) {
      alert(`La suma de MR (${totalMR}) excede el máximo (${maxMR})`);
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/procesar/diputados', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          anio: config.anio,
          plan: config.plan,
          mr_distritos_manuales: JSON.stringify(mrValues),
          
          // ⚠️ CRÍTICO: Pasar SIEMPRE estos parámetros
          escanos_totales: config.escanos_totales,
          mr_seats: config.mr_seats,
          rp_seats: config.rp_seats,
          
          aplicar_topes: true,
          sobrerrepresentacion: 8,
          usar_coaliciones: true
        })
      });

      const data = await response.json();
      setResultado(data);
    } catch (error) {
      console.error('Error:', error);
      alert('Error al simular escenario');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="sliders-container">
      <h2>⚙️ Ajustar Distritos MR por Partido</h2>
      
      {/* Mostrar configuración actual */}
      <div className="config-info">
        <p>📊 Escenario: {config.escanos_totales} escaños totales 
           ({config.mr_seats} MR + {config.rp_seats} RP)</p>
      </div>
      
      <div className={`total-indicator ${excedeLimite ? 'error' : ''}`}>
        <span>Total MR asignado: {totalMR} / {maxMR}</span>
        {excedeLimite && (
          <span className="error-msg">⚠️ Excede el máximo permitido!</span>
        )}
        {totalMR < maxMR && (
          <span className="warning-msg">ℹ️ Quedan {maxMR - totalMR} MR sin asignar</span>
        )}
      </div>

      {Object.entries(mrValues).map(([partido, valor]) => (
        <div key={partido} className="slider-row">
          <label>{partido}</label>
          <input
            type="range"
            min="0"
            max={maxMR}  // ← Dinámico
            value={valor}
            onChange={(e) => handleSliderChange(partido, e.target.value)}
          />
          <input
            type="number"
            min="0"
            max={maxMR}  // ← Dinámico
            value={valor}
            onChange={(e) => handleSliderChange(partido, e.target.value)}
          />
          <span className="slider-value">{valor}</span>
        </div>
      ))}

      <button 
        onClick={simularEscenario}
        disabled={loading || excedeLimite}
        className={excedeLimite ? 'disabled' : ''}
      >
        {loading ? 'Calculando...' : '🚀 Simular Escenario'}
      </button>

      {resultado && (
        <div className="resultado">
          <h3>📊 Resultados:</h3>
          <table>
            <thead>
              <tr>
                <th>Partido</th>
                <th>MR</th>
                <th>RP</th>
                <th>Total</th>
                <th>% Votos</th>
                <th>% Escaños</th>
              </tr>
            </thead>
            <tbody>
              {resultado.resultados.map(r => (
                <tr key={r.partido}>
                  <td>{r.partido}</td>
                  <td>{r.mr}</td>
                  <td>{r.rp}</td>
                  <td>{r.total}</td>
                  <td>{r.porcentaje_votos.toFixed(2)}%</td>
                  <td>{r.porcentaje_escanos.toFixed(2)}%</td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="kpis">
            <p><strong>Total escaños:</strong> {resultado.kpis.total_escanos}</p>
            <p><strong>Índice Gallagher:</strong> {resultado.kpis.gallagher.toFixed(2)}</p>
            <p><strong>MAE:</strong> {resultado.kpis.mae_votos_vs_escanos.toFixed(3)}</p>
          </div>

          {resultado.mayorias && (
            <div className="mayorias">
              <h4>📈 Mayorías:</h4>
              {resultado.mayorias.mayoria_simple?.alcanzada && (
                <p>✅ <strong>{resultado.mayorias.mayoria_simple.partido}</strong> 
                   tiene mayoría simple ({resultado.mayorias.mayoria_simple.escanos} escaños)</p>
              )}
              {resultado.mayorias.mayoria_calificada?.alcanzada && (
                <p>🎉 <strong>{resultado.mayorias.mayoria_calificada.partido}</strong> 
                   tiene mayoría calificada (2/3)</p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default SlidersMRGenerico;
```

---

## 📋 EJEMPLOS DE DIFERENTES ESCENARIOS

### **Ejemplo 1: Diputados Federales (300 MR)**

```javascript
const configDiputados = {
  escanos_totales: 500,
  mr_seats: 300,
  rp_seats: 200,
  anio: 2024,
  plan: "vigente"
};

const request = {
  anio: 2024,
  plan: "vigente",
  mr_distritos_manuales: JSON.stringify({
    MORENA: 180, PAN: 50, PRI: 30, PVEM: 25, PT: 10, MC: 5
  }),
  escanos_totales: 500,
  mr_seats: 300,
  rp_seats: 200,
  aplicar_topes: true,
  sobrerrepresentacion: 8
};
```

### **Ejemplo 2: Escenario Custom (100 MR + 50 RP)**

```javascript
const configCustom = {
  escanos_totales: 150,
  mr_seats: 100,    // ← Solo 100 escaños MR
  rp_seats: 50,     // ← 50 escaños RP
  anio: 2024,
  plan: "custom"
};

const request = {
  anio: 2024,
  plan: "custom",
  mr_distritos_manuales: JSON.stringify({
    MORENA: 40,  // De 100 MR totales
    PAN: 30,
    PRI: 20,
    PVEM: 5,
    PT: 3,
    MC: 2
    // Total: 100/100
  }),
  escanos_totales: 150,
  mr_seats: 100,   // ← CRÍTICO: Especificar límite
  rp_seats: 50,
  aplicar_topes: true,
  sobrerrepresentacion: 8
};
```

### **Ejemplo 3: Senadores (64 MR + 32 PM)**

```javascript
const configSenadores = {
  escanos_totales: 128,
  mr_seats: 64,     // ← 2 por estado (32 estados)
  pm_seats: 32,     // ← Primera minoría
  rp_seats: 32,     // ← Representación proporcional
  anio: 2024,
  plan: "vigente"
};

const request = {
  anio: 2024,
  plan: "vigente",
  mr_distritos_manuales: JSON.stringify({
    MORENA: 30, PAN: 15, PRI: 10, PVEM: 5, PT: 3, MC: 1
    // Total: 64/64
  }),
  escanos_totales: 128,
  mr_seats: 64,
  pm_seats: 32,
  rp_seats: 32,
  aplicar_topes: true,
  sobrerrepresentacion: 8
};
```

### **Ejemplo 4: Congreso Local Pequeño (25 MR + 15 RP)**

```javascript
const configLocalPequeno = {
  escanos_totales: 40,
  mr_seats: 25,
  rp_seats: 15,
  anio: 2024,
  plan: "local_tlaxcala"
};

const request = {
  anio: 2024,
  plan: "local_tlaxcala",
  mr_distritos_manuales: JSON.stringify({
    MORENA: 12, PAN: 7, PRI: 4, PVEM: 2
    // Total: 25/25
  }),
  escanos_totales: 40,
  mr_seats: 25,
  rp_seats: 15,
  aplicar_topes: true,
  sobrerrepresentacion: 8
};
```

---

## ⚙️ CONFIGURACIÓN DINÁMICA DEL FRONTEND

```javascript
// Función para obtener configuración según el tipo de elección
function getConfiguracionEleccion(tipo) {
  const configuraciones = {
    'diputados_federal': {
      escanos_totales: 500,
      mr_seats: 300,
      rp_seats: 200,
      label: "Diputados Federales"
    },
    'senadores': {
      escanos_totales: 128,
      mr_seats: 64,
      pm_seats: 32,
      rp_seats: 32,
      label: "Senadores"
    },
    'custom_100': {
      escanos_totales: 150,
      mr_seats: 100,
      rp_seats: 50,
      label: "Escenario Custom (100 MR)"
    },
    'custom_50': {
      escanos_totales: 75,
      mr_seats: 50,
      rp_seats: 25,
      label: "Escenario Custom (50 MR)"
    }
  };
  
  return configuraciones[tipo] || configuraciones['diputados_federal'];
}

// Uso en el componente
function SlidersMRConSelector() {
  const [tipoEleccion, setTipoEleccion] = useState('diputados_federal');
  const config = getConfiguracionEleccion(tipoEleccion);
  
  return (
    <div>
      <select 
        value={tipoEleccion} 
        onChange={(e) => setTipoEleccion(e.target.value)}
      >
        <option value="diputados_federal">Diputados Federales (300 MR)</option>
        <option value="senadores">Senadores (64 MR)</option>
        <option value="custom_100">Custom: 100 MR + 50 RP</option>
        <option value="custom_50">Custom: 50 MR + 25 RP</option>
      </select>
      
      <SlidersMRGenerico config={config} />
    </div>
  );
}
```

---

## ✅ VALIDACIONES GENÉRICAS

```javascript
// Validación genérica que funciona para CUALQUIER configuración
function validarMRSliders(mrSliders, config) {
  const errors = [];
  
  // 1. Validar suma total
  const totalMR = Object.values(mrSliders).reduce((a, b) => a + b, 0);
  if (totalMR > config.mr_seats) {
    errors.push(`La suma de MR (${totalMR}) excede el máximo (${config.mr_seats})`);
  }
  
  // 2. Validar valores positivos
  if (Object.values(mrSliders).some(v => v < 0)) {
    errors.push('Los valores deben ser positivos');
  }
  
  // 3. Validar que sean números enteros
  if (Object.values(mrSliders).some(v => !Number.isInteger(v))) {
    errors.push('Los valores deben ser números enteros');
  }
  
  // 4. Advertencia si hay MR sin asignar
  if (totalMR < config.mr_seats) {
    const sinAsignar = config.mr_seats - totalMR;
    console.warn(`Quedan ${sinAsignar} MR sin asignar. Esto es válido pero inusual.`);
  }
  
  return {
    valid: errors.length === 0,
    errors: errors,
    totalMR: totalMR,
    maxMR: config.mr_seats,
    sinAsignar: Math.max(0, config.mr_seats - totalMR)
  };
}
```

---

## 🚀 REQUEST GENÉRICO AL BACKEND

```javascript
async function procesarEscenarioMR(config, mrSliders) {
  // Validar primero
  const validacion = validarMRSliders(mrSliders, config);
  if (!validacion.valid) {
    throw new Error(validacion.errors.join(', '));
  }
  
  // Construir request genérico
  const request = {
    anio: config.anio,
    plan: config.plan,
    mr_distritos_manuales: JSON.stringify(mrSliders),
    
    // ⚠️ SIEMPRE incluir estos parámetros
    escanos_totales: config.escanos_totales,
    mr_seats: config.mr_seats,
    rp_seats: config.rp_seats,
    
    // Opcionales pero recomendados
    aplicar_topes: config.aplicar_topes ?? true,
    sobrerrepresentacion: config.sobrerrepresentacion ?? 8,
    usar_coaliciones: config.usar_coaliciones ?? true
  };
  
  // Si hay PM (Senadores), agregarlo
  if (config.pm_seats) {
    request.pm_seats = config.pm_seats;
  }
  
  const response = await fetch('/procesar/diputados', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al procesar escenario');
  }
  
  return await response.json();
}
```

---

## 📊 TABLA COMPARATIVA DE ESCENARIOS

| Escenario | Total Escaños | MR | RP | PM | Máximo por slider |
|-----------|--------------|-----|-----|-----|-------------------|
| **Diputados Federales** | 500 | 300 | 200 | - | 300 |
| **Senadores** | 128 | 64 | 32 | 32 | 64 |
| **Custom 100** | 150 | 100 | 50 | - | 100 |
| **Custom 50** | 75 | 50 | 25 | - | 50 |
| **Congreso Local Grande** | 66 | 40 | 26 | - | 40 |
| **Congreso Local Pequeño** | 25 | 17 | 8 | - | 17 |

---

## 🎯 CONCLUSIÓN

El sistema de sliders de MR es **completamente genérico** y funciona para:

✅ **Cualquier número de escaños MR** (50, 100, 300, etc.)  
✅ **Cualquier configuración total** (escanos_totales)  
✅ **Cualquier combinación MR + RP + PM**  
✅ **Congresos federales, locales o simulaciones custom**  

**Regla de oro:** Siempre especificar `escanos_totales`, `mr_seats` y `rp_seats` en el request al backend.

**El backend NO asume valores hardcodeados.** Todo se calcula dinámicamente según los parámetros que envíe el frontend.
