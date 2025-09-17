import pandas as pd
import pyarrow.parquet as pq
import re

PARQUET = 'data/computos_diputados_2024.parquet'
SIGLADO = 'data/siglado-diputados-2024.csv'
OUT_PREFIX = 'outputs/mr_smoke'

print('Leyendo parquet...')
tbl = pq.read_table(PARQUET)
df = tbl.to_pandas()
print('Filas parquet:', len(df))

# Normalizar distrito ID a 3 chars
if 'DISTRITO' in df.columns:
    df['DIST_CH'] = df['DISTRITO'].astype(int).astype(str).str.zfill(3)
else:
    # intentar inferir
    possible = [c for c in df.columns if 'distr' in c.lower()]
    if possible:
        df['DIST_CH'] = df[possible[0]].astype(int).astype(str).str.zfill(3)
    else:
        raise SystemExit('No se encontró columna de distrito')

# Detect party/formula columns (heurística: mayúsculas o listado común)
common = ['MORENA','PAN','PRI','PRD','PT','PVEM','MC','PES','RSP','NA','CI']
party_cols = [c for c in df.columns if c.upper() in common]
# fallback: columnas con solo letras y sin acentos (aprox)
if not party_cols:
    party_cols = [c for c in df.columns if re.match(r'^[A-ZÑ]+$', str(c).upper())]

print('Party cols detected (sample):', party_cols[:20])

# 1) Agregación por distrito x partido/formula
dist_comp = df[['DIST_CH'] + party_cols].melt(id_vars=['DIST_CH'], var_name='PARTY', value_name='VOTOS')
# eliminar filas sin votos o cero
dist_comp = dist_comp[dist_comp['VOTOS'].notna()]
try:
    dist_comp['VOTOS'] = pd.to_numeric(dist_comp['VOTOS'], errors='coerce').fillna(0).astype(int)
except Exception:
    pass

# 2) Filtrar basura
ban = set(['NULOS','NO REGISTRADO','NO REGISTRADOS','NR','BLANCOS','VOTOS NULOS','CANDIDATO NO REGISTRADO','NA','CI'])
dist_comp_clean = dist_comp[~dist_comp['PARTY'].str.upper().isin(ban)]

# 1-check duplicates: count rows per district after aggregation (should be #parties)
dist_counts = dist_comp_clean.groupby(['DIST_CH','PARTY'], as_index=False)['VOTOS'].sum()
# duplicates are none after aggregation but detect if original had multiple rows per district-party before.
# We can detect if melt produced multiple source rows by comparing group sizes in original df
orig_group = df.groupby(['DIST_CH']).size().reset_index(name='rows_per_dist')
orig_group.to_csv(OUT_PREFIX + '_rows_per_district.csv', index=False)

# 3) Competidores basura: list of party labels that look like garbage
unique_parties = sorted(dist_comp['PARTY'].unique())
garbage = [p for p in unique_parties if p.upper() in ban]
pd.DataFrame({'garbage':garbage}).to_csv(OUT_PREFIX + '_garbage_parties.csv', index=False)

# 4) IDs that don't machan: check leading zeros issues between parquet and siglado
sig = pd.read_csv(SIGLADO, dtype=str)
if 'distrito' in sig.columns:
    sig['DIST_CH'] = sig['distrito'].astype(int).astype(str).str.zfill(3)
else:
    # try entidad_ascii + distrito
    sig['DIST_CH'] = sig['distrito'].astype(str).str.zfill(3)

parquet_dists = set(df['DIST_CH'].unique())
sig_dists = set(sig['DIST_CH'].unique())
missing_in_siglado = sorted(list(parquet_dists - sig_dists))
missing_in_parquet = sorted(list(sig_dists - parquet_dists))
pd.DataFrame({'missing_in_siglado': missing_in_siglado}).to_csv(OUT_PREFIX + '_missing_in_siglado.csv', index=False)
pd.DataFrame({'missing_in_parquet': missing_in_parquet}).to_csv(OUT_PREFIX + '_missing_in_parquet.csv', index=False)

# 5) Empates: compute winners per district and detect ties
agg = dist_comp_clean.groupby(['DIST_CH','PARTY'], as_index=False)['VOTOS'].sum()
# winners per district
agg_sorted = agg.sort_values(['DIST_CH','VOTOS'], ascending=[True, False])
# pick top per district and mark ties
winner = agg_sorted.groupby('DIST_CH').apply(lambda g: g[g['VOTOS']==g['VOTOS'].max()]).reset_index(drop=True)
win_counts = winner.groupby('DIST_CH').size().reset_index(name='n_winners')
ties = win_counts[win_counts['n_winners']>1]['DIST_CH'].tolist()
pd.DataFrame({'tied_districts': ties}).to_csv(OUT_PREFIX + '_ties.csv', index=False)

# 6) Siglado mapping check: need mapping by DIST_CH + PARTY -> partido_siglado
# detect if siglado has columns coalicion or partido
sig_cols = [c.lower() for c in sig.columns]
has_coal = 'coalicion' in sig_cols
if has_coal:
    # normalize sig entries
    sig_map = sig[['entidad','DIST_CH','coalicion']].copy()
    sig_map.columns = ['entidad','DIST_CH','coalicion']
    # We'll join by DIST_CH and PARTY (coalicion may match party label)
    join_df = winner.merge(sig_map, on='DIST_CH', how='left')
    join_df['mapped'] = join_df.apply(lambda r: r['PARTY'] == r['coalicion'] if pd.notna(r.get('coalicion')) else False, axis=1)
    missing_map = join_df[join_df['coalicion'].isna()]
    missing_map.to_csv(OUT_PREFIX + '_missing_siglado_map.csv', index=False)
else:
    print('Siglado no tiene columna coalicion clara; salteando mapeo territorial')

# Summary
summary = {
    'n_parquet_rows': len(df),
    'n_unique_parquet_districts': len(parquet_dists),
    'n_siglado_rows': len(sig),
    'n_unique_siglado_districts': len(sig_dists),
    'n_ties': len(ties)
}
pd.DataFrame([summary]).to_csv(OUT_PREFIX + '_summary.csv', index=False)
print('Smoke checks done. Outputs prefix:', OUT_PREFIX)
