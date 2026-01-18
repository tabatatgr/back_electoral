# ✅ FIX: Parámetro `solo_partido` en Mayoría Forzada

## 🎯 Problema Resuelto

Cuando se calculaba mayoría forzada para `partido=MORENA`, el backend estaba sumando automáticamente los escaños de **toda la coalición 4T** (MORENA + PT + PVEM) en lugar de solo MORENA.

## 🔧 Solución Implementada

Se agregó el parámetro **`solo_partido`** (boolean) en ambos endpoints:
- `/calcular/mayoria_forzada` (Diputados)
- `/calcular/mayoria_forzada_senado` (Senado)

---

## 📋 Parámetro `solo_partido`

### Valores:
- **`solo_partido=true`** (DEFAULT) → Cuenta **SOLO** el partido especificado
- **`solo_partido=false`** → Cuenta **toda la coalición**

### Comportamiento:

#### ✅ `solo_partido=true` (Solo partido individual)
```
GET /calcular/mayoria_forzada?partido=MORENA&tipo_mayoria=simple&solo_partido=true
```

**Resultado:**
```json
{
  "viable": true,
  "diputados_obtenidos": 251,  // ← SOLO MORENA
  "mr_asignados": 180,          // ← SOLO MORENA
  "rp_asignados": 71,           // ← SOLO MORENA
  "solo_partido": true,
  "seat_chart": [
    { "party": "MORENA", "seats": 251, ... },
    { "party": "PT", "seats": 45, ... },      // ← PT NO se suma
    { "party": "PVEM", "seats": 38, ... }     // ← PVEM NO se suma
  ]
}
```

---

#### 🤝 `solo_partido=false` (Coalición completa)
```
GET /calcular/mayoria_forzada?partido=MORENA&tipo_mayoria=simple&solo_partido=false
```

**Resultado:**
```json
{
  "viable": true,
  "diputados_obtenidos": 334,  // ← MORENA + PT + PVEM
  "mr_asignados": 230,          // ← Suma de los 3 partidos
  "rp_asignados": 104,          // ← Suma de los 3 partidos
  "solo_partido": false,
  "seat_chart": [
    { "party": "MORENA", "seats": 251, ... },
    { "party": "PT", "seats": 45, ... },      // ← PT SÍ se suma
    { "party": "PVEM", "seats": 38, ... }     // ← PVEM SÍ se suma
  ]
}
```

---

## 🔍 Detección Automática de Coaliciones

### Si el parámetro `partido` contiene `+`, se fuerza `solo_partido=false`:

```
GET /calcular/mayoria_forzada?partido=MORENA+PT+PVEM&tipo_mayoria=calificada
```

**Comportamiento:**
- El backend detecta el `+` en el nombre
- Automáticamente establece `solo_partido=false`
- Suma los escaños de MORENA + PT + PVEM

---

## 🏛️ Coaliciones Reconocidas

### Coalición 4T (2024):
- **Miembros:** MORENA, PT, PVEM
- **Nombre:** "4T (MORENA+PT+PVEM)"

Si `partido=MORENA` y `solo_partido=false`, suma MORENA + PT + PVEM

### Coalición Fuerza y Corazón por México:
- **Miembros:** PAN, PRI, PRD
- **Nombre:** "Fuerza y Corazón por México (PAN+PRI+PRD)"

Si `partido=PAN` y `solo_partido=false`, suma PAN + PRI + PRD

### Coaliciones Explícitas:
Si envías `partido=MORENA+PT+PVEM`, el backend divide por `+` y suma esos partidos específicos.

---

## 📡 Ejemplos de Uso

### Caso 1: MORENA solo (mayoría simple)
```bash
GET /calcular/mayoria_forzada?partido=MORENA&tipo_mayoria=simple&plan=vigente&aplicar_topes=true&anio=2024&solo_partido=true
```

**Esperado:**
- `diputados_obtenidos`: Solo escaños de MORENA
- `seat_chart`: Todos los partidos, pero el conteo solo incluye MORENA

---

### Caso 2: Coalición 4T completa (mayoría calificada)
```bash
GET /calcular/mayoria_forzada?partido=MORENA&tipo_mayoria=calificada&plan=vigente&aplicar_topes=false&anio=2024&solo_partido=false
```

**Esperado:**
- `diputados_obtenidos`: MORENA + PT + PVEM sumados
- `seat_chart`: Todos los partidos con sus valores individuales

---

### Caso 3: Coalición explícita (PAN+PRI)
```bash
GET /calcular/mayoria_forzada?partido=PAN+PRI&tipo_mayoria=simple&plan=vigente&aplicar_topes=true&anio=2024
```

**Esperado:**
- `solo_partido`: Automáticamente `false` (detecta el `+`)
- `diputados_obtenidos`: PAN + PRI sumados
- PRD NO se incluye (solo los partidos especificados en el parámetro)

---

## 🧪 Verificación

### Test 1: Solo MORENA
```bash
curl "http://localhost:8000/calcular/mayoria_forzada?partido=MORENA&tipo_mayoria=simple&plan=vigente&aplicar_topes=true&anio=2024&solo_partido=true"
```

**Verificar:**
- `solo_partido` debe ser `true`
- `diputados_obtenidos` debe ser < 300 (solo MORENA, sin PT ni PVEM)

---

### Test 2: Coalición 4T
```bash
curl "http://localhost:8000/calcular/mayoria_forzada?partido=MORENA&tipo_mayoria=simple&plan=vigente&aplicar_topes=true&anio=2024&solo_partido=false"
```

**Verificar:**
- `solo_partido` debe ser `false`
- `diputados_obtenidos` debe ser > 300 (incluye PT y PVEM)

---

### Test 3: Coalición explícita con `+`
```bash
curl "http://localhost:8000/calcular/mayoria_forzada?partido=MORENA+PT+PVEM&tipo_mayoria=calificada&plan=vigente&aplicar_topes=false&anio=2024"
```

**Verificar:**
- `solo_partido` debe ser `false` (forzado por el `+`)
- `partido` debe ser `"MORENA+PT+PVEM"`
- `diputados_obtenidos` debe incluir los 3 partidos

---

## 🎨 Implementación en Frontend

### Opción 1: Toggle switch
```jsx
const [soloPartido, setSoloPartido] = useState(true);

<label>
  <input
    type="checkbox"
    checked={soloPartido}
    onChange={(e) => setSoloPartido(e.target.checked)}
  />
  Contar solo {partidoSeleccionado} (sin coalición)
</label>

// Al hacer la llamada:
const url = `/calcular/mayoria_forzada?partido=${partido}&tipo_mayoria=${tipo}&solo_partido=${soloPartido}`;
```

---

### Opción 2: Radio buttons
```jsx
const [modoConteo, setModoConteo] = useState('solo'); // 'solo' o 'coalicion'

<div>
  <label>
    <input
      type="radio"
      value="solo"
      checked={modoConteo === 'solo'}
      onChange={(e) => setModoConteo(e.target.value)}
    />
    Solo {partidoSeleccionado}
  </label>
  
  <label>
    <input
      type="radio"
      value="coalicion"
      checked={modoConteo === 'coalicion'}
      onChange={(e) => setModoConteo(e.target.value)}
    />
    Coalición completa ({partidoSeleccionado}+PT+PVEM)
  </label>
</div>

// Al hacer la llamada:
const soloPartido = modoConteo === 'solo';
const url = `/calcular/mayoria_forzada?partido=${partido}&tipo_mayoria=${tipo}&solo_partido=${soloPartido}`;
```

---

### Opción 3: Selector de coalición
```jsx
const [partidoSeleccionado, setPartidoSeleccionado] = useState('MORENA');

<select onChange={(e) => setPartidoSeleccionado(e.target.value)}>
  <option value="MORENA">Solo MORENA</option>
  <option value="MORENA+PT+PVEM">Coalición 4T (MORENA+PT+PVEM)</option>
  <option value="PAN">Solo PAN</option>
  <option value="PAN+PRI+PRD">Coalición Fuerza y Corazón (PAN+PRI+PRD)</option>
</select>

// El backend detecta automáticamente si tiene "+" y aplica solo_partido=false
const url = `/calcular/mayoria_forzada?partido=${partidoSeleccionado}&tipo_mayoria=${tipo}`;
```

---

## 📊 Respuesta Actualizada

La respuesta ahora incluye el campo `solo_partido` para que el frontend sepa cómo se calculó:

```json
{
  "viable": true,
  "diputados_necesarios": 251,
  "diputados_obtenidos": 334,
  "votos_porcentaje": 47.0,
  "mr_asignados": 230,
  "rp_asignados": 104,
  "partido": "MORENA",
  "plan": "vigente",
  "tipo_mayoria": "simple",
  "solo_partido": false,  // ← NUEVO: Indica si se contó solo el partido o coalición
  "seat_chart": [ ... ],
  "kpis": { ... }
}
```

---

## ⚠️ Notas Importantes

1. **Default es `solo_partido=true`**: Si no se especifica, cuenta solo el partido
2. **Coaliciones explícitas con `+`**: Fuerzan `solo_partido=false` automáticamente
3. **Compatibilidad hacia atrás**: Las llamadas anteriores sin el parámetro seguirán funcionando (con `solo_partido=true`)
4. **Senado funciona igual**: El mismo parámetro está disponible en `/calcular/mayoria_forzada_senado`

---

## 🚀 Estado Actual

✅ **Implementado en:**
- `GET /calcular/mayoria_forzada` (Diputados)
- `GET /calcular/mayoria_forzada_senado` (Senado)

✅ **Funcionando:**
- Detección automática de coaliciones con `+`
- Suma correcta de escaños según `solo_partido`
- Respuesta incluye el flag `solo_partido` para confirmación

🎯 **Listo para usar en frontend**

---

¿Necesitas más ejemplos o tienes alguna duda? 🙋‍♂️
