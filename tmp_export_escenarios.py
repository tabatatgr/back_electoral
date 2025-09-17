import pandas as pd
from engine.procesar_diputados_v2 import procesar_diputados_v2

PARQUET = 'data/computos_diputados_2024.parquet'
SIGLADO = 'data/siglado-diputados-2024.normalized.csv'
from datetime import datetime
OUT = f"outputs/escenarios_diputados_custom.{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

# Scenarios requested by user:
# - 500 seats: 300 MR + 200 RP
# - 500 seats: 250 MR + 250 RP
# - 500 seats: 300 MR + 200 PM (primera minoría) -> usar_pm=True
# - 500 seats: 0 MR + 500 RP
# - 500 seats: 300 MR + 100 RP + 100 PM
scenarios = [
    # dejar mr_seats=None para usar MR recomputado por el siglado (no forzar magnitud MR)
    ('500_300MR_200RP', dict(max_seats=500, sistema='mixto', mr_seats=None, rp_seats=200)),
    ('500_250MR_250RP', dict(max_seats=500, sistema='mixto', mr_seats=250, rp_seats=250)),
    ('500_300MR_200PM', dict(max_seats=500, sistema='mixto', mr_seats=300, rp_seats=200, usar_pm=True, pm_seats=200)),
    ('500_0MR_500RP', dict(max_seats=500, sistema='rp', mr_seats=0, rp_seats=500)),
    ('500_300MR_100RP_100PM', dict(max_seats=500, sistema='mixto', mr_seats=300, rp_seats=100, usar_pm=True, pm_seats=100)),
]

# función simple para simular PM (primera minoría) si el engine no lo tiene: asignar pm_seats a los segundos lugares por votos MR
# esto es aproximado: extraemos recomposed y por distrito ordenamos votos, tomamos segundo puesto

def simulate_pm_by_runnerup(recomposed_df, pm_seats, partidos):
    # recomposed_df debe contener columnas ENTIDAD,DISTRITO y partidos con votos
    rows = []
    for _, row in recomposed_df.iterrows():
        votos = [(p, float(row.get(p,0))) for p in partidos]
        votos_sorted = sorted(votos, key=lambda x: -x[1])
        if len(votos_sorted) >= 2:
            segundo = votos_sorted[1][0]
            rows.append(segundo)
    # contar moda hasta pm_seats
    from collections import Counter
    c = Counter(rows)
    pm_dict = {p: 0 for p in partidos}
    for p, _ in c.most_common()[:pm_seats]:
        pm_dict[p] = c[p]
    return pm_dict


with pd.ExcelWriter(OUT) as writer:
    for name, params in scenarios:
        print('ejecutando', name, params)
        usar_pm = params.pop('usar_pm', False)
        # enforce VVE 3% and sobrerrepresentacion 8pp inside call
        res = procesar_diputados_v2(path_parquet=PARQUET, anio=2024, path_siglado=SIGLADO, max_seats=params.get('max_seats',500), sistema=params.get('sistema','mixto'), mr_seats=params.get('mr_seats',None), rp_seats=params.get('rp_seats',None), usar_coaliciones=True, sobrerrepresentacion=8.0, umbral=0.03, print_debug=False)
        mr = res.get('mr', {})
        rp = res.get('rp', {})
        tot = res.get('tot', {})
        partidos = list(tot.keys())
        df = pd.DataFrame([{
            'partido': p,
            'mr': mr.get(p,0),
            'rp': rp.get(p,0),
            'tot': tot.get(p,0)
        } for p in partidos])

        # simular PM si pide: usar recomposition para elegir segundos lugares por DIST_UID
        if usar_pm:
            try:
                from engine.recomposicion import recompose_coalitions
                import pyarrow.parquet as pq
                table = pq.read_table(PARQUET)
                df_parq = table.to_pandas()
                recomposed = recompose_coalitions(df_parq, 2024, 'diputados', rule='equal_residue_siglado', siglado_path=SIGLADO)
                pm_assigned = simulate_pm_by_runnerup(recomposed, params.get('pm_seats',100), partidos)
                df['pm'] = df['partido'].map(lambda p: pm_assigned.get(p,0))
            except Exception as e:
                print('Error simulando PM:', e)
                df['pm'] = 0
        else:
            df['pm'] = 0

        df.to_excel(writer, sheet_name=name[:31], index=False)

print('Exportado a', OUT)
