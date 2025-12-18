"""
Script para confirmar que el problema de +1 RP es por max_seats_per_party=300
siendo aplicado incluso cuando aplicar_topes=False
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.procesar_diputados_v2 import procesar_diputados_v2

# PRUEBA 1: SIN coaliciones, SIN topes (max_seats_per_party=None)
print("\n" + "="*80)
print("PRUEBA 1: SIN coaliciones, aplicar_topes=False, max_seats_per_party=None")
print("="*80)

resultado1 = procesar_diputados_v2(
    path_parquet="data/computos_diputados_2024.parquet",
    anio=2024,
    path_siglado="data/siglado-diputados-2024.csv",
    max_seats=500,
    sistema="mixto",
    mr_seats=None,
    rp_seats=200,
    pm_seats=0,
    umbral=0.03,
    max_seats_per_party=None,  # ← SIN tope
    sobrerrepresentacion=None,
    aplicar_topes=False,
    quota_method="hare",
    divisor_method=None,
    usar_coaliciones=False,
    votos_redistribuidos=None,
    seed=42,
    print_debug=False
)

print(f"\nRESULTADO CON max_seats_per_party=None:")
print(f"MORENA: MR={resultado1['mr'].get('MORENA', 0)}, RP={resultado1['rp'].get('MORENA', 0)}, TOTAL={resultado1['tot'].get('MORENA', 0)}")

# PRUEBA 2: SIN coaliciones, CON max_seats_per_party=300 (como en la API)
print("\n" + "="*80)
print("PRUEBA 2: SIN coaliciones, aplicar_topes=False, max_seats_per_party=300")
print("="*80)

resultado2 = procesar_diputados_v2(
    path_parquet="data/computos_diputados_2024.parquet",
    anio=2024,
    path_siglado="data/siglado-diputados-2024.csv",
    max_seats=500,
    sistema="mixto",
    mr_seats=None,
    rp_seats=200,
    pm_seats=0,
    umbral=0.03,
    max_seats_per_party=300,  # ← CON tope de 300
    sobrerrepresentacion=None,
    aplicar_topes=False,
    quota_method="hare",
    divisor_method=None,
    usar_coaliciones=False,
    votos_redistribuidos=None,
    seed=42,
    print_debug=False
)

print(f"\nRESULTADO CON max_seats_per_party=300:")
print(f"MORENA: MR={resultado2['mr'].get('MORENA', 0)}, RP={resultado2['rp'].get('MORENA', 0)}, TOTAL={resultado2['tot'].get('MORENA', 0)}")

# COMPARACIÓN
print("\n" + "="*80)
print("COMPARACIÓN:")
print("="*80)
print(f"CSV esperado:  MORENA TOTAL = 256 (MR=163, RP=93)")
print(f"Con None:      MORENA TOTAL = {resultado1['tot'].get('MORENA', 0)} (MR={resultado1['mr'].get('MORENA', 0)}, RP={resultado1['rp'].get('MORENA', 0)})")
print(f"Con 300:       MORENA TOTAL = {resultado2['tot'].get('MORENA', 0)} (MR={resultado2['mr'].get('MORENA', 0)}, RP={resultado2['rp'].get('MORENA', 0)})")

if resultado1['tot'].get('MORENA', 0) == 256:
    print("\n✅ max_seats_per_party=None PRODUCE EL RESULTADO CORRECTO (256)")
else:
    print(f"\n❌ max_seats_per_party=None produce {resultado1['tot'].get('MORENA', 0)}, esperado 256")

if resultado2['tot'].get('MORENA', 0) == 257:
    print("✅ max_seats_per_party=300 PRODUCE EL ERROR (+1 RP) → TOTAL 257")
else:
    print(f"❌ max_seats_per_party=300 produce {resultado2['tot'].get('MORENA', 0)}, esperado 257 (error conocido)")

# CONCLUSIÓN
print("\n" + "="*80)
print("CONCLUSIÓN:")
print("="*80)
if resultado1['tot'].get('MORENA', 0) == 256 and resultado2['tot'].get('MORENA', 0) == 257:
    print("🎯 CONFIRMADO: El problema es que la API pasa max_seats_per_party=300")
    print("   incluso cuando aplicar_topes=False.")
    print("\nSOLUCIÓN:")
    print("   En main.py, cuando aplicar_topes=False, debe establecerse:")
    print("   max_seats_per_party_final = None")
else:
    print("⚠️  Los resultados no coinciden con el patrón esperado. Investigar más.")
