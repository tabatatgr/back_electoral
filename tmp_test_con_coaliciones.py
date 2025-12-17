"""
Test CON COALICIONES para ver si da el resultado correcto (252 escaños)
"""
import sys
sys.path.insert(0, '.')

import numpy as np
import pandas as pd
from engine.procesar_diputados_v2 import procesar_diputados_v2

print("=" * 80)
print("TEST: MORENA CON COALICIONES (debería dar 252 escaños con 8%)")
print("=" * 80)

# Llamar con usar_coaliciones=TRUE
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
    max_seats_per_party=None,
    sobrerrepresentacion=8.0,   # CON cláusula del 8%
    aplicar_topes=True,
    quota_method=None,
    divisor_method="d_hondt",
    usar_coaliciones=True,  # ← CON COALICIONES
    votos_redistribuidos=None,
    print_debug=False  # Desactivar debug para ver solo el resultado
)

print("\n" + "=" * 80)
print("RESULTADO CON COALICIONES:")
print("=" * 80)

if 'tot' in resultado:
    morena_total = resultado['tot'].get('MORENA', 0)
    morena_mr = resultado['mr'].get('MORENA', 0) if 'mr' in resultado else 0
    morena_rp = resultado['rp'].get('MORENA', 0) if 'rp' in resultado else 0
    
    print(f"\nMORENA:")
    print(f"  MR: {morena_mr}")
    print(f"  RP: {morena_rp}")
    print(f"  TOTAL: {morena_total}")
    
    if morena_total == 252:
        print(f"\n✅ CORRECTO: Da exactamente 252 escaños")
    elif 250 <= morena_total <= 254:
        print(f"\n✅ CASI CORRECTO: Da ~252 escaños (diferencia: {morena_total - 252})")
    else:
        print(f"\n❌ INCORRECTO: Esperado ~252, obtenido {morena_total}")
