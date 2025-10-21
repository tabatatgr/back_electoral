# 🎯 RESUMEN PARA EL FRONTEND - IMPLEMENTACIÓN PM

## ✅ EL BACKEND YA ESTÁ LISTO

### 📨 Request que Haces:
```
POST /procesar/diputados?anio=2024&plan=personalizado&sistema=mr&escanos_totales=300&pm_seats=100&umbral=0.03
```

### 📥 Response que Recibes:
```json
{
  "resultados": [
    {
      "partido": "MORENA",
      "mr": 107,        ← Escaños MR efectivos
      "pm": 15,         ← Escaños PM (2dos lugares)
      "rp": 0,          ← Escaños RP
      "total": 122      ← TOTAL = mr + pm + rp
    }
  ]
}
```

---

## 🎨 Lo Que Tienes Que Hacer en el Frontend:

### 1. Añadir Input PM
```html
<input type="number" name="pm_seats" placeholder="Ej: 100" />
```

### 2. Incluir en Request
```javascript
const params = new URLSearchParams({
  anio: 2024,
  plan: 'personalizado',
  sistema: 'mr',
  escanos_totales: 300,
  pm_seats: 100,    // ← Añadir este parámetro
  umbral: 0.03
});

const response = await fetch(`/procesar/diputados?${params}`);
const data = await response.json();
```

### 3. Mostrar en Tabla
```jsx
<table>
  <tr>
    <th>Partido</th>
    <th>MR</th>
    <th>PM</th>     ← Nueva columna
    <th>RP</th>
    <th>Total</th>
  </tr>
  {data.resultados.map(r => (
    <tr>
      <td>{r.partido}</td>
      <td>{r.mr}</td>
      <td>{r.pm}</td>      ← Mostrar PM
      <td>{r.rp}</td>
      <td>{r.total}</td>
    </tr>
  ))}
</table>
```

---

## 📊 Ejemplo Real:

### Request:
```
pm_seats = 100
escanos_totales = 300
```

### Response:
| Partido | MR  | PM  | RP | Total |
|---------|-----|-----|----|-------|
| MORENA  | 107 | 15  | 0  | 122   |
| PAN     | 22  | 35  | 0  | 57    |
| PVEM    | 39  | 9   | 0  | 48    |
| PT      | 26  | 5   | 0  | 31    |
| PRI     | 6   | 19  | 0  | 25    |
| MC      | 0   | 17  | 0  | 17    |
| **TOTAL** | **200** | **100** | **0** | **300** |

---

## ✅ Checklist:

- [ ] Añadir `<input name="pm_seats">` en formulario
- [ ] Incluir `pm_seats` en URLSearchParams del request
- [ ] Añadir columna "PM" en tabla de resultados
- [ ] Acceder a `resultado.pm` para cada partido
- [ ] Mostrar totales: `sum(pm)` debe ser igual a `pm_seats` solicitado

---

## 🚀 Listo!

El backend ya envía TODO lo que necesitas:
- ✅ `mr`: MR efectivo (ya con PM descontado)
- ✅ `pm`: Escaños de primera minoría
- ✅ `rp`: Escaños de representación proporcional  
- ✅ `total`: Suma de los 3 anteriores

**Solo necesitas leer esos 4 campos y mostrarlos en tu UI.**
