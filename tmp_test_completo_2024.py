"""
Test completo: Replicar 2024 con reglas normales
300 MR + 200 RP = 500 escaños
Comparar CON y SIN coaliciones
"""
from engine.procesar_diputados_v2 import procesar_diputados_v2

print("="*70)
print("TEST COMPLETO: REPLICAR 2024 CON REGLAS NORMALES")
print("300 MR + 200 RP = 500 escaños totales")
print("="*70)

# ========== SIN COALICIÓN ==========
print("\n[1/2] Procesando SIN coalición...")
print("      (MORENA compite solo, calculando ganadores por votos directos)")

resultado_sin = procesar_diputados_v2(
    path_parquet='data/computos_diputados_2024.parquet',
    anio=2024,
    path_siglado='data/siglado-diputados-2024.csv',
    max_seats=500,
    sistema='mixto',
    mr_seats=300,
    rp_seats=200,
    umbral=0.03,
    quota_method='hare',
    usar_coaliciones=False,
    print_debug=False
)

# ========== CON COALICIÓN ==========
print("\n[2/2] Procesando CON coalición...")
print("      (Convenio MORENA-PT-PVEM según siglado real)")

resultado_con = procesar_diputados_v2(
    path_parquet='data/computos_diputados_2024.parquet',
    anio=2024,
    path_siglado='data/siglado-diputados-2024.csv',
    max_seats=500,
    sistema='mixto',
    mr_seats=300,
    rp_seats=200,
    umbral=0.03,
    quota_method='hare',
    usar_coaliciones=True,
    print_debug=False
)

# ========== RESULTADOS DETALLADOS ==========
print("\n" + "="*70)
print("RESULTADOS DETALLADOS")
print("="*70)

partidos = ['MORENA', 'PT', 'PVEM', 'PAN', 'PRI', 'PRD', 'MC']

print("\n--- SIN COALICIÓN (MORENA compite solo) ---")
print(f"\n{'Partido':<10} {'MR':<6} {'RP':<6} {'TOTAL':<8} {'%':<8}")
print("-" * 45)
total_sin = 0
for partido in partidos:
    mr = resultado_sin['mr'].get(partido, 0)
    rp = resultado_sin['rp'].get(partido, 0)
    tot = resultado_sin['tot'].get(partido, 0)
    pct = (tot / 500) * 100
    total_sin += tot
    print(f"{partido:<10} {mr:<6} {rp:<6} {tot:<8} {pct:>6.2f}%")

print("-" * 45)
print(f"{'TOTAL':<10} {sum(resultado_sin['mr'].values()):<6} {sum(resultado_sin['rp'].values()):<6} {total_sin:<8}")

# Calcular bloque MORENA+PT+PVEM
bloque_sin = resultado_sin['tot']['MORENA'] + resultado_sin['tot']['PT'] + resultado_sin['tot']['PVEM']
print(f"\nBloque MORENA+PT+PVEM: {bloque_sin} ({(bloque_sin/500)*100:.1f}%)")
print(f"  ¿Mayoría simple (>250)?: {'SÍ' if bloque_sin > 250 else 'NO'}")
print(f"  ¿Mayoría calificada (>=334)?: {'SÍ' if bloque_sin >= 334 else 'NO'}")

print("\n--- CON COALICIÓN (Convenio MORENA-PT-PVEM) ---")
print(f"\n{'Partido':<10} {'MR':<6} {'RP':<6} {'TOTAL':<8} {'%':<8}")
print("-" * 45)
total_con = 0
for partido in partidos:
    mr = resultado_con['mr'].get(partido, 0)
    rp = resultado_con['rp'].get(partido, 0)
    tot = resultado_con['tot'].get(partido, 0)
    pct = (tot / 500) * 100
    total_con += tot
    print(f"{partido:<10} {mr:<6} {rp:<6} {tot:<8} {pct:>6.2f}%")

print("-" * 45)
print(f"{'TOTAL':<10} {sum(resultado_con['mr'].values()):<6} {sum(resultado_con['rp'].values()):<6} {total_con:<8}")

# Calcular bloque MORENA+PT+PVEM
bloque_con = resultado_con['tot']['MORENA'] + resultado_con['tot']['PT'] + resultado_con['tot']['PVEM']
print(f"\nBloque MORENA+PT+PVEM: {bloque_con} ({(bloque_con/500)*100:.1f}%)")
print(f"  ¿Mayoría simple (>250)?: {'SÍ' if bloque_con > 250 else 'NO'}")
print(f"  ¿Mayoría calificada (>=334)?: {'SÍ' if bloque_con >= 334 else 'NO'}")

# ========== ANÁLISIS DE DIFERENCIAS ==========
print("\n" + "="*70)
print("ANÁLISIS: IMPACTO DE LA COALICIÓN")
print("="*70)

print("\n1. MAYORÍA RELATIVA (MR - Distritos uninominales)")
print("-" * 50)
print(f"   MORENA:")
print(f"     Sin coalición: {resultado_sin['mr']['MORENA']} distritos")
print(f"     Con coalición: {resultado_con['mr']['MORENA']} distritos")
print(f"     Diferencia:    {resultado_con['mr']['MORENA'] - resultado_sin['mr']['MORENA']:+d} (MORENA cede al convenio)")

print(f"\n   PT:")
print(f"     Sin coalición: {resultado_sin['mr']['PT']} distritos")
print(f"     Con coalición: {resultado_con['mr']['PT']} distritos")
print(f"     Diferencia:    {resultado_con['mr']['PT'] - resultado_sin['mr']['PT']:+d} (gana por convenio)")

print(f"\n   PVEM:")
print(f"     Sin coalición: {resultado_sin['mr']['PVEM']} distritos")
print(f"     Con coalición: {resultado_con['mr']['PVEM']} distritos")
print(f"     Diferencia:    {resultado_con['mr']['PVEM'] - resultado_sin['mr']['PVEM']:+d} (gana por convenio)")

mr_sin_bloque = resultado_sin['mr']['MORENA'] + resultado_sin['mr']['PT'] + resultado_sin['mr']['PVEM']
mr_con_bloque = resultado_con['mr']['MORENA'] + resultado_con['mr']['PT'] + resultado_con['mr']['PVEM']

print(f"\n   BLOQUE (MORENA+PT+PVEM):")
print(f"     Sin coalición: {mr_sin_bloque} distritos")
print(f"     Con coalición: {mr_con_bloque} distritos")
print(f"     Diferencia:    {mr_con_bloque - mr_sin_bloque:+d} (beneficio de sumar votos)")

print("\n2. REPRESENTACIÓN PROPORCIONAL (RP)")
print("-" * 50)
print(f"   MORENA:")
print(f"     Sin coalición: {resultado_sin['rp']['MORENA']} escaños RP")
print(f"     Con coalición: {resultado_con['rp']['MORENA']} escaños RP")
print(f"     Diferencia:    {resultado_con['rp']['MORENA'] - resultado_sin['rp']['MORENA']:+d}")

print("\n3. TOTALES")
print("-" * 50)
print(f"   MORENA individual:")
print(f"     Sin coalición: {resultado_sin['tot']['MORENA']} escaños ({(resultado_sin['tot']['MORENA']/500)*100:.1f}%)")
print(f"     Con coalición: {resultado_con['tot']['MORENA']} escaños ({(resultado_con['tot']['MORENA']/500)*100:.1f}%)")
print(f"     Diferencia:    {resultado_con['tot']['MORENA'] - resultado_sin['tot']['MORENA']:+d}")

print(f"\n   Bloque (MORENA+PT+PVEM):")
print(f"     Sin coalición: {bloque_sin} escaños ({(bloque_sin/500)*100:.1f}%)")
print(f"     Con coalición: {bloque_con} escaños ({(bloque_con/500)*100:.1f}%)")
print(f"     Diferencia:    {bloque_con - bloque_sin:+d}")

# ========== VALIDACIONES ==========
print("\n" + "="*70)
print("VALIDACIONES")
print("="*70)

checks = [
    ("Total escaños suma 500 (sin coal)", total_sin == 500),
    ("Total escaños suma 500 (con coal)", total_con == 500),
    ("MORENA pierde MR por convenio", resultado_con['mr']['MORENA'] < resultado_sin['mr']['MORENA']),
    ("PT gana MR por convenio", resultado_con['mr']['PT'] > resultado_sin['mr']['PT']),
    ("PVEM gana MR por convenio", resultado_con['mr']['PVEM'] > resultado_sin['mr']['PVEM']),
    ("Bloque gana distritos MR sumando", mr_con_bloque > mr_sin_bloque),
    ("Coalición compensa en RP", resultado_con['rp']['MORENA'] > resultado_sin['rp']['MORENA']),
]

for desc, passed in checks:
    status = "[OK] PASS" if passed else "[X] FAIL"
    print(f"  {status} {desc}")

# ========== COMPARACIÓN CON SIGLADO REAL ==========
print("\n" + "="*70)
print("COMPARACIÓN CON SIGLADO REAL 2024")
print("="*70)

print("\nDistribución MR esperada (del siglado real):")
print("  MORENA: 148 distritos")
print("  PT:     46 distritos")
print("  PVEM:   71 distritos")
print("  TOTAL:  265 distritos (coalición)")

print("\nDistribución MR obtenida (con coalición):")
print(f"  MORENA: {resultado_con['mr']['MORENA']} distritos")
print(f"  PT:     {resultado_con['mr']['PT']} distritos")
print(f"  PVEM:   {resultado_con['mr']['PVEM']} distritos")
print(f"  TOTAL:  {mr_con_bloque} distritos (coalición)")

print("\nDiferencias vs siglado real:")
diff_morena = resultado_con['mr']['MORENA'] - 148
diff_pt = resultado_con['mr']['PT'] - 46
diff_pvem = resultado_con['mr']['PVEM'] - 71
diff_total = mr_con_bloque - 265

print(f"  MORENA: {diff_morena:+d}")
print(f"  PT:     {diff_pt:+d}")
print(f"  PVEM:   {diff_pvem:+d}")
print(f"  TOTAL:  {diff_total:+d}")

if abs(diff_morena) <= 15 and abs(diff_pt) <= 10 and abs(diff_pvem) <= 15:
    print("\n  >> Diferencias aceptables (el siglado tiene lógica de convenio específica)")
else:
    print("\n  [!] Diferencias significativas - revisar lógica de asignación")

print("\n" + "="*70)
print("FIN DEL TEST")
print("="*70)
