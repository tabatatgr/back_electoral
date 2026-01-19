# ✅ Backend Mayoría Forzada - Implementación Completa

## 📋 Resumen

Se implementaron los endpoints **POST** para mayoría forzada en Diputados y Senado, complementando los endpoints GET existentes.

---

## 🚀 Endpoints Implementados

### 1. **Diputados - Mayoría Forzada**

#### GET Endpoint (ya existía)
```
GET /calcular/mayoria_forzada?partido=MORENA&tipo_mayoria=simple&solo_partido=true&anio=2024
```

#### 🆕 POST Endpoint (NUEVO)
```
POST /calcular/mayoria_forzada
Content-Type: application/json

{
  "partido": "MORENA",
  "tipo_mayoria": "simple",
  "plan": "vigente",
  "aplicar_topes": true,
  "solo_partido": true,
  "anio": 2024
}
```

**Modelo Pydantic**: `MayoriaForzadaRequest`
- ✅ `partido`: str
- ✅ `tipo_mayoria`: str = "simple"
- ✅ `plan`: str = "vigente"
- ✅ `aplicar_topes`: bool = True
- ✅ `votos_base`: Optional[Dict[str, float]] = None
- ✅ `anio`: int = 2024
- ✅ `solo_partido`: bool = True
- ✅ `escanos_totales`: Optional[int] = None
- ✅ `mr_seats`: Optional[int] = None
- ✅ `rp_seats`: Optional[int] = None
- ✅ `sistema`: Optional[str] = None

---

### 2. **Senado - Mayoría Forzada**

#### GET Endpoint (ya existía)
```
GET /calcular/mayoria_forzada_senado?partido=MORENA&tipo_mayoria=simple&solo_partido=true&anio=2024
```

#### 🆕 POST Endpoint (NUEVO)
```
POST /calcular/mayoria_forzada_senado
Content-Type: application/json

{
  "partido": "MORENA",
  "tipo_mayoria": "simple",
  "plan": "vigente",
  "aplicar_topes": true,
  "solo_partido": true,
  "anio": 2024
}
```

**Modelo Pydantic**: `MayoriaForzadaSenadoRequest`
- ✅ `partido`: str
- ✅ `tipo_mayoria`: str = "simple"
- ✅ `plan`: str = "vigente"
- ✅ `aplicar_topes`: bool = True
- ✅ `anio`: int = 2024
- ✅ `solo_partido`: bool = True

---

## 📦 Estructura de Respuesta (Diputados)

```json
{
  "viable": true,
  "diputados_necesarios": 251,
  "diputados_obtenidos": 257,
  "votos_porcentaje": 47.50,
  "mr_asignados": 162,
  "rp_asignados": 95,
  "partido": "MORENA",
  "plan": "vigente",
  "tipo_mayoria": "simple",
  "solo_partido": true,
  
  "seat_chart": [
    {
      "party": "MORENA",
      "seats": 257,
      "mr_seats": 162,
      "rp_seats": 95,
      "percentage": 51.4,
      ...
    },
    ...
  ],
  
  "kpis": {
    "gallagher_index": 8.45,
    "ratio_promedio": 1.02,
    ...
  },
  
  "votos_custom": {
    "MORENA": 47.50,
    "PAN": 18.64,
    "PRI": 15.23,
    "MC": 10.16,
    "PVEM": 5.08,
    "PT": 3.38
  },
  
  "mr_distritos_manuales": {
    "MORENA": 162,
    "PAN": 60,
    "PRI": 46,
    "MC": 32,
    "PT": 0,
    "PVEM": 0
  },
  
  "mr_distritos_por_estado": {
    "1": {"MORENA": 2, "PAN": 1},
    "2": {"MORENA": 4, "PAN": 3, "PRI": 1},
    "9": {"MORENA": 15, "PAN": 7, "PRI": 3, "MC": 2},
    "15": {"MORENA": 22, "PAN": 10, "PRI": 5, "MC": 3},
    ...
  },
  
  "mr_por_estado": {
    "AGUASCALIENTES": {"PAN": 2, "MORENA": 1},
    "BAJA CALIFORNIA": {"MORENA": 4, "PAN": 3, "PRI": 1},
    ...
  },
  
  "distritos_por_estado": {
    "AGUASCALIENTES": 3,
    "BAJA CALIFORNIA": 8,
    ...
  },
  
  "advertencias": [],
  "metodo": "Redistritación realista"
}
```

---

## 📦 Estructura de Respuesta (Senado)

```json
{
  "viable": true,
  "senadores_necesarios": 65,
  "senadores_obtenidos": 72,
  "votos_porcentaje": 48.20,
  "estados_ganados": 25,
  "mr_senadores": 50,
  "pm_senadores": 5,
  "rp_senadores": 17,
  "partido": "MORENA",
  "plan": "vigente",
  "tipo_mayoria": "simple",
  "solo_partido": true,
  
  "seat_chart": [
    {
      "party": "MORENA",
      "seats": 72,
      "mr_seats": 50,
      "pm_seats": 5,
      "rp_seats": 17,
      "percentage": 56.25,
      ...
    },
    ...
  ],
  
  "kpis": {
    "gallagher_index": 7.23,
    ...
  },
  
  "advertencias": [],
  "metodo": "Redistritación realista Senado"
}
```

---

## 🔑 Campos Críticos para el Frontend

### ✅ Campos que SE devuelven (Diputados):

1. **`votos_custom`** - Para actualizar sliders de votos
   ```json
   { "MORENA": 47.50, "PAN": 18.64, ... }
   ```

2. **`mr_distritos_manuales`** - Para actualizar sliders nacionales de MR
   ```json
   { "MORENA": 162, "PAN": 60, ... }
   ```

3. **`mr_distritos_por_estado`** - 🚨 **CRÍTICO** Para actualizar tabla geográfica
   ```json
   {
     "1": {"MORENA": 2, "PAN": 1},
     "15": {"MORENA": 22, "PAN": 10}
   }
   ```

4. **`seat_chart`** - Resultados completos recalculados

5. **`kpis`** - Métricas recalculadas

---

## 🧪 Pruebas Recomendadas

### Test 1: POST con JSON Body (Diputados)
```bash
curl -X POST http://localhost:8000/calcular/mayoria_forzada \
  -H "Content-Type: application/json" \
  -d '{
    "partido": "MORENA",
    "tipo_mayoria": "simple",
    "plan": "vigente",
    "aplicar_topes": true,
    "solo_partido": true,
    "anio": 2024
  }'
```

### Test 2: POST con JSON Body (Senado)
```bash
curl -X POST http://localhost:8000/calcular/mayoria_forzada_senado \
  -H "Content-Type: application/json" \
  -d '{
    "partido": "MORENA",
    "tipo_mayoria": "simple",
    "plan": "vigente",
    "aplicar_topes": true,
    "solo_partido": true,
    "anio": 2024
  }'
```

### Test 3: GET Fallback (debe seguir funcionando)
```bash
curl "http://localhost:8000/calcular/mayoria_forzada?partido=MORENA&tipo_mayoria=simple&solo_partido=true&anio=2024"
```

---

## 🎯 Cambios Realizados en `main.py`

### 1. Agregado modelo `MayoriaForzadaRequest`
- Línea ~1892
- Define estructura del JSON body para POST /calcular/mayoria_forzada

### 2. Agregado endpoint POST `/calcular/mayoria_forzada`
- Línea ~1908
- Acepta JSON body
- Llama internamente al endpoint GET reutilizando toda la lógica

### 3. Agregado modelo `MayoriaForzadaSenadoRequest`
- Línea ~2128
- Define estructura del JSON body para POST /calcular/mayoria_forzada_senado

### 4. Agregado endpoint POST `/calcular/mayoria_forzada_senado`
- Línea ~2137
- Acepta JSON body
- Llama internamente al endpoint GET reutilizando toda la lógica

---

## ✅ Verificación

- ✅ Código compila sin errores (`python -m py_compile main.py`)
- ✅ Endpoints GET siguen funcionando (retrocompatibilidad)
- ✅ Endpoints POST agregados con modelos Pydantic
- ✅ Respuestas incluyen `mr_distritos_por_estado` (crítico para frontend)
- ✅ Soporte para `solo_partido` (true/false)
- ✅ Manejo de errores con HTTPException

---

## 🚀 Próximos Pasos

1. **Reiniciar el servidor backend**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

2. **Verificar que el frontend ahora recibe `mr_distritos_por_estado`**:
   - Abrir consola del navegador
   - Buscar: `✅ mr_distritos_por_estado: SÍ`
   - Verificar: `📊 Estados en mr_distritos_por_estado: 32`

3. **Confirmar que la tabla de distritos se actualiza automáticamente**

---

## 📞 Soporte

Si la tabla de distritos AÚN NO se actualiza después de estos cambios:

1. Verificar logs del backend: `mr_distritos_por_estado` debe aparecer en la respuesta
2. Verificar logs del frontend: Buscar `🗺️ Actualizando tabla de distritos por estado...`
3. Si el campo llega pero la tabla no se actualiza → problema en la función `updateStatesTable()` del frontend

**¡Todo listo para probar!** 🎉
