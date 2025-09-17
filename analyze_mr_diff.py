import pandas as pd
from engine.procesar_diputados_v2 import cols_candidaturas_anio_con_coaliciones, partidos_de_col, norm_ascii_up

PARQUET = 'data/computos_diputados_2024.parquet'
SIGLADO = 'data/siglado-diputados-2024.csv'

print('Cargando parquet...')
df = pd.read_parquet(PARQUET)
print('Columns:', df.columns.tolist()[:50])

# normalize columns to mimic engine behavior
df.columns = [norm_ascii_up(c) for c in df.columns]

# load siglado
sig = pd.read_csv(SIGLADO)
sig['entidad_normalizada'] = sig['entidad_ascii'].apply(lambda x: str(x).strip().upper())

# set parties base from columns
exclude = set(['ENTIDAD','DISTRITO','TOTAL_BOLETAS','TOTAL_PARTIDOS_SUM','ANIO','CI','TOTAL'])
party_cols = [c for c in df.columns if c not in exclude]
print('Party cols detected:', party_cols)

# winners by argmax on party_cols
winners_argmax = df[party_cols].idxmax(axis=1).str.strip().str.upper()
arg_counts = winners_argmax.value_counts()
print('\nArgmax winners top 20:', arg_counts.head(20).to_dict())

# Build candidaturas_cols
cand_cols = cols_candidaturas_anio_con_coaliciones(df, 2024)
print('\nCandidaturas cols detected by function:', cand_cols)

# winners by candidaturas_cols logic
winners_cand = []
for _, row in df.iterrows():
    max_v = -1
    winner = None
    for col in cand_cols:
        if col in row.index:
            try:
                val = row[col]
            except Exception:
                val = 0
            if val > max_v:
                max_v = val
                winner = col
    winners_cand.append(winner if winner is not None else None)

cand_counts = pd.Series([str(x).strip().upper() if x is not None else None for x in winners_cand]).value_counts()
print('\nWinners by candidaturas logic top 20:', cand_counts.head(20).to_dict())

# Compare mismatches where argmax==MORENA but candidaturas logic != MORENA
mismatch_samples = []
for idx, row in df.iterrows():
    arg = winners_argmax.iloc[idx]
    cand = winners_cand[idx]
    if str(arg).upper() == 'MORENA' and (cand is None or str(cand).upper() != 'MORENA'):
        mismatch_samples.append((idx, row['ENTIDAD'], row['DISTRITO'], arg, cand))
        if len(mismatch_samples) >= 10:
            break

print('\nSample mismatches where argmax==MORENA but candidaturas logic != MORENA (up to 10):')
for m in mismatch_samples:
    print(m)

print('\nDone')
