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

# Mapeo global de nombres completos de estados a abreviaciones
NOMBRE_ESTADO_A_ABREV = {
    'AGUASCALIENTES': 'AGS', 'BAJA CALIFORNIA': 'BC', 'BAJA CALIFORNIA SUR': 'BCS',
    'CAMPECHE': 'CAM', 'CHIAPAS': 'CHS', 'CHIHUAHUA': 'CHH', 'COAHUILA': 'COA',
    'COLIMA': 'COL', 'CIUDAD DE MEXICO': 'CDMX', 'DURANGO': 'DGO', 'GUANAJUATO': 'GTO',
    'GUERRERO': 'GRO', 'HIDALGO': 'HGO', 'JALISCO': 'JAL', 'MEXICO': 'MEX',
    'MICHOACAN': 'MIC', 'MORELOS': 'MOR', 'NAYARIT': 'NAY', 'NUEVO LEON': 'NL',
    'OAXACA': 'OAX', 'PUEBLA': 'PUE', 'QUERETARO': 'QRO', 'QUINTANA ROO': 'QR',
    'SAN LUIS POTOSI': 'SLP', 'SINALOA': 'SIN', 'SONORA': 'SON', 'TABASCO': 'TAB',
    'TAMAULIPAS': 'TAM', 'TLAXCALA': 'TLX', 'VERACRUZ': 'VER', 'YUCATAN': 'YUC',
    'ZACATECAS': 'ZAC'
}

def _convertir_estados_a_abrev(dict_estados: Dict) -> Dict:
    """Convierte las claves de un diccionario de estados de nombres completos a abreviaciones"""
    if not dict_estados or not isinstance(dict_estados, dict):
        return dict_estados
    
    dict_abrev = {}
    for estado, valor in dict_estados.items():
        abrev = NOMBRE_ESTADO_A_ABREV.get(estado, estado)
        dict_abrev[abrev] = valor
    
    return dict_abrev

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
                           S: int, max_pp: Optional[float] = 0.08, max_seats: int = 300, 
                           max_seats_per_party: Optional[int] = None,
                           threshold: float = 0.03,  # Umbral de 3% para filtrar partidos
                           iter_max: int = 16,
                           partidos_nombres: Optional[List[str]] = None,
                           mr_son_manuales: bool = False) -> Dict[str, np.ndarray]:
    """
    Aplica topes constitucionales de forma iterativa con bloqueo de partidos capados
    
    Parámetros:
    - s_mr: escaños de MR por partido
    - s_rp: escaños de RP iniciales por partido  
    - v_nacional: proporción de votos nacionales (solo partidos >=3%)
    - S: total de escaños en la cámara
    - max_pp: máximo de sobrerrepresentación (+8 puntos porcentuales). Si es None, NO se aplica límite de %
    - max_seats: tope absoluto de escaños por defecto (300)
    - max_seats_per_party: tope absoluto de escaños por partido (si se especifica, anula max_seats)
    - threshold: umbral de 3% sobre votos válidos (default 0.03)
    - iter_max: máximo de iteraciones
    - mr_son_manuales: True si los MR vienen del frontend (no deben recortarse, solo RP)
    
    Retorna:
    - Dict con 's_rp' (RP ajustado) y 's_tot' (total ajustado)
    """
    # DEBUG: activar diagnóstico automático si recibimos la lista de partidos
    # y contiene 'MORENA' (útil para pruebas locales). Mantener False por defecto.
    debug_morena = False  # Desactivar debug en producción
    try:
        if partidos_nombres and any(str(n).upper() == 'MORENA' for n in partidos_nombres):
            debug_morena = True
    except Exception:
        pass
    
    N = len(s_mr)
    s_mr = s_mr.astype(int)
    s_rp = s_rp.astype(int)
    
    rp_total = int(S - np.sum(s_mr))
    if rp_total < 0:
        rp_total = 0
    
    # Partidos elegibles: deben pasar el umbral del 3% (threshold)
    # CRÍTICO: usar threshold para determinar elegibilidad, no solo v_nacional > 0
    ok = v_nacional >= threshold
    
    # Límites por sobrerrepresentación (+8 pp)
    # IMPORTANTE: Si max_pp es None, NO aplicar límite de %
    if max_pp is not None:
        # Aplicar cláusula de sobrerrepresentación - CORREGIDO: usar floor estricto
        cap_dist = np.floor((v_nacional + max_pp) * S).astype(int)
        cap_dist[~ok] = s_mr[~ok]  # Partidos <3%: límite = MR únicamente
    else:
        # SIN límite de sobrerrepresentación: cap_dist = infinito (usar valor muy alto)
        cap_dist = np.full(N, S, dtype=int)  # Límite = total de escaños (sin restricción %)
    
    # DEBUG: Imprimir cálculo de cap para partidos grandes
    if debug_morena and max_pp is not None:
        for idx in range(N):
            if v_nacional[idx] > 0.25:  # Partidos con >25% votación
                nombre = partidos_nombres[idx] if partidos_nombres else f"partido_{idx}"
                print(f"\n[DEBUG CAP CALCULATION - {nombre} (idx={idx})]")
                print(f"  v_nacional: {v_nacional[idx]:.6f}")
                print(f"  v_nacional + max_pp: {v_nacional[idx] + max_pp:.6f}")
                print(f"  (v_nacional + max_pp) * S: {(v_nacional[idx] + max_pp) * S:.2f}")
                print(f"  cap_dist (floor): {cap_dist[idx]}")
                print(f"  Expected cap for 42.49%: {np.floor((0.4249 + 0.08) * S)}")
    
    # Determinar tope absoluto a aplicar
    # IMPORTANTE: Si max_seats_per_party es None, NO aplicar tope absoluto
    if max_seats_per_party is not None:
        tope_absoluto = max_seats_per_party
    else:
        # NO aplicar tope absoluto: usar valor muy alto (igual al total de escaños S)
        # Esto efectivamente desactiva el tope absoluto
        tope_absoluto = S  
    
    # Límites efectivos por el tope del +8%
    # CRÍTICO: El tope constitucional es ABSOLUTO, no puede excederse por MR
    # Si un partido gana 311 MR pero el tope +8% es 252, debe quedarse con solo 252
    lim_max = cap_dist.copy()
    
    # Aplicar tope absoluto solo si está definido explícitamente
    if max_seats_per_party is not None:
        lim_max = np.minimum(lim_max, tope_absoluto)
    
    # EXCEPCIÓN: Si tengo MR > tope (porque la gente votó así), respetamos MR 
    # Pero el partido NO PUEDE recibir RP adicional
    # Por ahora, aplicamos el tope estricto y recortamos MR si excede
    # (esto es debatible, pero parece ser la interpretación constitucional)
    
    s_tot = s_mr + s_rp
    
    # Conjunto de partidos bloqueados para reinyección (empezar vacío)
    capped = np.zeros(N, dtype=bool)
    
    # PASO 1: Recorte inicial - identificar partidos que exceden el tope
    sobrantes = 0
    
    # DEBUG: Imprimir información de partidos que exceden el tope
    if debug_morena and N > 0:
        for idx in range(N):
            nombre = partidos_nombres[idx] if partidos_nombres else f"partido_{idx}"
            if s_tot[idx] > cap_dist[idx]:
                print(f"\n[DEBUG PASO 1 INICIO - {nombre} (idx={idx})]")
                print(f"  cap_dist (tope +8%): {cap_dist[idx]}")
                print(f"  lim_max (límite efectivo): {lim_max[idx]}")
                print(f"  s_mr (MR inicial): {s_mr[idx]}")
                print(f"  s_rp (RP inicial): {s_rp[idx]}")
                print(f"  s_tot (total inicial): {s_tot[idx]}")
    
    for p in range(N):
        cap_eff = lim_max[p]
        if s_tot[p] > cap_eff:
            # 🔥 CRÍTICO: Si los MR son manuales del frontend, NO recortarlos
            # Solo recortar RP en este caso
            if mr_son_manuales:
                # MR manuales: solo quitar RP, NUNCA tocar MR
                excess = s_tot[p] - cap_eff
                cut_rp = min(excess, s_rp[p])
                s_rp[p] -= cut_rp
                s_tot[p] -= cut_rp
                sobrantes += cut_rp
                cut_mr = 0
                
                # Bloquear si está al tope
                if s_tot[p] >= cap_eff:
                    capped[p] = True
                    
                if debug_morena:
                    nombre = partidos_nombres[p] if partidos_nombres else f"partido_{p}"
                    print(f"[DEBUG MR MANUALES - {nombre}] Recorte: -RP={cut_rp}, MR preservados={s_mr[p]}, Total={s_tot[p]}")
            else:
                # MR calculados: aplicar tope normal (primero RP, luego MR si excede)
                excess = s_tot[p] - cap_eff
                
                # Primero intentar quitar RP
                cut_rp = min(excess, s_rp[p])
                s_rp[p] -= cut_rp
                s_tot[p] -= cut_rp
                sobrantes += cut_rp
                excess -= cut_rp
                
                # Si aún excede después de quitar todo el RP, quitar MR
                if excess > 0:
                    cut_mr = min(excess, s_mr[p])
                    s_mr[p] -= cut_mr
                    s_tot[p] -= cut_mr
                    sobrantes += cut_mr
                else:
                    cut_mr = 0
                
                # Bloquear partido para no recibir más RP
                if s_tot[p] >= cap_eff:
                    capped[p] = True
                
            # DEBUG: Imprimir info después del recorte
            if debug_morena:
                nombre = partidos_nombres[p] if partidos_nombres else f"partido_{p}"
                print(f"\n[DEBUG PASO 1 DESPUÉS RECORTE - {nombre} (idx={p})]")
                print(f"  cut_rp: {cut_rp}")
                print(f"  cut_mr: {cut_mr}")
                print(f"  s_mr después: {s_mr[p]}")
                print(f"  s_rp después: {s_rp[p]}")
                print(f"  s_tot después: {s_tot[p]}")
                print(f"  capped: {capped[p]}")
                print(f"  sobrantes totales: {sobrantes}")
    
    # Partidos <3% también se bloquean (no pueden recibir RP)
    capped[~ok] = True
    
    # DEBUG: Estado antes de PASO 2
    if debug_morena:
        for idx in range(N):
            if capped[idx]:
                nombre = partidos_nombres[idx] if partidos_nombres else f"partido_{idx}"
                print(f"\n[DEBUG ANTES PASO 2 - {nombre} (idx={idx}) BLOQUEADO]")
                print(f"  s_tot: {s_tot[idx]}")
                print(f"  lim_max: {lim_max[idx]}")
        print(f"\n[DEBUG ANTES PASO 2]")
        print(f"  sobrantes para redistribuir: {sobrantes}")
    
    # PASO 2: Reinyección iterativa SIN romper topes
    # Los RP sobrantes se redistribuyen a partidos NO capados
    while sobrantes > 0:
        # Votos efectivos solo de partidos no capados y elegibles
        v_eff = v_nacional.copy()
        v_eff[capped] = 0.0
        
        if np.sum(v_eff) <= 0:
            # No hay a quién reasignar sin romper topes
            break
        
        # Usar fórmula de residuos (largest remainder)
        # q es la cuota para distribuir los sobrantes
        q = np.sum(v_eff) / sobrantes if sobrantes > 0 else 0.0
        if q <= 0:
            break
        
        # Calcular residuos para cada partido no capado
        residuos = v_eff % q
        
        # Encontrar el partido con mayor residuo entre no capados
        cand_idx = -1
        max_residuo = -np.inf
        for p in range(N):
            if not capped[p] and v_eff[p] > 0:
                if residuos[p] > max_residuo:
                    max_residuo = residuos[p]
                    cand_idx = p
        
        if cand_idx == -1:
            # No encontramos candidato válido
            break
        
        # Intentar asignar 1 RP al candidato
        cap_eff = lim_max[cand_idx]
        
        if s_tot[cand_idx] >= cap_eff:
            # Ya está en el tope - bloquear y continuar
            capped[cand_idx] = True
            continue
        
        # Asignar el escaño
        s_rp[cand_idx] += 1
        s_tot[cand_idx] += 1
        sobrantes -= 1
        
        # DEBUG: Si se asigna a cualquier partido
        if debug_morena:
            nombre = partidos_nombres[cand_idx] if partidos_nombres else f"partido_{cand_idx}"
            if s_tot[cand_idx] > lim_max[cand_idx] * 0.95:  # Solo imprimir si está cerca del tope
                print(f"\n[DEBUG PASO 2 - ASIGNACIÓN A {nombre} (idx={cand_idx})]")
                print(f"  Sobrantes restantes: {sobrantes}")
                print(f"  s_tot ahora: {s_tot[cand_idx]}")
                print(f"  s_rp ahora: {s_rp[cand_idx]}")
                print(f"  lim_max: {lim_max[cand_idx]}")
        
        # Si llegó al tope exacto, bloquear para futuras asignaciones
        if s_tot[cand_idx] >= cap_eff:
            capped[cand_idx] = True
    
    # PASO 3: Si quedan sobrantes y no pudimos reasignarlos, redistribuir proporcionalmente
    # entre todos los no capados usando LR estándar
    if sobrantes > 0:
        v_eff = v_nacional.copy()
        v_eff[capped] = 0.0
        
        if np.sum(v_eff) > 0:
            add = LR_ties(v_eff, n=sobrantes)
            for p in range(N):
                if not capped[p] and add[p] > 0:
                    # Verificar que no rompa el tope
                    margen = lim_max[p] - s_tot[p]
                    asignar = min(add[p], margen)
                    s_rp[p] += asignar
                    s_tot[p] += asignar
    
    # PASO 4: Ajuste final para cumplir exactamente S escaños (sin romper topes)
    delta = int(S - np.sum(s_tot))
    
    if delta != 0:
        # Calcular margen disponible por partido (cuánto pueden crecer sin romper tope)
        margin = lim_max - s_tot
        margin[capped] = 0  # Partidos capados no tienen margen
        margin[~ok] = 0  # Partidos <3% tampoco
        
        if delta > 0:
            # Faltan escaños: asignar a quienes tienen margen positivo
            cand = np.where(margin > 0)[0]
            if len(cand) > 0:
                # Ordenar por proporción de votos descendente
                ord_idx = np.argsort(-v_nacional[cand])
                for i in range(min(delta, len(cand))):
                    p = cand[ord_idx[i]]
                    # Verificar que aún tenga margen (por si ya asignamos antes)
                    if s_tot[p] < lim_max[p]:
                        s_rp[p] += 1
                        s_tot[p] += 1
        else:
            # Sobran escaños: quitar de quienes tienen RP
            cand = np.where((s_rp > 0) & ok)[0]
            if len(cand) > 0:
                # Ordenar por RP descendente
                ord_idx = np.argsort(-s_rp[cand])
                for i in range(min(-delta, len(cand))):
                    p = cand[ord_idx[i]]
                    if s_rp[p] > 0:
                        s_rp[p] -= 1
                        s_tot[p] -= 1
    
    # PASO 5: Validación final estricta
    # Asegurar que partidos <3% no reciben RP
    s_rp[~ok] = 0
    
    # Validar que ningún partido excede su tope
    for p in range(N):
        if s_tot[p] > lim_max[p]:
            # Esto NO debería pasar, pero si pasa, recortar RP
            excess = s_tot[p] - lim_max[p]
            cut = min(excess, s_rp[p])
            s_rp[p] -= cut
            s_tot[p] -= cut
    
    # Validación: partidos que exceden +8pp no deben tener RP
    violadores = np.where(s_mr > cap_dist)[0]
    for p in violadores:
        if ok[p] and s_rp[p] > 0:
            # Si un partido tiene MR que ya excede el tope de +8pp, no puede tener RP
            s_rp[p] = 0
    
    # Recalcular totales finales
    s_tot = s_mr + s_rp
    
    # DEBUG: Estado final - todos los partidos capados
    if debug_morena:
        print(f"\n[DEBUG FINAL - PARTIDOS CAPADOS]")
        for idx in range(N):
            if s_tot[idx] >= lim_max[idx] * 0.95:  # Cerca del tope o sobre él
                nombre = partidos_nombres[idx] if partidos_nombres else f"partido_{idx}"
                excede = s_tot[idx] > lim_max[idx]
                print(f"\n  {nombre} (idx={idx}):")
                print(f"    s_mr: {s_mr[idx]}")
                print(f"    s_rp: {s_rp[idx]}")
                print(f"    s_tot: {s_tot[idx]}")
                print(f"    lim_max (cap +8%): {lim_max[idx]}")
                print(f"    EXCEDE TOPE: {excede}")
                if excede:
                    print(f"    EXCESO: {s_tot[idx] - lim_max[idx]} escaños")
    
    return {
        's_rp': s_rp.astype(int),
        's_tot': s_tot.astype(int)
    }


# --------------------- Export scenarios helper ---------------------
def _simulate_pm_by_runnerup(recomposed_df: pd.DataFrame, pm_seats: int, partidos: list) -> dict:
    """Simula asignación PM repartiendo a los partidos que fueron segundos por distrito.

    Devuelve un dict partido->escaños PM distribuyendo pm_seats proporcionalmente a las apariciones como segundo.
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
    
    # Distribuir pm_seats proporcionalmente a las apariciones como segundo
    if not segundos or pm_seats == 0:
        return pm_dict
    
    # Obtener todos los segundos lugares ordenados por frecuencia
    total_segundos = sum(c.values())
    escanos_asignados = 0
    
    # Método proporcional: asignar escaños PM según proporción de segundos lugares
    partidos_ordenados = c.most_common()
    for i, (partido, conteo) in enumerate(partidos_ordenados):
        if escanos_asignados >= pm_seats:
            break
        # Calcular proporción y asignar
        proporcion = conteo / total_segundos
        escanos_partido = int(proporcion * pm_seats)
        # Asegurar que no excedamos pm_seats
        escanos_partido = min(escanos_partido, pm_seats - escanos_asignados)
        if escanos_partido > 0:
            pm_dict[partido] = escanos_partido
            escanos_asignados += escanos_partido
    
    # Asignar escaños restantes uno por uno a los partidos con más segundos lugares
    if escanos_asignados < pm_seats:
        for partido, _ in partidos_ordenados:
            if escanos_asignados >= pm_seats:
                break
            pm_dict[partido] += 1
            escanos_asignados += 1
    
    return pm_dict


def _aplicar_topes_a_pm(mr_dict: dict, pm_dict: dict, votos_pct: dict, 
                        partidos: list, S: int = 400,
                        max_pp: Optional[float] = 0.08, 
                        max_seats_per_party: Optional[int] = 300,
                        threshold: float = 0.03,
                        print_debug: bool = False) -> dict:
    """Aplica topes constitucionales a la asignación de PM.
    
    Los topes se aplican al TOTAL de escaños (MR + PM), no solo a PM.
    Si MR + PM excede el límite, se reduce PM proporcionalmente.
    Los escaños PM sobrantes se redistribuyen a otros partidos elegibles.
    
    Parámetros:
    - mr_dict: escaños de MR por partido
    - pm_dict: escaños de PM iniciales por partido
    - votos_pct: porcentaje de votos nacionales por partido (ej: 0.4249 para 42.49%)
    - partidos: lista de partidos
    - S: total de escaños (400 para diputados)
    - max_pp: máximo de sobrerrepresentación (+8 pp)
    - max_seats_per_party: tope absoluto por partido (300)
    - threshold: umbral del 3%
    - print_debug: activar logs
    
    Retorna:
    - pm_dict ajustado respetando topes constitucionales
    """
    if max_pp is None and max_seats_per_party is None:
        # Sin topes, retornar PM sin cambios
        return pm_dict
    
    pm_ajustado = pm_dict.copy()
    
    # Calcular límites por partido
    caps = {}
    for p in partidos:
        v_pct = votos_pct.get(p, 0.0)
        
        # Límite por sobrerrepresentación (+8%)
        if max_pp is not None and v_pct >= threshold:
            cap_sobrerep = int(np.floor((v_pct + max_pp) * S))
        else:
            cap_sobrerep = S  # Sin límite de sobrerrepresentación
        
        # Límite absoluto (300 escaños)
        if max_seats_per_party is not None:
            cap_absoluto = max_seats_per_party
        else:
            cap_absoluto = S  # Sin límite absoluto
        
        # El tope efectivo es el menor de ambos
        caps[p] = min(cap_sobrerep, cap_absoluto)
        
        # Partidos <3%: solo pueden tener MR
        if v_pct < threshold:
            caps[p] = mr_dict.get(p, 0)
    
    # PASO 1: Recortar PM de partidos que exceden el tope
    pm_sobrantes = 0
    partidos_capados = set()
    
    for p in partidos:
        mr = mr_dict.get(p, 0)
        pm = pm_ajustado.get(p, 0)
        total = mr + pm
        cap = caps.get(p, S)
        
        if total > cap:
            # Excede el tope: reducir PM
            exceso = total - cap
            recorte_pm = min(exceso, pm)  # No podemos recortar más PM del que tiene
            
            pm_ajustado[p] -= recorte_pm
            pm_sobrantes += recorte_pm
            partidos_capados.add(p)
            
            if print_debug:
                v_pct = votos_pct.get(p, 0.0)
                _maybe_log(f"[TOPES PM] {p}: MR={mr} + PM={pm} = {total} > {cap} (votos={v_pct:.2%}+{max_pp*100:.0%}={v_pct+max_pp:.2%})", 'debug', print_debug)
                _maybe_log(f"[TOPES PM] {p}: Recortando {recorte_pm} PM → PM ajustado={pm_ajustado[p]}", 'debug', print_debug)
    
    # Marcar partidos <3% como capados (no pueden recibir PM redistributed)
    for p in partidos:
        if votos_pct.get(p, 0.0) < threshold:
            partidos_capados.add(p)
    
    # PASO 2: Redistribuir PM sobrantes a partidos NO capados
    if pm_sobrantes > 0 and print_debug:
        _maybe_log(f"[TOPES PM] PM sobrantes para redistribuir: {pm_sobrantes}", 'debug', print_debug)
    
    while pm_sobrantes > 0:
        # Calcular votos efectivos de partidos elegibles (no capados, >=3%)
        votos_elegibles = {}
        for p in partidos:
            if p in partidos_capados:
                continue
            
            v_pct = votos_pct.get(p, 0.0)
            if v_pct < threshold:
                continue
            
            mr = mr_dict.get(p, 0)
            pm = pm_ajustado.get(p, 0)
            cap = caps.get(p, S)
            
            # ¿Tiene espacio para más PM?
            if mr + pm < cap:
                votos_elegibles[p] = v_pct
        
        if not votos_elegibles:
            # No hay partidos elegibles: los PM sobrantes se pierden
            if print_debug:
                _maybe_log(f"[TOPES PM] No hay partidos elegibles. {pm_sobrantes} PM sobrantes se pierden.", 'warning', print_debug)
            break
        
        # Asignar 1 PM al partido con más votos que tenga espacio
        p_max = max(votos_elegibles, key=votos_elegibles.get)
        pm_ajustado[p_max] += 1
        pm_sobrantes -= 1
        
        # Verificar si el partido alcanzó su tope
        mr = mr_dict.get(p_max, 0)
        pm = pm_ajustado.get(p_max, 0)
        cap = caps.get(p_max, S)
        
        if mr + pm >= cap:
            partidos_capados.add(p_max)
            if print_debug:
                _maybe_log(f"[TOPES PM] {p_max}: Alcanzó tope {cap} (MR={mr} + PM={pm})", 'debug', print_debug)
    
    return pm_ajustado

    

# ====================== ASIGNACIÓN PRINCIPAL ======================

def asignadip_v2(x: np.ndarray, ssd: np.ndarray, 
                 indep: int = 0, nulos: int = 0, no_reg: int = 0,
                 m: int = 200, S: Optional[int] = None,
                 threshold: float = 0.03,
                 max_seats: int = 300, max_pp: Optional[float] = 0.08,
                 max_seats_per_party: Optional[int] = None,
                 apply_caps: bool = True,
                 quota_method: Optional[str] = None,
                 divisor_method: Optional[str] = None,
                 seed: Optional[int] = None,
                 partidos_base: Optional[List[str]] = None,
                 mr_son_manuales: bool = False,  # 🔥 NUEVO: Flag para MR manuales del frontend
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
    - max_seats: tope de 300 escaños por partido (por defecto)
    - max_pp: sobrerrepresentación máxima (+8 pp)
    - max_seats_per_party: tope absoluto de escaños por partido (anula max_seats si se especifica)
    - apply_caps: aplicar topes constitucionales
    - mr_son_manuales: True si los MR vienen del frontend (sliders), no deben recortarse
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
    
    # Proporción nacional (sobre TODOS los votos, no solo elegibles)
    # CRÍTICO: El tope de +8pp se calcula sobre la proporción nacional REAL,
    # no sobre la proporción redistribuida entre solo partidos elegibles
    v_nacional_total = x / np.sum(x) if np.sum(x) > 0 else np.zeros_like(x)
    
    # Aplicar topes constitucionales
    if apply_caps:
        resultado_topes = aplicar_topes_nacionales(
            s_mr=ssd, s_rp=s_rp_init, v_nacional=v_nacional_total,
            S=S, max_pp=max_pp, max_seats=max_seats,
            max_seats_per_party=max_seats_per_party,
            threshold=threshold,  # Pasar umbral del 3% para filtrado correcto
            partidos_nombres=partidos_base,
            mr_son_manuales=mr_son_manuales  # 🔥 CRÍTICO: Preservar MR manuales del frontend
        )
        s_tot = resultado_topes['s_tot']
        s_rp_final = resultado_topes['s_rp']
        # IMPORTANTE: Calcular MR ajustado después de aplicar topes
        s_mr_final = s_tot - s_rp_final
        
        # Verificar suma exacta
        if np.sum(s_tot) != S:
            if print_debug:
                _maybe_log(f"Ajustando suma: {np.sum(s_tot)} -> {S}", 'debug', print_debug)
            s_rp_final = s_rp_final.copy()
            s_tot = ssd + s_rp_final
        
        # Calcular MR ajustado (puede haber sido recortado por topes)
        s_mr_final = s_tot - s_rp_final
    else:
        # Sin topes: solo ajustar para cumplir S exactamente
        s_tot = ssd + s_rp_init
        delta = int(S - np.sum(s_tot))
        
        if delta != 0:
            ord_idx = np.argsort(-v_nacional_total)
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
        s_mr_final = ssd  # Sin topes, MR no cambia
    
    # Preparar matrices de resultados
    # IMPORTANTE: tot debe ser siempre s_mr_final + s_rp_final para consistencia
    seats = np.row_stack([
        s_mr_final.astype(int),  # MR (ajustado si apply_caps recortó)
        s_rp_final.astype(int),  # RP
        (s_mr_final + s_rp_final).astype(int)  # Total = MR + RP (consistente)
    ])
    
    # Proporción nacional solo de elegibles (para reportar, no para topes)
    v_nacional_elegibles = x_ok / np.sum(x_ok) if np.sum(x_ok) > 0 else np.zeros_like(x_ok)
    
    votes = np.row_stack([
        x / VTE if VTE > 0 else np.zeros_like(x),  # Proporción sobre total
        x / VVE if VVE > 0 else np.zeros_like(x),  # Proporción sobre válida
        v_nacional_elegibles  # Proporción nacional (solo elegibles)
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
            'ok_3pct': ok.tolist(),  # Convertir ndarray a lista para JSON
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
                          pm_seats: Optional[int] = None,  # Primera minoría
                          regla_electoral: Optional[str] = None,
                          quota_method: str = 'hare',
                          divisor_method: str = 'dhondt',
                          umbral: float = 0.03,  # Default: umbral del 3% (cambiar a 0.0 para desactivar)
                          max_seats_per_party: Optional[int] = None,
                          sobrerrepresentacion: Optional[float] = None,
                          aplicar_topes: bool = True,  # Nuevo: controlar si se aplican topes constitucionales
                          usar_coaliciones: bool = True,
                          votos_redistribuidos: Optional[Dict] = None,
                          mr_ganados_geograficos: Optional[Dict[str, int]] = None,  # NUEVO: MR por partido con redistritación geográfica
                          seed: Optional[int] = None,
                          print_debug: bool = False) -> Dict:
    """
    Procesador principal de diputados versión 2
    
    Args:
        ...
        mr_ganados_geograficos: Dict opcional con MR ganados por cada partido usando redistritación geográfica real.
                                Si se proporciona, se usa en lugar del cálculo proporcional simple.
                                Formato: {'MORENA': 153, 'PAN': 45, ...}
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
        
        # CRÍTICO: Si usar_coaliciones=False, desagregar votos de coalición
        # Esto simula el contrafactual "como si nunca hubieran competido juntos"
        if not usar_coaliciones and coaliciones_detectadas:
            if print_debug:
                _maybe_log("DESAGREGANDO votos de coalición (contrafactual: competencia separada)", 'info', print_debug)
            
            # Identificar coaliciones por año
            coaliciones_por_anio = {
                2018: ['MORENA', 'PT', 'PES'],
                2021: ['MORENA', 'PT', 'PVEM'],
                2024: ['MORENA', 'PT', 'PVEM']
            }
            
            partidos_coalicion = coaliciones_por_anio.get(anio, [])
            
            if partidos_coalicion:
                # Cargar datos históricos para calcular proporciones (año anterior)
                anio_ref = anio - 3  # 2024 → 2021, 2021 → 2018
                path_ref = f"data/computos_diputados_{anio_ref}.parquet"
                
                proporciones_desagregacion = {}
                
                if os.path.exists(path_ref):
                    try:
                        df_ref = pd.read_parquet(path_ref)
                        df_ref.columns = [norm_ascii_up(c) for c in df_ref.columns]
                        
                        # Calcular proporciones nacionales del año de referencia
                        votos_ref = {}
                        for p in partidos_coalicion:
                            if p in df_ref.columns:
                                votos_ref[p] = df_ref[p].sum()
                        
                        total_ref = sum(votos_ref.values())
                        if total_ref > 0:
                            for p in partidos_coalicion:
                                proporciones_desagregacion[p] = votos_ref.get(p, 0) / total_ref
                            
                            if print_debug:
                                _maybe_log(f"Proporciones de desagregación (basadas en {anio_ref}):", 'debug', print_debug)
                                for p in partidos_coalicion:
                                    pct = proporciones_desagregacion.get(p, 0) * 100
                                    _maybe_log(f"  {p}: {pct:.2f}%", 'debug', print_debug)
                    except Exception as e:
                        if print_debug:
                            _maybe_log(f"Error cargando datos de referencia {anio_ref}: {e}", 'warn', print_debug)
                
                # Si no hay datos de referencia, usar proporciones por default
                if not proporciones_desagregacion:
                    # Proporciones aproximadas históricas
                    if anio == 2024:
                        proporciones_desagregacion = {'MORENA': 0.75, 'PT': 0.10, 'PVEM': 0.15}
                    elif anio == 2021:
                        proporciones_desagregacion = {'MORENA': 0.80, 'PT': 0.08, 'PVEM': 0.12}
                    elif anio == 2018:
                        proporciones_desagregacion = {'MORENA': 0.70, 'PT': 0.15, 'PES': 0.15}
                    
                    if print_debug:
                        _maybe_log(f"Usando proporciones por default", 'warn', print_debug)
                
                # Desagregar votos: tomar el total de la coalición y repartirlo
                total_coalicion = sum(votos_partido.get(p, 0) for p in partidos_coalicion)
                
                if print_debug:
                    _maybe_log(f"Total votos coalición: {total_coalicion:,}", 'debug', print_debug)
                
                # Redistribuir según proporciones
                for p in partidos_coalicion:
                    if p in proporciones_desagregacion:
                        votos_desagregados = int(total_coalicion * proporciones_desagregacion[p])
                        votos_partido[p] = votos_desagregados
                        
                        if print_debug:
                            _maybe_log(f"  {p}: {votos_desagregados:,} votos ({proporciones_desagregacion[p]*100:.1f}%)", 'debug', print_debug)
        
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
        # NUEVO: Si se proporciona mr_ganados_geograficos, usar esos valores directamente
        # (evita el cálculo distrito por distrito usando redistritación geográfica real)
        mr_son_manuales = False  # 🔥 Bandera para evitar reescalar MR manuales del frontend
        if mr_ganados_geograficos is not None:
            if print_debug:
                _maybe_log("Usando MR geográficos proporcionados (redistritación geográfica real)", 'info', print_debug)
                _maybe_log(f"MR geográficos: {mr_ganados_geograficos}", 'debug', print_debug)
            
            # Asegurar que todos los partidos base están representados
            mr_aligned = {p: int(mr_ganados_geograficos.get(p, 0)) for p in partidos_base}
            indep_mr = 0
            mr_son_manuales = True  # ✅ Marcar que estos MR vienen del frontend (no reescalar)
            
            total_mr_geograficos = sum(mr_aligned.values())
            if print_debug:
                _maybe_log(f"Total MR geográficos: {total_mr_geograficos}", 'debug', print_debug)
            
            # 🔥 CRÍTICO: Construir mr_por_estado_raw para distribución geográfica
            # Cuando se usan mr_ganados_geograficos, necesitamos distribuirlos por estado
            # para que la tabla de distritos muestre TODOS los partidos, no solo uno
            mr_por_estado_raw = {}
            try:
                from redistritacion.modulos.reparto_distritos import repartir_distritos_hare
                from redistritacion.modulos.distritacion import cargar_secciones_ine
                
                # Cargar población por estado
                secciones = cargar_secciones_ine()
                poblacion_por_estado = secciones.groupby('ENTIDAD')['POBTOT'].sum().to_dict()
                
                # Determinar total de distritos MR a distribuir
                total_mr_a_distribuir = total_mr_geograficos if total_mr_geograficos > 0 else mr_seats
                
                # VALIDACIÓN CRÍTICA: Si total_mr_a_distribuir < 64 (mínimo constitucional)
                # usar mr_seats como base para la distribución Hare
                # Esto evita el error cuando el usuario envía MR manuales con total < 64
                n_distritos_para_hare = max(total_mr_a_distribuir, 64)
                
                if print_debug and total_mr_a_distribuir < 64:
                    _maybe_log(f"[mr_por_estado_raw] Total MR manuales ({total_mr_a_distribuir}) < 64, usando {n_distritos_para_hare} para Hare", 'warn', print_debug)
                
                # Repartir distritos usando Hare
                asignacion_distritos = repartir_distritos_hare(
                    poblacion_estados=poblacion_por_estado,
                    n_distritos=n_distritos_para_hare,
                    piso_constitucional=2
                )
                
                # Mapeo de IDs a nombres
                estado_nombres = {
                    1: 'AGUASCALIENTES', 2: 'BAJA CALIFORNIA', 3: 'BAJA CALIFORNIA SUR',
                    4: 'CAMPECHE', 5: 'CHIAPAS', 6: 'CHIHUAHUA', 7: 'COAHUILA',
                    8: 'COLIMA', 9: 'CIUDAD DE MEXICO', 10: 'DURANGO', 11: 'GUANAJUATO',
                    12: 'GUERRERO', 13: 'HIDALGO', 14: 'JALISCO', 15: 'MEXICO',
                    16: 'MICHOACAN', 17: 'MORELOS', 18: 'NAYARIT', 19: 'NUEVO LEON',
                    20: 'OAXACA', 21: 'PUEBLA', 22: 'QUERETARO', 23: 'QUINTANA ROO',
                    24: 'SAN LUIS POTOSI', 25: 'SINALOA', 26: 'SONORA', 27: 'TABASCO',
                    28: 'TAMAULIPAS', 29: 'TLAXCALA', 30: 'VERACRUZ', 31: 'YUCATAN',
                    32: 'ZACATECAS'
                }
                
                # Inicializar estados con abreviaciones
                for estado_id, nombre_estado in estado_nombres.items():
                    if estado_id in asignacion_distritos:
                        abrev = NOMBRE_ESTADO_A_ABREV.get(nombre_estado, nombre_estado)
                        mr_por_estado_raw[abrev] = {p: 0 for p in partidos_base}
                
                # Distribuir MR de cada partido proporcionalmente por estado usando POBLACIÓN
                # NO usar total_mr_a_distribuir porque da 0 para partidos con pocos MR
                import math
                
                # Calcular total de población para normalizar
                poblacion_total = sum(poblacion_por_estado.values())
                
                for partido in partidos_base:
                    mr_partido_total = mr_aligned.get(partido, 0)
                    if mr_partido_total == 0:
                        continue
                    
                    # Calcular distribución proporcional USANDO POBLACIÓN DEL ESTADO
                    mr_asignados = 0
                    residuos = []
                    
                    for estado_id, nombre_estado in estado_nombres.items():
                        if estado_id not in asignacion_distritos:
                            continue
                        
                        abrev = NOMBRE_ESTADO_A_ABREV.get(nombre_estado, nombre_estado)
                        
                        # Proporción basada en POBLACIÓN del estado (no en total de MR)
                        poblacion_estado = poblacion_por_estado.get(estado_id, 0)
                        proporcion_poblacional = poblacion_estado / poblacion_total if poblacion_total > 0 else 0
                        proporcion = mr_partido_total * proporcion_poblacional
                        
                        # Asignar parte entera
                        mr_floor = math.floor(proporcion)
                        mr_por_estado_raw[abrev][partido] = mr_floor
                        mr_asignados += mr_floor
                        
                        # Guardar residuo para método Hare
                        residuo = proporcion - mr_floor
                        residuos.append((residuo, abrev, estado_id))
                    
                    # Asignar MR restantes usando método Hare (mayores residuos)
                    # VALIDACIÓN: solo asignar si el estado tiene capacidad disponible
                    mr_faltantes = mr_partido_total - mr_asignados
                    residuos.sort(reverse=True)
                    
                    for i in range(mr_faltantes):
                        if i >= len(residuos):
                            break
                        
                        # Buscar un estado con capacidad disponible
                        asignado = False
                        for j in range(i, len(residuos)):
                            _, abrev_estado, estado_id = residuos[j]
                            max_distritos = asignacion_distritos.get(estado_id, 0)
                            total_actual = sum(mr_por_estado_raw[abrev_estado].values())
                            
                            # Solo asignar si hay capacidad
                            if total_actual < max_distritos:
                                mr_por_estado_raw[abrev_estado][partido] += 1
                                asignado = True
                                # Mover este estado al final para no volver a usarlo de inmediato
                                if j > i:
                                    residuos[i], residuos[j] = residuos[j], residuos[i]
                                break
                        
                        if not asignado:
                            # No hay estados disponibles para este MR adicional
                            if print_debug:
                                _maybe_log(f"[mr_por_estado_raw] No se pudo asignar 1 MR de {partido} (sin capacidad)", 'warn', print_debug)
                            break
                
                if print_debug:
                    _maybe_log(f"[mr_por_estado_raw] Construido para {len(mr_por_estado_raw)} estados desde mr_ganados_geograficos", 'debug', print_debug)
                    total_desglosado = sum(sum(partidos.values()) for partidos in mr_por_estado_raw.values())
                    _maybe_log(f"[mr_por_estado_raw] Total desglosado: {total_desglosado}/{total_mr_geograficos}", 'debug', print_debug)
                    
            except Exception as e_geo:
                if print_debug:
                    _maybe_log(f"[mr_por_estado_raw] Error construyendo distribución geográfica: {e_geo}", 'warn', print_debug)
                import traceback
                traceback.print_exc()
                mr_por_estado_raw = {}  # Dejar vacío y usar FALLBACK después
        elif coaliciones_detectadas and usar_coaliciones:
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
            mr_por_estado_raw = {}  # 📍 Tracking geográfico: {estado: {partido: count}}
            distritos_procesados = 0
            
            # Helper para asignar MR tanto nacional como por estado
            def asignar_mr_distrito(partido, estado):
                """Incrementa contador MR nacional y por estado para un partido"""
                mr_raw[partido] = mr_raw.get(partido, 0) + 1
                if estado not in mr_por_estado_raw:
                    mr_por_estado_raw[estado] = {p: 0 for p in partidos_base}
                mr_por_estado_raw[estado][partido] = mr_por_estado_raw[estado].get(partido, 0) + 1

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
                                    asignar_mr_distrito(ppn_gp, entidad)
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
                                    asignar_mr_distrito(ppn_gp, entidad)
                                    distrito_procesado = True
                                    if print_debug:
                                        _maybe_log(f"{entidad}-{num_distrito}: FCM ganó -> acreditar a {ppn_gp}", 'info', print_debug)

                        # 3) Si solo hay un nominador y ganó ese partido -> acreditar a ese partido
                        if not distrito_procesado and len(nominadores_set) == 1:
                            solo = list(nominadores_set)[0]
                            if coalicion_ganadora == solo or (solo in partidos_base and coalicion_ganadora == solo):
                                if solo in partidos_base:
                                    asignar_mr_distrito(solo, entidad)
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
                                    asignar_mr_distrito(partido_ganador, entidad)
                                    distrito_procesado = True
                                    if print_debug:
                                        _maybe_log(f"{entidad}-{num_distrito}: acreditar a dominante {partido_ganador}", 'warn', print_debug)

                            # Si no hay registro en siglado o no aplica, usar fallback por votos dentro de la coalición
                            if not distrito_procesado:
                                partidos_coalicion_list = partidos_de_col(coalicion_ganadora)
                                votos_coalicion = {p: float(distrito.get(p,0) or 0) for p in partidos_coalicion_list if p in partidos_base}
                                if votos_coalicion:
                                    partido_fallback = max(votos_coalicion, key=votos_coalicion.get)
                                    asignar_mr_distrito(partido_fallback, entidad)
                                    distrito_procesado = True
                                    if print_debug:
                                        _maybe_log(f"Distrito {entidad}-{num_distrito}: {coalicion_ganadora} -> {partido_fallback} (por votos coalición)", 'warn', print_debug)
                    elif not is_coalition_win:
                        # Aunque la suma ponderada sugiera una coalición, la columna de coalición
                        # no existía o no tenía votos en el parquet: tratar como partido individual
                        if coalicion_ganadora in partidos_base:
                            asignar_mr_distrito(coalicion_ganadora, entidad)
                            distrito_procesado = True
                            if print_debug and len(mr_raw) <= 5:
                                _maybe_log(f"Distrito {entidad}-{num_distrito}: {coalicion_ganadora} (individual, sin columna de coalición)", 'debug', print_debug)
                        else:
                            # Fallback conservador: asignar al partido con más votos entre partidos base
                            votos_ind = {p: float(distrito.get(p,0) or 0) for p in partidos_base}
                            if votos_ind:
                                ganador_ind = max(votos_ind, key=votos_ind.get)
                                asignar_mr_distrito(ganador_ind, entidad)
                                distrito_procesado = True
                                if print_debug:
                                    _maybe_log(f"Distrito {entidad}-{num_distrito}: {ganador_ind} (fallback sin columna de coalición)", 'debug', print_debug)
                    else:
                        # Partido individual ganó directamente
                        if coalicion_ganadora in partidos_base:
                            asignar_mr_distrito(coalicion_ganadora, entidad)
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
                        asignar_mr_distrito(ganador_individual, entidad)
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
            # CALCULAR MR SIN COALICIONES: ganador directo por votos individuales
            # NO usar siglado (que ya tiene el convenio de coalición aplicado)
            # Recalcular ganadores distrito por distrito usando SOLO votos de partidos individuales
            if print_debug:
                if coaliciones_detectadas and not usar_coaliciones:
                    _maybe_log("Coaliciones detectadas pero DESACTIVADAS - recalculando MR por votos individuales", 'info', print_debug)
                else:
                    _maybe_log("Calculando MR por partido individual (sin coaliciones)", 'debug', print_debug)
            
            # Calcular ganador por distrito usando solo votos de partidos base
            mr_raw = {}
            for _, distrito in recomposed.iterrows():
                # Obtener votos de cada partido en este distrito
                votos_distrito = {}
                for partido in partidos_base:
                    votos_distrito[partido] = float(distrito.get(partido, 0) or 0)
                
                # El partido con más votos gana el distrito
                if votos_distrito:
                    ganador = max(votos_distrito, key=votos_distrito.get)
                    mr_raw[ganador] = mr_raw.get(ganador, 0) + 1
            
            # Asegurar que todos los partidos base están representados
            mr_aligned = {p: int(mr_raw.get(p, 0)) for p in partidos_base}
            indep_mr = 0
            
            if print_debug:
                _maybe_log(f"MR sin coaliciones calculado: {mr_aligned}", 'info', print_debug)
                total_mr = sum(mr_aligned.values())
                _maybe_log(f"Total distritos MR procesados: {total_mr}", 'info', print_debug)
        
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

                # IMPORTANTE: Preparar parámetros de límites de forma INDEPENDIENTE
                # Los dos sistemas de límites son distintos y deben funcionar por separado:
                # 1. max_seats_per_party: Tope ABSOLUTO de escaños (ej: max 300 escaños)
                # 2. sobrerrepresentacion: Cláusula RELATIVA % (ej: max +8% sobre votos)
                #
                # Si aplicar_topes=False: Desactivar AMBOS límites
                # Si aplicar_topes=True: Aplicar solo los que estén definidos (no usar defaults)
                
                if aplicar_topes:
                    # Convertir sobrerrepresentacion a max_pp
                    # Si sobrerrepresentacion=None, NO aplicar cláusula % (pasar None)
                    max_pp_value = (sobrerrepresentacion / 100.0) if sobrerrepresentacion is not None else None
                    # Si max_seats_per_party=None, NO aplicar tope absoluto
                    max_seats_per_party_value = int(max_seats_per_party) if max_seats_per_party is not None else None
                else:
                    # aplicar_topes=False: Desactivar TODOS los límites
                    max_pp_value = None
                    max_seats_per_party_value = None
                
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
                    max_pp=max_pp_value,  # None = NO aplicar cláusula de sobrerrepresentación
                    max_seats_per_party=max_seats_per_party_value,  # None = NO aplicar tope absoluto
                    apply_caps=aplicar_topes,  # Activar/desactivar sistema completo
                    quota_method=quota_method,
                    divisor_method=divisor_method,
                    seed=seed,
                    partidos_base=partidos_base,
                    mr_son_manuales=False,  # RP-only: no aplica MR manuales
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
                    _maybe_log(f"usar_coaliciones={usar_coaliciones}, coaliciones_detectadas={bool(coaliciones_detectadas)}", 'debug', print_debug)
                # Ajustar MR calculado para que sume exactamente mr_seats
                total_mr_actual = sum(mr_aligned.values())
                
                # 🔥 CRÍTICO: NO ajustar si los MR son manuales del frontend (mr_ganados_geograficos)
                # El frontend ya envió los valores exactos que quiere, NO deben reescalarse
                if mr_son_manuales:
                    if print_debug:
                        _maybe_log(f"✅ MR manuales del frontend ({total_mr_actual}) - NO se reescalarán", 'info', print_debug)
                        _maybe_log(f"   Valores recibidos: {mr_aligned}", 'debug', print_debug)
                    # Actualizar mr_seats para reflejar el total real de MR manuales
                    # Esto permite que el resto del código funcione correctamente
                    mr_seats = total_mr_actual
                    if print_debug:
                        _maybe_log(f"   mr_seats actualizado a {mr_seats} para coincidir con MR manuales", 'debug', print_debug)
                elif total_mr_actual != mr_seats:
                    if print_debug:
                        _maybe_log(f"Ajustando MR de {total_mr_actual} a {mr_seats}", 'debug', print_debug)
                    
                    # CRÍTICO: Si usar_coaliciones=False, NO usar scale_siglado porque volvería
                    # al siglado original (que tiene convenio de coalición aplicado).
                    # En su lugar, escalar proporcionalmente los MR recalculados.
                    if not usar_coaliciones and coaliciones_detectadas:
                        if print_debug:
                            _maybe_log(f"Escalando MR recalculados sin coalición (no usar siglado)", 'info', print_debug)
                            _maybe_log(f"MR antes de escalar: {mr_aligned}", 'debug', print_debug)
                        # Escalado proporcional simple de los MR recalculados
                        factor = mr_seats / total_mr_actual if total_mr_actual > 0 else 0
                        mr_ajustado = {p: int(round(mr_aligned.get(p, 0) * factor)) for p in partidos_base}
                        diferencia = mr_seats - sum(mr_ajustado.values())
                        if print_debug:
                            _maybe_log(f"Factor de escalado: {factor:.4f}", 'debug', print_debug)
                            _maybe_log(f"MR después de escalar (antes de ajuste): {mr_ajustado}", 'debug', print_debug)
                            _maybe_log(f"Diferencia a ajustar: {diferencia}", 'debug', print_debug)
                        if diferencia != 0:
                            partidos_ordenados = sorted(partidos_base, key=lambda x: mr_ajustado[x], reverse=True)
                            for i in range(abs(diferencia)):
                                if diferencia > 0:
                                    mr_ajustado[partidos_ordenados[i % len(partidos_ordenados)]] += 1
                                else:
                                    if mr_ajustado[partidos_ordenados[i % len(partidos_ordenados)]] > 0:
                                        mr_ajustado[partidos_ordenados[i % len(partidos_ordenados)]] -= 1
                        mr_aligned = mr_ajustado
                        if print_debug:
                            _maybe_log(f"MR final después de ajuste: {mr_aligned}", 'info', print_debug)
                        scaled_info = {
                            'method': 'proportional_scaling_no_coalition',
                            'note': 'MR escalados desde recalculo sin coalicion'
                        }
                    # Intentar escalado estratificado determinista usando scale_siglado
                    elif total_mr_actual > 0:
                        if print_debug:
                            _maybe_log(f"Usando scale_siglado para ajuste MR", 'debug', print_debug)
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
            # NOTA: Ya NO forzamos sobrerrepresentacion=8.0 cuando es None
            # Esto permite que los parámetros funcionen independientemente
            # if sobrerrepresentacion is None:
            #     sobrerrepresentacion = 8.0

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

                # IMPORTANTE: Preparar parámetros de límites de forma INDEPENDIENTE
                # Los dos sistemas de límites son distintos y deben funcionar por separado:
                # 1. max_seats_per_party: Tope ABSOLUTO de escaños (ej: max 300 escaños)
                # 2. sobrerrepresentacion: Cláusula RELATIVA % (ej: max +8% sobre votos)
                #
                # Si aplicar_topes=False: Desactivar AMBOS límites
                # Si aplicar_topes=True: Aplicar solo los que estén definidos (no usar defaults)
                
                if aplicar_topes:
                    # Convertir sobrerrepresentacion a max_pp
                    # Si sobrerrepresentacion=None, NO aplicar cláusula % (pasar None)
                    max_pp_value = (sobrerrepresentacion / 100.0) if sobrerrepresentacion is not None else None
                    # Si max_seats_per_party=None, NO aplicar tope absoluto
                    max_seats_per_party_value = int(max_seats_per_party) if max_seats_per_party is not None else None
                else:
                    # aplicar_topes=False: Desactivar TODOS los límites
                    max_pp_value = None
                    max_seats_per_party_value = None
                
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
                    max_pp=max_pp_value,  # None = NO aplicar cláusula de sobrerrepresentación
                    max_seats_per_party=max_seats_per_party_value,  # None = NO aplicar tope absoluto
                    apply_caps=aplicar_topes,  # Activar/desactivar sistema completo
                    quota_method=quota_method,
                    divisor_method=divisor_method,
                    seed=seed,
                    partidos_base=partidos_base,
                    mr_son_manuales=mr_son_manuales,  # 🔥 CRÍTICO: Preservar MR manuales del frontend
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

            # NOTA: El límite de sobrerrepresentación YA fue aplicado dentro de asignadip_v2
            # cuando apply_caps=True. La función aplicar_topes_nacionales se encarga de:
            # 1. Aplicar el tope +8pp sobre el TOTAL de escaños (MR+RP, o solo MR, o solo RP)
            # 2. Aplicar el tope de 300 escaños máximo por partido
            # 3. Redistribuir los escaños sobrantes a partidos no capados
            # Por lo tanto, NO es necesario aplicar el límite aquí nuevamente.
            if print_debug:
                if aplicar_topes:
                    _maybe_log(f"Topes constitucionales ya aplicados en asignadip_v2", 'debug', print_debug)
                else:
                    _maybe_log(f"aplicar_topes=False: sin límites constitucionales", 'info', print_debug)
        
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
        
        # ===============================================
        # PRIMERA MINORÍA (PM): Calcular y ajustar MR
        # ===============================================
        pm_dict = {p: 0 for p in partidos_base}  # Default: sin PM
        
        if pm_seats is not None and pm_seats > 0:
            # CRÍTICO: Cuando hay PM, NO debe haber RP (son mutuamente excluyentes)
            # Limpiar RP dict para evitar que se sumen escaños incorrectos
            rp_dict = {p: 0 for p in partidos_base}
            if print_debug:
                _maybe_log(f"[PM] Calculando primera minoría: {pm_seats} escaños", 'debug', print_debug)
            
            try:
                # Llamar a la función que simula PM por runnerup
                pm_dict = _simulate_pm_by_runnerup(
                    recomposed_df=recomposed,  # Usar 'recomposed' que es la variable correcta
                    pm_seats=pm_seats,
                    partidos=partidos_base
                )
                
                if print_debug:
                    _maybe_log(f"[PM] Escaños PM calculados: {pm_dict}", 'debug', print_debug)
                    _maybe_log(f"[PM] Total PM: {sum(pm_dict.values())}", 'debug', print_debug)
                
                # ===============================================
                # VERIFICACIÓN DE TOPES CON PM (SOLO REPORTE)
                # ===============================================
                # CRÍTICO: PM NO SE AJUSTA, es resultado de victorias de segunda fuerza
                # Si MR + PM excede el tope, se REPORTA pero NO se corrige
                # Solo RP puede ajustarse para respetar el tope
                if aplicar_topes and print_debug:
                    # Calcular porcentajes de votos para reporte
                    total_votos = sum(votos_partido.values()) if 'votos_partido' in locals() else 1
                    
                    for p in partidos_base:
                        mr = mr_dict.get(p, 0)
                        pm = pm_dict.get(p, 0)
                        total_sin_rp = mr + pm
                        
                        if total_sin_rp > 0:
                            votos_p = votos_partido.get(p, 0) if 'votos_partido' in locals() else 0
                            votos_pct = votos_p / total_votos if total_votos > 0 else 0.0
                            
                            # Calcular tope
                            if votos_pct >= umbral:
                                if sobrerrepresentacion is not None:
                                    cap_sobrerep = int(np.floor((votos_pct + sobrerrepresentacion) * (S if S else 400)))
                                else:
                                    cap_sobrerep = S if S else 400
                                
                                if max_seats_per_party is not None:
                                    cap = min(cap_sobrerep, max_seats_per_party)
                                else:
                                    cap = cap_sobrerep
                                
                                # Verificar si MR + PM ya excede el tope
                                if total_sin_rp > cap:
                                    _maybe_log(f"[PM TOPES] {p}: MR+PM={total_sin_rp} EXCEDE tope {cap} (votos={votos_pct:.2%})", 'warning', print_debug)
                                    _maybe_log(f"[PM TOPES] {p}: Esta sobrerrepresentación es PERMITIDA (victorias directas)", 'info', print_debug)
                
                # PM se añade al resultado final (SIN MODIFICAR)
                # IMPORTANTE: Cuando mr_seats está configurado explícitamente, NO reducir MR
                # porque el caller ya especificó cuántos MR quiere (ej: mr_seats=300, pm_seats=100)
                # Solo reducir MR si NO fue especificado explícitamente
                
                # Verificar si mr_seats fue especificado explícitamente
                mr_seats_explicito = mr_seats is not None and mr_seats > 0
                
                if not mr_seats_explicito:
                    # Solo ajustar MR si NO fue especificado (caso automático)
                    total_mr_original = sum(mr_dict.values())
                    if total_mr_original > 0:
                        # Reducir MR proporcionalmente para hacer espacio a PM
                        total_pm = sum(pm_dict.values())
                        mr_objetivo = max(0, total_mr_original - total_pm)
                        
                        # Calcular factor de reducción
                        factor = mr_objetivo / total_mr_original if total_mr_original > 0 else 0
                        
                        # Aplicar reducción proporcional a todos los partidos
                        mr_dict_ajustado = {}
                        for partido in partidos_base:
                            mr_original = mr_dict.get(partido, 0)
                            mr_dict_ajustado[partido] = int(mr_original * factor)
                        
                        # Ajustar residuos para llegar exactamente a mr_objetivo
                        total_ajustado = sum(mr_dict_ajustado.values())
                        diferencia = mr_objetivo - total_ajustado
                        if diferencia != 0:
                            # Distribuir diferencia a los partidos más grandes
                            partidos_ordenados = sorted(mr_dict_ajustado.items(), key=lambda x: x[1], reverse=True)
                            for i in range(abs(int(diferencia))):
                                if i < len(partidos_ordenados):
                                    partido = partidos_ordenados[i][0]
                                    mr_dict_ajustado[partido] += 1 if diferencia > 0 else -1
                        
                        mr_dict = mr_dict_ajustado
                        
                        if print_debug:
                            _maybe_log(f"[PM] MR ajustado de {total_mr_original} a {sum(mr_dict.values())} para hacer espacio a {sum(pm_dict.values())} PM", 'debug', print_debug)
                else:
                    # MR fue especificado explícitamente, NO reducir
                    if print_debug:
                        _maybe_log(f"[PM] MR={mr_seats} especificado explícitamente, NO se reduce para PM", 'debug', print_debug)
                
                # ACTUALIZAR TOT: incluir PM en el total
                tot_dict = {p: int(mr_dict.get(p, 0) + pm_dict.get(p, 0) + rp_dict.get(p, 0)) for p in partidos_base}
                
                if print_debug:
                    _maybe_log(f"[PM] Totales actualizados con PM: {tot_dict}", 'debug', print_debug)
                    _maybe_log(f"[PM] Suma total: {sum(tot_dict.values())}", 'debug', print_debug)
                    
            except Exception as e:
                if print_debug:
                    _maybe_log(f"[PM] Error calculando PM: {e}", 'error', print_debug)
                # En caso de error, mantener pm_dict vacío
                pm_dict = {p: 0 for p in partidos_base}
        
        try:
            if 'scaled_info' in locals() and scaled_info is not None:
                meta_out['scaled_info'] = scaled_info
        except Exception:
            pass

        # 📊 Desglosar MR FINALES por estado (para tabla geográfica del frontend)
        # IMPORTANTE: Usar mr_por_estado_raw que ya capturó la lógica correcta de coaliciones
        # durante el procesamiento de distritos (líneas 1370-1560)
        mr_por_estado_partido = {}
        distritos_por_estado = {}
        
        try:
            # Usar el tracking geográfico que ya se construyó durante el cálculo de MR
            if 'mr_por_estado_raw' in locals() and mr_por_estado_raw:
                mr_por_estado_partido = mr_por_estado_raw.copy()
                _maybe_log(f"[mr_por_estado] Usando mr_por_estado_raw (tracking geográfico)", 'debug', print_debug)
                
                # 🔥 CRÍTICO: Escalar mr_por_estado cuando mr_seats < total histórico
                # Esto pasa en modo personalizado cuando el usuario pide 64 MR en lugar de 300
                total_historico = sum(sum(partidos.values()) for partidos in mr_por_estado_partido.values())
                if mr_seats and total_historico > 0 and mr_seats != total_historico:
                    _maybe_log(f"[mr_por_estado] 📊 Escalando distribución geográfica: {total_historico} → {mr_seats} MR", 'info', print_debug)
                    
                    # Escalar proporcionalmente manteniendo distribución geográfica
                    import math
                    mr_por_estado_escalado = {}
                    celdas_con_residuos = []  # Lista de (estado, partido, residuo)
                    
                    for estado, partidos in mr_por_estado_partido.items():
                        mr_por_estado_escalado[estado] = {}
                        for partido, mr_hist in partidos.items():
                            # Calcular proporción escalada
                            mr_escalado_exacto = (mr_hist / total_historico) * mr_seats
                            mr_floor = math.floor(mr_escalado_exacto)
                            residuo = mr_escalado_exacto - mr_floor
                            
                            mr_por_estado_escalado[estado][partido] = mr_floor
                            
                            # Guardar residuo para largest remainder
                            if residuo > 0:
                                celdas_con_residuos.append((estado, partido, residuo))
                    
                    # Distribuir residuos usando largest remainder
                    total_asignado = sum(sum(partidos.values()) for partidos in mr_por_estado_escalado.values())
                    faltantes = mr_seats - total_asignado
                    
                    if faltantes > 0:
                        # Ordenar celdas por residuo descendente
                        celdas_con_residuos.sort(key=lambda x: x[2], reverse=True)
                        
                        # Asignar los faltantes a las celdas con mayor residuo
                        for i in range(min(faltantes, len(celdas_con_residuos))):
                            estado, partido, _ = celdas_con_residuos[i]
                            mr_por_estado_escalado[estado][partido] += 1
                    
                    # Reemplazar con versión escalada
                    mr_por_estado_partido = mr_por_estado_escalado
                    
                    if print_debug:
                        total_final = sum(sum(partidos.values()) for partidos in mr_por_estado_partido.values())
                        _maybe_log(f"[mr_por_estado] ✅ Escalado completo: {total_final}/{mr_seats} MR", 'debug', print_debug)
                
                # Calcular distritos por estado
                if 'recomposed' in locals() and recomposed is not None and 'ENTIDAD' in recomposed.columns:
                    for estado in recomposed['ENTIDAD'].unique():
                        # Mantener el nombre completo (sin convertir a abreviación todavía)
                        distritos_por_estado[estado] = len(recomposed[recomposed['ENTIDAD'] == estado])
                    
                    # 🔥 CRÍTICO: Escalar distritos_por_estado cuando mr_seats < total histórico (300)
                    # Esto es necesario para planes personalizados (ej: 64 MR en lugar de 300)
                    total_historico_distritos = sum(distritos_por_estado.values())
                    if mr_seats and total_historico_distritos > 0 and mr_seats != total_historico_distritos:
                        _maybe_log(f"[distritos_por_estado] 📊 Escalando totales: {total_historico_distritos} → {mr_seats} MR", 'info', print_debug)
                        
                        import math
                        distritos_escalados = {}
                        estados_con_residuos = []
                        
                        for estado, distritos_hist in distritos_por_estado.items():
                            # Calcular proporción escalada
                            distritos_escalado_exacto = (distritos_hist / total_historico_distritos) * mr_seats
                            distritos_floor = math.floor(distritos_escalado_exacto)
                            residuo = distritos_escalado_exacto - distritos_floor
                            
                            distritos_escalados[estado] = distritos_floor
                            
                            # Guardar residuo para largest remainder
                            if residuo > 0:
                                estados_con_residuos.append((estado, residuo))
                        
                        # Distribuir residuos usando largest remainder
                        total_asignado = sum(distritos_escalados.values())
                        faltantes = mr_seats - total_asignado
                        
                        if faltantes > 0:
                            # Ordenar estados por residuo descendente
                            estados_con_residuos.sort(key=lambda x: x[1], reverse=True)
                            
                            # Asignar los faltantes a los estados con mayor residuo
                            for i in range(min(faltantes, len(estados_con_residuos))):
                                estado, _ = estados_con_residuos[i]
                                distritos_escalados[estado] += 1
                        
                        # Reemplazar con versión escalada
                        distritos_por_estado = distritos_escalados
                        
                        if print_debug:
                            total_final_distritos = sum(distritos_por_estado.values())
                            _maybe_log(f"[distritos_por_estado] ✅ Escalado completo: {total_final_distritos}/{mr_seats} distritos totales", 'debug', print_debug)
                
                # 🔥 CRÍTICO: RECONSTRUIR mr_por_estado usando EXACTAMENTE mr_dict (seat_chart)
                # Esto asegura que la tabla de distritos coincida EXACTAMENTE con el seat_chart
                total_mr_desglosado = sum(sum(partidos.values()) for partidos in mr_por_estado_partido.values())
                total_mr_dict = sum(mr_dict.values()) if mr_dict else 0
                
                # Verificar si mr_dict tiene valores diferentes a mr_por_estado_partido
                mr_dict_actual = {}
                for estado, partidos_estado in mr_por_estado_partido.items():
                    for partido, mr in partidos_estado.items():
                        mr_dict_actual[partido] = mr_dict_actual.get(partido, 0) + mr
                
                necesita_reconstruccion = False
                if mr_dict:
                    for partido, mr_final in mr_dict.items():
                        if mr_final != mr_dict_actual.get(partido, 0):
                            necesita_reconstruccion = True
                            break
                
                if necesita_reconstruccion and mr_dict:
                    _maybe_log(f"[mr_por_estado] 🔄 RECONSTRUYENDO con valores EXACTOS de seat_chart", 'info', print_debug)
                    
                    # ESTRATEGIA: Distribuir los MR de cada partido entre sus estados con mayor fuerza histórica
                    import math
                    mr_por_estado_final = {estado: {p: 0 for p in partidos_base} for estado in mr_por_estado_partido.keys()}
                    
                    for partido, mr_final_partido in mr_dict.items():
                        if mr_final_partido == 0:
                            continue
                        
                        # Calcular "fuerza" del partido en cada estado (basado en mr_por_estado_partido histórico)
                        fuerza_por_estado = []
                        total_fuerza = 0
                        
                        for estado, partidos_estado in mr_por_estado_partido.items():
                            fuerza = partidos_estado.get(partido, 0)
                            if fuerza > 0:
                                fuerza_por_estado.append((estado, fuerza))
                                total_fuerza += fuerza
                        
                        if total_fuerza == 0:
                            # Si el partido no tiene fuerza histórica, distribuir equitativamente
                            estados = list(mr_por_estado_partido.keys())
                            mr_por_estado_base = mr_final_partido // len(estados)
                            sobrantes = mr_final_partido % len(estados)
                            
                            for i, estado in enumerate(estados):
                                mr_por_estado_final[estado][partido] = mr_por_estado_base + (1 if i < sobrantes else 0)
                        else:
                            # Distribuir proporcionalmente a la fuerza histórica
                            asignados = {}
                            residuos = []
                            
                            for estado, fuerza in fuerza_por_estado:
                                proporcion_exacta = (fuerza / total_fuerza) * mr_final_partido
                                mr_floor = math.floor(proporcion_exacta)
                                residuo = proporcion_exacta - mr_floor
                                
                                asignados[estado] = mr_floor
                                if residuo > 0:
                                    residuos.append((estado, residuo))
                            
                            # Distribuir residuos (largest remainder)
                            total_asignado = sum(asignados.values())
                            faltantes = mr_final_partido - total_asignado
                            
                            if faltantes > 0 and residuos:
                                residuos.sort(key=lambda x: x[1], reverse=True)
                                for i in range(min(faltantes, len(residuos))):
                                    estado, _ = residuos[i]
                                    asignados[estado] += 1
                            
                            # Aplicar asignaciones
                            for estado, mr_asignado in asignados.items():
                                mr_por_estado_final[estado][partido] = mr_asignado
                    
                    mr_por_estado_partido = mr_por_estado_final
                    total_mr_desglosado = sum(sum(p.values()) for p in mr_por_estado_partido.values())
                
                if print_debug:
                    _maybe_log(f"[mr_por_estado] ✅ Desglosados {total_mr_desglosado}/{total_mr_dict} MR en {len(mr_por_estado_partido)} estados", 'debug', print_debug)
                    
                    # Validación: verificar que cada estado no exceda sus distritos
                    for estado, partidos in mr_por_estado_partido.items():
                        total_estado = sum(partidos.values())
                        max_distritos = distritos_por_estado.get(estado, 0)
                        if total_estado > max_distritos:
                            _maybe_log(f"[mr_por_estado] ⚠️  {estado}: {total_estado} MR > {max_distritos} distritos!", 'error', print_debug)
                
                # 🔥 CRÍTICO: Ajustar mr_por_estado para que cada estado respete su límite de distritos
                # Esto previene casos como Campeche con MC=1 + MORENA=2 = 3 cuando solo tiene 1 distrito
                for estado, partidos_estado in list(mr_por_estado_partido.items()):
                    total_estado = sum(partidos_estado.values())
                    max_distritos = distritos_por_estado.get(estado, 0)
                    
                    # Caso especial: Estado con 0 distritos escalados
                    if total_estado > 0 and max_distritos == 0:
                        _maybe_log(f"[mr_por_estado] 🔧 AJUSTANDO {estado}: {total_estado} MR → 0 distritos (escalado a 0)", 'info', print_debug)
                        mr_por_estado_partido[estado] = {partido: 0 for partido in partidos_estado.keys()}
                        continue
                    
                    # Caso normal: Estado excede su límite de distritos
                    if total_estado > max_distritos and max_distritos > 0:
                        _maybe_log(f"[mr_por_estado] 🔧 AJUSTANDO {estado}: {total_estado} MR → {max_distritos} distritos (exceso: {total_estado - max_distritos})", 'info', print_debug)
                        
                        # Estrategia: Reducir proporcionalmente manteniendo distribución relativa
                        import math
                        partidos_ajustados = {}
                        partidos_con_residuos = []
                        
                        for partido, mr_actual in partidos_estado.items():
                            if mr_actual == 0:
                                partidos_ajustados[partido] = 0
                                continue
                            
                            # Calcular proporción ajustada
                            mr_ajustado_exacto = (mr_actual / total_estado) * max_distritos
                            mr_floor = math.floor(mr_ajustado_exacto)
                            residuo = mr_ajustado_exacto - mr_floor
                            
                            partidos_ajustados[partido] = mr_floor
                            
                            if residuo > 0:
                                partidos_con_residuos.append((partido, residuo))
                        
                        # Distribuir residuos para llegar exactamente a max_distritos
                        total_asignado = sum(partidos_ajustados.values())
                        faltantes = max_distritos - total_asignado
                        
                        if faltantes > 0 and partidos_con_residuos:
                            partidos_con_residuos.sort(key=lambda x: x[1], reverse=True)
                            for i in range(min(faltantes, len(partidos_con_residuos))):
                                partido, _ = partidos_con_residuos[i]
                                partidos_ajustados[partido] += 1
                        
                        # Reemplazar con versión ajustada
                        mr_por_estado_partido[estado] = partidos_ajustados
                        
                        if print_debug:
                            nuevo_total = sum(partidos_ajustados.values())
                            _maybe_log(f"[mr_por_estado]   ✅ {estado} ajustado: {nuevo_total}/{max_distritos} distritos", 'debug', print_debug)
                            for partido, mr in sorted(partidos_ajustados.items(), key=lambda x: x[1], reverse=True):
                                if mr > 0:
                                    _maybe_log(f"[mr_por_estado]      {partido}: {partidos_estado.get(partido, 0)} → {mr}", 'debug', print_debug)
            
            # FALLBACK: Si no hay mr_por_estado_raw, usar distribución proporcional pura
            elif mr_dict and mr_seats and mr_seats > 0:
                _maybe_log("[mr_por_estado] FALLBACK: Distribuyendo MR finales por estado usando Hare", 'info', print_debug)
                _maybe_log(f"[mr_por_estado] mr_dict={mr_dict}, mr_seats={mr_seats}", 'debug', print_debug)
                if print_debug:
                    _maybe_log("[mr_por_estado] Distribuyendo MR finales por estado usando Hare", 'debug', print_debug)
                    _maybe_log(f"[mr_por_estado] MR finales a distribuir: {mr_dict}", 'debug', print_debug)
                
                try:
                    from redistritacion.modulos.reparto_distritos import repartir_distritos_hare
                    from redistritacion.modulos.distritacion import cargar_secciones_ine
                    
                    # Cargar población por estado
                    secciones = cargar_secciones_ine()
                    poblacion_por_estado = secciones.groupby('ENTIDAD')['POBTOT'].sum().to_dict()
                    
                    # Repartir distritos usando Hare
                    asignacion_distritos = repartir_distritos_hare(
                        poblacion_estados=poblacion_por_estado,
                        n_distritos=mr_seats,
                        piso_constitucional=2
                    )
                    
                    # Mapeo de IDs a nombres
                    estado_nombres = {
                        1: 'AGUASCALIENTES', 2: 'BAJA CALIFORNIA', 3: 'BAJA CALIFORNIA SUR',
                        4: 'CAMPECHE', 5: 'CHIAPAS', 6: 'CHIHUAHUA', 7: 'COAHUILA',
                        8: 'COLIMA', 9: 'CIUDAD DE MEXICO', 10: 'DURANGO', 11: 'GUANAJUATO',
                        12: 'GUERRERO', 13: 'HIDALGO', 14: 'JALISCO', 15: 'MEXICO',
                        16: 'MICHOACAN', 17: 'MORELOS', 18: 'NAYARIT', 19: 'NUEVO LEON',
                        20: 'OAXACA', 21: 'PUEBLA', 22: 'QUERETARO', 23: 'QUINTANA ROO',
                        24: 'SAN LUIS POTOSI', 25: 'SINALOA', 26: 'SONORA', 27: 'TABASCO',
                        28: 'TAMAULIPAS', 29: 'TLAXCALA', 30: 'VERACRUZ', 31: 'YUCATAN',
                        32: 'ZACATECAS'
                    }
                    
                    # CRÍTICO: Usar mr_dict (MR finales) en lugar de mr_ganados_geograficos
                    # mr_dict ya tiene los topes aplicados y es lo que se muestra en seat_chart
                    total_mr_nacional = sum(mr_dict.values())
                    
                    if print_debug:
                        _maybe_log(f"[mr_por_estado] Total MR nacional (finales): {total_mr_nacional}", 'debug', print_debug)
                    
                    # PASO 1: Distribuir usando floor (parte entera) y acumular residuos por partido
                    import math
                    residuos_por_partido = {p: 0.0 for p in partidos_base}  # Acumular residuos
                    
                    # Calcular población total para proporción
                    poblacion_total = sum(poblacion_por_estado.values())
                    
                    for estado_id, nombre_estado in estado_nombres.items():
                        # Usar abreviación en lugar de nombre completo
                        abrev_estado = NOMBRE_ESTADO_A_ABREV.get(nombre_estado, nombre_estado)
                        
                        distritos_totales = asignacion_distritos.get(estado_id, 0)
                        distritos_por_estado[abrev_estado] = distritos_totales
                        mr_por_estado_partido[abrev_estado] = {p: 0 for p in partidos_base}
                        
                        if total_mr_nacional > 0 and distritos_totales > 0 and poblacion_total > 0:
                            poblacion_estado = poblacion_por_estado.get(estado_id, 0)
                            proporcion_poblacional = poblacion_estado / poblacion_total
                            
                            for partido in partidos_base:
                                mr_partido_nacional = mr_dict.get(partido, 0)
                                # Calcular proporción exacta usando población (no total_mr para evitar floor=0)
                                proporcion_exacta = mr_partido_nacional * proporcion_poblacional
                                # Asignar parte entera
                                mr_asignado = math.floor(proporcion_exacta)
                                mr_por_estado_partido[abrev_estado][partido] = mr_asignado
                                # Acumular residuo para este partido
                                residuos_por_partido[partido] += (proporcion_exacta - mr_asignado)
                            
                            # Ajustar para que este estado sume exactamente distritos_totales
                            suma_actual = sum(mr_por_estado_partido[abrev_estado].values())
                            if suma_actual != distritos_totales:
                                # Método Hare: dar residuos a partidos con mayor fracción EN ESTE ESTADO
                                diferencia = distritos_totales - suma_actual
                                
                                if diferencia > 0:
                                    # Agregar distritos: ordenar por mayor residuo
                                    partidos_ordenados = sorted(
                                        partidos_base,
                                        key=lambda p: (mr_dict.get(p, 0) * proporcion_poblacional) % 1,
                                        reverse=True
                                    )
                                    for i in range(abs(diferencia)):
                                        if i < len(partidos_ordenados):
                                            mr_por_estado_partido[abrev_estado][partidos_ordenados[i]] += 1
                                else:
                                    # Quitar distritos: SOLO de partidos con MR > 0 en este estado
                                    partidos_con_mr = [p for p in partidos_base if mr_por_estado_partido[abrev_estado][p] > 0]
                                    if partidos_con_mr:
                                        # Ordenar por menor residuo (quitar de los menos "merecidos")
                                        partidos_ordenados = sorted(
                                            partidos_con_mr,
                                            key=lambda p: (mr_dict.get(p, 0) * proporcion_poblacional) % 1,
                                            reverse=False
                                        )
                                        for i in range(min(abs(diferencia), len(partidos_ordenados))):
                                            if mr_por_estado_partido[abrev_estado][partidos_ordenados[i]] > 0:
                                                mr_por_estado_partido[abrev_estado][partidos_ordenados[i]] -= 1
                    
                    # PASO 2: Verificar y ajustar totales por partido para que coincidan con mr_dict
                    for partido in partidos_base:
                        total_asignado = sum(mr_por_estado_partido[estado].get(partido, 0) for estado in mr_por_estado_partido)
                        objetivo = mr_dict.get(partido, 0)
                        diferencia_partido = objetivo - total_asignado
                        
                        if diferencia_partido != 0 and print_debug:
                            _maybe_log(f"[mr_por_estado] Ajustando {partido}: {total_asignado} → {objetivo} (dif: {diferencia_partido:+d})", 'debug', print_debug)
                        
                        # Ajustar estado por estado hasta cuadrar
                        intentos_maximos = 1000  # Evitar loops infinitos
                        while diferencia_partido != 0 and intentos_maximos > 0:
                            intentos_maximos -= 1
                            
                            # Ordenar estados por mayor residuo acumulado de este partido
                            if diferencia_partido > 0:
                                # Necesitamos agregar: buscar estado donde este partido tiene más peso proporcional
                                # PERO que NO haya alcanzado su límite de distritos
                                estados_disponibles = [
                                    e for e in mr_por_estado_partido.keys()
                                    if sum(mr_por_estado_partido[e].values()) < distritos_por_estado.get(e, 0)
                                ]
                                
                                if not estados_disponibles:
                                    if print_debug:
                                        _maybe_log(f"[mr_por_estado] ⚠️  No hay estados disponibles para agregar MR de {partido} (todos en límite)", 'warn', print_debug)
                                    break  # No podemos agregar más sin violar límites
                                
                                estado_a_ajustar = max(
                                    estados_disponibles,
                                    key=lambda e: (mr_dict.get(partido, 0) * (poblacion_por_estado.get([k for k,v in estado_nombres.items() if v==e][0], 0) / poblacion_total)) if poblacion_total > 0 else 0
                                )
                                mr_por_estado_partido[estado_a_ajustar][partido] += 1
                                diferencia_partido -= 1
                            else:
                                # Necesitamos quitar: buscar estado donde este partido tiene MR asignados
                                estados_con_mr = [e for e in mr_por_estado_partido if mr_por_estado_partido[e][partido] > 0]
                                if not estados_con_mr:
                                    if print_debug:
                                        _maybe_log(f"[mr_por_estado] ⚠️  No hay estados con MR>0 para quitar de {partido}", 'warn', print_debug)
                                    break  # No hay de dónde quitar
                                # Elegir el estado con MR menor (para distribuir equitativamente)
                                estado_a_ajustar = min(estados_con_mr, key=lambda e: mr_por_estado_partido[e][partido])
                                # VALIDACIÓN: Asegurar que no se vuelva negativo
                                if mr_por_estado_partido[estado_a_ajustar][partido] > 0:
                                    mr_por_estado_partido[estado_a_ajustar][partido] -= 1
                                    diferencia_partido += 1
                                else:
                                    if print_debug:
                                        _maybe_log(f"[mr_por_estado] ⚠️  Intento de restar MR de {partido} en {estado_a_ajustar} con valor {mr_por_estado_partido[estado_a_ajustar][partido]}", 'warn', print_debug)
                                    break  # Evitar valores negativos
                    
                    if print_debug:
                        _maybe_log(f"[mr_por_estado] Distribución calculada con MR finales", 'debug', print_debug)
                        _maybe_log(f"[mr_por_estado] Total distritos: {sum(distritos_por_estado.values())}", 'debug', print_debug)
                    
                except Exception as e_geo:
                    if print_debug:
                        _maybe_log(f"[mr_por_estado] Error distribuyendo con mr_ganados_geograficos: {e_geo}", 'warn', print_debug)
                    # Caer al método tradicional (distrito por distrito)
                    mr_por_estado_partido = {}
                    distritos_por_estado = {}
            
            # 🔥 VALIDACIÓN CRÍTICA: Asegurar que totales por partido coincidan EXACTAMENTE con mr_dict
            if mr_por_estado_partido and mr_dict:
                for partido in partidos_base:
                    total_distribuido = sum(mr_por_estado_partido.get(estado, {}).get(partido, 0) for estado in mr_por_estado_partido)
                    mr_esperado = mr_dict.get(partido, 0)
                    
                    if total_distribuido != mr_esperado:
                        diferencia = mr_esperado - total_distribuido
                        
                        if print_debug:
                            _maybe_log(f"[mr_por_estado] ⚠️ AJUSTANDO {partido}: distribuido={total_distribuido}, esperado={mr_esperado}, diff={diferencia}", 'warn', print_debug)
                        
                        # Ajustar la diferencia distribuyendo/quitando de estados con mayor residuo
                        if diferencia > 0:
                            # Necesitamos agregar MR: buscar estados con capacidad disponible
                            for _ in range(abs(diferencia)):
                                # Buscar estado con espacio disponible (suma < max_distritos)
                                mejor_estado = None
                                for estado in mr_por_estado_partido:
                                    max_distritos = distritos_por_estado.get(estado, 0)
                                    suma_actual = sum(mr_por_estado_partido[estado].values())
                                    if suma_actual < max_distritos:
                                        mejor_estado = estado
                                        break
                                
                                if mejor_estado:
                                    mr_por_estado_partido[mejor_estado][partido] += 1
                                    if print_debug:
                                        _maybe_log(f"[mr_por_estado]   +1 MR de {partido} en {mejor_estado}", 'debug', print_debug)
                                else:
                                    if print_debug:
                                        _maybe_log(f"[mr_por_estado]   ❌ No hay estados disponibles para agregar +1 MR de {partido}", 'warn', print_debug)
                                    break
                        else:
                            # Necesitamos quitar MR: buscar estados con MR de este partido
                            for _ in range(abs(diferencia)):
                                # Buscar estado con MR de este partido
                                estados_con_mr = [e for e in mr_por_estado_partido if mr_por_estado_partido[e].get(partido, 0) > 0]
                                if estados_con_mr:
                                    # Quitar del estado con más MR de este partido
                                    mejor_estado = max(estados_con_mr, key=lambda e: mr_por_estado_partido[e][partido])
                                    mr_por_estado_partido[mejor_estado][partido] -= 1
                                    if print_debug:
                                        _maybe_log(f"[mr_por_estado]   -1 MR de {partido} en {mejor_estado}", 'debug', print_debug)
                                else:
                                    if print_debug:
                                        _maybe_log(f"[mr_por_estado]   ❌ No hay estados con MR de {partido} para quitar", 'warn', print_debug)
                                    break
            
            # Guardar en meta solo si hay datos (convertir claves a abreviaciones al final)
            if mr_por_estado_partido:
                # Convertir TODAS las claves a abreviaciones sin importar de dónde vengan
                mr_por_estado_final = {}
                for estado, partidos in mr_por_estado_partido.items():
                    abrev = NOMBRE_ESTADO_A_ABREV.get(estado, estado)
                    mr_por_estado_final[abrev] = partidos
                
                distritos_por_estado_final = {}
                for estado, total in distritos_por_estado.items():
                    abrev = NOMBRE_ESTADO_A_ABREV.get(estado, estado)
                    distritos_por_estado_final[abrev] = total
                
                meta_out['mr_por_estado'] = mr_por_estado_final
                meta_out['distritos_por_estado'] = distritos_por_estado_final
                
                if print_debug:
                    _maybe_log(f"[mr_por_estado] ✅ Datos guardados en meta con abreviaciones", 'debug', print_debug)
                    
        except Exception as e:
            if print_debug:
                _maybe_log(f"Error calculando mr_por_estado: {e}", 'warn', print_debug)

        return {
            'mr': mr_dict,
            'pm': pm_dict,  # Nueva clave para PM
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
            'pm': {p: 0 for p in partidos},  # Incluir PM en caso de error
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
