import pandas as pd

df = pd.read_csv('outputs/comparativa_2021_vs_2024_CORREGIDO_20260106_135015.csv')
morena_2024 = df[(df['Año']==2024) & (df['Partido']=='MORENA')]

print('MORENA 2024 - Votos: 42.49%')
print('Tope +8%: 42.49% + 8% = 50.49% de 400 = 201.96 → 201 escaños MAX\n')
print(morena_2024[['Escenario','Votos_%','MR','PM','RP','Total','Escaños_%']].to_string(index=False))

print('\n\nResumen por escenario:')
for _, row in morena_2024.iterrows():
    total = row['MR'] + row['PM'] + row['RP']
    espacio = 201 - row['MR']  # Cuántos escaños tiene de espacio después de MR
    excede = total > 201
    print(f"{row['Escenario']}: MR={int(row['MR'])}, PM={int(row['PM'])}, RP={int(row['RP'])}, Total={total}, Tope=201, Espacio_para_PM/RP={espacio}, {'⚠️ EXCEDE' if excede else '✓ OK'}")
