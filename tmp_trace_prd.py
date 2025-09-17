import pandas as pd
from pathlib import Path
p = Path('outputs/mr_audit_by_district.csv')
if not p.exists():
    print('Missing audit file:', p)
    raise SystemExit(1)

df = pd.read_csv(p, dtype=str).fillna('')

# Determine assigned MR per district by priority:
# 1) mr_por_afiliacion (if non-empty)
# 2) mr_por_convenio (if non-empty)
# 3) winner_by_votes_valid
# 4) winner_by_votes_raw

assigned = []
for _, r in df.iterrows():
    ent = r['ENTIDAD']
    dist = r['DISTRITO']
    if str(r.get('mr_por_afiliacion','')).strip():
        party = r['mr_por_afiliacion'].strip()
        reason = 'afiliacion'
    elif str(r.get('mr_por_convenio','')).strip():
        party = r['mr_por_convenio'].strip()
        reason = 'convenio'
    elif str(r.get('winner_by_votes_valid','')).strip():
        party = r['winner_by_votes_valid'].strip()
        reason = 'winner_valid'
    else:
        party = r.get('winner_by_votes_raw','').strip()
        reason = 'winner_raw'
    assigned.append({'ENTIDAD': ent, 'DISTRITO': int(dist), 'assigned_party': party, 'reason': reason, 'postuladores': r.get('postuladores',''), 'siglado_ppn': r.get('siglado_ppn',''), 'winner_by_votes_valid': r.get('winner_by_votes_valid',''), 'winner_by_votes_raw': r.get('winner_by_votes_raw','')})

adf = pd.DataFrame(assigned)
adf.to_csv('outputs/mr_assigned_by_district_inferred.csv', index=False)

# Summary counts
counts = adf['assigned_party'].str.upper().value_counts()
counts.to_csv('outputs/mr_assigned_by_district_counts.csv')

# Filter PRD assignments
prd = adf[adf['assigned_party'].str.upper()=='PRD']
prd.to_csv('outputs/mr_prd_assigned_districts.csv', index=False)

print('Total MR assigned districts (rows):', len(adf))
print('Total PRD MR assigned:', len(prd))
print('\nPRD assigned districts:')
for _, r in prd.iterrows():
    print(f"{r['ENTIDAD']} {r['DISTRITO']} (reason={r['reason']}, postuladores={r['postuladores']}, ppn={r['siglado_ppn']}, winner_valid={r['winner_by_votes_valid']})")

print('\nWrote files: outputs/mr_assigned_by_district_inferred.csv, outputs/mr_assigned_by_district_counts.csv, outputs/mr_prd_assigned_districts.csv')
