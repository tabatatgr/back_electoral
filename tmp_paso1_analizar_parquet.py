"""
PASO 1: Analizar el parquet para entender QUÉ COLUMNAS HAY realmente
"""

import pandas as pd

print("=" * 80)
print("ANÁLISIS DEL PARQUET - Estructura real de datos")
print("=" * 80)

df = pd.read_parquet('data/computos_diputados_2024.parquet')

print(f"\n📊 Dimensiones: {len(df)} filas x {len(df.columns)} columnas")

print("\n📋 TODAS las columnas:")
for i, col in enumerate(df.columns, 1):
    print(f"   {i:2d}. {col}")

print("\n" + "=" * 80)
print("Primeras 3 filas completas:")
print("=" * 80)
print(df.head(3).T)  # Transpuesto para ver mejor

print("\n" + "=" * 80)
print("¿Hay columnas de COALICIONES?")
print("=" * 80)

# Buscar columnas que puedan ser coaliciones
posibles_coaliciones = [col for col in df.columns if col not in 
                        ['ENTIDAD', 'DISTRITO', 'TOTAL_BOLETAS', 'CI', 
                         'MORENA', 'PAN', 'PRI', 'PRD', 'PT', 'PVEM', 'MC']]

if posibles_coaliciones:
    print(f"\n✓ Columnas que NO son partidos conocidos ni metadata:")
    for col in posibles_coaliciones:
        print(f"   - {col}")
    
    print("\n📊 Valores en esas columnas (primera fila):")
    for col in posibles_coaliciones:
        val = df[col].iloc[0]
        print(f"   {col}: {val}")
    
    print("\n📊 ¿Tienen valores > 0?")
    for col in posibles_coaliciones:
        count_nonzero = (df[col] > 0).sum()
        print(f"   {col}: {count_nonzero} distritos con votos > 0")
else:
    print("\n✗ No hay columnas adicionales (solo partidos individuales)")

print("\n" + "=" * 80)
print("Verificar si hay 300 distritos:")
print("=" * 80)

print(f"\nTotal filas: {len(df)}")

# Verificar duplicados
duplicados = df.groupby(['ENTIDAD', 'DISTRITO']).size()
if (duplicados > 1).any():
    print(f"\n⚠️  HAY DUPLICADOS:")
    print(duplicados[duplicados > 1])
else:
    print("\n✓ No hay duplicados (cada entidad+distrito aparece 1 vez)")

# Contar distritos únicos
distritos_unicos = df.groupby('ENTIDAD')['DISTRITO'].nunique().sum()
print(f"\nDistritos únicos: {distritos_unicos}")

if distritos_unicos == 300:
    print("✓ Correcto: 300 distritos")
else:
    print(f"⚠️  Esperados 300, encontrados {distritos_unicos}")
