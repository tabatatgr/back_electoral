import pandas as pd
import os

IN = 'data/siglado-diputados-2024.normalized.csv'
OUT = 'data/siglado-diputados-2024.engine.csv'

if not os.path.exists(IN):
    print('missing', IN)
    raise SystemExit(1)

df = pd.read_csv(IN)
# ensure columns: entidad_ascii,distrito,coalicion,grupo_parlamentario
if 'entidad_ascii' not in df.columns:
    if 'entidad' in df.columns:
        df['entidad_ascii'] = df['entidad']
    else:
        df['entidad_ascii'] = df.iloc[:,0]

# create composite key
df['KEY'] = df['entidad_ascii'].astype(str) + '|' + df['distrito'].astype(str)
# assign unique id per KEY
unique_keys = df['KEY'].drop_duplicates().reset_index(drop=True)
map_id = {k:i+1 for i,k in enumerate(unique_keys)}

# map to numeric distrito unique
df['distrito_unico'] = df['KEY'].map(map_id)
# write engine-friendly file: entidad,distrito,coalicion,grupo_parlamentario
out = df[['entidad_ascii','distrito_unico','coalicion','grupo_parlamentario']].copy()
out.columns = ['entidad','distrito','coalicion','grupo_parlamentario']
out.to_csv(OUT,index=False)
print('WROTE', OUT, 'rows=', len(out), 'unique_distritos=', out['distrito'].nunique())
