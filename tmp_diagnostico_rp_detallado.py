"""
Diagnóstico detallado del reparto RP para encontrar el +1 extra
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.procesar_diputados_v2 import procesar_diputados_v2
import numpy as np

print("\n" + "="*80)
print("DIAGNÓSTICO RP - 400 escaños (200 MR + 200 RP)")
print("="*80)

# Ejecutar con print_debug=True para ver los cálculos internos
resultado = procesar_diputados_v2(
    path_parquet="data/computos_diputados_2024.parquet",
    anio=2024,
    path_siglado="data/siglado-diputados-2024.csv",
    max_seats=400,
    sistema="mixto",
    mr_seats=200,
    rp_seats=200,
    pm_seats=0,
    umbral=0.03,
    max_seats_per_party=None,
    sobrerrepresentacion=None,
    aplicar_topes=False,
    quota_method="hare",
    divisor_method=None,
    usar_coaliciones=False,
    votos_redistribuidos=None,
    seed=42,
    print_debug=True  # ← Ver detalles internos
)

print("\n" + "="*80)
print("RESULTADO FINAL:")
print("="*80)

for partido in ['MORENA', 'PAN', 'PRI', 'MC', 'PT', 'PVEM']:
    if partido in resultado['tot']:
        mr = resultado['mr'].get(partido, 0)
        rp = resultado['rp'].get(partido, 0)
        total = resultado['tot'].get(partido, 0)
        print(f"{partido:8} -> MR: {mr:3}, RP: {rp:3}, TOTAL: {total:3}")

print(f"\nTotal MR: {sum(resultado['mr'].values())}")
print(f"Total RP: {sum(resultado['rp'].values())}")
print(f"Total:    {sum(resultado['tot'].values())}")

# Verificar si hay información sobre el cálculo RP en meta
if 'meta' in resultado:
    meta = resultado['meta']
    if 'rp_calculation' in meta:
        print("\n" + "="*80)
        print("DETALLE CÁLCULO RP:")
        print("="*80)
        rp_calc = meta['rp_calculation']
        print(f"Método: {rp_calc.get('method', 'N/A')}")
        print(f"Escaños RP a repartir: {rp_calc.get('seats_to_assign', 'N/A')}")
