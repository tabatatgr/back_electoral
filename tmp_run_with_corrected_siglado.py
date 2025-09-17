from engine.procesar_diputados_v2 import procesar_diputados_v2

PARQUET = 'data/computos_diputados_2024.parquet'
SIGLADO = 'data/siglado-diputados-2024.corrected.csv'

res = procesar_diputados_v2(path_parquet=PARQUET, anio=2024, path_siglado=SIGLADO, max_seats=500, sistema='mixto', mr_seats=None, rp_seats=200, usar_coaliciones=True, sobrerrepresentacion=8.0, umbral=0.03, print_debug=True)
mr = res.get('mr', {})
for p, s in sorted(mr.items(), key=lambda x: -x[1]):
    print(f"{p}: {s}")
