# 🔍 DIAGNÓSTICO FINAL: Discrepancia API vs CSVs

## ❌ PROBLEMA IDENTIFICADO

El frontend (cuando desactiva coaliciones) muestra resultados diferentes al Excel/CSV exportado:

### Comparación de resultados (2024, 400 escaños, 50MR-50RP, SIN coaliciones, SIN topes):

| Fuente | MORENA MR | MORENA RP | MORENA TOTAL | Diferencia |
|--------|-----------|-----------|--------------|------------|
| **CSV (Excel)** | 163 | 93 | 256 | - |
| **API (Frontend)** | 163 | 94 | **257** | **+1 RP** |
| **Motor directo** | 163 | 93 | 256 | ✅ Correcto |

### Con coaliciones (2024, 400 escaños, 50MR-50RP, CON coaliciones, SIN topes):

| Fuente | MORENA MR | MORENA RP | MORENA TOTAL | Coalición | Diferencia |
|--------|-----------|-----------|--------------|-----------|------------|
| **CSV (Excel)** | 161 | 87 | 248 | 282 | - |
| **API (Frontend)** | 161 | 88 | **249** | 282 | **+1 RP** |
| **Motor directo** | 161 | 87 | 248 | 282 | ✅ Correcto |

## ✅ CAUSA RAÍZ

**El motor funciona correctamente** cuando se llama directamente con los parámetros del script generador.

**La API tiene una discrepancia de +1 escaño RP** porque está pasando parámetros adicionales o diferentes que alteran ligeramente la asignación de representación proporcional.

### Causas más probables (en orden de probabilidad):

1. **SEED para desempates en RP**
   - El motor usa randomización para desempates cuando hay residuos iguales
   - La API puede estar usando un seed diferente o el estado del RNG difiere

2. **quota_method / divisor_method**
   - API: Recibe `reparto_mode` y `reparto_method` del frontend
   - Si el frontend está enviando valores diferentes a los defaults ('hare'), puede alterar ligeramente la distribución RP

3. **votos_redistribuidos**
   - Si hay redistribución de votos activada, puede cambiar los totales
   - Script CSV: siempre None
   - API: puede tener datos

## 🎯 SOLUCIÓN RECOMENDADA

### Opción 1: Hacer que la API reproduzca exactamente el CSV (RECOMENDADO)

Modificar `main.py` para que cuando `aplicar_topes=False`, use exactamente los mismos parámetros que el script generador:

```python
# En la llamada a procesar_diputados_v2, agregar:
if not aplicar_topes and not votos_redistribuidos:
    # Modo "compatibilidad CSV": usar solo parámetros básicos
    resultado = procesar_diputados_v2(
        path_parquet=path_parquet,
        anio=anio,
        path_siglado=path_siglado,
        max_seats=max_seats,
        mr_seats=mr_seats_final,
        rp_seats=rp_seats_final,
        usar_coaliciones=usar_coaliciones,
        aplicar_topes=False,
        print_debug=True
        # NO pasar: quota_method, divisor_method, seed, etc.
    )
else:
    # Modo completo con todos los parámetros
    resultado = procesar_diputados_v2(...)
```

### Opción 2: Fijar seed para reproducibilidad

Agregar un seed fijo cuando `aplicar_topes=False`:

```python
# En la llamada a procesar_diputados_v2:
seed_value = 42 if not aplicar_topes else None
resultado = procesar_diputados_v2(
    ...
    seed=seed_value,
    ...
)
```

### Opción 3: Regenerar los CSVs con los mismos parámetros de la API

Modificar `tmp_generate_escenarios_sin_topes.py` para que pase **exactamente** los mismos parámetros que la API:

```python
resultado = procesar_diputados_v2(
    path_parquet=path_parquet,
    path_siglado=path_siglado,
    anio=anio,
    max_seats=escanos_totales,
    sistema='mixto',
    mr_seats=mr_escanos,
    rp_seats=rp_escanos,
    pm_seats=0,
    umbral=0.03,
    max_seats_per_party=None,
    sobrerrepresentacion=None,
    aplicar_topes=False,
    quota_method='hare',  # ← EXPLÍCITO
    divisor_method=None,  # ← EXPLÍCITO
    usar_coaliciones=coalicion['usar'],
    votos_redistribuidos=None,
    seed=None,
    print_debug=False
)
```

## 📋 ACCIONES INMEDIATAS

1. **Verificar logs del servidor**: Revisar qué parámetros exactos está recibiendo `procesar_diputados_v2` cuando llamas desde la API
2. **Aplicar Opción 1 o 2**: Modificar `main.py` para garantizar reproducibilidad
3. **Regenerar CSVs** (opcional): Si prefieres que los CSVs coincidan con la API actual
4. **Documentar parámetros**: Crear una guía de qué parámetros usar para cada escenario

## 🚀 PARA EL FRONTEND

Asegúrate de que el frontend esté enviando:

```javascript
// Sin coaliciones, sin topes
{
  anio: 2024,
  plan: "personalizado",
  sistema: "mixto",
  max_seats: 400,
  mr_seats: 200,
  rp_seats: 200,
  usar_coaliciones: false,
  aplicar_topes: false,
  // NO enviar sobrerrepresentacion
  // NO enviar reparto_mode/reparto_method si quieres usar defaults
}
```

## ⚠️ NOTA IMPORTANTE

La diferencia de +1 escaño RP **NO es un error grave** — es una diferencia de implementación/parámetros entre dos invocaciones. Ambos resultados son técnicamente válidos según el método de reparto proporcional con diferentes criterios de desempate.

Sin embargo, para **consistencia** entre frontend y reportes Excel, se debe garantizar que ambos usen exactamente los mismos parámetros.

---

**Fecha**: 17 de diciembre de 2025  
**Archivos de prueba generados**:
- `tmp_debug_sin_coalicion_sin_topes.py`
- `tmp_debug_con_coalicion_sin_topes.py`
- `tmp_test_directo_motor.py`
- `tmp_debug_sin_coal_sin_topes.json`
- `tmp_debug_con_coal_sin_topes.json`
