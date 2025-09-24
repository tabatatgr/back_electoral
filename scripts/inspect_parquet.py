import sys
import pandas as pd

p = sys.argv[1] if len(sys.argv) > 1 else 'outputs/tmp_redistrib_8f4b51ef78ca4e09b8af3a2521fd01ab.parquet'
print('Inspecting', p)
try:
    df = pd.read_parquet(p)
except Exception as e:
    print('Error reading parquet:', e)
    sys.exit(2)

print('shape:', df.shape)
print('columns:', df.columns.tolist())
print('\nhead:')
print(df.head().to_string())

vote_like = [c for c in df.columns if any(k in c.lower() for k in ('vot','vote','porc','porcentaje'))]
print('\nvote-like cols:', vote_like)
if vote_like:
    sums = df[vote_like].select_dtypes('number').sum().to_dict()
    print('\nsums:')
    for k,v in sums.items():
        print('  ', k, v)
else:
    print('\nNo vote-like columns found; trying groupby party columns by dtype numeric')
    numcols = df.select_dtypes('number').columns.tolist()
    print('numeric columns:', numcols)
    if numcols:
        sums = df[numcols].sum().to_dict()
        print('\nsums:')
        for k,v in sums.items():
            print('  ', k, v)

print('\nDone')