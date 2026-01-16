# Sliders de Distritos por Partido (MR Ajustables)

## Descripción
Permite al usuario ajustar manualmente cuántos distritos de Mayoría Relativa (MR) gana cada partido usando sliders interactivos. El sistema reajusta automáticamente los demás partidos para mantener el total constante.

## Funcionamiento

### 1. Parámetros del Endpoint

**Endpoint:** `POST /procesar/diputados`

**Parámetros relevantes:**
```json
{
  "anio": 2024,
  "plan": "personalizado",
  "total_distritos": 300,  // Total de distritos a distribuir
  "mr_distritos_manuales": "{\"MORENA\": 180, \"PAN\": 60, \"PRI\": 40, \"PVEM\": 20}"  // JSON string
}
```

### 2. Flujo de Uso

#### Paso 1: Obtener Distribución Inicial
El frontend hace una petición inicial para obtener la distribución base:

```javascript
const responseInicial = await fetch('/procesar/diputados', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    anio: 2024,
    plan: 'vigente',
    total_distritos: 300
  })
});

const data = await responseInicial.json();
const mrInicial = data.mr;  // {"MORENA": 234, "PAN": 38, "PRI": 18, ...}
```

#### Paso 2: Renderizar Sliders por Partido
```jsx
{Object.entries(mrInicial).map(([partido, escanos]) => (
  <div key={partido}>
    <label>{partido}: {escanos} distritos</label>
    <input 
      type="range" 
      min="0" 
      max={totalDistritos}  // 300
      value={escanos}
      onChange={(e) => ajustarDistrito(partido, e.target.value)}
    />
  </div>
))}
```

#### Paso 3: Ajustar Automáticamente los Demás Partidos
Cuando el usuario mueve un slider, el frontend debe:

1. **Actualizar el partido modificado**
2. **Calcular la diferencia** (ej: MORENA sube de 234 → 250 = +16)
3. **Redistribuir la diferencia** entre los demás partidos proporcionalmente

```javascript
function ajustarDistrito(partidoModificado, nuevoValor) {
  const valorAnterior = mrActual[partidoModificado];
  const diferencia = nuevoValor - valorAnterior;
  
  // Actualizar el partido modificado
  const nuevoMr = { ...mrActual };
  nuevoMr[partidoModificado] = parseInt(nuevoValor);
  
  // Calcular total de otros partidos
  const otrosPartidos = Object.keys(mrActual).filter(p => p !== partidoModificado);
  const totalOtros = otrosPartidos.reduce((sum, p) => sum + mrActual[p], 0);
  
  // Redistribuir proporcionalmente
  otrosPartidos.forEach(partido => {
    const proporcion = mrActual[partido] / totalOtros;
    const ajuste = Math.round(-diferencia * proporcion);
    nuevoMr[partido] = Math.max(0, mrActual[partido] + ajuste);
  });
  
  // Normalizar para asegurar que suma = total_distritos
  const suma = Object.values(nuevoMr).reduce((a, b) => a + b, 0);
  if (suma !== totalDistritos) {
    // Ajustar el partido con más escaños
    const partidoMayor = Object.keys(nuevoMr).reduce((a, b) => 
      nuevoMr[a] > nuevoMr[b] ? a : b
    );
    nuevoMr[partidoMayor] += (totalDistritos - suma);
  }
  
  setMrActual(nuevoMr);
  
  // Enviar al backend
  recalcular(nuevoMr);
}
```

#### Paso 4: Enviar al Backend y Recalcular
```javascript
async function recalcular(mrManual) {
  const response = await fetch('/procesar/diputados', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      anio: 2024,
      plan: 'personalizado',
      sistema: 'mixto',
      total_distritos: 300,
      mr_seats: 300,
      rp_seats: 200,
      mr_distritos_manuales: JSON.stringify(mrManual)
    })
  });
  
  const data = await response.json();
  
  // Actualizar UI con nuevos resultados
  actualizarTabla(data.seat_chart);
  actualizarGraficas(data);
}
```

### 3. Validación Backend

El backend ya valida que:
```python
# En main.py líneas 2830-2850
if mr_distritos_manuales:
    mr_ganados_geograficos = json.loads(mr_distritos_manuales)
    
    # Validar que el total no exceda mr_seats_final
    total_mr_manuales = sum(mr_ganados_geograficos.values())
    if total_mr_manuales > mr_seats_final:
        raise HTTPException(
            status_code=400,
            detail=f"La suma de MR manuales ({total_mr_manuales}) excede el total de escaños MR ({mr_seats_final})"
        )
```

### 4. Ejemplo Completo de Request

```json
POST /procesar/diputados
{
  "anio": 2024,
  "plan": "personalizado",
  "sistema": "mixto",
  "escanos_totales": 500,
  "mr_seats": 300,
  "rp_seats": 200,
  "total_distritos": 300,
  "mr_distritos_manuales": "{\"MORENA\": 250, \"PAN\": 30, \"PRI\": 15, \"PVEM\": 5}",
  "aplicar_topes": true
}
```

**Respuesta esperada:**
```json
{
  "mr": {
    "MORENA": 250,  // ← Valor del slider
    "PAN": 30,      // ← Valor del slider
    "PRI": 15,      // ← Valor del slider
    "PVEM": 5       // ← Valor del slider
  },
  "rp": {
    "MORENA": 50,   // ← Calculado automáticamente por el backend
    "PAN": 80,
    "PRI": 50,
    "PVEM": 20
  },
  "tot": {
    "MORENA": 300,  // MR + RP (puede estar limitado por topes)
    "PAN": 110,
    "PRI": 65,
    "PVEM": 25
  },
  "seat_chart": [...],
  "meta": {
    "mr_por_estado": {
      "AGUASCALIENTES": {"MORENA": 2, "PAN": 1},
      // ... distribución geográfica recalculada
    }
  }
}
```

## Características Importantes

### ✅ Lo que el Backend Hace Automáticamente:

1. **Validación de Totales**: Verifica que la suma de MR manuales = `mr_seats`
2. **Recálculo de RP**: Calcula los escaños de RP basándose en los MR manuales
3. **Aplicación de Topes**: Si `aplicar_topes=true`, limita cada partido a 300 escaños
4. **Distribución Geográfica**: Distribuye los MR manuales por estado usando el método Hare
5. **Cálculo de Mayorías**: Detecta mayoría simple/calificada con los nuevos valores

### ⚠️ Lo que el Frontend Debe Hacer:

1. **Ajuste Proporcional**: Cuando un slider sube, bajar los demás proporcionalmente
2. **Validación Cliente**: Asegurar que la suma de sliders = `total_distritos`
3. **Debouncing**: Evitar enviar requests en cada movimiento del slider
4. **Feedback Visual**: Mostrar qué partido pierde/gana al mover un slider

## Ejemplo de UI Recomendada

```
┌─────────────────────────────────────────────┐
│  DISTRIBUCIÓN DE DISTRITOS MR (300 total)   │
├─────────────────────────────────────────────┤
│                                             │
│  MORENA: 250 distritos                      │
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░ 250/300    │
│  [━━━━━━━━━━━━━━━━━━━━●━━━━━━━━━━━━━━━]    │
│                                             │
│  PAN: 30 distritos (↓ -8 por ajuste)       │
│  ▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 30/300    │
│  [━━━●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━]    │
│                                             │
│  PRI: 15 distritos (↓ -3 por ajuste)       │
│  ▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 15/300    │
│  [━●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━]    │
│                                             │
│  PVEM: 5 distritos (↓ -5 por ajuste)       │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 5/300     │
│  [●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━]    │
│                                             │
│  [Recalcular Resultados]                    │
└─────────────────────────────────────────────┘
```

## Casos de Uso

### Caso 1: Usuario sube MORENA de 234 → 250 (+16)
```
ANTES:  MORENA=234, PAN=38, PRI=18, PVEM=10  (total=300)
DESPUÉS: MORENA=250, PAN=30, PRI=15, PVEM=5   (total=300)
```

El frontend distribuye los -16 proporcionalmente:
- PAN pierde 8 (38 × 16/66 ≈ 8)
- PRI pierde 3 (18 × 16/66 ≈ 3)
- PVEM pierde 5 (10 × 16/66 ≈ 5)

### Caso 2: Usuario baja PAN de 38 → 20 (-18)
```
ANTES:  MORENA=234, PAN=38, PRI=18, PVEM=10  (total=300)
DESPUÉS: MORENA=246, PAN=20, PRI=24, PVEM=10  (total=300)
```

Los +18 se distribuyen a los demás:
- MORENA gana 12 (234/(234+18+10) × 18 ≈ 12)
- PRI gana 6 (18/(234+18+10) × 18 ≈ 6)

## Implementación Completa en React

```jsx
import { useState, useEffect } from 'react';

function DistritosSliders() {
  const [totalDistritos, setTotalDistritos] = useState(300);
  const [mrDistribucion, setMrDistribucion] = useState({});
  const [loading, setLoading] = useState(false);
  
  // Cargar distribución inicial
  useEffect(() => {
    async function cargarInicial() {
      const res = await fetch('/procesar/diputados', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          anio: 2024,
          plan: 'vigente',
          total_distritos: totalDistritos
        })
      });
      const data = await res.json();
      setMrDistribucion(data.mr);
    }
    cargarInicial();
  }, []);
  
  const ajustarPartido = (partido, nuevoValor) => {
    const valorAnterior = mrDistribucion[partido];
    const diferencia = parseInt(nuevoValor) - valorAnterior;
    
    const nuevoMr = { ...mrDistribucion };
    nuevoMr[partido] = parseInt(nuevoValor);
    
    // Redistribuir entre otros
    const otros = Object.keys(nuevoMr).filter(p => p !== partido);
    const totalOtros = otros.reduce((sum, p) => sum + mrDistribucion[p], 0);
    
    otros.forEach(p => {
      const proporcion = mrDistribucion[p] / totalOtros;
      nuevoMr[p] = Math.max(0, mrDistribucion[p] - Math.round(diferencia * proporcion));
    });
    
    // Normalizar
    const suma = Object.values(nuevoMr).reduce((a, b) => a + b, 0);
    if (suma !== totalDistritos) {
      const mayor = Object.keys(nuevoMr).reduce((a, b) => nuevoMr[a] > nuevoMr[b] ? a : b);
      nuevoMr[mayor] += (totalDistritos - suma);
    }
    
    setMrDistribucion(nuevoMr);
  };
  
  const recalcular = async () => {
    setLoading(true);
    const res = await fetch('/procesar/diputados', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        anio: 2024,
        plan: 'personalizado',
        sistema: 'mixto',
        mr_seats: totalDistritos,
        rp_seats: 200,
        total_distritos: totalDistritos,
        mr_distritos_manuales: JSON.stringify(mrDistribucion)
      })
    });
    const data = await res.json();
    // Actualizar UI con data.seat_chart, data.tot, etc.
    setLoading(false);
  };
  
  return (
    <div>
      <h3>Distribución Manual de Distritos MR ({totalDistritos} total)</h3>
      {Object.entries(mrDistribucion).map(([partido, escanos]) => (
        <div key={partido}>
          <label>{partido}: {escanos}</label>
          <input
            type="range"
            min="0"
            max={totalDistritos}
            value={escanos}
            onChange={(e) => ajustarPartido(partido, e.target.value)}
          />
        </div>
      ))}
      <button onClick={recalcular} disabled={loading}>
        {loading ? 'Recalculando...' : 'Aplicar Cambios'}
      </button>
    </div>
  );
}
```

## Notas Técnicas

- **Performance**: El backend puede recalcular en ~500ms para 300 distritos
- **Caché**: No usar caché en el navegador (`Cache-Control: no-cache`)
- **Validación**: El backend rechaza totales incorrectos con HTTP 400
- **Topes**: Si `aplicar_topes=true`, el total final puede ser < escanos_totales

## Ejemplo de Error

Si el usuario envía suma incorrecta:
```json
{
  "mr_distritos_manuales": "{\"MORENA\": 200, \"PAN\": 150}"  // suma = 350 > 300
}
```

**Respuesta:**
```json
HTTP 400
{
  "detail": "La suma de MR manuales (350) excede el total de escaños MR (300)"
}
```
