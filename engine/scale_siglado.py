import numpy as np
import pandas as pd
from typing import Optional, List


def hare_quota(weights: np.ndarray, M: int) -> np.ndarray:
    """Reparte M unidades usando la regla de Hare/Hamilton según pesos."""
    w = np.array(weights, dtype=float)
    w = np.maximum(w, 0.0)
    if w.sum() <= 0 or M <= 0:
        return np.zeros_like(w, dtype=int)

    prop = w / w.sum()
    raw = prop * M
    floor_q = np.floor(raw).astype(int)
    rem = M - floor_q.sum()
    if rem > 0:
        frac = raw - floor_q
        add_idx = np.argsort(-frac)[:rem]
        floor_q[add_idx] += 1
    return floor_q


def scale_siglado(
    df: pd.DataFrame,
    M_target: int,
    partidos_base: Optional[List[str]] = None,
    strata: str = "ENTIDAD",
    weight_var: Optional[str] = None,
    seed: int = 123,
) -> pd.DataFrame:
    """
    Escala (down/up) un siglado (DataFrame por distrito) a una magnitud MR `M_target`.

    - df: DataFrame que contiene por fila un distrito con columnas: `ENTIDAD`, `DISTRITO` y las columnas de partido.
    - partidos_base: lista de partidos (si None, inferir como columnas que no sean ENTIDAD/DISTRITO/TOTALES)
    - strata: columna de estrato (por defecto ENTIDAD)
    - weight_var: columna de peso por distrito (población/turnout). Si None, se usa la suma de votos por fila.
    - Devuelve un DataFrame con exactamente M_target filas y columnas: strata, distrito_id, sigla, weight, virtual (bool), distrito_id_new
    """
    np.random.seed(seed)

    if strata not in df.columns:
        raise ValueError(f"Columna de estrato {strata} no encontrada en df")

    # Inferir partidos si no se proveen
    if partidos_base is None:
        reserved = {strata, 'DISTRITO', 'ENTIDAD', 'TOTAL_BOLETAS', 'TOTAL_PARTIDOS_SUM', 'anio'}
        partidos_base = [c for c in df.columns if c not in reserved and df[c].dtype.kind in 'iuft']

    # Determinar ganador por fila (sigla)
    winner_col = None
    for cand in ['MR_DOMINANTE', 'DOMINANTE', 'DOMINANTE_PARTIDO']:
        if cand in df.columns:
            winner_col = cand
            break

    base = df.copy()
    # distrito_id base
    def _make_id(r):
        ent = str(r.get('ENTIDAD') or r.get('entidad') or '')
        dist = str(r.get('DISTRITO') or r.get('distrito') or '')
        return f"{ent}__{dist}"

    base['distrito_id'] = base.apply(_make_id, axis=1)

    if winner_col is not None:
        base['sigla'] = base[winner_col].astype(str)
    else:
        # calcular por mayor voto entre partidos_base
        if len(partidos_base) == 0:
            raise ValueError('No se encontraron columnas de partido para inferir sigla')
        parts = [p for p in partidos_base if p in base.columns]
        if len(parts) == 0:
            # fallback: tomar cualquier columna numérica
            parts = [c for c in base.columns if base[c].dtype.kind in 'iuft']
        base['sigla'] = base[parts].idxmax(axis=1)

    # peso por distrito
    if weight_var and weight_var in base.columns:
        base['_weight'] = pd.to_numeric(base[weight_var], errors='coerce').fillna(0.0)
    else:
        # sumar votos por partidos
        parts = [p for p in partidos_base if p in base.columns]
        if len(parts) == 0:
            # fallback: 1 por fila
            base['_weight'] = 1.0
        else:
            base['_weight'] = base[parts].sum(axis=1).astype(float)

    # quotas por estrato
    ent_weights = base.groupby(strata)['_weight'].sum().reset_index()
    quotas = hare_quota(ent_weights['_weight'].values, M_target)
    ent_weights['quota'] = quotas

    scaled_rows = []

    for _, row in ent_weights.iterrows():
        ent = row[strata]
        quota = int(row['quota'])
        group = base[base[strata] == ent].copy()
        n0 = len(group)

        if quota <= 0:
            continue

        if quota <= n0:
            # Downscale: seleccionar quota filas preservando mezcla por sigla (PPS por peso dentro de sigla)
            # calcular target por sigla dentro del estrato según peso
            sig_w = group.groupby('sigla')['_weight'].sum().reset_index()
            sig_w['raw'] = sig_w['_weight'] / sig_w['_weight'].sum() * quota
            sig_w['k'] = np.floor(sig_w['raw']).astype(int)
            rem = quota - sig_w['k'].sum()
            if rem > 0:
                frac = sig_w['raw'] - sig_w['k']
                add_idx = np.argsort(-frac)[:rem]
                sig_w.loc[add_idx, 'k'] += 1

            picked_parts = []
            for _, srow in sig_w.iterrows():
                s = srow['sigla']
                k = int(srow['k'])
                pool = group[group['sigla'] == s]
                if k <= 0:
                    continue
                if len(pool) <= k:
                    sel = pool
                else:
                    probs = pool['_weight'].values
                    if probs.sum() <= 0:
                        idx = np.random.choice(pool.index, size=k, replace=False)
                    else:
                        probs = probs / probs.sum()
                        idx = np.random.choice(pool.index, size=k, replace=False, p=probs)
                    sel = pool.loc[idx]
                picked_parts.append(sel)

            if len(picked_parts) > 0:
                picked = pd.concat(picked_parts, ignore_index=True)
            else:
                picked = pd.DataFrame(columns=group.columns)

            # si faltan por redondeo, completar PPS global
            if len(picked) < quota:
                faltan = quota - len(picked)
                remain = group[~group['distrito_id'].isin(picked['distrito_id'])]
                if len(remain) > 0:
                    probs = remain['_weight'].values
                    if probs.sum() <= 0:
                        idx = np.random.choice(remain.index, size=min(faltan, len(remain)), replace=False)
                    else:
                        probs = probs / probs.sum()
                        idx = np.random.choice(remain.index, size=min(faltan, len(remain)), replace=False, p=probs)
                    extra = remain.loc[idx]
                    picked = pd.concat([picked, extra], ignore_index=True)

            picked = picked.copy()
            picked['virtual'] = False
            picked['distrito_id_new'] = picked['distrito_id']
            scaled_rows.append(picked)

        else:
            # Upscale: quota > n0, duplicar filas controladamente
            k = quota - n0
            base_sel = group.copy()
            base_sel['virtual'] = False
            base_sel['distrito_id_new'] = base_sel['distrito_id']

            # ordenar por sigla y peso para anti-colisión
            ord_df = group.sort_values(['sigla', '_weight'], ascending=[True, False]).reset_index(drop=True)
            adds = []
            i = 1
            j = 0
            while len(adds) < k:
                rowi = ord_df.iloc[j % len(ord_df)].copy()
                rowi['virtual'] = True
                rowi['distrito_id_new'] = f"{rowi['distrito_id']}_v{(i)}"
                adds.append(rowi)
                i += 1
                j += 1

            adds_df = pd.DataFrame(adds)
            combined = pd.concat([base_sel, adds_df], ignore_index=True)
            scaled_rows.append(combined)

    if len(scaled_rows) == 0:
        return pd.DataFrame(columns=['sigla', '_weight', 'distrito_id', 'distrito_id_new', 'virtual', strata])

    out = pd.concat(scaled_rows, ignore_index=True)
    # asegurar que tenga exactamente M_target filas (cortar/excedente por seguridad)
    if len(out) > M_target:
        out = out.sample(n=M_target, random_state=seed).reset_index(drop=True)
    elif len(out) < M_target:
        # Si por rounding faltan, completar con duplicados probabilísticos globales
        faltan = M_target - len(out)
        pool = out if len(out) > 0 else base
        probs = pool['_weight'].values
        if probs.sum() <= 0:
            idx = np.random.choice(pool.index, size=faltan, replace=True)
        else:
            probs = probs / probs.sum()
            idx = np.random.choice(pool.index, size=faltan, replace=True, p=probs)
        extra = pool.loc[idx].copy()
        extra['virtual'] = True
        extra['distrito_id_new'] = extra['distrito_id'] + '_vfill'
        out = pd.concat([out, extra], ignore_index=True)

    # Normalizar columnas mínimas
    out = out.reset_index(drop=True)
    out = out[[strata, 'distrito_id', 'distrito_id_new', 'sigla', '_weight', 'virtual']]
    out = out.rename(columns={strata: strata, '_weight': 'weight'})
    return out
