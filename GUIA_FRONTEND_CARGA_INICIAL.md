# Guía Frontend: Carga de Datos Iniciales

## Problema Resuelto

El frontend necesitaba cargar automáticamente los datos de **2024 vigente** al inicializar, pero:

1. ❌ No había endpoint unificado para ambas cámaras
2. ❌ Los datos geográficos (`mr_por_estado`, `distritos_por_estado`) no se incluían en la carga inicial
3. ❌ No había soporte para cambiar entre Diputados y Senado fácilmente

## Solución Implementada

### ✅ Endpoint Mejorado: `GET /data/initial`

```http
GET /data/initial?camara=diputados
GET /data/initial?camara=senadores
```

**Parámetros:**
- `camara` (opcional): `"diputados"` o `"senadores"` (default: `"diputados"`)

**Respuesta Completa:**

```json
{
  "seat_chart": [
    {"partido": "MORENA", "escanos": 234, "color": "#A0235E"},
    {"partido": "PAN", "escanos": 71, "color": "#0080FF"},
    ...
  ],
  "mr": {
    "MORENA": 234,
    "PAN": 38,
    "PRI": 18,
    ...
  },
  "rp": {
    "MORENA": 0,
    "PAN": 33,
    "PRI": 17,
    ...
  },
  "tot": {
    "MORENA": 234,
    "PAN": 71,
    "PRI": 35,
    ...
  },
  "meta": {
    "mr_por_estado": {
      "AGUASCALIENTES": {
        "MORENA": 2,
        "PAN": 1,
        "PRI": 0
      },
      "BAJA CALIFORNIA": {
        "MORENA": 7,
        "PAN": 1,
        "PRI": 0
      },
      ...
    },
    "distritos_por_estado": {
      "AGUASCALIENTES": 3,
      "BAJA CALIFORNIA": 8,
      "BAJA CALIFORNIA SUR": 2,
      ...
    }
  },
  "mayorias": {
    "total_escanos": 500,
    "mayoria_simple": {
      "umbral": 251,
      "alcanzada": false,
      "partido": null,
      "escanos": 0,
      "es_coalicion": false
    },
    "mayoria_calificada": {
      "umbral": 334,
      "alcanzada": false,
      "partido": null,
      "escanos": 0,
      "es_coalicion": false
    }
  },
  "config_inicial": {
    "anio": 2024,
    "camara": "diputados",
    "plan": "vigente",
    "descripcion": "Datos vigentes de la Cámara de Diputados 2024-2027",
    "total_escanos": 500,
    "mr_escanos": 300,
    "rp_escanos": 200,
    "fecha_carga": "2026-01-16T12:30:45.123456"
  },
  "partidos_principales": [
    {
      "partido": "MORENA",
      "porcentaje_votos": 42.5,
      "escanos": 234,
      "color": "#A0235E"
    },
    ...
  ]
}
```

## Implementación en el Frontend

### 1. Carga Inicial de Diputados

```javascript
// Al inicializar la aplicación o la página de Diputados
async function cargarDatosIniciales() {
  try {
    const response = await fetch('/data/initial?camara=diputados');
    const data = await response.json();
    
    // Verificar que los datos estén completos
    if (!data.meta || !data.meta.mr_por_estado) {
      console.error('⚠️ Datos geográficos no incluidos en respuesta');
      return;
    }
    
    // Actualizar UI con todos los datos
    actualizarSeatChart(data.seat_chart);
    actualizarTablaPartidos(data.mr, data.rp, data.tot);
    actualizarTablaGeografica(data.meta.mr_por_estado, data.meta.distritos_por_estado);
    actualizarMayorias(data.mayorias);
    
    console.log('✅ Datos de Diputados 2024 vigente cargados');
    console.log(`Total escaños: ${data.config_inicial.total_escanos}`);
    console.log(`MR por estado: ${Object.keys(data.meta.mr_por_estado).length} estados`);
    
  } catch (error) {
    console.error('Error cargando datos iniciales:', error);
  }
}
```

### 2. Carga Inicial de Senado

```javascript
// Al cambiar a la pestaña/página de Senado
async function cargarDatosSenado() {
  try {
    const response = await fetch('/data/initial?camara=senadores');
    const data = await response.json();
    
    // Verificar estructura específica de Senado
    if (!data.meta || !data.meta.senadores_por_estado) {
      console.error('⚠️ Datos de senadores por estado no incluidos');
      return;
    }
    
    // Actualizar UI con datos de Senado
    actualizarSeatChart(data.seat_chart);
    actualizarTablaPartidos(data.mr, data.rp, data.tot);
    actualizarTablaSenadores(data.meta.mr_por_estado, data.meta.senadores_por_estado);
    actualizarMayorias(data.mayorias);
    
    console.log('✅ Datos de Senado 2024 vigente cargados');
    console.log(`Total senadores: ${data.config_inicial.total_escanos}`);
    console.log(`MR: ${data.config_inicial.mr_escanos}, PM: ${data.config_inicial.pm_escanos}, RP: ${data.config_inicial.rp_escanos}`);
    
  } catch (error) {
    console.error('Error cargando datos de Senado:', error);
  }
}
```

### 3. Componente React - Carga Automática

```jsx
import { useEffect, useState } from 'react';

function CamaraSelector() {
  const [camara, setCamara] = useState('diputados');
  const [datos, setDatos] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    cargarDatos();
  }, [camara]);
  
  async function cargarDatos() {
    setLoading(true);
    try {
      const response = await fetch(`/data/initial?camara=${camara}`);
      const data = await response.json();
      
      // Validar datos completos
      if (!data.meta) {
        throw new Error('Respuesta incompleta del servidor');
      }
      
      setDatos(data);
      console.log(`✅ Datos de ${camara} cargados`);
      
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  }
  
  return (
    <div>
      {/* Selector de cámara */}
      <select value={camara} onChange={(e) => setCamara(e.target.value)}>
        <option value="diputados">Cámara de Diputados</option>
        <option value="senadores">Senado</option>
      </select>
      
      {/* Mostrar datos */}
      {loading ? (
        <p>Cargando {camara}...</p>
      ) : datos ? (
        <div>
          <h2>{datos.config_inicial.descripcion}</h2>
          <p>Total escaños: {datos.config_inicial.total_escanos}</p>
          
          {/* Seat Chart */}
          <SeatChart data={datos.seat_chart} />
          
          {/* Tabla de Partidos */}
          <TablaPartidos mr={datos.mr} rp={datos.rp} tot={datos.tot} />
          
          {/* Tabla Geográfica */}
          {camara === 'diputados' ? (
            <TablaDistritos 
              mrPorEstado={datos.meta.mr_por_estado}
              distritosPorEstado={datos.meta.distritos_por_estado}
            />
          ) : (
            <TablaSenadores
              mrPorEstado={datos.meta.mr_por_estado}
              senadoresPorEstado={datos.meta.senadores_por_estado}
            />
          )}
          
          {/* Mayorías */}
          <InfoMayorias mayorias={datos.mayorias} />
        </div>
      ) : (
        <p>Error cargando datos</p>
      )}
    </div>
  );
}
```

### 4. Tabla Geográfica - Diputados

```jsx
function TablaDistritos({ mrPorEstado, distritosPorEstado }) {
  return (
    <table>
      <thead>
        <tr>
          <th>Estado</th>
          <th>Total Distritos</th>
          <th>MORENA</th>
          <th>PAN</th>
          <th>PRI</th>
          <th>PVEM</th>
          <th>PT</th>
          <th>MC</th>
          <th>PRD</th>
        </tr>
      </thead>
      <tbody>
        {Object.entries(mrPorEstado).map(([estado, partidos]) => (
          <tr key={estado}>
            <td>{estado}</td>
            <td>{distritosPorEstado[estado]}</td>
            <td>{partidos.MORENA || 0}</td>
            <td>{partidos.PAN || 0}</td>
            <td>{partidos.PRI || 0}</td>
            <td>{partidos.PVEM || 0}</td>
            <td>{partidos.PT || 0}</td>
            <td>{partidos.MC || 0}</td>
            <td>{partidos.PRD || 0}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

### 5. Tabla Geográfica - Senado

```jsx
function TablaSenadores({ mrPorEstado, senadoresPorEstado }) {
  return (
    <table>
      <thead>
        <tr>
          <th>Estado</th>
          <th>Total Senadores</th>
          <th>MORENA</th>
          <th>PAN</th>
          <th>PRI</th>
          <th>PVEM</th>
          <th>PT</th>
          <th>MC</th>
          <th>PRD</th>
        </tr>
      </thead>
      <tbody>
        {Object.entries(mrPorEstado).map(([estado, partidos]) => (
          <tr key={estado}>
            <td>{estado}</td>
            <td>{senadoresPorEstado[estado]}</td>
            <td>{partidos.MORENA || 0}</td>
            <td>{partidos.PAN || 0}</td>
            <td>{partidos.PRI || 0}</td>
            <td>{partidos.PVEM || 0}</td>
            <td>{partidos.PT || 0}</td>
            <td>{partidos.MC || 0}</td>
            <td>{partidos.PRD || 0}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

## Diferencias Clave: Diputados vs Senado

### Diputados
```json
{
  "meta": {
    "mr_por_estado": { ... },
    "distritos_por_estado": {
      "AGUASCALIENTES": 3,
      "CDMX": 24,
      ...
    }
  },
  "config_inicial": {
    "total_escanos": 500,
    "mr_escanos": 300,
    "rp_escanos": 200
  }
}
```

### Senado
```json
{
  "meta": {
    "mr_por_estado": { ... },
    "senadores_por_estado": {
      "AGUASCALIENTES": 3,
      "CDMX": 3,
      ...  // Todos son 3
    }
  },
  "config_inicial": {
    "total_escanos": 128,
    "mr_escanos": 64,
    "pm_escanos": 32,
    "rp_escanos": 32
  }
}
```

## Validación de Datos

```javascript
function validarDatosCompletos(data, camara) {
  const checks = {
    seatChart: !!data.seat_chart,
    mr: !!data.mr,
    rp: !!data.rp,
    tot: !!data.tot,
    meta: !!data.meta,
    mrPorEstado: !!(data.meta && data.meta.mr_por_estado),
    geografico: camara === 'diputados' 
      ? !!(data.meta && data.meta.distritos_por_estado)
      : !!(data.meta && data.meta.senadores_por_estado),
    config: !!data.config_inicial
  };
  
  const faltantes = Object.entries(checks)
    .filter(([key, value]) => !value)
    .map(([key]) => key);
  
  if (faltantes.length > 0) {
    console.error(`⚠️ Datos faltantes: ${faltantes.join(', ')}`);
    return false;
  }
  
  console.log('✅ Todos los datos están presentes');
  return true;
}

// Uso
const response = await fetch('/data/initial?camara=diputados');
const data = await response.json();

if (validarDatosCompletos(data, 'diputados')) {
  // Proceder con actualización de UI
  actualizarUI(data);
}
```

## Verificación en Consola del Backend

Al llamar el endpoint, el backend imprime:

```
[INFO] Cargando datos iniciales: Diputados 2024 vigente
[INFO] ✅ mr_por_estado presente con 32 estados
[INFO] ✅ distritos_por_estado presente: 300 distritos totales
[INFO] Datos iniciales de diputados cargados exitosamente
```

O para Senado:

```
[INFO] Cargando datos iniciales: Senadores 2024 vigente
[INFO] ✅ mr_por_estado presente con 32 estados
[INFO] ✅ senadores_por_estado presente: 96 senadores totales
[INFO] Datos iniciales de senadores cargados exitosamente
```

## Checklist de Implementación Frontend

- [ ] **Actualizar llamada inicial**: Usar `GET /data/initial?camara=diputados`
- [ ] **Procesar datos geográficos**: Leer `meta.mr_por_estado` y `meta.distritos_por_estado`
- [ ] **Renderizar tabla geográfica**: Mostrar distribución por estado
- [ ] **Agregar selector de cámara**: Permitir cambiar entre Diputados/Senado
- [ ] **Validar respuesta completa**: Verificar que todos los campos estén presentes
- [ ] **Manejar errores**: Mostrar mensaje si faltan datos
- [ ] **Actualizar UI automáticamente**: Al cambiar de cámara

## Testing

```bash
# Test Diputados
curl "http://localhost:8000/data/initial?camara=diputados" | jq '.meta.mr_por_estado | keys | length'
# Debe devolver: 32

curl "http://localhost:8000/data/initial?camara=diputados" | jq '.meta.distritos_por_estado | add'
# Debe devolver: 300

# Test Senado
curl "http://localhost:8000/data/initial?camara=senadores" | jq '.meta.senadores_por_estado | add'
# Debe devolver: 96
```

## Ejemplo de Respuesta Completa (Resumida)

```json
{
  "seat_chart": [...],
  "mr": {"MORENA": 234, "PAN": 38, ...},
  "rp": {"MORENA": 0, "PAN": 33, ...},
  "tot": {"MORENA": 234, "PAN": 71, ...},
  "meta": {
    "mr_por_estado": {
      "AGUASCALIENTES": {"MORENA": 2, "PAN": 1},
      "BAJA CALIFORNIA": {"MORENA": 7, "PAN": 1},
      ...
    },
    "distritos_por_estado": {
      "AGUASCALIENTES": 3,
      "BAJA CALIFORNIA": 8,
      ...
    }
  },
  "mayorias": {...},
  "config_inicial": {...},
  "partidos_principales": [...]
}
```

---

## Resumen

✅ **Backend listo**: Endpoint `/data/initial` devuelve datos completos para ambas cámaras  
✅ **Datos geográficos incluidos**: `mr_por_estado` + `distritos_por_estado`/`senadores_por_estado`  
✅ **Senado soportado**: Usar parámetro `?camara=senadores`  
✅ **Validación automática**: Backend verifica y reporta datos presentes  
✅ **Desglose geográfico verificado**: Test local confirma que funciona correctamente

## ⚠️ IMPORTANTE: Interpretación de mr_por_estado

El desglose geográfico (`mr_por_estado`) muestra **quién ganó DIRECTAMENTE** cada distrito/estado:

```json
{
  "mr_por_estado": {
    "AGUASCALIENTES": {
      "MORENA": 0,  // ← Distritos ganados DIRECTAMENTE
      "PAN": 3      // ← PAN ganó los 3 distritos
    }
  }
}
```

**Diferencia con seat_chart/mr total**:
- `mr_por_estado`: Ganadores DIRECTOS por distrito (geografía real)
- `seat_chart.mr`: Incluye ajustes por coaliciones (escaños finales)

**Ejemplo**: En 2024 vigente:
- MORENA ganó **245 distritos directamente** → `mr_por_estado` muestra 245
- PVEM tiene **58 MR** en seat_chart → porque ganó en coalición con MORENA
- La tabla geográfica debe mostrar los **245 de MORENA** (realidad geográfica)
- El seat_chart muestra los **58 de PVEM** (realidad legislativa)

Ambos son correctos, solo muestran perspectivas diferentes del mismo resultado.

**Próximo paso**: Frontend debe actualizar la llamada inicial para usar este endpoint y procesar los datos geográficos.
