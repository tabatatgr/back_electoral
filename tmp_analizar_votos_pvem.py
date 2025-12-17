"""
Análisis de votos de PVEM 2024:
¿Su % de votos justifica 18 RP o solo 2 RP?
"""

import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(__file__))

# Cargar computos 2024
df = pd.read_parquet('data/computos_diputados_2024.parquet')

print("=" * 80)
print("ANÁLISIS DE VOTOS PVEM 2024")
print("=" * 80)

# Ver estructura
print("\n📋 Estructura del parquet:")
print(df.columns.tolist())
print(f"\nTotal filas: {len(df)}")

# Ver primeras filas
print("\n📊 Primeras filas:")
print(df.head(10))

# Buscar columnas de votos
votos_cols = [col for col in df.columns if 'voto' in col.lower() or 'pvem' in col.lower()]
print(f"\n🔍 Columnas relacionadas con votos o PVEM:")
print(votos_cols)

# Intentar calcular votos por partido
print("\n" + "=" * 80)
print("VOTOS NACIONALES 2024")
print("=" * 80)

# Ver si hay columnas de partidos
partido_cols = [col for col in df.columns if any(p in col.upper() for p in ['MORENA', 'PAN', 'PVEM', 'PT', 'PRI', 'MC', 'PRD'])]
print(f"\nColumnas de partidos encontradas: {partido_cols}")

# Si hay columnas específicas por partido, sumar
if partido_cols:
    print("\n📊 Total de votos por partido:")
    for col in partido_cols:
        total = df[col].sum()
        print(f"  {col}: {total:,}")

# Buscar columna PVEM específica
pvem_cols = [col for col in df.columns if 'PVEM' in col.upper()]
print(f"\n🎯 Columnas PVEM: {pvem_cols}")

if pvem_cols:
    for col in pvem_cols:
        print(f"\n{col}:")
        print(f"  Total: {df[col].sum():,}")
        print(f"  Promedio: {df[col].mean():.2f}")
        print(f"  Max: {df[col].max()}")
        print(f"  Min: {df[col].min()}")
