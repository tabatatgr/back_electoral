#!/usr/bin/env python3
from pathlib import Path
from engine.procesar_diputados_v2 import procesar_diputados_v2

# Suprimir warnings (temporal)
import warnings
warnings.filterwarnings('ignore')

# Ejecutar
r = procesar_diputados_v2(
    str(Path('data/computos_diputados_2024.parquet')),
    anio=2024,
    max_seats=500,
    mr_seats=375,
    rp_seats=125,
    usar_coaliciones=True
)

# Extraer MORENA
mr = r['mr'].get('MORENA', 0)
rp = r['rp'].get('MORENA', 0)
tot = r['tot'].get('MORENA', 0)

print(f"\nMORENA EN 75MR/25RP:")
print(f"  MR: {mr}")
print(f"  RP: {rp}")
print(f"  TOTAL: {tot}")
print(f"  TOPE TEORICO: 252")
print(f"  EXCESO: {tot - 252}")
