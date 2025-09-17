import sys, os
import pandas as pd
# ensure project root is on sys.path so `engine` package is importable
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from engine.recomposicion import recompose_coalitions
import pyarrow.parquet as pq

PARQUET = 'data/computos_diputados_2024.parquet'
SIGLADO = 'data/siglado-diputados-2024.normalized.csv'
OUT = 'outputs/winners_by_district_siglado.csv'

# read parquet
print('reading parquet...')
table = pq.read_table(PARQUET)
df = table.to_pandas()

print('recomposing with siglado...')
recomposed = recompose_coalitions(df, 2024, 'diputados', rule='equal_residue_siglado', siglado_path=SIGLADO)

# determine winner per district by max votes among parties
parties = [c for c in recomposed.columns if c not in ('ENTIDAD','DISTRITO','CI','TOTAL_BOLETAS')]

winners = []
for i, row in recomposed.iterrows():
    entidad = row['ENTIDAD']
    distrito = int(row['DISTRITO'])
    vals = {p: float(row.get(p,0) or 0) for p in parties}
    winner = max(vals.items(), key=lambda x: x[1])[0]
    winners.append({'ENTIDAD': entidad, 'DISTRITO': distrito, 'WINNER_SIGLADO': winner})

pd.DataFrame(winners).to_csv(OUT, index=False)
print('wrote', OUT, 'rows=', len(winners))
