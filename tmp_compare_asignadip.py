import numpy as np
import pandas as pd
from engine.procesar_diputados_v2 import procesar_diputados_v2

PARQUET = 'data/computos_diputados_2024.parquet'
SIGLADO = 'data/siglado-diputados-2024.csv'

# Utilidades replicando la lógica R

def na_if(x, mask):
    x = np.array(x, dtype=float)
    x = x.copy()
    x[mask] = np.nan
    return x


def cl(x):
    x = np.array(x, dtype=float)
    # Replace nan with 0 for sum denom
    s = np.nansum(x)
    if s == 0:
        return np.zeros_like(x)
    return x / s


def LR(x, n, q=None):
    # x: array numeric (can contain nan)
    x = np.array(x, dtype=float)
    # treat NaNs as zeros for sums except keep them as NaN for final assignment
    mask = np.isnan(x)
    x_valid = np.where(mask, 0.0, x)
    if q is None:
        total = np.nansum(x)
        q = total / float(n) if (n > 0 and total > 0) else 0
    # floor division
    if q <= 0:
        # nothing to distribute
        return {i: 0 for i in range(len(x))}
    t = np.floor(x_valid / q).astype(int)
    u = int(n - np.nansum(t))
    if u <= 0:
        return {i: int(t[i]) for i in range(len(x))}
    # remainders
    rem = x_valid - t * q
    # rank by remainder desc
    order = np.argsort(-rem)
    r = np.zeros_like(t, dtype=int)
    for idx in order[:u]:
        r[idx] = 1
    out = t + r
    # set NaN entries to np.nan or 0? In original R they keep NA and ignore in sum; we'll set to 0
    out = np.where(mask, 0, out).astype(int)
    return {i: int(out[i]) for i in range(len(out))}


def asignadip_py(x, ssd, m=200, S=None, threshold=0.03, threshold_ref='valida', max_seats=300, max_distortion=0.08):
    # x and ssd are dicts partido->value following partidos order
    partidos = list(x.keys())
    N = len(partidos)
    x_arr = np.array([float(x[p]) for p in partidos], dtype=float)
    ssd_arr = np.array([int(ssd.get(p,0)) for p in partidos], dtype=int)

    if S is None:
        S = int(m + np.nansum(ssd_arr))
    # v total
    v_total = x_arr.copy()
    # v valida: here we approximate votes valid as proportion excluding independents since recomposed doesn't include independents separately
    # normalize to proportion
    v_valida = cl(v_total)

    # threshold mask
    mask_threshold = v_valida < threshold

    # v nacional: set to NA those below threshold
    v_nacional = cl(na_if(v_total, mask_threshold))

    # limits
    l_seats = np.array([max_seats] * N)
    # compute l_distortion only for non-nan entries
    l_distortion = np.full(N, np.nan)
    for i in range(N):
        if not np.isnan(v_nacional[i]):
            l_distortion[i] = np.floor((v_nacional[i] + max_distortion) * S)
    l_max = np.where(np.isnan(l_distortion), np.nan, np.minimum(l_seats, l_distortion))

    # Penalized matrix - MR (only where l_max is numeric)
    p_mr = np.zeros(N, dtype=bool)
    for i in range(N):
        if not np.isnan(l_max[i]):
            p_mr[i] = ssd_arr[i] >= l_max[i]

    # v efectiva: v_nacional with NA for p_mr
    v_efectiva = cl(na_if(v_nacional, p_mr))

    # rp_init via LR over v_efectiva
    rp_init_dict = LR(v_efectiva, int(m))
    rp_init = np.array([rp_init_dict[i] for i in range(N)], dtype=int)
    tot_init = ssd_arr + rp_init

    p_rp_init = tot_init > l_max

    if np.any(p_rp_init):
        v_efectiva = cl(na_if(v_efectiva, p_rp_init))
        rp = np.array([np.nan] * N, dtype=float)
        # assign to penalized: l_max - mr (only where l_max numeric)
        for i in range(N):
            if p_rp_init[i] and not np.isnan(l_max[i]):
                rp[i] = l_max[i] - ssd_arr[i]
        assigned = int(np.nansum(np.where(~np.isnan(rp), rp, 0)))
        n = int(m - assigned)
        if n < 0:
            n = 0
        lr_dict = LR(v_efectiva, n)
        lr_arr = np.array([lr_dict[i] for i in range(N)], dtype=int)
        # pmax: if rp is nan, replace with lr_arr
        rp = np.where(np.isnan(rp), lr_arr, rp).astype(int)
    else:
        rp = rp_init

    tot = ssd_arr + rp

    # Build output dicts
    mr_dict = {partidos[i]: int(ssd_arr[i]) for i in range(N)}
    rp_dict = {partidos[i]: int(rp[i]) for i in range(N)}
    tot_dict = {partidos[i]: int(tot[i]) for i in range(N)}

    return {
        'mr': mr_dict,
        'rp': rp_dict,
        'tot': tot_dict,
        'meta': {
            'v_total': dict(zip(partidos, v_total)),
            'v_nacional': dict(zip(partidos, v_nacional)),
            'limits_max': dict(zip(partidos, l_max.astype(int)))
        }
    }


if __name__ == '__main__':
    # Ejecutar el procesador para obtener votos y MR (siglado ligado)
    print('Ejecutando procesador para obtener votos y MR (siglado activo)...')
    res = procesar_diputados_v2(path_parquet=PARQUET, anio=2024, path_siglado=SIGLADO, max_seats=500, sistema='mixto', mr_seats=None, rp_seats=None, usar_coaliciones=True, sobrerrepresentacion=8.0, print_debug=False)
    votos = res.get('votos', {})
    mr = res.get('mr', {})
    rp_engine = res.get('rp', {})
    tot_engine = res.get('tot', {})

    # probar con m=200, S=500
    print('\nComparando con asignadip_py (m=200, S=500)...')
    out = asignadip_py(votos, mr, m=200, S=500, threshold=0.03, max_seats=300, max_distortion=0.08)

    partidos = sorted(votos.keys(), key=lambda k: -votos[k])

    print('\nPartido | MR(engine) | RP(engine) | TOT(engine) || MR(py) | RP(py) | TOT(py) | diff_tot')
    for p in partidos:
        e_mr = mr.get(p,0)
        e_rp = rp_engine.get(p,0)
        e_tot = tot_engine.get(p,0)
        py_mr = out['mr'].get(p,0)
        py_rp = out['rp'].get(p,0)
        py_tot = out['tot'].get(p,0)
        print(f"{p:8} | {e_mr:10} | {e_rp:10} | {e_tot:10} || {py_mr:6} | {py_rp:6} | {py_tot:6} | {py_tot - e_tot:9}")

    print('\nSuma engine tot:', sum(tot_engine.values()))
    print('Suma py tot:', sum(out['tot'].values()))

    # escribir CSV comparativa
    rows = []
    for p in partidos:
        rows.append({
            'partido': p,
            'mr_engine': mr.get(p,0),
            'rp_engine': rp_engine.get(p,0),
            'tot_engine': tot_engine.get(p,0),
            'mr_py': out['mr'].get(p,0),
            'rp_py': out['rp'].get(p,0),
            'tot_py': out['tot'].get(p,0),
            'diff_tot': out['tot'].get(p,0) - tot_engine.get(p,0)
        })
    pd.DataFrame(rows).to_csv('outputs/compare_asignadip.csv', index=False)
    print('Guardado outputs/compare_asignadip.csv')
