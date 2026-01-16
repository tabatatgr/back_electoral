# 📊 GUÍA COMPLETA: SLIDERS DE MR (MAYORÍA RELATIVA) PARA EL FRONTEND

## 🎯 ¿Qué hace el sistema de sliders de MR?

El usuario puede **modificar manualmente cuántos distritos gana cada partido** (MR - Mayoría Relativa) en lugar de usar los resultados históricos del siglado.

**Ejemplo de uso:**
> "¿Qué pasaría si MORENA ganara 180 distritos en vez de 160?"
> "Quiero ver el escenario donde PAN gane 50 distritos y PRI solo 5"

Cuando el usuario ajusta estos valores, el backend:
1. ✅ **Usa los MR manuales** que le envió el frontend
2. ✅ **Recalcula automáticamente los VOTOS** para que sean coherentes con esos MR
3. ✅ **Redistribuye geográficamente** (por estado) los distritos ganados
4. ✅ **Recalcula RP** (Representación Proporcional) con los nuevos porcentajes
5. ✅ **Aplica topes** y reglas constitucionales
6. ✅ **Devuelve resultados completos** con todos los cálculos actualizados

---

## 📡 CÓMO ENVIAR LOS DATOS DESDE EL FRONTEND

### **OPCIÓN 1: MR Manuales Totales (Más Simple) ⭐ RECOMENDADA**

Envía un JSON con el total de distritos MR que cada partido debe ganar a nivel nacional.

```javascript
// Ejemplo: Usuario mueve sliders
const mrSliders = {
  "MORENA": 180,   // Usuario quiere que MORENA gane 180 distritos
  "PAN": 50,       // PAN gana 50 distritos
  "PRI": 30,       // PRI gana 30 distritos
  "PVEM": 25,      // etc.
  "PT": 10,
  "MC": 5
  // Total debe ≤ 300 (para Diputados)
};

// Hacer el request POST al backend
const response = await fetch('/procesar/diputados', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    anio: 2024,
    plan: "vigente",
    mr_distritos_manuales: JSON.stringify(mrSliders),  // ← AQUÍ van los sliders
    aplicar_topes: true,
    sobrerrepresentacion: 8,
    usar_coaliciones: true
  })
});

const resultado = await response.json();
// ✅ resultado.resultados tiene los nuevos MR, RP y totales
// ✅ resultado.meta.mr_por_estado tiene la distribución geográfica
```

**Formato del parámetro:**
```
mr_distritos_manuales: JSON string
{
  "MORENA": 180,
  "PAN": 50,
  "PRI": 30,
  "PVEM": 25,
  "PT": 10,
  "MC": 5
}
```

**Validaciones automáticas del backend:**
- ✅ La suma total de MR no puede exceder 300 (Diputados) o 96 (Senado MR+PM)
- ✅ Si la suma es menor a 300, el backend NO la ajusta (quedan distritos "sin asignar")
- ✅ Se calculan automáticamente los porcentajes de voto que justificarían esos MR

---

### **OPCIÓN 2: MR por Estado (Avanzado)**

Si quieres control granular estado por estado:

```javascript
const mrPorEstado = {
  "15": {  // Estado de México (ID 15)
    "MORENA": 22,
    "PAN": 8,
    "PVEM": 6,
    "PT": 4
    // Total debe = distritos del estado (40 para Edomex)
  },
  "9": {  // CDMX (ID 9)
    "MORENA": 14,
    "PAN": 5,
    "PT": 3
    // Total debe = 22 (distritos CDMX)
  }
  // ... resto de estados
};

const response = await fetch('/procesar/diputados', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    anio: 2024,
    plan: "vigente",
    mr_distritos_por_estado: JSON.stringify(mrPorEstado),  // ← MR estado por estado
    aplicar_topes: true,
    sobrerrepresentacion: 8
  })
});
```

**Validaciones automáticas:**
- ✅ Los IDs de estado deben estar en el rango 1-32
- ✅ La suma de distritos por estado debe coincidir con la asignación Hare del estado
- ✅ Se convierte automáticamente a `mr_distritos_manuales` (suma total por partido)

---

## 🔄 CÓMO EL BACKEND RECALCULA TODO AUTOMÁTICAMENTE

### **Paso 1: Recibe los MR manuales**
```python
# Backend recibe:
mr_ganados_geograficos = {
  "MORENA": 180,
  "PAN": 50,
  "PRI": 30,
  ...
}
```

### **Paso 2: Calcula porcentajes de voto equivalentes**
El backend usa **eficiencias geográficas REALES** de cada partido (históricas del año seleccionado) para calcular qué % de voto nacional necesitaría cada partido para ganar esos distritos.

```python
# Ejemplo simplificado:
# Si MORENA históricamente gana 1.5 distritos por cada 1% de votos (eficiencia)
# Y queremos que gane 180 distritos:
# Votos necesarios = 180 / 1.5 = 120% ... ajustar proporcionalmente

# El backend hace esto automáticamente en main.py líneas 2963-3095
```

### **Paso 3: Redistribuye votos geográficamente**
Aplica los nuevos porcentajes a cada estado, manteniendo las proporciones relativas históricas.

### **Paso 4: Recalcula MR distrito por distrito**
Usa el siglado (candidatos históricos) pero con los nuevos porcentajes de voto para determinar quién gana cada distrito.

### **Paso 5: Calcula RP con los nuevos votos**
La Representación Proporcional se calcula usando los **nuevos porcentajes de voto** ajustados.

### **Paso 6: Aplica topes constitucionales**
- Sobrerrepresentación máxima (8% o custom)
- Tope de 300 escaños por partido
- etc.

---

## 📤 QUÉ DEVUELVE EL BACKEND

```javascript
{
  "plan": "vigente",
  "resultados": [
    {
      "partido": "MORENA",
      "mr": 180,          // ← Los MR que pediste
      "rp": 67,           // ← Recalculado automáticamente
      "total": 247,       // ← Total ajustado con topes
      "porcentaje_votos": 42.5,    // ← % de voto recalculado
      "porcentaje_escanos": 49.4,  // ← % de escaños final
      "color": "#8B2231"
    },
    // ... resto de partidos
  ],
  "kpis": {
    "total_votos": 57155258,
    "total_escanos": 500,
    "gallagher": 9.2,          // ← Índice de desproporcionalidad recalculado
    "mae_votos_vs_escanos": 0.64
  },
  "meta": {
    "mr_por_estado": {          // ← DISTRIBUCIÓN GEOGRÁFICA RECALCULADA
      "AGUASCALIENTES": {
        "MORENA": 1,
        "PAN": 2
      },
      "CHIAPAS": {
        "MORENA": 9,
        "PVEM": 3,
        "PT": 1
      },
      // ... 32 estados
    },
    "distritos_por_estado": {
      "AGUASCALIENTES": 3,
      "CHIAPAS": 13,
      // ... etc
    }
  },
  "mayorias": {
    "mayoria_simple": {
      "alcanzada": true,
      "partido": "MORENA",
      "escanos": 247,
      "umbral": 251
    },
    "mayoria_calificada": {
      "alcanzada": false,
      "umbral": 334
    }
  }
}
```

---

## 🎨 EJEMPLO COMPLETO: COMPONENTE REACT CON SLIDERS

```jsx
import React, { useState } from 'react';

function SlidersMR() {
  const [mrValues, setMrValues] = useState({
    MORENA: 160,
    PAN: 33,
    PRI: 9,
    PVEM: 58,
    PT: 38,
    MC: 1,
    PRD: 1
  });

  const [loading, setLoading] = useState(false);
  const [resultado, setResultado] = useState(null);

  const totalMR = Object.values(mrValues).reduce((a, b) => a + b, 0);
  const maxMR = 300; // Para Diputados

  const handleSliderChange = (partido, nuevoValor) => {
    setMrValues({
      ...mrValues,
      [partido]: parseInt(nuevoValor)
    });
  };

  const simularEscenario = async () => {
    if (totalMR > maxMR) {
      alert(`La suma de MR (${totalMR}) excede el máximo (${maxMR})`);
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/procesar/diputados', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          anio: 2024,
          plan: "vigente",
          mr_distritos_manuales: JSON.stringify(mrValues),
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
      
      <div className="total-indicator">
        <span>Total MR: {totalMR} / {maxMR}</span>
        {totalMR > maxMR && (
          <span className="error">⚠️ Excede el máximo!</span>
        )}
      </div>

      {Object.entries(mrValues).map(([partido, valor]) => (
        <div key={partido} className="slider-row">
          <label>{partido}</label>
          <input
            type="range"
            min="0"
            max="200"
            value={valor}
            onChange={(e) => handleSliderChange(partido, e.target.value)}
          />
          <input
            type="number"
            min="0"
            max="300"
            value={valor}
            onChange={(e) => handleSliderChange(partido, e.target.value)}
          />
        </div>
      ))}

      <button 
        onClick={simularEscenario}
        disabled={loading || totalMR > maxMR}
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
                </tr>
              ))}
            </tbody>
          </table>

          <div className="kpis">
            <p>Índice Gallagher: {resultado.kpis.gallagher.toFixed(2)}</p>
            <p>MAE: {resultado.kpis.mae_votos_vs_escanos.toFixed(3)}</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default SlidersMR;
```

---

## ⚠️ VALIDACIONES IMPORTANTES

### **En el Frontend:**
```javascript
// 1. Validar suma total
const totalMR = Object.values(mrSliders).reduce((a, b) => a + b, 0);
if (totalMR > 300) {  // Para Diputados
  alert('La suma de MR no puede exceder 300');
  return;
}

// 2. Validar valores positivos
if (Object.values(mrSliders).some(v => v < 0)) {
  alert('Los valores deben ser positivos');
  return;
}

// 3. Validar que sean números enteros
if (Object.values(mrSliders).some(v => !Number.isInteger(v))) {
  alert('Los valores deben ser números enteros');
  return;
}
```

### **En el Backend (automático):**
```python
# main.py líneas 2950-2957
total_mr_manuales = sum(mr_ganados_geograficos.values())
if total_mr_manuales > mr_seats_final:
    raise HTTPException(
        status_code=400,
        detail=f"La suma de MR manuales ({total_mr_manuales}) excede el total de escaños MR ({mr_seats_final})"
    )
```

---

## 🔍 DEBUGGING: CÓMO VERIFICAR QUE FUNCIONA

### **1. Ver logs del backend:**
```python
[DEBUG] Usando MR manuales: {"MORENA": 180, "PAN": 50, ...}
[DEBUG] MR manuales validados: {...} (total=300/300)
[DEBUG] Calculando eficiencias históricas para 2024...
[DEBUG] Eficiencias calculadas: {'MORENA': 1.42, 'PAN': 1.18, ...}
[DEBUG] MR ganados con redistritación geográfica: {"MORENA": 180, ...}
[INFO] ✅ MR se calcularán con REDISTRITACIÓN GEOGRÁFICA
```

### **2. Verificar respuesta del frontend:**
```javascript
console.log('MR enviados:', mrSliders);
console.log('MR recibidos:', resultado.resultados.map(r => ({
  partido: r.partido,
  mr: r.mr
})));

// Deben coincidir EXACTAMENTE (o con ajustes por topes)
```

### **3. Verificar coherencia geográfica:**
```javascript
// La suma de mr_por_estado debe = MR total de cada partido
const sumaEstados = {};
Object.values(resultado.meta.mr_por_estado).forEach(estado => {
  Object.entries(estado).forEach(([partido, mr]) => {
    sumaEstados[partido] = (sumaEstados[partido] || 0) + mr;
  });
});

console.log('Suma por estado:', sumaEstados);
console.log('MR totales:', resultado.resultados.map(r => ({
  partido: r.partido,
  mr: r.mr
})));
// Deben coincidir
```

---

## 📝 NOTAS TÉCNICAS

### **¿Por qué se recalculan los votos?**
Para mantener coherencia con el sistema electoral mexicano:
- Los **MR** se ganan por votos en distritos
- Los **RP** se asignan proporcionalmente a % de votos
- Si cambias MR manualmente, el sistema necesita calcular qué % de votos justificarían esos resultados

### **¿Por qué usar eficiencias reales?**
Cada partido tiene diferente capacidad de convertir votos en distritos ganados:
- **MORENA**: Alta eficiencia geográfica (concentra votos en distritos ganables)
- **PAN**: Eficiencia media (votos más dispersos)
- **MC**: Baja eficiencia (muchos votos pero pocos distritos)

El sistema usa datos históricos del año seleccionado para hacer cálculos realistas.

### **¿Qué pasa si no envío mr_distritos_manuales?**
El backend usa el siglado histórico real (quién ganó cada distrito en las elecciones del año seleccionado).

---

## 🎯 CASOS DE USO TÍPICOS

### **Caso 1: "¿Qué pasa si MORENA gana 20 distritos más?"**
```javascript
const mrActuales = { MORENA: 160, PAN: 33, ... };
const mrNuevos = { ...mrActuales, MORENA: 180 };

// Enviar mrNuevos al backend
// ✅ El backend recalcula todo automáticamente
```

### **Caso 2: "Escenario de empate técnico"**
```javascript
const mrEmpate = {
  MORENA: 150,
  PAN: 75,
  PRI: 75
  // Total = 300
};
```

### **Caso 3: "Mayoría calificada para reforma constitucional"**
```javascript
const mrMayoriaCalificada = {
  MORENA: 240,  // Necesita 334/500 total para 2/3
  // ... el resto distribuido
};
```

---

## ✅ CHECKLIST PARA IMPLEMENTACIÓN

- [ ] Crear componente de sliders con rangos 0-300
- [ ] Mostrar total actual y máximo permitido
- [ ] Validar suma ≤ 300 antes de enviar
- [ ] Enviar `mr_distritos_manuales` como JSON string
- [ ] Incluir `aplicar_topes: true` para respetar límites constitucionales
- [ ] Mostrar resultados: MR, RP, Total por partido
- [ ] Mostrar KPIs recalculados (Gallagher, MAE)
- [ ] Mostrar tabla geográfica con `meta.mr_por_estado`
- [ ] Agregar loading state durante cálculo
- [ ] Manejar errores del backend (400 si excede límites)

---

## 🚀 ENDPOINT COMPLETO

```
POST /procesar/diputados
Content-Type: application/json

{
  "anio": 2024,
  "plan": "vigente",
  "mr_distritos_manuales": "{\"MORENA\":180,\"PAN\":50,\"PRI\":30,\"PVEM\":25,\"PT\":10,\"MC\":5}",
  "aplicar_topes": true,
  "sobrerrepresentacion": 8,
  "usar_coaliciones": true,
  "max_seats_per_party": 300
}
```

**Respuesta:**
- `200 OK`: Cálculo exitoso, devuelve resultados completos
- `400 Bad Request`: Suma de MR excede límite o JSON inválido
- `500 Internal Server Error`: Error en el procesamiento

---

## 📚 ARCHIVOS RELEVANTES

- **Frontend → Backend**: `main.py` líneas 2880-3140 (procesamiento de `mr_distritos_manuales`)
- **Cálculo de eficiencias**: `engine/calcular_eficiencia_real.py`
- **Redistritación geográfica**: `main.py` líneas 2963-3095
- **Procesamiento final**: `engine/procesar_diputados_v2.py` líneas 1263-1275
- **Tests de ejemplo**: `tests/test_escenario_personalizado.py` líneas 168-245

---

**¡Listo!** Con esta guía el frontend puede implementar sliders para que el usuario ajuste MR y el backend recalcule todo automáticamente. 🎉
