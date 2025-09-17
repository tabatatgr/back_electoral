from engine.procesar_diputados_v2 import procesar_diputados_v2
import json
res = procesar_diputados_v2(path_parquet='data/computos_diputados_2024.parquet', anio=2024, path_siglado='data/siglado-diputados-2024.normalized.csv', max_seats=500, sistema='mixto', mr_seats=300, rp_seats=200, usar_coaliciones=True, sobrerrepresentacion=8.0, umbral=0.03, print_debug=False)
print(json.dumps({'mr':res.get('mr'), 'rp':res.get('rp'), 'tot':res.get('tot')}, ensure_ascii=False, indent=2))
