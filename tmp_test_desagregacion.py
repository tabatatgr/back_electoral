"""
Test: Verificar desagregación automática de votos cuando usar_coaliciones=False
"""
from engine.procesar_diputados_v2 import procesar_diputados_v2

print("="*80)
print("TEST: Desagregación Automática de Votos")
print("="*80)

# CON coalición (votos originales)
print("\n[1/2] CON coalición (usar_coaliciones=True)...")
resultado_con = procesar_diputados_v2(
    path_parquet='data/computos_diputados_2024.parquet',
    anio=2024,
    path_siglado='data/siglado-diputados-2024.csv',
    max_seats=500,
    sistema='mixto',
    mr_seats=300,  # Usar 300 real
    rp_seats=200,
    umbral=0.03,
    quota_method='hare',
    usar_coaliciones=True,
    print_debug=True  # Ver logs de desagregación
)

print("\n" + "="*80)
print("RESULTADOS CON COALICIÓN")
print("="*80)
print(f"MORENA: {resultado_con['tot']['MORENA']} total ({resultado_con['mr']['MORENA']} MR + {resultado_con['rp']['MORENA']} RP)")
print(f"PT:     {resultado_con['tot']['PT']} total ({resultado_con['mr']['PT']} MR + {resultado_con['rp']['PT']} RP)")
print(f"PVEM:   {resultado_con['tot']['PVEM']} total ({resultado_con['mr']['PVEM']} MR + {resultado_con['rp']['PVEM']} RP)")
bloque_con = resultado_con['tot']['MORENA'] + resultado_con['tot']['PT'] + resultado_con['tot']['PVEM']
print(f"BLOQUE: {bloque_con} escaños ({(bloque_con/500)*100:.1f}%)")

# SIN coalición (votos desagregados automáticamente)
print("\n[2/2] SIN coalición (usar_coaliciones=False) - DESAGREGANDO VOTOS...")
resultado_sin = procesar_diputados_v2(
    path_parquet='data/computos_diputados_2024.parquet',
    anio=2024,
    path_siglado='data/siglado-diputados-2024.csv',
    max_seats=500,
    sistema='mixto',
    mr_seats=300,  # Usar 300 real
    rp_seats=200,
    umbral=0.03,
    quota_method='hare',
    usar_coaliciones=False,
    print_debug=True  # Ver logs de desagregación
)

print("\n" + "="*80)
print("RESULTADOS SIN COALICIÓN (competencia separada)")
print("="*80)
print(f"MORENA: {resultado_sin['tot']['MORENA']} total ({resultado_sin['mr']['MORENA']} MR + {resultado_sin['rp']['MORENA']} RP)")
print(f"PT:     {resultado_sin['tot']['PT']} total ({resultado_sin['mr']['PT']} MR + {resultado_sin['rp']['PT']} RP)")
print(f"PVEM:   {resultado_sin['tot']['PVEM']} total ({resultado_sin['mr']['PVEM']} MR + {resultado_sin['rp']['PVEM']} RP)")
bloque_sin = resultado_sin['tot']['MORENA'] + resultado_sin['tot']['PT'] + resultado_sin['tot']['PVEM']
print(f"BLOQUE: {bloque_sin} escaños ({(bloque_sin/500)*100:.1f}%)")

print("\n" + "="*80)
print("COMPARACION")
print("="*80)
print(f"MORENA: {resultado_con['tot']['MORENA']} CON -> {resultado_sin['tot']['MORENA']} SIN (Delta={resultado_sin['tot']['MORENA']-resultado_con['tot']['MORENA']:+d})")
print(f"PT:     {resultado_con['tot']['PT']} CON -> {resultado_sin['tot']['PT']} SIN (Delta={resultado_sin['tot']['PT']-resultado_con['tot']['PT']:+d})")
print(f"PVEM:   {resultado_con['tot']['PVEM']} CON -> {resultado_sin['tot']['PVEM']} SIN (Delta={resultado_sin['tot']['PVEM']-resultado_con['tot']['PVEM']:+d})")
print(f"BLOQUE: {bloque_con} CON -> {bloque_sin} SIN (Delta={bloque_sin-bloque_con:+d})")

if resultado_sin['tot']['MORENA'] != resultado_con['tot']['MORENA']:
    print("\n✅ ÉXITO: Los escaños de MORENA SON DIFERENTES")
    print("   La desagregación de votos está funcionando")
else:
    print("\n❌ PROBLEMA: Los escaños de MORENA siguen siendo iguales")
    print("   La desagregación no está teniendo efecto")
