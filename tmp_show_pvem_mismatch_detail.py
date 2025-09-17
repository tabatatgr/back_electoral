import pandas as pd
import pyarrow.parquet as pq
from engine.recomposicion import recompose_coalitions, _normalize_text

PARQUET = 'data/computos_diputados_2024.parquet'
SIGLADO = 'data/siglado-diputados-2024.normalized.csv'

m = pd.read_csv('outputs/pvem_mismatch_by_district.csv')
print('mismatches loaded:', len(m))

table = pq.read_table(PARQUET)
df = table.to_pandas()
recomposed = recompose_coalitions(df, 2024, 'diputados', rule='equal_residue_siglado', siglado_path=SIGLADO)

# Ensure normalization
recomposed['ENTIDAD'] = recomposed['ENTIDAD'].astype(str)
recomposed['DISTRITO'] = pd.to_numeric(recomposed['DISTRITO'], errors='coerce').fillna(0).astype(int)

partidos = [c for c in recomposed.columns if c.upper() in ['PAN','PRI','PRD','PVEM','PT','MC','MORENA','PES','NA','CI','FXM','RSP']]

for idx, row in m.iterrows():
    ent = row['ENTIDAD']
    dist = int(row['DISTRITO'])
    # usar la misma normalización que recompose_coalitions
    ent_key = _normalize_text(ent)
    sel = recomposed[(recomposed['ENTIDAD'].map(lambda x: _normalize_text(str(x)))==ent_key) & (recomposed['DISTRITO']==dist)]
    print('\n---', ent, dist, 'rows:', len(sel))
    if len(sel)==0:
        print('No recomposed row found for this district (naming mismatch?)')
        continue
    r = sel.iloc[0]
    # show votes for all partidos found
    votos = {p: int(r.get(p,0)) for p in partidos if p in r.index}
    # sort
    votos_sorted = sorted(votos.items(), key=lambda x: -x[1])
    print('Top votos:', votos_sorted[:8])
    print('winner_by_votes_raw from audit:', row.get('winner_by_votes_raw'))
    print('winner_by_votes_valid from audit:', row.get('winner_by_votes_valid'))
    print('postuladores:', row.get('postuladores'))
