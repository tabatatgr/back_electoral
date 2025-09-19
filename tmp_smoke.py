from engine.procesar_diputados_v2 import procesar_diputados_v2
from engine.procesar_senadores_v2 import procesar_senadores_v2

print('Arrancando smoke tests')

try:
    res = procesar_diputados_v2(
        path_parquet='data/computos_diputados_2024.parquet',
        anio=2024,
        path_siglado='data/siglado-diputados-2024.csv',
        max_seats=100,
        sistema='mixto',
        mr_seats=60,
        rp_seats=40,
        usar_coaliciones=True,
        print_debug=False,
    )
    print('procesar_diputados_v2 OK - keys:', list(res.keys()))
except Exception as e:
    print('ERROR en procesar_diputados_v2:', e)

try:
    res2 = procesar_senadores_v2(
        path_parquet='data/computos_senado_2024.parquet',
        anio=2024,
        path_siglado=None,
        max_seats=100,
        sistema='mixto',
        mr_seats=60,
        rp_seats=40,
    )
    print('procesar_senadores_v2 OK - keys:', list(res2.keys()))
except Exception as e:
    print('ERROR en procesar_senadores_v2:', e)

print('Smoke tests finalizados')
