# 🎯 RESUMEN EJECUTIVO: SLIDERS DE MR

## ✅ SÍ, EL BACKEND YA HACE TODO ESTO

El backend **YA está completamente implementado** para soportar sliders de MR (distritos ganados por partido). Cuando el usuario mueve los sliders en el frontend:

### 🔄 **Lo que el backend hace automáticamente:**

1. ✅ **Recibe los MR manuales** del frontend
2. ✅ **Valida** que no excedan el límite (300 para Diputados, 96 para Senado)
3. ✅ **Calcula porcentajes de voto equivalentes** usando eficiencias geográficas reales del año
4. ✅ **Redistribuye votos estado por estado** manteniendo proporciones realistas
5. ✅ **Recalcula RP** (Representación Proporcional) con los nuevos porcentajes
6. ✅ **Aplica topes constitucionales** (sobrerrepresentación 8%, max 300 escaños)
7. ✅ **Genera distribución geográfica** (mr_por_estado) coherente
8. ✅ **Calcula mayorías** (simple y calificada)
9. ✅ **Devuelve KPIs actualizados** (Gallagher, MAE, etc.)

---

## 📡 LO QUE EL FRONTEND DEBE ENVIAR

### **Formato del request:**

```javascript
POST /procesar/diputados
Content-Type: application/json

{
  "anio": 2024,
  "plan": "vigente",
  "mr_distritos_manuales": "{\"MORENA\":180,\"PAN\":50,\"PRI\":30,...}",  // ← AQUÍ
  "aplicar_topes": true,
  "sobrerrepresentacion": 8,
  "usar_coaliciones": true
}
```

### **Validaciones antes de enviar:**

```javascript
// 1. Suma total
const totalMR = Object.values(mrSliders).reduce((a, b) => a + b, 0);
if (totalMR > 300) {
  alert('La suma no puede exceder 300');
  return;
}

// 2. Valores positivos enteros
if (Object.values(mrSliders).some(v => v < 0 || !Number.isInteger(v))) {
  alert('Valores deben ser enteros positivos');
  return;
}

// 3. Enviar
const response = await fetch('/procesar/diputados', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    anio: 2024,
    plan: "vigente",
    mr_distritos_manuales: JSON.stringify(mrSliders),
    aplicar_topes: true,
    sobrerrepresentacion: 8
  })
});
```

---

## 📊 LO QUE EL BACKEND DEVUELVE

```javascript
{
  "resultados": [
    {
      "partido": "MORENA",
      "mr": 180,              // ← El MR que configuraste
      "rp": 67,               // ← Recalculado automáticamente
      "total": 247,           // ← Con topes aplicados
      "porcentaje_votos": 42.5,    // ← % de voto calculado
      "porcentaje_escanos": 49.4
    },
    // ... resto de partidos
  ],
  "meta": {
    "mr_por_estado": {       // ← Distribución geográfica
      "AGUASCALIENTES": { "MORENA": 1, "PAN": 2 },
      "CHIAPAS": { "MORENA": 9, "PVEM": 3, "PT": 1 },
      // ... 32 estados
    }
  },
  "kpis": {
    "gallagher": 9.2,
    "mae_votos_vs_escanos": 0.64
  },
  "mayorias": {
    "mayoria_simple": {
      "alcanzada": true,
      "partido": "MORENA",
      "escanos": 247
    }
  }
}
```

---

## 🧪 CÓMO PROBAR

### **Opción 1: Con el script de prueba**

```bash
# 1. Asegúrate que el servidor esté corriendo
uvicorn main:app --reload

# 2. En otra terminal, ejecuta el test
python test_sliders_mr.py
```

Verás 4 pruebas completas que demuestran todo el flujo.

### **Opción 2: Con curl**

```bash
curl -X POST http://localhost:8000/procesar/diputados \
  -H "Content-Type: application/json" \
  -d '{
    "anio": 2024,
    "plan": "vigente",
    "mr_distritos_manuales": "{\"MORENA\":180,\"PAN\":50,\"PRI\":30,\"PVEM\":25,\"PT\":10,\"MC\":3,\"PRD\":2}",
    "aplicar_topes": true,
    "sobrerrepresentacion": 8,
    "usar_coaliciones": true
  }'
```

---

## 🎨 EJEMPLO DE UI (REACT)

```jsx
const [mrValues, setMrValues] = useState({
  MORENA: 160,
  PAN: 33,
  PRI: 9,
  PVEM: 58,
  PT: 38,
  MC: 1,
  PRD: 1
});

const totalMR = Object.values(mrValues).reduce((a, b) => a + b, 0);

// Sliders
{Object.entries(mrValues).map(([partido, valor]) => (
  <div key={partido}>
    <label>{partido}</label>
    <input
      type="range"
      min="0"
      max="200"
      value={valor}
      onChange={(e) => setMrValues({
        ...mrValues,
        [partido]: parseInt(e.target.value)
      })}
    />
    <span>{valor}</span>
  </div>
))}

<p>Total: {totalMR} / 300</p>

<button onClick={simular} disabled={totalMR > 300}>
  Simular Escenario
</button>
```

---

## ⚠️ CASOS ESPECIALES

### **1. Si el usuario NO usa sliders:**
El backend usa los resultados históricos reales del año seleccionado (del siglado).

### **2. Si la suma es < 300:**
El backend acepta el valor. Quedan "distritos sin asignar" (útil para escenarios parciales).

### **3. Si la suma es > 300:**
El backend devuelve error 400:
```json
{
  "detail": "La suma de MR manuales (350) excede el total de escaños MR (300)"
}
```

### **4. Si hay topes constitucionales:**
El backend ajusta los MR finales para respetar:
- Sobrerrepresentación máxima (8%)
- Tope de 300 escaños por partido
- El usuario ve en la respuesta los valores ajustados

---

## 🔍 VERIFICACIONES DE COHERENCIA

El backend garantiza:

1. ✅ **Suma geográfica = MR total**
   ```
   sum(mr_por_estado["CHIAPAS"]) + sum(mr_por_estado["CDMX"]) + ... = MR_MORENA
   ```

2. ✅ **Suma por estado = distritos del estado**
   ```
   sum(mr_por_estado["CHIAPAS"].values()) = 13 distritos
   ```

3. ✅ **MR + RP = Total (con topes)**
   ```
   resultado["mr"] + resultado["rp"] = resultado["total"]
   ```

---

## 📂 ARCHIVOS RELEVANTES

- **📘 Guía completa**: `GUIA_SLIDERS_MR_FRONTEND.md` (126 KB, muy detallada)
- **🧪 Script de prueba**: `test_sliders_mr.py` (ejecutable)
- **⚙️ Backend principal**: `main.py` líneas 2880-3140
- **🔧 Procesador**: `engine/procesar_diputados_v2.py` líneas 1263-1275
- **📊 Eficiencias**: `engine/calcular_eficiencia_real.py`

---

## ✅ CHECKLIST PARA IMPLEMENTAR EN FRONTEND

- [ ] Crear sliders para cada partido (rango 0-300)
- [ ] Mostrar suma total y máximo (300)
- [ ] Validar suma ≤ 300 antes de enviar
- [ ] Mostrar indicador visual si excede
- [ ] Enviar `mr_distritos_manuales` como JSON string
- [ ] Incluir `aplicar_topes: true`
- [ ] Mostrar tabla de resultados (MR, RP, Total)
- [ ] Mostrar porcentajes de voto calculados
- [ ] Mostrar tabla geográfica con `mr_por_estado`
- [ ] Mostrar mayorías (simple y calificada)
- [ ] Mostrar KPIs (Gallagher, MAE)
- [ ] Agregar loading state
- [ ] Manejar error 400 (suma excedida)
- [ ] Permitir reset a valores históricos

---

## 🎯 CONCLUSIÓN

**TODO ESTÁ LISTO EN EL BACKEND.** El frontend solo necesita:

1. **Crear sliders** para ajustar MR por partido
2. **Validar** que la suma ≤ 300
3. **Enviar** `mr_distritos_manuales` en el POST
4. **Mostrar** los resultados recalculados

El backend se encarga de:
- ✅ Recalcular votos
- ✅ Recalcular RP
- ✅ Aplicar topes
- ✅ Distribuir geográficamente
- ✅ Calcular mayorías y KPIs

**NO necesitas hacer nada más en el backend.** Todo el sistema ya funciona. 🎉

---

**Archivos creados:**
1. `GUIA_SLIDERS_MR_FRONTEND.md` - Guía completa con ejemplos
2. `test_sliders_mr.py` - Script de prueba ejecutable
3. Este resumen ejecutivo

**Para probarlo ahora:**
```bash
python test_sliders_mr.py
```
