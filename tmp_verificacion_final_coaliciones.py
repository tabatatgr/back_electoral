"""
Verificación final: ¿Qué números del CSV esperas vs qué devuelve la API?
"""
import json

print("="*80)
print("VERIFICACIÓN: CSV vs API (ambos casos)")
print("="*80)
print()

# CSV SIN TOPES
print("📄 CSV ESPERADO (2024, 400, 50MR_50RP):")
print("-" * 80)
print("CON coaliciones, SIN topes:")
print("  MORENA: MR=161, RP=87, TOTAL=248, COALICIÓN=282")
print()
print("SIN coaliciones, SIN topes:")
print("  MORENA: MR=163, RP=93, TOTAL=256, COALICIÓN=284")
print()
print("-" * 80)
print()

# API actual
with open('tmp_debug_sin_coal_sin_topes.json', 'r', encoding='utf-8') as f:
    sin_coal = json.load(f)
with open('tmp_debug_con_coal_sin_topes.json', 'r', encoding='utf-8') as f:
    con_coal = json.load(f)

print("🌐 API ACTUAL:")
print("-" * 80)

# CON coaliciones
morena_con = next(x for x in con_coal['resultados'] if x['partido'] == 'MORENA')
pt_con = next(x for x in con_coal['resultados'] if x['partido'] == 'PT')
pvem_con = next(x for x in con_coal['resultados'] if x['partido'] == 'PVEM')
coal_con = morena_con['total'] + pt_con['total'] + pvem_con['total']

print("CON coaliciones, SIN topes:")
print(f"  MORENA: MR={morena_con['mr']}, RP={morena_con['rp']}, TOTAL={morena_con['total']}, COALICIÓN={coal_con}")

# SIN coaliciones
morena_sin = next(x for x in sin_coal['resultados'] if x['partido'] == 'MORENA')
pt_sin = next(x for x in sin_coal['resultados'] if x['partido'] == 'PT')
pvem_sin = next(x for x in sin_coal['resultados'] if x['partido'] == 'PVEM')
coal_sin = morena_sin['total'] + pt_sin['total'] + pvem_sin['total']

print()
print("SIN coaliciones, SIN topes:")
print(f"  MORENA: MR={morena_sin['mr']}, RP={morena_sin['rp']}, TOTAL={morena_sin['total']}, COALICIÓN={coal_sin}")
print()
print("-" * 80)
print()

print("🔍 COMPARACIÓN DETALLADA")
print("="*80)
print()

# CON coaliciones
print("CON COALICIONES:")
print(f"  CSV: MORENA MR=161, RP=87, TOTAL=248")
print(f"  API: MORENA MR={morena_con['mr']}, RP={morena_con['rp']}, TOTAL={morena_con['total']}")
if morena_con['mr'] == 161 and morena_con['rp'] == 87 and morena_con['total'] == 248:
    print("  ✅ COINCIDEN (excepto +1 RP que ya diagnosticamos)")
else:
    print(f"  ❌ DISCREPANCIA:")
    print(f"     MR: {morena_con['mr']} vs 161 (diff: {morena_con['mr']-161:+d})")
    print(f"     RP: {morena_con['rp']} vs 87 (diff: {morena_con['rp']-87:+d})")
    print(f"     TOTAL: {morena_con['total']} vs 248 (diff: {morena_con['total']-248:+d})")

print()
print("SIN COALICIONES:")
print(f"  CSV: MORENA MR=163, RP=93, TOTAL=256")
print(f"  API: MORENA MR={morena_sin['mr']}, RP={morena_sin['rp']}, TOTAL={morena_sin['total']}")
if morena_sin['mr'] == 163 and morena_sin['rp'] == 93 and morena_sin['total'] == 256:
    print("  ✅ COINCIDEN (excepto +1 RP que ya diagnosticamos)")
else:
    print(f"  ❌ DISCREPANCIA:")
    print(f"     MR: {morena_sin['mr']} vs 163 (diff: {morena_sin['mr']-163:+d})")
    print(f"     RP: {morena_sin['rp']} vs 93 (diff: {morena_sin['rp']-93:+d})")
    print(f"     TOTAL: {morena_sin['total']} vs 256 (diff: {morena_sin['total']-256:+d})")

print()
print("="*80)
print("💡 RESUMEN FINAL")
print("="*80)
print()
print("Las diferencias entre CON y SIN coaliciones son ESPERADAS y CORRECTAS:")
print()
print("  MR cambia porque:")
print("    - CON coalición: usa siglado (convenios entre partidos)")
print("    - SIN coalición: usa ganador por votos individuales")
print()
print("  RP cambia porque:")
print("    - Diferentes totales MR → diferentes escaños RP a repartir")
print("    - Distribución proporcional se recalcula con nueva base")
print()
print("Si el frontend muestra números DIFERENTES a estos,")
print("revisa si está enviando correctamente usar_coaliciones=True/False")
print()
print("="*80)
