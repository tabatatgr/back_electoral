import pandas as pd
from pathlib import Path
from engine.recomposicion import normalize_entidad_ascii

prd_diag = Path('outputs/prd_mr_diagnostic.csv')
siglado = Path('data/siglado-diputados-2024.csv')
out = Path('outputs/siglado_suspect_prd_rows.csv')

if not prd_diag.exists():
    print('Diagnostic CSV not found:', prd_diag)
    raise SystemExit(1)
if not siglado.exists():
    print('Siglado file not found:', siglado)
    raise SystemExit(1)

df_diag = pd.read_csv(prd_diag, dtype=str)
keys = set()
for _, r in df_diag.iterrows():
    ent = r.get('ENTIDAD')
    dist = r.get('DISTRITO')
    try:
        dist_i = int(float(dist))
    except Exception:
        try:
            dist_i = int(str(dist))
        except Exception:
            dist_i = 0
    keys.add((normalize_entidad_ascii(ent), dist_i))

s = pd.read_csv(siglado, dtype=str, keep_default_na=False)
# find entity and distrito columns
ent_cols = [c for c in s.columns if 'entidad' in c.lower()]
dist_cols = [c for c in s.columns if 'distrito' in c.lower()]

if not ent_cols or not dist_cols:
    print('No entidad/distrito columns found in siglado')
    raise SystemExit(1)

entc = ent_cols[0]
distc = dist_cols[0]

rows = []
for i, r in s.iterrows():
    ent_val = r.get(entc, '')
    dist_val = r.get(distc, '')
    try:
        dist_i = int(pd.to_numeric(dist_val, errors='coerce'))
    except Exception:
        try:
            dist_i = int(str(dist_val))
        except Exception:
            dist_i = 0
    ent_n = normalize_entidad_ascii(ent_val)
    if (ent_n, dist_i) in keys:
        row = r.to_dict()
        row['_ENT_N'] = ent_n
        row['_DIST'] = dist_i
        rows.append(row)

if rows:
    out_df = pd.DataFrame(rows)
    out.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out, index=False)
    print('Wrote', out, 'rows:', len(out_df))
else:
    print('No matching rows found in siglado for PRD diagnostics')
