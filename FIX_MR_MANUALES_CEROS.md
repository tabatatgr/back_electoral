# Fix: MR Manuales Devolviendo Ceros

## Problema

Cuando el frontend enviaba `mr_distritos_manuales` (valores de sliders por partido), el backend devolvía **todos los MR en 0**.

### Diagnóstico

Se identificaron **DOS problemas independientes**:

### Problema 1: Totales por partido no coincidían con seat_chart

**Síntoma**: Backend devolvía `MORENA: 43` en lugar de `MORENA: 52` en la respuesta inicial.

**Causa**: El código que construye `mr_por_estado` (desglose geográfico) distribuía los MR usando el método Hare, y por errores de redondeo/capacidades de estados, la **suma de MORENA en todos los estados no coincidía con el total en seat_chart**.

**Solución**: Agregada validación en `engine/procesar_diputados_v2.py` (líneas ~2830) que **fuerza** que la suma de MR por estado para cada partido coincida EXACTAMENTE con el valor en `mr_dict` (seat_chart):

```python
# 🔥 VALIDACIÓN CRÍTICA: Asegurar que totales por partido coincidan EXACTAMENTE con mr_dict
if mr_por_estado_partido and mr_dict:
    for partido in partidos_base:
        total_distribuido = sum(mr_por_estado_partido.get(estado, {}).get(partido, 0) 
                               for estado in mr_por_estado_partido)
        mr_esperado = mr_dict.get(partido, 0)
        
        if total_distribuido != mr_esperado:
            # Ajustar agregando/quitando MR para que coincidan exactamente
            ...
```

### Problema 2: `aplicar_topes_nacionales` recortaba los MR manuales

**Síntoma**: Cuando el frontend reenviaba `mr_distritos_manuales={"MORENA":43,...}`, el backend devolvía `{"MORENA":0,...}` (todos ceros).

**Causa**: La función `aplicar_topes_nacionales` **recortaba los MR manuales** cuando excedían el tope del +8% de sobrerrepresentación (líneas 480-503):

```python
# Si aún excede después de quitar todo el RP, quitar MR
if excess > 0:
    cut_mr = min(excess, s_mr[p])
    s_mr[p] -= cut_mr  # ❌ PROBLEMA: Recorta MR manuales del frontend
```

Cuando MORENA tenía 43 MR pero el tope era menor, se recortaban **todos los MR**, resultando en 0.

**Solución**: Agregado parámetro `mr_son_manuales` a:
- `aplicar_topes_nacionales()` 
- `asignadip_v2()`
- `procesar_diputados_v2()`

Cuando `mr_son_manuales=True`, **solo se recortan RP, NUNCA los MR**:

```python
if mr_son_manuales:
    # MR manuales: solo quitar RP, NUNCA tocar MR
    excess = s_tot[p] - cap_eff
    cut_rp = min(excess, s_rp[p])
    s_rp[p] -= cut_rp
    s_tot[p] -= cut_rp
    sobrantes += cut_rp
    cut_mr = 0  # ✅ MR preservados
```

## Archivos Modificados

### `engine/procesar_diputados_v2.py`

1. **Función `aplicar_topes_nacionales`** (líneas ~361):
   - Agregado parámetro `mr_son_manuales: bool = False`
   - Modificada lógica de recorte (líneas ~470-520) para preservar MR cuando son manuales

2. **Función `asignadip_v2`** (líneas ~881):
   - Agregado parámetro `mr_son_manuales: bool = False`
   - Pasa el flag a `aplicar_topes_nacionales`

3. **Función `procesar_diputados_v2`** (líneas ~1264):
   - Marca `mr_son_manuales = True` cuando se recibe `mr_ganados_geograficos`
   - Pasa el flag a `asignadip_v2` en ambas llamadas (líneas ~1900, ~2175)

4. **Validación de totales** (líneas ~2830):
   - Agregado bloque de código que verifica y ajusta la distribución geográfica
   - Garantiza que `sum(mr_por_estado[partido]) == mr_dict[partido]` para cada partido

## Flujo Correcto Ahora

1. **Carga inicial (sin sliders)**:
   - Backend calcula MR base: `{MORENA: 52, PAN: 8, ...}` ✅
   - Construye `mr_por_estado` distribuyendo por población
   - **NUEVO**: Valida y ajusta para que totales coincidan exactamente ✅
   - Devuelve al frontend: `seat_chart={MORENA: 52}`, `mr_por_estado={CDMX: {MORENA: 12}, ...}` ✅

2. **Frontend mueve sliders**:
   - Frontend suma totales: `mr_distritos_manuales={MORENA: 52, PAN: 10, ...}` (correctos ahora)
   - Envía al backend en el request

3. **Backend procesa MR manuales**:
   - Marca `mr_son_manuales = True` ✅
   - Calcula MR base para regla de tres: `{MORENA: 52, PAN: 8, ...}`
   - Ajusta votos proporcionalmente
   - Llama a `asignadip_v2` con `mr_son_manuales=True` ✅
   - **NUEVO**: `aplicar_topes_nacionales` NO recorta MR manuales ✅
   - Devuelve: `{MORENA: 52, PAN: 10, ...}` ✅ (valores correctos, no ceros)

## Pruebas Recomendadas

1. **Test básico**: Verificar que carga inicial devuelva MORENA=52 (no 43)
2. **Test sliders**: Mover sliders y verificar que MR no vuelvan a 0
3. **Test topes**: Con MR manuales altos, verificar que solo se recorten RP
4. **Test totales**: Verificar que `sum(mr_por_estado[MORENA]) == seat_chart.MORENA`

## Notas Técnicas

- La validación de totales usa un algoritmo greedy para agregar/quitar MR de estados con más capacidad disponible
- El flag `mr_son_manuales` se propaga a través de 3 niveles de llamadas
- Los topes constitucionales (8%) se siguen aplicando, pero solo a RP cuando hay MR manuales
- Esta solución preserva la intención del usuario (sliders) mientras respeta la matemática electoral

## Fecha

2025-01-09
