# wrappers.py
from __future__ import annotations
from typing import Dict, Any, Optional, Tuple
import math
import pandas as pd

from .recomposicion import recompose_coalitions, parties_for
# Usar archivos relativos del engine:
from .procesar_diputados import procesar_diputados_parquet
from .procesar_senadores_v2 import procesar_senadores_v2
from .core import (
    assign_diputados,
    largest_remainder, 
    divisor_apportionment,
    mr_by_siglado,
    DipParams
)

# -------------------- helpers de parsing --------------------

def _to_float(x: Any) -> float:
    if x is None: return float("nan")
    if isinstance(x, (int, float)): return float(x)
    s = str(x).strip().lower().replace(",", ".")
    s = s.replace("%", "")
    try:
        v = float(s)
        return v
    except:
        return float("nan")

def parse_percent(x: Any, default: Optional[float]=None) -> Optional[float]:
    """
    Acepta 3, 3.0, 0.03, "3", "3%", "0.03", etc. Devuelve proporción (0-1).
    """
    if x is None: return default
    s = str(x).strip().lower().replace(",", ".")
    if s.endswith("%"):
        try: return float(s[:-1]) / 100.0
        except: return default
    v = _to_float(s)
    if math.isnan(v): return default
    return v/100.0 if v > 1 else v

def parse_plus_pp(x: Any, default: float=0.08) -> float:
    """
    +pp: “8”, “8pp”, “0.08” → 0.08
    """
    if x is None: return default
    s = str(x).strip().lower().replace("pp", "").replace("+", "")
    v = _to_float(s)
    if math.isnan(v): return default
    return v/100.0 if v > 1 else v

def parse_max_seats(x: Any, default: Optional[int]=None) -> Optional[int]:
    """
    Tope de escaños absolutos por partido: “<100”, “100”, None
    """
    if x is None: return default
    s = str(x).strip().lower()
    s = s.replace("<", "").replace("≤", "")
    v = _to_float(s)
    if math.isnan(v): return default
    return int(round(v))

def parse_int(x: Any, default: int) -> int:
    try:
        return int(float(str(x).strip()))
    except:
        return default

def parse_system(s: str) -> str:
    s = (s or "").strip().lower()
    if s in {"mixto","mix","mixed"}: return "mixto"
    if s in {"rp","proporcional"}:   return "rp"
    if s in {"mr","mayoria","mr_puro"}: return "mr"
    return "mixto"

def _ok_parties_vector(vec: Dict[str, int|float]) -> Dict[str, float]:
    return {k: float(v or 0) for k,v in vec.items()}

# -------------------- carga de boletas --------------------

def load_boleta(anio: int, camara: str) -> pd.DataFrame:
    cam = camara.lower().strip()
    if cam == "diputados":
        path = f"data/computos_diputados_{anio}.parquet"
        df = pd.read_parquet(path)
        # Estándares mínimos:
        assert "ENTIDAD" in df.columns and "DISTRITO" in df.columns, "Diputados requiere ENTIDAD y DISTRITO"
        return df
    elif cam == "senado":
        # Usar tus archivos reales de senado
        path = f"data/computos_senado_{anio}.parquet"
        df = pd.read_parquet(path)
        # normaliza numéricos
        for c in df.columns:
            if c not in {"ENTIDAD"}:
                df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
        assert "ENTIDAD" in df.columns, "Senado requiere ENTIDAD"
        return df
    else:
        raise ValueError("Cámara inválida.")

def siglado_path_for(anio: int, camara: str) -> Optional[str]:
    cam = camara.lower().strip()
    if cam == "diputados":
        if anio == 2018: return "data/ine_cg2018_diputados_siglado_long.csv"
        if anio == 2021: return "data/ine_cg466_2021_grupo_parlamentario_por_distrito.csv"
        if anio == 2024: return "data/ine_cges2024_grupo_parlamentario_por_distrito.csv"
    elif cam == "senado":
        if anio == 2018: return "data/siglado_senado_2018_corregido.csv"
        if anio == 2024: return "data/siglado-senado-2024.csv"
    return None

# -------------------- wrapper principal --------------------

def run_simulacion(
    *,
    anio: int,
    camara: str,                  # "diputados" | "senado"
    modelo: str,                  # "vigente" | "plan_a" | "plan_c" | "personalizado"
    sistema: Optional[str]=None,  # "mixto" | "rp" | "mr" (para personalizado)
    magnitud: Optional[int]=None, # S total (p.ej. 500 diputados, 128 senado) o definido por usuario
    mixto_mr_seats: Optional[int]=None,  # solo para sistema=mixto
    umbral: Optional[str|float|int]=None,    # 3, "3%", 0.03
    quota_method: str="hare",     # "hare","droop","imperiali"...
    divisor_method: str="dhondt", # "dhondt","sainte-lague","modified-sainte-lague"
    max_pp: Optional[str|float|int]=0.08,    # +pp (8 -> 0.08)
    max_seats_per_party: Optional[str|int]=None,  # "<100", 100, None
    sobrerrepresentacion: Optional[str|float|int]=None, # 8 -> 0.08
    recomposicion_rule: str="equal_residue_solo", # o "equal_residue_siglado"
) -> Dict[str, Any]:
    """
    Devuelve un dict estilo:
    {
      "mr":  {party: seats},
      "rp":  {party: seats},
      "tot": {party: seats},
      "ok":  {party: bool (pasó umbral)},
      "votos": {party: votos_abs (recompuestos)},
      "votos_ok": {party: votos_abs (solo quienes pasan umbral)},
      "meta": {...}
    }
    """
    cam = camara.lower().strip()
    model = (modelo or "").strip().lower()
    sistema = parse_system(sistema or ("mixto" if model in {"vigente","personalizado"} else ("mr" if model=="plan_c" else "rp")))
    parties = parties_for(anio)

    # --- S y m (MR/RP) por default según cámara/modelo ---
    if magnitud is None:
        magnitud = 500 if cam == "diputados" else 128
    S = int(magnitud)

    if sistema == "mixto":
        # default “vigente”: Dip 300 MR + 200 RP; Sen 96 MR/PM + 32 RP
        if mixto_mr_seats is None:
            mixto_mr_seats = 300 if cam == "diputados" else 96
        m_rp = S - int(mixto_mr_seats)
        m_mr = int(mixto_mr_seats)
    elif sistema == "rp":
        m_rp = S
        m_mr = 0
    else:  # "mr"
        m_rp = 0
        m_mr = S

    # --- parámetros legales ---
    thr = parse_percent(umbral, default=(0.03 if cam=="diputados" else 0.03))
    plus_pp = parse_plus_pp(max_pp, default=0.08) if max_pp is not None else None
    cap_abs = parse_max_seats(max_seats_per_party, default=None)
    overrep = parse_percent(sobrerrepresentacion, default=None)

    # --- boleta y recomposición ---
    boleta = load_boleta(anio, cam)
    sig_path = siglado_path_for(anio, cam) if recomposicion_rule == "equal_residue_siglado" else None
    rec = recompose_coalitions(
        df=boleta,
        year=anio,
        chamber=cam,
        rule=recomposicion_rule,
        siglado_path=sig_path
    )

    # votos por partido (nacionales)
    party_cols = [p for p in parties if p in rec.columns]
    votos_party = rec[party_cols].sum(axis=0).to_dict()
    votos_party = _ok_parties_vector(votos_party)

    # --- MR (si aplica): usar siglado o cálculo directo ---
    if m_mr > 0:
        # Usar mr_by_siglado o calcular directamente
        if sig_path and cam == "diputados":
            mr_sig = mr_by_siglado(boleta, sig_path, anio)
        elif cam == "diputados":
            # Usar tu función procesar_diputados_parquet para obtener MR
            result_dip = procesar_diputados_parquet(
                path_parquet=None,  # Ya tienes boleta
                partidos_base=parties,
                anio=anio,
                path_siglado=sig_path,
                max_seats=S,
                sistema=sistema,
                mr_seats=m_mr,
                rp_seats=m_rp
            )
            mr_sig = result_dip.get('mr', {}) if result_dip else {}
        else:
            # Para senadores
            parquet_path = f"data/computos_senado_{anio}.parquet"
            result_sen = procesar_senadores_v2(
                path_parquet=parquet_path,
                anio=anio,
                path_siglado=sig_path,
                partidos_base=parties,
                max_seats=S,
                umbral=thr if thr else 0.03,
                sistema=sistema,
                mr_seats=m_mr,
                rp_seats=m_rp
            )
            mr_sig = result_sen.get('mr', {}) if result_sen else {}
        
        ssd_party = {p: int(mr_sig.get(p, 0)) for p in parties}
        
        # Ajustar si el total MR no coincide
        total_mr_original = sum(ssd_party.values())
        if total_mr_original and total_mr_original != m_mr:
            factor = m_mr / total_mr_original
            # redondeo por resto
            base = {p: int(math.floor(ssd_party[p] * factor)) for p in parties}
            resto = m_mr - sum(base.values())
            if resto > 0:
                # reparte sobrantes por los mayores residuos
                residues = {p: (ssd_party[p] * factor - base[p]) for p in parties}
                for p,_ in sorted(residues.items(), key=lambda kv: kv[1], reverse=True)[:resto]:
                    base[p] += 1
            ssd_party = base
    else:
        ssd_party = {p: 0 for p in parties}

    # --- asignación usando tu función real ---
    if cam == "diputados":
        # Crear parámetros para assign_diputados
        params = DipParams(
            S=S,
            mr_seats=m_mr,
            threshold=thr,
            quota_method=quota_method,
            divisor_method=divisor_method,
            use_divisor_for_rp=(divisor_method is not None),
            max_pp=plus_pp,
            max_seats=cap_abs or 300,
            overrep_cap=overrep
        )
        
        # Convertir votos a Series
        votos_series = pd.Series(votos_party)
        
        # Usar tu función principal
        result = assign_diputados(votos_series, ssd_party, params)
        
    else:  # senadores - usar tu función de senadores
        parquet_path = f"data/computos_senado_{anio}.parquet"
        result_sen = procesar_senadores_v2(
            path_parquet=parquet_path,
            anio=anio,
            path_siglado=sig_path,
            partidos_base=parties,
            max_seats=S,
            umbral=thr if thr else 0.03,
            sistema=sistema,
            mr_seats=m_mr,
            rp_seats=m_rp
        )
        result = result_sen if result_sen else {"mr": {}, "rp": {}, "tot": {}}

    # --- resultado final ---
    # Asegurar que todas las claves existen
    if "mr" not in result:
        result["mr"] = {p: 0 for p in parties}
    if "rp" not in result:
        result["rp"] = {p: 0 for p in parties}  
    if "tot" not in result:
        result["tot"] = {p: result["mr"].get(p, 0) + result["rp"].get(p, 0) for p in parties}
    if "votos" not in result:
        result["votos"] = votos_party
    if "votos_ok" not in result:
        # Filtrar partidos que pasan umbral
        total_votos = sum(votos_party.values())
        result["votos_ok"] = {p: v for p, v in votos_party.items() if v/total_votos >= thr} if total_votos > 0 else {}
    if "ok" not in result:
        total_votos = sum(votos_party.values())  
        result["ok"] = {p: (v/total_votos >= thr) for p, v in votos_party.items()} if total_votos > 0 else {p: False for p in parties}

    # --- metadata amigable ---
    result.setdefault("meta", {})
    result["meta"].update({
        "anio": anio,
        "camara": cam,
        "modelo": model,
        "sistema": sistema,
        "S": S,
        "m_rp": m_rp,
        "m_mr": m_mr,
        "threshold": thr,
        "quota_method": quota_method,
        "divisor_method": divisor_method,
        "max_plus_pp": plus_pp,
        "max_seats_abs": cap_abs,
        "sobrerrepresentacion": overrep,
        "recomposicion_rule": recomposicion_rule
    })
    return result
