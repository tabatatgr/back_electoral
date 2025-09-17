import pandas as pd
from engine.recomposicion import recompose_coalitions, _load_siglado_dip, normalize_entidad_ascii, parties_for
from tmp_compare_asignadip import asignadip_py
from engine.procesar_diputados_v2 import procesar_diputados_v2

PARQUET = 'data/computos_diputados_2024.parquet'
SIGLADO = 'data/siglado-diputados-2024.csv'

print('1) Ejecutando recomposición con regla equal_residue_siglado...')
try:
    recomposed = recompose_coalitions(pd.read_parquet(PARQUET), 2024, 'diputados', rule='equal_residue_siglado', siglado_path=SIGLADO)
    print('Recomposed shape:', recomposed.shape)
except Exception as e:
    print('Error en recomposition:', e)
    raise

# parties columns
parties = parties_for(2024)
party_cols = [p for p in parties if p in recomposed.columns]
print('Party columns used:', party_cols)

# build ENT_KEY and DIST_CH
recomposed['ENT_KEY'] = recomposed['ENTIDAD'].apply(lambda x: normalize_entidad_ascii(x))
recomposed['DIST_CH'] = recomposed['DISTRITO'].astype(int).astype(str).str.zfill(3)
recomposed['DIST_UID'] = recomposed['ENT_KEY'] + '-' + recomposed['DIST_CH']

# melt and aggregate per DIST_UID x party
m = recomposed[['DIST_UID'] + party_cols].melt(id_vars=['DIST_UID'], var_name='PARTY', value_name='VOTOS')
m = m[m['VOTOS'].notna()]
m['VOTOS'] = m['VOTOS'].astype(float)
agg = m.groupby(['DIST_UID','PARTY'], as_index=False)['VOTOS'].sum()

# winners per DIST_UID
winners = agg.loc[agg.groupby('DIST_UID')['VOTOS'].idxmax()].copy()
# detect ties
multi = agg.groupby('DIST_UID')['VOTOS'].max().reset_index()
# tie detection simpler: count how many equal to max per DIST_UID
tie_counts = agg.groupby('DIST_UID').apply(lambda g: (g['VOTOS']==g['VOTOS'].max()).sum()).reset_index(name='n_winners')

# load siglado map
sigmap = _load_siglado_dip(SIGLADO)
# build map key (entidad_key,distrito)->dominante
sigmap['entidad_key'] = sigmap['entidad_key']
map_key = sigmap.set_index(['entidad_key','distrito'])['dominante'].to_dict()

# map winners to partido_siglado
def map_to_dominante(dist_uid, party):
    ent_key, dist_ch = dist_uid.split('-',1)
    dist = int(dist_ch)
    return map_key.get((ent_key, dist), None)

winners['DOMINANTE'] = winners.apply(lambda r: map_to_dominante(r['DIST_UID'], r['PARTY']), axis=1)
missing_map = winners[winners['DOMINANTE'].isna()]
print('Missing siglado mappings (rows):', len(missing_map))

# build ssd by DOMINANTE ignoring ties (we'll treat ties as unresolved)
winners_with_counts = winners.copy()
# add tie flag
tie_dict = dict(zip(tie_counts['DIST_UID'], tie_counts['n_winners']))
winners_with_counts['TIE'] = winners_with_counts['DIST_UID'].apply(lambda d: tie_dict.get(d,1)>1)
ssd = winners_with_counts[~winners_with_counts['TIE'] & winners_with_counts['DOMINANTE'].notna()].groupby('DOMINANTE').size().to_dict()
print('SSD (MR seats) by dominante sample:', list(ssd.items())[:10])

# now get national votes vector from engine run
print('Running engine to obtain votos (for national totals) ...')
try:
    res = procesar_diputados_v2(path_parquet=PARQUET, anio=2024, path_siglado=SIGLADO, max_seats=500, sistema='mixto', mr_seats=None, rp_seats=None, usar_coaliciones=True, print_debug=True)
except Exception as e:
    print('Error running engine:', e)
    raise
votos = res.get('votos', {})
mr_engine = res.get('mr', {})
rp_engine = res.get('rp', {})
tot_engine = res.get('tot', {})

# build ssd_vec aligned to votos keys
partidos = sorted(votos.keys(), key=lambda k: -votos[k])
ssd_vec = {p: int(ssd.get(p,0)) for p in partidos}
print('ssd_vec sample:', ssd_vec)

# run asignadip_py
print('Running asignadip_py with computed ssd...')
out = asignadip_py(votos, ssd_vec, m=200, S=500, threshold=0.03, max_seats=300, max_distortion=0.08)

print('\nComparison engine vs recomposed+asignadip_py (with compound key MR):')
print('Partido | MR(engine) | MR(compound) | RP(engine) | RP(py) | TOT(engine) | TOT(py)')
for p in partidos:
    print(f"{p:8} | {mr_engine.get(p,0):10} | {ssd_vec.get(p,0):12} | {rp_engine.get(p,0):10} | {out['rp'].get(p,0):6} | {tot_engine.get(p,0):11} | {out['tot'].get(p,0):6}")

# save ssd and results
pd.DataFrame([{'partido':p, 'ssd_compound':ssd_vec.get(p,0), 'mr_engine':mr_engine.get(p,0), 'rp_engine':rp_engine.get(p,0), 'tot_engine':tot_engine.get(p,0), 'rp_py': out['rp'].get(p,0), 'tot_py': out['tot'].get(p,0)} for p in partidos]).to_csv('outputs/mr_compound_compare.csv', index=False)
print('Wrote outputs/mr_compound_compare.csv')
