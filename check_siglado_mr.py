import pandas as pd

SIG = 'data/siglado-diputados-2024.csv'
try:
    df = pd.read_csv(SIG)
except Exception as e:
    print('ERROR leyendo siglado:', e)
    raise

# Normalizar columnas probables
cols = [c.lower().strip() for c in df.columns]
# Map possible names
ent_col = None
if 'entidad' in cols:
    ent_col = df.columns[cols.index('entidad')]
elif 'entidad_ascii' in cols:
    ent_col = df.columns[cols.index('entidad_ascii')]
else:
    ent_col = df.columns[0]

dist_col = None
if 'distrito' in cols:
    dist_col = df.columns[cols.index('distrito')]
else:
    # try variants
    for c in df.columns:
        if 'distrito' in c.lower():
            dist_col = c
            break

gp_col = None
for name in ['grupo_parlamentario','grupo_parlamentario'.upper(),'partido_origen','partido_origen'.upper(),'partido']:
    if name in df.columns:
        gp_col = name
        break
if gp_col is None:
    # fallback to any column that looks like party
    for c in df.columns:
        if c.lower().startswith('grupo') or c.lower().startswith('partido'):
            gp_col = c
            break

print('Usando columnas -> entidad:', ent_col, ', distrito:', dist_col, ', gp:', gp_col)

if dist_col is None or gp_col is None:
    print('No se detectaron columnas necesarias en siglado')
else:
    # Normalize strings
    df['_ent'] = df[ent_col].astype(str).str.strip().str.upper()
    df['_dist'] = df[dist_col].astype(int)
    df['_gp'] = df[gp_col].astype(str).str.strip().str.upper()

    # group by unique distrito (entidad+dist) and take first non-null gp
    grouped = df.groupby(['_ent','_dist'])['_gp'].agg(lambda x: x.dropna().iloc[0] if len(x.dropna())>0 else None)
    counts = grouped.value_counts()
    total = counts.sum()
    print('\nUnique district winners count total:', total)
    print('\nTop winners from siglado (unique districts):')
    print(counts.head(30).to_dict())

    # print MORENA count
    print('\nMORENA unique districts:', int(counts.get('MORENA',0)))

print('\nDone')
