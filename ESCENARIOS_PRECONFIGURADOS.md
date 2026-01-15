# 🎯 Escenarios Preconfigurados con Redistritación Geográfica

## ⚡ IMPORTANTE: Redistritación Geográfica por Defecto

**TODOS los escenarios ahora usan redistritación geográfica automática por defecto.**

La redistritación geográfica:
- ✅ Reparte distritos MR por población (método Hare)
- ✅ Calcula eficiencias históricas reales por partido
- ✅ Produce resultados más realistas que la redistritación proporcional simple
- ✅ Funciona con `votos_redistribuidos` y `mr_distritos_manuales`

## Nuevos Escenarios Disponibles

Se agregaron 3 nuevos escenarios preconfigurados que aprovechan la redistritación geográfica con eficiencias históricas reales del año 2024.

### 📋 Lista de Escenarios

| Plan | Descripción | MR | RP | Total | Topes | Redistritación Geográfica |
|------|-------------|----|----|-------|-------|---------------------------|
| **vigente** | Sistema actual | 300* | 200 | 500 | ✅ 300 max | ✅ **SÍ** (por defecto) |
| **plan_a** | Solo RP | 0 | 300 | 300 | ❌ No | N/A (sin MR) |
| **plan_c** | Solo MR | 300 | 0 | 300 | ❌ No | ✅ **SÍ** (por defecto) |
| **300_100_con_topes** | Mixto con topes | 300 | 100 | 400 | ✅ 300 max | ✅ **SÍ** (por defecto) |
| **300_100_sin_topes** | Mixto sin topes | 300 | 100 | 400 | ❌ No | ✅ **SÍ** (por defecto) |
| **200_200_sin_topes** | Equilibrado sin topes | 200 | 200 | 400 | ❌ No | ✅ **SÍ** (por defecto) |

*En vigente, los MR se calculan del siglado real

## 🆕 Nuevos Escenarios Detallados

### 1. 300_100_con_topes

**Configuración:**
- 300 distritos de Mayoría Relativa (MR)
- 100 escaños de Representación Proporcional (RP)
- **Total: 400 escaños**
- Tope constitucional: máximo 300 escaños por partido
- Umbral: 3%
- Redistritación geográfica: **ACTIVADA**

**Uso en frontend:**
```javascript
const request = {
  plan: "300_100_con_topes",
  anio: 2024,
  votos_redistribuidos: {
    "MORENA": 50.0,
    "PAN": 20.0,
    "PRI": 15.0,
    "PVEM": 8.0,
    "MC": 7.0
  }
};
```

**Ejemplo de resultados (MORENA 50%):**
- MR: ~76 (con eficiencia real 0.604)
- RP: ~50 (distribución proporcional)
- Total: ~126 escaños
- Aplicación de tope: Si el total excede 300, se recorta

### 2. 300_100_sin_topes

**Configuración:**
- 300 distritos MR
- 100 escaños RP
- **Total: 400 escaños**
- **Sin tope** de sobrerrepresentación
- Umbral: 3%
- Redistritación geográfica: **ACTIVADA**

**Uso en frontend:**
```javascript
const request = {
  plan: "300_100_sin_topes",
  anio: 2024,
  votos_redistribuidos: {
    "MORENA": 50.0,
    "PAN": 20.0,
    "PRI": 15.0,
    "PVEM": 8.0,
    "MC": 7.0
  }
};
```

**Ejemplo de resultados (MORENA 50%):**
- MR: ~76 (con eficiencia real 0.604)
- RP: ~50 (distribución proporcional)
- Total: ~126 escaños (sin restricción de tope)

**Diferencia vs con_topes:**
- Permite sobrerrepresentación sin límite
- Partidos pequeños eficientes pueden ganar más de lo proporcional

### 3. 200_200_sin_topes

**Configuración:**
- 200 distritos MR
- 200 escaños RP
- **Total: 400 escaños**
- **Sin tope** de sobrerrepresentación
- Umbral: 3%
- Redistritación geográfica: **ACTIVADA**

**Uso en frontend:**
```javascript
const request = {
  plan: "200_200_sin_topes",
  anio: 2024,
  votos_redistribuidos: {
    "MORENA": 50.0,
    "PAN": 20.0,
    "PRI": 15.0,
    "PVEM": 8.0,
    "MC": 7.0
  }
};
```

**Ejemplo de resultados (MORENA 50%):**
- MR: ~43 (con eficiencia real 0.604)
- RP: ~100 (distribución proporcional)
- Total: ~143 escaños

**Características especiales:**
- Sistema más equilibrado (50% MR, 50% RP)
- Menor peso de la geografía vs sistema 300-100
- RP compensa mejor las ineficiencias geográficas

## 🎯 Ventajas de los Escenarios Preconfigurados

### ✅ Simplicidad
```javascript
// ❌ ANTES: Usuario tenía que configurar TODO
{
  plan: "personalizado",
  mr_seats: 300,
  rp_seats: 100,
  max_seats: 400,
  aplicar_topes: true,
  max_seats_per_party: 300,
  umbral: 0.03,
  redistritacion_geografica: true,
  sistema: "mixto",
  quota_method: "hare",
  // ... más parámetros
}

// ✅ AHORA: Solo selecciona el escenario
{
  plan: "300_100_con_topes",
  anio: 2024,
  votos_redistribuidos: { ... }
}
```

### ✅ Redistritación Geográfica Automática

Los nuevos escenarios usan **eficiencias históricas reales** del año 2024:

| Partido | Eficiencia | Significado |
|---------|-----------|-------------|
| MORENA | 0.604 | ❌ Desperdicia votos (gana solo 60% de lo proporcional) |
| PAN | 1.172 | ✅ +17% eficiencia geográfica |
| PRI | 1.732 | ✅ +73% eficiencia geográfica |
| PRD | 4.919 | 🚀 Super eficiente (gana 5x lo proporcional) |
| PVEM | 1.469 | ✅ +47% eficiencia geográfica |
| PT | 1.461 | ✅ +46% eficiencia geográfica |
| MC | 0.000 | 💀 No gana distritos (concentrado en Jalisco) |

### ✅ Configuración Completa

Cada escenario incluye automáticamente:
- Número exacto de MR y RP
- Aplicación o no de topes constitucionales
- Umbral electoral correcto
- Método de reparto (Hare)
- Redistritación geográfica con eficiencias reales
- Sistema electoral (mixto)

## 🔄 Comparación de Resultados

**Escenario de prueba: MORENA 50%, PAN 20%, PRI 15%, PVEM 8%, MC 7%**

### Escenario: 300_100_con_topes

| Partido | % Votos | MR Geográfico | RP Proporcional | Total | Con Tope |
|---------|---------|---------------|-----------------|-------|----------|
| MORENA | 50.0% | 76 | 50 | 126 | 126 |
| PAN | 20.0% | 51 | 20 | 71 | 71 |
| PRI | 15.0% | 58 | 15 | 73 | 73 |
| PVEM | 8.0% | 18 | 8 | 26 | 26 |
| MC | 7.0% | 0 | 7 | 7 | 7 |

**Observaciones:**
- MORENA con 50% solo obtiene 126/400 (31.5%) por ineficiencia geográfica
- PRI obtiene más escaños que su % de votos (eficiencia alta)
- MC pierde todos los MR por concentración en Jalisco

### Escenario: 200_200_sin_topes

| Partido | % Votos | MR Geográfico | RP Proporcional | Total |
|---------|---------|---------------|-----------------|-------|
| MORENA | 50.0% | 43 | 100 | 143 |
| PAN | 20.0% | 32 | 40 | 72 |
| PRI | 15.0% | 37 | 30 | 67 |
| PVEM | 8.0% | 8 | 16 | 24 |
| MC | 7.0% | 0 | 14 | 14 |

**Observaciones:**
- Sistema más proporcional (200 RP compensan ineficiencia geográfica)
- MORENA obtiene 143/400 (35.75%) más cercano a su 50%
- MC recupera escaños vía RP

## 💻 Implementación en el Frontend

### Componente de Selección de Escenario

```jsx
import { useState } from 'react';

const EscenarioSelector = () => {
  const [escenario, setEscenario] = useState('300_100_con_topes');
  
  const escenarios = [
    { 
      id: 'vigente', 
      nombre: 'Vigente (300 MR + 200 RP)',
      descripcion: 'Sistema actual con topes',
      redistGeo: false
    },
    { 
      id: 'plan_a', 
      nombre: 'Plan A (300 RP puro)',
      descripcion: 'Solo representación proporcional',
      redistGeo: false
    },
    { 
      id: 'plan_c', 
      nombre: 'Plan C (300 MR puro)',
      descripcion: 'Solo mayoría relativa',
      redistGeo: false
    },
    { 
      id: '300_100_con_topes', 
      nombre: '300-100 CON TOPES 🌎',
      descripcion: 'Mixto con topes + redistritación geográfica',
      redistGeo: true,
      badge: 'NUEVO'
    },
    { 
      id: '300_100_sin_topes', 
      nombre: '300-100 SIN TOPES 🌎',
      descripcion: 'Mixto sin topes + redistritación geográfica',
      redistGeo: true,
      badge: 'NUEVO'
    },
    { 
      id: '200_200_sin_topes', 
      nombre: '200-200 EQUILIBRADO 🌎',
      descripcion: 'Sistema equilibrado + redistritación geográfica',
      redistGeo: true,
      badge: 'NUEVO'
    }
  ];
  
  return (
    <div className="escenario-selector">
      <label>Seleccionar Escenario Electoral:</label>
      <select 
        value={escenario} 
        onChange={(e) => setEscenario(e.target.value)}
      >
        {escenarios.map(esc => (
          <option key={esc.id} value={esc.id}>
            {esc.nombre} {esc.badge && `[${esc.badge}]`}
          </option>
        ))}
      </select>
      
      {escenarios.find(e => e.id === escenario)?.redistGeo && (
        <div className="geo-badge">
          🌎 Redistritación geográfica con eficiencias históricas
        </div>
      )}
      
      <p className="descripcion">
        {escenarios.find(e => e.id === escenario)?.descripcion}
      </p>
    </div>
  );
};
```

### Request al Backend

```javascript
const procesarEscenario = async (escenario, votos) => {
  const response = await fetch('/procesar/diputados', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      plan: escenario,  // 'vigente', '300_100_con_topes', etc.
      anio: 2024,
      votos_redistribuidos: votos
    })
  });
  
  return await response.json();
};

// Uso
const votos = {
  "MORENA": 50.0,
  "PAN": 20.0,
  "PRI": 15.0,
  "PVEM": 8.0,
  "MC": 7.0
};

const resultado = await procesarEscenario('300_100_con_topes', votos);
console.log(resultado.asignaciones);
```

## 📊 Response del Backend

```json
{
  "asignaciones": {
    "MORENA": {
      "MR": 76,
      "RP": 50,
      "Total": 126,
      "Porcentaje_Votos": 50.0,
      "Porcentaje_Escanos": 31.5
    },
    "PAN": {
      "MR": 51,
      "RP": 20,
      "Total": 71,
      "Porcentaje_Votos": 20.0,
      "Porcentaje_Escanos": 17.75
    },
    // ... otros partidos
  },
  "total_escanos": 400,
  "mr_total": 300,
  "rp_total": 100,
  "redistritacion_geografica": true,
  "eficiencias_aplicadas": {
    "MORENA": 0.604,
    "PAN": 1.172,
    // ...
  }
}
```

## 🎓 Casos de Uso

### Caso 1: Análisis de Mayoría Calificada
```javascript
// ¿Qué % necesita MORENA para 267 escaños (2/3)?
// Probar con diferentes escenarios

const escenarios = ['300_100_con_topes', '300_100_sin_topes', '200_200_sin_topes'];
const objetivo = 267;

for (const escenario of escenarios) {
  // Buscar % que da ~267 escaños
  const resultado = await procesarEscenario(escenario, {
    "MORENA": 65.0,  // Ajustar este valor
    "PAN": 15.0,
    "PRI": 10.0,
    "PVEM": 5.0,
    "MC": 5.0
  });
  
  console.log(`${escenario}: MORENA obtiene ${resultado.asignaciones.MORENA.Total} escaños`);
}
```

### Caso 2: Comparar Efecto de Topes
```javascript
// Comparar mismo escenario con y sin topes
const conTopes = await procesarEscenario('300_100_con_topes', votos);
const sinTopes = await procesarEscenario('300_100_sin_topes', votos);

console.log('Con topes:', conTopes.asignaciones.MORENA.Total);
console.log('Sin topes:', sinTopes.asignaciones.MORENA.Total);
```

### Caso 3: Analizar Impacto de MR vs RP
```javascript
// Comparar sistema 300-100 vs 200-200
const mas_mr = await procesarEscenario('300_100_sin_topes', votos);
const equilibrado = await procesarEscenario('200_200_sin_topes', votos);

// Más MR favorece a partidos eficientes geográficamente
// Más RP favorece representación proporcional directa
```

## ✅ Checklist de Integración

- [ ] Agregar opciones de escenarios en UI
- [ ] Mostrar badge "🌎 Redistritación Geográfica" para nuevos escenarios
- [ ] Tooltip explicando qué es redistritación geográfica
- [ ] Tabla comparativa de resultados
- [ ] Gráfico de eficiencias por partido
- [ ] Indicador de topes aplicados
- [ ] Export de resultados en CSV/JSON

## 🎛️ Control Manual de MR (Nuevo)

Todos los escenarios con redistritación geográfica ahora soportan el parámetro **`mr_distritos_manuales`** que permite especificar manualmente los distritos MR ganados por cada partido, sobrescribiendo el cálculo automático.

**Ejemplo:**
```javascript
const request = {
  plan: "300_100_sin_topes",
  anio: 2024,
  redistritacion_geografica: true,
  mr_distritos_manuales: JSON.stringify({
    "MORENA": 200,  // En lugar de ~150 calculados
    "PAN": 50,
    "PRI": 30,
    "PVEM": 10,
    "PT": 5,
    "MC": 5
  })
};
```

**Documentación completa:** Ver [MR_DISTRITOS_MANUALES.md](MR_DISTRITOS_MANUALES.md)

## 🚀 Próximos Pasos

1. **Testing:** Probar los 3 escenarios con diferentes distribuciones de votos
2. **UI:** Crear selector visual de escenarios
3. **Documentación:** Agregar tooltips explicativos
4. **Visualización:** Gráficos comparativos de resultados
5. **Export:** Permitir descargar resultados

---

**Última actualización:** 15 de enero de 2026  
**Versión:** 1.1  
**Escenarios disponibles:** 6 (3 clásicos + 3 nuevos con redistritación geográfica)
**Nueva funcionalidad:** Control manual de MR con `mr_distritos_manuales`
