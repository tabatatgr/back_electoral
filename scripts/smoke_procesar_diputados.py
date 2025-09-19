"""Smoke test: llama a procesar_diputados_v2 con el dataset 2024 y siglado vigente.
Imprime resumen de totales y algunas comprobaciones sencillas.
"""
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from engine.procesar_diputados_v2 import procesar_diputados_v2


def run():
    path_parquet = 'data/computos_diputados_2024.parquet'
    path_siglado = 'data/siglado-diputados-2024.csv'

    if not os.path.exists(path_parquet):
        raise FileNotFoundError(path_parquet)
    if not os.path.exists(path_siglado):
        raise FileNotFoundError(path_siglado)

    print('Ejecutando procesar_diputados_v2 (vigente) ...')
    res = procesar_diputados_v2(
        path_parquet=path_parquet,
        anio=2024,
        path_siglado=path_siglado,
        max_seats=500,
        sistema='mixto',
        mr_seats=None,
        rp_seats=200,
        umbral=0.03,
        quota_method='hare',
        usar_coaliciones=True,
        print_debug=False
    )

    print('\nResultado tipo:', type(res))
    if isinstance(res, dict):
        if 'tot' in res:
            tot = res['tot']
            print('Totales partidos:', tot)
            print('Suma escaños:', sum(tot.values()))
        else:
            print('No hay clave tot en resultado. Keys:', list(res.keys()))
    else:
        print('Resultado no es dict. Raw repr:')
        print(res)

if __name__ == '__main__':
    run()
