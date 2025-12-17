"""
Test directo del cálculo de topes sin necesidad del servidor
Para diagnosticar por qué el 8% no da 252 escaños
"""
import sys
sys.path.insert(0, '.')

import numpy as np
import pandas as pd
from engine.procesar_diputados_v2 import procesar_diputados_v2

print("=" * 80)
print("DIAGNÓSTICO: ¿Por qué 8% no da 252 escaños para MORENA?")
print("=" * 80)

# Llamar directamente al motor
resultado = procesar_diputados_v2(
    path_parquet="data/computos_diputados_2024.parquet",
    anio=2024,
    path_siglado="data/siglado-diputados-2024.csv",
    max_seats=500,
    sistema="mixto",
    mr_seats=300,
    rp_seats=200,
    pm_seats=0,
    umbral=0.03,
    max_seats_per_party=None,  # SIN tope absoluto
    sobrerrepresentacion=8.0,   # CON cláusula del 8%
    aplicar_topes=True,
    quota_method=None,
    divisor_method="d_hondt",
    usar_coaliciones=False,
    votos_redistribuidos=None,
    print_debug=True
)

print("\n" + "=" * 80)
print("RESULTADO:")
print("=" * 80)

if 'tot' in resultado:
    morena_total = resultado['tot'].get('MORENA', 0)
    morena_mr = resultado['mr'].get('MORENA', 0) if 'mr' in resultado else 0
    morena_rp = resultado['rp'].get('MORENA', 0) if 'rp' in resultado else 0
    
    print(f"\nMORENA:")
    print(f"  MR: {morena_mr}")
    print(f"  RP: {morena_rp}")
    print(f"  TOTAL: {morena_total}")
    
    print(f"\n¿Por qué {morena_total} en vez de ~252?")
    print(f"Revisa los [DEBUG CAP CALCULATION] arriba para ver el cálculo exacto de v_nacional")
