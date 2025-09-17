# script to generate district_discrepancies.csv
import pandas as pd
import os

out_dir = 'outputs'
os.makedirs(out_dir, exist_ok=True)

diag = pd.read_csv('outputs/mr_diagnostics_full.csv')
# mr_diagnostics_full has WINNERS (winner by parquet per-district recomposed) and SIGLADO_DOMINANTE (engine siglado mapping)

# build winner_compound from WINNERS column (already present) and winner_siglado from SIGLADO_DOMINANTE

df = diag.copy()
df['winner_compound'] = df['WINNERS']
df['winner_siglado'] = df['SIGLADO_DOMINANTE']

# mark equal/different
ndf = df[['ENTIDAD','DISTRITO','DIST_CH','winner_compound','winner_siglado','SIGLADO_PRESENT','TOTAL_VOTOS']].copy()
ndf['same'] = ndf['winner_compound'] == ndf['winner_siglado']

# write full and only-diff
full_path = os.path.join(out_dir,'district_discrepancies_full.csv')
ndf.to_csv(full_path,index=False)

diff_path = os.path.join(out_dir,'district_discrepancies_only_diff.csv')
ndf[~ndf['same']].to_csv(diff_path,index=False)

print(f'wrote {full_path} ({len(ndf)} rows) and {diff_path} ({len(ndf[~ndf["same"]])} diffs)')
