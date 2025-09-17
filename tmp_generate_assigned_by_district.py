import pandas as pd
import os

in_path = 'outputs/mr_audit_by_district.csv'
out_path = 'outputs/assigned_by_district_with_source.csv'
counts_out = 'outputs/assigned_counts.csv'

if not os.path.exists(in_path):
    print('input audit CSV not found:', in_path)
    raise SystemExit(1)

df = pd.read_csv(in_path, dtype=str).fillna('')

# Normalize
for c in ['mr_por_afiliacion','mr_por_convenio','siglado_ppn','winner_by_votes_valid','winner_by_votes_raw']:
    if c in df.columns:
        df[c+'_N'] = df[c].astype(str).str.strip().str.upper()
    else:
        df[c+'_N'] = ''

assigned = []
for _, r in df.iterrows():
    ent = r['ENTIDAD']
    dist = r['DISTRITO']
    source = ''
    party = ''
    # Priority: afiliacion override > por_convenio > votos_valid > votos_raw > siglado_ppn
    if r.get('mr_por_afiliacion_N',''):
        party = r['mr_por_afiliacion_N']
        source = 'afiliacion_override'
    elif r.get('mr_por_convenio_N',''):
        party = r['mr_por_convenio_N']
        source = 'siglado_convenio'
    elif r.get('winner_by_votes_valid_N','') and r.get('winner_by_votes_valid_N','').upper() != '':
        party = r['winner_by_votes_valid_N']
        source = 'votes_valid'
    elif r.get('winner_by_votes_raw_N','') and r.get('winner_by_votes_raw_N','').upper() != '':
        party = r['winner_by_votes_raw_N']
        source = 'votes_raw'
    elif r.get('siglado_ppn_N',''):
        party = r['siglado_ppn_N']
        source = 'siglado_ppn'
    else:
        party = 'UNKNOWN'
        source = 'unknown'
    assigned.append({
        'ENTIDAD': ent,
        'DISTRITO': dist,
        'assigned_party': party,
        'assigned_source': source,
        'postuladores': r.get('postuladores',''),
        'siglado_ppn': r.get('siglado_ppn',''),
        'mr_por_convenio': r.get('mr_por_convenio',''),
        'mr_por_afiliacion': r.get('mr_por_afiliacion',''),
        'winner_by_votes_valid': r.get('winner_by_votes_valid',''),
        'winner_by_votes_raw': r.get('winner_by_votes_raw','')
    })

out_df = pd.DataFrame(assigned)
os.makedirs('outputs', exist_ok=True)
out_df.to_csv(out_path, index=False)
print('Wrote', out_path, 'rows:', len(out_df))

# Counts
cnt = out_df['assigned_party'].value_counts().rename_axis('party').reset_index(name='count')
cnt.to_csv(counts_out, index=False)
print('Wrote', counts_out)
print(cnt.to_string(index=False))
