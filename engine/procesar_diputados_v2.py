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
from typing import Dict, List, Optional, Tuple
from .recomposicion import recompose_coalitions, parties_for
from .core import apply_overrep_cap
from .core import DipParams
from .core import largest_remainder, divisor_apportionment

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
        print(f"[DEBUG] Extrayendo coaliciones del siglado: {siglado_path}")
        
        # Verificar estructura del archivo
        if 'coalicion' not in siglado.columns or 'grupo_parlamentario' not in siglado.columns:
            print(f"[DEBUG] Archivo siglado no tiene estructura esperada: {siglado.columns.tolist()}")
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
        
        print(f"[DEBUG] Coaliciones detectadas: {coaliciones}")
        return coaliciones
        
    except Exception as e:
        print(f"[ERROR] Error leyendo siglado {siglado_path}: {e}")
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
            print(f"[DEBUG] Coalición creada: {col_name} = {partidos_disponibles} ({df_modificado[col_name].sum():,} votos)")
    
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
            print(f"[DEBUG] Usando método cuota: {method_normalized}")
            return largest_remainder(votos, escanos, method_normalized)
        else:
            # Fallback a LR_ties original si método no reconocido
            print(f"[DEBUG] Método cuota '{quota_method}' no reconocido, usando LR_ties")
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
            print(f"[DEBUG] Usando método divisor: {method_normalized}")
            return divisor_apportionment(votos, escanos, method_normalized)
        else:
            # Fallback a LR_ties si método no reconocido
            print(f"[DEBUG] Método divisor '{divisor_method}' no reconocido, usando LR_ties")
            q = np.sum(votos) / escanos if escanos > 0 else 0
            return LR_ties(votos, n=escanos, q=q, seed=seed)
            
    else:
        # FALLBACK: usar LR_ties original (comportamiento anterior)
        print(f"[DEBUG] Sin método específico o ambos definidos, usando LR_ties por defecto")
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
            s_rp = s_rp_nuevo
        
        s_tot = s_mr + s_rp
    
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
        print(f"[DEBUG] VTE: {VTE}, VVE: {VVE}, threshold: {threshold}")
    
    # Aplicar umbral de 3%
    ok = (x / VVE >= threshold) if VVE > 0 else np.zeros_like(x, dtype=bool)
    x_ok = x.copy()
    x_ok[~ok] = 0.0  # Partidos <3% no participan en RP
    
    if print_debug:
        print(f"[DEBUG] Partidos que pasan 3%: {np.sum(ok)}")
        print(f"[DEBUG] Votos elegibles: {np.sum(x_ok)}")
    
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
                print(f"[DEBUG] Ajustando suma: {np.sum(s_tot)} -> {S}")
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
        print("[DEBUG] Resultados finales:")
        print(f"MR: {dict(zip(range(len(ssd)), ssd))}")
        print(f"RP: {dict(zip(range(len(s_rp_final)), s_rp_final))}")
        print(f"Total: {dict(zip(range(len(s_tot)), s_tot))}")
    
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
                          max_seats: int = 300, 
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
        if not path_parquet:
            raise ValueError("Debe proporcionar path_parquet")
        
        if not partidos_base:
            partidos_base = parties_for(anio)
        
        if print_debug:
            print(f"[DEBUG] Procesando diputados {anio} con {len(partidos_base)} partidos")
        
        # Leer datos
        try:
            df = pd.read_parquet(path_parquet)
        except Exception as e:
            print(f"[WARN] Error leyendo Parquet: {e}")
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
                    print(f"[DEBUG] Dataset con coaliciones shape: {df.shape}")
                    print("[DEBUG] Saltando recomposición: ya tenemos coaliciones del siglado")
            else:
                if print_debug:
                    print("[DEBUG] No se detectaron coaliciones válidas")
        else:
            if print_debug:
                print(f"[DEBUG] No existe archivo siglado: {siglado_path_auto}")
        
        # Recomposición de coaliciones (solo si no tenemos coaliciones del siglado)
        if coaliciones_detectadas:
            # Usar el dataset con coaliciones directamente
            recomposed = df.copy()
            if print_debug:
                print(f"[DEBUG] Recomposición completada, shape: {recomposed.shape}")
        else:
            # Usar recomposición tradicional
            if path_siglado and os.path.exists(path_siglado):
                if print_debug:
                    print(f"[DEBUG] Usando recomposición con siglado: {path_siglado}")
                # Normalizar siglado
                siglado_df = pd.read_csv(path_siglado)
                siglado_df.columns = [c.upper().replace('ASCII', '').replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U') for c in siglado_df.columns]
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
                    print("[DEBUG] Usando recomposición estándar")
                recomposed = recompose_coalitions(
                    df=df, year=anio, chamber="diputados",
                    rule="equal_residue_solo", siglado_path=None
                )
        
        # Extraer votos nacionales (solo votos individuales para RP)
        votos_partido = {p: int(recomposed[p].sum()) if p in recomposed.columns else 0 for p in partidos_base}
        indep = int(recomposed['CI'].sum()) if 'CI' in recomposed.columns else 0
        
        if print_debug:
            print(f"[DEBUG] Votos por partido (originales): {votos_partido}")
            print(f"[DEBUG] Independientes: {indep}")
        
        # NUEVO: Aplicar redistribución de votos si se proporciona
        if votos_redistribuidos:
            if print_debug:
                print(f"[DEBUG] Aplicando redistribución de votos: {votos_redistribuidos}")
            
            # Calcular total de votos válidos (excluyendo independientes)
            total_votos_validos = sum(votos_partido.values())
            
            if total_votos_validos > 0:
                # CORRECCIÓN: Normalizar TODOS los partidos, no solo los especificados
                votos_partido_redistribuidos = {}
                
                # Verificar si la suma de porcentajes redistribuidos es 100%
                total_porcentajes_especificados = sum(votos_redistribuidos.values())
                
                if abs(total_porcentajes_especificados - 100.0) < 0.01:
                    # Caso 1: Porcentajes suman 100% - usar directamente
                    if print_debug:
                        print(f"[DEBUG] Porcentajes suman 100%, aplicando directamente")
                    
                    for partido in partidos_base:
                        if partido in votos_redistribuidos:
                            nuevo_porcentaje = votos_redistribuidos[partido] / 100.0
                            nuevos_votos = int(total_votos_validos * nuevo_porcentaje)
                            votos_partido_redistribuidos[partido] = nuevos_votos
                        else:
                            # Partido no especificado = 0 votos
                            votos_partido_redistribuidos[partido] = 0
                else:
                    # Caso 2: Porcentajes parciales - mantener proporcionalidad del resto
                    if print_debug:
                        print(f"[DEBUG] Porcentajes parciales ({total_porcentajes_especificados}%), normalizando resto")
                    
                    # Calcular votos para partidos especificados
                    votos_especificados_total = 0
                    for partido in partidos_base:
                        if partido in votos_redistribuidos:
                            nuevo_porcentaje = votos_redistribuidos[partido] / 100.0
                            nuevos_votos = int(total_votos_validos * nuevo_porcentaje)
                            votos_partido_redistribuidos[partido] = nuevos_votos
                            votos_especificados_total += nuevos_votos
                    
                    # Distribuir votos restantes proporcionalmente entre partidos no especificados
                    votos_restantes = total_votos_validos - votos_especificados_total
                    partidos_no_especificados = [p for p in partidos_base if p not in votos_redistribuidos]
                    
                    if partidos_no_especificados and votos_restantes > 0:
                        votos_originales_no_especificados = sum(votos_partido[p] for p in partidos_no_especificados)
                        
                        if votos_originales_no_especificados > 0:
                            for partido in partidos_no_especificados:
                                proporcion = votos_partido[partido] / votos_originales_no_especificados
                                nuevos_votos = int(votos_restantes * proporcion)
                                votos_partido_redistribuidos[partido] = nuevos_votos
                        else:
                            # Distribuir equitativamente si no hay votos originales
                            votos_por_partido = votos_restantes // len(partidos_no_especificados)
                            for partido in partidos_no_especificados:
                                votos_partido_redistribuidos[partido] = votos_por_partido
                
                # Actualizar votos nacionales
                votos_partido = votos_partido_redistribuidos
                
                if print_debug:
                    print(f"[DEBUG] Votos por partido (redistribuidos): {votos_partido}")
                    total_redistribuido = sum(votos_partido.values())
                    print(f"[DEBUG] Total votos después de redistribución: {total_redistribuido}")
        
        # Calcular MR por distrito considerando coaliciones
        if coaliciones_detectadas and usar_coaliciones:
            if print_debug:
                print("[DEBUG] Calculando MR con coaliciones y siglado")
            
            # Cargar siglado para saber qué partido específico gana cada distrito
            siglado_path_auto = f"data/siglado-diputados-{anio}.csv"
            siglado_df = pd.read_csv(siglado_path_auto)
            
            # Obtener todas las columnas candidatas (partidos + coaliciones)
            candidaturas_cols = cols_candidaturas_anio_con_coaliciones(recomposed, anio)
            
            # Calcular ganador por distrito
            mr_raw = {}
            distritos_procesados = 0
            
            for _, distrito in recomposed.iterrows():
                entidad = distrito['ENTIDAD']
                num_distrito = distrito['DISTRITO']
                
                # Encontrar candidatura con más votos
                max_votos = -1
                coalicion_ganadora = None
                for col in candidaturas_cols:
                    if col in distrito and distrito[col] > max_votos:
                        max_votos = distrito[col]
                        coalicion_ganadora = col
                
                distrito_procesado = False
                
                if coalicion_ganadora:
                    # DEBUG: Verificar variables en scope
                    if print_debug and entidad == "AGUASCALIENTES" and num_distrito == 1:
                        print(f"[DEBUG-SCOPE] coalicion_ganadora: {coalicion_ganadora}")
                        print(f"[DEBUG-SCOPE] coaliciones_detectadas keys: {list(coaliciones_detectadas.keys()) if coaliciones_detectadas else 'None'}")
                        print(f"[DEBUG-SCOPE] coalicion_ganadora in coaliciones_detectadas: {coalicion_ganadora in coaliciones_detectadas if coaliciones_detectadas else 'coaliciones_detectadas is None'}")
                    
                    # Si ganó una coalición, buscar en siglado qué partido específico gana
                    if coalicion_ganadora in coaliciones_detectadas:
                        # Normalizar entidad para matching
                        entidad_normalizada = normalize_entidad_ascii(entidad)
                        
                        # Buscar en siglado con normalización flexible
                        siglado_df['entidad_normalizada'] = siglado_df['entidad_ascii'].apply(lambda x: normalize_entidad_ascii(str(x).replace(' ', '')))
                        
                        mask = (siglado_df['entidad_normalizada'] == entidad_normalizada) & (siglado_df['distrito'] == num_distrito)
                        distrito_siglado = siglado_df[mask]
                        
                        if len(distrito_siglado) > 0:
                            # Obtener el partido ganador según siglado
                            partido_ganador = distrito_siglado['grupo_parlamentario'].iloc[0]
                            if partido_ganador in partidos_base:
                                mr_raw[partido_ganador] = mr_raw.get(partido_ganador, 0) + 1
                                distrito_procesado = True
                                if print_debug and len(mr_raw) <= 5:
                                    print(f"[DEBUG] Distrito {entidad}-{num_distrito}: {coalicion_ganadora} -> {partido_ganador} (siglado)")
                        else:
                            # FALLBACK: No está en siglado, usar votos directos de coalición
                            if print_debug:
                                print(f"[FALLBACK] Distrito {entidad}-{num_distrito} no en siglado, usando votos directos")
                            
                            partidos_coalicion = partidos_de_col(coalicion_ganadora)
                            if len(partidos_coalicion) == 1:
                                # Si es partido individual, asignar directamente
                                if partidos_coalicion[0] in partidos_base:
                                    mr_raw[partidos_coalicion[0]] = mr_raw.get(partidos_coalicion[0], 0) + 1
                                    distrito_procesado = True
                                    if print_debug:
                                        print(f"[FALLBACK] Distrito {entidad}-{num_distrito}: {coalicion_ganadora} -> {partidos_coalicion[0]} (directo)")
                            else:
                                # Si es coalición, usar partido con más votos en el distrito
                                votos_coalicion = {}
                                for p in partidos_coalicion:
                                    if p in distrito and p in partidos_base:
                                        votos_coalicion[p] = distrito.get(p, 0)
                                
                                if votos_coalicion:
                                    partido_fallback = max(votos_coalicion, key=votos_coalicion.get)
                                    mr_raw[partido_fallback] = mr_raw.get(partido_fallback, 0) + 1
                                    distrito_procesado = True
                                    if print_debug:
                                        print(f"[FALLBACK] Distrito {entidad}-{num_distrito}: {coalicion_ganadora} -> {partido_fallback} (por votos coalición)")
                                else:
                                    # Último recurso: primer partido de la coalición
                                    partido_fallback = partidos_coalicion[0]
                                    if partido_fallback in partidos_base:
                                        mr_raw[partido_fallback] = mr_raw.get(partido_fallback, 0) + 1
                                        distrito_procesado = True
                                        if print_debug:
                                            print(f"[FALLBACK] Distrito {entidad}-{num_distrito}: {coalicion_ganadora} -> {partido_fallback} (primero de coalición)")
                    else:
                        # Partido individual ganó directamente
                        if coalicion_ganadora in partidos_base:
                            mr_raw[coalicion_ganadora] = mr_raw.get(coalicion_ganadora, 0) + 1
                            distrito_procesado = True
                            if print_debug and len(mr_raw) <= 5:
                                print(f"[DEBUG] Distrito {entidad}-{num_distrito}: {coalicion_ganadora} (individual)")
                
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
                            print(f"[GARANTÍA] Distrito {entidad}-{num_distrito}: {ganador_individual} (ganador directo por votos parquet)")
                
                if distrito_procesado:
                    distritos_procesados += 1
            
            if print_debug:
                print(f"[DEBUG] Total distritos procesados para MR: {distritos_procesados}/300")
            
            mr_aligned = {p: int(mr_raw.get(p, 0)) for p in partidos_base}
            indep_mr = 0
        else:
            # Usar método tradicional sin coaliciones (partido individual con más votos gana)
            if print_debug:
                if coaliciones_detectadas and not usar_coaliciones:
                    print("[DEBUG] Coaliciones detectadas pero DESACTIVADAS por parámetro")
                print("[DEBUG] Calculando MR por partido individual (sin coaliciones)")
            
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
                    print(f"[WARN] Error en mr_by_siglado: {e}")
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
            print(f"[DEBUG] Parámetros recibidos: sistema={sistema}, mr_seats={mr_seats}, rp_seats={rp_seats}, max_seats={max_seats}")
        
        if sistema_tipo == 'mr':
            # Solo MR, sin RP
            m = 0
            S = max_seats
            # Mantener MR calculado del siglado
        elif sistema_tipo == 'rp':
            # Solo RP, sin MR (Plan A)
            m = max_seats
            S = max_seats
            mr_aligned = {p: 0 for p in partidos_base}  # FORZAR MR=0 para Plan A
            if print_debug:
                print(f"[DEBUG] Plan A detectado: forzando MR=0 para todos los partidos")
        else:  # sistema_tipo == 'mixto'
            if mr_seats is not None and rp_seats is not None:
                # Plan C o similar: parámetros explícitos para MR y RP
                if print_debug:
                    print(f"[DEBUG] Plan con parámetros explícitos: MR={mr_seats}, RP={rp_seats}")
                # Ajustar MR calculado para que sume exactamente mr_seats
                total_mr_actual = sum(mr_aligned.values())
                if total_mr_actual != mr_seats:
                    if print_debug:
                        print(f"[DEBUG] Ajustando MR de {total_mr_actual} a {mr_seats}")
                    # Reescalar proporcionalmente
                    if total_mr_actual > 0:
                        factor = mr_seats / total_mr_actual
                        mr_ajustado = {}
                        for p in partidos_base:
                            mr_ajustado[p] = int(round(mr_aligned[p] * factor))
                        # Ajuste fino para suma exacta
                        diferencia = mr_seats - sum(mr_ajustado.values())
                        if diferencia != 0:
                            # Ordenar por MR descendente y ajustar
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
                        votos_array = np.array([votos_partido[p] for p in partidos_base])
                        mr_dist = LR_ties(votos_array, mr_seats)
                        mr_aligned = {partidos_base[i]: int(mr_dist[i]) for i in range(len(partidos_base))}
                
                m = rp_seats
                S = max_seats
            elif mr_seats == 0:
                # Plan A explícito
                if print_debug:
                    print(f"[DEBUG] Plan A explícito (mr_seats=0)")
                m = max_seats
                S = max_seats
                mr_aligned = {p: 0 for p in partidos_base}
            elif rp_seats is not None:
                # Plan vigente: MR libre + RP fijo (caso especial)
                if print_debug:
                    print(f"[DEBUG] Plan vigente detectado: MR libre + RP fijo = {rp_seats}")
                total_mr = sum(mr_aligned.values())
                m = rp_seats  # Usar RP fijo, no calculado
                S = max_seats
            else:
                # Sistema vigente tradicional (usar MR calculado)
                if print_debug:
                    print(f"[DEBUG] Sistema vigente tradicional")
                total_mr = sum(mr_aligned.values())
                m = max_seats - total_mr
                S = max_seats
        
        if print_debug:
            print(f"[DEBUG] Sistema: {sistema_tipo}, m: {m}, S: {S}")
            print(f"[DEBUG] MR por partido: {mr_aligned}")
        
        # Convertir a arrays numpy
        x = np.array([votos_partido[p] for p in partidos_base], dtype=float)
        ssd = np.array([mr_aligned[p] for p in partidos_base], dtype=int)
        
        # Aplicar algoritmo mejorado
        resultado = asignadip_v2(
            x=x, ssd=ssd, indep=indep, nulos=0, no_reg=0,
            m=m, S=S, threshold=umbral, max_seats=max_seats, max_pp=0.08,
            apply_caps=True, quota_method=quota_method, divisor_method=divisor_method,
            seed=seed, print_debug=print_debug
        )
        
        # Convertir resultado a formato esperado
        seats = resultado['seats']
        votes = resultado['votes']
        ok_3pct = resultado['meta']['ok_3pct']
        
        # Crear diccionarios por partido
        mr_dict = {partidos_base[i]: int(seats[0, i]) for i in range(len(partidos_base))}
        rp_dict = {partidos_base[i]: int(seats[1, i]) for i in range(len(partidos_base))}
        tot_dict = {partidos_base[i]: int(seats[2, i]) for i in range(len(partidos_base))}
        ok_dict = {partidos_base[i]: bool(ok_3pct[i]) for i in range(len(partidos_base))}
        votos_ok = {p: votos_partido[p] if ok_dict[p] else 0 for p in partidos_base}
        
        # Aplicar tope por partido si se especifica
        if max_seats_per_party and max_seats_per_party > 0:
            for p in tot_dict:
                if tot_dict[p] > max_seats_per_party:
                    exceso = tot_dict[p] - max_seats_per_party
                    tot_dict[p] = max_seats_per_party
                    rp_dict[p] = max(0, max_seats_per_party - mr_dict[p])
        
        # Aplicar límite de sobrerrepresentación si se especifica
        if sobrerrepresentacion and sobrerrepresentacion > 0:
            if print_debug:
                print(f"[DEBUG] Aplicando límite de sobrerrepresentación: {sobrerrepresentacion}%")
                print(f"[DEBUG] Escaños antes de sobrerrepresentación: {tot_dict}")
            
            # Calcular votos válidos (los que cumplen el umbral)
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
                    print(f"[DEBUG] over_cap = {over_cap} ({sobrerrepresentacion}%)")
                    print(f"[DEBUG] total_escanos = {max_seats}")
                    print(f"[DEBUG] vote_share_valid = {vote_share_valid}")
                
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
                                print(f"[DEBUG] {p}: {tot_dict[p]} -> {tot_dict_ajustado[p]} escaños (límite sobrerrepresentación)")
                            tot_dict[p] = tot_dict_ajustado[p]
                            # Recalcular RP = total - MR
                            rp_dict[p] = max(0, tot_dict[p] - mr_dict[p])
                
                if print_debug:
                    print(f"[DEBUG] Escaños después de sobrerrepresentación: {tot_dict}")
        
        return {
            'mr': mr_dict,
            'rp': rp_dict,
            'tot': tot_dict,
            'ok': ok_dict,
            'votos': votos_partido,
            'votos_ok': votos_ok,
            'meta': resultado['meta']
        }
        
    except Exception as e:
        print(f"[ERROR] procesar_diputados_v2: {e}")
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
