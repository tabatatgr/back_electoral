import pandas as pd
import pyarrow.parquet as pq
from collections import Counter
import re

PARQUET = 'data/computos_diputados_2024.parquet'
SIGLADO = 'data/siglado-diputados-2024.csv'
OUT_FULL = 'outputs/mr_diagnostics_full.csv'
OUT_MISSING = 'outputs/mr_diagnostics_missing_siglado.csv'
OUT_SIGLADO_CLEAN = 'data/siglado-diputados-2024.clean.csv'

print('Leyendo parquet...')
tbl = pq.read_table(PARQUET)
df = tbl.to_pandas()
print('Parquet columns:', df.columns.tolist())

print('Leyendo siglado...')
sig = pd.read_csv(SIGLADO, dtype=str)
print('Siglado rows:', len(sig))

# Normalizadores simples
def norm_ent(s):
    if pd.isna(s):
        return ''
    s = str(s).strip().upper()
    s = re.sub(r'[^A-Z0-9 ]', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s

sig['entidad_key'] = sig['entidad'].apply(norm_ent)
sig['distrito'] = sig['distrito'].astype(int)
sig['DIST_CH'] = sig['distrito'].astype(str).str.zfill(3)

# Build mapping entidad+dist -> dominante (coalicion)
sig_map = sig.dropna(subset=['entidad_key','DIST_CH']).set_index(['entidad_key','DIST_CH'])['coalicion'].to_dict()

# Detect party-like columns in parquet
possible_party_cols = [c for c in df.columns if re.match(r'^[A-ZÑ]+$', str(c)) and c.upper() not in ('ENTIDAD','DISTRITO')]
# also include common tokens
extras = [c for c in df.columns if c.upper() in ('MORENA','PAN','PRI','PRD','PVEM','MC','PT','PES','RSP')]
party_cols = sorted(list(set(possible_party_cols + extras)))
print('Detected party-like columns:', party_cols)

rows = []
miss_rows = []
for i, g in df.groupby(['ENTIDAD','DISTRITO']):
    entidad, distrito = i
    ent_key = norm_ent(entidad)
    dist_ch = int(distrito)
    dist_ch_s = str(dist_ch).zfill(3)
    # gather votes per party-like col
    votes = {}
    present_cols = []
    for c in party_cols:
        if c in g.columns:
            s = g[c].sum()
            if pd.notna(s) and s>0:
                votes[c] = int(s)
                present_cols.append(c)
    total_votes = sum(votes.values())
    # sort
    sorted_votes = sorted(votes.items(), key=lambda x: x[1], reverse=True)
    winners = []
    if sorted_votes:
        topv = sorted_votes[0][1]
        winners = [p for p,v in sorted_votes if v==topv]
    # get siglado dominant
    dom = sig_map.get((ent_key, dist_ch_s))
    has_siglado = dom is not None
    row = {
        'ENTIDAD': entidad,
        'ENT_KEY': ent_key,
        'DISTRITO': int(distrito),
        'DIST_CH': dist_ch_s,
        'N_PARTY_COLS': len(present_cols),
        'PARTY_COLS': '|'.join(present_cols),
        'TOTAL_VOTOS': int(total_votes),
        'N_WINNERS': len(winners),
        'WINNERS': '|'.join(winners),
        'SIGLADO_DOMINANTE': dom if dom is not None else '',
        'SIGLADO_PRESENT': has_siglado
    }
    rows.append(row)
    if not has_siglado:
        miss_rows.append(row)

out_df = pd.DataFrame(rows)
out_df.to_csv(OUT_FULL, index=False)
print('Wrote', OUT_FULL, 'rows=', len(out_df))

miss_df = pd.DataFrame(miss_rows)
miss_df.to_csv(OUT_MISSING, index=False)
print('Wrote', OUT_MISSING, 'miss=', len(miss_df))

# Create a cleaned siglado by grouping entidad+distrito and picking mode of coalicion
clean = sig.copy()
clean['coalicion_norm'] = clean['coalicion'].astype(str).str.strip()
cleaned = clean.groupby(['entidad_key','distrito'], as_index=False).agg({'coalicion_norm': lambda x: Counter(x).most_common(1)[0][0], 'grupo_parlamentario': lambda x: Counter(x).most_common(1)[0][0]})
# write cleaned as CSV with columns aligned to original
cleaned = cleaned.rename(columns={'coalicion_norm':'coalicion','distrito':'distrito','entidad_key':'entidad_key'})
# create display entidad from entidad_key (best-effort)
cleaned['entidad'] = cleaned['entidad_key']
cleaned['DIST_CH'] = cleaned['distrito'].astype(int).astype(str).str.zfill(3)
cleaned.to_csv(OUT_SIGLADO_CLEAN, index=False)
print('Wrote cleaned siglado to', OUT_SIGLADO_CLEAN, 'rows=', len(cleaned))
