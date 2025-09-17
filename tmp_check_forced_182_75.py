from engine.procesar_diputados_v2 import procesar_diputados_v2

res = procesar_diputados_v2(path_parquet='data/computos_diputados_2024.parquet', anio=2024, path_siglado='data/siglado-diputados-2024.csv', max_seats=500, sistema='mixto', mr_seats=182, rp_seats=75, usar_coaliciones=True, print_debug=False)
print('MR (top):', {k:v for k,v in sorted(res['mr'].items(), key=lambda x:-x[1])[:10]})
print('RP (top):', {k:v for k,v in sorted(res['rp'].items(), key=lambda x:-x[1])[:10]})
print('TOT (top):', {k:v for k,v in sorted(res['tot'].items(), key=lambda x:-x[1])[:10]})
print('Sum TOT:', sum(res['tot'].values()))
