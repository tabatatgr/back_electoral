import pandas as pd
import json
from engine.procesar_diputados_v2 import procesar_diputados_v2

SIGLADO = 'data/siglado-diputados-2024.csv'
PARQUET = 'data/computos_diputados_2024.parquet'

print('Leyendo siglado...')
df_sig = pd.read_csv(SIGLADO)
print('Columnas siglado:', list(df_sig.columns)[:20])

if 'grupo_parlamentario' in df_sig.columns:
    gp_counts = df_sig['grupo_parlamentario'].str.strip().str.upper().value_counts()
    print('\nTop grupos parlamentarios (siglado):')
    print(gp_counts.head(20).to_dict())
else:
    print('No se encontró columna grupo_parlamentario en siglado')

print('\nLeyendo parquet...')
df = pd.read_parquet(PARQUET)
print('Columns parquet sample:', list(df.columns)[:40])

# Determinar ganador por distrito en parquet (partidos list)
# Buscar columnas de partidos comunes
exclude = set(['ENTIDAD','DISTRITO','TOTAL_BOLETAS','TOTAL_PARTIDOS_SUM','ANIO','CI','TOTAL'])
party_cols = [c for c in df.columns if c not in exclude]
print('Detected party columns (sample 30):', party_cols[:30])

# Compute winner by votes per district using party_cols intersection of known parties from siglado
# Normalize names

def norm(s):
    try:
        return str(s).strip().upper()
    except Exception:
        return s

# Try simple per-row argmax among party_cols
if party_cols:
    winners = df[party_cols].idxmax(axis=1)
    winners_norm = winners.str.strip().str.upper()
    pv = winners_norm.value_counts()
    print('\nWinners by parquet (top 20):')
    print(pv.head(20).to_dict())
else:
    print('No party columns detected to compute winners')

print('\nEjecutando procesar_diputados_v2...')
res = procesar_diputados_v2(path_parquet=PARQUET, anio=2024, path_siglado=SIGLADO, max_seats=500, sistema='mixto', mr_seats=None, rp_seats=200, usar_coaliciones=True, print_debug=False)

print('\nMR from engine (top 20):')
mr = res.get('mr', {})
print({k: v for k, v in sorted(mr.items(), key=lambda x: -x[1])[:20]})
print('Total MR seats engine:', sum(mr.values()))

print('\nTotales from engine (top 20):')
tot = res.get('tot', {})
print({k: v for k, v in sorted(tot.items(), key=lambda x: -x[1])[:20]})
print('Total seats engine:', sum(tot.values()))

# Compare siglado counts for MORENA
if 'grupo_parlamentario' in df_sig.columns:
    morena_sig = gp_counts.get('MORENA', 0)
    print('\nMORENA in siglado count:', morena_sig)

# Compare winners by parquet winners for MORENA
if 'MORENA' in pv.index:
    print('MORENA winners by parquet (raw argmax):', int(pv['MORENA']))

print('\nDone')
