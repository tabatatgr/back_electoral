"""
Probar motor DIRECTO con seed=42 para ver si cambia el resultado
"""
from engine.procesar_diputados_v2 import procesar_diputados_v2

anio = 2024
escanos_totales = 400
mr_escanos = 200
rp_escanos = 200
path_parquet = f'data/computos_diputados_{anio}.parquet'
path_siglado = f'data/siglado-diputados-{anio}.csv'

print("="*80)
print("PRUEBA: Motor directo CON seed=42")
print("="*80)
print()

resultado_sin_seed = procesar_diputados_v2(
    path_parquet=path_parquet,
    path_siglado=path_siglado,
    anio=anio,
    max_seats=escanos_totales,
    mr_seats=mr_escanos,
    rp_seats=rp_escanos,
    usar_coaliciones=False,
    aplicar_topes=False
    # SIN seed
)

resultado_con_seed = procesar_diputados_v2(
    path_parquet=path_parquet,
    path_siglado=path_siglado,
    anio=anio,
    max_seats=escanos_totales,
    mr_seats=mr_escanos,
    rp_seats=rp_escanos,
    usar_coaliciones=False,
    aplicar_topes=False,
    seed=42  # CON seed
)

print("SIN seed:")
print(f"  MORENA MR: {resultado_sin_seed['mr'].get('MORENA', 0)}")
print(f"  MORENA RP: {resultado_sin_seed['rp'].get('MORENA', 0)}")
print(f"  MORENA TOTAL: {resultado_sin_seed['tot'].get('MORENA', 0)}")
print()

print("CON seed=42:")
print(f"  MORENA MR: {resultado_con_seed['mr'].get('MORENA', 0)}")
print(f"  MORENA RP: {resultado_con_seed['rp'].get('MORENA', 0)}")
print(f"  MORENA TOTAL: {resultado_con_seed['tot'].get('MORENA', 0)}")
print()

if resultado_sin_seed['tot'].get('MORENA') == resultado_con_seed['tot'].get('MORENA'):
    print("✅ Seed NO afecta el resultado (ambos iguales)")
else:
    print("⚠️ Seed SÍ afecta el resultado (diferentes)")

print()
print("CSV esperado: MORENA MR=163, RP=93, TOTAL=256")
print()
print("="*80)
