"""
Verificar: ¿Cuántos distritos REALMENTE tienen coaliciones según el siglado?
"""

import pandas as pd

siglado = pd.read_csv('data/siglado-diputados-2024.csv')

print("=" * 80)
print("ANÁLISIS REAL DEL SIGLADO")
print("=" * 80)

# Total de filas
print(f"\n📊 Total filas en siglado: {len(siglado)}")

# Distritos únicos
siglado['entidad_distrito'] = siglado['entidad'].astype(str) + '_' + siglado['distrito'].astype(str)
distritos_unicos = siglado['entidad_distrito'].nunique()
print(f"📊 Distritos únicos: {distritos_unicos}")

# ¿Cuántos distritos tienen 1 fila vs 2 filas?
conteo_filas = siglado.groupby('entidad_distrito').size()

print(f"\n📊 Distribución de filas por distrito:")
print(f"   Distritos con 1 fila: {(conteo_filas == 1).sum()}")
print(f"   Distritos con 2 filas: {(conteo_filas == 2).sum()}")
print(f"   Distritos con 3+ filas: {(conteo_filas >= 3).sum()}")

# Coaliciones presentes
print(f"\n📊 Coaliciones en el siglado:")
print(siglado['coalicion'].value_counts())

# Partidos por coalición
print(f"\n📊 Distribución de partidos por coalición:")
print("\nFUERZA Y CORAZON POR MEXICO:")
fcm = siglado[siglado['coalicion'] == 'FUERZA Y CORAZON POR MEXICO']
print(fcm['grupo_parlamentario'].value_counts())

print("\nSIGAMOS HACIENDO HISTORIA:")
shh = siglado[siglado['coalicion'] == 'SIGAMOS HACIENDO HISTORIA']
print(shh['grupo_parlamentario'].value_counts())

print("\n" + "=" * 80)
print("💡 INTERPRETACIÓN:")
print("=" * 80)

print(f"""
Total distritos en México: 300
Distritos en siglado: {distritos_unicos}
Filas totales: {len(siglado)}

Si hay {distritos_unicos} distritos pero {len(siglado)} filas:
- Esto significa que algunos distritos tienen AMBAS coaliciones
- Pero NO todos los distritos tienen coaliciones

Distritos con 1 fila: {(conteo_filas == 1).sum()} → Solo 1 coalición compitió
Distritos con 2 filas: {(conteo_filas == 2).sum()} → Ambas coaliciones compitieron

¿Faltantes? {300 - distritos_unicos} distritos NO están en el siglado
→ Esos distritos probablemente NO tuvieron coaliciones (competencia individual)
""")

print("\n" + "=" * 80)
print("🔍 Ejemplos de distritos con 2 coaliciones:")
print("=" * 80)

distritos_dobles = conteo_filas[conteo_filas == 2].index[:5]
for dist_id in distritos_dobles:
    print(f"\n{dist_id}:")
    filas = siglado[siglado['entidad_distrito'] == dist_id][['coalicion', 'grupo_parlamentario']]
    for _, fila in filas.iterrows():
        print(f"  - {fila['coalicion']}: {fila['grupo_parlamentario']}")

print("\n" + "=" * 80)
print("🔍 Ejemplos de distritos con 1 coalición:")
print("=" * 80)

distritos_simples = conteo_filas[conteo_filas == 1].index[:5]
for dist_id in distritos_simples:
    print(f"\n{dist_id}:")
    filas = siglado[siglado['entidad_distrito'] == dist_id][['coalicion', 'grupo_parlamentario']]
    for _, fila in filas.iterrows():
        print(f"  - {fila['coalicion']}: {fila['grupo_parlamentario']}")
