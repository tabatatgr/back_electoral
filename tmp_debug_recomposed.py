import pyarrow.parquet as pq
import pandas as pd
from engine.recomposicion import recompose_coalitions

PARQUET='data/computos_diputados_2024.parquet'
SIGLADO='data/siglado-diputados-2024.normalized.csv'

table = pq.read_table(PARQUET)
df = table.to_pandas()
print('parquet shape', df.shape)
recomp = recompose_coalitions(df, 2024, 'diputados', rule='equal_residue_siglado', siglado_path=SIGLADO)
print('recomp shape', recomp.shape)
print('columns sample:', [c for c in recomp.columns if c.upper() in ('PVEM','MORENA','PAN','PRI')])
# winners by district via recomposed
parties = [c for c in recomp.columns if isinstance(c, str) and c.upper() in ('PVEM','MORENA','PAN','PRI','PRD','PT','MC','PES','RSP','NA','CI','FXM')]
print('detected parties cols', parties)
# compute winners
winners = recomp.groupby(['ENTIDAD','DISTRITO'])[parties].sum().idxmax(axis=1)
print('winners_by_district sample:', winners.head(10))
print('PVEM district wins count recomposed:', (winners.str.upper()=='PVEM').sum())
# show rows for PVEM-winning districts from outputs/winners_by_district_siglado.csv
pvem_districts = [('CHIAPAS',1),('SAN LUIS POTOSI',1),('SAN LUIS POTOSI',2),('SAN LUIS POTOSI',3),('SAN LUIS POTOSI',6),('SAN LUIS POTOSI',7)]
for ent,d in pvem_districts:
    # normalize names in recomposed ENTIDAD
    sub = recomp[(recomp['ENTIDAD'].str.upper().str.contains(ent)) & (recomp['DISTRITO']==d)]
    print('\nDistrict', ent, d, 'rows', len(sub))
    if len(sub)>0:
        print(sub[[col for col in sub.columns if col in parties]].sum())
    else:
        print('no rows matched (name mismatch)')
