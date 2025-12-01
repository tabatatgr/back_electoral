"""Test rápido: verificar que MR + RP = TOTAL después del fix"""
import importlib
import sys

# Forzar reload del módulo
if 'engine.procesar_diputados_v2' in sys.modules:
    importlib.reload(sys.modules['engine.procesar_diputados_v2'])

from engine.procesar_diputados_v2 import procesar_diputados_v2

print("🧪 Test: 75MR/25RP SIN TOPES")
print("="*60)

r = procesar_diputados_v2(
    path_parquet='data/computos_diputados_2024.parquet',
    anio=2024,
    max_seats=500,
    mr_seats=375,
    rp_seats=125,
    usar_coaliciones=True,
    aplicar_topes=False,
    print_debug=False
)

morena_mr = r['mr']['MORENA']
morena_rp = r['rp']['MORENA']
morena_tot = r['tot']['MORENA']
suma = morena_mr + morena_rp

print(f"MORENA:")
print(f"  MR:    {morena_mr}")
print(f"  RP:    {morena_rp}")
print(f"  TOTAL: {morena_tot}")
print(f"  MR+RP: {suma}")
print()

if suma == morena_tot:
    print("✅ ¡ÉXITO! MR + RP = TOTAL")
else:
    print(f"❌ FALLO: MR + RP ({suma}) ≠ TOTAL ({morena_tot})")
    print(f"   Diferencia: {morena_tot - suma}")
