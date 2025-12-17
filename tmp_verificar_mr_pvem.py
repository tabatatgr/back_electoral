"""
Verificar: ¿PVEM realmente ganó 58 distritos de MR?
Si PVEM debe tener 60 total y 18 RP es correcto, entonces PVEM debe tener 42 MR, no 58.
Diferencia: 58 - 42 = 16 distritos que PVEM NO debería ganar.
"""

import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(__file__))

# Cargar siglado 2024
siglado = pd.read_csv('data/siglado-diputados-2024.csv')

print("=" * 80)
print("VERIFICACIÓN: ¿PVEM ganó 58 distritos de MR?")
print("=" * 80)

print(f"\n📋 Estructura del siglado:")
print(siglado.columns.tolist())
print(f"\nTotal filas: {len(siglado)}")

print("\n📊 Primeras 10 filas:")
print(siglado.head(10))

# Buscar columna de partido/coalición
partido_cols = [col for col in siglado.columns if any(word in col.lower() for word in ['partido', 'sigla', 'coalicion'])]
print(f"\n🔍 Columnas de partido/coalición: {partido_cols}")

# Buscar columnas de votos
votos_cols = [col for col in siglado.columns if 'voto' in col.lower()]
print(f"🔍 Columnas de votos: {votos_cols}")

# Ver valores únicos de partidos
if partido_cols:
    for col in partido_cols:
        valores = siglado[col].unique()
        print(f"\n📊 Valores únicos en '{col}':")
        print(valores)

print("\n" + "=" * 80)
print("GANADORES DE MR POR PARTIDO")
print("=" * 80)

# Agrupar por distrito y encontrar ganador
if 'DISTRITO' in siglado.columns and 'VOTOS' in siglado.columns:
    # Encontrar el ganador de cada distrito (el que tiene más votos)
    ganadores = siglado.loc[siglado.groupby('DISTRITO')['VOTOS'].idxmax()]
    
    print(f"\nTotal distritos: {len(ganadores)}")
    print(f"\nColumnas disponibles para ganadores:")
    print(ganadores.columns.tolist())
    
    # Buscar columna de partido en ganadores
    for col in partido_cols:
        if col in ganadores.columns:
            print(f"\n📊 Distribución de ganadores por {col}:")
            conteo = ganadores[col].value_counts().sort_values(ascending=False)
            print(conteo)
            
            # ¿Cuántos ganó PVEM?
            pvem_variants = [val for val in conteo.index if 'PVEM' in str(val).upper()]
            print(f"\n🎯 Variantes de PVEM en ganadores: {pvem_variants}")
            
            for variant in pvem_variants:
                count = conteo[variant]
                print(f"  {variant}: {count} distritos")

print("\n" + "=" * 80)
print("ANÁLISIS ESPECÍFICO DE PVEM")
print("=" * 80)

# Buscar todas las filas con PVEM
if partido_cols:
    for col in partido_cols:
        pvem_filas = siglado[siglado[col].str.contains('PVEM', case=False, na=False)]
        print(f"\n📊 Filas con 'PVEM' en columna '{col}': {len(pvem_filas)}")
        
        if len(pvem_filas) > 0:
            print("\nPrimeras 5 filas con PVEM:")
            print(pvem_filas.head())
            
            # Ver valores únicos
            print(f"\nValores únicos de PVEM en '{col}':")
            print(pvem_filas[col].unique())
