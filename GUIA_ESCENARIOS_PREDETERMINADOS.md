# 📋 Guía de Escenarios Predeterminados - Frontend

## 🎯 Resumen Ejecutivo

El backend ahora soporta **7 escenarios predeterminados** más el modo **personalizado**. Solo necesitas enviar el parámetro `plan` con uno de estos valores en el endpoint `/procesar/diputados`.

---

## 📊 DIPUTADOS - Escenarios Disponibles

### 1️⃣ **VIGENTE** (Sistema actual)
```json
{
  "plan": "vigente",
  "anio": 2024
}
```

**Características:**
- ✅ **300 MR** (Mayoría Relativa) - calculados desde datos históricos
- ✅ **200 RP** (Representación Proporcional)
- ✅ **500 TOTAL**
- ✅ **Umbral**: 3%
- ✅ **Tope**: 300 escaños máximo por partido
- ✅ **SIN Primera Minoría (PM)**
- ✅ **Método**: Hare (cuota)

**Uso en el frontend:**
```javascript
const response = await fetch('/procesar/diputados', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    anio: 2024,
    plan: "vigente"
  })
});
```

---

### 2️⃣ **PLAN A** (Solo RP - Propuesta reforma)
```json
{
  "plan": "plan_a",
  "anio": 2024
}
```

**Características:**
- ❌ **0 MR**
- ✅ **300 RP** (100% Representación Proporcional)
- ✅ **300 TOTAL**
- ✅ **Umbral**: 3%
- ❌ **SIN tope** (partidos pueden ganar lo que les corresponda)
- ❌ **SIN Primera Minoría**
- ✅ **Método**: Hare (cuota)

**Descripción:**
Elimina completamente la Mayoría Relativa. Todos los escaños se asignan proporcionalmente a los votos nacionales.

---

### 3️⃣ **PLAN C** (Solo MR - Propuesta reforma)
```json
{
  "plan": "plan_c",
  "anio": 2024
}
```

**Características:**
- ✅ **300 MR** (100% Mayoría Relativa)
- ❌ **0 RP**
- ✅ **300 TOTAL**
- ❌ **SIN umbral** (0%)
- ❌ **SIN tope**
- ❌ **SIN Primera Minoría**
- ⚠️ **NO usa método** (solo MR distrital)

**Descripción:**
Elimina completamente la Representación Proporcional. Solo cuenta quién ganó cada distrito.

---

### 4️⃣ **300-100 CON TOPES** ⭐ NUEVO
```json
{
  "plan": "300_100_con_topes",
  "anio": 2024
}
```

**Características:**
- ✅ **300 MR**
- ✅ **100 RP**
- ✅ **400 TOTAL**
- ✅ **Umbral**: 3%
- ✅ **Tope**: 300 escaños máximo por partido
- ❌ **SIN Primera Minoría**
- ✅ **Método**: Hare (cuota)
- ✅ **Redistritación geográfica**: Activa

**Descripción:**
Reduce el tamaño de la cámara a 400 escaños manteniendo los topes constitucionales.

---

### 5️⃣ **300-100 SIN TOPES** ⭐ NUEVO
```json
{
  "plan": "300_100_sin_topes",
  "anio": 2024
}
```

**Características:**
- ✅ **300 MR**
- ✅ **100 RP**
- ✅ **400 TOTAL**
- ✅ **Umbral**: 3%
- ❌ **SIN tope** (partidos pueden ganar más de 300)
- ❌ **SIN Primera Minoría**
- ✅ **Método**: Hare (cuota)
- ✅ **Redistritación geográfica**: Activa

**Descripción:**
Igual que el anterior pero sin límite de escaños por partido. Permite ver sobrerrepresentación natural.

---

### 6️⃣ **200-200 SIN TOPES** ⭐ NUEVO
```json
{
  "plan": "200_200_sin_topes",
  "anio": 2024
}
```

**Características:**
- ✅ **200 MR** (50% Mayoría Relativa)
- ✅ **200 RP** (50% Representación Proporcional)
- ✅ **400 TOTAL**
- ✅ **Umbral**: 3%
- ❌ **SIN tope**
- ❌ **SIN Primera Minoría**
- ✅ **Método**: Hare (cuota)
- ✅ **Redistritación geográfica**: Activa

**Descripción:**
Sistema más balanceado: mitad MR, mitad RP. Reduce cámara a 400 escaños.

---

### 7️⃣ **PERSONALIZADO**
```json
{
  "plan": "personalizado",
  "anio": 2024,
  "sistema": "mixto",
  "escanos_totales": 450,
  "mr_seats": 250,
  "rp_seats": 200,
  "umbral": 0.05,
  "max_seats_per_party": 280,
  "aplicar_topes": true,
  "reparto_mode": "cuota",
  "reparto_method": "hare"
}
```

**Parámetros configurables:**
- `sistema`: `"mixto"`, `"rp"`, o `"mr"`
- `escanos_totales`: Total de escaños (ej: 450, 400, 500)
- `mr_seats`: Escaños de Mayoría Relativa
- `rp_seats`: Escaños de Representación Proporcional
- `pm_seats`: (Opcional) Escaños de Primera Minoría
- `umbral`: Umbral electoral (ej: 0.03 = 3%, 0.05 = 5%)
- `max_seats_per_party`: Tope máximo de escaños por partido (null = sin tope)
- `sobrerrepresentacion`: Porcentaje máximo de sobrerrepresentación (ej: 10.8)
- `aplicar_topes`: `true` o `false` - Si aplica topes constitucionales
- `reparto_mode`: `"cuota"` o `"divisor"`
- `reparto_method`: 
  - Si `cuota`: `"hare"`, `"droop"`, `"imperiali"`
  - Si `divisor`: `"dhondt"`, `"sainte_lague"`, `"webster"`

---

## 🏛️ SENADO - Escenarios Disponibles

### 1️⃣ **VIGENTE** (Sistema actual)
```json
{
  "plan": "vigente",
  "anio": 2024
}
```

**Características:**
- ✅ **64 MR** (2 por estado)
- ✅ **32 PM** (Primera Minoría - 1 por estado)
- ✅ **32 RP** (Lista Nacional)
- ✅ **128 TOTAL**
- ✅ **Umbral**: 3%
- ✅ **Método**: Hare (cuota)

---

### 2️⃣ **PLAN A** (Solo RP)
```json
{
  "plan": "plan_a",
  "anio": 2024
}
```

**Características:**
- ❌ **0 MR**
- ❌ **0 PM**
- ✅ **96 RP** (100% Lista Nacional)
- ✅ **96 TOTAL**
- ✅ **Umbral**: 3%
- ✅ **Método**: Hare (cuota)

---

### 3️⃣ **PLAN C** (Solo MR + PM)
```json
{
  "plan": "plan_c",
  "anio": 2024
}
```

**Características:**
- ✅ **32 MR** (1 por estado)
- ✅ **32 PM** (1 por estado)
- ❌ **0 RP**
- ✅ **64 TOTAL**
- ❌ **SIN umbral** (0%)

---

### 4️⃣ **PERSONALIZADO**
```json
{
  "plan": "personalizado",
  "anio": 2024,
  "sistema": "mixto",
  "mr_seats": 64,
  "pm_seats": 32,
  "rp_seats": 32,
  "umbral": 0.03,
  "reparto_mode": "divisor",
  "reparto_method": "dhondt"
}
```

---

## 🎨 Sugerencia de UI para el Frontend

### Dropdown de Escenarios Predeterminados

```javascript
const ESCENARIOS_DIPUTADOS = [
  {
    id: 'vigente',
    nombre: 'Sistema Vigente',
    descripcion: '300 MR + 200 RP = 500 (con topes)',
    categoria: 'oficial',
    icon: '⚖️'
  },
  {
    id: 'plan_a',
    nombre: 'Plan A - Solo RP',
    descripcion: '300 RP puro (sin mayorías)',
    categoria: 'reforma',
    icon: '📊'
  },
  {
    id: 'plan_c',
    nombre: 'Plan C - Solo MR',
    descripcion: '300 MR puro (sin proporcionales)',
    categoria: 'reforma',
    icon: '🗳️'
  },
  {
    id: '300_100_con_topes',
    nombre: '300-100 con Topes',
    descripcion: '300 MR + 100 RP = 400 (tope 300)',
    categoria: 'nuevo',
    icon: '🆕',
    badge: 'NUEVO'
  },
  {
    id: '300_100_sin_topes',
    nombre: '300-100 sin Topes',
    descripcion: '300 MR + 100 RP = 400 (sin tope)',
    categoria: 'nuevo',
    icon: '🆕',
    badge: 'NUEVO'
  },
  {
    id: '200_200_sin_topes',
    nombre: '200-200 Balanceado',
    descripcion: '200 MR + 200 RP = 400 (50-50)',
    categoria: 'nuevo',
    icon: '⚖️',
    badge: 'NUEVO'
  },
  {
    id: 'personalizado',
    nombre: 'Personalizado',
    descripcion: 'Configura tus propios parámetros',
    categoria: 'custom',
    icon: '⚙️'
  }
];

const ESCENARIOS_SENADO = [
  {
    id: 'vigente',
    nombre: 'Sistema Vigente',
    descripcion: '64 MR + 32 PM + 32 RP = 128',
    categoria: 'oficial',
    icon: '⚖️'
  },
  {
    id: 'plan_a',
    nombre: 'Plan A - Solo RP',
    descripcion: '96 RP puro',
    categoria: 'reforma',
    icon: '📊'
  },
  {
    id: 'plan_c',
    nombre: 'Plan C - Solo MR+PM',
    descripcion: '32 MR + 32 PM = 64',
    categoria: 'reforma',
    icon: '🗳️'
  },
  {
    id: 'personalizado',
    nombre: 'Personalizado',
    descripcion: 'Configura tus propios parámetros',
    categoria: 'custom',
    icon: '⚙️'
  }
];
```

### Ejemplo de Componente React

```jsx
function EscenarioSelector({ camara, onSelect }) {
  const escenarios = camara === 'diputados' 
    ? ESCENARIOS_DIPUTADOS 
    : ESCENARIOS_SENADO;
  
  return (
    <div className="escenario-selector">
      <label>Escenario Predeterminado:</label>
      <select onChange={(e) => onSelect(e.target.value)}>
        {escenarios.map(esc => (
          <option key={esc.id} value={esc.id}>
            {esc.icon} {esc.nombre} - {esc.descripcion}
            {esc.badge && ` [${esc.badge}]`}
          </option>
        ))}
      </select>
    </div>
  );
}
```

---

## 🔧 Función Helper para Construir Request

```javascript
/**
 * Construye el payload para el backend según el escenario seleccionado
 * @param {string} escenario - ID del escenario ('vigente', '300_100_con_topes', etc.)
 * @param {number} anio - Año electoral (2018, 2021, 2024)
 * @param {object} customParams - Parámetros adicionales para personalizado
 * @returns {object} Payload listo para enviar al backend
 */
function buildRequestPayload(escenario, anio, customParams = {}) {
  const basePayload = {
    anio,
    plan: escenario
  };
  
  // Si es personalizado, agregar todos los parámetros custom
  if (escenario === 'personalizado') {
    return {
      ...basePayload,
      ...customParams
    };
  }
  
  // Para escenarios predeterminados, solo enviar plan y año
  return basePayload;
}

// Uso:
const payload = buildRequestPayload('300_100_con_topes', 2024);
// Resultado: { anio: 2024, plan: "300_100_con_topes" }

const payloadCustom = buildRequestPayload('personalizado', 2024, {
  sistema: 'mixto',
  mr_seats: 250,
  rp_seats: 150,
  umbral: 0.05,
  aplicar_topes: false
});
```

---

## 📝 Notas Importantes

### ✅ Lo que ya funciona:
- `vigente`, `plan_a`, `plan_c` ya están implementados en el frontend
- `personalizado` ya funciona con parámetros

### 🆕 Lo que hay que agregar:
- **3 nuevos escenarios**: `300_100_con_topes`, `300_100_sin_topes`, `200_200_sin_topes`
- Solo necesitas agregarlos al dropdown/selector
- El backend los reconoce automáticamente

### 🎯 Validaciones del Backend:
- Si envías `escanos_totales` en plan_a, plan_c o escenarios nuevos → **será ignorado** (están hardcodeados)
- Si envías parámetros incompatibles → El backend devuelve error 400 con detalle
- Si falta un parámetro requerido en `personalizado` → Error 400

### 🔄 Compatibilidad:
- Todos los escenarios son compatibles con:
  - ✅ Sliders de partidos (porcentajes)
  - ✅ Sliders nacionales MR (`mr_distritos_manuales`)
  - ✅ Flechitas geográficas (`mr_distritos_por_estado`)
  - ✅ Votos custom, partidos fijos, overrides pool

---

## 🚀 Checklist de Implementación Frontend

- [ ] Agregar 3 nuevos escenarios al selector de Diputados
- [ ] Agregar badges "NUEVO" o íconos distintivos
- [ ] Actualizar tooltips/descripciones con características de cada escenario
- [ ] Agregar validación: deshabilitar campos incompatibles según escenario
- [ ] Agregar indicadores visuales de diferencias clave (topes sí/no, totales, etc.)
- [ ] Crear sección de "Comparar Escenarios" (opcional)
- [ ] Documentar en ayuda/tutorial del usuario

---

## 📊 Tabla Comparativa Rápida - DIPUTADOS

| Escenario | Total | MR | RP | Umbral | Tope | PM |
|-----------|-------|----|----|--------|------|----|
| **Vigente** | 500 | 300 | 200 | 3% | 300 | ❌ |
| **Plan A** | 300 | 0 | 300 | 3% | ❌ | ❌ |
| **Plan C** | 300 | 300 | 0 | ❌ | ❌ | ❌ |
| **300-100 (con topes)** | 400 | 300 | 100 | 3% | 300 | ❌ |
| **300-100 (sin topes)** | 400 | 300 | 100 | 3% | ❌ | ❌ |
| **200-200** | 400 | 200 | 200 | 3% | ❌ | ❌ |
| **Personalizado** | ⚙️ | ⚙️ | ⚙️ | ⚙️ | ⚙️ | ⚙️ |

---

## 🎨 Ejemplo de Código Frontend Completo

```javascript
// Estado del componente
const [escenarioActual, setEscenarioActual] = useState('vigente');
const [modoPersonalizado, setModoPersonalizado] = useState(false);

// Handler para cambio de escenario
const handleEscenarioChange = (nuevoEscenario) => {
  setEscenarioActual(nuevoEscenario);
  setModoPersonalizado(nuevoEscenario === 'personalizado');
  
  // Enviar request al backend
  procesarEscenario(nuevoEscenario);
};

// Función para procesar escenario
const procesarEscenario = async (escenario) => {
  const payload = {
    anio: añoSeleccionado,
    plan: escenario
  };
  
  // Si es personalizado, agregar parámetros del formulario
  if (escenario === 'personalizado') {
    payload.sistema = sistemaPersonalizado;
    payload.mr_seats = mrSeats;
    payload.rp_seats = rpSeats;
    // ... más parámetros
  }
  
  try {
    const response = await fetch('/procesar/diputados', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      console.error('Error:', data.detail);
      return;
    }
    
    // Actualizar UI con resultados
    actualizarResultados(data);
    
  } catch (error) {
    console.error('Error de red:', error);
  }
};
```

---

¿Necesitas más detalles sobre algún escenario en particular? 🎯
