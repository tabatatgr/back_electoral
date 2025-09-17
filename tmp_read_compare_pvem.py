import pandas as pd
print('reading outputs/compare_asignadip.csv')
df=pd.read_csv('outputs/compare_asignadip.csv')
if 'partido' in df.columns:
    row=df[df['partido']=='PVEM']
    if row.shape[0]==0:
        print('PVEM not found in compare_asignadip.csv')
    else:
        print(row.to_string(index=False))
else:
    print('compare_asignadip.csv missing partido column; columns:', df.columns.tolist())
