# 📊 Estructura de Respuesta del Backend con PM

## ✅ El Backend YA Envía Todo Lo Que Necesitas

### 🎯 Por Cada Partido, Recibes:

```json
{
  "partido": "MORENA",
  "votos": 22905421,
  
  // 🔵 ESCAÑOS DESGLOSADOS:
  "mr": 107,        // ← MR efectivo (ya con PM descontado)
  "pm": 15,         // ← Escaños de Primera Minoría
  "rp": 0,          // ← Escaños de Representación Proporcional
  "total": 122,     // ← TOTAL = mr + pm + rp
  
  "porcentaje_votos": 38.5,
  "porcentaje_escanos": 40.67
}
```

---

## 📋 Estructura Completa de la Respuesta

### Request al Backend:
```javascript
POST /procesar/diputados
Content-Type: application/json

{
  "plan": "personalizado",
  "anio": 2024,
  "sistema": "mr",
  "escanos_totales": 300,
  "pm_seats": 100,     // ← PIDES 100 PM
  "umbral": 0.03
}
```

### Response del Backend:
```json
{
  "plan": "personalizado",
  
  // 📊 ARRAY DE RESULTADOS POR PARTIDO
  "resultados": [
    {
      "partido": "MORENA",
      "votos": 22905421,
      
      // ⚡ AQUÍ ESTÁ EL DESGLOSE QUE NECESITAS:
      "mr": 107,      // MR efectivo (300 - 100 PM = 200 MR para repartir)
      "pm": 15,       // De esos 100 PM solicitados, MORENA ganó 15
      "rp": 0,        // No hay RP en este escenario
      "total": 122,   // 107 + 15 + 0 = 122 total
      
      "porcentaje_votos": 38.5,
      "porcentaje_escanos": 40.67
    },
    {
      "partido": "PAN",
      "votos": 14328493,
      "mr": 22,       // MR efectivo que ganó
      "pm": 35,       // PM que ganó (fue 2do en muchos distritos)
      "rp": 0,
      "total": 57,    // 22 + 35 + 0 = 57
      "porcentaje_votos": 24.1,
      "porcentaje_escanos": 19.0
    }
    // ... más partidos
  ],
  
  // 📈 KPIs GENERALES
  "kpis": {
    "total_votos": 59455073,
    "total_escanos": 300,      // ← Suma de todos los totales
    "gallagher": 4.23,
    "partidos_con_escanos": 6
  },
  
  // 🎨 DATOS PARA GRÁFICAS
  "seat_chart": [
    {
      "party": "MORENA",
      "seats": 122,              // = mr + pm + rp
      "color": "#A0522D",
      "percent": 40.67,
      "votes": 22905421
    }
    // ... más partidos
  ]
}
```

---

## 🎯 Interpretación para el Frontend

### Ejemplo con 300 total y 100 PM solicitados:

| Partido | MR Efectivo | PM (2dos Lugares) | RP | **Total** |
|---------|------------|-------------------|----|-----------| 
| MORENA  | 107        | **15**            | 0  | **122**   |
| PAN     | 22         | **35**            | 0  | **57**    |
| PVEM    | 39         | **9**             | 0  | **48**    |
| PT      | 26         | **5**             | 0  | **31**    |
| PRI     | 6          | **19**            | 0  | **25**    |
| MC      | 0          | **17**            | 0  | **17**    |
| **TOTAL** | **200** | **100**           | **0** | **300** |

### 🔍 Explicación:
- Solicitaste 300 total con 100 PM
- Backend asignó solo **200 MR** (300 - 100)
- Luego calculó qué partidos fueron **2dos en cada distrito**
- Distribuyó los **100 PM** entre esos partidos
- **Total final = 200 (MR) + 100 (PM) + 0 (RP) = 300** ✅

---

## 💡 Cómo Usar en el Frontend

### 1. Tabla Simple:
```jsx
<table>
  <thead>
    <tr>
      <th>Partido</th>
      <th>MR</th>
      <th>PM</th>
      <th>RP</th>
      <th>Total</th>
    </tr>
  </thead>
  <tbody>
    {resultados.map(r => (
      <tr key={r.partido}>
        <td>{r.partido}</td>
        <td>{r.mr}</td>
        <td className="pm-highlight">{r.pm}</td>
        <td>{r.rp}</td>
        <td><strong>{r.total}</strong></td>
      </tr>
    ))}
  </tbody>
  <tfoot>
    <tr>
      <td><strong>TOTAL</strong></td>
      <td>{sumaMR}</td>
      <td>{sumaPM}</td>
      <td>{sumaRP}</td>
      <td><strong>{kpis.total_escanos}</strong></td>
    </tr>
  </tfoot>
</table>
```

### 2. Calcular Totales:
```javascript
const sumaMR = resultados.reduce((sum, r) => sum + r.mr, 0);
const sumaPM = resultados.reduce((sum, r) => sum + r.pm, 0);
const sumaRP = resultados.reduce((sum, r) => sum + r.rp, 0);
const sumaTotal = resultados.reduce((sum, r) => sum + r.total, 0);

console.log(`MR: ${sumaMR}, PM: ${sumaPM}, RP: ${sumaRP}, Total: ${sumaTotal}`);
// Output: MR: 200, PM: 100, RP: 0, Total: 300
```

### 3. Mostrar Desglose:
```jsx
<div className="resumen">
  <div className="card">
    <h3>MR Efectivo</h3>
    <p className="number">{sumaMR}</p>
    <small>Mayoría Relativa directa</small>
  </div>
  
  <div className="card highlight-pm">
    <h3>PM</h3>
    <p className="number">{sumaPM}</p>
    <small>Primera Minoría (segundos lugares)</small>
  </div>
  
  <div className="card">
    <h3>RP</h3>
    <p className="number">{sumaRP}</p>
    <small>Representación Proporcional</small>
  </div>
  
  <div className="card total">
    <h3>Total</h3>
    <p className="number">{kpis.total_escanos}</p>
    <small>Escaños totales</small>
  </div>
</div>
```

---

## ✅ Resumen: Lo Que Recibes del Backend

```typescript
interface ResultadoPartido {
  partido: string;
  votos: number;
  
  // 🎯 LOS 3 TIPOS DE ESCAÑOS:
  mr: number;     // Mayoría Relativa efectiva
  pm: number;     // Primera Minoría (segundos lugares)
  rp: number;     // Representación Proporcional
  
  total: number;  // Suma de los 3 anteriores
  
  porcentaje_votos: number;
  porcentaje_escanos: number;
}
```

### 📊 Garantías:
- ✅ `total = mr + pm + rp` (siempre)
- ✅ `sum(todos.mr) = escanos_totales - pm_seats - rp_seats`
- ✅ `sum(todos.pm) = pm_seats` (lo que pediste)
- ✅ `sum(todos.total) = escanos_totales` (300 en el ejemplo)

---

## 🚀 El Backend Está Listo

No necesitas cambiar nada más en el backend. Ya envía:
1. ✅ Desglose por tipo (mr, pm, rp)
2. ✅ Total por partido
3. ✅ Porcentajes
4. ✅ KPIs generales
5. ✅ Datos para gráficas

**Solo necesitas consumir los campos `mr`, `pm`, `rp` y `total` en tu frontend.**
