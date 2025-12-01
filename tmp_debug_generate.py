"""
Debug: Ver qué está devolviendo el script generate_escenarios_morena
para la configuración específica 2024 / 500 / 50MR-50RP
"""
from engine.procesar_diputados_v2 import procesar_diputados_v2

print("="*80)
print("DEBUG: Verificando resultados 2024 con 500 escaños (250 MR + 250 RP)")
print("="*80)

# Configuración exacta del script generate_escenarios_morena
magnitud = 500
mr_seats = 250  # 50%
rp_seats = 250  # 50%

print(f"\nConfiguración: {magnitud} escaños ({mr_seats} MR + {rp_seats} RP)")

# CON coalición
print("\n[1/2] Llamando procesar_diputados_v2 CON usar_coaliciones=True...")
resultado_con = procesar_diputados_v2(
    path_parquet='data/computos_diputados_2024.parquet',
    anio=2024,
    path_siglado='data/siglado-diputados-2024.csv',
    max_seats=magnitud,
    sistema='mixto',
    mr_seats=mr_seats,
    rp_seats=rp_seats,
    umbral=0.03,
    quota_method='hare',
    usar_coaliciones=True,  # <-- CON coalición
    print_debug=False
)

print("\nResultado CON coalición:")
print(f"  MORENA: {resultado_con['tot'].get('MORENA', 0)} escaños")
print(f"  PT:     {resultado_con['tot'].get('PT', 0)} escaños")
print(f"  PVEM:   {resultado_con['tot'].get('PVEM', 0)} escaños")
coalicion_con = resultado_con['tot'].get('MORENA', 0) + resultado_con['tot'].get('PT', 0) + resultado_con['tot'].get('PVEM', 0)
print(f"  COALICIÓN TOTAL: {coalicion_con} escaños")

# SIN coalición
print("\n[2/2] Llamando procesar_diputados_v2 CON usar_coaliciones=False...")
resultado_sin = procesar_diputados_v2(
    path_parquet='data/computos_diputados_2024.parquet',
    anio=2024,
    path_siglado='data/siglado-diputados-2024.csv',
    max_seats=magnitud,
    sistema='mixto',
    mr_seats=mr_seats,
    rp_seats=rp_seats,
    umbral=0.03,
    quota_method='hare',
    usar_coaliciones=False,  # <-- SIN coalición
    print_debug=False
)

print("\nResultado SIN coalición:")
print(f"  MORENA: {resultado_sin['tot'].get('MORENA', 0)} escaños")
print(f"  PT:     {resultado_sin['tot'].get('PT', 0)} escaños")
print(f"  PVEM:   {resultado_sin['tot'].get('PVEM', 0)} escaños")
coalicion_sin = resultado_sin['tot'].get('MORENA', 0) + resultado_sin['tot'].get('PT', 0) + resultado_sin['tot'].get('PVEM', 0)
print(f"  COALICIÓN TOTAL: {coalicion_sin} escaños")

print("\n" + "="*80)
print("COMPARACIÓN")
print("="*80)
print(f"MORENA CON coalición: {resultado_con['tot'].get('MORENA', 0)} escaños")
print(f"MORENA SIN coalición: {resultado_sin['tot'].get('MORENA', 0)} escaños")
print(f"Diferencia: {resultado_con['tot'].get('MORENA', 0) - resultado_sin['tot'].get('MORENA', 0)}")

print(f"\nBloque CON coalición: {coalicion_con} escaños")
print(f"Bloque SIN coalición: {coalicion_sin} escaños")
print(f"Diferencia: {coalicion_con - coalicion_sin}")

if resultado_con['tot'].get('MORENA', 0) == resultado_sin['tot'].get('MORENA', 0):
    print("\n[ERROR] MORENA tiene los mismos escaños en ambos casos!")
    print("        Esto indica que usar_coaliciones NO está funcionando con 250 MR")
else:
    print("\n[OK] MORENA tiene diferentes escaños. La corrección funciona.")
