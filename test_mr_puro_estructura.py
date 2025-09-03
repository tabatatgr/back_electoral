#!/usr/bin/env python3
"""
Verificar estructura específica del MR puro
"""

from engine.procesar_senadores_v2 import procesar_senadores_v2

print("🔍 VERIFICANDO ESTRUCTURA MR PURO")
print("=" * 50)

# Test MR puro
result_mr = procesar_senadores_v2(
    anio=2018,
    sistema="mr",
    max_seats=64,
    pm_seats=0,
    umbral=0.03,
    path_parquet="data/computos_senado_2018.parquet",
    path_siglado="data/siglado_senado_2018_corregido.csv"
)

print(f"Tipo: {type(result_mr)}")
print(f"Keys: {list(result_mr.keys())}")

for key, value in result_mr.items():
    if isinstance(value, dict):
        print(f"{key}: dict con {len(value)} elementos")
        if len(value) <= 20:  # Mostrar si no es muy grande
            print(f"   {value}")
    elif isinstance(value, list):
        print(f"{key}: list con {len(value)} elementos")
        if len(value) <= 3:  # Mostrar primeros elementos
            print(f"   Primeros 3: {value[:3]}")
    else:
        print(f"{key}: {value}")
