import pandas as pd
from engine.procesar_diputados_v2 import procesar_diputados_v2

ORIG_SIG = 'data/siglado-diputados-2024.csv'
MISSING = 'outputs/mr_diagnostics_missing_siglado.csv'
FIXED = 'data/siglado-diputados-2024.fixed.csv'
PARQUET = 'data/computos_diputados_2024.parquet'

print('Leyendo siglado original...')
orig = pd.read_csv(ORIG_SIG, dtype=str)
print('Filas original siglado:', len(orig))

print('Leyendo missing...')
miss = pd.read_csv(MISSING, dtype=str)
print('Missing rows:', len(miss))

# For each missing row, add an entry using ENTIDAD and ENT_KEY if available
adds = []
for _, r in miss.iterrows():
    entidad = r.get('ENTIDAD', r.get('ENT_KEY', ''))
    entidad_ascii = entidad
    try:
        distrito = int(r['DIST_CH'])
    except Exception:
        distrito = int(r.get('DISTRITO', 0))
    winner = r['WINNERS'] if pd.notna(r['WINNERS']) and r['WINNERS']!='' else 'MORENA'
    row = {
        'entidad': entidad,
        'entidad_ascii': entidad_ascii,
        'distrito': distrito,
        'coalicion': winner,
        'grupo_parlamentario': winner
    }
    adds.append(row)

if adds:
    add_df = pd.DataFrame(adds)
    fixed = pd.concat([orig, add_df], ignore_index=True, sort=False)
else:
    fixed = orig.copy()

fixed.to_csv(FIXED, index=False)
print('Wrote fixed siglado to', FIXED, 'rows=', len(fixed))

# Run processor using fixed siglado
print('Running processor with fixed siglado...')
res = procesar_diputados_v2(path_parquet=PARQUET, anio=2024, path_siglado=FIXED, max_seats=500, sistema='mixto', mr_seats=None, rp_seats=None, usar_coaliciones=True, print_debug=True)

mr = res.get('mr', {})
rp = res.get('rp', {})
tot = res.get('tot', {})

print('\n-- MR --')
for p,v in sorted(mr.items(), key=lambda x:-x[1]):
    print(p, v)
print('\n-- RP --')
for p,v in sorted(rp.items(), key=lambda x:-x[1]):
    print(p, v)
print('\n-- TOT --')
for p,v in sorted(tot.items(), key=lambda x:-x[1]):
    print(p, v)

print('\nSuma totales reportada:', sum(tot.values()) if tot else 'N/A')
