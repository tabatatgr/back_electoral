import shutil, pathlib, pandas as pd
BASE=pathlib.Path('.')
SIG = BASE/'data'/'siglado-diputados-2024.csv'
BACK = BASE/'data'/'siglado-diputados-2024.csv.bak'
COR = BASE/'data'/'siglado-diputados-2024.corrected.csv'

# backup
shutil.copy2(SIG, BACK)
print('Backup written to', BACK)

sig = pd.read_csv(SIG, dtype=str).fillna('')
# ensure partido_origen column exists
if 'partido_origen' not in sig.columns:
    sig['partido_origen'] = ''
# normalize entidad function
import unicodedata

def norm(s):
    s = str(s).strip().upper()
    s = unicodedata.normalize('NFKD', s)
    return ''.join(c for c in s if not unicodedata.combining(c))

sig['_ENT_N'] = sig['entidad'].apply(norm)
# rows to correct (from earlier list)
targets = [
 ('BAJA CALIFORNIA',3),('BAJA CALIFORNIA',4),('CHIAPAS',12),('HIDALGO',3),('MEXICO',11),('MEXICO',29),('MEXICO',31),('MICHOACAN',2),('TABASCO',1),('TABASCO',2),('TABASCO',3),('TABASCO',5)
]

changed = []
for entn,dist in targets:
    mask = (sig['_ENT_N']==entn) & (sig['distrito'].astype(str).str.strip()==str(dist))
    idxs = sig[mask].index.tolist()
    if not idxs:
        print('No rows for', entn, dist)
    for i in idxs:
        # only fill if partido_origen empty
        if not sig.at[i,'partido_origen']:
            sig.at[i,'partido_origen']='PAN|PRD|PRI'
            changed.append(i)

sig.to_csv(COR, index=False)
print('Wrote corrected copy with', len(changed), 'rows modified to', COR)
