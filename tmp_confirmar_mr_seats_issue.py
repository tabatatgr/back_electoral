"""
Script para confirmar el papel de mr_seats en el cálculo
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.procesar_diputados_v2 import procesar_diputados_v2

# PRUEBA 1: SIN coaliciones, mr_seats=None (comportamiento API actual)
print("\n" + "="*80)
print("PRUEBA 1: SIN coaliciones, mr_seats=None")
print("="*80)

resultado1 = procesar_diputados_v2(
    path_parquet="data/computos_diputados_2024.parquet",
    anio=2024,
    path_siglado="data/siglado-diputados-2024.csv",
    max_seats=500,
    sistema="mixto",
    mr_seats=None,  # ← API pasa None para vigente
    rp_seats=200,
    pm_seats=0,
    umbral=0.03,
    max_seats_per_party=300,
    sobrerrepresentacion=None,
    aplicar_topes=False,
    quota_method="hare",
    divisor_method=None,
    usar_coaliciones=False,
    votos_redistribuidos=None,
    seed=42,
    print_debug=False
)

print(f"\nRESULTADO CON mr_seats=None:")
print(f"MORENA: MR={resultado1['mr'].get('MORENA', 0)}, RP={resultado1['rp'].get('MORENA', 0)}, TOTAL={resultado1['tot'].get('MORENA', 0)}")

# PRUEBA 2: SIN coaliciones, mr_seats=300 (valor explícito)
print("\n" + "="*80)
print("PRUEBA 2: SIN coaliciones, mr_seats=300")
print("="*80)

resultado2 = procesar_diputados_v2(
    path_parquet="data/computos_diputados_2024.parquet",
    anio=2024,
    path_siglado="data/siglado-diputados-2024.csv",
    max_seats=500,
    sistema="mixto",
    mr_seats=300,  # ← Forzar 300 MR
    rp_seats=200,
    pm_seats=0,
    umbral=0.03,
    max_seats_per_party=300,
    sobrerrepresentacion=None,
    aplicar_topes=False,
    quota_method="hare",
    divisor_method=None,
    usar_coaliciones=False,
    votos_redistribuidos=None,
    seed=42,
    print_debug=False
)

print(f"\nRESULTADO CON mr_seats=300:")
print(f"MORENA: MR={resultado2['mr'].get('MORENA', 0)}, RP={resultado2['rp'].get('MORENA', 0)}, TOTAL={resultado2['tot'].get('MORENA', 0)}")

# COMPARACIÓN
print("\n" + "="*80)
print("COMPARACIÓN:")
print("="*80)
print(f"CSV esperado:   MORENA TOTAL = 256 (MR=163, RP=93)")
print(f"Con None:       MORENA TOTAL = {resultado1['tot'].get('MORENA', 0)} (MR={resultado1['mr'].get('MORENA', 0)}, RP={resultado1['rp'].get('MORENA', 0)})")
print(f"Con 300:        MORENA TOTAL = {resultado2['tot'].get('MORENA', 0)} (MR={resultado2['mr'].get('MORENA', 0)}, RP={resultado2['rp'].get('MORENA', 0)})")

if resultado2['tot'].get('MORENA', 0) == 256 and resultado2['mr'].get('MORENA', 0) == 163:
    print("\n✅ mr_seats=300 PRODUCE EL RESULTADO CORRECTO (MR=163, RP=93, TOTAL=256)")
elif resultado2['tot'].get('MORENA', 0) == 257 and resultado2['mr'].get('MORENA', 0) == 163:
    print("\n⚠️  mr_seats=300 produce MR correcto (163) pero RP incorrecto (94 vs 93)")
else:
    print(f"\n❌ mr_seats=300 no produce el resultado esperado")

# CONCLUSIÓN
print("\n" + "="*80)
print("CONCLUSIÓN:")
print("="*80)
if resultado2['tot'].get('MORENA', 0) == 256:
    print("🎯 CONFIRMADO: El problema es que la API pasa mr_seats=None en vez de mr_seats=300")
    print("\nSOLUCIÓN:")
    print("   En main.py, para el plan 'vigente', debe establecerse:")
    print("   mr_seats_final = 300  (en vez de None)")
elif resultado2['tot'].get('MORENA', 0) == 257:
    print("🎯 mr_seats=300 arregla el MR pero sigue habiendo +1 RP")
    print("   Hay otro problema adicional con el reparto RP")
else:
    print("⚠️  Investigar más: el patrón no coincide")
