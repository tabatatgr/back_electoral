import pandas as pd
SIG = 'data/siglado-diputados-2024.csv'

df = pd.read_csv(SIG)
# normalize cols
ent_col = 'entidad' if 'entidad' in df.columns else 'entidad_ascii' if 'entidad_ascii' in df.columns else df.columns[0]
dist_col = 'distrito' if 'distrito' in df.columns else None
gp_col = None
for c in ['grupo_parlamentario','partido_origen','partido']:
    if c in df.columns:
        gp_col = c
        break
if gp_col is None:
    raise SystemExit('No gp column')

# normalize values
df['_ent'] = df[ent_col].astype(str).str.strip().str.upper()
if dist_col:
    df['_dist'] = df[dist_col].astype(int)
else:
    df['_dist'] = 0

df['_gp'] = df[gp_col].astype(str).str.strip().str.upper()

# compute mode per district
mode = df.groupby(['_ent','_dist'])['_gp'].agg(lambda x: x.mode().iloc[0] if not x.mode().empty else x.dropna().iloc[0] if len(x.dropna())>0 else None)
counts = mode.value_counts()
print('Total unique districts (mode):', counts.sum())
print('Top winners (mode):')
print(counts.head(30).to_dict())
print('\nMORENA districts (mode):', int(counts.get('MORENA',0)))
