"""
Comparar conteo de MR: Siglado vs Motor
"""

import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(__file__))

from engine.procesar_diputados_v2 import procesar_diputados_v2

# Sistema vigente
config = {
    'max_seats': 500,
    'mr_seats': None,
    'rp_seats': 200,
    'max_seats_per_party': 300,
    'sobrerrepresentacion': None,
    'usar_coaliciones': True,
    'quota_method': 'hare',
    'print_debug': False  # No queremos debug
}

print("=" * 80)
print("COMPARACIÓN: SIGLADO vs MOTOR (Conteo MR)")
print("=" * 80)

# 1. Leer siglado
siglado = pd.read_csv('data/siglado-diputados-2024.csv')
conteo_siglado = siglado['grupo_parlamentario'].value_counts().sort_index()

print("\n📊 Conteo MR según SIGLADO:")
print(conteo_siglado.to_string())
print(f"\nTotal MR en siglado: {conteo_siglado.sum()}")

# 2. Ejecutar motor
resultado = procesar_diputados_v2(
    anio=2024,
    path_parquet='data/computos_diputados_2024.parquet',
    **config
)

print("\n📊 Conteo MR según MOTOR:")
if 'MR' in resultado.columns:
    print(resultado[['MR']].to_string())
    print(f"\nTotal MR en motor: {resultado['MR'].sum()}")
else:
    print("⚠️ Motor no devolvió columna 'MR'")

print("\n" + "=" * 80)
print("COMPARACIÓN LADO A LADO")
print("=" * 80)

# Comparar
if 'MR' in resultado.columns:
    comparacion = pd.DataFrame({
        'Siglado': conteo_siglado,
        'Motor': resultado['MR']
    }).fillna(0).astype(int)
    
    comparacion['Diferencia'] = comparacion['Motor'] - comparacion['Siglado']
    
    print("\n" + comparacion.to_string())
    
    print("\n" + "=" * 80)
    print("💡 ANÁLISIS:")
    print("=" * 80)
    
    diff_total = comparacion['Diferencia'].abs().sum()
    print(f"\nDiferencia total absoluta: {diff_total}")
    
    if diff_total == 0:
        print("\n✅ El motor está contando EXACTAMENTE como el siglado")
    else:
        print("\n⚠️  El motor NO está contando como el siglado")
        print(f"\nPartidos con diferencias:")
        discrepantes = comparacion[comparacion['Diferencia'] != 0]
        print(discrepantes.to_string())
