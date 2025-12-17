"""
VERIFICACIÓN FINAL: ¿El siglado tiene los resultados oficiales?
"""

import pandas as pd

# Cargar siglado
siglado = pd.read_csv('data/siglado-diputados-2024.csv')

print("=" * 80)
print("VERIFICACIÓN: ¿El siglado tiene los resultados oficiales?")
print("=" * 80)

print(f"\n📊 Total filas en siglado: {len(siglado)}")

# Contar distritos únicos
siglado['entidad_distrito'] = siglado['entidad'].astype(str) + '_' + siglado['distrito'].astype(str)
distritos_unicos = siglado['entidad_distrito'].nunique()

print(f"📊 Distritos únicos: {distritos_unicos}")

# Contar por partido
conteo_partidos = siglado['grupo_parlamentario'].value_counts().sort_values(ascending=False)

print("\n📊 MR por partido (según siglado):")
for partido, count in conteo_partidos.items():
    print(f"   {partido:10s}: {count}")

print(f"\n   {'TOTAL':10s}: {conteo_partidos.sum()}")

print("\n" + "=" * 80)
print("COMPARACIÓN CON DATOS OFICIALES")
print("=" * 80)

# Datos oficiales de MR (total - RP calculado antes)
oficial_mr = {
    'MORENA': 257 - 85,   # 172
    'PAN': 71 - 35,       # 36
    'PVEM': 60 - 18,      # 42
    'PT': 47 - 11,        # 36
    'PRI': 36 - 23,       # 13
    'MC': 27 - 23,        # 4
    'PRD': 1 - 5          # -4 (no tiene sentido, asumimos 0)
}

# Ajustar PRD
if oficial_mr['PRD'] < 0:
    print("\n⚠️  Ajuste: PRD oficial tiene escaños negativos calculados, asumiendo que tiene MR positivos")
    oficial_mr['PRD'] = max(1, 1)  # PRD tiene 1 total oficial

print(f"\n{'Partido':<10} {'Siglado MR':>12} {'Oficial MR':>12} {'Diferencia':>12}")
print("-" * 50)

todos_partidos = set(conteo_partidos.index) | set(oficial_mr.keys())
diff_total = 0

for partido in sorted(todos_partidos):
    siglado_val = conteo_partidos.get(partido, 0)
    oficial_val = oficial_mr.get(partido, 0)
    diff = siglado_val - oficial_val
    diff_total += abs(diff)
    marca = "✅" if diff == 0 else "⚠️"
    print(f"{partido:<10} {siglado_val:>12} {oficial_val:>12} {diff:>12} {marca}")

print(f"\n{'TOTAL':<10} {conteo_partidos.sum():>12} {sum(v for v in oficial_mr.values() if v > 0):>12}")

print("\n" + "=" * 80)
print("💡 CONCLUSIÓN:")
print("=" * 80)

if diff_total == 0:
    print("\n✅ El siglado COINCIDE EXACTAMENTE con los datos oficiales de MR")
    print("\nPor lo tanto:")
    print("- El siglado ES la fuente oficial de resultados")
    print("- El motor DEBE usar el siglado directamente, no calcular desde votos")
    print("- El problema del motor es que está IGNORANDO el siglado")
else:
    print(f"\n⚠️  El siglado tiene diferencias con los oficiales (total: {diff_total})")
    print("\nDiferencias detectadas:")
    for partido in sorted(todos_partidos):
        siglado_val = conteo_partidos.get(partido, 0)
        oficial_val = oficial_mr.get(partido, 0)
        if siglado_val != oficial_val:
            print(f"   {partido}: siglado={siglado_val}, oficial={oficial_val}, diff={siglado_val - oficial_val}")

print("\n" + "=" * 80)
print("🔍 ANÁLISIS DE DISTRIBUCIÓN:")
print("=" * 80)

print("\nEl siglado tiene 553 filas para 332 distritos únicos.")
print("Esto significa que algunos distritos tienen múltiples filas.")
print("\n¿Por qué?")
print("Posiblemente:")
print("1. Distritos donde ambas coaliciones compitieron y se lista ambas")
print("2. Distritos con circunstancias especiales")
print("3. Formato del archivo con filas redundantes")

# Ver distritos con múltiples filas
duplicados = siglado.groupby('entidad_distrito').size()
distritos_multiples = duplicados[duplicados > 1]

print(f"\nDistritos con múltiples filas: {len(distritos_multiples)}")
print("\nEjemplos:")
for distrito_id in list(distritos_multiples.index)[:5]:
    count = distritos_multiples[distrito_id]
    filas = siglado[siglado['entidad_distrito'] == distrito_id]
    print(f"\n   {distrito_id} ({count} filas):")
    for _, fila in filas.iterrows():
        print(f"      {fila['coalicion']}: {fila['grupo_parlamentario']}")
