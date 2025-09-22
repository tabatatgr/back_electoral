from engine.procesar_diputados_v2 import procesar_diputados_v2

if __name__ == '__main__':
    print('Calling procesar_diputados_v2 with max_seats=128')
    res = procesar_diputados_v2(
        path_parquet='data/computos_diputados_2024.parquet',
        anio=2024,
        max_seats=128,
        sistema='mr',
        print_debug=False
    )

    total = sum(res.get('tot', {}).values())
    print('Returned total seats sum =', total)
    meta_S = res.get('meta', {}).get('params', {}).get('S')
    print('meta.S =', meta_S)
    # Print a small sample of tot
    for k, v in list(res.get('tot', {}).items())[:8]:
        print(k, v)
