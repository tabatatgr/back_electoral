import pandas as pd
import unicodedata
import re
import os

def norm(s):
    if pd.isna(s):
        return ''
    s = str(s).upper().strip()
    s = unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('ASCII')
    s = re.sub(r"\bMEXICO\b", "MEXICO", s)
    s = re.sub(r"\s+"," ", s)
    s = s.replace('.', '')
    return s

w = pd.read_csv('outputs/winners_by_district_siglado.csv')
w['ENT_NORM'] = w['ENTIDAD'].apply(norm)

pvem = w[w['WINNER_SIGLADO'].str.upper()=='PVEM'][['ENTIDAD','ENT_NORM','DISTRITO']]
print('PVEM districts to find:', len(pvem))

# read parquet
try:
    df = pd.read_parquet('data/computos_diputados_2024.parquet')
except Exception as e:
    import pyarrow.parquet as pq
    table = pq.read_table('data/computos_diputados_2024.parquet')
    df = table.to_pandas()

# normalize entidad in parquet
if 'ENTIDAD' in df.columns:
    df['ENT_NORM'] = df['ENTIDAD'].apply(norm)
elif 'entidad' in df.columns:
    df['ENT_NORM'] = df['entidad'].apply(norm)
else:
    df['ENT_NORM'] = ''

# ensure distrito column
if 'DISTRITO' in df.columns:
    df['DIST_NUM'] = df['DISTRITO']
elif 'distrito' in df.columns:
    df['DIST_NUM'] = df['distrito']
else:
    df['DIST_NUM'] = df.get('DIST_CH', df.get('DISTRITO_NUM', None))

rows = []
for _, r in pvem.iterrows():
    ent = r['ENT_NORM']
    d = int(r['DISTRITO'])
    # try exact match
    sub = df[(df['ENT_NORM']==ent) & (df['DIST_NUM']==d)]
    if len(sub)==0:
        # try contains (some parquet ENT_NORM may be 'SAN LUIS POTOSI' vs 'SAN LUIS POTOSI')
        sub = df[(df['ENT_NORM'].str.contains(ent)) & (df['DIST_NUM']==d)]
    if len(sub)==0:
        # try fuzzy: compare first word
        first = ent.split()[0]
        sub = df[(df['ENT_NORM'].str.contains(first)) & (df['DIST_NUM']==d)]
    if len(sub)==0:
        rows.append({'ENTIDAD':r['ENTIDAD'],'DISTRITO':d,'ERROR':'no_data'})
    else:
        # aggregate party votes
        possible_parties = ['MORENA','PAN','PRI','PRD','PVEM','PT','MC','PES','RSP','NA','CI','FXM']
        party_cols = [c for c in sub.columns if c.upper() in possible_parties]
        agg = sub[party_cols].sum()
        row = {'ENTIDAD':r['ENTIDAD'],'DISTRITO':d}
        for p in party_cols:
            row[p]=int(agg[p])
        row['TOTAL_VOTOS'] = int(sub['TOTAL_BOLETAS'].sum()) if 'TOTAL_BOLETAS' in sub.columns else int(sub[party_cols].sum().sum())
        rows.append(row)

out = pd.DataFrame(rows)
os.makedirs('outputs', exist_ok=True)
out.to_csv('outputs/pvem_mr_districts_fixed.csv', index=False)
print('Wrote outputs/pvem_mr_districts_fixed.csv rows=', len(out))
