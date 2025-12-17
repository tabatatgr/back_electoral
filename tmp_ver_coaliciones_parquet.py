"""
Ver los votos de coaliciones en el parquet
"""

import pandas as pd

df = pd.read_parquet('data/computos_diputados_2024.parquet')

print("=" * 80)
print("VOTOS DE COALICIONES EN AGUASCALIENTES-1")
print("=" * 80)

# Buscar AGUASCALIENTES-1
distrito = df[(df['ENTIDAD'].str.upper() == 'AGUASCALIENTES') & (df['DISTRITO'] == 1)].iloc[0]

print("\n📊 Partidos individuales:")
print(f"   MORENA: {distrito['MORENA']:>10,.0f}")
print(f"   PAN:    {distrito['PAN']:>10,.0f}")
print(f"   PRI:    {distrito['PRI']:>10,.0f}")
print(f"   PRD:    {distrito['PRD']:>10,.0f}")
print(f"   PT:     {distrito['PT']:>10,.0f}")
print(f"   PVEM:   {distrito['PVEM']:>10,.0f}")
print(f"   MC:     {distrito['MC']:>10,.0f}")

print("\n📊 Posibles coaliciones:")
print(f"   FXM:    {distrito.get('FXM', 0):>10,.0f}")
print(f"   NA:     {distrito.get('NA', 0):>10,.0f}")
print(f"   PES:    {distrito.get('PES', 0):>10,.0f}")
print(f"   RSP:    {distrito.get('RSP', 0):>10,.0f}")

print("\n" + "=" * 80)
print("💡 INTERPRETACIÓN:")
print("=" * 80)

fxm = distrito.get('FXM', 0)
pan = distrito['PAN']
pri = distrito['PRI']
prd = distrito['PRD']

print(f"\nFXM = {fxm:,.0f}")
print(f"PAN+PRI+PRD = {pan:,.0f} + {pri:,.0f} + {prd:,.0f} = {pan+pri+prd:,.0f}")

if abs(fxm - (pan + pri + prd)) < 1:
    print("\n✅ FXM = PAN + PRI + PRD (es la suma de la coalición)")
else:
    print("\n⚠️  FXM NO es la suma de PAN + PRI + PRD")

# Buscar coalición SIGAMOS HACIENDO HISTORIA
print("\n" + "=" * 80)
print("Buscando coalición SIGAMOS HACIENDO HISTORIA...")
print("=" * 80)

morena = distrito['MORENA']
pt = distrito['PT']
pvem = distrito['PVEM']

print(f"\nMORENA+PT+PVEM = {morena:,.0f} + {pt:,.0f} + {pvem:,.0f} = {morena+pt+pvem:,.0f}")

# Ver todas las columnas para buscar SHH
print("\n📋 Todas las columnas del parquet:")
for col in sorted(df.columns):
    val = distrito.get(col, 0)
    if isinstance(val, (int, float)) and val > 0:
        print(f"   {col:20s}: {val:>10,.0f}")
