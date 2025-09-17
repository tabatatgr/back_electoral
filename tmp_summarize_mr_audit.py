import pandas as pd
from pathlib import Path

p = Path('outputs/mr_audit_by_district.csv')
if not p.exists():
    print('Audit file not found:', p)
    raise SystemExit(1)

df = pd.read_csv(p, dtype=str).fillna('')
# normalize

df['mr_por_convenio_up'] = df['mr_por_convenio'].str.upper().fillna('')
counts = df['mr_por_convenio_up'].value_counts().reset_index()
counts.columns = ['party','count']
counts.to_csv('outputs/mr_safe_mode_party_counts.csv', index=False)

# rows where convention assignment is PRD
prd_rows = df[df['mr_por_convenio_up']=='PRD']
prd_rows.to_csv('outputs/mr_safe_mode_prd_rows.csv', index=False)

# rows with empty mr_por_convenio but winner_by_votes_valid exists and differs
mask = (df['mr_por_convenio_up']=='') & (df['winner_by_votes_valid'].str.upper()!='')
df_discrep = df[mask].copy()
df_discrep['winner_up'] = df_discrep['winner_by_votes_valid'].str.upper()
df_discrep = df_discrep[df_discrep['winner_up']!='']
df_discrep.to_csv('outputs/mr_safe_mode_discrepancies.csv', index=False)

print('Wrote outputs/mr_safe_mode_party_counts.csv (party counts)')
print('PRD convention rows:', len(prd_rows))
print('Discrepancies (mr_por_convenio empty but winner valid present):', len(df_discrep))
print('\nTop parties by mr_por_convenio:')
print(counts.head(20).to_string(index=False))
