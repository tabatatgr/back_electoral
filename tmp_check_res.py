from engine.procesar_diputados_v2 import procesar_diputados_v2
import pandas as pd

print('Llamando procesar_diputados_v2 para 500_300MR_200RP')
res = procesar_diputados_v2(path_parquet='data/computos_diputados_2024.parquet', anio=2024, path_siglado='data/siglado-diputados-2024.normalized.csv', max_seats=500, sistema='mixto', mr_seats=300, rp_seats=200, usar_coaliciones=True, sobrerrepresentacion=8.0, umbral=0.03, print_debug=False)
print('Claves devueltas:', list(res.keys()))
partido='PVEM'
print('PVEM en tot keys?:', partido in res.get('tot', {}))
print('MR:', res.get('mr', {}).get(partido, None))
print('RP:', res.get('rp', {}).get(partido, None))
print('TOT:', res.get('tot', {}).get(partido, None))

# Mostrar resumen por partido (mr,rp,tot) para los partidos con tot>0
print('\nResumen partidos con tot>0:')
for p,t in res.get('tot', {}).items():
    if t>0:
        print(p, 'mr=', res.get('mr', {}).get(p,0), 'rp=', res.get('rp', {}).get(p,0), 'tot=', t)

# Leer compare_asignadip.csv si existe para comparar
try:
    df = pd.read_csv('outputs/compare_asignadip.csv')
    if 'partido' in df.columns:
        print('\ncompare_asignadip.csv PVEM row:')
        print(df[df['partido']=='PVEM'].to_string(index=False))
except Exception as e:
    print('No se pudo leer compare_asignadip.csv:', e)
