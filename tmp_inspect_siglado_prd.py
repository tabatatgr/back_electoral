import pandas as pd
from pathlib import Path

SIG='data/siglado-diputados-2024.csv'
if not Path(SIG).exists():
    print('siglado file not found:', SIG)
    raise SystemExit(1)

df=pd.read_csv(SIG, dtype=str, keep_default_na=False)
# normalize column names
cols=[c.strip().lower() for c in df.columns]
print('columns:', cols)

keys=[
    ('BAJA CALIFORNIA',3),('CHIAPAS',12),('HIDALGO',3),('MICHOACAN',2),
    ('MEXICO',11),('MEXICO',29),('MEXICO',31),('TABASCO',1),('TABASCO',2),('TABASCO',3),('TABASCO',5),('BAJA CALIFORNIA',4)
]

# find possible entidad columns
ent_cols=[c for c in df.columns if 'entidad' in c.lower()]
dist_cols=[c for c in df.columns if 'distrito' in c.lower()]
print('ent_cols', ent_cols, 'dist_cols', dist_cols)

for ent,dist in keys:
    mask = pd.Series([False]*len(df))
    for ec in ent_cols:
        mask = mask | (df[ec].astype(str).str.upper().str.strip() == ent.upper())
    for dc in dist_cols:
        mask = mask & (pd.to_numeric(df[dc], errors='coerce').fillna(0).astype(int) == dist)
    sel = df[mask]
    print('\n---', ent, dist, 'rows:', len(sel))
    if len(sel)>0:
        print(sel.to_string(index=False))
    else:
        # try fuzzy search
        mask2 = df[ent_cols[0]].astype(str).str.upper().str.contains(ent.upper()) & (pd.to_numeric(df[dist_cols[0]], errors='coerce').fillna(0).astype(int) == dist)
        if mask2.any():
            print('fuzzy match:')
            print(df[mask2].to_string(index=False))
        else:
            print('no match in siglado for', ent, dist)
