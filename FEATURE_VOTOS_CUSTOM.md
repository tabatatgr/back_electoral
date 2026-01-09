# Feature: Edición de Votos Personalizados (votos_custom)

## 📋 Descripción

Cuando el usuario selecciona **"Plan Personalizado"**, debe aparecer un **toggle/switch** que permite activar/desactivar la edición manual de porcentajes de votos por partido.

---

## 🎨 UI/UX Propuesto

### Estado: Plan Personalizado DESACTIVADO
```
┌─────────────────────────────────────────────────┐
│ Plan Electoral: [Personalizado ▼]              │
│                                                  │
│ ☐ Editar distribución de votos                 │
│   (desactivado - usa votos históricos reales)   │
└─────────────────────────────────────────────────┘
```

### Estado: Edición de Votos ACTIVADA
```
┌─────────────────────────────────────────────────┐
│ Plan Electoral: [Personalizado ▼]              │
│                                                  │
│ ☑ Editar distribución de votos                 │
│                                                  │
│ ┌─────────────────────────────────────────────┐ │
│ │ MORENA:  [40.0] %  ═══════════════════════  │ │
│ │ PAN:     [20.0] %  ══════════════           │ │
│ │ PRI:     [12.0] %  ════════                 │ │
│ │ PVEM:    [ 8.0] %  ═════                    │ │
│ │ PT:      [ 6.0] %  ════                     │ │
│ │ MC:      [ 9.0] %  ══════                   │ │
│ │ PRD:     [ 5.0] %  ███                      │ │
│ │                                              │ │
│ │ Total: 100.0% ✓                             │ │
│ └─────────────────────────────────────────────┘ │
│                                                  │
│ ⚠️ Los votos reales de 2024 serán reemplazados │
└─────────────────────────────────────────────────┘
```

---

## 🔧 Implementación Backend (ya disponible)

### Endpoint
```
POST /procesar/diputados
```

### Parámetros

**SIN votos personalizados (default):**
```json
{
  "anio": 2024,
  "plan": "personalizado",
  "escanos_totales": 500,
  "sistema": "mixto",
  "mr_seats": 300,
  "rp_seats": 200,
  "umbral": 0.03
  // votos_custom NO enviado → usa votos históricos reales
}
```

**CON votos personalizados:**
```json
{
  "anio": 2024,
  "plan": "personalizado",
  "escanos_totales": 500,
  "sistema": "mixto",
  "mr_seats": 300,
  "rp_seats": 200,
  "umbral": 0.03,
  "votos_custom": "{\"MORENA\":40,\"PAN\":20,\"PRI\":12,\"PVEM\":8,\"PT\":6,\"MC\":9,\"PRD\":5}"
}
```

### Formato de votos_custom

**String JSON** con porcentajes por partido:
```javascript
const votosPersonalizados = {
  "MORENA": 40.0,
  "PAN": 20.0,
  "PRI": 12.0,
  "PVEM": 8.0,
  "PT": 6.0,
  "MC": 9.0,
  "PRD": 5.0
};

// Convertir a string para enviar al backend
const payload = {
  ...otrosParametros,
  votos_custom: JSON.stringify(votosPersonalizados)
};
```

---

## ✅ Validaciones Frontend

### 1. Suma de porcentajes = 100%
```javascript
function validarVotos(votos) {
  const total = Object.values(votos).reduce((a, b) => a + b, 0);
  if (Math.abs(total - 100) > 0.01) {
    return { valido: false, error: `Total debe ser 100% (actual: ${total}%)` };
  }
  return { valido: true };
}
```

### 2. Porcentajes válidos (0-100)
```javascript
function validarRango(votos) {
  for (const [partido, pct] of Object.entries(votos)) {
    if (pct < 0 || pct > 100) {
      return { valido: false, error: `${partido}: ${pct}% fuera de rango` };
    }
  }
  return { valido: true };
}
```

### 3. Warning si partido < 3% pero tiene votos
```javascript
function advertirUmbral(votos) {
  const warnings = [];
  for (const [partido, pct] of Object.entries(votos)) {
    if (pct > 0 && pct < 3) {
      warnings.push(`⚠️ ${partido} (${pct}%) NO alcanzará umbral del 3% - no recibirá RP`);
    }
  }
  return warnings;
}
```

---

## 🎯 Comportamiento Esperado

### Caso 1: Toggle DESACTIVADO (default)
- Usa votos históricos reales de 2024
- PRD con 2.54% → 0 escaños RP ✓
- Todos los demás partidos con sus porcentajes reales

### Caso 2: Toggle ACTIVADO
- Permite editar cada porcentaje manualmente
- Validación en tiempo real (suma = 100%)
- Warnings si algún partido < 3%
- Al enviar, incluye `votos_custom` en el request

### Caso 3: Cambiar de plan
- Si cambia de "Personalizado" a "Vigente" → ocultar toggle
- Si cambia de "Vigente" a "Personalizado" → mostrar toggle (desactivado)

---

## 📊 Ejemplo de Uso

### Escenario: "¿Qué pasaría si PRD hubiera sacado 5%?"

**Usuario:**
1. Selecciona "Plan Personalizado"
2. Activa toggle "Editar distribución de votos"
3. Cambia PRD de 2.54% → 5.0%
4. Ajusta MORENA para que sume 100%
5. Click "Calcular"

**Resultado:**
- PRD ahora SÍ recibe escaños RP (alcanzó 3% umbral)
- Distribución total de escaños se recalcula

---

## 🔍 Verificación Backend

El backend ya está implementado y probado. Ver script de prueba:
```bash
python tmp_test_votos_custom.py
```

**Resultado comprobado:**
- ✅ PRD con votos reales (2.54%) → 0 RP
- ✅ PRD con votos_custom (5.0%) → 10 RP
- ✅ Todos los cálculos correctos

---

## 💡 Mejoras Futuras (Opcional)

1. **Presets**: Botones con escenarios predefinidos
   - "Empate técnico" (todos ~14%)
   - "Dominio MORENA" (MORENA 50%)
   - "Distribución equitativa"

2. **Sliders**: En lugar de inputs, usar sliders con auto-ajuste
   - Cuando cambias uno, los demás se reajustan proporcionalmente

3. **Visualización**: Gráfico de pastel en tiempo real

4. **Comparación**: Mostrar lado a lado votos reales vs personalizados

---

## 📝 Checklist de Implementación

### Frontend
- [ ] Agregar toggle "Editar distribución de votos" en plan personalizado
- [ ] Mostrar inputs/sliders por partido cuando toggle activado
- [ ] Validar suma = 100% en tiempo real
- [ ] Mostrar warnings si partido < 3%
- [ ] Enviar `votos_custom` como string JSON en request
- [ ] Manejar errores de validación del backend

### Backend
- [x] Endpoint acepta parámetro `votos_custom` ✓
- [x] Parsea JSON y usa esos porcentajes ✓
- [x] Aplica umbral correctamente ✓
- [x] Devuelve resultados con votos personalizados ✓

---

## 🚨 Consideraciones Importantes

1. **Solo para Plan Personalizado**: Esta feature NO debe estar disponible en "Plan Vigente"
2. **Validación estricta**: No permitir enviar si suma ≠ 100%
3. **UX clara**: Usuario debe entender que está usando datos simulados, no reales
4. **Performance**: No recalcular en cada keystroke, usar debounce
5. **Estado**: Recordar valores editados si usuario cambia de pestaña y vuelve

---

## 📞 Contacto

Si tienen dudas sobre la implementación backend o necesitan ajustes en el endpoint:
- Revisar: `main.py` línea 775 (parámetro `votos_custom`)
- Script de prueba: `tmp_test_votos_custom.py`
