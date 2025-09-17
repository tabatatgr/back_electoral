import pandas as pd
from pathlib import Path
p = Path('outputs/mr_audit_by_district.csv')
if not p.exists():
    print('missing', p)
    raise SystemExit(1)

df = pd.read_csv(p, dtype=str).fillna('')
mask = (df['mr_por_convenio'].str.strip()=='') & (df['winner_by_votes_valid'].str.strip()!='')
disc = df[mask].copy()
cols = ['ENTIDAD','DISTRITO','postuladores','winner_by_votes_raw','winner_by_votes_valid','siglado_ppn','mr_por_convenio']
if not disc.empty:
    disc.to_csv('outputs/mr_safe_mode_discrepancies.csv', index=False)
    # summary by winner
    summary = disc['winner_by_votes_valid'].str.upper().value_counts().reset_index()
    summary.columns = ['party','count']
    summary.to_csv('outputs/mr_safe_mode_discrepancies_summary.csv', index=False)
    print('Wrote', 'outputs/mr_safe_mode_discrepancies.csv', 'rows:', len(disc))
    print('Wrote summary outputs/mr_safe_mode_discrepancies_summary.csv')
else:
    print('No discrepancies found')
