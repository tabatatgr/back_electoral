"""
Test para verificar que 50MR/50RP y 75MR/25RP dan resultados diferentes después del fix
"""
from engine.procesar_diputados_v2 import procesar_diputados_v2
import numpy as np

# Ejecutar simulación con 50MR/50RP
print("="*60)
print("PRUEBA 1: 250MR / 250RP (50/50)")
print("="*60)

resultado_50 = procesar_diputados_v2(
    path_parquet='data/computos_diputados_2024.parquet',
    anio=2024,
    path_siglado='data/siglado-diputados-2024.csv',
    max_seats=500,
    sistema='mixto',
    mr_seats=250,
    rp_seats=250,
    umbral=0.03,
    usar_coaliciones=True,  # CON coalición (escenario real)
    print_debug=False
)

morena_mr_50 = resultado_50['mr'].get('MORENA', 0)
morena_rp_50 = resultado_50['rp'].get('MORENA', 0)
morena_tot_50 = resultado_50['tot'].get('MORENA', 0)

print(f"\nMORENA EN 50MR/50RP:")
print(f"  MR: {morena_mr_50}")
print(f"  RP: {morena_rp_50}")
print(f"  TOTAL: {morena_tot_50}")
print(f"  Tope teórico (+8%): 252")

# Ejecutar simulación con 75MR/25RP
print("\n" + "="*60)
print("PRUEBA 2: 375MR / 125RP (75/25)")
print("="*60)

resultado_75 = procesar_diputados_v2(
    path_parquet='data/computos_diputados_2024.parquet',
    anio=2024,
    path_siglado='data/siglado-diputados-2024.csv',
    max_seats=500,
    sistema='mixto',
    mr_seats=375,
    rp_seats=125,
    umbral=0.03,
    usar_coaliciones=True,  # CON coalición (escenario real)
    print_debug=False
)

morena_mr_75 = resultado_75['mr'].get('MORENA', 0)
morena_rp_75 = resultado_75['rp'].get('MORENA', 0)
morena_tot_75 = resultado_75['tot'].get('MORENA', 0)

print(f"\nMORENA EN 75MR/25RP:")
print(f"  MR: {morena_mr_75}")
print(f"  RP: {morena_rp_75}")
print(f"  TOTAL: {morena_tot_75}")
print(f"  Tope teórico (+8%): 252")

# Comparación
print("\n" + "="*60)
print("COMPARACIÓN")
print("="*60)

print(f"\n50/50 vs 75/25:")
print(f"  MR:    {morena_mr_50:3d}  vs  {morena_mr_75:3d}  (Δ = {morena_mr_75 - morena_mr_50:+d})")
print(f"  RP:    {morena_rp_50:3d}  vs  {morena_rp_75:3d}  (Δ = {morena_rp_75 - morena_rp_50:+d})")
print(f"  TOTAL: {morena_tot_50:3d}  vs  {morena_tot_75:3d}  (Δ = {morena_tot_75 - morena_tot_50:+d})")

if morena_tot_50 == morena_tot_75 and morena_tot_50 == 252:
    print(f"\n✓ CORRECTO: TOTAL IDÉNTICO ({morena_tot_50}) - TOPE CONSTITUCIONAL")
    print(f"  Como dijo el usuario: 'si estás topado por 8 puntos,")
    print(f"  da igual 50/50 o 75/25, el resultado se aplana al tope'")
    print(f"  Esto es el COMPORTAMIENTO ESPERADO y CONSTITUCIONAL.")
elif morena_tot_50 == morena_tot_75:
    print(f"\n⚠️  PROBLEMA: TOTAL IDÉNTICO ({morena_tot_50}) pero NO en el tope")
else:
    print(f"\n✓ Los totales son diferentes (no topado)")

# Verificar que ninguno excede el tope
if morena_tot_50 > 252:
    print(f"\n✗ ERROR 50/50: Excede tope por {morena_tot_50 - 252} escaños")
else:
    print(f"\n✓ OK 50/50: Respeta tope de 252")

if morena_tot_75 > 252:
    print(f"✗ ERROR 75/25: Excede tope por {morena_tot_75 - 252} escaños")
else:
    print(f"✓ OK 75/25: Respeta tope de 252")
