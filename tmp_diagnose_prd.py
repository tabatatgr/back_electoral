import pandas as pd
import os

path = 'outputs/mr_audit_by_district.csv'
out = 'outputs/prd_mr_diagnostic.csv'

if not os.path.exists(path):
    print('Audit CSV not found:', path)
    raise SystemExit(1)

df = pd.read_csv(path, dtype=str)
# normalize columns
for c in ['ENTIDAD','DISTRITO','postuladores','winner_by_votes_raw','winner_by_votes_valid','siglado_ppn','mr_por_convenio','mr_por_afiliacion']:
    if c not in df.columns:
        df[c] = ''

df['DISTRITO'] = pd.to_numeric(df['DISTRITO'], errors='coerce').fillna(0).astype(int)

# rows where MR asignado por convenio o afiliacion es PRD
mask_convenio = df['mr_por_convenio'].str.upper().fillna('') == 'PRD'
mask_afiliacion = df['mr_por_afiliacion'].str.upper().fillna('') == 'PRD'
mask_any = mask_convenio | mask_afiliacion

res = df[mask_any].copy()
res.to_csv(out, index=False)

# Additional checks: show postuladores in those rows, and whether winners match
print('PRD MR assigned rows count:', len(res))
if len(res) > 0:
    print('\nSample rows:')
    print(res[['ENTIDAD','DISTRITO','postuladores','winner_by_votes_raw','winner_by_votes_valid','siglado_ppn','mr_por_convenio','mr_por_afiliacion']].head(20).to_string(index=False))

# Count by postuladores pattern
from collections import Counter
patterns = [ (tuple(sorted([p.strip().upper() for p in (s or '').split('|') if p.strip()]))) for s in res['postuladores'] ]
cnt = Counter(patterns)
print('\nTop postuladores patterns for PRD-assigned MR:')
for k,v in cnt.most_common(10):
    print(k, v)

# Check if these PRD assignments occur in districts where winner_by_votes_raw is PRD
raw_wins = res[res['winner_by_votes_raw'].str.upper() == 'PRD']
print('\nRows where PRD won by raw votes but still assigned PRD MR (count):', len(raw_wins))

# Check PVEM flags etc
pvem_flags = res[res['PVEM_raw_gana_sin_nominar'].astype(int)==1] if 'PVEM_raw_gana_sin_nominar' in res.columns else pd.DataFrame()
print('Rows with PVEM_raw_gana_sin_nominar flag among PRD-assigned:', len(pvem_flags))

print('\nDiagnostic CSV written to', out)
