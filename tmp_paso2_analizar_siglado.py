"""
PASO 2: Analizar el siglado - estructura REAL y crear clave única correcta
"""

import pandas as pd

print("=" * 80)
print("ANÁLISIS DEL SIGLADO - Estructura y claves únicas")
print("=" * 80)

siglado = pd.read_csv('data/siglado-diputados-2024.csv')

print(f"\n📊 Dimensiones: {len(siglado)} filas x {len(siglado.columns)} columnas")

print("\n📋 Columnas:")
for col in siglado.columns:
    print(f"   - {col}")

print("\n📊 Primeras 10 filas:")
print(siglado.head(10).to_string(index=False))

print("\n" + "=" * 80)
print("CREAR CLAVE ÚNICA: entidad + distrito")
print("=" * 80)

# Crear clave única
siglado['clave_unica'] = siglado['entidad'].astype(str).str.upper().str.strip() + '_' + siglado['distrito'].astype(str)

print(f"\nTotal filas: {len(siglado)}")
print(f"Claves únicas: {siglado['clave_unica'].nunique()}")

# Buscar duplicados
duplicados = siglado.groupby('clave_unica').size()
duplicados_df = duplicados[duplicados > 1].sort_values(ascending=False)

if len(duplicados_df) > 0:
    print(f"\n⚠️  HAY {len(duplicados_df)} CLAVES CON DUPLICADOS:")
    print(f"\nTop 10 con más duplicados:")
    print(duplicados_df.head(10))
    
    print("\n🔍 Ejemplo de duplicado (AGUASCALIENTES_1):")
    ejemplo = siglado[siglado['clave_unica'] == 'AGUASCALIENTES_1']
    print(ejemplo[['entidad', 'distrito', 'coalicion', 'grupo_parlamentario']].to_string(index=False))
    
    print("\n💡 INTERPRETACIÓN:")
    print("Los duplicados son porque HAY MÚLTIPLES FILAS POR DISTRITO:")
    print("- Una fila por cada coalición que compite en ese distrito")
    print("- Cada fila indica qué partido de esa coalición recibe el escaño si gana")
else:
    print("\n✓ No hay duplicados")

print("\n" + "=" * 80)
print("ANALIZAR ESTRUCTURA POR DISTRITO:")
print("=" * 80)

# Contar filas por distrito
filas_por_distrito = siglado.groupby('clave_unica').size()

print(f"\nDistritos con 1 fila: {(filas_por_distrito == 1).sum()}")
print(f"Distritos con 2 filas: {(filas_por_distrito == 2).sum()}")
print(f"Distritos con 3+ filas: {(filas_por_distrito >= 3).sum()}")

# Total distritos en siglado
total_distritos_siglado = siglado['clave_unica'].nunique()
print(f"\nTotal distritos en siglado: {total_distritos_siglado}")
print(f"Total distritos en México: 300")
print(f"Distritos SIN coalición (no en siglado): {300 - total_distritos_siglado}")

print("\n" + "=" * 80)
print("¿POR QUÉ HAY MÁS DE 300 'DISTRITOS'?")
print("=" * 80)

# Analizar por entidad
print("\nDistritos por entidad (del siglado):")
por_entidad = siglado.groupby('entidad')['distrito'].nunique().sort_values(ascending=False)
print(por_entidad.head(10))

# Comparar con el parquet
parquet = pd.read_parquet('data/computos_diputados_2024.parquet')
print("\nDistritos por entidad (del parquet - REAL):")
por_entidad_parquet = parquet.groupby('ENTIDAD')['DISTRITO'].nunique().sort_values(ascending=False)
print(por_entidad_parquet.head(10))

print("\n" + "=" * 80)
print("BUSCAR INCONSISTENCIAS:")
print("=" * 80)

# Buscar entidades que están en siglado pero no en parquet
entidades_siglado = set(siglado['entidad'].str.upper().str.strip())
entidades_parquet = set(parquet['ENTIDAD'].str.upper().str.strip())

solo_siglado = entidades_siglado - entidades_parquet
solo_parquet = entidades_parquet - entidades_siglado

if solo_siglado:
    print(f"\n⚠️  Entidades SOLO en siglado (no en parquet):")
    for e in sorted(solo_siglado):
        count = siglado[siglado['entidad'].str.upper() == e]['clave_unica'].nunique()
        print(f"   - {e}: {count} distritos")

if solo_parquet:
    print(f"\n⚠️  Entidades SOLO en parquet (no en siglado):")
    for e in sorted(solo_parquet):
        count = parquet[parquet['ENTIDAD'].str.upper() == e]['DISTRITO'].nunique()
        print(f"   - {e}: {count} distritos")

print("\n" + "=" * 80)
print("COALICIONES Y PARTIDOS:")
print("=" * 80)

print("\n📊 Coaliciones presentes:")
print(siglado['coalicion'].value_counts())

print("\n📊 Partidos por coalición:")
for coalicion in siglado['coalicion'].unique():
    print(f"\n{coalicion}:")
    partidos = siglado[siglado['coalicion'] == coalicion]['grupo_parlamentario'].value_counts()
    print(partidos.to_string())
