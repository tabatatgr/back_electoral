"""
Análisis específico: MR con coaliciones ON vs OFF
"""
import json

print("="*80)
print("ANÁLISIS: MR CON COALICIONES VS SIN COALICIONES")
print("="*80)
print()

# Leer las respuestas guardadas
with open('tmp_debug_sin_coal_sin_topes.json', 'r', encoding='utf-8') as f:
    sin_coal = json.load(f)

with open('tmp_debug_con_coal_sin_topes.json', 'r', encoding='utf-8') as f:
    con_coal = json.load(f)

print("📊 COMPARACIÓN DE ESCAÑOS MR")
print("-" * 80)
print(f"{'Partido':<12} | {'CON Coalición':<15} | {'SIN Coalición':<15} | {'Diferencia':>10}")
print("-" * 80)

# Extraer MR de cada respuesta
partidos = ['MORENA', 'PT', 'PVEM', 'PAN', 'PRI', 'PRD', 'MC']

for p in partidos:
    mr_con = next((x['mr'] for x in con_coal['resultados'] if x['partido'] == p), 0)
    mr_sin = next((x['mr'] for x in sin_coal['resultados'] if x['partido'] == p), 0)
    diff = mr_sin - mr_con
    
    diff_str = f"{diff:+d}" if diff != 0 else "="
    print(f"{p:<12} | {mr_con:>15} | {mr_sin:>15} | {diff_str:>10}")

print("-" * 80)
print()

print("📊 COMPARACIÓN DE ESCAÑOS RP")
print("-" * 80)
print(f"{'Partido':<12} | {'CON Coalición':<15} | {'SIN Coalición':<15} | {'Diferencia':>10}")
print("-" * 80)

for p in partidos:
    rp_con = next((x['rp'] for x in con_coal['resultados'] if x['partido'] == p), 0)
    rp_sin = next((x['rp'] for x in sin_coal['resultados'] if x['partido'] == p), 0)
    diff = rp_sin - rp_con
    
    diff_str = f"{diff:+d}" if diff != 0 else "="
    print(f"{p:<12} | {rp_con:>15} | {rp_sin:>15} | {diff_str:>10}")

print("-" * 80)
print()

print("📊 COMPARACIÓN DE ESCAÑOS TOTALES")
print("-" * 80)
print(f"{'Partido':<12} | {'CON Coalición':<15} | {'SIN Coalición':<15} | {'Diferencia':>10}")
print("-" * 80)

for p in partidos:
    tot_con = next((x['total'] for x in con_coal['resultados'] if x['partido'] == p), 0)
    tot_sin = next((x['total'] for x in sin_coal['resultados'] if x['partido'] == p), 0)
    diff = tot_sin - tot_con
    
    diff_str = f"{diff:+d}" if diff != 0 else "="
    print(f"{p:<12} | {tot_con:>15} | {tot_sin:>15} | {diff_str:>10}")

print("-" * 80)
print()

print("🔍 ANÁLISIS DE DIFERENCIAS EN MR")
print("="*80)
print()

# Identificar diferencias en MR
mr_diffs = []
for p in partidos:
    mr_con = next((x['mr'] for x in con_coal['resultados'] if x['partido'] == p), 0)
    mr_sin = next((x['mr'] for x in sin_coal['resultados'] if x['partido'] == p), 0)
    if mr_con != mr_sin:
        mr_diffs.append({
            'partido': p,
            'con': mr_con,
            'sin': mr_sin,
            'diff': mr_sin - mr_con
        })

if mr_diffs:
    print("⚠️ DIFERENCIAS EN MR DETECTADAS:")
    for d in mr_diffs:
        print(f"  {d['partido']}: {d['con']} → {d['sin']} ({d['diff']:+d})")
    print()
    print("Esto es CORRECTO porque:")
    print("  - CON coalición: usa el SIGLADO para asignar distritos")
    print("    (el siglado dice qué partido específico gana cada distrito)")
    print("  - SIN coalición: usa VOTOS INDIVIDUALES de cada partido")
    print("    (el partido con más votos propios gana el distrito)")
    print()
    print("Ejemplo: Un distrito puede tener:")
    print("  - Coalición FXM gana (PAN+PRI+PRD sumados)")
    print("  - Pero individualmente MORENA tiene más votos que PAN solo")
    print("  → CON coalición: distrito va a PAN (según siglado)")
    print("  → SIN coalición: distrito va a MORENA (más votos individuales)")
else:
    print("✅ No hay diferencias en MR (esto sería raro)")

print()
print("="*80)
print("💡 CONCLUSIÓN")
print("="*80)
print()
print("Si el frontend muestra resultados MUY diferentes cuando apagas coaliciones,")
print("probablemente está:")
print()
print("1. ❌ NO pasando correctamente usar_coaliciones=False")
print("2. ❌ Usando un siglado o configuración diferente")
print("3. ❌ Aplicando topes cuando no debería")
print()
print("Para verificar: inspecciona la petición HTTP que hace el frontend")
print("y confirma que el parámetro 'usar_coaliciones' está llegando como False")
print()
print("="*80)
