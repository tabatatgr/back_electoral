# 🚀 Resumen Ejecutivo: Nuevos Escenarios para Frontend

## ✅ ¿Qué hay que hacer?

El backend ya tiene **3 nuevos escenarios** implementados y listos para usar. Solo necesitas agregarlos al selector/dropdown del frontend.

---

## 📋 Nuevos Escenarios Disponibles

### DIPUTADOS

#### 1. **300_100_con_topes** 🆕
```javascript
{
  plan: "300_100_con_topes",
  anio: 2024
}
```
- 300 MR + 100 RP = **400 total**
- CON topes (300 máx por partido)
- Cámara más pequeña, mantiene topes constitucionales

#### 2. **300_100_sin_topes** 🆕
```javascript
{
  plan: "300_100_sin_topes",
  anio: 2024
}
```
- 300 MR + 100 RP = **400 total**
- SIN topes
- Permite ver sobrerrepresentación natural

#### 3. **200_200_sin_topes** 🆕
```javascript
{
  plan: "200_200_sin_topes",
  anio: 2024
}
```
- 200 MR + 200 RP = **400 total**
- SIN topes
- Sistema más balanceado (50-50)

---

## 🔗 Endpoints Disponibles

### 1. **GET /data/escenarios**
Devuelve la lista completa de escenarios con todas sus características:

```javascript
const response = await fetch('http://localhost:8000/data/escenarios');
const data = await response.json();

console.log(data.diputados); // Array con todos los escenarios de diputados
console.log(data.senado);    // Array con todos los escenarios de senado
```

**Respuesta de ejemplo:**
```json
{
  "diputados": [
    {
      "id": "vigente",
      "nombre": "Sistema Vigente",
      "descripcion": "300 MR + 200 RP = 500 (con topes)",
      "categoria": "oficial",
      "icon": "⚖️",
      "detalles": {
        "total": 500,
        "mr": 300,
        "rp": 200,
        "umbral": 0.03,
        "tope_max": 300
      }
    },
    {
      "id": "300_100_con_topes",
      "nombre": "300-100 con Topes",
      "descripcion": "300 MR + 100 RP = 400 (tope 300)",
      "categoria": "nuevo",
      "icon": "🆕",
      "badge": "NUEVO",
      "detalles": {
        "total": 400,
        "mr": 300,
        "rp": 100,
        "tope_max": 300
      }
    }
    // ... más escenarios
  ],
  "senado": [ /* ... */ ]
}
```

### 2. **GET /data/options** (Actualizado)
Ahora incluye todos los planes en el array `planes`:

```javascript
const response = await fetch('http://localhost:8000/data/options');
const data = await response.json();

console.log(data.planes);
// ["vigente", "plan_a", "plan_c", "300_100_con_topes", "300_100_sin_topes", "200_200_sin_topes", "personalizado"]
```

---

## 💻 Implementación Frontend

### Opción 1: Hardcodear (Más rápido)

```javascript
const ESCENARIOS_DIPUTADOS = [
  {
    id: 'vigente',
    nombre: 'Sistema Vigente',
    descripcion: '300 MR + 200 RP = 500',
    badge: null
  },
  {
    id: 'plan_a',
    nombre: 'Plan A - Solo RP',
    descripcion: '300 RP puro',
    badge: null
  },
  {
    id: 'plan_c',
    nombre: 'Plan C - Solo MR',
    descripcion: '300 MR puro',
    badge: null
  },
  {
    id: '300_100_con_topes',
    nombre: '300-100 con Topes',
    descripcion: '300 MR + 100 RP = 400',
    badge: 'NUEVO'
  },
  {
    id: '300_100_sin_topes',
    nombre: '300-100 sin Topes',
    descripcion: '300 MR + 100 RP = 400',
    badge: 'NUEVO'
  },
  {
    id: '200_200_sin_topes',
    nombre: '200-200 Balanceado',
    descripcion: '200 MR + 200 RP = 400',
    badge: 'NUEVO'
  },
  {
    id: 'personalizado',
    nombre: 'Personalizado',
    descripcion: 'Configura parámetros',
    badge: null
  }
];

// En tu componente:
<select onChange={(e) => handlePlanChange(e.target.value)}>
  {ESCENARIOS_DIPUTADOS.map(esc => (
    <option key={esc.id} value={esc.id}>
      {esc.nombre} - {esc.descripcion}
      {esc.badge && ` [${esc.badge}]`}
    </option>
  ))}
</select>
```

### Opción 2: Cargar desde API (Más flexible)

```javascript
import { useEffect, useState } from 'react';

function EscenarioSelector() {
  const [escenarios, setEscenarios] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetch('http://localhost:8000/data/escenarios')
      .then(res => res.json())
      .then(data => {
        setEscenarios(data.diputados); // o data.senado
        setLoading(false);
      })
      .catch(err => {
        console.error('Error cargando escenarios:', err);
        setLoading(false);
      });
  }, []);
  
  if (loading) return <div>Cargando...</div>;
  
  return (
    <select onChange={(e) => handlePlanChange(e.target.value)}>
      {escenarios.map(esc => (
        <option key={esc.id} value={esc.id}>
          {esc.icon} {esc.nombre} - {esc.descripcion}
          {esc.badge && ` [${esc.badge}]`}
        </option>
      ))}
    </select>
  );
}
```

---

## 🎨 Ejemplo de UI Mejorada

### Con badges y categorías:

```jsx
function EscenarioSelectorMejorado({ onChange }) {
  const [escenarios, setEscenarios] = useState([]);
  
  useEffect(() => {
    fetch('/data/escenarios')
      .then(res => res.json())
      .then(data => setEscenarios(data.diputados));
  }, []);
  
  // Agrupar por categoría
  const oficial = escenarios.filter(e => e.categoria === 'oficial');
  const reforma = escenarios.filter(e => e.categoria === 'reforma');
  const nuevos = escenarios.filter(e => e.categoria === 'nuevo');
  const custom = escenarios.filter(e => e.categoria === 'custom');
  
  return (
    <select onChange={(e) => onChange(e.target.value)}>
      <optgroup label="📌 Sistema Actual">
        {oficial.map(esc => (
          <option key={esc.id} value={esc.id}>
            {esc.nombre}
          </option>
        ))}
      </optgroup>
      
      <optgroup label="📋 Propuestas de Reforma">
        {reforma.map(esc => (
          <option key={esc.id} value={esc.id}>
            {esc.nombre}
          </option>
        ))}
      </optgroup>
      
      <optgroup label="🆕 Nuevos Escenarios">
        {nuevos.map(esc => (
          <option key={esc.id} value={esc.id}>
            {esc.nombre} ⭐
          </option>
        ))}
      </optgroup>
      
      <optgroup label="⚙️ Personalizar">
        {custom.map(esc => (
          <option key={esc.id} value={esc.id}>
            {esc.nombre}
          </option>
        ))}
      </optgroup>
    </select>
  );
}
```

---

## 📝 Checklist de Implementación

### Paso 1: Actualizar constantes
- [ ] Agregar 3 nuevos escenarios al array de opciones
- [ ] Agregar badges "NUEVO" o íconos ⭐

### Paso 2: Actualizar UI
- [ ] Verificar que el selector muestre los nuevos escenarios
- [ ] Agregar separadores visuales por categoría (opcional)
- [ ] Agregar tooltips con detalles de cada escenario (opcional)

### Paso 3: Probar
- [ ] Probar cada nuevo escenario enviando request al backend
- [ ] Verificar que los resultados se muestren correctamente
- [ ] Verificar que los sliders/flechitas funcionen con los nuevos escenarios

### Paso 4: Documentar (opcional)
- [ ] Agregar sección de ayuda/tutorial para nuevos escenarios
- [ ] Agregar tabla comparativa visual

---

## 🧪 Testing Rápido

### Test 1: Verificar endpoint de escenarios
```bash
curl http://localhost:8000/data/escenarios
```

### Test 2: Probar nuevo escenario
```bash
curl -X POST http://localhost:8000/procesar/diputados \
  -H "Content-Type: application/json" \
  -d '{"anio": 2024, "plan": "300_100_con_topes"}'
```

### Test 3: Verificar data/options actualizado
```bash
curl http://localhost:8000/data/options
```

---

## ❓ FAQ

**P: ¿Necesito cambiar algo en mi código para que funcionen los nuevos escenarios?**  
R: No, solo agrégalos al selector. El backend ya los reconoce automáticamente.

**P: ¿Los sliders y flechitas funcionan con los nuevos escenarios?**  
R: Sí, todos los escenarios son compatibles con sliders y flechitas.

**P: ¿Puedo combinar escenarios con parámetros personalizados?**  
R: No, los escenarios predeterminados tienen parámetros fijos. Para customizar usa `plan: "personalizado"`.

**P: ¿Qué pasa si envío `escanos_totales` con un escenario predeterminado?**  
R: El backend lo ignorará. Los escenarios predeterminados tienen totales fijos.

---

## 📄 Archivos de Referencia

- **Guía completa**: `GUIA_ESCENARIOS_PREDETERMINADOS.md`
- **Endpoint de escenarios**: `GET /data/escenarios`
- **Endpoint de opciones**: `GET /data/options`

---

¿Necesitas ayuda con la implementación? 🤝
