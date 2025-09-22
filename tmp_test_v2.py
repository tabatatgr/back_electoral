import json
from engine.procesar_diputados_v2 import procesar_diputados_v2
import os

path_parquet = os.path.join(os.path.dirname(__file__), 'data', 'computos_diputados_2024.parquet')
path_siglado = os.path.join(os.path.dirname(__file__), 'data', 'siglado-diputados-2024.csv')

print('Calling procesar_diputados_v2 with max_seats=128...')
try:
    res = procesar_diputados_v2(
        path_parquet=path_parquet,
        anio=2024,
        path_siglado=path_siglado if os.path.exists(path_siglado) else None,
        max_seats=128,
        sistema='mr',
        mr_seats=64,
        rp_seats=64,
        usar_coaliciones=True,
        print_debug=True
    )
    print('\n--- RESULT SUMMARY ---')
    print('Keys:', list(res.keys()))
    if 'kpis' in res:
        print('kpis.total_escanos:', res['kpis'].get('total_escanos'))
    tot = res.get('tot', {})
    s = sum(int(v) for v in tot.values()) if tot else 0
    print('sum tot =', s)
    mr = res.get('mr', {})
    print('sum mr =', sum(int(v) for v in mr.values()) if mr else 0)
    rp = res.get('rp', {})
    print('sum rp =', sum(int(v) for v in rp.values()) if rp else 0)
    print('meta:', res.get('meta'))
    print('\nFull tot (first 10):', dict(list(tot.items())[:10]))
except Exception as e:
    print('Exception during run:', e)
    import traceback
    traceback.print_exc()

print('done')
