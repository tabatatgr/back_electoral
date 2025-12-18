"""
Llamada DIRECTA a procesar_diputados_v2 para reproducir el CSV
con EXACTAMENTE los mismos parámetros que usa tmp_generate_escenarios_sin_topes.py
"""
from engine.procesar_diputados_v2 import procesar_diputados_v2

# Parámetros idénticos al script generador
anio = 2024
escanos_totales = 400
mr_escanos = 200
rp_escanos = 200
path_parquet = f'data/computos_diputados_{anio}.parquet'
path_siglado = f'data/siglado-diputados-{anio}.csv'

print("="*80)
print("PRUEBA DIRECTA: Sin coaliciones, sin topes")
print("="*80)
print(f"Parámetros del script generador:")
print(f"  anio: {anio}")
print(f"  max_seats: {escanos_totales}")
print(f"  mr_seats: {mr_escanos}")
print(f"  rp_seats: {rp_escanos}")
print(f"  usar_coaliciones: False")
print(f"  aplicar_topes: False")
print(f"  (NO se pasan: quota_method, divisor_method, seed, umbral)")
print()

# Llamada idéntica al script generador
resultado = procesar_diputados_v2(
    path_parquet=path_parquet,
    path_siglado=path_siglado,
    anio=anio,
    max_seats=escanos_totales,
    mr_seats=mr_escanos,
    rp_seats=rp_escanos,
    usar_coaliciones=False,
    aplicar_topes=False
    # NO pasar: quota_method, divisor_method, seed, umbral, print_debug
)

print("RESULTADO:")
print(f"  MORENA MR: {resultado['mr'].get('MORENA', 0)}")
print(f"  MORENA RP: {resultado['rp'].get('MORENA', 0)}")
print(f"  MORENA TOTAL: {resultado['tot'].get('MORENA', 0)}")
print()
print(f"CSV esperado:")
print(f"  MORENA MR: 163")
print(f"  MORENA RP: 93")
print(f"  MORENA TOTAL: 256")
print()

morena_mr = resultado['mr'].get('MORENA', 0)
morena_rp = resultado['rp'].get('MORENA', 0)
morena_total = resultado['tot'].get('MORENA', 0)

if morena_mr == 163 and morena_rp == 93 and morena_total == 256:
    print("✅ COINCIDE EXACTAMENTE CON CSV")
else:
    print(f"❌ DISCREPANCIA:")
    print(f"   MR: {morena_mr} vs 163 (diff: {morena_mr - 163:+d})")
    print(f"   RP: {morena_rp} vs 93 (diff: {morena_rp - 93:+d})")
    print(f"   TOTAL: {morena_total} vs 256 (diff: {morena_total - 256:+d})")

print()
print("="*80)
print("AHORA CON COALICIONES")
print("="*80)

resultado_con_coal = procesar_diputados_v2(
    path_parquet=path_parquet,
    path_siglado=path_siglado,
    anio=anio,
    max_seats=escanos_totales,
    mr_seats=mr_escanos,
    rp_seats=rp_escanos,
    usar_coaliciones=True,
    aplicar_topes=False
)

print("RESULTADO CON COALICIONES:")
print(f"  MORENA MR: {resultado_con_coal['mr'].get('MORENA', 0)}")
print(f"  MORENA RP: {resultado_con_coal['rp'].get('MORENA', 0)}")
print(f"  MORENA TOTAL: {resultado_con_coal['tot'].get('MORENA', 0)}")
print()
print(f"CSV esperado:")
print(f"  MORENA MR: 161")
print(f"  MORENA RP: 87")
print(f"  MORENA TOTAL: 248")
print()

morena_mr_coal = resultado_con_coal['mr'].get('MORENA', 0)
morena_rp_coal = resultado_con_coal['rp'].get('MORENA', 0)
morena_total_coal = resultado_con_coal['tot'].get('MORENA', 0)

if morena_mr_coal == 161 and morena_rp_coal == 87 and morena_total_coal == 248:
    print("✅ COINCIDE EXACTAMENTE CON CSV")
else:
    print(f"❌ DISCREPANCIA:")
    print(f"   MR: {morena_mr_coal} vs 161 (diff: {morena_mr_coal - 161:+d})")
    print(f"   RP: {morena_rp_coal} vs 87 (diff: {morena_rp_coal - 87:+d})")
    print(f"   TOTAL: {morena_total_coal} vs 248 (diff: {morena_total_coal - 248:+d})")

print()
print("="*80)
