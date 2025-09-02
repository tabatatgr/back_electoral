# recomposicion.py
from __future__ import annotations
from typing import Dict, List, Tuple, Optional
import re
import math
import pandas as pd

# ======================== Config por año/cámara ========================

PARTIDOS_2018 = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","NA"]
PARTIDOS_2021 = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","RSP","FXM"]
PARTIDOS_2024 = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA"]
ALL_PARTIES = sorted(set(PARTIDOS_2018 + PARTIDOS_2021 + PARTIDOS_2024 + ["NA","PES","RSP","FXM","CI"]))

import re
import unicodedata


def parties_for(year: int) -> List[str]:
    if year == 2018:
        return PARTIDOS_2018
    if year == 2021:
        return PARTIDOS_2021
    if year == 2024:
        return PARTIDOS_2024
    # fallback: universo completo sin duplicados
    return [p for p in ALL_PARTIES if p != "CI"]

def _normalize_text(s: str) -> str:
    # alias que usan los loaders de siglado
    return norm_ascii_up(s)

def _tokens_from_col(col: str) -> List[str]:
    if not col:
        return []
    return [t for t in re.split(r"[-_]", col.upper()) if t]

def split_tokens(col: str) -> List[str]:
    # corregida: NO recursiva
    return _tokens_from_col(col)

def _is_candidate_col(col: str, year: int) -> bool:
    toks = _tokens_from_col(col)
    if not toks:
        return False
    valid = set(parties_for(year) + ["CI"])
    return all(t in valid for t in toks)

def _is_coalition_col(col: str, year: int) -> bool:
    toks = _tokens_from_col(col)
    if not toks:
        return False
    valid = set(parties_for(year))
    return (len(toks) >= 2) and all(t in valid for t in toks)

def norm_ascii_up(s: str) -> str:
    if s is None: return ""
    s = str(s).strip().upper()
    s = unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode("ASCII")
    s = re.sub(r"\s+", " ", s)
    return s

def normalize_entidad_ascii(x: str) -> str:
    x = norm_ascii_up(x)
    x = x.replace(".", "")
    x = re.sub(r"^CDMX$|^DISTRITO FEDERAL$", "CIUDAD DE MEXICO", x)
    x = re.sub(r"^Q\s*ROO$|^QROO$", "QUINTANA ROO", x)
    x = re.sub(r"^QUERETARO DE ARTEAGA$", "QUERETARO", x)
    x = x.replace("ESTADO DE MEXICO", "MEXICO")
    x = x.replace("MICHOACAN DE OCAMPO", "MICHOACAN")
    x = x.replace("VERACRUZ DE IGNACIO DE LA LLAVE", "VERACRUZ")
    x = x.replace("COAHUILA DE ZARAGOZA", "COAHUILA")
    return x

def canonizar_siglado(x: str) -> str:
    y = norm_ascii_up(x)
    y = re.sub(r"\bGRUPO PARLAMENTARIO\b|\bGP\b|\bPARTIDO\b", "", y)
    y = re.sub(r"\s+", " ", y).strip()
    # siglas partidos:
    y = re.sub(r"\bMOVIMIENTO CIUDADANO\b|\bMC\b", "MC", y)
    y = re.sub(r"\bVERDE\b|PARTIDO VERDE|\bPVEM\b|\bP V E M\b", "PVEM", y)
    y = re.sub(r"ENCUENTRO SOCIAL|ENCUENTRO SOLIDARIO|\bPES\b", "PES", y)
    y = re.sub(r"FUERZA POR MEXICO|\bFXM\b", "FXM", y)
    y = re.sub(r"\bMORENA\b", "MORENA", y)
    y = re.sub(r"PARTIDO DEL TRABAJO|\bPT\b", "PT", y)
    y = re.sub(r"PARTIDO ACCION NACIONAL|\bPAN\b", "PAN", y)
    y = re.sub(r"PARTIDO REVOLUCIONARIO INSTITUCIONAL|\bPRI\b", "PRI", y)
    y = re.sub(r"PARTIDO DE LA REVOLUCION DEMOCRATICA|\bPRD\b", "PRD", y)
    y = re.sub(r"NUEVA ALIANZA|\bNA\b|\bPANAL\b", "NA", y)
    # coaliciones 2018 (texto canónico sin acentos):
    y = y.replace("JUNTOS HAREMOS HISTORIA", "JUNTOS HAREMOS HISTORIA")
    y = y.replace("POR MEXICO AL FRENTE", "POR MEXICO AL FRENTE")
    y = y.replace("TODOS POR MEXICO", "TODOS POR MEXICO")
    # 2024
    y = y.replace("SIGAMOS HACIENDO HISTORIA", "SIGAMOS HACIENDO HISTORIA")
    y = y.replace("FUERZA Y CORAZON POR MEXICO", "FUERZA Y CORAZON POR MEXICO")
    return y


def canonizar_coalicion(tokens, anio):
    S = sorted(set(t.upper().strip() for t in tokens if t))
    if anio == 2018:
        if set(S) == {"MORENA", "PT", "PES"}:
            return "JUNTOS HAREMOS HISTORIA"
        if set(S) == {"PAN", "PRD", "MC"}:
            return "POR MEXICO AL FRENTE"
        if set(S) == {"PRI", "PVEM", "NA"}:
            return "TODOS POR MEXICO"
        if len(S) == 1 and S[0] in {"PAN", "PRI", "PRD", "PVEM", "PT", "MC", "MORENA", "PES", "NA", "CI"}:
            return S[0]
        return None
    if anio == 2021:
        if set(S) == {"PAN", "PRI", "PRD"}:
            return "VA POR MEXICO"
        if len(S) == 1 and S[0] in {"PAN", "PRI", "PRD", "PVEM", "PT", "MC", "MORENA", "PES", "RSP", "FXM", "CI"}:
            return S[0]
        return None
    if anio == 2024:
        if set(S) == {"MORENA", "PT", "PVEM"}:
            return "SIGAMOS HACIENDO HISTORIA"
        if set(S) == {"PAN", "PRI", "PRD"}:
            return "FUERZA Y CORAZON POR MEXICO"
        if len(S) == 1 and S[0] in {"PAN", "PRI", "PRD", "PVEM", "PT", "MC", "MORENA", "CI"}:
            return S[0]
        return None
    return None


def split_tokens(col: str):
    if not col:
        return []
    return [t for t in re.split(r"[-_]", col.upper()) if t]

def _is_candidate_col(col: str, year: int) -> bool:
    toks = _tokens_from_col(col)
    if not toks: return False
    valid = set(parties_for(year) + ["CI"])
    return all(t in valid for t in toks)

def _is_coalition_col(col: str, year: int) -> bool:
    toks = _tokens_from_col(col)
    if not toks: return False
    valid = set(parties_for(year))
    return len(toks) >= 2 and all(t in valid for t in toks)

def _solo_party_cols(df: pd.DataFrame, party: str) -> List[str]:
    patt = re.compile(rf"(^|[-_]){re.escape(party)}($|[-_])")
    return [c for c in df.columns if bool(patt.search(c)) and c.upper() == party]

# ==================== Siglado (mapas por fila) ====================

def _load_siglado_dip(path_csv: str) -> pd.DataFrame:
    """Esperado: columnas (entidad|entidad_ascii), (distrito), coalicion, grupo_parlamentario|partido_origen"""
    gp = pd.read_csv(path_csv, dtype=str, encoding="utf-8", keep_default_na=False)
    gp.columns = [c.strip().lower() for c in gp.columns]
    # normaliza llaves
    if "entidad_ascii" in gp.columns:
        gp["entidad_key"] = gp["entidad_ascii"].map(_normalize_text)
    elif "entidad" in gp.columns:
        gp["entidad_key"] = gp["entidad"].map(_normalize_text)
    else:
        raise ValueError("Siglado DIP: falta columna ENTIDAD/entidad_ascii.")
    if "distrito" not in gp.columns:
        raise ValueError("Siglado DIP: falta columna DISTRITO.")
    gp["distrito"] = gp["distrito"].astype(str).str.extract(r"(\d+)").fillna("0").astype(int)
    # toma GP o partido_origen
    gp["dominante"] = gp.get("grupo_parlamentario", "").fillna("") \
        .where(gp.get("grupo_parlamentario", "").astype(str).str.len()>0,
               gp.get("partido_origen", ""))
    gp["dominante"] = gp["dominante"].map(_normalize_text)
    # clave de coalición 
    if "coalicion" in gp.columns:
        gp["coalicion_key"] = gp["coalicion"].map(_normalize_text)
    else:
        gp["coalicion_key"] = ""
    return gp[["entidad_key","distrito","coalicion_key","dominante"]]

def _load_siglado_sen(path_csv: str) -> pd.DataFrame:
    """Esperado: columnas ENTIDAD, COALICION, FORMULA, GRUPO_PARLAMENTARIO|PARTIDO_ORIGEN"""
    gp = pd.read_csv(path_csv, dtype=str, encoding="utf-8", keep_default_na=False)
    gp.columns = [c.strip().upper() for c in gp.columns]
    
    # Manejar caso donde viene ENTIDAD_ASCII en lugar de ENTIDAD
    if 'ENTIDAD_ASCII' in gp.columns and 'ENTIDAD' not in gp.columns:
        gp['ENTIDAD'] = gp['ENTIDAD_ASCII']
    
    req = {"ENTIDAD","COALICION","FORMULA"}
    if not req.issubset(set(gp.columns)):
        available = list(gp.columns)
        raise ValueError(f"Siglado SEN: se esperan columnas ENTIDAD, COALICION, FORMULA. Disponibles: {available}")
    dom_col = "GRUPO_PARLAMENTARIO" if "GRUPO_PARLAMENTARIO" in gp.columns else "PARTIDO_ORIGEN"
    gp["DOMINANTE"] = gp[dom_col].fillna("").map(_normalize_text)
    gp["ENTIDAD_KEY"] = gp["ENTIDAD"].map(_normalize_text)
    gp["COALICION_KEY"] = gp["COALICION"].map(_normalize_text)
    gp["FORMULA"] = gp["FORMULA"].astype(str).str.extract(r"(\d+)").fillna("0").astype(int)
    gp = gp.sort_values(["ENTIDAD_KEY","COALICION_KEY","FORMULA"])
    gp_dom = gp.drop_duplicates(["ENTIDAD_KEY","COALICION_KEY"], keep="first")
    return gp_dom[["ENTIDAD_KEY","COALICION_KEY","DOMINANTE"]]

# ================== Reglas de residuo (selector) ==================

def _pick_residue_solo(row: pd.Series, parties: List[str], tokens: List[str]) -> str:
    # el "dominante" es el que tiene más voto "solo" en esta fila
    solos = {p: float(row.get(p, 0) or 0) for p in tokens if p in parties}
    if not solos: return tokens[0]
    return max(solos.items(), key=lambda kv: kv[1])[0]

def _pick_residue_siglado_dip(row: pd.Series, sig_map: pd.DataFrame, tokens: List[str]) -> str:
    ent = _normalize_text(str(row.get("ENTIDAD", "")))
    dist = int(re.findall(r"\d+", str(row.get("DISTRITO", "0")))[0]) if re.findall(r"\d+", str(row.get("DISTRITO", "0"))) else 0
    # intenta buscar dominante para esa ENTIDAD/DISTRITO y la coalición (a partir de tokens)
    # como "coalicion_key" en siglado puede no coincidir con tokens, nos quedamos con el dominante si es uno de los tokens
    hit = sig_map[(sig_map["entidad_key"]==ent) & (sig_map["distrito"]==dist)]
    if len(hit):
        dom = str(hit.iloc[0]["dominante"])
        if dom in tokens:
            return dom
    # fallback a solo
    return _pick_residue_solo(row, parties_for_guess(tokens), tokens)

def _pick_residue_siglado_sen(row: pd.Series, sig_map: pd.DataFrame, tokens: List[str]) -> str:
    ent = _normalize_text(str(row.get("ENTIDAD", "")))
    hit = sig_map[(sig_map["ENTIDAD_KEY"]==ent)]
    if len(hit):
        dom = str(hit.iloc[0]["DOMINANTE"])
        if dom in tokens:
            return dom
    # fallback a solo
    return _pick_residue_solo(row, parties_for_guess(tokens), tokens)

def parties_for_guess(tokens: List[str]) -> List[str]:
    # ayuda a no romper si viene mezcla de años
    candidates = sorted(set(tokens) & set(ALL_PARTIES))
    return candidates or tokens

# ================== Recomposición principal ==================

def recompose_coalitions(
    df: pd.DataFrame,
    year: int,
    chamber: str,  # "diputados" | "senado"
    rule: str = "equal_residue_solo",  # o "equal_residue_siglado"
    siglado_path: Optional[str] = None
) -> pd.DataFrame:
    """
    Devuelve un DataFrame con columnas: ENTIDAD, (DISTRITO si aplica), PARTIDOS..., CI, TOTAL_BOLETAS
    donde cada fila trae los votos recombinados por partido.
    """
    chamber = chamber.lower().strip()
    parties = parties_for(year)

    # Copia y llaves mínimas
    out = pd.DataFrame()
    if "ENTIDAD" not in df.columns:
        raise ValueError("Se requiere columna 'ENTIDAD' en el DataFrame de boleta.")
    out["ENTIDAD"] = df["ENTIDAD"]

    if chamber == "diputados":
        if "DISTRITO" not in df.columns:
            raise ValueError("Diputados requiere columna 'DISTRITO'.")
        out["DISTRITO"] = pd.to_numeric(df["DISTRITO"], errors="coerce").fillna(0).astype(int)

    # Prepara mapa de siglado si la regla lo pide
    sig_map = None
    if rule == "equal_residue_siglado":
        if not siglado_path:
            raise ValueError("Para 'equal_residue_siglado' debes pasar siglado_path.")
        sig_map = _load_siglado_dip(siglado_path) if chamber=="diputados" else _load_siglado_sen(siglado_path)

    # Inicializa columnas por partido y CI
    for p in parties:
        out[p] = 0.0
    if "CI" in df.columns:
        out["CI"] = pd.to_numeric(df["CI"], errors="coerce").fillna(0.0)
    else:
        out["CI"] = 0.0

    # Identifica columnas candidaturas
    cand_cols = [c for c in df.columns if _is_candidate_col(c, year)]
    if not cand_cols:
        raise ValueError("No encuentro columnas de candidaturas para ese año.")

    # primero, suma votos "solo" por partido
    for p in parties:
        if p in df.columns:
            out[p] += pd.to_numeric(df[p], errors="coerce").fillna(0.0)

    # ahora procesa coaliciones
    coal_cols = [c for c in cand_cols if _is_coalition_col(c, year)]
    for c in coal_cols:
        tokens = _tokens_from_col(c)
        k = len(tokens)
        V = pd.to_numeric(df[c], errors="coerce").fillna(0.0)

        # parte entera para todos
        q = (V // k).astype(float)
        r = (V %  k).astype(int)

        for p in tokens:
            out[p] += q

        # reparte residuo 1-a-1 usando la regla seleccionada
        for i in range(len(df)):
            if r.iat[i] <= 0: 
                continue
            row = df.iloc[i]
            if rule == "equal_residue_siglado" and sig_map is not None:
                pick = _pick_residue_siglado_dip(row, sig_map, tokens) if chamber=="diputados" else _pick_residue_siglado_sen(row, sig_map, tokens)
            else:
                pick = _pick_residue_solo(row, parties, tokens)
            out.at[i, pick] += float(r.iat[i])

    # TOTAL_BOLETAS (partidos + CI)
    party_cols = [p for p in parties]
    out["TOTAL_BOLETAS"] = out[party_cols].sum(axis=1, numeric_only=True) + out["CI"]

    # orden columnas amigable
    base_cols = ["ENTIDAD"] + (["DISTRITO"] if chamber=="diputados" else [])
    out = out[ base_cols + party_cols + (["CI"] if "CI" in out.columns else []) + ["TOTAL_BOLETAS"] ]

    return out
