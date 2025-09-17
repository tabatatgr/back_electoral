import pandas as pd

# 1) winners_by_district_siglado.csv
w = pd.read_csv('outputs/winners_by_district_siglado.csv')
count_w = (w['WINNER_SIGLADO'].str.upper()=='PVEM').sum()
print('PVEM MR count in winners_by_district_siglado.csv:', count_w)

# 2) mr_diagnostics_full.csv (WINNERS column)
m = pd.read_csv('outputs/mr_diagnostics_full.csv')
count_m = (m['WINNERS'].str.upper()=='PVEM').sum()
print('PVEM MR count in mr_diagnostics_full.csv:', count_m)

# 3) Excel sheet 500_300MR_200RP tot/mr
xl = pd.ExcelFile('outputs/escenarios_diputados_custom.xlsx')
df = xl.parse('500_300MR_200RP')
# find PVEM row
row = df[df['partido'].str.upper()=='PVEM']
print('\nPVEM row in sheet 500_300MR_200RP:')
print(row.to_string(index=False))

# 4) compare_asignadip.csv mr counts
ca = pd.read_csv('outputs/compare_asignadip.csv')
if 'PVEM' in ca['partido'].values:
    row_ca = ca[ca['partido']=='PVEM'].iloc[0]
    print('\ncompare_asignadip.csv PVEM:', dict(row_ca))
else:
    print('\nPVEM not found in compare_asignadip.csv')
