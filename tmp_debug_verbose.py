"""
Debug con print_debug=True para ver qué pasa
"""
from engine.procesar_diputados_v2 import procesar_diputados_v2

print("="*80)
print("DEBUG CON print_debug=True")
print("="*80)

# SIN coalición con debug
print("\n[PRUEBA] SIN coalición (usar_coaliciones=False)...")
resultado_sin = procesar_diputados_v2(
    path_parquet='data/computos_diputados_2024.parquet',
    anio=2024,
    path_siglado='data/siglado-diputados-2024.csv',
    max_seats=500,
    sistema='mixto',
    mr_seats=250,
    rp_seats=250,
    umbral=0.03,
    quota_method='hare',
    usar_coaliciones=False,
    print_debug=True  # <-- ACTIVAR DEBUG
)

print("\n" + "="*80)
print(f"RESULTADO: MORENA={resultado_sin['tot'].get('MORENA', 0)} escaños")
print("="*80)
