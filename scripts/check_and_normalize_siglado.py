import pandas as pd
import os
import unicodedata

IN_FILES = [
    'data/siglado-diputados-2024.csv',
    'data/siglado-diputados-2024.fixed.csv'
]
OUT = 'data/siglado-diputados-2024.normalized.csv'

def norm(s):
    if pd.isna(s):
        return s
    s = str(s).strip().upper()
    s = ''.join(ch for ch in unicodedata.normalize('NFKD', s) if not unicodedata.combining(ch))
    s = s.replace('  ', ' ')
    # common normalization
    s = s.replace('MEXICO', 'MXICO') if 'CIUDAD DE MEXICO' in s else s
    s = s.replace('CIUDAD DE MXICO', 'CIUDAD DE MXICO')
    s = s.replace('\u00A0',' ')
    return s

rows = []
summary = []

for f in IN_FILES:
    if not os.path.exists(f):
        print('no existe', f)
        continue
    df = pd.read_csv(f)
    # normalize columns names
    df.columns = [c.strip() for c in df.columns]
    if 'entidad_ascii' in df.columns:
        df['ENTIDAD_N'] = df['entidad_ascii'].map(norm)
    elif 'entidad' in df.columns:
        df['ENTIDAD_N'] = df['entidad'].map(norm)
    else:
        df['ENTIDAD_N'] = ''
    if 'distrito' in df.columns:
        df['DISTRITO_N'] = pd.to_numeric(df['distrito'], errors='coerce').fillna(0).astype(int)
    else:
        df['DISTRITO_N'] = 0
    df['KEY'] = df['ENTIDAD_N'].astype(str) + '-' + df['DISTRITO_N'].astype(str)
    unique_keys = df['KEY'].nunique()
    total_rows = len(df)
    summary.append((f, total_rows, unique_keys))
    rows.append(df)
    print(f, 'rows=', total_rows, 'unique_keys=', unique_keys)

# merge and prefer fixed over original
all_df = pd.concat(rows, ignore_index=True)
all_df = all_df.drop_duplicates(subset=['KEY','coalicion','grupo_parlamentario'], keep='last')
# build normalized output with ENTIDAD_N,DISTRITO_N,coalicion,grupo_parlamentario
out_df = all_df[['ENTIDAD_N','DISTRITO_N','coalicion','grupo_parlamentario']].copy()
out_df.columns = ['entidad_ascii','distrito','coalicion','grupo_parlamentario']
# ensure sorted by entidad,distrito
out_df = out_df.sort_values(['entidad_ascii','distrito'])

if len(out_df) > 0:
    out_df.to_csv(OUT, index=False)
    print('WROTE', OUT, 'rows=', len(out_df), 'unique_keys=', out_df.shape[0])
else:
    print('No rows to write')

# show stats per entidad
if len(out_df)>0:
    ent_counts = out_df.groupby('entidad_ascii').size().sort_values(ascending=False)
    print('\nTop entidades and district counts:')
    print(ent_counts.head(20))

print('\nSummary:')
for s in summary:
    print(s)
