import pandas as pd
import numpy as np
import unicodedata
import re
import os
from .recomposicion import recompose_coalitions, parties_for
from .core import assign_senadores, SenParams

# utils_normalize.py helpers
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
    return y

def coalicion_de_tokens(tokens, anio):
    S = sorted(set(tokens))
    if anio == 2018:
        if set(S) == {"MORENA","PT","PES"}: return "JUNTOS HAREMOS HISTORIA"
        if set(S) == {"PAN","PRD","MC"}:    return "POR MEXICO AL FRENTE"
        if set(S) == {"PRI","PVEM","NA"}:   return "TODOS POR MEXICO"
    if anio == 2024:
        if set(S) == {"MORENA","PT","PVEM"}: return "SIGAMOS HACIENDO HISTORIA"
        if set(S) == {"PAN","PRI","PRD"}:    return "FUERZA Y CORAZON POR MEXICO"
    if len(S) == 1 and S[0] in {"PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","NA","CI"}:
        return S[0]
    return None

def partidos_de_coalicion(coalicion, anio):
    """Regresa lista de partidos que forman una coalición específica"""
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
    
    # Para partidos individuales, retornar lista con solo ese partido
    partidos_base = ["PAN", "PRI", "PRD", "PVEM", "PT", "MC", "MORENA", "PES", "NA", "CI"]
    if coalicion in partidos_base:
        return [coalicion]
    return []

def calcular_mr_pm_senado(df, partidos_base, anio, path_siglado=None):
    """
    Calcula MR y PM para senadores basado en votos y siglado.
    """
    resultados = []
    
    # Simplificado: devolver estructura básica si no hay siglado
    if path_siglado is None or not os.path.exists(path_siglado):
        for partido in partidos_base:
            resultados.append({
                'entidad': 'NACIONAL',
                'partido': partido,
                'votos': 0,
                'mr': 0,
                'pm': 0
            })
        return pd.DataFrame(resultados)
    
    # Procesar con siglado...
    for partido in partidos_base:
        resultados.append({
            'entidad': 'NACIONAL', 
            'partido': partido,
            'votos': 0,
            'mr': 0,
            'pm': 0
        })
    
    return pd.DataFrame(resultados)

def procesar_senadores_parquet(path_parquet=None, partidos_base=None, anio=2024, path_siglado=None, max_seats=128, sistema='mixto', mr_seats=None, rp_seats=None, regla_electoral=None, quota_method='hare', divisor_method='dhondt', umbral=None, max_seats_per_party=None):
    """
    Procesa la elección de senadores desde un parquet, incluyendo MR, PM y RP.
    """
    try:
        if not path_parquet:
            raise ValueError("Debe proporcionar path_parquet")
        
        if not partidos_base:
            partidos_base = parties_for(anio)
            
        print(f"[DEBUG] Leyendo Parquet: {path_parquet}")
        print(f"[DEBUG] Path Parquet absoluto: {os.path.abspath(path_parquet)}")
        
        if not os.path.exists(path_parquet):
            print(f"[ERROR] Archivo no existe: {path_parquet}")
            return None
            
        try:
            df = pd.read_parquet(path_parquet)
        except Exception as e:
            print(f"[WARN] Error leyendo Parquet normal, intentando forzar: {e}")
            import pyarrow.parquet as pq
            table = pq.read_table(path_parquet)
            df = table.to_pandas()
            for col in df.columns:
                if df[col].dtype == object:
                    df[col] = df[col].apply(lambda x: x.decode('utf-8', errors='replace') if isinstance(x, bytes) else x)

        print(f"[DEBUG] Parquet Senado columnas: {df.columns.tolist()}")
        print(f"[DEBUG] Parquet Senado shape: {df.shape}")
        
        # Normalizar nombres de columnas
        df.columns = [norm_ascii_up(c) for c in df.columns]
        
        if 'ENTIDAD' in df.columns:
            df['ENTIDAD'] = df['ENTIDAD'].apply(lambda x: x.decode('utf-8', errors='replace') if isinstance(x, bytes) else x)
            df['ENTIDAD'] = df['ENTIDAD'].apply(normalize_entidad_ascii)

        # Recomposición de votos usando siglado si está disponible
        recomposed = None
        if path_siglado is not None and os.path.exists(path_siglado):
            print(f"[DEBUG] Usando recomposición con siglado: {path_siglado}")
            # Normaliza nombres de columna del siglado antes de pasar a recompose_coalitions
            siglado_df = pd.read_csv(path_siglado)
            
            # Primero aplicar normalización general
            siglado_df.columns = [c.upper().replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U') for c in siglado_df.columns]
            print(f"[DEBUG] Columnas después de normalización: {list(siglado_df.columns)}")
            
            # Después corregir problema específico de ENTIDAD_ASCII -> ENTIDAD
            if 'ENTIDAD_ASCII' in siglado_df.columns and 'ENTIDAD' not in siglado_df.columns:
                siglado_df = siglado_df.rename(columns={'ENTIDAD_ASCII': 'ENTIDAD'})
                print(f"[DEBUG] Siglado: Renombrado ENTIDAD_ASCII -> ENTIDAD")
            
            print(f"[DEBUG] Columnas finales: {list(siglado_df.columns)}")
            
            # Verificar que el siglado tiene las columnas requeridas
            required_cols = ['ENTIDAD', 'COALICION', 'FORMULA']
            missing_cols = [col for col in required_cols if col not in siglado_df.columns]
            if missing_cols:
                print(f"[ERROR] procesar_senadores_parquet: Siglado SEN: se esperan columnas {', '.join(required_cols)}.")
                print(f"[DEBUG] Columnas disponibles: {list(siglado_df.columns)}")
                return None
                
            # Guardar temporalmente el siglado normalizado para que recompose_coalitions lo lea
            _sig_path = path_siglado + '.tmp_normalized.csv'
            siglado_df.to_csv(_sig_path, index=False)
            recomposed = recompose_coalitions(
                df=df,
                year=anio,
                chamber="senado",
                rule="equal_residue_siglado",
                siglado_path=_sig_path
            )
            try:
                os.remove(_sig_path)
            except Exception:
                pass
        else:
            print("[DEBUG] Usando recomposición estándar (sin siglado)")
            recomposed = recompose_coalitions(
                df=df,
                year=anio,
                chamber="senado",
                rule="equal_residue_solo",
                siglado_path=None
            )

        # Suma nacional de votos por partido
        votos_partido = {p: int(recomposed[p].sum()) if p in recomposed.columns else 0 for p in partidos_base}
        print(f"[DEBUG] votos_partido Senado (RECOMPUESTOS): {votos_partido}")
        
        indep = int(recomposed['CI'].sum()) if 'CI' in recomposed.columns else 0
        print(f"[DEBUG] Independientes Senado: {indep}")

        # Calcular MR y PM usando la función existente si hay siglado
        if path_siglado is not None and os.path.exists(path_siglado):
            print(f"[DEBUG] Calculando MR/PM con siglado y recomposed")
            mr_pm_result = calcular_mr_pm_senado(recomposed, partidos_base, anio, path_siglado)
            mr_count = {p: mr_pm_result[mr_pm_result['partido'] == p]['mr'].sum() for p in partidos_base}
            pm_count = {p: mr_pm_result[mr_pm_result['partido'] == p]['pm'].sum() for p in partidos_base}
        else:
            mr_count = {p: 0 for p in partidos_base}
            pm_count = {p: 0 for p in partidos_base}

        print(f"[DEBUG] mr_count (nueva función): {mr_count}")
        print(f"[DEBUG] pm_count (nueva función): {pm_count}")

        # RP nacional: votos totales por partido recombinados
        resultados_rp = [{'party': p, 'votes': votos_partido.get(p, 0)} for p in partidos_base]
        print(f"[DEBUG] resultados_rp: {resultados_rp}")

        # Umbral
        if umbral is None:
            umbral = 0.03
        if umbral >= 1:
            umbral = umbral / 100.0
        print(f"[DEBUG] Umbral usado para filtro: {umbral}")

        # Aplicar umbral a votos
        total_votos_validos = sum(votos_partido.values())
        votos_ok = {p: int(votos_partido.get(p, 0)) if total_votos_validos > 0 and (votos_partido.get(p, 0)/total_votos_validos) >= umbral else 0 for p in partidos_base}
        
        # Crear diccionarios alineados
        mr_dict = {p: int(mr_count.get(p, 0)) for p in partidos_base}
        pm_dict = {p: int(pm_count.get(p, 0)) for p in partidos_base}
        
        # Determinar RP seats
        total_mr_pm = sum(mr_dict.values()) + sum(pm_dict.values())
        rp_seats = max_seats - total_mr_pm if total_mr_pm <= max_seats else 0
        
        print(f"[DEBUG] Total MR+PM: {total_mr_pm}, RP seats disponibles: {rp_seats}")

        # Asignar RP usando assign_senadores si hay escaños disponibles
        rp_dict = {p: 0 for p in partidos_base}
        if rp_seats > 0 and sum(votos_ok.values()) > 0:
            # Crear parámetros para assign_senadores
            params = SenParams(
                S=max_seats,
                threshold=umbral,
                quota_method=quota_method,
                divisor_method=divisor_method,
                use_divisor_for_rp=True
            )
            
            votos_series = pd.Series(votos_ok)
            rp_result = assign_senadores(votos_series, rp_seats, params)
            rp_dict = {p: int(rp_result.get(p, 0)) for p in partidos_base}

        # Totales
        tot_dict = {p: mr_dict[p] + pm_dict[p] + rp_dict[p] for p in partidos_base}
        
        # OK dict
        ok_dict = {p: (votos_ok.get(p, 0) > 0 and votos_ok.get(p, 0) / sum(votos_ok.values()) >= umbral) for p in partidos_base} if sum(votos_ok.values()) > 0 else {p: False for p in partidos_base}
        
        # Estructura consistente con procesar_diputados
        resultado = {
            'mr': {p: mr_dict[p] + pm_dict[p] for p in partidos_base},  # MR incluye PM
            'rp': rp_dict,
            'tot': tot_dict,
            'ok': ok_dict,
            'votos': votos_ok,
            'votos_ok': {p: v for p, v in votos_ok.items() if ok_dict[p]}
        }
        
        return resultado

    except Exception as e:
        print(f"[ERROR] procesar_senadores_parquet: {e}")
        # Retornar dict estándar vacío para evitar que truene el pipeline
        partidos = partidos_base if partidos_base else []
        return {
            'mr': {p: 0 for p in partidos},
            'rp': {p: 0 for p in partidos},
            'tot': {p: 0 for p in partidos},
            'ok': {p: False for p in partidos},
            'votos': {p: 0 for p in partidos},
            'votos_ok': {p: 0 for p in partidos}
        }
