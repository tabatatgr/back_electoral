import pandas as pd
import os

in_path = 'outputs/mr_audit_by_district.csv'
out_path = 'outputs/prd_mr_sources.csv'

if not os.path.exists(in_path):
    print('input audit CSV not found:', in_path)
    raise SystemExit(1)

df = pd.read_csv(in_path, dtype=str).fillna('')
# Normalize uppercase trimmed
for col in ['siglado_ppn','postuladores','mr_por_convenio','mr_por_afiliacion','winner_by_votes_raw','winner_by_votes_valid']:
    if col in df.columns:
        df[col+'_N'] = df[col].astype(str).str.strip().str.upper()
    else:
        df[col+'_N'] = ''

# Flags
cond = (
    (df['siglado_ppn_N'] == 'PRD') |
    (df['postuladores_N'].str.contains('PRD')) |
    (df['mr_por_convenio_N'] == 'PRD') |
    (df['mr_por_afiliacion_N'] == 'PRD') |
    (df['winner_by_votes_raw_N'] == 'PRD') |
    (df['winner_by_votes_valid_N'] == 'PRD')
)

res = df[cond].copy()
# Select cols to output
cols = ['ENTIDAD','DISTRITO','postuladores','siglado_ppn','mr_por_convenio','mr_por_afiliacion','winner_by_votes_raw','winner_by_votes_valid','PVEM_raw_gana_sin_nominar','incompleto_siglado']
cols_out = [c for c in cols if c in res.columns]
res.to_csv(out_path, index=False, columns=cols_out)
print('Wrote', out_path, 'rows:', len(res))
