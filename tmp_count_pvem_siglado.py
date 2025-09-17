import pandas as pd
files = [
    'data/siglado-diputados-2024.normalized.csv',
    'data/siglado-diputados-2024.fixed.csv',
    'data/siglado-diputados-2024.engine.csv',
    'data/siglado-diputados-2024.csv'
]
for f in files:
    try:
        df = pd.read_csv(f)
        if 'grupo_parlamentario' in df.columns:
            col = 'grupo_parlamentario'
        elif 'PARTIDO_ORIGEN' in df.columns:
            col = 'PARTIDO_ORIGEN'
        elif 'grupo_parlamentario' in df.columns.str.lower():
            col = [c for c in df.columns if 'grupo' in c.lower()][0]
        else:
            col = None
        pv_rows = 0
        unique_pairs = set()
        if col is not None:
            for _, r in df.iterrows():
                val = str(r.get(col,'')).upper()
                if 'PVEM' in val or 'VERDE' in val:
                    pv_rows += 1
                    # try to extract entidad+distrito
                    ent = None
                    dist = None
                    for candidate in ['entidad_ascii','ENTIDAD','ENTIDAD_NORM','entidad','ENTIDAD_ORIGEN']:
                        if candidate in df.columns:
                            ent = str(r.get(candidate,'')).upper()
                            break
                    for candidate in ['distrito','DISTRITO']:
                        if candidate in df.columns:
                            dist = str(r.get(candidate,'')).strip()
                            break
                    unique_pairs.add((ent, dist))
        print(f'{f}: pv_rows={pv_rows}, unique_districts_with_pvem={len([p for p in unique_pairs if p[0] is not None])}')
    except Exception as e:
        print('ERROR reading', f, e)
