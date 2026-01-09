import pandas as pd

df = pd.read_csv('outputs/comparativa_2021_vs_2024_CORREGIDO_20260106_140933.csv')

# Filtrar 2024, escenario MR 200 - PM 200, SIN coaliciones
pm_200 = df[(df['Año']==2024) & (df['Escenario']=='MR 200 - PM 200') & (~df['Partido'].str.startswith('COALICIÓN', na=False))]

print('=' * 80)
print('ESCENARIO: MR 200 - PM 200 (2024)')
print('Distribución de PM entre todos los partidos')
print('=' * 80)
print()
print(pm_200[['Partido','MR','PM','RP','Total']].to_string(index=False))

print('\n' + '=' * 80)
print('TOTALES:')
print('=' * 80)
print(f"MR total: {pm_200['MR'].sum()}")
print(f"PM total: {pm_200['PM'].sum()}")
print(f"RP total: {pm_200['RP'].sum()}")
print(f"TOTAL: {pm_200['Total'].sum()}")
print()
print(f"PM configurado: 200")
print(f"PM asignado: {pm_200['PM'].sum()}")
print(f"Diferencia: {200 - pm_200['PM'].sum()}")
