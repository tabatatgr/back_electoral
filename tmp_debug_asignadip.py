from engine.procesar_diputados_v2 import procesar_diputados_v2, parties_for, asignadip_v2

path_parquet = 'data/computos_diputados_2024.parquet'
partidos = parties_for(2024)

# Reuse logic to compute recomposed and mr_aligned by calling procesar but with a flag? 
# We'll call procesar_diputados_v2 up to the point where it prepares arrays by importing functions.

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

# Print summary
print('\n--- SUMMARY FROM procesar_diputados_v2 ---')
print('mr keys sample:', list(res.get('mr', {}).keys())[:10])
print('tot sample:', {k: res.get('tot', {}).get(k) for k in list(res.get('tot', {}).keys())[:7]})
print('meta keys:', list(res.get('meta', {}).keys()))

print('\nIf asignadip_v2 failed inside procesar_diputados_v2, check logs above for traceback.')
