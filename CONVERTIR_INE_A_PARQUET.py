"""
Convierte INE_SECCION_2020.csv (50MB) a parquet (5-10MB) para reducir uso de RAM.
"""

import pandas as pd
from pathlib import Path

print("Cargando INE_SECCION_2020.csv...")
csv_path = Path('redistritacion/data/INE_SECCION_2020.csv')
parquet_path = Path('redistritacion/data/INE_SECCION_2020.parquet')

# Leer CSV
df = pd.read_csv(csv_path)

print(f"Filas: {len(df):,}")
print(f"Columnas: {list(df.columns)}")
print(f"Tamaño CSV: {csv_path.stat().st_size / 1024 / 1024:.2f} MB")

# Guardar como parquet (comprimido)
df.to_parquet(parquet_path, compression='snappy', index=False)

print(f"Tamaño Parquet: {parquet_path.stat().st_size / 1024 / 1024:.2f} MB")
print(f"Reducción: {(1 - parquet_path.stat().st_size / csv_path.stat().st_size) * 100:.1f}%")

print("\n✅ Conversión completada")
print(f"Archivo guardado en: {parquet_path}")
