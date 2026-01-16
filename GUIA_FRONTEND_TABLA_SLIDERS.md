# Guía Frontend: Tabla Interactiva de Distritos con Sliders

## 🎯 Objetivo
Crear una tabla que muestre la distribución de escaños por partido con **sliders interactivos** que permitan:
1. Ajustar el % de votos de cada partido
2. Ajustar manualmente los distritos MR ganados por partido
3. Ver actualización en tiempo real de la distribución final de escaños

## 📡 Endpoints Disponibles

### 1. Endpoint Principal: `/procesar/diputados` (POST)

```javascript
POST /procesar/diputados
Content-Type: application/json
```

#### Parámetros Clave

```typescript
interface DiputadosRequest {
  // Básicos
  anio: number;                           // 2018, 2021, 2024
  plan: string;                           // "vigente", "personalizado", etc.
  
  // Configuración del sistema
  escanos_totales?: number;               // Total de escaños (ej: 128)
  mr_seats?: number;                      // Escaños MR (ej: 64)
  rp_seats?: number;                      // Escaños RP (ej: 64)
  sistema?: string;                       // "mixto", "mr", "rp"
  umbral?: number;                        // Default: 0.03 (3%)
  aplicar_topes?: boolean;                // Default: true
  
  // 🎚️ SLIDERS: Redistribución de votos
  votos_custom?: string;                  // JSON: {"MORENA": 55.0, "PAN": 15.5, ...}
  
  // 🎚️ SLIDERS: Distritos MR por partido (MANUAL)
  mr_distritos_manuales?: string;         // JSON: {"MORENA": 32, "PAN": 13, ...}
  
  // 🗺️ OPCIONAL: Distribución geográfica detallada
  mr_distritos_por_estado?: string;       // JSON: {"AGUASCALIENTES": {"PAN": 3}, ...}
  
  // Otras opciones
  usar_coaliciones?: boolean;             // Default: true
  redistritacion_geografica?: boolean;    // Default: true
}
```

## 🎨 Implementación Frontend

### Paso 1: Estado Inicial

```typescript
// types.ts
interface PartidoState {
  nombre: string;
  votos_pct: number;      // % de votos (slider 1)
  mr_manual: number;      // Distritos MR (slider 2)
  color: string;
}

interface ResultadoState {
  partidos: Array<{
    party: string;
    seats: number;
    mr: number;
    rp: number;
    pm: number;
    votes: number;
    percent: number;
  }>;
  kpis: {
    total_votos: number;
    total_escanos: number;
    gallagher: number;
  };
  mr_por_estado?: Record<string, Record<string, number>>;
  distritos_por_estado?: Record<string, number>;
}
```

```javascript
// Estado inicial del componente
const [config, setConfig] = useState({
  anio: 2024,
  plan: 'personalizado',
  escanos_totales: 128,
  mr_seats: 64,
  rp_seats: 64,
  sistema: 'mixto',
  aplicar_topes: true
});

const [partidos, setPartidos] = useState([
  { nombre: 'MORENA', votos_pct: 42.5, mr_manual: 32, color: '#9d2449' },
  { nombre: 'PAN', votos_pct: 20.7, mr_manual: 13, color: '#0066CC' },
  { nombre: 'PRI', votos_pct: 13.1, mr_manual: 8, color: '#EE1C25' },
  { nombre: 'MC', votos_pct: 8.5, mr_manual: 6, color: '#FF6600' },
  { nombre: 'PVEM', votos_pct: 4.3, mr_manual: 3, color: '#66CC33' },
  { nombre: 'PT', votos_pct: 2.9, mr_manual: 2, color: '#CC0000' },
  { nombre: 'PRD', votos_pct: 2.5, mr_manual: 0, color: '#FFD700' }
]);

const [resultado, setResultado] = useState(null);
const [loading, setLoading] = useState(false);
```

### Paso 2: Función de Recalcular

```javascript
async function recalcularDistribucion() {
  setLoading(true);
  
  try {
    // Preparar datos para el backend
    const votos_custom = {};
    const mr_distritos_manuales = {};
    
    partidos.forEach(p => {
      votos_custom[p.nombre] = p.votos_pct;
      mr_distritos_manuales[p.nombre] = p.mr_manual;
    });
    
    // Validar que MR sume correctamente
    const totalMR = Object.values(mr_distritos_manuales).reduce((a, b) => a + b, 0);
    if (totalMR !== config.mr_seats) {
      alert(`Los distritos MR deben sumar ${config.mr_seats}, actualmente suman ${totalMR}`);
      return;
    }
    
    // Validar que votos sumen 100%
    const totalVotos = partidos.reduce((sum, p) => sum + p.votos_pct, 0);
    if (Math.abs(totalVotos - 100) > 0.1) {
      alert(`Los porcentajes de votos deben sumar 100%, actualmente suman ${totalVotos.toFixed(1)}%`);
      return;
    }
    
    // Hacer petición al backend
    const response = await fetch('/procesar/diputados', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        anio: config.anio,
        plan: config.plan,
        escanos_totales: config.escanos_totales,
        mr_seats: config.mr_seats,
        rp_seats: config.rp_seats,
        sistema: config.sistema,
        aplicar_topes: config.aplicar_topes,
        usar_coaliciones: true,
        redistritacion_geografica: true,
        
        // 🎚️ SLIDERS: Enviar valores ajustados
        votos_custom: JSON.stringify(votos_custom),
        mr_distritos_manuales: JSON.stringify(mr_distritos_manuales)
      })
    });
    
    if (!response.ok) {
      throw new Error(`Error: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    
    // Actualizar resultado
    setResultado({
      partidos: data.seat_chart || [],
      kpis: data.kpis || {},
      mr_por_estado: data.meta?.mr_por_estado,
      distritos_por_estado: data.meta?.distritos_por_estado
    });
    
  } catch (error) {
    console.error('Error al recalcular:', error);
    alert('Error al recalcular la distribución');
  } finally {
    setLoading(false);
  }
}
```

### Paso 3: Componentes de UI

#### Tabla Principal con Sliders

```jsx
function TablaDistribucion() {
  return (
    <div className="tabla-distribucion">
      <h2>Configuración del Sistema Electoral</h2>
      
      {/* Controles Globales */}
      <div className="controles-globales">
        <div className="control">
          <label>Total de Escaños:</label>
          <input 
            type="number" 
            value={config.escanos_totales}
            onChange={(e) => setConfig({...config, escanos_totales: parseInt(e.target.value)})}
          />
        </div>
        
        <div className="control">
          <label>Escaños MR:</label>
          <input 
            type="number" 
            value={config.mr_seats}
            onChange={(e) => {
              const newMR = parseInt(e.target.value);
              setConfig({
                ...config, 
                mr_seats: newMR,
                rp_seats: config.escanos_totales - newMR
              });
            }}
          />
        </div>
        
        <div className="control">
          <label>Escaños RP:</label>
          <input 
            type="number" 
            value={config.rp_seats}
            onChange={(e) => {
              const newRP = parseInt(e.target.value);
              setConfig({
                ...config,
                rp_seats: newRP,
                mr_seats: config.escanos_totales - newRP
              });
            }}
          />
        </div>
        
        <div className="control">
          <label>
            <input 
              type="checkbox" 
              checked={config.aplicar_topes}
              onChange={(e) => setConfig({...config, aplicar_topes: e.target.checked})}
            />
            Aplicar Topes Constitucionales (8%)
          </label>
        </div>
      </div>
      
      {/* Tabla de Partidos con Sliders */}
      <table className="tabla-partidos">
        <thead>
          <tr>
            <th>Partido</th>
            <th>% Votos</th>
            <th>Slider Votos</th>
            <th>Distritos MR</th>
            <th>Slider MR</th>
            <th>Escaños RP</th>
            <th>Total Escaños</th>
          </tr>
        </thead>
        <tbody>
          {partidos.map((partido, idx) => (
            <tr key={partido.nombre} style={{borderLeft: `4px solid ${partido.color}`}}>
              {/* Partido */}
              <td><strong>{partido.nombre}</strong></td>
              
              {/* % Votos */}
              <td>{partido.votos_pct.toFixed(1)}%</td>
              
              {/* Slider de Votos */}
              <td>
                <input
                  type="range"
                  min="0"
                  max="100"
                  step="0.1"
                  value={partido.votos_pct}
                  onChange={(e) => {
                    const nuevosPartidos = [...partidos];
                    nuevosPartidos[idx].votos_pct = parseFloat(e.target.value);
                    setPartidos(nuevosPartidos);
                  }}
                  className="slider slider-votos"
                />
              </td>
              
              {/* Distritos MR */}
              <td>{partido.mr_manual}</td>
              
              {/* Slider de Distritos MR */}
              <td>
                <input
                  type="range"
                  min="0"
                  max={config.mr_seats}
                  step="1"
                  value={partido.mr_manual}
                  onChange={(e) => {
                    const nuevosPartidos = [...partidos];
                    nuevosPartidos[idx].mr_manual = parseInt(e.target.value);
                    setPartidos(nuevosPartidos);
                  }}
                  className="slider slider-mr"
                />
              </td>
              
              {/* Escaños RP (calculados) */}
              <td>
                {resultado ? 
                  resultado.partidos.find(p => p.party === partido.nombre)?.rp || 0 
                  : '-'}
              </td>
              
              {/* Total Escaños (calculados) */}
              <td>
                <strong>
                  {resultado ? 
                    resultado.partidos.find(p => p.party === partido.nombre)?.seats || 0 
                    : '-'}
                </strong>
              </td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr>
            <td><strong>TOTAL</strong></td>
            <td>
              <strong>
                {partidos.reduce((sum, p) => sum + p.votos_pct, 0).toFixed(1)}%
              </strong>
              {Math.abs(partidos.reduce((sum, p) => sum + p.votos_pct, 0) - 100) > 0.1 && 
                <span style={{color: 'red'}}> ⚠️</span>
              }
            </td>
            <td></td>
            <td>
              <strong>
                {partidos.reduce((sum, p) => sum + p.mr_manual, 0)}
              </strong>
              {partidos.reduce((sum, p) => sum + p.mr_manual, 0) !== config.mr_seats && 
                <span style={{color: 'red'}}> ⚠️</span>
              }
            </td>
            <td></td>
            <td>
              <strong>
                {resultado ? 
                  resultado.partidos.reduce((sum, p) => sum + p.rp, 0) 
                  : '-'}
              </strong>
            </td>
            <td>
              <strong>
                {resultado ? 
                  resultado.partidos.reduce((sum, p) => sum + p.seats, 0) 
                  : '-'}
              </strong>
            </td>
          </tr>
        </tfoot>
      </table>
      
      {/* Botón de Recalcular */}
      <div className="acciones">
        <button 
          onClick={recalcularDistribucion}
          disabled={loading}
          className="btn-recalcular"
        >
          {loading ? 'Calculando...' : '🔄 Recalcular Distribución'}
        </button>
        
        <button 
          onClick={resetearValores}
          className="btn-reset"
        >
          🔙 Resetear Valores
        </button>
      </div>
      
      {/* KPIs */}
      {resultado && (
        <div className="kpis">
          <h3>Indicadores</h3>
          <div className="kpi-grid">
            <div className="kpi">
              <label>Total Escaños:</label>
              <value>{resultado.kpis.total_escanos}</value>
            </div>
            <div className="kpi">
              <label>Índice Gallagher:</label>
              <value>{resultado.kpis.gallagher?.toFixed(2)}</value>
            </div>
            <div className="kpi">
              <label>Partidos con Escaños:</label>
              <value>{resultado.kpis.partidos_con_escanos}</value>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
```

#### Tabla de Distribución por Estado (Opcional)

```jsx
function TablaEstados({ mr_por_estado, distritos_por_estado }) {
  if (!mr_por_estado || !distritos_por_estado) return null;
  
  return (
    <div className="tabla-estados">
      <h3>Distribución Geográfica por Estado</h3>
      <table>
        <thead>
          <tr>
            <th>Estado</th>
            <th>Total Distritos</th>
            {partidos.map(p => (
              <th key={p.nombre} style={{color: p.color}}>{p.nombre}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {Object.keys(mr_por_estado).sort().map(estado => (
            <tr key={estado}>
              <td>{estado}</td>
              <td><strong>{distritos_por_estado[estado]}</strong></td>
              {partidos.map(p => (
                <td key={p.nombre}>
                  {mr_por_estado[estado][p.nombre] || '-'}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

### Paso 4: Funciones Auxiliares

```javascript
// Resetear a valores por defecto
function resetearValores() {
  setPartidos([
    { nombre: 'MORENA', votos_pct: 42.5, mr_manual: 32, color: '#9d2449' },
    { nombre: 'PAN', votos_pct: 20.7, mr_manual: 13, color: '#0066CC' },
    { nombre: 'PRI', votos_pct: 13.1, mr_manual: 8, color: '#EE1C25' },
    { nombre: 'MC', votos_pct: 8.5, mr_manual: 6, color: '#FF6600' },
    { nombre: 'PVEM', votos_pct: 4.3, mr_manual: 3, color: '#66CC33' },
    { nombre: 'PT', votos_pct: 2.9, mr_manual: 2, color: '#CC0000' },
    { nombre: 'PRD', votos_pct: 2.5, mr_manual: 0, color: '#FFD700' }
  ]);
  setResultado(null);
}

// Auto-normalizar votos a 100%
function normalizarVotos() {
  const total = partidos.reduce((sum, p) => sum + p.votos_pct, 0);
  if (total === 0) return;
  
  const nuevosPartidos = partidos.map(p => ({
    ...p,
    votos_pct: (p.votos_pct / total) * 100
  }));
  
  setPartidos(nuevosPartidos);
}

// Auto-ajustar MR al total
function ajustarMRTotal() {
  const totalActual = partidos.reduce((sum, p) => sum + p.mr_manual, 0);
  const diferencia = config.mr_seats - totalActual;
  
  if (diferencia === 0) return;
  
  // Distribuir la diferencia proporcionalmente
  const nuevosPartidos = [...partidos];
  let restante = diferencia;
  
  // Ordenar por MR actual (desc) para ajustar los más grandes primero
  const indices = nuevosPartidos
    .map((p, i) => ({ partido: p, index: i }))
    .sort((a, b) => b.partido.mr_manual - a.partido.mr_manual);
  
  indices.forEach(({ index }) => {
    if (restante > 0) {
      nuevosPartidos[index].mr_manual += 1;
      restante--;
    } else if (restante < 0 && nuevosPartidos[index].mr_manual > 0) {
      nuevosPartidos[index].mr_manual -= 1;
      restante++;
    }
  });
  
  setPartidos(nuevosPartidos);
}
```

### Paso 5: CSS de Ejemplo

```css
.tabla-distribucion {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.controles-globales {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 30px;
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
}

.control {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.control label {
  font-weight: bold;
  font-size: 14px;
}

.control input[type="number"] {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 16px;
}

.tabla-partidos {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}

.tabla-partidos th,
.tabla-partidos td {
  padding: 12px;
  text-align: center;
  border: 1px solid #ddd;
}

.tabla-partidos thead {
  background: #333;
  color: white;
}

.tabla-partidos tfoot {
  background: #f5f5f5;
  font-weight: bold;
}

.slider {
  width: 100%;
  height: 8px;
  border-radius: 5px;
  outline: none;
  cursor: pointer;
}

.slider-votos {
  background: linear-gradient(to right, #4CAF50, #FFC107, #F44336);
}

.slider-mr {
  background: linear-gradient(to right, #2196F3, #9C27B0);
}

.acciones {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin: 20px 0;
}

.btn-recalcular,
.btn-reset {
  padding: 12px 24px;
  font-size: 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-recalcular {
  background: #4CAF50;
  color: white;
}

.btn-recalcular:hover {
  background: #45a049;
}

.btn-recalcular:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-reset {
  background: #f44336;
  color: white;
}

.btn-reset:hover {
  background: #da190b;
}

.kpis {
  margin-top: 30px;
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
  margin-top: 15px;
}

.kpi {
  text-align: center;
  padding: 15px;
  background: white;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.kpi label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

.kpi value {
  display: block;
  font-size: 24px;
  font-weight: bold;
  color: #333;
}
```

## 🔄 Flujo de Trabajo

1. **Usuario ajusta sliders** de % votos o distritos MR
2. **Frontend valida** que los totales sean correctos
3. **Usuario presiona "Recalcular"**
4. **Frontend envía** POST a `/procesar/diputados` con:
   - `votos_custom`: JSON con % de votos
   - `mr_distritos_manuales`: JSON con MR por partido
5. **Backend calcula** distribución de RP con Hare
6. **Backend retorna** `seat_chart` completo
7. **Frontend actualiza** tabla con nuevos valores

## 📊 Ejemplo de Request/Response

### Request
```json
POST /procesar/diputados

{
  "anio": 2024,
  "plan": "personalizado",
  "escanos_totales": 128,
  "mr_seats": 64,
  "rp_seats": 64,
  "sistema": "mixto",
  "aplicar_topes": true,
  "votos_custom": "{\"MORENA\": 55.0, \"PAN\": 15.5, \"PRI\": 12.5, \"MC\": 8.0, \"PVEM\": 4.5, \"PT\": 2.5, \"PRD\": 2.0}",
  "mr_distritos_manuales": "{\"MORENA\": 35, \"PAN\": 12, \"PRI\": 8, \"MC\": 5, \"PVEM\": 2, \"PT\": 2, \"PRD\": 0}"
}
```

### Response
```json
{
  "plan": "personalizado",
  "seat_chart": [
    {
      "party": "MORENA",
      "seats": 71,
      "mr": 35,
      "pm": 0,
      "rp": 36,
      "votes": 32232500,
      "percent": 55.0,
      "color": "#9d2449"
    },
    {
      "party": "PAN",
      "seats": 22,
      "mr": 12,
      "pm": 0,
      "rp": 10,
      "votes": 9083763,
      "percent": 15.5,
      "color": "#0066CC"
    }
    // ... resto de partidos
  ],
  "kpis": {
    "total_votos": 58604910,
    "total_escanos": 128,
    "gallagher": 2.45,
    "partidos_con_escanos": 6
  },
  "meta": {
    "mr_por_estado": {...},
    "distritos_por_estado": {...}
  }
}
```

## ⚠️ Validaciones Importantes

```javascript
// Validar antes de enviar
function validarAntesDe Recalcular() {
  const errores = [];
  
  // 1. Votos deben sumar 100%
  const totalVotos = partidos.reduce((sum, p) => sum + p.votos_pct, 0);
  if (Math.abs(totalVotos - 100) > 0.1) {
    errores.push(`Votos deben sumar 100%, actualmente: ${totalVotos.toFixed(1)}%`);
  }
  
  // 2. MR debe sumar al total configurado
  const totalMR = partidos.reduce((sum, p) => sum + p.mr_manual, 0);
  if (totalMR !== config.mr_seats) {
    errores.push(`Distritos MR deben sumar ${config.mr_seats}, actualmente: ${totalMR}`);
  }
  
  // 3. MR + RP debe igualar total
  if (config.mr_seats + config.rp_seats !== config.escanos_totales) {
    errores.push(`MR (${config.mr_seats}) + RP (${config.rp_seats}) debe igualar Total (${config.escanos_totales})`);
  }
  
  if (errores.length > 0) {
    alert('Errores de validación:\n' + errores.join('\n'));
    return false;
  }
  
  return true;
}
```

## 🎁 Funcionalidades Extra

### Auto-recalcular con Debounce

```javascript
import { useEffect, useRef } from 'react';

function useDebounce(value, delay) {
  const [debouncedValue, setDebouncedValue] = useState(value);
  
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);
    
    return () => clearTimeout(handler);
  }, [value, delay]);
  
  return debouncedValue;
}

// En el componente:
const debouncedPartidos = useDebounce(partidos, 1000); // 1 segundo de delay

useEffect(() => {
  if (validarAntesDe Recalcular()) {
    recalcularDistribucion();
  }
}, [debouncedPartidos]);
```

## 📝 Notas Finales

✅ **Backend ya soporta** todos los parámetros necesarios
✅ **Redistritación geográfica** se calcula automáticamente
✅ **Validaciones** aseguran consistencia de datos
✅ **Respuesta completa** incluye distribución por estado
✅ **Compatible** con mayoría forzada endpoint

El frontend solo necesita implementar los sliders y llamar al endpoint con los valores ajustados. ¡Todo el cálculo pesado lo hace el backend!
