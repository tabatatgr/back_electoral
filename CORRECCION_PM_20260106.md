# CORRECCIÓN IMPLEMENTADA - PM NO SE AJUSTA
# Fecha: 2026-01-06
# =========================================

## PROBLEMA IDENTIFICADO (reportado por usuario)

El código anterior INCORRECTAMENTE:
- Recortaba PM cuando MR + PM excedía el tope constitucional
- Redistribuía escaños PM "sobrantes" como si fueran compensatorios
- Trataba PM como "RP disfrazada"

Esto es CONSTITUCIONALMENTE INCORRECTO porque:
- PM = Primera Minoría = Segundo lugar en un distrito
- NO es negociable, NO es ajustable, NO es redistribuible
- Si un partido quedó segundo en X distritos, ganó X escaños PM. PUNTO.
- El tope puede romperse por victorias directas (MR + PM), y eso está PERMITIDO

## CORRECCIÓN APLICADA

engine/procesar_diputados_v2.py líneas 2147-2190:

ANTES (INCORRECTO):
```python
if aplicar_topes:
    pm_dict = _aplicar_topes_a_pm(...)  # Recortaba PM
```

DESPUÉS (CORRECTO):
```python
# PM NO SE AJUSTA - es resultado de victorias de segunda fuerza
# Si MR + PM excede el tope, se REPORTA pero NO se corrige
# Solo RP puede ajustarse para respetar el tope
if aplicar_topes and print_debug:
    # Solo verificación/reporte, NO modificación
    if total_sin_rp > cap:
        _maybe_log(f"[PM TOPES] {p}: MR+PM={total_sin_rp} EXCEDE tope {cap}")
        _maybe_log(f"[PM TOPES] {p}: Esta sobrerrepresentación es PERMITIDA")
```

La función _aplicar_topes_a_pm() sigue existiendo en el código (líneas 727-813)
pero YA NO SE LLAMA. Queda como referencia histórica o para escenarios
contrafactuales futuros.

## VERIFICACIÓN DE RESULTADOS

Archivo: outputs/comparativa_2021_vs_2024_CORREGIDO_20260106_140933.csv

MORENA 2024 (42.49% votos, tope = 201 escaños):

MR 200 - RP 200: MR=161 + PM=0  + RP=40 = 201 [OK - capado en RP]
MR 300 - RP 100: MR=160 + PM=0  + RP=41 = 201 [OK - capado en RP]
MR 200 - PM 200: MR=161 + PM=30 + RP=0  = 191 [OK - dentro del tope]
MR 300 - PM 100: MR=160 + PM=15 + RP=0  = 175 [OK - dentro del tope]

DISTRIBUCIÓN PM (escenario MR 200 - PM 200):
- PAN:    70 PM (segundos lugares)
- PRI:    37 PM
- MC:     34 PM
- MORENA: 30 PM ← NO se ajustó, quedó segundo en ~30 distritos
- PVEM:   18 PM
- PT:     10 PM
- PRD:     1 PM (aunque <3%, ganó 1 segundo lugar)
Total:   200 PM ✓

## LÓGICA CONSTITUCIONAL CORRECTA

1. Tope se evalúa sobre MR + PM + RP ✓
2. MR NO se toca (victorias directas) ✓
3. PM NO se toca (segundos lugares) ✓  ← CORRECCIÓN APLICADA
4. RP absorbe todo el ajuste posible ✓
5. Si quitando RP el partido rebasa → sobrerrepresentación permitida ✓

## CONCLUSIÓN

✅ PM ya NO se ajusta artificialmente
✅ El modelo respeta la naturaleza no-compensatoria de Primera Minoría
✅ Si MR+PM excede el tope, se permite (sobrerrepresentación estructural)
✅ Solo RP se usa para cumplir topes constitucionales

El código ahora refleja correctamente la tensión real del sistema
electoral mexicano entre:
- Respetar victorias directas (MR + PM)
- Cumplir topes constitucionales (vía RP)
