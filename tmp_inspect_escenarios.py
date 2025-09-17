import pandas as pd
fn = 'outputs/escenarios_diputados_custom.xlsx'
xl = pd.ExcelFile(fn)
print('sheets:', xl.sheet_names)
for s in xl.sheet_names:
    df = xl.parse(s)
    print('\nSheet', s)
    if 'partido' in df.columns:
        pv = df[df['partido'].str.upper()=='PVEM'] if df['partido'].dtype == object else df[df['partido']=='PVEM']
        print('PVEM rows in sheet:', len(pv))
        if len(pv)>0:
            print(pv.to_string(index=False))
    else:
        print('no partido column; columns:', df.columns.tolist())

# show any party with tot==0 in any sheet
for s in xl.sheet_names:
    df = xl.parse(s)
    if 'tot' in df.columns:
        zeros = df[df['tot']==0]
        if len(zeros)>0:
            print('\nIn sheet', s, 'parties with tot==0:')
            print(zeros[['partido','mr','rp','tot']].to_string(index=False))
