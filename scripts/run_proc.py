from engine.procesar_diputados_v2 import procesar_diputados_v2

if __name__ == '__main__':
    res = procesar_diputados_v2(
        path_parquet='outputs/tmp_redistrib_8f4b51ef78ca4e09b8af3a2521fd01ab.parquet',
        anio=2024,
        path_siglado='data/siglado-diputados-2024.csv',
        max_seats=128,
        sistema='mixto',
        mr_seats=64,
        rp_seats=64,
        umbral=0.03,
        usar_coaliciones=True,
        print_debug=True
    )
    import json
    print('\nRESULT:')
    print(json.dumps(res, indent=2, default=str))
