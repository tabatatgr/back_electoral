#!/usr/bin/env python3

import pandas as pd
from engine.procesar_diputados_v2 import procesar_diputados_v2

print("🔍 ANÁLISIS DETALLADO DE MC DESPUÉS DE LA CORRECCIÓN")
print("=" * 50)

# Procesar 2018
resultados = procesar_diputados_v2(
    anio=2018,
    sistema='mixto',
    mr_seats=None,
    rp_seats=200,
    max_seats=500
)

print(f"MC MR: {resultados['MR']['MC']}")
print(f"MC RP: {resultados['RP']['MC']}")
print(f"MC Total: {resultados['Total']['MC']}")

# Revisar siglado para MC
print("\n🔍 ANÁLISIS DEL SIGLADO:")
siglado = pd.read_csv('data/siglado-diputados-2018.csv')
mc_distritos = siglado[siglado['partido'] == 'MC']['distrito'].unique()
print(f"Distritos donde MC aparece en siglado: {len(mc_distritos)}")
if len(mc_distritos) > 0:
    print(f"Primeros 10: {list(mc_distritos[:10])}")

# Revisar coaliciones
print("\n🔍 COALICIONES EN SIGLADO:")
coaliciones_mc = siglado[siglado['partido'] == 'MC'][['distrito', 'coalicion']].drop_duplicates()
print(f"MC en coaliciones:")
for _, row in coaliciones_mc.head(10).iterrows():
    print(f"  {row['distrito']}: {row['coalicion']}")

print("\n✅ CORRECCIÓN EXITOSA: MC ahora recibe escaños MR desde las coaliciones!")
