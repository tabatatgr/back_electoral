# ============================================================
# procesar_diputados_v2.py - VERSIÓN MEJORADA
# ------------------------------------------------------------
# Implementa asignación de diputaciones con algoritmos más robustos
# basados en la implementación de R (asignadip_ine.R)
#
# Mejoras clave:
# 1. LR_ties: Algoritmo Hare con desempates por votación absoluta + randomización
# 2. Aplicación de topes nacionales iterativa y robusta
# 3. Partidos <3% solo reciben MR, nunca RP
# 4. Validaciones estrictas de constitucionalidad
# ============================================================

import numpy as np
import pandas as pd
import os
import re
import unicodedata
import logging
from typing import Dict, List, Optional, Tuple
from .recomposicion import recompose_coalitions, parties_for, _load_siglado_dip
from .scale_siglado import scale_siglado
from .core import apply_overrep_cap
from .core import DipParams
from .core import largest_remainder, divisor_apportionment

# Configurar logger del módulo
logger = logging.getLogger(__name__)
if not logger.handlers:
    # handler por defecto que no doble el logging si ya está configurado por el consumidor
    ch = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(logging.INFO)

# Helper para logging que respeta el flag print_debug
def _maybe_log(msg: str, level: str = 'debug', print_debug: bool = False):
    """Registra msg usando logger; si print_debug=True registra todo (debug/info/warn/error),
    si False registra solo warnings y errors.
    """
    lvl = level.lower()
    if print_debug:
        if lvl in ('warn', 'warning'):
            logger.warning(msg)
        elif lvl == 'error':
            logger.error(msg)
        elif lvl == 'info':
            logger.info(msg)
        else:
            logger.debug(msg)
    else:
        if lvl in ('warn', 'warning'):
            logger.warning(msg)
        elif lvl == 'error':
            logger.error(msg)

# ====================== UTILIDADES ======================

def norm_ascii_up(s: str) -> str:
    """Normaliza texto a ASCII mayúsculas"""
    if s is None: 
        return ""
    s = str(s).strip().upper()
    s = unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode("ASCII")
    s = re.sub(r"\s+", " ", s)
    return s

def normalize_entidad_ascii(x: str) -> str:
    """Normaliza nombres de entidades federativas"""
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

# ====================== SISTEMA DE COALICIONES ======================

def extraer_coaliciones_de_siglado(siglado_path: str, anio: int) -> Dict[str, List[str]]:
    """
    Extrae coaliciones del archivo siglado
    """
    coaliciones = {}
    
    try:
        siglado = pd.read_csv(siglado_path)
        logger.debug(f"Extrayendo coaliciones del siglado: {siglado_path}")

        # Verificar estructura del archivo
        if 'coalicion' not in siglado.columns or 'grupo_parlamentario' not in siglado.columns:
            logger.debug(f"Archivo siglado no tiene estructura esperada: {siglado.columns.tolist()}")
            return {}

        # Renombrar columnas para estandarizar
        siglado = siglado.rename(columns={'coalicion': 'COALICION', 'grupo_parlamentario': 'PARTIDO_ORIGEN'})

        # Agrupar por coalición y obtener partidos únicos
        for coalicion_name in siglado['COALICION'].unique():
            if pd.isna(coalicion_name) or coalicion_name.strip() == '':
                continue

            partidos_en_coalicion = siglado[siglado['COALICION'] == coalicion_name]['PARTIDO_ORIGEN'].unique()
            partidos_limpios = [p for p in partidos_en_coalicion if pd.notna(p) and p.strip() != '']

            if len(partidos_limpios) > 1:  # Solo considerar verdaderas coaliciones (más de 1 partido)
                # Normalizar nombre de coalición para que coincida con las columnas del dataset
                nombre_normalizado = coalicion_name.upper().replace(' ', '_')
                coaliciones[nombre_normalizado] = sorted(partidos_limpios)

        logger.debug(f"Coaliciones detectadas: {coaliciones}")
        return coaliciones
    except Exception as e:
        logger.error(f"Error leyendo siglado {siglado_path}: {e}")
        return {}

def agregar_columnas_coalicion(df, coaliciones):
    """
    Agrega columnas de coalición al DataFrame sumando los votos de los partidos miembros
    """
    df_modificado = df.copy()
    
    for coalicion_name, partidos in coaliciones.items():
        # Limpiar nombre de coalición para usar como columna
        col_name = coalicion_name.replace(' ', '_').replace('É', 'E').replace('Á', 'A')
        
        # Verificar que todos los partidos existan en el DataFrame
        partidos_disponibles = [p for p in partidos if p in df.columns]
        
        if len(partidos_disponibles) >= 2:  # Solo crear coalición si hay al menos 2 partidos
            # Sumar votos de los partidos de la coalición
            df_modificado[col_name] = df_modificado[partidos_disponibles].sum(axis=1)
            logger.debug(f"Coalición creada: {col_name} = {partidos_disponibles} ({df_modificado[col_name].sum():,} votos)")
    
    return df_modificado

def canonizar_siglado(x: str) -> str:
    """Canonización de siglado - idéntica al R"""
    y = norm_ascii_up(x)
    y = re.sub(r"\bGRUPO PARLAMENTARIO\b|\bGP\b|\bPARTIDO\b", "", y)
    y = re.sub(r"\s+", " ", y).strip()
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
    return y

def coalicion_de_tokens(tokens: List[str], anio: int) -> Optional[str]:
    """Determina coalición a partir de tokens - idéntica al R"""
    S = sorted(set(tokens))
    if anio == 2018:
        if set(S) == {"MORENA","PT","PES"}: 
            return "JUNTOS HAREMOS HISTORIA"
        if set(S) == {"PAN","PRD","MC"}:    
            return "POR MEXICO AL FRENTE"
        if set(S) == {"PRI","PVEM","NA"}:   
            return "TODOS POR MEXICO"
    elif anio == 2024:
        if set(S) == {"MORENA","PT","PVEM"}: 
            return "SIGAMOS HACIENDO HISTORIA"
        if set(S) == {"PAN","PRI","PRD"}:    
            return "FUERZA Y CORAZON POR MEXICO"
    return None

def cols_candidaturas_anio_con_coaliciones(df, anio: int) -> List[str]:
    """
    Detecta columnas de candidaturas incluyendo coaliciones
    """
    candidaturas = []
    
    for col in df.columns:
        if col in ['ENTIDAD', 'DISTRITO', 'TOTAL_BOLETAS', 'TOTAL_PARTIDOS_SUM', 'anio']:
            continue
        
        # Detectar partidos individuales
        if col in ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA', 'PES', 'NA', 'CI', 'FXM', 'RSP']:
            candidaturas.append(col)
        
        # Detectar coaliciones por patrones en el nombre
        col_upper = col.upper()
        if any(keyword in col_upper for keyword in ['FRENTE', 'HISTORIA', 'MEXICO', 'COALICION', 'ALIANZA']):
            candidaturas.append(col)
    
    return candidaturas

def partidos_de_col(col: str) -> List[str]:
    """
    Extrae partidos de un nombre de columna (individual o coalición)
    """
    # Casos especiales para coaliciones conocidas
    if col == "POR_MEXICO_AL_FRENTE":
        return ["PAN", "PRD", "MC"]
    elif col == "JUNTOS_HAREMOS_HISTORIA":
        return ["MORENA", "PT"]
    elif col in ["PAN", "PRI", "PRD", "PVEM", "PT", "MC", "MORENA", "PES", "NA", "CI", "FXM", "RSP"]:
        return [col]
    else:
        # Fallback: dividir por guión bajo
        return col.split("_")

# ====================== ALGORITMO LR CON DESEMPATES MEJORADO ======================

def asignar_rp_con_metodo(votos: np.ndarray, escanos: int, quota_method: Optional[str] = None, 
                         divisor_method: Optional[str] = None, seed: Optional[int] = None) -> np.ndarray:
    """
    Asigna escaños RP usando el método especificado (cuota O divisor)
    
    Args:
        votos: Array de votos por partido
        escanos: Número de escaños a asignar
        quota_method: Método de cuota ("hare", "droop", None)
        divisor_method: Método divisor ("dhondt", "saintelague", None)
        seed: Semilla para randomización en empates
    
    Returns:
        Array de escaños asignados por partido
    """
    if escanos <= 0 or np.sum(votos) <= 0:
        return np.zeros_like(votos, dtype=int)
    
    # Determinar qué método usar (exclusivo)
    if quota_method is not None and divisor_method is None:
        # MODO CUOTA: usar largest_remainder de core.py
        # Normalizar variantes de métodos de cuota
        method_normalized = quota_method.lower().replace("_", "").replace("-", "")
        
        if method_normalized in ["hare", "droop", "hb", "imperiali"]:
            _maybe_log(f"Usando método cuota: {method_normalized}", 'debug')
            return largest_remainder(votos, escanos, method_normalized)
        else:
            # Fallback a LR_ties original si método no reconocido
            _maybe_log(f"Método cuota '{quota_method}' no reconocido, usando LR_ties", 'debug')
            q = np.sum(votos) / escanos if escanos > 0 else 0
            return LR_ties(votos, n=escanos, q=q, seed=seed)
            
    elif divisor_method is not None and quota_method is None:
        # MODO DIVISOR: usar divisor_apportionment de core.py
        # Normalizar variantes de métodos divisores
        method_normalized = divisor_method.lower().replace("_", "").replace("-", "").replace("'", "")
        
        # Webster es equivalente a Sainte-Laguë
        if method_normalized == "webster":
            method_normalized = "saintelague"
        
        if method_normalized in ["dhondt", "saintelague"]:
            # Usar el nombre normalizado que acepta core.py
            _maybe_log(f"Usando método divisor: {method_normalized}", 'debug')
            return divisor_apportionment(votos, escanos, method_normalized)
        else:
            # Fallback a LR_ties si método no reconocido
            _maybe_log(f"Método divisor '{divisor_method}' no reconocido, usando LR_ties", 'debug')
            q = np.sum(votos) / escanos if escanos > 0 else 0
            return LR_ties(votos, n=escanos, q=q, seed=seed)
            
    else:
        # FALLBACK: usar LR_ties original (comportamiento anterior)
        _maybe_log(f"Sin método específico o ambos definidos, usando LR_ties por defecto", 'debug')
        q = np.sum(votos) / escanos if escanos > 0 else 0
        return LR_ties(votos, n=escanos, q=q, seed=seed)


def LR_ties(v_abs: np.ndarray, n: int, q: Optional[float] = None, seed: Optional[int] = None) -> np.ndarray:
    """
    Algoritmo Largest Remainder (Hare) con desempates sofisticados
    
    Parámetros:
    - v_abs: votos absolutos por partido
    - n: número total de escaños a distribuir
    - q: cuota (si None, se calcula como sum(v_abs)/n)
    - seed: semilla para desempates aleatorios
    
    Retorna:
    - Array de escaños asignados por partido
    """
    v_abs = np.nan_to_num(v_abs.astype(float))
    v_abs[~np.isfinite(v_abs)] = 0.0
    
    if not np.isfinite(q) if q is not None else False:
        q = None
    if q is None:
        q = np.sum(v_abs) / n if n > 0 else 0.0
    
    if q <= 0 or n <= 0:
        return np.zeros_like(v_abs, dtype=int)
    
    # Distribución base por cuota
    t = np.floor(v_abs / q).astype(int)
    u = int(n - np.sum(t))
    
    if u <= 0:
        return t
    
    # Calcular residuos
    rem = v_abs % q
    
    # Ordenamiento base por residuo descendente
    base_ord = np.argsort(-rem)
    
    if seed is not None:
        np.random.seed(seed)
    
    # Construir ranking final con desempates
    rank = np.zeros(len(v_abs), dtype=int)
    i = 0
    
    while i < len(base_ord):
        # Encontrar bloque de partidos con mismo residuo
        j = i
        while j < len(base_ord) and abs(rem[base_ord[j]] - rem[base_ord[i]]) < 1e-12:
            j += 1
        
        idx_bloque = base_ord[i:j]
        
        if len(idx_bloque) > 1:
            # Desempate por votación absoluta
            v_bloque = v_abs[idx_bloque]
            ord_votos = np.argsort(-v_bloque)
            
            # Identificar empates en votación
            empates = []
            k = 0
            while k < len(ord_votos):
                l = k
                while l < len(ord_votos) and abs(v_bloque[ord_votos[l]] - v_bloque[ord_votos[k]]) < 1e-12:
                    l += 1
                if l - k > 1:  # Hay empate
                    empates.extend(idx_bloque[ord_votos[k:l]])
                k = l
            
            # Resolver empates aleatoriamente
            if empates:
                perm_empates = np.random.permutation(empates)
                for orig, nuevo in zip(empates, perm_empates):
                    pos_orig = np.where(idx_bloque[ord_votos] == orig)[0][0]
                    idx_bloque[ord_votos[pos_orig]] = nuevo
            
            idx_bloque = idx_bloque[ord_votos]
        
        rank[i:j] = idx_bloque
        i = j
    
    # Asignar escaños restantes
    add = np.zeros_like(v_abs, dtype=int)
    for i in range(min(u, len(rank))):
        add[rank[i]] += 1
    
    return t + add

# ====================== APLICACIÓN DE TOPES NACIONALES ======================

def aplicar_topes_nacionales(s_mr: np.ndarray, s_rp: np.ndarray, v_nacional: np.ndarray, 
                           S: int, max_pp: float = 0.08, max_seats: int = 300, 
                           iter_max: int = 16) -> Dict[str, np.ndarray]:
    """
    Aplica topes constitucionales de forma iterativa
    
    Parámetros:
    - s_mr: escaños de MR por partido
    - s_rp: escaños de RP iniciales por partido  
    - v_nacional: proporción de votos nacionales (solo partidos >=3%)
    - S: total de escaños en la cámara
    - max_pp: máximo de sobrerrepresentación (+8 puntos porcentuales)
    - max_seats: tope absoluto de escaños (300)
    - iter_max: máximo de iteraciones
    
    Retorna:
    - Dict con 's_rp' (RP ajustado) y 's_tot' (total ajustado)
    """
    N = len(s_mr)
    s_mr = s_mr.astype(int)
    s_rp = s_rp.astype(int)
    
    rp_total = int(S - np.sum(s_mr))
    if rp_total < 0:
        rp_total = 0
    
    # Partidos elegibles (solo los que tienen v_nacional > 0)
    ok = v_nacional > 0
    
    # Límites por sobrerrepresentación (+8 pp)
    cap_dist = np.floor((v_nacional + max_pp) * S).astype(int)
    cap_dist[~ok] = s_mr[~ok]  # Partidos <3%: límite = MR únicamente
    
    # Límites finales (máximo entre MR y cap_dist, pero <= 300)
    lim_dist = np.maximum(s_mr, cap_dist)
    lim_300 = np.full(N, max_seats, dtype=int)
    lim_max = np.minimum(lim_dist, lim_300)
    
    s_tot = s_mr + s_rp
    
    # Iteración para aplicar topes
    for iteracion in range(iter_max):
        # Partidos que exceden límites
        over = np.where(s_tot > lim_max)[0]
        if len(over) == 0:
            break
        
        # Reducir RP de partidos que exceden
        s_rp[over] = np.maximum(0, lim_max[over] - s_mr[over])
        
        # Marcar partidos fijados
        fixed = np.zeros(N, dtype=bool)
        fixed[over] = True
        fixed[~ok] = True  # Partidos <3% también se fijan
        
        # Votos efectivos para redistribución (solo no fijados y elegibles)
        v_eff = v_nacional.copy()
        v_eff[fixed] = 0.0
        
        # RP ya fijados
        rp_fijos = int(np.sum(np.maximum(0, lim_max[fixed] - s_mr[fixed])))
        n_rest = max(0, rp_total - rp_fijos)
        
        # Redistribuir RP restantes
        if n_rest == 0 or np.sum(v_eff) <= 0:
            s_rp[~fixed] = 0
        else:
            q = np.sum(v_eff) / n_rest
            add = LR_ties(v_eff, n=n_rest, q=q)
            s_rp_nuevo = np.zeros(N, dtype=int)
            s_rp_nuevo[fixed] = np.maximum(0, lim_max[fixed] - s_mr[fixed])
            s_rp_nuevo[~fixed] = add[~fixed]

            # Actualizar s_rp con la nueva distribución
            s_rp = s_rp_nuevo

            # Asegurar que partidos <3% no reciben RP
            s_rp[~ok] = 0
            s_tot = s_mr + s_rp

            # Ajuste final para cumplir exactamente S escaños
            delta = int(S - np.sum(s_tot))
            if delta != 0:
                margin = lim_max - s_tot
                margin[~ok] = 0  # Solo partidos elegibles

                if delta > 0:
                    # Faltan escaños: asignar a quienes tienen margen
                    cand = np.where(margin > 0)[0]
                    if len(cand) > 0:
                        # Ordenar por proporción de votos descendente
                        ord_idx = np.argsort(-v_nacional[cand])
                        take = cand[ord_idx[:min(delta, len(cand))]]
                        s_rp[take] += 1
                else:
                    # Sobran escaños: quitar de quienes tienen RP
                    cand = np.where((s_rp > 0) & ok)[0]
                    if len(cand) > 0:
                        # Ordenar por RP descendente
                        ord_idx = np.argsort(-s_rp[cand])
                        take = cand[ord_idx[:min(-delta, len(cand))]]
                        s_rp[take] -= 1

            # Validación final: partidos que exceden +8pp no deben tener RP
            violadores = np.where(s_mr > np.floor((v_nacional + max_pp) * S))[0]
            if len(violadores) > 0:
                assert np.all(s_rp[violadores] == 0), f"Partidos que exceden +8pp tienen RP: {violadores}"

            return {
                's_rp': s_rp.astype(int),
                's_tot': (s_mr + s_rp).astype(int)
            }

    # Si salimos del bucle sin haber retornado (no hubo over o ya ajustado),
    # aplicar los ajustes finales y retornar siempre un dict.
    # Asegurar que partidos <3% no reciben RP
    s_rp[~ok] = 0
    s_tot = s_mr + s_rp

    # Ajuste final para cumplir exactamente S escaños
    delta = int(S - np.sum(s_tot))
    if delta != 0:
        margin = lim_max - s_tot
        margin[~ok] = 0  # Solo partidos elegibles

        if delta > 0:
            # Faltan escaños: asignar a quienes tienen margen
            cand = np.where(margin > 0)[0]
            if len(cand) > 0:
                # Ordenar por proporción de votos descendente
                ord_idx = np.argsort(-v_nacional[cand])
                take = cand[ord_idx[:min(delta, len(cand))]]
                s_rp[take] += 1
        else:
            # Sobran escaños: quitar de quienes tienen RP
            cand = np.where((s_rp > 0) & ok)[0]
            if len(cand) > 0:
                # Ordenar por RP descendente
                ord_idx = np.argsort(-s_rp[cand])
                take = cand[ord_idx[:min(-delta, len(cand))]]
                s_rp[take] -= 1

    # Validación final: partidos que exceden +8pp no deben tener RP
    violadores = np.where(s_mr > np.floor((v_nacional + max_pp) * S))[0]
    if len(violadores) > 0:
        assert np.all(s_rp[violadores] == 0), f"Partidos que exceden +8pp tienen RP: {violadores}"

    return {
        's_rp': s_rp.astype(int),
        's_tot': (s_mr + s_rp).astype(int)
    }


# --------------------- Export scenarios helper ---------------------
def _simulate_pm_by_runnerup(recomposed_df: pd.DataFrame, pm_seats: int, partidos: list) -> dict:
    """Simula asignación PM repartiendo a los partidos que fueron segundos por distrito.

    Devuelve un dict partido->escaños PM (conteo de apariciones entre segundos lugares, hasta pm_seats por moda).
    """
    from collections import Counter
    segundos = []
    for _, row in recomposed_df.iterrows():
        votos = [(p, float(row.get(p, 0) or 0.0)) for p in partidos]
        votos_sorted = sorted(votos, key=lambda x: -x[1])
        if len(votos_sorted) >= 2:
            segundos.append(votos_sorted[1][0])

    c = Counter(segundos)
    pm_dict = {p: 0 for p in partidos}
    for p, _ in c.most_common()[:pm_seats]:
        pm_dict[p] = c[p]
    return pm_dict

    

# ====================== ASIGNACIÓN PRINCIPAL ======================

def asignadip_v2(x: np.ndarray, ssd: np.ndarray, 
                 indep: int = 0, nulos: int = 0, no_reg: int = 0,
                 m: int = 200, S: Optional[int] = None,
                 threshold: float = 0.03,
                 max_seats: int = 300, max_pp: float = 0.08,
                 apply_caps: bool = True,
                 quota_method: Optional[str] = None,
                 divisor_method: Optional[str] = None,
                 seed: Optional[int] = None,
                 print_debug: bool = False) -> Dict:
    """
    Asignación de diputaciones versión 2 (basada en R)
    
    Parámetros:
    - x: votos nacionales por partido
    - ssd: escaños de MR por partido
    - indep: votos independientes
    - nulos: votos nulos  
    - no_reg: votos no registrados
    - m: escaños de RP a asignar
    - S: total de escaños (si None, se calcula como sum(ssd) + m)
    - threshold: umbral de 3% sobre VVE
    - max_seats: tope de 300 escaños por partido
    - max_pp: sobrerrepresentación máxima (+8 pp)
    - apply_caps: aplicar topes constitucionales
    - seed: semilla para desempates
    - print_debug: imprimir información de depuración
    
    Retorna:
    - Dict con 'votes', 'seats', 'meta'
    """
    x = np.array(x, dtype=float)
    ssd = np.array(ssd, dtype=int)
    
    if len(x) != len(ssd):
        raise ValueError("x y ssd deben tener la misma longitud")
    
    if S is None:
        S = int(np.sum(ssd) + m)
    
    # Cálculo de totales electorales
    VTE = int(np.sum(x) + indep + nulos + no_reg)
    VVE = int(VTE - nulos - no_reg)
    
    if print_debug:
        _maybe_log(f"VTE: {VTE}, VVE: {VVE}, threshold: {threshold}", 'debug', print_debug)
    
    # Aplicar umbral de 3%
    ok = (x / VVE >= threshold) if VVE > 0 else np.zeros_like(x, dtype=bool)
    x_ok = x.copy()
    x_ok[~ok] = 0.0  # Partidos <3% no participan en RP
    
    if print_debug:
        _maybe_log(f"Partidos que pasan 3%: {np.sum(ok)}", 'debug', print_debug)
        _maybe_log(f"Votos elegibles: {np.sum(x_ok)}", 'debug', print_debug)
    
    # Asignación inicial de RP usando LR
    if seed is not None:
        np.random.seed(seed)
    
    if m > 0 and np.sum(x_ok) > 0:
        s_rp_init = asignar_rp_con_metodo(
            votos=x_ok, 
            escanos=m, 
            quota_method=quota_method,
            divisor_method=divisor_method,
            seed=seed
        )
    else:
        s_rp_init = np.zeros_like(ssd)
    
    # Proporción nacional (solo partidos elegibles)
    v_nacional = x_ok / np.sum(x_ok) if np.sum(x_ok) > 0 else np.zeros_like(x_ok)
    
    # Aplicar topes constitucionales
    if apply_caps:
        resultado_topes = aplicar_topes_nacionales(
            s_mr=ssd, s_rp=s_rp_init, v_nacional=v_nacional,
            S=S, max_pp=max_pp, max_seats=max_seats
        )
        s_tot = resultado_topes['s_tot']
        s_rp_final = resultado_topes['s_rp']
        
        # Verificar suma exacta
        if np.sum(s_tot) != S:
            if print_debug:
                _maybe_log(f"Ajustando suma: {np.sum(s_tot)} -> {S}", 'debug', print_debug)
            s_rp_final = s_rp_final.copy()
            s_tot = ssd + s_rp_final
    else:
        # Sin topes: solo ajustar para cumplir S exactamente
        s_tot = ssd + s_rp_init
        delta = int(S - np.sum(s_tot))
        
        if delta != 0:
            ord_idx = np.argsort(-v_nacional)
            if delta > 0:
                # Asignar escaños faltantes por orden de votación
                take = ord_idx[:min(delta, len(ord_idx))]
                s_tot[take] += 1
            else:
                # Quitar escaños sobrantes de RP
                cand = np.where(s_tot - ssd > 0)[0]
                if len(cand) > 0:
                    ord_rp = np.argsort(-(s_tot - ssd)[cand])
                    take = cand[ord_rp[:min(-delta, len(cand))]]
                    s_tot[take] -= 1
        
        s_rp_final = s_tot - ssd
    
    # Preparar matrices de resultados
    seats = np.row_stack([
        ssd.astype(int),  # MR
        s_rp_final.astype(int),  # RP
        s_tot.astype(int)  # Total
    ])
    
    votes = np.row_stack([
        x / VTE if VTE > 0 else np.zeros_like(x),  # Proporción sobre total
        x / VVE if VVE > 0 else np.zeros_like(x),  # Proporción sobre válida
        v_nacional  # Proporción nacional (solo elegibles)
    ])
    
    if print_debug:
        _maybe_log("Resultados finales:", 'debug', print_debug)
        _maybe_log(f"MR: {dict(zip(range(len(ssd)), ssd))}", 'debug', print_debug)
        _maybe_log(f"RP: {dict(zip(range(len(s_rp_final)), s_rp_final))}", 'debug', print_debug)
        _maybe_log(f"Total: {dict(zip(range(len(s_tot)), s_tot))}", 'debug', print_debug)
    
    return {
        'votes': votes,
        'seats': seats,
        'meta': {
            'VTE': VTE,
            'VVE': VVE,
            'ok_3pct': ok,
            'params': {
                'm': m, 'threshold': threshold, 'max_pp': max_pp,
                'max_seats': max_seats, 'S': S, 'seed': seed,
                'apply_caps': apply_caps
            }
        }
    }

# ====================== PROCESADOR PRINCIPAL ======================

def procesar_diputados_v2(path_parquet: Optional[str] = None, 
                          partidos_base: Optional[List[str]] = None,
                          anio: int = 2024, 
                          path_siglado: Optional[str] = None,
                          max_seats: Optional[int] = None, 
                          sistema: str = 'mixto',
                          mr_seats: Optional[int] = None, 
                          rp_seats: Optional[int] = None,
                          regla_electoral: Optional[str] = None,
                          quota_method: str = 'hare',
                          divisor_method: str = 'dhondt',
                          umbral: Optional[float] = None,
                          max_seats_per_party: Optional[int] = None,
                          sobrerrepresentacion: Optional[float] = None,
                          usar_coaliciones: bool = True,
                          votos_redistribuidos: Optional[Dict] = None,
                          seed: Optional[int] = None,
                          print_debug: bool = False) -> Dict:
    """
    Procesador principal de diputados versión 2
    """
    try:
        # Seguridad: evitar comportamiento silencioso con un default no explícito.
        # Requerimos que el caller provea `max_seats` (magnitud total). Si no se
        # proporciona, lanzamos un error claro para evitar que se use un valor
        # por defecto inesperado.
        if max_seats is None:
            raise ValueError("max_seats (magnitud total) no fue provisto. Pase 'escanos_totales' desde el frontend o proporcione 'max_seats' explícitamente al invocar procesar_diputados_v2.")

        if not path_parquet:
            raise ValueError("Debe proporcionar path_parquet")
        
        if not partidos_base:
            partidos_base = parties_for(anio)
        
        if print_debug:
            _maybe_log(f"Procesando diputados {anio} con {len(partidos_base)} partidos", 'debug', print_debug)
        
        # Leer datos
        try:
            df = pd.read_parquet(path_parquet)
        except Exception as e:
            _maybe_log(f"Error leyendo Parquet: {e}", 'warn', print_debug)
            import pyarrow.parquet as pq
            table = pq.read_table(path_parquet)
            df = table.to_pandas()
            # Decodificar bytes a UTF-8 si es necesario
            for col in df.columns:
                if df[col].dtype == object:
                    df[col] = df[col].apply(lambda x: x.decode('utf-8', errors='replace') if isinstance(x, bytes) else x)
        
        # Normalizar columnas
        df.columns = [norm_ascii_up(c) for c in df.columns]
        
        # Normalizar entidades y distritos
        if 'ENTIDAD' in df.columns:
            df['ENTIDAD'] = df['ENTIDAD'].apply(lambda x: x.decode('utf-8', errors='replace') if isinstance(x, bytes) else x)
            df['ENTIDAD'] = df['ENTIDAD'].apply(normalize_entidad_ascii)
        if 'DISTRITO' in df.columns:
            df['DISTRITO'] = pd.to_numeric(df['DISTRITO'], errors='coerce').fillna(0).astype(int)
        
        # NUEVO: Detectar y agregar coaliciones automáticamente
        siglado_path_auto = f"data/siglado-diputados-{anio}.csv"
        coaliciones_detectadas = {}
        if os.path.exists(siglado_path_auto):
            coaliciones_detectadas = extraer_coaliciones_de_siglado(siglado_path_auto, anio)
            if coaliciones_detectadas:
                df = agregar_columnas_coalicion(df, coaliciones_detectadas)
                if print_debug:
                    _maybe_log(f"Dataset con coaliciones shape: {df.shape}", 'debug', print_debug)
                    _maybe_log("Saltando recomposición: ya tenemos coaliciones del siglado", 'debug', print_debug)
            else:
                if print_debug:
                    _maybe_log("No se detectaron coaliciones válidas", 'debug', print_debug)
        else:
            if print_debug:
                _maybe_log(f"No existe archivo siglado: {siglado_path_auto}", 'debug', print_debug)
        
        # Recomposición: siempre usar la recomposición oficial. Si existe el CSV de siglado,
        # usar la regla 'equal_residue_siglado' pasando una versión normalizada del CSV.
        if path_siglado and os.path.exists(path_siglado):
            if print_debug:
                _maybe_log(f"Usando recomposición con siglado: {path_siglado}", 'debug', print_debug)
            # Normalizar siglado para el loader de recomposición
            siglado_df = pd.read_csv(path_siglado, dtype=str, keep_default_na=False)
            # Normalize column names to ASCII lowercase but keep tokens like 'ASCII'
            def _col_norm(c):
                c2 = norm_ascii_up(c)
                c2 = c2.replace(' ', '_')
                return c2.lower()
            siglado_df.columns = [_col_norm(c) for c in siglado_df.columns]
            _sig_path = path_siglado + '.tmp_normalized.csv'
            siglado_df.to_csv(_sig_path, index=False)

            recomposed = recompose_coalitions(
                df=df, year=anio, chamber="diputados",
                rule="equal_residue_siglado", siglado_path=_sig_path
            )

            try:
                os.remove(_sig_path)
            except Exception:
                pass
        else:
            if print_debug:
                _maybe_log("Usando recomposición estándar", 'debug', print_debug)
            recomposed = recompose_coalitions(
                df=df, year=anio, chamber="diputados",
                rule="equal_residue_solo", siglado_path=None
            )
        
        # Extraer votos nacionales (solo votos individuales para RP)
        votos_partido = {p: int(recomposed[p].sum()) if p in recomposed.columns else 0 for p in partidos_base}
        indep = int(recomposed['CI'].sum()) if 'CI' in recomposed.columns else 0
        
        if print_debug:
            _maybe_log(f"Votos por partido (originales): {votos_partido}", 'debug', print_debug)
            _maybe_log(f"Independientes: {indep}", 'debug', print_debug)
        
        # NUEVO: Aplicar redistribución de votos si se proporciona
        if votos_redistribuidos:
            if print_debug:
                _maybe_log(f"Aplicando redistribución de votos: {votos_redistribuidos}", 'debug', print_debug)
            
            # Calcular total de votos válidos (excluyendo independientes)
            total_votos_validos = sum(votos_partido.values())
            
            if total_votos_validos > 0:
                # Aplicar porcentajes redistribuidos
                votos_partido_redistribuidos = {}
                for partido in partidos_base:
                    if partido in votos_redistribuidos:
                        # Usar porcentaje redistribuido
                        nuevo_porcentaje = votos_redistribuidos[partido] / 100.0
                        nuevos_votos = int(total_votos_validos * nuevo_porcentaje)
                        votos_partido_redistribuidos[partido] = nuevos_votos
                    else:
                        # Mantener votos originales para partidos no especificados
                        votos_partido_redistribuidos[partido] = votos_partido[partido]
                
                # Actualizar votos nacionales
                votos_partido = votos_partido_redistribuidos
                
                if print_debug:
                    _maybe_log(f"Votos por partido (redistribuidos): {votos_partido}", 'debug', print_debug)
                    total_redistribuido = sum(votos_partido.values())
                    _maybe_log(f"Total votos después de redistribución: {total_redistribuido}", 'debug', print_debug)
        
    # Calcular MR por distrito considerando coaliciones
        if coaliciones_detectadas and usar_coaliciones:
            if print_debug:
                _maybe_log("Calculando MR con coaliciones y siglado", 'debug', print_debug)
            
            # Cargar siglado para saber qué partido específico gana cada distrito
            siglado_path_auto = f"data/siglado-diputados-{anio}.csv"
            # Usar el loader centralizado que normaliza columnas y claves
            try:
                siglado_df = _load_siglado_dip(siglado_path_auto)
                # _load_siglado_dip devuelve columnas: entidad_key, distrito, coalicion_key, dominante
            except Exception:
                # Fallback robusto si el CSV tiene una estructura distinta
                siglado_df = pd.read_csv(siglado_path_auto, dtype=str, keep_default_na=False)
                siglado_df.columns = [c.strip().lower() for c in siglado_df.columns]
                # Normalizar nombre de entidad a clave homogénea
                if 'entidad_ascii' in siglado_df.columns:
                    siglado_df['entidad_key'] = siglado_df['entidad_ascii'].map(lambda x: norm_ascii_up(str(x)))
                elif 'entidad' in siglado_df.columns:
                    siglado_df['entidad_key'] = siglado_df['entidad'].map(lambda x: norm_ascii_up(str(x)))
                else:
                    siglado_df['entidad_key'] = ''
                # Asegurar columna 'distrito' numérica
                if 'distrito' in siglado_df.columns:
                    siglado_df['distrito'] = siglado_df['distrito'].astype(str).str.extract(r"(\d+)").fillna('0').astype(int)
                else:
                    siglado_df['distrito'] = 0
                # Determinar columna dominante (grupo_parlamentario o partido_origen)
                if 'grupo_parlamentario' in siglado_df.columns:
                    siglado_df['dominante'] = siglado_df['grupo_parlamentario'].map(lambda x: norm_ascii_up(str(x)))
                elif 'partido_origen' in siglado_df.columns:
                    siglado_df['dominante'] = siglado_df['partido_origen'].map(lambda x: norm_ascii_up(str(x)))
                else:
                    siglado_df['dominante'] = ''
            
            # Preparar candidatos: partidos individuales + coaliciones (sumadas por partidos)
            # Evitamos depender de columnas de coalición que pueden no existir tras recomposición.
            candidaturas_partidos = partidos_base
            candidaturas_coaliciones = coaliciones_detectadas if coaliciones_detectadas else {}

            # Construir mapa por distrito desde el siglado: nominadores_set y ppn_gp (grupo parlamentario)
            siglado_map = {}
            try:
                siglado_raw = pd.read_csv(siglado_path_auto, dtype=str, keep_default_na=False)
                siglado_raw.columns = [c.strip().lower() for c in siglado_raw.columns]
                for _, r in siglado_raw.iterrows():
                    # obtener entidad y distrito
                    ent = r.get('entidad_ascii') or r.get('entidad') or ''
                    ent_key_norm = norm_ascii_up(str(ent))
                    ent_key_full = normalize_entidad_ascii(str(ent))
                    try:
                        dist = int(str(r.get('distrito','0')) and re.findall(r"(\d+)", str(r.get('distrito','0')))[0])
                    except Exception:
                        try:
                            dist = int(r.get('distrito', 0))
                        except Exception:
                            dist = 0

                    # obtener nominador (partido que postuló) y grupo parlamentario si existe
                    partido_origen = ''
                    gp = ''
                    # posibles nombres de columna
                    if 'partido_origen' in siglado_raw.columns:
                        partido_origen = r.get('partido_origen','')
                    elif 'partido' in siglado_raw.columns:
                        partido_origen = r.get('partido','')
                    elif 'postulador' in siglado_raw.columns:
                        partido_origen = r.get('postulador','')

                    if 'grupo_parlamentario' in siglado_raw.columns:
                        gp = r.get('grupo_parlamentario','')
                    elif 'grupo' in siglado_raw.columns:
                        gp = r.get('grupo','')

                    partido_origen_norm = norm_ascii_up(str(partido_origen)) if partido_origen else ''
                    gp_norm = norm_ascii_up(str(gp)) if gp else ''

                    for key in [(ent_key_norm, dist), (ent_key_full, dist)]:
                        entry = siglado_map.get(key, {'nominadores': set(), 'ppn_set': set()})
                        if partido_origen_norm:
                            entry['nominadores'].add(partido_origen_norm)
                        if gp_norm:
                            entry['ppn_set'].add(gp_norm)
                        siglado_map[key] = entry

                # finalize map: convert ppn_set to single ppn_gp (or '' if ambiguous)
                for k, v in list(siglado_map.items()):
                    nominadores = set([p for p in v['nominadores'] if p and p.strip()])
                    ppn_vals = set([p for p in v['ppn_set'] if p and p.strip()])
                    ppn_gp = ''
                    if len(ppn_vals) == 1:
                        ppn_gp = list(ppn_vals)[0]
                    elif len(ppn_vals) > 1:
                        _maybe_log(f"Múltiples GRUPO_PARLAMENTARIO para {k}: {ppn_vals}; ignorando ppn_gp", 'warn', print_debug)
                        ppn_gp = ''
                    siglado_map[k] = {'nominadores_set': nominadores, 'ppn_gp': ppn_gp}
            except Exception as e:
                _maybe_log(f"No se pudo construir siglado_map desde {siglado_path_auto}: {e}", 'warn', print_debug)

            # Calcular ganador por distrito
            mr_raw = {}
            distritos_procesados = 0

            # Construir lookup del dataframe original (antes de recomposición) para comprobar columnas de coalición por fila
            df_lookup = None
            try:
                df_lookup = df.set_index(['ENTIDAD', 'DISTRITO'])
            except Exception:
                df_lookup = None

            for _, distrito in recomposed.iterrows():
                entidad = distrito['ENTIDAD']
                num_distrito = distrito['DISTRITO']

                # Construir mapa de votos para candidatos (partidos + coaliciones)
                candidate_votes = {}
                # votos por partido
                for p in candidaturas_partidos:
                    candidate_votes[p] = float(distrito.get(p, 0) or 0.0)

                # votos por coalición = suma de partidos miembros
                for coal_name, miembros in candidaturas_coaliciones.items():
                    s = 0.0
                    for miembro in miembros:
                        # sólo sumar si la columna existe en el recomposed
                        if miembro in distrito:
                            s += float(distrito.get(miembro, 0) or 0.0)
                    candidate_votes[coal_name] = s

                # Determinar ganador (nombre de partido o coalición)
                coalicion_ganadora = max(candidate_votes, key=lambda k: candidate_votes.get(k, 0))
                max_votos = candidate_votes.get(coalicion_ganadora, 0)

                # Si el ganador es una coalición, confirmemos que la columna de coalición
                # realmente existía en el parquet para este distrito (y tenía votos).
                is_coalition_win = False
                if coalicion_ganadora in candidaturas_coaliciones:
                    # la clave de coalición en candidaturas_coaliciones coincide con el nombre creado por agregar_columnas_coalicion
                    # Comprobar en df_lookup si esa columna existe y tiene valor >0
                    if df_lookup is not None:
                        try:
                            val = df_lookup.at[(entidad, int(num_distrito)), coalicion_ganadora]
                            if float(val or 0) > 0:
                                is_coalition_win = True
                        except Exception:
                            is_coalition_win = False
                    else:
                        # Si no hay lookup, conservamos la interpretación original (coincidiendo por suma)
                        is_coalition_win = True
                
                distrito_procesado = False
                
                if coalicion_ganadora:
                    # DEBUG: Verificar variables en scope
                    if print_debug and entidad == "AGUASCALIENTES" and num_distrito == 1:
                        _maybe_log(f"coalicion_ganadora: {coalicion_ganadora}", 'debug', print_debug)
                        _maybe_log(f"coaliciones_detectadas keys: {list(coaliciones_detectadas.keys()) if coaliciones_detectadas else 'None'}", 'debug', print_debug)
                        _maybe_log(f"coalicion_ganadora in coaliciones_detectadas: {coalicion_ganadora in coaliciones_detectadas if coaliciones_detectadas else 'coaliciones_detectadas is None'}", 'debug', print_debug)
                    
                    # Si ganó una coalición (y efectivamente es una coalición en el parquet), decidir si usar siglado o fallback según nominadores
                    if is_coalition_win and coalicion_ganadora in coaliciones_detectadas:
                        # Obtener lista de partidos que componen la coalición (ej. ['MORENA','PT','PVEM'])
                        partidos_coalicion = [norm_ascii_up(str(p)) for p in coaliciones_detectadas.get(coalicion_ganadora, [])]

                        # Obtener nominadores y ppn_gp desde el mapa por distrito (si existe)
                        ent_key_norm = norm_ascii_up(entidad)
                        ent_key_full = normalize_entidad_ascii(entidad)
                        distrito_info = siglado_map.get((ent_key_norm, int(num_distrito))) or siglado_map.get((ent_key_full, int(num_distrito))) or {'nominadores_set': set(), 'ppn_gp': ''}
                        nominadores_set = distrito_info.get('nominadores_set', set())
                        ppn_gp = distrito_info.get('ppn_gp', '')

                        # Sanity checks
                        if nominadores_set and len(nominadores_set) not in (1,3):
                            _maybe_log(f"Distrito {entidad}-{num_distrito}: nominadores_set inesperado {nominadores_set}", 'warn', print_debug)
                        if (set(partidos_coalicion) == {"MORENA","PT","PVEM"} or set(partidos_coalicion) == {"PAN","PRI","PRD"}) and not ppn_gp:
                            _maybe_log(f"Distrito {entidad}-{num_distrito}: coalición detectada pero ppn_gp ausente", 'warn', print_debug)

                        # Reglas jurídicas (prioridad):
                        SHH = {"MORENA","PT","PVEM"}
                        FCM = {"PAN","PRI","PRD"}

                        # 1) Si nominadores coinciden exactamente con SHH y ganó la coalición SHH -> acreditar ppn_gp
                        if nominadores_set == SHH and set(partidos_coalicion) == SHH and coalicion_ganadora in coaliciones_detectadas:
                            if ppn_gp:
                                if ppn_gp in partidos_base:
                                    mr_raw[ppn_gp] = mr_raw.get(ppn_gp, 0) + 1
                                    distrito_procesado = True
                                    if print_debug:
                                        _maybe_log(f"{entidad}-{num_distrito}: SHH ganó -> acreditar a {ppn_gp}", 'info', print_debug)
                                else:
                                    # ppn_gp no corresponde a partido base: fallback por votos
                                    pass

                        # 2) Si nominadores coinciden exactamente con FCM y ganó la coalición FCM -> acreditar ppn_gp
                        if not distrito_procesado and nominadores_set == FCM and set(partidos_coalicion) == FCM and coalicion_ganadora in coaliciones_detectadas:
                            if ppn_gp:
                                if ppn_gp in partidos_base:
                                    mr_raw[ppn_gp] = mr_raw.get(ppn_gp, 0) + 1
                                    distrito_procesado = True
                                    if print_debug:
                                        _maybe_log(f"{entidad}-{num_distrito}: FCM ganó -> acreditar a {ppn_gp}", 'info', print_debug)

                        # 3) Si solo hay un nominador y ganó ese partido -> acreditar a ese partido
                        if not distrito_procesado and len(nominadores_set) == 1:
                            solo = list(nominadores_set)[0]
                            if coalicion_ganadora == solo or (solo in partidos_base and coalicion_ganadora == solo):
                                if solo in partidos_base:
                                    mr_raw[solo] = mr_raw.get(solo, 0) + 1
                                    distrito_procesado = True
                                    if print_debug:
                                        _maybe_log(f"{entidad}-{num_distrito}: único nominador {solo} y ganó -> acreditar a {solo}", 'info', print_debug)

                        # 4) En otros casos, solo acreditar ppn_gp si la coalición ganó y ppn_gp pertenece a la coalición
                        if not distrito_procesado:
                            # Si partido ganador proviene de la coalición, asignar al dominante si pertenece a la coalición
                            # buscar filas de siglado para este distrito
                            mask = (siglado_df.get('entidad_key', '') == normalize_entidad_ascii(entidad)) & (siglado_df['distrito'] == num_distrito)
                            if 'coalicion_key' in siglado_df.columns:
                                coalicion_lookup = norm_ascii_up(coalicion_ganadora).replace('_', ' ')
                                mask = mask & (siglado_df['coalicion_key'] == coalicion_lookup)
                            distrito_siglado = siglado_df[mask]

                            if len(distrito_siglado) > 0:
                                partido_ganador = distrito_siglado['dominante'].iloc[0]
                                partido_ganador = norm_ascii_up(str(partido_ganador))
                                # Solo acreditar ppn_gp si ganador es la coalición y ppn_gp pertenece a la coalición
                                if partido_ganador in partidos_coalicion and partido_ganador in partidos_base:
                                    mr_raw[partido_ganador] = mr_raw.get(partido_ganador, 0) + 1
                                    distrito_procesado = True
                                    if print_debug:
                                        _maybe_log(f"{entidad}-{num_distrito}: acreditar a dominante {partido_ganador}", 'warn', print_debug)

                            # Si no hay registro en siglado o no aplica, usar fallback por votos dentro de la coalición
                            if not distrito_procesado:
                                partidos_coalicion_list = partidos_de_col(coalicion_ganadora)
                                votos_coalicion = {p: float(distrito.get(p,0) or 0) for p in partidos_coalicion_list if p in partidos_base}
                                if votos_coalicion:
                                    partido_fallback = max(votos_coalicion, key=votos_coalicion.get)
                                    mr_raw[partido_fallback] = mr_raw.get(partido_fallback, 0) + 1
                                    distrito_procesado = True
                                    if print_debug:
                                        _maybe_log(f"Distrito {entidad}-{num_distrito}: {coalicion_ganadora} -> {partido_fallback} (por votos coalición)", 'warn', print_debug)
                    elif not is_coalition_win:
                        # Aunque la suma ponderada sugiera una coalición, la columna de coalición
                        # no existía o no tenía votos en el parquet: tratar como partido individual
                        if coalicion_ganadora in partidos_base:
                            mr_raw[coalicion_ganadora] = mr_raw.get(coalicion_ganadora, 0) + 1
                            distrito_procesado = True
                            if print_debug and len(mr_raw) <= 5:
                                _maybe_log(f"Distrito {entidad}-{num_distrito}: {coalicion_ganadora} (individual, sin columna de coalición)", 'debug', print_debug)
                        else:
                            # Fallback conservador: asignar al partido con más votos entre partidos base
                            votos_ind = {p: float(distrito.get(p,0) or 0) for p in partidos_base}
                            if votos_ind:
                                ganador_ind = max(votos_ind, key=votos_ind.get)
                                mr_raw[ganador_ind] = mr_raw.get(ganador_ind, 0) + 1
                                distrito_procesado = True
                                if print_debug:
                                    _maybe_log(f"Distrito {entidad}-{num_distrito}: {ganador_ind} (fallback sin columna de coalición)", 'debug', print_debug)
                    else:
                        # Partido individual ganó directamente
                        if coalicion_ganadora in partidos_base:
                            mr_raw[coalicion_ganadora] = mr_raw.get(coalicion_ganadora, 0) + 1
                            distrito_procesado = True
                            if print_debug and len(mr_raw) <= 5:
                                _maybe_log(f"Distrito {entidad}-{num_distrito}: {coalicion_ganadora} (individual)", 'debug', print_debug)
                
                # GARANTÍA: Si el distrito aún no se procesó, usar VOTOS DIRECTOS del parquet
                if not distrito_procesado:
                    # Calcular ganador entre partidos individuales del parquet
                    votos_individuales = {}
                    for p in partidos_base:
                        if p in distrito:
                            votos_individuales[p] = distrito.get(p, 0)
                    
                    if votos_individuales:
                        ganador_individual = max(votos_individuales, key=votos_individuales.get)
                        mr_raw[ganador_individual] = mr_raw.get(ganador_individual, 0) + 1
                        distrito_procesado = True
                        if print_debug:
                            _maybe_log(f"Distrito {entidad}-{num_distrito}: {ganador_individual} (ganador directo por votos parquet)", 'info', print_debug)
                
                if distrito_procesado:
                    distritos_procesados += 1
            
            if print_debug:
                _maybe_log(f"Total distritos procesados para MR: {distritos_procesados}/300", 'debug', print_debug)
            
            mr_aligned = {p: int(mr_raw.get(p, 0)) for p in partidos_base}
            indep_mr = 0
        else:
            # Usar método tradicional sin coaliciones (partido individual con más votos gana)
            if print_debug:
                if coaliciones_detectadas and not usar_coaliciones:
                    _maybe_log("Coaliciones detectadas pero DESACTIVADAS por parámetro", 'debug', print_debug)
                _maybe_log("Calculando MR por partido individual (sin coaliciones)", 'debug', print_debug)
            
            from .core import mr_by_siglado
            try:
                mr, indep_mr = mr_by_siglado(
                    winners_df=recomposed,
                    group_keys=["ENTIDAD", "DISTRITO"],
                    gp_col="MR_DOMINANTE" if "MR_DOMINANTE" in recomposed.columns else "DOMINANTE",
                    parties=partidos_base
                )
                mr_aligned = {p: int(mr.get(p, 0)) for p in partidos_base}
            except Exception as e:
                if print_debug:
                    _maybe_log(f"Error en mr_by_siglado: {e}", 'warn', print_debug)
                # Fallback: ganador por votos
                ganadores = recomposed.groupby(['ENTIDAD', 'DISTRITO'])[partidos_base].sum().idxmax(axis=1)
                mr = ganadores.value_counts().to_dict()
                mr_aligned = {p: int(mr.get(p, 0)) for p in partidos_base}
                indep_mr = mr.get('CI', 0)
        
    # Configurar parámetros
        if umbral is None:
            umbral = 0.03
        if umbral >= 1:
            umbral = umbral / 100.0
        
        # Determinar configuración según sistema y parámetros específicos
        sistema_tipo = sistema.lower() if sistema else 'mixto'
        
        if print_debug:
            _maybe_log(f"Parámetros recibidos: sistema={sistema}, mr_seats={mr_seats}, rp_seats={rp_seats}, max_seats={max_seats}", 'debug', print_debug)
        
        if sistema_tipo == 'mr':
            # Solo MR, sin RP
            m = 0
            S = max_seats
            # Mantener MR calculado del siglado
            # Si la magnitud solicitada difiere del total de distritos originales,
            # escalamos el siglado para que sea determinístico y estratificado.
            total_distritos_base = sum([mr_aligned.get(p, 0) for p in partidos_base])
            if total_distritos_base != S:
                try:
                    # Preparar df de recomposed con las columnas necesarias
                    df_siglado_like = recomposed.copy()
                    # Asegurar columnas ENTIDAD, DISTRITO y dominantes
                    if 'ENTIDAD' not in df_siglado_like.columns:
                        df_siglado_like['ENTIDAD'] = df_siglado_like.get('entidad', '')
                    if 'DISTRITO' not in df_siglado_like.columns:
                        df_siglado_like['DISTRITO'] = df_siglado_like.get('distrito', 0)

                    scaled = scale_siglado(
                        df=df_siglado_like,
                        M_target=S,
                        partidos_base=partidos_base,
                        strata='ENTIDAD',
                        weight_var=None,
                        seed=seed or 123
                    )

                    # Reconstruir mr_aligned a partir del scaled siglado
                    mr_count = scaled.groupby('sigla').size().to_dict()
                    # Normalizar claves y asegurar presencia de todos los partidos
                    mr_aligned = {p: int(mr_count.get(p, 0)) for p in partidos_base}

                    # Añadir info de scaled al meta para trazabilidad
                    # Híbrido: persistir CSV en outputs/ para auditoría (archivo) y
                    # mantener un resumen pequeño inline en meta para trazabilidad.
                    try:
                        # Determinar si se debe persistir el CSV a disco (por defecto ON)
                        use_persist = os.environ.get('SCALED_SIGLADO_PERSIST', '1')
                        use_persist = str(use_persist).strip() not in ('0', 'false', 'False', '')
                        from datetime import datetime
                        import uuid
                        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                        out_dir = 'outputs'
                        scaled_csv_path = None
                        if use_persist:
                            os.makedirs(out_dir, exist_ok=True)
                            filename = f'scaled_siglado.{ts}.{uuid.uuid4().hex[:8]}.csv'
                            out_path = os.path.join(out_dir, filename)
                            # Escribir CSV en disco de forma segura
                            scaled.to_csv(out_path, index=False)
                            scaled_csv_path = out_path
                    except Exception as _e:
                        # En caso de fallo al escribir, mantener el CSV en memoria
                        if print_debug:
                            _maybe_log(f"No se pudo escribir scaled CSV a disco: {_e}", 'warn', print_debug)
                        scaled_csv_path = None

                    scaled_info = {
                        'total_base': int(total_distritos_base),
                        'total_target': int(S),
                        'by_party': mr_aligned,
                        'by_entidad': scaled.groupby('ENTIDAD').size().to_dict(),
                        'virtual_count': int(scaled['virtual'].sum()),
                        # Path al CSV persistido (si se pudo escribir). Si es None,
                        # se mantiene el CSV inline en 'scaled_csv' para compatibilidad.
                        'scaled_csv_path': scaled_csv_path,
                        'scaled_csv': None if scaled_csv_path is not None else scaled.to_csv(index=False),
                        'provenance': {
                            'method': 'scale_siglado',
                            'seed': int(seed or 123),
                            'strata': 'ENTIDAD'
                        }
                    }
                except Exception as e:
                    if print_debug:
                        _maybe_log(f"scale_siglado fallo: {e}", 'warn', print_debug)
                    scaled_info = {'error': str(e)}
            # Validación: no tiene sentido pedir una magnitud total menor
            # que la cantidad de distritos (MR) ya ganados. Si el caller
            # pidió una magnitud menor, lanzamos un error claro para que
            # el frontend no reciba resultados inconsistentes.
            total_mr_actual = sum(mr_aligned.values())
            if S is not None and S < total_mr_actual:
                raise ValueError(f"max_seats ({S}) es menor que la suma de MR ({total_mr_actual}). No se puede asignar menos escaños totales que distritos MR existentes.")
        elif sistema_tipo == 'rp':
            # Solo RP, sin MR (Plan A)
            m = max_seats
            S = max_seats
            mr_aligned = {p: 0 for p in partidos_base}  # FORZAR MR=0 para Plan A
            if print_debug:
                _maybe_log(f"Plan A detectado: forzando MR=0 para todos los partidos", 'debug', print_debug)
            # Preparar datos y llamar a asignadip_v2 igual que en la rama mixto,
            # para generar rp/tot y poblar resultado cuando el sistema es RP puro.
            # Determinar qué partidos pasan el umbral sobre votos válidos
            total_votos_validos = sum(votos_partido.values())
            if total_votos_validos > 0:
                ok_dict = {p: (votos_partido.get(p, 0) / total_votos_validos) >= umbral for p in partidos_base}
            else:
                ok_dict = {p: False for p in partidos_base}

            # votos_ok: votos contables para RP (0 si no pasan umbral)
            votos_ok = {p: int(votos_partido.get(p, 0)) if ok_dict.get(p, False) else 0 for p in partidos_base}

            # Preparar arrays para asignadip_v2
            x_array = np.array([votos_partido.get(p, 0) for p in partidos_base], dtype=float)
            ssd_array = np.array([mr_aligned.get(p, 0) for p in partidos_base], dtype=int)

            try:
                if print_debug:
                    try:
                        _maybe_log(f"[RP] partidos_base sample: {partidos_base[:10]}", 'debug', print_debug)
                        _maybe_log(f"[RP] x_array dtype={x_array.dtype}, sample={x_array[:10]}", 'debug', print_debug)
                        _maybe_log(f"[RP] ssd_array dtype={ssd_array.dtype}, sample={ssd_array[:10]}", 'debug', print_debug)
                    except Exception:
                        pass

                resultado = asignadip_v2(
                    x=x_array,
                    ssd=ssd_array,
                    indep=int(indep) if indep is not None else 0,
                    nulos=0,
                    no_reg=0,
                    m=int(m) if m is not None else 0,
                    S=int(S) if S is not None else None,
                    threshold=umbral,
                    max_seats=int(max_seats) if max_seats is not None else 300,
                    max_pp=(sobrerrepresentacion / 100.0) if sobrerrepresentacion is not None else 0.08,
                    apply_caps=True,
                    quota_method=quota_method,
                    divisor_method=divisor_method,
                    seed=seed,
                    print_debug=print_debug
                )
            except Exception as e:
                if print_debug:
                    _maybe_log(f"asignadip_v2 falló en RP: {e}", 'error', print_debug)
                resultado = {
                    'votes': None,
                    'seats': np.zeros((3, len(partidos_base)), dtype=int),
                    'meta': {}
                }

            # Extraer MR/RP/Totales del resultado y poblar diccionarios
            seats = resultado.get('seats')
            if seats is None:
                seats = np.zeros((3, len(partidos_base)), dtype=int)

            mr_row = seats[0] if seats.shape[0] > 0 else np.zeros(len(partidos_base), dtype=int)
            rp_row = seats[1] if seats.shape[0] > 1 else np.zeros(len(partidos_base), dtype=int)
            tot_row = seats[2] if seats.shape[0] > 2 else np.zeros(len(partidos_base), dtype=int)

            mr_dict = {partidos_base[i]: int(mr_row[i]) for i in range(len(partidos_base))}
            rp_dict = {partidos_base[i]: int(rp_row[i]) for i in range(len(partidos_base))}
            tot_dict = {partidos_base[i]: int(tot_row[i]) for i in range(len(partidos_base))}
        else:  # sistema_tipo == 'mixto'
            if mr_seats is not None and rp_seats is not None:
                # Plan C o similar: parámetros explícitos para MR y RP
                if print_debug:
                    _maybe_log(f"Plan con parámetros explícitos: MR={mr_seats}, RP={rp_seats}", 'debug', print_debug)
                # Ajustar MR calculado para que sume exactamente mr_seats
                total_mr_actual = sum(mr_aligned.values())
                if total_mr_actual != mr_seats:
                    if print_debug:
                        _maybe_log(f"Ajustando MR de {total_mr_actual} a {mr_seats}", 'debug', print_debug)
                    # Intentar escalado estratificado determinista usando scale_siglado
                    if total_mr_actual > 0:
                        try:
                            df_siglado_like = recomposed.copy()
                            if 'ENTIDAD' not in df_siglado_like.columns:
                                df_siglado_like['ENTIDAD'] = df_siglado_like.get('entidad', '')
                            if 'DISTRITO' not in df_siglado_like.columns:
                                df_siglado_like['DISTRITO'] = df_siglado_like.get('distrito', 0)

                            scaled = scale_siglado(
                                df=df_siglado_like,
                                M_target=mr_seats,
                                partidos_base=partidos_base,
                                strata='ENTIDAD',
                                weight_var=None,
                                seed=seed or 123
                            )

                            mr_count = scaled.groupby('sigla').size().to_dict()
                            mr_ajustado = {p: int(mr_count.get(p, 0)) for p in partidos_base}

                            # Híbrido: persistir CSV y dejar resumen inline
                            try:
                                # Determinar si se debe persistir el CSV a disco (por defecto ON)
                                use_persist = os.environ.get('SCALED_SIGLADO_PERSIST', '1')
                                use_persist = str(use_persist).strip() not in ('0', 'false', 'False', '')
                                from datetime import datetime
                                import uuid
                                ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                                out_dir = 'outputs'
                                scaled_csv_path = None
                                if use_persist:
                                    os.makedirs(out_dir, exist_ok=True)
                                    filename = f'scaled_siglado.{ts}.{uuid.uuid4().hex[:8]}.csv'
                                    out_path = os.path.join(out_dir, filename)
                                    scaled.to_csv(out_path, index=False)
                                    scaled_csv_path = out_path
                            except Exception as _e:
                                if print_debug:
                                    _maybe_log(f"No se pudo escribir scaled CSV a disco (mixto): {_e}", 'warn', print_debug)
                                scaled_csv_path = None

                            scaled_info = {
                                'total_base': int(total_mr_actual),
                                'total_target': int(mr_seats),
                                'by_party': mr_ajustado,
                                'by_entidad': scaled.groupby('ENTIDAD').size().to_dict(),
                                'virtual_count': int(scaled['virtual'].sum()),
                                'scaled_csv_path': scaled_csv_path,
                                'scaled_csv': None if scaled_csv_path is not None else scaled.to_csv(index=False),
                                'provenance': {
                                    'method': 'scale_siglado',
                                    'seed': int(seed or 123),
                                    'strata': 'ENTIDAD'
                                }
                            }
                            mr_aligned = mr_ajustado
                        except Exception as e:
                            if print_debug:
                                _maybe_log(f"scale_siglado (mixto) fallo: {e}, cayendo a reescalado proporcional", 'warn', print_debug)
                            # Fallback proporcional
                            factor = mr_seats / total_mr_actual if total_mr_actual > 0 else 0
                            mr_ajustado = {p: int(round(mr_aligned.get(p, 0) * factor)) for p in partidos_base}
                            diferencia = mr_seats - sum(mr_ajustado.values())
                            if diferencia != 0:
                                partidos_ordenados = sorted(partidos_base, key=lambda x: mr_ajustado[x], reverse=True)
                                for i in range(abs(diferencia)):
                                    if diferencia > 0:
                                        mr_ajustado[partidos_ordenados[i % len(partidos_ordenados)]] += 1
                                    else:
                                        if mr_ajustado[partidos_ordenados[i % len(partidos_ordenados)]] > 0:
                                            mr_ajustado[partidos_ordenados[i % len(partidos_ordenados)]] -= 1
                            mr_aligned = mr_ajustado
                    else:
                        # Si no hay MR calculado, distribuir usando largest remainder
                        votos_array = np.array([votos_partido.get(p, 0) for p in partidos_base])
                        mr_dist = LR_ties(votos_array, mr_seats)
                        mr_aligned = {partidos_base[i]: int(mr_dist[i]) for i in range(len(partidos_base))}
                
                m = rp_seats
                S = max_seats
            elif mr_seats == 0:
                # Plan A explícito
                if print_debug:
                    _maybe_log(f"Plan A explícito (mr_seats=0)", 'debug', print_debug)
                m = max_seats
                S = max_seats
                mr_aligned = {p: 0 for p in partidos_base}
            elif rp_seats is not None:
                # Plan vigente: MR libre + RP fijo (caso especial)
                if print_debug:
                    _maybe_log(f"Plan vigente detectado: MR libre + RP fijo = {rp_seats}", 'debug', print_debug)
                total_mr = sum(mr_aligned.values())
                m = rp_seats  # Usar RP fijo, no calculado
                S = max_seats
            else:
                # Sistema vigente tradicional (usar MR calculado)
                # Nada especial que hacer aquí; se usa mr_aligned calculado
                pass
            
            # Preparar datos y llamar a asignadip_v2 para obtener mr/rp/totales
            # Asegurar valor por defecto de sobrerrepresentacion (en %)
            # Defensive: asegurar que 'm' (RP seats) y 'S' (total seats) estén definidos
            # en todos los caminos de control. Evita UnboundLocalError y calcula
            # RP cuando sólo se proporciona mr_seats.
            if ('m' not in locals()) or (m is None):
                try:
                    if mr_seats is not None and rp_seats is None and max_seats is not None:
                        # Si el caller dio mr_seats pero no rp_seats, RP = max_seats - mr_seats
                        m = int(max_seats) - int(mr_seats)
                    elif rp_seats is not None:
                        m = int(rp_seats)
                    elif 'mr_aligned' in locals() and max_seats is not None:
                        # Calcular RP como diferencia entre total y MR calculado
                        m = int(max_seats) - int(sum(int(v) for v in mr_aligned.values()))
                    else:
                        # Fallback conservador: asignar todos los escaños a RP
                        m = int(max_seats) if max_seats is not None else 0
                except Exception:
                    m = int(max_seats) if max_seats is not None else 0

            if ('S' not in locals()) or (S is None):
                S = int(max_seats) if max_seats is not None else None

            # Asegurar m no negativo
            try:
                m = max(0, int(m))
            except Exception:
                m = 0
            if sobrerrepresentacion is None:
                sobrerrepresentacion = 8.0

            # Determinar qué partidos pasan el umbral sobre votos válidos
            total_votos_validos = sum(votos_partido.values())
            if total_votos_validos > 0:
                ok_dict = {p: (votos_partido.get(p, 0) / total_votos_validos) >= umbral for p in partidos_base}
            else:
                ok_dict = {p: False for p in partidos_base}

            # votos_ok: votos contables para RP (0 si no pasan umbral)
            votos_ok = {p: int(votos_partido.get(p, 0)) if ok_dict.get(p, False) else 0 for p in partidos_base}

            # Preparar arrays para asignadip_v2
            x_array = np.array([votos_partido.get(p, 0) for p in partidos_base], dtype=float)
            ssd_array = np.array([mr_aligned.get(p, 0) for p in partidos_base], dtype=int)

            # Llamar al motor de asignación (asignadip_v2)
            try:
                # Debug: verificar tipos/valores antes de llamar a asignadip_v2
                if print_debug:
                    try:
                        _maybe_log(f"partidos_base sample: {partidos_base[:10]}", 'debug', print_debug)
                        _maybe_log(f"mr_aligned sample: {{k: mr_aligned[k] for k in list(mr_aligned.keys())[:10]}}", 'debug', print_debug)
                        _maybe_log(f"x_array dtype={x_array.dtype}, sample={x_array[:10]}", 'debug', print_debug)
                        _maybe_log(f"ssd_array dtype={ssd_array.dtype}, sample={ssd_array[:10]}", 'debug', print_debug)
                    except Exception as _e:
                        _maybe_log(f"error printing debug samples: {_e}", 'warn', print_debug)

                resultado = asignadip_v2(
                    x=x_array,
                    ssd=ssd_array,
                    indep=int(indep) if indep is not None else 0,
                    nulos=0,
                    no_reg=0,
                    m=int(m) if m is not None else 0,
                    S=int(S) if S is not None else None,
                    threshold=umbral,
                    max_seats=int(max_seats) if max_seats is not None else 300,
                    max_pp=(sobrerrepresentacion / 100.0) if sobrerrepresentacion is not None else 0.08,
                    apply_caps=True,
                    quota_method=quota_method,
                    divisor_method=divisor_method,
                    seed=seed,
                    print_debug=print_debug
                )
            except Exception as e:
                # En caso de fallo, retornar estado conservador
                if print_debug:
                    _maybe_log(f"asignadip_v2 falló: {e}", 'error', print_debug)
                    import traceback
                    traceback.print_exc()
                resultado = {
                    'votes': None,
                    'seats': np.zeros((3, len(partidos_base)), dtype=int),
                    'meta': {}
                }

            # Extraer MR/RP/Totales del resultado
            seats = resultado.get('seats')
            if seats is None:
                seats = np.zeros((3, len(partidos_base)), dtype=int)

            mr_row = seats[0] if seats.shape[0] > 0 else np.zeros(len(partidos_base), dtype=int)
            rp_row = seats[1] if seats.shape[0] > 1 else np.zeros(len(partidos_base), dtype=int)
            tot_row = seats[2] if seats.shape[0] > 2 else np.zeros(len(partidos_base), dtype=int)

            mr_dict = {partidos_base[i]: int(mr_row[i]) for i in range(len(partidos_base))}
            rp_dict = {partidos_base[i]: int(rp_row[i]) for i in range(len(partidos_base))}
            tot_dict = {partidos_base[i]: int(tot_row[i]) for i in range(len(partidos_base))}

            if print_debug:
                _maybe_log(f"mr: {mr_dict}", 'debug', print_debug)
                _maybe_log(f"rp: {rp_dict}", 'debug', print_debug)
                _maybe_log(f"tot: {tot_dict}", 'debug', print_debug)

            # Ahora continuar con la aplicación de límites de sobrerrepresentación
            total_votos_validos = sum(votos_ok.values())
            if total_votos_validos > 0:
                # Convertir a arrays para apply_overrep_cap
                # Crear arrays en el mismo orden que partidos_base
                seats_array = np.array([tot_dict[p] for p in partidos_base])
                votes_array = np.array([votos_ok[p] for p in partidos_base])

                # Calcular vote_share_valid 
                vote_share_valid = votes_array / total_votos_validos

                # Aplicar límite (convertir de porcentaje a fracción)
                over_cap = sobrerrepresentacion / 100.0

                if print_debug:
                    _maybe_log(f"over_cap = {over_cap} ({sobrerrepresentacion}%)", 'debug', print_debug)
                    _maybe_log(f"total_escanos = {max_seats}", 'debug', print_debug)
                    _maybe_log(f"vote_share_valid = {vote_share_valid}", 'debug', print_debug)

                # Aplicar límite de sobrerrepresentación
                seats_ajustados = apply_overrep_cap(
                    seats=seats_array,
                    vote_share_valid=vote_share_valid,
                    S=max_seats,
                    over_cap=over_cap
                )

                # Convertir de vuelta a diccionario
                tot_dict_ajustado = {partidos_base[i]: int(seats_ajustados[i]) for i in range(len(partidos_base))}

                # Verificar si hubo cambios y aplicarlos
                if tot_dict_ajustado != tot_dict:
                    for p in partidos_base:
                        if tot_dict_ajustado[p] != tot_dict[p]:
                            if print_debug:
                                _maybe_log(f"{p}: {tot_dict[p]} -> {tot_dict_ajustado[p]} escaños (límite sobrerrepresentación)", 'debug', print_debug)
                            tot_dict[p] = tot_dict_ajustado[p]
                            # Recalcular RP = total - MR
                            rp_dict[p] = max(0, tot_dict[p] - mr_dict[p])

                if print_debug:
                    _maybe_log(f"Escaños después de sobrerrepresentación: {tot_dict}", 'debug', print_debug)
        
        # Si existe `scaled` pero por alguna razón no se construyó `scaled_info`,
        # crear un scaled_info mínimo y persistir el CSV si es posible. Esto
        # cubre rutas en las que el escalado falló parcialmente después de
        # generar `scaled` pero antes de poblar la metadata.
        try:
            if 'scaled' in locals() and (('scaled_info' not in locals()) or scaled_info is None):
                try:
                    use_persist = os.environ.get('SCALED_SIGLADO_PERSIST', '1')
                    use_persist = str(use_persist).strip() not in ('0', 'false', 'False', '')
                    from datetime import datetime
                    import uuid
                    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                    scaled_csv_path = None
                    if use_persist:
                        out_dir = 'outputs'
                        os.makedirs(out_dir, exist_ok=True)
                        filename = f'scaled_siglado.{ts}.{uuid.uuid4().hex[:8]}.csv'
                        out_path = os.path.join(out_dir, filename)
                        scaled.to_csv(out_path, index=False)
                        scaled_csv_path = out_path
                except Exception as _e:
                    scaled_csv_path = None

                try:
                    by_party = scaled.groupby('sigla').size().to_dict() if 'sigla' in scaled.columns else {}
                    by_entidad = scaled.groupby('ENTIDAD').size().to_dict() if 'ENTIDAD' in scaled.columns else {}
                    virtual_count = int(scaled['virtual'].sum()) if 'virtual' in scaled.columns else 0
                except Exception:
                    by_party = {}
                    by_entidad = {}
                    virtual_count = 0

                scaled_info = {
                    'total_base': int(scaled.shape[0]) if hasattr(scaled, 'shape') else None,
                    'total_target': None,
                    'by_party': by_party,
                    'by_entidad': by_entidad,
                    'virtual_count': int(virtual_count),
                    'scaled_csv_path': scaled_csv_path,
                    'scaled_csv': None if scaled_csv_path is not None else (scaled.to_csv(index=False) if hasattr(scaled, 'to_csv') else None),
                    'provenance': {
                        'method': 'scale_siglado',
                        'seed': int(seed or 123) if 'seed' in locals() else None,
                        'strata': 'ENTIDAD'
                    }
                }
        except Exception:
            # Si cualquier cosa falla aquí, no queremos romper el retorno principal
            pass

        # Asegurar que 'resultado' exista (en ramas MR-only no se llamó a asignadip_v2)
        if 'resultado' not in locals():
            # resultado mínimo para permitir devolver meta y scaled_info
            resultado = {'meta': {}}

        # Si existió scaled_info (por escalado MR), añadirlo a la metadata para trazabilidad
        meta_out = resultado['meta'].copy() if isinstance(resultado.get('meta'), dict) else {}

        # Asegurar que los diccionarios de salida existan (caso MR-only u otras ramas)
        if 'mr_dict' not in locals():
            try:
                mr_dict = {p: int(mr_aligned.get(p, 0)) for p in partidos_base}
            except Exception:
                mr_dict = {p: 0 for p in partidos_base}
        if 'rp_dict' not in locals():
            rp_dict = {p: 0 for p in partidos_base}
        if 'tot_dict' not in locals():
            try:
                tot_dict = {p: int(mr_dict.get(p, 0) + rp_dict.get(p, 0)) for p in partidos_base}
            except Exception:
                tot_dict = {p: 0 for p in partidos_base}
        # Asegurar valores por defecto para ok/votos si no fueron calculados
        if 'ok_dict' not in locals():
            ok_dict = {p: False for p in partidos_base}
        if 'votos_partido' not in locals():
            votos_partido = {p: 0 for p in partidos_base}
        if 'votos_ok' not in locals():
            votos_ok = {p: 0 for p in partidos_base}
        try:
            if 'scaled_info' in locals() and scaled_info is not None:
                meta_out['scaled_info'] = scaled_info
        except Exception:
            pass

        return {
            'mr': mr_dict,
            'rp': rp_dict,
            'tot': tot_dict,
            'ok': ok_dict,
            'votos': votos_partido,
            'votos_ok': votos_ok,
            'meta': meta_out
        }
        
    except Exception as e:
        _maybe_log(f"procesar_diputados_v2: {e}", 'error', print_debug)
        if print_debug:
            import traceback
            traceback.print_exc()
        
        # Retornar resultado vacío en caso de error
        partidos = partidos_base if partidos_base else []
        return {
            'mr': {p: 0 for p in partidos},
            'rp': {p: 0 for p in partidos},
            'tot': {p: 0 for p in partidos},
            'ok': {p: False for p in partidos},
            'votos': {p: 0 for p in partidos},
            'votos_ok': {p: 0 for p in partidos},
            'meta': {}
        }


def export_scenarios(path_parquet: str, siglado_path: str, scenarios: list, out_path: str = None, anio: int = 2024, print_debug: bool = False):
    """Ejecuta una serie de escenarios y exporta un Excel con pestañas por escenario.

    scenarios: list de tuplas (name, params_dict) como en tmp_export_escenarios.py
    Cada params_dict puede contener: max_seats, sistema, mr_seats, rp_seats, usar_pm (bool), pm_seats
    """
    import pandas as pd
    import os

    if out_path is None:
        from datetime import datetime
        out_path = f"outputs/escenarios_diputados_custom.{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    with pd.ExcelWriter(out_path) as writer:
        for name, params in scenarios:
            if print_debug:
                _maybe_log(f"ejecutando {name} {params}", 'info', print_debug)
            # copy params to avoid mutation
            p = dict(params)
            usar_pm = p.pop('usar_pm', False)

            res = procesar_diputados_v2(
                path_parquet=path_parquet,
                anio=anio,
                path_siglado=siglado_path,
                max_seats=p.get('max_seats', 500),
                sistema=p.get('sistema', 'mixto'),
                mr_seats=p.get('mr_seats', None),
                rp_seats=p.get('rp_seats', None),
                usar_coaliciones=True,
                sobrerrepresentacion=8.0,
                umbral=0.03,
                print_debug=print_debug,
            )

            mr = res.get('mr', {})
            rp = res.get('rp', {})
            tot = res.get('tot', {})
            partidos = list(tot.keys())

            df = pd.DataFrame([{
                'partido': p0,
                'mr': int(mr.get(p0, 0)),
                'rp': int(rp.get(p0, 0)),
                'tot': int(tot.get(p0, 0)),
            } for p0 in partidos])

            if usar_pm:
                try:
                    # read parquet and recompute recomposed with siglado rule
                    df_parq = pd.read_parquet(path_parquet)
                    recomposed = recompose_coalitions(df_parq, anio, 'diputados', rule='equal_residue_siglado', siglado_path=siglado_path)
                    pm_assigned = _simulate_pm_by_runnerup(recomposed, p.get('pm_seats', 100), partidos)
                    df['pm'] = df['partido'].map(lambda x: pm_assigned.get(x, 0))
                except Exception as e:
                    if print_debug:
                        _maybe_log(f"Error simulando PM: {e}", 'error', print_debug)
                    df['pm'] = 0
            else:
                df['pm'] = 0

            # write sheet
            safe_name = (name or 'sheet')[:31]
            df.to_excel(writer, sheet_name=safe_name, index=False)

    _maybe_log(f"Exportado a {out_path}", 'info', False)
    return out_path
