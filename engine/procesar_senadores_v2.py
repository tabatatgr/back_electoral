"""
Procesar Senadores V2 - Implementación basada en código R
Traducción directa del algoritmo R para garantizar equivalencia
"""

import pandas as pd
import numpy as np
import unicodedata
import re
import os
from typing import Dict, List, Tuple, Optional
from .recomposicion import recompose_coalitions, parties_for

def extraer_coaliciones_de_siglado(siglado_path):
    """
    Extrae las coaliciones del archivo siglado y devuelve un diccionario
    con la estructura: {'COALICION_NAME': ['PARTIDO1', 'PARTIDO2', ...]}
    """
    try:
        siglado = pd.read_csv(siglado_path, encoding='utf-8')
        
        # Verificar que tenga las columnas necesarias
        required_cols = ['COALICION', 'PARTIDO_ORIGEN']
        for col in required_cols:
            if col not in siglado.columns:
                return {}
        
        # Extraer coaliciones únicas y sus partidos
        coaliciones = {}
        
        # Agrupar por coalición y obtener partidos únicos
        for coalicion_name in siglado['COALICION'].unique():
            if pd.isna(coalicion_name) or coalicion_name.strip() == '':
                continue
                
            partidos_en_coalicion = siglado[siglado['COALICION'] == coalicion_name]['PARTIDO_ORIGEN'].unique()
            partidos_limpios = [p for p in partidos_en_coalicion if pd.notna(p) and p.strip() != '']
            
            if len(partidos_limpios) > 1:  # Solo considerar verdaderas coaliciones (más de 1 partido)
                coaliciones[coalicion_name] = sorted(partidos_limpios)
        
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

def norm_ascii_up(s: str) -> str:
    """Normalización ASCII mayúsculas"""
    if s is None: 
        return ""
    s = str(s).strip().upper()
    s = unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode("ASCII")
    s = re.sub(r"\s+", " ", s)
    return s

def normalize_entidad_ascii(x: str) -> str:
    """Normalización específica para entidades - idéntica al R"""
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
    
    if len(S) == 1 and S[0] in {"PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","NA","CI"}:
        return S[0]
    return None

def tokens_de_coalicion(coalicion: str, anio: int) -> List[str]:
    """Descompone coalición en partidos - basada en R"""
    if anio == 2018:
        if coalicion == "JUNTOS HAREMOS HISTORIA":
            return ["MORENA", "PT", "PES"]
        elif coalicion == "POR MEXICO AL FRENTE":
            return ["PAN", "PRD", "MC"]
        elif coalicion == "TODOS POR MEXICO":
            return ["PRI", "PVEM", "NA"]
    elif anio == 2024:
        if coalicion == "SIGAMOS HACIENDO HISTORIA":
            return ["MORENA", "PT", "PVEM"]
        elif coalicion == "FUERZA Y CORAZON POR MEXICO":
            return ["PAN", "PRI", "PRD"]
    
    if coalicion in ["MC","PAN","PRI","PRD","MORENA","PVEM","PT","PES","NA","CI"]:
        return [coalicion]
    return []

def partidos_de_col(col: str) -> List[str]:
    """Extrae partidos de nombre de columna - incluyendo coaliciones"""
    # Caso especial: coaliciones conocidas
    if col == "POR_MEXICO_AL_FRENTE":
        return ["PAN", "PRD", "MC"]
    elif col == "JUNTOS_HAREMOS_HISTORIA":
        return ["MORENA", "PT"]
    # Casos regulares: partidos separados por _
    else:
        return col.split("_")

def cols_candidaturas_anio_con_coaliciones(columnas: List[str], anio: int) -> List[str]:
    """Identifica columnas de candidaturas válidas incluyendo coaliciones"""
    if anio == 2018:
        partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","NA"]
    elif anio == 2024:
        partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA"]
    else:
        partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","NA","RSP","FXM","CI"]
    
    validas = []
    for col in columnas:
        # Caso 1: Columnas de partidos individuales o CI
        tokens = col.split("_")
        if len(tokens) > 0 and all(len(t) > 0 for t in tokens) and all(t in partidos_base + ["CI"] for t in tokens):
            validas.append(col)
        # Caso 2: Columnas de coaliciones (nombres que contienen FRENTE, HISTORIA, etc.)
        elif any(palabra in col.upper() for palabra in ['FRENTE', 'HISTORIA', 'MEXICO', 'HAREMOS', 'JUNTOS']):
            validas.append(col)
            print(f"[DEBUG] Coalición detectada: {col}")
    
    return validas

def cols_candidaturas_anio(columnas: List[str], anio: int) -> List[str]:
    """Identifica columnas de candidaturas válidas - traducida del R"""
    # Usar la nueva función que incluye coaliciones
    return cols_candidaturas_anio_con_coaliciones(columnas, anio)

def read_siglado_sen_long(csv_path: str) -> pd.DataFrame:
    """Lee archivo siglado senado - traducida del R"""
    gp = pd.read_csv(csv_path, encoding='utf-8')
    gp.columns = [c.upper() for c in gp.columns]
    
    # Manejar caso donde viene ENTIDAD_ASCII en lugar de ENTIDAD
    if 'ENTIDAD_ASCII' in gp.columns and 'ENTIDAD' not in gp.columns:
        gp['ENTIDAD'] = gp['ENTIDAD_ASCII']
    
    required = ["ENTIDAD", "COALICION", "FORMULA", "GRUPO_PARLAMENTARIO"]
    if not all(req in gp.columns for req in required):
        available = gp.columns.tolist()
        raise ValueError(f"El CSV de siglado debe tener: {', '.join(required)}. Disponibles: {available}")
    
    # Si no existe ENTIDAD_ASCII, crearla
    if 'ENTIDAD_ASCII' not in gp.columns:
        gp['ENTIDAD_ASCII'] = gp['ENTIDAD'].apply(normalize_entidad_ascii)
    
    gp['COALICION'] = gp['COALICION'].apply(norm_ascii_up)
    gp['FORMULA'] = gp['FORMULA'].astype(int)
    gp['GRUPO_PARLAMENTARIO'] = gp['GRUPO_PARLAMENTARIO'].apply(canonizar_siglado)
    
    if 'PARTIDO_ORIGEN' in gp.columns:
        gp['PARTIDO_ORIGEN'] = gp['PARTIDO_ORIGEN'].apply(canonizar_siglado)
    else:
        gp['PARTIDO_ORIGEN'] = None
    
    return gp[['ENTIDAD_ASCII', 'COALICION', 'FORMULA', 'GRUPO_PARLAMENTARIO', 'PARTIDO_ORIGEN']]

def gp_lookup(entidad: str, coalicion: str, formula: int, acred_row: pd.Series, 
              gp_long: pd.DataFrame, partidos_base: List[str], anio: int) -> Optional[str]:
    """Busca grupo parlamentario - traducida del R"""
    entk = normalize_entidad_ascii(entidad)
    coalN = norm_ascii_up(coalicion)
    
    # Buscar en siglado
    hit = gp_long[
        (gp_long['ENTIDAD_ASCII'] == entk) & 
        (gp_long['COALICION'] == coalN) & 
        (gp_long['FORMULA'] == int(formula))
    ]
    
    if len(hit) >= 1 and pd.notna(hit.iloc[0]['GRUPO_PARLAMENTARIO']) and len(str(hit.iloc[0]['GRUPO_PARLAMENTARIO']).strip()) > 0:
        return hit.iloc[0]['GRUPO_PARLAMENTARIO']
    
    if len(hit) >= 1 and 'PARTIDO_ORIGEN' in hit.columns and pd.notna(hit.iloc[0]['PARTIDO_ORIGEN']) and len(str(hit.iloc[0]['PARTIDO_ORIGEN']).strip()) > 0:
        return hit.iloc[0]['PARTIDO_ORIGEN']
    
    # Fallback: usar tokens de coalición
    toks = tokens_de_coalicion(coalN, anio)
    if toks:
        toks_disponibles = [t for t in toks if t in acred_row.index]
        if toks_disponibles:
            votos = [acred_row[t] if pd.notna(acred_row[t]) else -np.inf for t in toks_disponibles]
            if any(np.isfinite(v) for v in votos):
                idx_max = np.argmax(votos)
                return toks_disponibles[idx_max]
    
    # Último fallback
    if coalN in partidos_base + ["CI"]:
        return coalN
    
    return None

def conteo_senado_MR_PM_sigladoF(df_boleta_est: pd.DataFrame, df_acred_est: pd.DataFrame, 
                                 partidos_base: List[str], gp_long: pd.DataFrame, anio: int,
                                 escanos_mr_efectivos: int = 64, escanos_pm: int = 32,
                                 siglado_map: Optional[Dict] = None) -> Dict:
    """
    Conteo MR+PM con siglado por fórmula - traducción directa del R
    MR: senadores por entidad distribuidos proporcionalmente según escanos_mr_efectivos
    PM: senadores de primera minoría distribuidos según escanos_pm
    """
    print(f"[DEBUG] conteo_senado_MR_PM_sigladoF iniciando para año {anio}")
    print(f"[DEBUG] Parámetros: MR efectivos={escanos_mr_efectivos}, PM={escanos_pm}")
    
    # Validaciones
    assert 'ENTIDAD' in df_boleta_est.columns, "df_boleta_est debe tener ENTIDAD"
    assert 'ENTIDAD' in df_acred_est.columns, "df_acred_est debe tener ENTIDAD"
    
    # Columnas de candidaturas válidas (excluyendo CI)
    cand_cols = cols_candidaturas_anio(df_boleta_est.columns.tolist(), anio)
    cand_cols = [c for c in cand_cols if c != "CI"]
    print(f"[DEBUG] Columnas candidaturas: {cand_cols}")
    
    # Mapeo columna -> coalición
    col2coal = {}
    for col in cand_cols:
        tokens = partidos_de_col(col)
        coal = coalicion_de_tokens(tokens, anio)
        col2coal[col] = coal
    print(f"[DEBUG] Mapeo col->coalición: {col2coal}")
    
    # Ordenar y validar que entidades coincidan
    df_boleta_est = df_boleta_est.sort_values('ENTIDAD').reset_index(drop=True)
    df_acred_est = df_acred_est.sort_values('ENTIDAD').reset_index(drop=True)
    
    if not df_boleta_est['ENTIDAD'].equals(df_acred_est['ENTIDAD']):
        raise ValueError("Las entidades en df_boleta_est y df_acred_est no coinciden")
    
    # Inicializar contadores
    ssd = {p: 0 for p in partidos_base}
    indep = 0
    
    print(f"[DEBUG] Procesando {len(df_boleta_est)} entidades")
    
    # Procesar cada entidad
    for i in range(len(df_boleta_est)):
        entidad = df_boleta_est.iloc[i]['ENTIDAD']
        print(f"[DEBUG] Procesando entidad {i+1}/{len(df_boleta_est)}: {entidad}")
        
        # Votos por columna en esta entidad
        votos_cols = []
        for col in cand_cols:
            if col in df_boleta_est.columns:
                voto = df_boleta_est.iloc[i][col]
                votos_cols.append({'coalicion': col2coal[col], 'votos': voto if pd.notna(voto) else 0})
        
        # Filtrar coaliciones válidas
        votos_validos = [v for v in votos_cols if v['coalicion'] is not None and len(str(v['coalicion']).strip()) > 0]
        if not votos_validos:
            print(f"[DEBUG] No hay votos válidos para {entidad}")
            continue
        
        # Agregar por coalición
        coal_votos = {}
        for v in votos_validos:
            coal = v['coalicion']
            if coal not in coal_votos:
                coal_votos[coal] = 0
            coal_votos[coal] += v['votos']
        
        # Ordenar coaliciones por votos (descendente)
        coaliciones_ordenadas = sorted(coal_votos.items(), key=lambda x: (-x[1], x[0]))
        print(f"[DEBUG] {entidad} - Coaliciones ordenadas: {coaliciones_ordenadas}")
        
        if not coaliciones_ordenadas:
            continue
            
        # Primera coalición (ganadora)
        top1 = coaliciones_ordenadas[0][0]
        top2 = coaliciones_ordenadas[1][0] if len(coaliciones_ordenadas) >= 2 else None
        
        print(f"[DEBUG] {entidad} - Ganador: {top1}, Segundo: {top2}")
        
        # MR efectivos: distribuir proporcionalmente entre 32 entidades
        escanos_mr_por_entidad = escanos_mr_efectivos // 32
        escanos_mr_extra = escanos_mr_efectivos % 32
        
        # PM: distribuir proporcionalmente entre 32 entidades
        escanos_pm_por_entidad = escanos_pm // 32
        escanos_pm_extra = escanos_pm % 32
        
        # Para esta entidad, calcular cuántos MR efectivos y PM le tocan
        # Simplificación: distribuir uniformemente (después se puede sofisticar)
        mr_esta_entidad = escanos_mr_por_entidad + (1 if i < escanos_mr_extra else 0)
        pm_esta_entidad = escanos_pm_por_entidad + (1 if i < escanos_pm_extra else 0)
        
        print(f"[DEBUG] {entidad} - Asignación: {mr_esta_entidad} MR efectivos, {pm_esta_entidad} PM")
        
        # MR efectivos: asignar al ganador (aplicar reglas jurídicas usando siglado_map cuando exista)
        for formula in range(1, mr_esta_entidad + 1):
            gp = None
            # intentar usar siglado_map si está disponible
            try:
                entk = normalize_entidad_ascii(entidad)
                coalN = norm_ascii_up(str(top1)) if top1 is not None else ''
                key = (entk, coalN, int(formula))
                entry = siglado_map.get(key) if siglado_map else None
            except Exception:
                entry = None

            if entry:
                nominadores_set = set([canonizar_siglado(x) for x in entry.get('nominadores_set', set())])
                ppn_gp = entry.get('ppn_gp', '')

                SHH = {"MORENA", "PT", "PVEM"}
                FCM = {"PAN", "PRI", "PRD"}

                # tokens de la coalición ganadora (si aplica)
                tokens = tokens_de_coalicion(coalN, anio) if coalN else []
                tokens_set = set(tokens) if tokens else set()

                # 1) nominadores == SHH y ganó SHH -> acreditar ppn_gp
                if nominadores_set == SHH and tokens_set == SHH and ppn_gp:
                    gp = ppn_gp
                    if gp not in partidos_base and gp != 'CI':
                        gp = None

                # 2) nominadores == FCM y ganó FCM -> acreditar ppn_gp
                if gp is None and nominadores_set == FCM and tokens_set == FCM and ppn_gp:
                    gp = ppn_gp
                    if gp not in partidos_base and gp != 'CI':
                        gp = None

                # 3) único nominador y coincide con ganador -> acreditar
                if gp is None and len(nominadores_set) == 1:
                    solo = list(nominadores_set)[0]
                    if solo in partidos_base and (not tokens_set or solo in tokens_set or solo == norm_ascii_up(str(top1))):
                        gp = solo

            # fallback: usar gp_lookup como antes
            if gp is None:
                gp = gp_lookup(entidad, top1, formula, df_acred_est.iloc[i], gp_long, partidos_base, anio)

            print(f"[DEBUG] {entidad} - MR F{formula}: {top1} -> {gp}")
            if gp is not None:
                if gp == "CI":
                    indep += 1
                elif gp in partidos_base:
                    ssd[gp] += 1
        
        # PM: asignar al segundo lugar si hay PM para esta entidad
        if pm_esta_entidad > 0 and top2 is not None:
            for formula in range(1, pm_esta_entidad + 1):
                gp2 = None
                try:
                    entk = normalize_entidad_ascii(entidad)
                    coalN2 = norm_ascii_up(str(top2)) if top2 is not None else ''
                    key2 = (entk, coalN2, int(formula))
                    entry2 = siglado_map.get(key2) if siglado_map else None
                except Exception:
                    entry2 = None

                if entry2:
                    nominadores_set2 = set([canonizar_siglado(x) for x in entry2.get('nominadores_set', set())])
                    ppn_gp2 = entry2.get('ppn_gp', '')

                    SHH = {"MORENA", "PT", "PVEM"}
                    FCM = {"PAN", "PRI", "PRD"}

                    tokens2 = tokens_de_coalicion(coalN2, anio) if coalN2 else []
                    tokens2_set = set(tokens2) if tokens2 else set()

                    if nominadores_set2 == SHH and tokens2_set == SHH and ppn_gp2:
                        gp2 = ppn_gp2 if ppn_gp2 in partidos_base or ppn_gp2 == 'CI' else None
                    if gp2 is None and nominadores_set2 == FCM and tokens2_set == FCM and ppn_gp2:
                        gp2 = ppn_gp2 if ppn_gp2 in partidos_base or ppn_gp2 == 'CI' else None
                    if gp2 is None and len(nominadores_set2) == 1:
                        solo2 = list(nominadores_set2)[0]
                        if solo2 in partidos_base and (not tokens2_set or solo2 in tokens2_set or solo2 == norm_ascii_up(str(top2))):
                            gp2 = solo2

                if gp2 is None:
                    gp2 = gp_lookup(entidad, top2, formula, df_acred_est.iloc[i], gp_long, partidos_base, anio)

                print(f"[DEBUG] {entidad} - PM F{formula}: {top2} -> {gp2}")
                if gp2 is not None:
                    if gp2 == "CI":
                        indep += 1
                    elif gp2 in partidos_base:
                        ssd[gp2] += 1
    
    total_asignados = sum(ssd.values()) + indep
    total_esperado = escanos_mr_efectivos + escanos_pm
    print(f"[DEBUG] Total MR+PM asignados: {total_asignados} (esperado: {total_esperado})")
    print(f"[DEBUG] Detalle por partido: {ssd}")
    print(f"[DEBUG] Independientes: {indep}")
    
    # Validar que se asignaron exactamente los escaños esperados
    if total_asignados != total_esperado:
        print(f"[WARNING] Se asignaron {total_asignados} escaños MR+PM, esperado: {total_esperado}")
    
    return {'ssd_partidos': ssd, 'indep_mr_pm': indep}

def asigna_senado_RP(votos: Dict[str, int], threshold: float = 0.03, escanos_rp: int = 32) -> Dict[str, int]:
    """
    Asignación RP nacional para senado - traducción directa del R con validaciones
    """
    print(f"[DEBUG] asigna_senado_RP con threshold={threshold}, escanos_rp={escanos_rp}")
    print(f"[DEBUG] Votos entrada: {votos}")
    
    # Convertir a arrays
    partidos = list(votos.keys())
    votos_array = np.array([votos[p] for p in partidos])
    
    if votos_array.sum() <= 0:
        return {p: 0 for p in partidos}
    
    # Calcular porcentajes
    total = votos_array.sum()
    v_valida = votos_array / total
    
    # Aplicar umbral
    mask = v_valida < threshold
    v_nacional = v_valida.copy()
    v_nacional[mask] = 0
    
    # Renormalizar después del umbral
    if v_nacional.sum() > 0:
        v_nacional = v_nacional / v_nacional.sum()
    
    print(f"[DEBUG] Porcentajes antes umbral: {dict(zip(partidos, v_valida))}")
    print(f"[DEBUG] Porcentajes después umbral: {dict(zip(partidos, v_nacional))}")
    
    # VALIDACIÓN: Si no hay partidos que superen el umbral
    partidos_validos = np.sum(v_nacional > 0)
    if partidos_validos == 0:
        print(f"[WARNING] Ningún partido supera umbral {threshold}. Retornando escaños vacíos.")
        return {p: 0 for p in partidos}
    
    # Fórmula de resto mayor
    t = np.floor(v_nacional * escanos_rp + 1e-12).astype(int)
    u = escanos_rp - t.sum()
    
    print(f"[DEBUG] Escaños base: {dict(zip(partidos, t))}")
    print(f"[DEBUG] Escaños restantes a asignar: {u}")
    print(f"[DEBUG] Partidos válidos: {partidos_validos}")
    
    if u > 0:
        # Calcular residuos solo para partidos con votos > 0
        rema = v_nacional * escanos_rp - t
        validos_mask = v_nacional > 0
        
        # VALIDACIÓN: Limitar u al número de partidos válidos
        u_safe = min(u, partidos_validos)
        print(f"[DEBUG] u limitado de {u} a {u_safe}")
        
        # Ordenar por residuo descendente, con índice como desempate
        orden = np.lexsort((np.arange(len(rema)), -rema))
        
        # Asignar escaños adicionales de forma segura
        asignados = 0
        for i in range(len(orden)):
            if asignados >= u_safe:
                break
            idx = orden[i]
            if v_nacional[idx] > 0:  # Solo a partidos válidos
                t[idx] += 1
                asignados += 1
        
        print(f"[DEBUG] Escaños adicionales asignados: {asignados}")
    
    resultado = {partidos[i]: int(t[i]) for i in range(len(partidos))}
    print(f"[DEBUG] Resultado RP: {resultado}")
    print(f"[DEBUG] Total RP asignados: {sum(resultado.values())}")
    
    return resultado

def procesar_senadores_v2(path_parquet: str, anio: int, path_siglado: str, 
                          partidos_base: Optional[List[str]] = None, 
                          max_seats: int = 128, umbral: float = 0.03,
                          sistema: str = "mixto", mr_seats: int = None, rp_seats: int = None,
                          pm_seats: int = 0, quota_method: str = "hare", 
                          divisor_method: str = "dhondt", usar_coaliciones: bool = True) -> Dict:
    """
    Procesador principal de senadores V2 - traducción directa del R
    
    Args:
        sistema: "mixto" (vigente), "rp" (Plan A), "mr" (Plan C)
        mr_seats: número de escaños MR totales disponibles
        rp_seats: número de escaños RP
        pm_seats: número de escaños de primera minoría (sale de mr_seats)
    """
    print(f"[DEBUG] procesar_senadores_v2 iniciando para año {anio}")
    print(f"[DEBUG] Sistema: {sistema}, max_seats: {max_seats}, mr_seats: {mr_seats}, rp_seats: {rp_seats}, pm_seats: {pm_seats}")
    
    # Configurar número de escaños según sistema
    if sistema == "mixto":
        # Sistema vigente: MR + PM + RP = total fijo
        # Los escaños PM "salen" de los escaños MR
        escanos_mr_total = mr_seats if mr_seats is not None else 96
        escanos_pm = pm_seats if pm_seats is not None else 0
        escanos_mr_efectivos = escanos_mr_total - escanos_pm  # MR puro
        escanos_rp = rp_seats if rp_seats is not None else 32
        
        print(f"[DEBUG] Configuración mixta - MR total: {escanos_mr_total}, PM: {escanos_pm}, MR efectivo: {escanos_mr_efectivos}, RP: {escanos_rp}")
        
        # Validar que PM no sea mayor que MR disponible
        if escanos_pm > escanos_mr_total:
            raise ValueError(f"PM ({escanos_pm}) no puede ser mayor que MR total ({escanos_mr_total})")
    elif sistema == "rp":
        # Plan A: Solo RP, típicamente 96 escaños
        escanos_mr_total = 0
        escanos_pm = 0
        escanos_mr_efectivos = 0
        escanos_rp = max_seats
    elif sistema == "mr":
        # Plan C: Solo MR, con posibilidad de PM
        escanos_mr_total = max_seats
        escanos_pm = pm_seats if pm_seats is not None else 0
        escanos_mr_efectivos = max_seats - escanos_pm  # MR efectivo = total - PM
        escanos_rp = 0
        
        # Validar que PM no sea mayor que el total
        if escanos_pm > escanos_mr_total:
            raise ValueError(f"PM ({escanos_pm}) no puede ser mayor que MR total ({escanos_mr_total})")
    else:
        raise ValueError(f"Sistema no reconocido: {sistema}")
    
    print(f"[DEBUG] Configuración final: {escanos_mr_total} MR total ({escanos_mr_efectivos} efectivo + {escanos_pm} PM) + {escanos_rp} RP = {escanos_mr_total + escanos_rp} total")
    
    if partidos_base is None:
        if anio == 2018:
            partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","NA"]
        elif anio == 2024:
            partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA"]
        else:
            partidos_base = parties_for(anio)
    
    try:
        # 1) Leer datos de boletas
        print(f"[DEBUG] Leyendo parquet: {path_parquet}")
        if not os.path.exists(path_parquet):
            raise FileNotFoundError(f"No existe: {path_parquet}")
        
        df_boletas = pd.read_parquet(path_parquet)
        print(f"[DEBUG] Boletas shape: {df_boletas.shape}")
        print(f"[DEBUG] Boletas columnas: {df_boletas.columns.tolist()}")
        
        # Normalizar columnas
        df_boletas.columns = [norm_ascii_up(c) for c in df_boletas.columns]
        
        # Normalizar entidades
        if 'ENTIDAD' in df_boletas.columns:
            df_boletas['ENTIDAD'] = df_boletas['ENTIDAD'].apply(
                lambda x: x.decode('utf-8', errors='replace') if isinstance(x, bytes) else str(x)
            )
            df_boletas['ENTIDAD'] = df_boletas['ENTIDAD'].apply(normalize_entidad_ascii)
        
        # 1.5) NUEVO: Agregar coaliciones automáticamente basadas en el siglado
        coaliciones_agregadas = False
        coaliciones_en_siglado = None  # Variable para detectar si existen coaliciones
        
        if path_siglado:
            print(f"[DEBUG] Extrayendo coaliciones del siglado: {path_siglado}")
            coaliciones_en_siglado = extraer_coaliciones_de_siglado(path_siglado)
            
            if coaliciones_en_siglado:
                print(f"[DEBUG] Coaliciones encontradas en siglado: {coaliciones_en_siglado}")
                
                if usar_coaliciones:
                    print(f"[DEBUG] Agregando columnas de coalición al dataset")
                    df_boletas = agregar_columnas_coalicion(df_boletas, coaliciones_en_siglado)
                    coaliciones_agregadas = True
                    print(f"[DEBUG] Dataset con coaliciones shape: {df_boletas.shape}")
                else:
                    print(f"[DEBUG] Coaliciones DESACTIVADAS por parámetro usar_coaliciones=False")
                    print(f"[DEBUG] Se aplicará desagregación de votos para contrafactual")
            else:
                print(f"[DEBUG] No se detectaron coaliciones en el siglado")
        
        # 2) Recomposición usando el sistema existente (solo si no agregamos coaliciones)
        if coaliciones_agregadas:
            print(f"[DEBUG] Saltando recomposición: ya tenemos coaliciones del siglado")
            recomposed = df_boletas
        else:
            # Si se proporcionó siglado, usar la regla con siglado; si no, usar la regla por defecto sin siglado
            if path_siglado:
                print(f"[DEBUG] Realizando recomposición con siglado: {path_siglado}")
                recomposed = recompose_coalitions(
                    df=df_boletas,
                    year=anio,
                    chamber="senado", 
                    rule="equal_residue_siglado",
                    siglado_path=path_siglado
                )
            else:
                print(f"[DEBUG] Realizando recomposición SIN siglado (equal_residue_solo)")
                recomposed = recompose_coalitions(
                    df=df_boletas,
                    year=anio,
                    chamber="senado", 
                    rule="equal_residue_solo",
                    siglado_path=None
                )
        print(f"[DEBUG] Recomposición completada, shape: {recomposed.shape}")
        
        # 3) Crear df_acred_est (votos por entidad y partido)
        # Sumar votos por entidad para cada partido
        df_acred_est = recomposed.groupby('ENTIDAD')[partidos_base].sum().reset_index()
        print(f"[DEBUG] Acreditación por entidad shape: {df_acred_est.shape}")
        
        # 4) Leer siglado (si fue provisto)
        if path_siglado:
            print(f"[DEBUG] Leyendo siglado: {path_siglado}")
            gp_long = read_siglado_sen_long(path_siglado)
            print(f"[DEBUG] Siglado shape: {gp_long.shape}")

            # 4.5) Construir siglado_map: llave (ENTIDAD_ASCII, COALICION, FORMULA) -> {nominadores_set, ppn_gp}
            siglado_map = {}
            try:
                grouped = gp_long.groupby(['ENTIDAD_ASCII', 'COALICION', 'FORMULA'])
                for key, dfg in grouped:
                    entk, coalN, formula = key
                    nominadores = set()
                    gps = set()
                    # PARTIDO_ORIGEN puede contener el partido nominador
                    if 'PARTIDO_ORIGEN' in dfg.columns:
                        for v in dfg['PARTIDO_ORIGEN'].unique():
                            if pd.notna(v) and str(v).strip() != '':
                                nominadores.add(canonizar_siglado(v))
                    # GRUPO_PARLAMENTARIO puede indicar el grupo parlamentario a acreditar
                    for g in dfg['GRUPO_PARLAMENTARIO'].unique():
                        if pd.notna(g) and str(g).strip() != '':
                            gps.add(canonizar_siglado(g))

                    ppn_gp = ''
                    if len(gps) == 1:
                        ppn_gp = list(gps)[0]
                    elif len(gps) > 1:
                        print(f"[WARN] Múltiples GRUPO_PARLAMENTARIO para {key}: {gps}; ignorando ppn_gp")

                    siglado_map[(normalize_entidad_ascii(entk), norm_ascii_up(coalN), int(formula))] = {
                        'nominadores_set': nominadores,
                        'ppn_gp': ppn_gp
                    }
                print(f"[DEBUG] siglado_map construido con {len(siglado_map)} entradas")
            except Exception as e:
                print(f"[WARN] No se pudo construir siglado_map: {e}")
                siglado_map = None
        else:
            print(f"[DEBUG] No se proporcionó path_siglado; gp_long vacío y sin siglado_map")
            gp_long = pd.DataFrame(columns=['ENTIDAD_ASCII','COALICION','FORMULA','GRUPO_PARLAMENTARIO','PARTIDO_ORIGEN'])
            siglado_map = None
        
        # 5) Calcular MR+PM usando siglado por fórmula (solo si aplica)
        if escanos_mr_total > 0:
            mrpm_result = conteo_senado_MR_PM_sigladoF(
                df_boleta_est=recomposed,
                df_acred_est=df_acred_est,
                partidos_base=partidos_base,
                gp_long=gp_long,
                anio=anio,
                escanos_mr_efectivos=escanos_mr_efectivos,
                escanos_pm=escanos_pm,
                siglado_map=siglado_map
            )
            
            ssd = mrpm_result['ssd_partidos']
            indep_mr_pm = mrpm_result['indep_mr_pm']
            
            print(f"[DEBUG] MR+PM por partido: {ssd}")
            print(f"[DEBUG] Independientes MR+PM: {indep_mr_pm}")
            
            # Ajustar proporcionalmente si el total no coincide con el esperado
            total_mr_pm_original = sum(ssd.values()) + indep_mr_pm
            print(f"[DEBUG] Total MR+PM original: {total_mr_pm_original}, esperado: {escanos_mr_total}")
            
            if total_mr_pm_original != escanos_mr_total and total_mr_pm_original > 0:
                # Ajustar proporcionalmente
                factor = escanos_mr_total / total_mr_pm_original
                ssd_ajustado = {}
                for p in partidos_base:
                    ssd_ajustado[p] = int(round(ssd.get(p, 0) * factor))
                
                # Ajustar diferencia por redondeo
                total_ajustado = sum(ssd_ajustado.values())
                diferencia = escanos_mr_total - total_ajustado
                
                if diferencia != 0:
                    # Distribuir diferencia en partidos con más votos
                    votos_partidos = [(p, recomposed[p].sum()) for p in partidos_base if ssd.get(p, 0) > 0]
                    votos_partidos.sort(key=lambda x: x[1], reverse=True)
                    
                    for i in range(abs(diferencia)):
                        if i < len(votos_partidos):
                            p = votos_partidos[i][0]
                            ssd_ajustado[p] += 1 if diferencia > 0 else -1
                
                ssd = ssd_ajustado
                print(f"[DEBUG] MR+PM ajustado: {ssd}")
        else:
            ssd = {p: 0 for p in partidos_base}
            indep_mr_pm = 0
        
        # 6) Calcular RP nacional (solo si aplica)
        votos_nacionales = {p: int(recomposed[p].sum()) for p in partidos_base}
        print(f"[DEBUG] Votos nacionales: {votos_nacionales}")
        
        # 6.5) CRÍTICO: Si usar_coaliciones=False, desagregar votos de coalición
        # Esto implementa el contrafactual: "como si nunca hubieran competido juntos"
        coaliciones_detectadas = coaliciones_en_siglado is not None and len(coaliciones_en_siglado) > 0
        
        if not usar_coaliciones and coaliciones_detectadas:
            print(f"[INFO] DESAGREGANDO votos de coalición (contrafactual: competencia separada)")
            
            # Identificar coaliciones por año (senado)
            coaliciones_por_anio = {
                2018: ['MORENA', 'PT', 'PES'],
                2024: ['MORENA', 'PT', 'PVEM']
            }
            
            partidos_coalicion = coaliciones_por_anio.get(anio, [])
            
            if partidos_coalicion and all(p in votos_nacionales for p in partidos_coalicion):
                # Calcular total de votos de la coalición
                total_coalicion = sum(votos_nacionales[p] for p in partidos_coalicion)
                print(f"[DEBUG] Total votos coalición {partidos_coalicion}: {total_coalicion:,}")
                
                # Intentar cargar proporciones del año de referencia (año-3 o año-6)
                proporciones = {}
                anio_ref = anio - 6  # Para senado: 2024→2018
                
                path_ref = f"data/computos_senado_{anio_ref}.parquet"
                if os.path.exists(path_ref):
                    try:
                        df_ref = pd.read_parquet(path_ref)
                        print(f"[DEBUG] Cargando proporciones históricas desde {anio_ref}")
                        
                        # Calcular totales nacionales del año de referencia
                        totales_ref = {}
                        for p in partidos_coalicion:
                            if p in df_ref.columns:
                                totales_ref[p] = df_ref[p].sum()
                        
                        total_ref = sum(totales_ref.values())
                        
                        if total_ref > 0:
                            # Calcular proporciones
                            for p in partidos_coalicion:
                                prop = totales_ref.get(p, 0) / total_ref
                                proporciones[p] = prop
                                print(f"[DEBUG]   {p}: {totales_ref.get(p, 0):,} votos ({prop*100:.2f}%)")
                        else:
                            print(f"[WARN] Total de referencia es 0, usando proporciones por defecto")
                    except Exception as e:
                        print(f"[WARN] Error cargando año de referencia {anio_ref}: {e}")
                
                # Proporciones por defecto si no hay datos históricos
                if not proporciones:
                    print(f"[DEBUG] Usando proporciones por defecto para {anio}")
                    if anio == 2024:
                        proporciones = {'MORENA': 0.75, 'PT': 0.10, 'PVEM': 0.15}
                    elif anio == 2018:
                        proporciones = {'MORENA': 0.70, 'PT': 0.15, 'PES': 0.15}
                    else:
                        # Distribuir equitativamente
                        n_partidos = len(partidos_coalicion)
                        proporciones = {p: 1.0/n_partidos for p in partidos_coalicion}
                
                # Redistribuir votos según proporciones
                print(f"[DEBUG] Redistribuyendo {total_coalicion:,} votos según proporciones:")
                for p in partidos_coalicion:
                    votos_desagregados = int(total_coalicion * proporciones.get(p, 0))
                    votos_originales = votos_nacionales[p]
                    votos_nacionales[p] = votos_desagregados
                    print(f"[DEBUG]   {p}: {votos_originales:,} -> {votos_desagregados:,} ({proporciones.get(p, 0)*100:.1f}%)")
                
                print(f"[DEBUG] Votos nacionales después de desagregación: {votos_nacionales}")
            else:
                print(f"[DEBUG] No se pudo identificar coalición para desagregar en {anio}")
        
        if escanos_rp > 0:
            rp_result = asigna_senado_RP(votos_nacionales, threshold=umbral, escanos_rp=escanos_rp)
            print(f"[DEBUG] RP resultado: {rp_result}")
        else:
            rp_result = {p: 0 for p in partidos_base}
        
        # 7) Totales
        totales = {}
        votos_ok = {}
        ok_dict = {}
        
        for p in partidos_base:
            mr_pm = ssd.get(p, 0)
            rp = rp_result.get(p, 0)
            total = mr_pm + rp
            votos = votos_nacionales.get(p, 0)
            
            # Determinar si supera umbral
            total_votos_validos = sum(votos_nacionales.values())
            supera_umbral = total_votos_validos > 0 and (votos / total_votos_validos) >= umbral
            
            totales[p] = total
            votos_ok[p] = votos if supera_umbral else 0
            ok_dict[p] = supera_umbral
        
        # 8) Construir seat_chart
        seat_chart = []
        total_votos = sum(votos_nacionales.values()) if votos_nacionales else 1
        total_escanos = sum(totales.values()) if totales else 1
        
        # Mapea colores por partido (copiado de main.py)
        PARTY_COLORS = {
            "MORENA": "#8B2231",
            "PAN": "#0055A5", 
            "PRI": "#0D7137",
            "PT": "#D52B1E",
            "PVEM": "#1E9F00",
            "MC": "#F58025",
            "PRD": "#FFCC00",
            "PES": "#6A1B9A",
            "NA": "#00B2E3",
            "FXM": "#FF69B4",
        }
        
        for partido in partidos_base:
            escanos = totales.get(partido, 0)
            votos = votos_nacionales.get(partido, 0)
            
            seat_chart_item = {
                "party": partido,
                "seats": escanos,
                "color": PARTY_COLORS.get(partido, "#888888"),
                "percent": round((escanos / total_escanos) * 100, 2) if total_escanos > 0 else 0,
                "votes": votos
            }
            seat_chart.append(seat_chart_item)
        
        # 9) Estructura de retorno compatible con seat_chart incluido
        resultado = {
            'mr': ssd,  # En senado, MR incluye PM (64 MR + 32 PM = 96 total)
            'rp': rp_result,
            'tot': totales,
            'ok': ok_dict,
            'votos': votos_nacionales,
            'votos_ok': votos_ok,
            'seat_chart': seat_chart
        }
        
        print(f"[DEBUG] Resultado final:")
        print(f"[DEBUG] - MR+PM: {resultado['mr']}")
        print(f"[DEBUG] - RP: {resultado['rp']}")
        print(f"[DEBUG] - Totales: {resultado['tot']}")
        print(f"[DEBUG] - Seat chart: {len(seat_chart)} partidos")
        
        # Validación final
        total_escanos = sum(resultado['tot'].values())
        escanos_esperados = escanos_mr_total + escanos_rp
        if total_escanos != escanos_esperados:
            print(f"[WARNING] Total escaños = {total_escanos}, esperado {escanos_esperados}")
        else:
            print(f"[SUCCESS] Total escaños correcto: {total_escanos}")
        
        return resultado
        
    except Exception as e:
        print(f"[ERROR] procesar_senadores_v2: {e}")
        import traceback
        traceback.print_exc()
        
        # Retorno de emergencia con seat_chart vacío
        return {
            'mr': {p: 0 for p in partidos_base},
            'rp': {p: 0 for p in partidos_base},
            'tot': {p: 0 for p in partidos_base},
            'ok': {p: False for p in partidos_base},
            'votos': {p: 0 for p in partidos_base},
            'votos_ok': {p: 0 for p in partidos_base},
            'seat_chart': []
        }
