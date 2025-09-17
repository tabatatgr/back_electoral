import pandas as pd
import numpy as np
from engine.procesar_diputados_v2 import procesar_diputados_v2
from engine.recomposicion import recompose_coalitions, parties_for

PARQUET = 'data/computos_diputados_2024.parquet'
SIGLADO = 'data/siglado-diputados-2024.csv'
OUT = 'outputs/mr_argmax_compare.csv'

# Reusing asignadip_py from tmp_compare_asignadip.py logic
from tmp_compare_asignadip import asignadip_py

# 1) Load parquet and recomposed using siglado
import pyarrow.parquet as pq
print('Leyendo parquet y recomponiendo con siglado...')
table = pq.read_table(PARQUET)
df_parq = table.to_pandas()
recomposed = recompose_coalitions(df_parq, 2024, 'diputados', rule='equal_residue_siglado', siglado_path=SIGLADO)

# 2) Calcular MR por argmax en cada distrito
parties = parties_for(2024)
if 'DISTRITO' not in recomposed.columns:
    raise SystemExit('Recomposed no tiene columna DISTRITO')

ganadores = recomposed.copy()
# determinar partido ganador por fila (argmax entre parties)
votes_matrix = ganadores[parties]
idx = votes_matrix.values.argmax(axis=1)
ganadores['GANADOR'] = [parties[i] for i in idx]

# Contar curules MR
ssd_tbl = ganadores.groupby('GANADOR').size().reset_index()
ssd_tbl.columns = ['partido','ssd']

# 3) Construir ssd vector en orden de votos nacionales
votos_nacionales = {p: int(recomposed[p].sum()) for p in parties}
partidos_order = sorted(votos_nacionales.keys(), key=lambda k: -votos_nacionales[k])
ssd_vec = {p: 0 for p in partidos_order}
for _, row in ssd_tbl.iterrows():
    if row['partido'] in ssd_vec:
        ssd_vec[row['partido']] = int(row['ssd'])

print('MR counts (ssd_vec):', ssd_vec)

# 4) Ejecutar asignadip_py con m = 200, S = 500
out_py = asignadip_py(votos_nacionales, ssd_vec, m=200, S=500, threshold=0.03, max_seats=300, max_distortion=0.08)

# 5) Ejecutar motor para comparar
res = procesar_diputados_v2(path_parquet=PARQUET, anio=2024, path_siglado=SIGLADO, max_seats=500, sistema='mixto', mr_seats=None, rp_seats=None, usar_coaliciones=True, sobrerrepresentacion=8.0, print_debug=False)

mr_engine = res.get('mr', {})
rp_engine = res.get('rp', {})
tot_engine = res.get('tot', {})

# 6) Guardar comparativa
rows = []
for p in partidos_order:
    rows.append({
        'partido': p,
        'votos': votos_nacionales.get(p,0),
        'ssd_argmax': ssd_vec.get(p,0),
        'mr_engine': mr_engine.get(p,0),
        'rp_engine': rp_engine.get(p,0),
        'tot_engine': tot_engine.get(p,0),
        'mr_py': out_py['mr'].get(p,0),
        'rp_py': out_py['rp'].get(p,0),
        'tot_py': out_py['tot'].get(p,0),
        'diff_tot': out_py['tot'].get(p,0) - tot_engine.get(p,0)
    })

pd.DataFrame(rows).to_csv(OUT, index=False)
print('Guardado', OUT)
