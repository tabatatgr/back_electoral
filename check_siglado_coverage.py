import pandas as pd
SIG = 'data/siglado-diputados-2024.csv'

df = pd.read_csv(SIG)
print('Rows:', len(df))

# Normalize entity and district columns
ent_col = 'entidad' if 'entidad' in df.columns else ('entidad_ascii' if 'entidad_ascii' in df.columns else df.columns[0])
dist_col = 'distrito' if 'distrito' in df.columns else None

print('Using columns:', ent_col, dist_col)

if dist_col is None:
    print('No district column detected; aborting')
else:
    df['_ent'] = df[ent_col].astype(str).str.strip().str.upper()
    df['_dist'] = pd.to_numeric(df[dist_col], errors='coerce').fillna(-1).astype(int)

    # Count unique districts overall
    unique = df.groupby(['_ent','_dist']).size().reset_index(name='count')
    print('Unique district groups:', len(unique))

    # Entities list and expected district ranges roughly 1..N per entity; show counts per entity
    per_ent = unique.groupby('_ent').size().sort_values(ascending=False)
    print('\nDistrict counts per entidad (top 20):')
    print(per_ent.head(50).to_dict())

    # Find entities with missing districts (gaps)
    gaps = {}
    for ent, grp in df.groupby('_ent'):
        dists = sorted(set(grp['_dist'].tolist()))
        if not dists:
            continue
        min_d, max_d = min(dists), max(dists)
        expected = set(range(min_d, max_d+1)) if min_d>0 else set(range(1, max_d+1))
        missing = sorted(list(expected - set(dists)))
        if missing:
            gaps[ent] = {'min':min_d,'max':max_d,'missing': missing[:10], 'missing_count': len(missing)}
    print('\nEntities with missing district numbers (sample up to 10 missing shown):')
    for k,v in list(gaps.items())[:30]:
        print(k, v)

    # Show any rows with invalid district
    bad = df[df['_dist'] < 1]
    print('\nRows with invalid district count:', len(bad))
    if len(bad) > 0:
        print(bad.head(10).to_dict())

print('\nDone')
