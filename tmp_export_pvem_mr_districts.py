import pandas as pd
import os

outdir = 'outputs'
os.makedirs(outdir, exist_ok=True)

w = pd.read_csv('outputs/winners_by_district_siglado.csv')
pvem_d = w[w['WINNER_SIGLADO'].str.upper()=='PVEM'][['ENTIDAD','DISTRITO']]
print('pvem districts found:', len(pvem_d))

# Try reading parquet with pandas (pyarrow backend)
try:
    df = pd.read_parquet('data/computos_diputados_2024.parquet')
except Exception as e:
    print('Error reading parquet with pandas:', e)
    try:
        import pyarrow.parquet as pq
        table = pq.read_table('data/computos_diputados_2024.parquet')
        df = table.to_pandas()
    except Exception as e2:
        print('Error reading parquet with pyarrow:', e2)
        raise

# Normalize entidad names in parquet to match winners file
if 'ENTIDAD' in df.columns:
    df['ENTIDAD_NORM'] = df['ENTIDAD'].str.upper().str.normalize('NFKD') if df['ENTIDAD'].dtype==object else df['ENTIDAD']
else:
    df['ENTIDAD_NORM'] = df['entidad'].str.upper()

# ensure DISTRITO numeric comparability
if 'DISTRITO' in df.columns:
    df['DISTRITO_NUM'] = df['DISTRITO']
else:
    df['DISTRITO_NUM'] = df['distrito']

# perform join/filter
pv_rows = []
for _, r in pvem_d.iterrows():
    ent = r['ENTIDAD']
    d = int(r['DISTRITO'])
    sub = df[(df['ENTIDAD_NORM'].str.contains(ent.upper())) & (df['DISTRITO_NUM']==d)]
    if len(sub)==0:
        # try matching without accents in ENTIDAD column
        sub = df[(df['ENTIDAD_NORM'].str.contains(ent.upper())) & (df['DISTRITO_NUM']==d)]
    if len(sub)>0:
        # aggregate votes for partidos columns (heuristic: detect party columns)
        party_cols = [c for c in sub.columns if c.upper() in ('MORENA','PAN','PRI','PRD','PVEM','PT','MC','PES','RSP','NA','CI','FXM')]
        if len(party_cols)==0:
            # try uppercase names
            party_cols = [c for c in sub.columns if c.upper() in ('MORENA','PAN','PRI','PRD','PVEM','PT','MC','PES','RSP','NA','CI','FXM')]
        agg = sub[party_cols].sum()
        row = {'ENTIDAD':ent, 'DISTRITO':d}
        for p in party_cols:
            row[p] = int(agg[p])
        row['TOTAL_VOTOS'] = int(sub['TOTAL_BOLETAS'].sum()) if 'TOTAL_BOLETAS' in sub.columns else int(sub[party_cols].sum().sum())
        pv_rows.append(row)
    else:
        pv_rows.append({'ENTIDAD':ent, 'DISTRITO':d, 'ERROR':'no_data'})

out_df = pd.DataFrame(pv_rows)
out_df.to_csv(os.path.join(outdir,'pvem_mr_districts.csv'), index=False)
print('Wrote outputs/pvem_mr_districts.csv rows=', len(out_df))
