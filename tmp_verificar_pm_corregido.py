import pandas as pd

df = pd.read_csv('outputs/comparativa_2021_vs_2024_CORREGIDO_20260106_140933.csv')
m = df[(df['Año']==2024) & (df['Partido']=='MORENA')]

print('=' * 80)
print('MORENA 2024 - PM SIN AJUSTAR (corrección constitucional)')
print('=' * 80)
print()
print(m[['Escenario','MR','PM','RP','Total']].to_string(index=False))

print('\n' + '=' * 80)
print('Verificación de topes (límite: 201 escaños)')
print('=' * 80)

for _, r in m.iterrows():
    total = int(r['Total'])
    excede = total > 201
    estado = '[EXCEDE TOPE - PERMITIDO]' if excede else '[OK]'
    print(f"\n{r['Escenario']}:")
    print(f"  MR={int(r['MR'])} + PM={int(r['PM'])} + RP={int(r['RP'])} = {total}")
    print(f"  Tope: 201")
    print(f"  Estado: {estado}")
    if excede:
        print(f"  >>> Sobrerrepresentación de {total - 201} escaños por victorias directas (MR+PM)")
