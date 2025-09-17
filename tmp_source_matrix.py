import pandas as pd
import os

p='outputs/assigned_by_district_with_source.csv'
if not os.path.exists(p):
    print('missing',p)
    raise SystemExit(1)

df=pd.read_csv(p,dtype=str).fillna('')
ct = pd.crosstab(df['assigned_party'].str.upper(), df['assigned_source'].str.upper())
print('Cross-tab assigned_party x source:')
print(ct.to_string())
print('\nTotals by source:')
print(df['assigned_source'].value_counts().to_string())
print('\nTotals by party (assigned):')
print(df['assigned_party'].value_counts().to_string())
