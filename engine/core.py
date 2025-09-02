from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Tuple
import numpy as np
import pandas as pd

# =========================
# 0) Helpers de métodos
# =========================

QuotaMethod = Literal["hare", "droop", "hb"]          # hare = Hare, droop = Droop, hb = Hare-Niemeyer
DivisorMethod = Literal["dhondt", "saintelague"]

def largest_remainder(votes: np.ndarray, seats: int, method: QuotaMethod) -> np.ndarray:
    votes = np.maximum(0, np.nan_to_num(votes.astype(float)))
    if seats <= 0 or votes.sum() <= 0:
        return np.zeros_like(votes, dtype=int)
    if method == "hare":
        q = votes.sum() / seats
    elif method == "droop":
        # Droop exacta: floor(V/(S+1)) + 1  -> usar versión proporcional
        q = (votes.sum() / (seats + 1)) + 1e-12
    elif method == "hb":  # Hare-Niemeyer = Hare
        q = votes.sum() / seats
    else:
        raise ValueError("QuotaMethod no soportado")

    base = np.floor(votes / q)
    left = seats - int(base.sum())
    if left <= 0:
        return base.astype(int)

    rema = votes / q - base
    order = np.argsort(-rema)  # mayores residuos
    base[order[:left]] += 1
    return base.astype(int)

def divisor_apportionment(votes: np.ndarray, seats: int, method: DivisorMethod) -> np.ndarray:
    votes = np.maximum(0, np.nan_to_num(votes.astype(float)))
    if seats <= 0 or votes.sum() <= 0:
        return np.zeros_like(votes, dtype=int)

    if method == "dhondt":
        divisors = np.arange(1, seats + 1, dtype=float)  # 1,2,3,...
    elif method == "saintelague":
        divisors = 2 * np.arange(seats, dtype=float) + 1  # 1,3,5,…
    else:
        raise ValueError("DivisorMethod no soportado")

    # tabla de cocientes
    quotients = (votes[:, None] / divisors[None, :]).reshape(-1)
    idx = np.argpartition(-quotients, seats - 1)[:seats]  # top-S sin ordenar todo
    party_idx = idx // len(divisors)
    out = np.bincount(party_idx, minlength=len(votes))
    return out.astype(int)

# =========================
# 1) Coaliciones (equidad + residuo al dominante por distrito)
# =========================

def redistribute_coalitions_equal_residual(
    df: pd.DataFrame,
    vote_cols: List[str],
    coalition_map: Dict[str, List[str]],
    group_keys: List[str] = ["ENTIDAD", "DISTRITO"],
) -> pd.DataFrame:
    """
    df: boleta a nivel distrito con columnas de candidaturas 
    """
    out = df[group_keys].copy()
    # crear columnas limpias de partidos base (las que aparecen en coalition_map)
    partidos_base = sorted({p for lst in coalition_map.values() for p in lst})
    for p in partidos_base:
        out[p] = 0

    def split_tokens(label: str) -> List[str]:
        tokens = split_tokens(colname)  # en vez de .split("_")
        toks = [t for t in label.replace("-", "_").split("_") if t]
        return [t.upper().strip() for t in toks]

    # por grupo (distrito)
    for _, g in df.groupby(group_keys, as_index=False):
        # votos solo (si existen)
        solo = {p: float(g[p].sum()) if p in g.columns else 0.0 for p in partidos_base}

        # sumar coaliciones: repartir equitativo y residuo al dominante (del conjunto de esa coalición)
        for col in vote_cols:
            if col not in g.columns:
                continue
            V = float(g[col].sum())
            if V <= 0:
                continue

            toks = split_tokens(col)
            # mapear tokens a una coalición conocida (si los tokens coinciden con un set del mapa)
            # estrategia: encontrar la coalición cuyo conjunto es superconjunto de toks
            cand = None
            toks_set = set(toks)
            for cname, members in coalition_map.items():
                mset = set(members)
                if len(toks_set) >= 2 and toks_set.issubset(mset):
                    cand = members
                    break
            # si no es coalición (1 token y es partido), lo tratamos como partido
            if cand is None:
                if len(toks) == 1 and toks[0] in partidos_base:
                    out.loc[g.index, toks[0]] += V
                # else: ignorar (col rara o partidos fuera del universo)
                continue

            k = len(cand)
            if k <= 0:
                continue
            q = V // k
            r = int(V - q * k)

            # repartir equitativo
            for p in cand:
                out.loc[g.index, p] += q

            # residuo al dominante (entre miembros de esa coalición, usando votos "solo")
            # si todos en cero, desempatar por orden de lista
            vals = [solo.get(p, 0.0) for p in cand]
            j = int(np.argmax(vals))
            out.loc[g.index, cand[j]] += r

    # total boletas reconstruidas (partidos_base) + CI si existe en df
    out["TOTAL_PARTIDOS"] = out[partidos_base].sum(axis=1)
    if "CI" in df.columns:
        out["CI"] = df["CI"]
        out["TOTAL_BOLETAS"] = out["TOTAL_PARTIDOS"] + out["CI"]
    else:
        out["TOTAL_BOLETAS"] = out["TOTAL_PARTIDOS"]
        out["CI"] = 0
    return out

# =========================
# 2) MR a partido con siglado (ganador por distrito)
# =========================

def mr_by_siglado(
    winners_df: pd.DataFrame,
    group_keys: List[str],
    gp_col: str,
    parties: List[str],
) -> Tuple[Dict[str, int], int]:
    """
    winners_df: dataframe a nivel distrito con la etiqueta final de 'grupo parlamentario' (gp) ganador por distrito.
    gp_col: columna con GP final por distrito (p. ej. salida de tu CSV de siglado + proxy)
    Devuelve ssd por partido y cuenta de 'CI' como independientes.
    """
    ssd = {p: 0 for p in parties}
    indep = 0
    for _, r in winners_df.iterrows():
        gp = str(r[gp_col]).upper().strip()
        if gp == "CI":
            indep += 1
        elif gp in ssd:
            ssd[gp] += 1
        # ignorar otros (ruido)
    return ssd, indep

# =========================
# 3) Topes nacionales (+8 pp y ≤ 300) 
# =========================

def apply_caps_national(
    s_mr: np.ndarray, s_rp: np.ndarray, v_nac: np.ndarray,
    S: int, max_pp: float = 0.08, max_seats: int = 300, iter_max: int = 16
) -> Tuple[np.ndarray, np.ndarray]:
    """
    s_mr: asientos por MR
    s_rp: asientos iniciales de RP (antes de topes)
    v_nac: participación nacional normalizada de partidos elegibles (después de umbral; suma 1)
    S: total de curules (MR+RP)
    """
    s_mr = s_mr.astype(int)
    s_rp = s_rp.astype(int)
    N = len(s_mr)

    rp_total = max(0, int(S - s_mr.sum()))
    ok = v_nac > 0

    cap_dist = np.floor((v_nac + max_pp) * S).astype(int)
    cap_dist[~ok] = s_mr[~ok]  # <3%: límite = MR (no reciben RP)

    lim_max = np.minimum(np.maximum(s_mr, cap_dist), max_seats)

    s_tot = s_mr + s_rp
    k = 0
    while True:
        over = np.where(s_tot > lim_max)[0]
        if not len(over) or k >= iter_max:
            break
        k += 1

        s_rp[over] = np.maximum(0, lim_max[over] - s_mr[over])

        fixed = np.zeros(N, dtype=bool)
        fixed[over] = True
        fixed[~ok] = True

        v_eff = v_nac.copy()
        v_eff[fixed] = 0

        rp_fijos = int(np.maximum(0, (lim_max - s_mr)).clip(min=0)[fixed].sum())
        n_rest = max(0, rp_total - rp_fijos)

        if n_rest == 0 or v_eff.sum() <= 0:
            s_rp[~fixed] = 0
        else:
            add = largest_remainder(v_eff, n_rest, "hare")
            s_rp = np.zeros(N, dtype=int)
            s_rp[fixed] = np.maximum(0, (lim_max - s_mr))[fixed]
            s_rp[~fixed] = add[~fixed]

        s_tot = s_mr + s_rp

    # Ajuste por si faltan/sobran por redondeos
    delta = int(S - s_tot.sum())
    if delta != 0:
        margin = (lim_max - s_tot).copy()
        margin[~ok] = 0
        if delta > 0:
            cand = np.where(margin > 0)[0]
            if len(cand):
                order = cand[np.argsort(-v_nac[cand])]
                take = order[: min(delta, len(order))]
                s_rp[take] += 1
        else:
            cand = np.where((s_rp > 0) & ok)[0]
            if len(cand):
                order = cand[np.argsort(-s_rp[cand])]
                take = order[: min(-delta, len(order))]
                s_rp[take] -= 1

    return s_rp.astype(int), (s_mr + s_rp).astype(int)

# =========================
# 4) Sobrerrepresentación 
# =========================

def apply_overrep_cap(
    seats: np.ndarray, vote_share_valid: np.ndarray, S: int, over_cap: float
) -> np.ndarray:
    """
    Corta partidos que excedan (v + over_cap) * S y redistribuye por LR con los demás.
    Si over_cap es None, no hace nada.
    """
    if over_cap is None:
        return seats
    cap = np.floor((vote_share_valid + over_cap) * S).astype(int)
    seats = seats.copy()
    # fijar tope
    seats = np.minimum(seats, cap)
    # redistribuir el resto por LR sobre los que tengan margen
    delta = S - int(seats.sum())
    if delta <= 0:
        return seats
    margin = cap - seats
    w = np.where(margin > 0, vote_share_valid, 0)
    if w.sum() <= 0:
        return seats
    add = largest_remainder(w, delta, "hare")
    seats += add
    return seats

# =========================
# 5) Orquestador Diputados (cámara completa)
# =========================

@dataclass
class DipParams:
    S: int                          # total curules (MR+RP)
    mr_seats: int                   # curules MR
    threshold: float               
    quota_method: QuotaMethod       # "hare" | "droop" | "hb" (para LR)
    divisor_method: Optional[DivisorMethod] = None  
    use_divisor_for_rp: bool = False               # True → usar divisor para RP
    max_pp: float = 0.08
    max_seats: int = 300
    overrep_cap: Optional[float] = None

@dataclass
class SenParams:
    """Parámetros para asignación de senadores"""
    S: int = 128                              # Total de escaños senado
    threshold: float = 0.03                   # Umbral nacional
    quota_method: str = "hare"                # Método de cuota
    divisor_method: str = "dhondt"            # Método divisor 
    use_divisor_for_rp: bool = True           # Usar divisor para RP

def assign_senadores(
    votos_partido_nacional: pd.Series,     # votos absolutos nacionales por partido
    rp_seats: int,                        # escaños RP a asignar (típicamente 32)
    params: SenParams
) -> Dict[str, int]:
    """
    Asigna escaños de RP para senado usando Largest Remainder.
    Implementa la lógica de asigna_senado_RP del script R.
    """
    parties = list(votos_partido_nacional.index)
    x = votos_partido_nacional.fillna(0).to_numpy(dtype=float)
    
    # Verificar entrada válida
    if len(x) == 0 or x.sum() <= 0 or rp_seats <= 0:
        return {p: 0 for p in parties}
    
    # Calcular porcentajes válidos
    total_votos = x.sum()
    v_valida = x / total_votos
    
    # Aplicar umbral
    mask = v_valida < params.threshold
    v_nacional = v_valida.copy()
    v_nacional[mask] = 0
    
    # Renormalizar después del umbral
    if v_nacional.sum() > 0:
        v_nacional = v_nacional / v_nacional.sum()
    else:
        return {p: 0 for p in parties}
    
    # Asignar usando Largest Remainder (equivalente a la lógica del R)
    t = np.floor(v_nacional * rp_seats + 1e-12).astype(int)
    u = rp_seats - t.sum()
    
    if u > 0:
        rema = v_nacional * rp_seats - t
        # Ordenar por residuo descendente, desempatar por índice
        ord_indices = np.argsort([-r if r > 0 else -1e10 for r in rema])
        for i in range(u):
            t[ord_indices[i]] += 1
    
    return {parties[i]: int(t[i]) for i in range(len(parties))}            

def assign_diputados(
    votos_partido_nacional: pd.Series,     # votos absolutos nacionales por partido (post-recomposición)
    ssd_por_partido: Dict[str, int],       # MR por partido (alineado al universo)
    params: DipParams
) -> Dict[str, Dict[str, int]]:
    """
    Devuelve dict con 'mr', 'rp', 'tot' por partido.
    """
    parties = list(votos_partido_nacional.index)
    x = votos_partido_nacional.fillna(0).to_numpy(dtype=float)
    s_mr = np.array([ssd_por_partido.get(p, 0) for p in parties], dtype=int)

    # sanity MR
    if s_mr.sum() != params.mr_seats:
        # reescalar proporcionalmente manteniendo enteros
        if s_mr.sum() > 0:
            s_mr = largest_remainder(s_mr.astype(float), params.mr_seats, "hare")
        else:
            s_mr = np.zeros_like(s_mr)

    m_rp = max(0, params.S - params.mr_seats)

    VTE = float(x.sum())
    VVE = VTE 
    share_valid = (x / VVE) if VVE > 0 else np.zeros_like(x)
    ok = share_valid >= params.threshold
    x_ok = x.copy()
    x_ok[~ok] = 0.0

    # base RP
    if m_rp == 0 or x_ok.sum() <= 0:
        s_rp_init = np.zeros_like(s_mr)
    else:
        if params.use_divisor_for_rp and params.divisor_method:
            s_rp_init = divisor_apportionment(x_ok, m_rp, params.divisor_method)
        else:
            s_rp_init = largest_remainder(x_ok, m_rp, params.quota_method)

    # v_nacional normalizada SOLO con partidos ok
    v_nac = x_ok / x_ok.sum() if x_ok.sum() > 0 else np.zeros_like(x_ok)

    # topes nacionales
    s_rp_cap, s_tot = apply_caps_national(
        s_mr=s_mr, s_rp=s_rp_init, v_nac=v_nac,
        S=params.S, max_pp=params.max_pp, max_seats=params.max_seats
    )

    # sobrerrepresentación 
    if params.overrep_cap is not None and VVE > 0:
        s_tot = apply_overrep_cap(
            s_tot, vote_share_valid=share_valid, S=params.S, over_cap=params.overrep_cap
        )
        s_rp_cap = np.maximum(0, s_tot - s_mr)

    out = {
        "mr": dict(zip(parties, s_mr.astype(int))),
        "rp": dict(zip(parties, s_rp_cap.astype(int))),
        "tot": dict(zip(parties, s_tot.astype(int))),
    }
    return out
