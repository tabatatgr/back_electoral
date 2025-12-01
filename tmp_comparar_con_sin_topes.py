"""
Comparación lado a lado: CON topes vs SIN topes
Escenario: 2024 | 500 escaños | 75MR/25RP | CON coalición
"""
from engine.procesar_diputados_v2 import procesar_diputados_v2

print("="*80)
print("COMPARACIÓN: 2024 | 500 escaños | 75MR/25RP | CON coalición")
print("="*80)

# CON topes
print("\n🔒 CON TOPES CONSTITUCIONALES (8% + 300 max):")
print("-"*80)

resultado_con = procesar_diputados_v2(
    path_parquet='data/computos_diputados_2024.parquet',
    anio=2024,
    max_seats=500,
    mr_seats=375,
    rp_seats=125,
    usar_coaliciones=True,
    aplicar_topes=True,  # CON topes
    print_debug=False
)

morena_con = {
    'MR': resultado_con['mr']['MORENA'],
    'RP': resultado_con['rp']['MORENA'],
    'TOTAL': resultado_con['tot']['MORENA']
}

total_votos = sum(resultado_con['votos'].values())
pct_votos = (resultado_con['votos']['MORENA'] / total_votos * 100)

print(f"MORENA:")
print(f"  % Votos:        {pct_votos:.2f}%")
print(f"  MR asignados:   {morena_con['MR']}")
print(f"  RP asignados:   {morena_con['RP']}")
print(f"  TOTAL:          {morena_con['TOTAL']} ({morena_con['TOTAL']/500*100:.1f}%)")
print(f"  MR + RP:        {morena_con['MR'] + morena_con['RP']}")

# Verificar tope 8%
cap_8pct = int((pct_votos/100 + 0.08) * 500)
print(f"\n  Tope 8%:        {cap_8pct} escaños")
print(f"  ¿Topado?        {'SÍ ✅' if morena_con['TOTAL'] == cap_8pct else 'NO ❌'}")

# SIN topes
print("\n\n🔓 SIN TOPES CONSTITUCIONALES (distribución pura):")
print("-"*80)

resultado_sin = procesar_diputados_v2(
    path_parquet='data/computos_diputados_2024.parquet',
    anio=2024,
    max_seats=500,
    mr_seats=375,
    rp_seats=125,
    usar_coaliciones=True,
    aplicar_topes=False,  # SIN topes
    print_debug=False
)

morena_sin = {
    'MR': resultado_sin['mr']['MORENA'],
    'RP': resultado_sin['rp']['MORENA'],
    'TOTAL': resultado_sin['tot']['MORENA']
}

print(f"MORENA:")
print(f"  % Votos:        {pct_votos:.2f}%")
print(f"  MR asignados:   {morena_sin['MR']}")
print(f"  RP asignados:   {morena_sin['RP']}")
print(f"  TOTAL:          {morena_sin['TOTAL']} ({morena_sin['TOTAL']/500*100:.1f}%)")
print(f"  MR + RP:        {morena_sin['MR'] + morena_sin['RP']}")

print("\n\n📊 DIFERENCIA:")
print("-"*80)
diff_mr = morena_sin['MR'] - morena_con['MR']
diff_rp = morena_sin['RP'] - morena_con['RP']
diff_tot = morena_sin['TOTAL'] - morena_con['TOTAL']

print(f"  MR:   {morena_sin['MR']:3d} - {morena_con['MR']:3d} = {diff_mr:+4d} escaños")
print(f"  RP:   {morena_sin['RP']:3d} - {morena_con['RP']:3d} = {diff_rp:+4d} escaños")
print(f"  TOT:  {morena_sin['TOTAL']:3d} - {morena_con['TOTAL']:3d} = {diff_tot:+4d} escaños")

print(f"\n  El tope del 8% redujo MORENA en {abs(diff_tot)} escaños")
print(f"  Pasó de {morena_sin['TOTAL']/500*100:.1f}% a {morena_con['TOTAL']/500*100:.1f}% de la cámara")

print("\n" + "="*80)
