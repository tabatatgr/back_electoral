import pandas as pd
import unicodedata
from pathlib import Path

BASE = Path('.')
SIGLADO = BASE / 'data' / 'siglado-diputados-2024.csv'
SUSPECT = BASE / 'outputs' / 'siglado_suspect_prd_rows.csv'
OUT_SUM = BASE / 'outputs' / 'siglado_prd_analysis.csv'
OUT_ROWS = BASE / 'outputs' / 'siglado_prd_matching_rows.csv'

sig = pd.read_csv(SIGLADO, dtype=str).fillna('')
sus = pd.read_csv(SUSPECT, dtype=str).fillna('')

# Normalizers
def norm(s):
    if not isinstance(s, str):
        s = str(s)
    s = s.strip().upper()
    s = unicodedata.normalize('NFKD', s)
    return ''.join(c for c in s if not unicodedata.combining(c))

sig['_ENT_N'] = sig['entidad'].apply(norm)
# ensure distrito numeric where possible
def to_int(x):
    try:
        return int(float(x))
    except Exception:
        return None

sig['distrito'] = sig['distrito'].apply(to_int)

sus['_ENT_N'] = sus['entidad'].apply(norm)
sus['distrito'] = sus['distrito'].apply(to_int)

rows = []
for _, r in sus.iterrows():
    ent = r['_ENT_N']
    dist = r['distrito']
    matched = sig[(sig['_ENT_N']==ent) & (sig['distrito']==dist)]
    if matched.empty:
        matched = sig[(sig['entidad'].str.upper()==r['entidad'].upper()) & (sig['distrito']==dist)]
    for _, m in matched.iterrows():
        partido_origen = m.get('partido_origen','').strip()
        grupo_parlamentario = m.get('grupo_parlamentario','').strip()
        coalicion = m.get('coalicion','').strip()
        nominadores = []
        if partido_origen:
            nominadores = [p.strip().upper() for p in partido_origen.split('|') if p.strip()]
        else:
            nominadores = [p.strip().upper() for p in grupo_parlamentario.split('|') if p.strip()]
        is_prd_in_partido_origen = 'PRD' in [p.strip().upper() for p in (partido_origen or '').split('|') if p.strip()]
        is_prd_in_grupo_parlamentario = 'PRD' in [p.strip().upper() for p in (grupo_parlamentario or '').split('|') if p.strip()]
        rows.append({
            'entidad': m.get('entidad',''),
            'entidad_norm': m.get('_ENT_N',''),
            'distrito': m.get('distrito',''),
            'coalicion': coalicion,
            'partido_origen': partido_origen,
            'grupo_parlamentario': grupo_parlamentario,
            'nominadores_list': '|'.join(nominadores),
            'nominadores_count': len(nominadores),
            'prd_in_partido_origen': is_prd_in_partido_origen,
            'prd_in_grupo_parlamentario': is_prd_in_grupo_parlamentario,
            'source_row_index': m.name
        })

if rows:
    dfrows = pd.DataFrame(rows)
    dfrows.to_csv(OUT_ROWS, index=False)
    grp = dfrows.groupby(['entidad_norm','distrito']).agg(
        partido_origen=('partido_origen', lambda s: '|'.join([x for x in s.unique() if x])),
        grupo_parlamentario=('grupo_parlamentario', lambda s: '|'.join([x for x in s.unique() if x])),
        nominadores_union=('nominadores_list', lambda s: '|'.join(sorted(set('|'.join(s).split('|')))) ),
        nominadores_count_min=('nominadores_count','min'),
        nominadores_count_max=('nominadores_count','max'),
        prd_in_partido_origen_any=('prd_in_partido_origen','any'),
        prd_in_grupo_parlamentario_any=('prd_in_grupo_parlamentario','any'),
        rows_found=('source_row_index','count')
    ).reset_index()
    grp.to_csv(OUT_SUM, index=False)
    print('Wrote', OUT_ROWS, 'and', OUT_SUM)
else:
    print('No matching rows found')
