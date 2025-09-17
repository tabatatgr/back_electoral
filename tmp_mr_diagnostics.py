import pandas as pd
import pyarrow.parquet as pq
from engine.recomposicion import _load_siglado_dip
from engine.recomposicion import parties_for
import random

PARQUET = 'data/computos_diputados_2024.parquet'
SIGLADO = 'data/siglado-diputados-2024.csv'
OUT_PREFIX = 'outputs/mr_diagnostics'

print('Leyendo parquet...')
tbl = pq.read_table(PARQUET)
df = tbl.to_pandas()
print('Columnas parquet:', df.columns.tolist())

# Intentar identificar columnas relevantes
candidates = [c for c in df.columns if 'distrito' in c.lower() or 'distr' in c.lower()]
parties = parties_for(2024)
party_cols = [p for p in parties if p in df.columns]
print('Detected district columns:', candidates)
print('Detected party columns count:', len(party_cols))

# Normalize district id column name
if 'DISTRITO' in df.columns:
    DIST_COL = 'DISTRITO'
else:
    # fallback: pick first candidate
    DIST_COL = candidates[0] if candidates else None

# Build df_norm: select district, candidate formula columns
# recomposition produces ENTIDAD, DISTRITO, party columns
from engine.recomposicion import recompose_coalitions
recomposed = recompose_coalitions(df, 2024, 'diputados', rule='equal_residue_siglado', siglado_path=SIGLADO)
print('Recomposed shape:', recomposed.shape)

# 1) Normalizar ID distrito
recomposed['DIST_CH'] = recomposed['DISTRITO'].astype(str).str.zfill(3)

# 2) Filtrar basura: eliminar filas sin partido (CI handled separately)
ban = set(['NULOS','NO REGISTRADO','NO REGISTRADOS','NR','BLANCOS','VOTOS NULOS','CANDIDATO NO REGISTRADO'])
# convert column names of parties to uppercase keys
# create dist_comp: one row per district×party with votes
parties = [p for p in parties if p in recomposed.columns]
print('Using parties:', parties)

dist_comp = recomposed[['DIST_CH'] + parties].melt(id_vars=['DIST_CH'], value_name='votos', var_name='partido')
dist_comp = dist_comp[~dist_comp['partido'].str.upper().isin(ban)]

dist_comp_agg = dist_comp.groupby(['DIST_CH','partido'], as_index=False)['votos'].sum()
print('dist_comp_agg rows:', len(dist_comp_agg))

a = dist_comp_agg.groupby('DIST_CH').size().reset_index(name='n_competidores')
print('Competidores por distrito: sample')
print(a.describe())

# 3) Ganadores por distrito (argmax)
idx = dist_comp_agg.groupby('DIST_CH')['votos'].transform(max) == dist_comp_agg['votos']
ganadores = dist_comp_agg[idx].copy()
# mark ties
gan_count = ganadores.groupby('DIST_CH').size().reset_index(name='n_winners')
ganadores = ganadores.merge(gan_count, on='DIST_CH')
ganadores['tie'] = ganadores['n_winners'] > 1

# 4) Verificar número de distritos únicos
n_dist = dist_comp_agg['DIST_CH'].nunique()
print('Unique districts after aggregation:', n_dist)

# 5) Chequear siglado territorial
sig_df = _load_siglado_dip(SIGLADO)
# sig_df: entidad_key, distrito, coalicion_key, dominante
sig_df['DIST_CH'] = sig_df['distrito'].astype(int).astype(str).str.zfill(3)
# Need mapping partido/formula -> partido_siglado; recomposed used formula columns tokens
# We'll attempt to join by DIST_CH and pick dominant
# but sig_df uses entidad_key; recomposed has ENTIDAD normalized
recomposed['ENT_KEY'] = recomposed['ENTIDAD'].apply(lambda x: str(x).strip().upper())
# Build map: (ENT_KEY, DIST_CH) -> dominante
sig_map = sig_df.copy()
# normalize entidad_key uppercase
sig_map['entidad_key'] = sig_map['entidad_key'].astype(str).str.upper()
map_key = sig_map.set_index(['entidad_key','DIST_CH'])['dominante'].to_dict()

# Join attempt: for each ganador find recomposed ENTIDAD
# get sample of ganadores with ENTIDAD
# we need mapping from DIST_CH to ENTIDAD in recomposed - pick first matching
ent_per_dist = recomposed.groupby('DIST_CH')['ENTIDAD'].agg(lambda x: x.iloc[0]).to_dict()

# Build detection of missing mapping
missing = 0
mismatches = []
for _, row in ganadores.iterrows():
    dist = row['DIST_CH']
    ent = ent_per_dist.get(dist, None)
    if ent is None:
        missing += 1
        mismatches.append((dist, row['partido'], 'NO_ENT'))
        continue
    key = (ent.strip().upper(), dist)
    dom = map_key.get(key, None)
    if dom is None:
        missing += 1
        mismatches.append((dist, row['partido'], 'NO_SIG'))

print('Siglado mapping missing count:', missing)

# 6) Invariante: sum MR (non-ties) must equal number of unique districts
ssd_tbl = ganadores[~ganadores['tie']].groupby('partido', as_index=False).size().rename(columns={'size':'ssd'})
ssd_sum = ssd_tbl['ssd'].sum()
print('MR seats counted (no ties):', ssd_sum)

# 7) Sample 10 districts with detail
random.seed(7)
sample_dist = random.sample(list(dist_comp_agg['DIST_CH'].unique()), min(10, dist_comp_agg['DIST_CH'].nunique()))
print('Sample districts:', sample_dist)
detail = dist_comp_agg[dist_comp_agg['DIST_CH'].isin(sample_dist)].sort_values(['DIST_CH','votos'], ascending=[True,False])
detail.to_csv(OUT_PREFIX + '_sample_detail.csv', index=False)
print('Saved sample detail to', OUT_PREFIX + '_sample_detail.csv')

# 8) Save winners and ssd
ganadores.to_csv(OUT_PREFIX + '_winners.csv', index=False)
ssd_tbl.to_csv(OUT_PREFIX + '_ssd.csv', index=False)

print('Diagnostics saved to outputs: ', OUT_PREFIX + '_winners.csv', OUT_PREFIX + '_ssd.csv')
