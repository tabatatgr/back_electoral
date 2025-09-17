import pandas as pd

path = 'outputs/diputados_scenarios.xlsx'
try:
    sheets = pd.read_excel(path, sheet_name=None)
except Exception as e:
    print('ERROR_LEYENDO_EXCEL', e)
    raise

for name, df in sheets.items():
    # Normalizar nombres de partido
    df['partido_norm'] = df['partido'].astype(str).str.strip().str.upper()
    mask = df['partido_norm'] == 'MORENA'
    total = df.loc[mask, 'total'].sum() if mask.any() else 0
    mr = df.loc[mask, 'mr'].sum() if mask.any() else 0
    rp = df.loc[mask, 'rp'].sum() if mask.any() else 0
    print(f"{name}: total={int(total)} (mr={int(mr)}, rp={int(rp)})")
