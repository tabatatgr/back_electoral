# Fix: Parámetro max_seats_per_party ahora funciona correctamente

## Problema reportado

El parámetro `max_seats_per_party` (tope absoluto de escaños por partido) no estaba funcionando. El sistema solo aplicaba restricción por sobrerrepresentación (8%) y un tope hardcoded de 300 escaños, pero ignoraba el valor personalizado enviado desde el frontend.

## Causa raíz

El parámetro `max_seats_per_party` se recibía correctamente en todos los niveles (endpoint → `procesar_diputados_v2` → `asignadip_v2`) pero NO se pasaba a la función `aplicar_topes_nacionales` que es donde realmente se aplica el límite de escaños.

## Solución implementada

### 1. Modificación de `aplicar_topes_nacionales` (línea ~362)

**Antes:**
```python
def aplicar_topes_nacionales(s_mr: np.ndarray, s_rp: np.ndarray,
                            v_nacional: np.ndarray,
                            S: int,
                            max_pp: float = 0.08,
                            max_seats: int = 300) -> Dict:
    # ...
    lim_300 = np.full(N, max_seats, dtype=int)
```

**Después:**
```python
def aplicar_topes_nacionales(s_mr: np.ndarray, s_rp: np.ndarray,
                            v_nacional: np.ndarray,
                            S: int,
                            max_pp: float = 0.08,
                            max_seats: int = 300,
                            max_seats_per_party: Optional[int] = None) -> Dict:
    # ...
    tope_absoluto = max_seats_per_party if max_seats_per_party is not None else max_seats
    lim_tope = np.full(N, tope_absoluto, dtype=int)
```

### 2. Modificación de `asignadip_v2` (línea ~544)

**Añadido parámetro:**
```python
def asignadip_v2(...,
                 max_seats_per_party: Optional[int] = None,
                 ...):
```

**Actualizada llamada a `aplicar_topes_nacionales` (línea ~620):**
```python
resultado_topes = aplicar_topes_nacionales(
    s_mr=ssd, s_rp=s_rp_init, v_nacional=v_nacional,
    S=S, max_pp=max_pp, max_seats=max_seats,
    max_seats_per_party=max_seats_per_party  # ← NUEVO
)
```

### 3. Modificación de llamadas en `procesar_diputados_v2` (líneas ~1295 y ~1505)

**Actualizado ambas llamadas a `asignadip_v2`:**
```python
resultado = asignadip_v2(
    ...,
    max_seats_per_party=int(max_seats_per_party) if max_seats_per_party is not None else None,  # ← NUEVO
    ...
)
```

### 4. Verificación en `main.py`

El endpoint `/procesar/diputados` ya pasaba correctamente `max_seats_per_party` a `procesar_diputados_v2`:
```python
resultado = procesar_diputados_v2(
    ...,
    max_seats_per_party=max_seats_per_party_final,
    ...
)
```

## Validación

Se creó test en `test_max_seats_per_party.py` que verifica:

**Escenario de prueba:**
- 5 partidos, el primero dominante (10M votos vs 2M, 1.5M, 1M, 0.5M)
- 180 escaños MR para el dominante (vs 30, 20, 15, 5)
- 500 escaños totales (250 MR + 250 RP)
- Límite: `max_seats_per_party=250`

**Resultados:**

| Configuración | Partido dominante | Total escaños |
|--------------|-------------------|---------------|
| **SIN** límite personalizado | 300 escaños | 500 |
| **CON** límite 250 | 250 escaños ✅ | 500 |

### Output del test:
```
✓ Sin límite personalizado, partido dominante tiene 300 escaños
✓ Con límite, partido dominante tiene 250 escaños (≤250) ✅
✓ Ningún partido supera el tope de 250 escaños ✅
✓ Suma total de escaños: 500/500
✅ TEST PASADO: max_seats_per_party funciona correctamente
```

## Comportamiento esperado

Cuando el frontend envía:
```json
{
  "max_seats_per_party": 250,
  "escanos_totales": 500,
  ...
}
```

El backend ahora:
1. ✅ Recibe el parámetro en el endpoint
2. ✅ Lo propaga a `procesar_diputados_v2`
3. ✅ Lo pasa a `asignadip_v2`
4. ✅ Lo usa en `aplicar_topes_nacionales`
5. ✅ **Ningún partido puede superar 250 escaños totales (MR+RP)**

Si `max_seats_per_party` es `None`, se usa el valor por defecto `max_seats=300`.

## Archivos modificados

- `engine/procesar_diputados_v2.py`:
  - Función `aplicar_topes_nacionales` (línea 362): añadido parámetro y lógica
  - Función `asignadip_v2` (línea 544): añadido parámetro y actualizada llamada
  - Función `procesar_diputados_v2` (líneas 1295, 1505): actualizadas ambas llamadas

## Test creado

- `test_max_seats_per_party.py`: Test unitario que valida el límite absoluto

## Fecha

21 de enero de 2025
