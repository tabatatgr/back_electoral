# FIX: Recálculo Dinámico de mr_por_estado y distritos_por_estado

## Problema Identificado

El backend estaba enviando datos **FIJOS** de `mr_por_estado` y `distritos_por_estado` que no cambiaban cuando el usuario modificaba los parámetros de la petición (especialmente la magnitud de MR).

Esto causaba que el frontend mostrara siempre la misma tabla geográfica sin importar si el usuario seleccionaba:
- 300 MR (plan vigente)
- 64 MR (sistema personalizado)
- 150 MR (sistema personalizado)

## Causa Raíz

El código que generaba `mr_por_estado` solo funcionaba cuando había datos distrito por distrito del siglado, pero cuando se usaba `mr_ganados_geograficos` (redistritación geográfica), **no se generaban los datos geográficos detallados**.

## Solución Implementada

### Archivo Modificado: `engine/procesar_diputados_v2.py`

Se agregó lógica dual para calcular `mr_por_estado`:

**CASO 1: Con redistritación geográfica (mr_ganados_geograficos)**
- Usa el método Hare para distribuir `mr_seats` entre los 32 estados según población
- Distribuye los MR de cada partido proporcionalmente entre estados
- Ajusta totales para que cada estado tenga exactamente los distritos asignados por Hare

**CASO 2: Sin redistritación (método tradicional)**
- Calcula distrito por distrito desde el DataFrame `recomposed`
- Determina ganador por votos en cada distrito
- Acumula por estado

### Código Agregado

```python
# CASO 1: Si hay mr_ganados_geograficos, distribuir por estado usando Hare
if mr_ganados_geograficos is not None and mr_seats and mr_seats > 0:
    # Cargar población por estado
    from redistritacion.modulos.reparto_distritos import repartir_distritos_hare
    from redistritacion.modulos.distritacion import cargar_secciones_ine
    
    secciones = cargar_secciones_ine()
    poblacion_por_estado = secciones.groupby('ENTIDAD')['POBTOT'].sum().to_dict()
    
    # Repartir distritos usando Hare
    asignacion_distritos = repartir_distritos_hare(
        poblacion_estados=poblacion_por_estado,
        n_distritos=mr_seats,
        piso_constitucional=2
    )
    
    # Distribuir MR de cada partido por estado proporcionalmente
    for estado_id, nombre_estado in estado_nombres.items():
        distritos_totales = asignacion_distritos.get(estado_id, 0)
        distritos_por_estado[nombre_estado] = distritos_totales
        
        total_mr_nacional = sum(mr_ganados_geograficos.values())
        
        if total_mr_nacional > 0 and distritos_totales > 0:
            for partido in partidos_base:
                mr_partido_nacional = mr_ganados_geograficos.get(partido, 0)
                mr_partido_estado = int(round((mr_partido_nacional / total_mr_nacional) * distritos_totales))
                mr_por_estado_partido[nombre_estado][partido] = mr_partido_estado
            
            # Ajustar residuo
            suma_actual = sum(mr_por_estado_partido[nombre_estado].values())
            if suma_actual != distritos_totales:
                partido_mayor = max(partidos_base, key=lambda p: mr_ganados_geograficos.get(p, 0))
                diferencia = distritos_totales - suma_actual
                mr_por_estado_partido[nombre_estado][partido_mayor] += diferencia
```

## Resultados del Test

```
✅ ÉXITO: Los datos de distritos_por_estado SÍ cambian según parámetros
   Valores únicos encontrados: [64, 150, 300]

📊 Coherencia MR solicitado vs asignado:
   ✅ Plan Vigente (300 MR): Diferencia 0 (0.0%)
   ✅ Personalizado (64 MR + 64 RP = 128 total): Diferencia 0 (0.0%)
   ✅ Personalizado (150 MR + 150 RP = 300 total): Diferencia 0 (0.0%)
```

### Ejemplo de Salida Dinámica

**Con 64 MR:**
```json
{
  "distritos_por_estado": {
    "AGUASCALIENTES": 2,
    "BAJA CALIFORNIA": 2,
    ...
  },
  "mr_por_estado": {
    "AGUASCALIENTES": {"PRI": 1, "PVEM": 1},
    ...
  }
}
```

**Con 150 MR:**
```json
{
  "distritos_por_estado": {
    "AGUASCALIENTES": 3,
    "BAJA CALIFORNIA": 5,
    ...
  },
  "mr_por_estado": {
    "AGUASCALIENTES": {"PAN": 1, "PRI": 1, "MORENA": 1},
    ...
  }
}
```

**Con 300 MR:**
```json
{
  "distritos_por_estado": {
    "AGUASCALIENTES": 3,
    "BAJA CALIFORNIA": 9,
    ...
  },
  "mr_por_estado": {
    "AGUASCALIENTES": {"PAN": 3},
    ...
  }
}
```

## Impacto

✅ El frontend ahora puede mostrar la tabla geográfica correcta para CUALQUIER configuración de escaños MR

✅ Los datos son dinámicos y reflejan exactamente los parámetros solicitados

✅ Funciona tanto para escenarios predefinidos (vigente, plan_a, etc.) como personalizados

## Archivos Modificados

- `engine/procesar_diputados_v2.py`: Lógica de recálculo dinámico de mr_por_estado
- `test_mr_por_estado_dinamico.py`: Test de verificación (NUEVO)

## Test de Verificación

Para verificar que los datos cambian correctamente:

```bash
python test_mr_por_estado_dinamico.py
```

El test compara 3 escenarios con diferentes magnitudes de MR y confirma que los totales son únicos y correctos.

---

**Estado:** ✅ COMPLETADO Y VERIFICADO
**Fecha:** 2026-01-16
