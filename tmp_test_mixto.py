from engine.procesar_diputados_v2 import procesar_diputados_v2, parties_for
import json

if __name__ == '__main__':
    path_parquet = 'data/computos_diputados_2024.parquet'
    partidos = parties_for(2024)
    res = procesar_diputados_v2(
        path_parquet=path_parquet,
        partidos_base=partidos,
        anio=2024,
        path_siglado='data/siglado-diputados-2024.csv',
        max_seats=300,
        sistema='mixto',
        mr_seats=128,
        rp_seats=None,
        usar_coaliciones=True,
        sobrerrepresentacion=8.0,
        umbral=0.03,
        seed=123,
        print_debug=True
    )

    print('MR sum:', sum(res.get('mr',{}).values()))
    print('Has scaled_info in meta?:', 'scaled_info' in res.get('meta', {}))
    if 'scaled_info' in res.get('meta', {}):
        si = res['meta']['scaled_info']
        print('scaled_info summary:', {k: si.get(k) for k in ['total_base','total_target','virtual_count']})
