"""
Verificar el % real de votos de MORENA en los datos de 2024
"""
import pandas as pd
import sys
sys.path.insert(0, '.')
from engine.recomposicion import recompose_coalitions

# Cargar datos
df = pd.read_parquet("data/computos_diputados_2024.parquet")

print("=" * 80)
print("ANÁLISIS DE VOTOS MORENA 2024")
print("=" * 80)

# Normalizar columnas
from engine.procesar_diputados_v2 import norm_ascii_up
df.columns = [norm_ascii_up(c) for c in df.columns]

# Ver columnas disponibles
print(f"\nColumnas en el parquet: {list(df.columns)[:20]}")

# Recomponer coaliciones
siglado_df = pd.read_csv("data/siglado-diputados-2024.csv", dtype=str, keep_default_na=False)
siglado_df.columns = [c.strip().lower() for c in siglado_df.columns]

def _col_norm(c):
    c2 = norm_ascii_up(c)
    c2 = c2.replace(' ', '_')
    return c2.lower()
    
siglado_df.columns = [_col_norm(c) for c in siglado_df.columns]
_sig_path = 'data/siglado-diputados-2024.csv.tmp_normalized.csv'
siglado_df.to_csv(_sig_path, index=False)

recomposed = recompose_coalitions(
    df=df, year=2024, chamber="diputados",
    rule="equal_residue_siglado", siglado_path=_sig_path
)

import os
try:
    os.remove(_sig_path)
except:
    pass

# Calcular votos nacionales
partidos = ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA']
votos_partido = {}
for p in partidos:
    if p in recomposed.columns:
        votos_partido[p] = int(recomposed[p].sum())
    else:
        votos_partido[p] = 0

indep = int(recomposed['CI'].sum()) if 'CI' in recomposed.columns else 0

print(f"\n📊 Votos por partido (después de recomposición):")
total_partidos = sum(votos_partido.values())
for p in partidos:
    v = votos_partido[p]
    pct = (v / total_partidos * 100) if total_partidos > 0 else 0
    print(f"  {p:8s}: {v:12,} votos ({pct:5.2f}%)")

print(f"\n  {'CI':8s}: {indep:12,} votos")
print(f"  {'TOTAL':8s}: {total_partidos:12,} votos")

# Calcular sobre total CON independientes
total_con_indep = total_partidos + indep
if total_con_indep > 0:
    print(f"\n📊 Porcentajes sobre total (incluyendo independientes):")
    for p in partidos:
        v = votos_partido[p]
        pct = (v / total_con_indep * 100)
        print(f"  {p:8s}: {pct:5.2f}%")
    print(f"  {'CI':8s}: {indep / total_con_indep * 100:5.2f}%")

# MORENA específicamente
morena_votos = votos_partido['MORENA']
morena_pct_sin_indep = (morena_votos / total_partidos * 100) if total_partidos > 0 else 0
morena_pct_con_indep = (morena_votos / total_con_indep * 100) if total_con_indep > 0 else 0

print(f"\n⭐ MORENA:")
print(f"  Votos: {morena_votos:,}")
print(f"  % (sin independientes): {morena_pct_sin_indep:.2f}%")
print(f"  % (con independientes): {morena_pct_con_indep:.2f}%")

# Calcular tope esperado
print(f"\n🎯 Tope constitucional del 8%:")
print(f"  Basado en {morena_pct_sin_indep:.2f}% de votos:")
print(f"    {morena_pct_sin_indep:.2f}% + 8% = {morena_pct_sin_indep + 8:.2f}%")
print(f"    {(morena_pct_sin_indep + 8)/100 * 500:.1f} escaños")
print(f"\n  Basado en {morena_pct_con_indep:.2f}% de votos:")
print(f"    {morena_pct_con_indep:.2f}% + 8% = {morena_pct_con_indep + 8:.2f}%")
print(f"    {(morena_pct_con_indep + 8)/100 * 500:.1f} escaños")
