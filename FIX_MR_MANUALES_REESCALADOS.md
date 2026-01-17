# 🔥 FIX: Backend reescalaba MR manuales del frontend

## Problema Reportado

**Síntoma:**
- Frontend envía: `mr_distritos_manuales='{"MORENA":51,"PAN":8,...}'` (total=63)
- Backend devuelve: `{"MORENA":247,"PAN":32,...}` (total=300, reescalado!)

**Causa Raíz:**
El backend recibía correctamente `mr_distritos_manuales` y lo convertía a `mr_ganados_geograficos`, pero luego en `procesar_diputados_v2.py` (línea 1924) había lógica que ajustaba los MR cuando `total_mr_actual != mr_seats`:

```python
# ANTES (línea 1924):
total_mr_actual = sum(mr_aligned.values())  # 63
if total_mr_actual != mr_seats:  # 63 != 300 → TRUE
    # Escalar proporcionalmente: 51 * (300/63) ≈ 247
    factor = mr_seats / total_mr_actual
    mr_ajustado = {p: round(mr_aligned[p] * factor) for p in partidos_base}
    mr_aligned = mr_ajustado  # ❌ DESTRUYE valores manuales!
```

## Solución Implementada

### 1. Bandera `mr_son_manuales`

**Archivo:** `engine/procesar_diputados_v2.py`  
**Líneas:** 1260-1274

```python
# Marcar cuando los MR vienen del frontend (no calcular)
mr_son_manuales = False

if mr_ganados_geograficos is not None:
    mr_aligned = {p: int(mr_ganados_geograficos.get(p, 0)) for p in partidos_base}
    mr_son_manuales = True  # ✅ Marcar que NO deben reescalarse
```

### 2. Evitar Reescalado

**Archivo:** `engine/procesar_diputados_v2.py`  
**Líneas:** 1922-1935

```python
total_mr_actual = sum(mr_aligned.values())

# 🔥 NUEVO: NO ajustar si los MR son manuales
if mr_son_manuales:
    _maybe_log(f"✅ MR manuales del frontend ({total_mr_actual}) - NO se reescalarán", 'info')
    # Actualizar mr_seats para reflejar el total real
    mr_seats = total_mr_actual
elif total_mr_actual != mr_seats:
    # Solo escalar si los MR fueron CALCULADOS (no manuales)
    ...
```

### 3. Logging Mejorado

El backend ahora muestra claramente cuando recibe MR manuales:

```
[INFO] Usando MR geográficos proporcionados (redistritación geográfica real)
[INFO] ✅ MR manuales del frontend (63) - NO se reescalarán
[INFO]    mr_seats actualizado a 63 para coincidir con MR manuales
```

## Tests de Validación

### Test 1: MR manuales básicos (total=63)

```python
mr_manuales = {"MORENA": 51, "PAN": 8, "PRI": 1, "MC": 2, "PVEM": 1}

# ANTES: Backend devolvía MORENA=247 (reescalado)
# AHORA: Backend devuelve MORENA=51 (exacto) ✅
```

**Resultado:** ✅ PASÓ

### Test 2: MR manuales con total != mr_seats

```python
mr_manuales = {"MORENA": 80, "PAN": 12, ...}  # total=100
mr_seats = 300  # Cámara vigente

# ANTES: Backend escalaba 100 → 300
# AHORA: Backend respeta 100 ✅
```

**Resultado:** ✅ PASÓ

## Archivos Modificados

1. **engine/procesar_diputados_v2.py**
   - Línea 1260: Agregar `mr_son_manuales = False`
   - Línea 1271: Setear `mr_son_manuales = True` cuando hay `mr_ganados_geograficos`
   - Líneas 1922-1935: Condicional que evita reescalado si `mr_son_manuales`

## Archivos de Test

1. **test_mr_manuales_respetados.py** (nuevo)
   - Test 1: MR manuales básicos
   - Test 2: MR manuales con total diferente a mr_seats
   - Ambos tests pasan ✅

## Flujo Corregido

### Frontend → Backend

1. Usuario usa sliders: CHIAPAS ↓
2. Frontend envía:
   ```json
   {
     "mr_distritos_manuales": '{"MORENA":51,"PAN":8,"PRI":1,"MC":2,"PVEM":1,"PT":0,"PRD":0}'
   }
   ```

3. Backend (main.py línea 3012):
   ```python
   mr_ganados_geograficos = json.loads(mr_distritos_manuales)
   # {"MORENA": 51, "PAN": 8, ...}
   ```

4. Backend (procesar_diputados_v2.py línea 1271):
   ```python
   mr_aligned = mr_ganados_geograficos
   mr_son_manuales = True  # ✅ NO reescalar
   ```

5. Backend (línea 1924):
   ```python
   if mr_son_manuales:
       # Saltear escalado, usar valores exactos
       mr_seats = total_mr_actual  # 63
   ```

6. Backend devuelve:
   ```json
   {
     "seat_chart": {"MORENA": 51, "PAN": 8, ...},  # ✅ Exacto!
     "meta": {"mr_por_estado": {...}}
   }
   ```

## Impacto

### ✅ Correcto Ahora

- Sliders de distritos MR funcionan correctamente
- Frontend recibe exactamente los valores que envió
- Tabla geográfica muestra distribución real después de sliders
- Totales por partido coinciden con ajustes manuales

### ⚠️  Cambio en Comportamiento

**ANTES:**
- Backend siempre ajustaba MR para sumar `mr_seats` (300)
- MR manuales se escalaban proporcionalmente

**AHORA:**
- Backend respeta MR manuales TAL CUAL
- `mr_seats` se actualiza dinámicamente al total de MR manuales
- Solo escala cuando los MR fueron CALCULADOS (no manuales)

## Compatibilidad

### ✅ Casos que funcionan igual

1. **Sin MR manuales:** Cálculo automático sigue igual
2. **Escenarios preconfigurados:** Sin cambios
3. **MR históricos:** Sin cambios

### ✅ Casos arreglados

1. **Sliders de distritos:** Ahora funcionan
2. **Redistribución geográfica manual:** Ahora funciona
3. **Tabla geográfica con sliders:** Ahora consistente

## Notas Adicionales

### Relación con Otras Correcciones

Este fix complementa las correcciones previas:

1. **Escalado de `distritos_por_estado`** (líneas 2467-2507)
   - Escala totales por estado según tamaño cámara

2. **Validación de límites por estado** (líneas 2596-2651)
   - Previene que partidos excedan límites estatales

**Juntas:**
- `distritos_por_estado` → Totales correctos por estado
- Validación de límites → Distribuciones válidas
- MR manuales respetados → Frontend y backend sincronizados ✅

### Commit Sugerido

```bash
git add engine/procesar_diputados_v2.py
git add test_mr_manuales_respetados.py
git commit -m "fix: Respetar MR manuales del frontend sin reescalar

- Agregar bandera mr_son_manuales para diferenciar MR calculados vs manuales
- Evitar reescalado cuando mr_ganados_geograficos viene del frontend
- Actualizar mr_seats dinámicamente al total de MR manuales
- Tests: 2/2 pasando (totales 63 y 100 con mr_seats=300)
- Fix para sliders de distritos MR que se reescalaban incorrectamente

Problema: Frontend enviaba MR=51 MORENA, backend devolvía MR=247 (reescalado)
Solución: Detectar y respetar MR manuales sin ajustar al mr_seats predefinido"

git push origin main
```

## Referencias

- Problema reportado en conversación resumida
- Línea problemática original: `engine/procesar_diputados_v2.py:1924`
- Tests de validación: `test_mr_manuales_respetados.py`
- Documentación previa: `BACKEND_AJUSTE_DISTRITOS_INDIVIDUALES.md`
