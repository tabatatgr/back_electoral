# --- BLOQUE DROP-IN: Loop de coaliciones (equivalente Python) ---
import numpy as np

def procesar_coaliciones(coal_cols, agg, out, partidos_de_col, to_num):
    if len(coal_cols):
        for cn in coal_cols:
            S = partidos_de_col(cn)
            k = len(S)
            if k < 2:
                continue

            V = to_num(agg[cn])  # vector: n_filas
            q = V // k           # reparto equitativo
            r = V % k            # residuo POR FILA

            # suma base por partes iguales
            for p in S:
                out[p] = out.get(p, 0) + q

            # “singles” por fila y por partido de la coalición (matriz n_filas x k)
            sing = np.column_stack([
                to_num(agg[p]) if p in agg.columns else np.zeros(len(agg), dtype=int)
                for p in S
            ])
            if sing.ndim == 1:
                sing = sing.reshape(-1, len(S))  # por si k==1 (no debería)

            # argmax POR FILA
            idx = np.argmax(sing, axis=1)  # vector: n_filas, valores en 0..k-1

            # construir matriz de residuo a sumar (n_filas x k)
            add_mat = np.zeros((len(agg), k), dtype=int)
            add_mat[np.arange(len(agg)), idx] = r

            # sumar residuo fila a fila al partido ganador “solo” dentro de la coalición
            for j, p in enumerate(S):
                out[p] = out.get(p, 0) + add_mat[:, j]
# --- FIN BLOQUE DROP-IN ---
import pandas as pd
import unicodedata
import re
import os
from .recomposicion import recompose_coalitions, parties_for
from .recomposicion import _is_coalition_col
from .core import assign_diputados, DipParams

# utils_normalize.py (o pégalo donde tengas helpers y úsalo en todo)
import re
import unicodedata

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

# --- Procesamiento principal para diputados ---
def procesar_diputados_parquet(path_parquet=None, partidos_base=None, anio=2024, path_siglado=None, max_seats=300, sistema='mixto', mr_seats=None, rp_seats=None, regla_electoral=None, quota_method='hare', divisor_method='dhondt', umbral=None, max_seats_per_party=None):
    """
    Lee y procesa la base Parquet de diputados, regresa dicts listos para el orquestador.
    - path_parquet: ruta al archivo Parquet
    - partidos_base: lista de partidos válidos
    - anio: año de elección
    - path_siglado: CSV de siglado por distrito (opcional, para MR)
    """
    try:
        if not path_parquet:
            raise ValueError("Debe proporcionar path_parquet")
        
        if not partidos_base:
            partidos_base = parties_for(anio)
            
        try:
            print(f"[DEBUG] Leyendo Parquet Diputados: {path_parquet}")
            df = pd.read_parquet(path_parquet)
        except Exception as e:
            print(f"[WARN] Error leyendo Parquet normal, intentando forzar a string y decodificar UTF-8: {e}")
            import pyarrow.parquet as pq
            table = pq.read_table(path_parquet)
            df = table.to_pandas()
            for col in df.columns:
                if df[col].dtype == object:
                    df[col] = df[col].apply(lambda x: x.decode('utf-8', errors='replace') if isinstance(x, bytes) else x)

        print(f"[DEBUG] Parquet Diputados columnas: {df.columns.tolist()}")
        print(f"[DEBUG] Parquet Diputados shape: {df.shape}")
        # Normaliza nombres de columnas
        df.columns = [norm_ascii_up(c) for c in df.columns]
        # Normaliza entidad y distrito
        if 'ENTIDAD' in df.columns:
            df['ENTIDAD'] = df['ENTIDAD'].apply(lambda x: x.decode('utf-8', errors='replace') if isinstance(x, bytes) else x)
            df['ENTIDAD'] = df['ENTIDAD'].apply(normalize_entidad_ascii)
        if 'DISTRITO' in df.columns:
            df['DISTRITO'] = pd.to_numeric(df['DISTRITO'], errors='coerce').fillna(0).astype(int)

        # --- Recomposición de votos usando siglado si está disponible ---
        recomposed = None
        if path_siglado is not None and os.path.exists(path_siglado):
            print(f"[DEBUG] Usando recomposición con siglado: {path_siglado}")
            # Normaliza nombres de columna del siglado antes de pasar a recompose_coalitions
            siglado_df = pd.read_csv(path_siglado, dtype=str)
            # normalize siglado column names to uppercase without ASCII suffix and accents
            siglado_df.columns = [c.upper().replace('ASCII', '').replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U').strip() for c in siglado_df.columns]

            # Accept multiple possible column names for entidad/distrito and party/group
            # Common alternatives in siglado files: ENTIDAD, ENTIDAD_ASCII, DISTRITO, DISTRITO_NUM
            ent_col = next((c for c in ['ENTIDAD', 'ENTIDAD_ASCII', 'ENTIDAD_N'] if c in siglado_df.columns), None)
            dist_col = next((c for c in ['DISTRITO', 'DISTRITO_NUM', 'DIST'] if c in siglado_df.columns), None)
            gp_col = next((c for c in ['GRUPO_PARLAMENTARIO', 'PARTIDO_ORIGEN', 'PARTIDO', 'GRUPO'] if c in siglado_df.columns), None)

            # Normalize ENTIDAD text and DISTRITO numeric columns
            if ent_col:
                siglado_df['ENTIDAD'] = siglado_df[ent_col].fillna('').apply(lambda x: x.upper().strip() if isinstance(x, str) else str(x))
            else:
                siglado_df['ENTIDAD'] = ''

            if dist_col:
                siglado_df['DISTRITO'] = pd.to_numeric(siglado_df[dist_col], errors='coerce').fillna(0).astype(int)
            else:
                # try to infer from a column named 'DISTRITO' in lowercase
                siglado_df['DISTRITO'] = siglado_df.get('DISTRITO', 0)
                siglado_df['DISTRITO'] = pd.to_numeric(siglado_df['DISTRITO'], errors='coerce').fillna(0).astype(int)

            # pick a group/parliamentary column: prefer GRUPO_PARLAMENTARIO then PARTIDO_ORIGEN
            if gp_col:
                siglado_df['DOMINANTE'] = siglado_df[gp_col].fillna('').apply(lambda x: x.upper().strip() if isinstance(x, str) else str(x))
            else:
                # try common names
                for candidate in ['GRUPO_PARLAMENTARIO', 'PARTIDO_ORIGEN', 'PARTIDO']:
                    if candidate in siglado_df.columns:
                        siglado_df['DOMINANTE'] = siglado_df[candidate].fillna('').apply(lambda x: x.upper().strip() if isinstance(x, str) else str(x))
                        break
                else:
                    siglado_df['DOMINANTE'] = ''

            # create a composite district id (ENTIDAD numeric if present or ENTIDAD text cleaned + DISTRITO zero-padded)
            # try to find a numeric entidad code column
            ent_code_col = next((c for c in ['CLAVE_ENTIDAD', 'CVE_ENT', 'CVE_ENTIDAD', 'ID_ENTIDAD'] if c in siglado_df.columns), None)
            if ent_code_col:
                siglado_df['ENT_CH'] = pd.to_numeric(siglado_df[ent_code_col], errors='coerce').fillna(0).astype(int).astype(str).str.zfill(2)
            else:
                # fallback: map ENTIDAD names to a pseudo-code by taking first two letters
                siglado_df['ENT_CH'] = siglado_df['ENTIDAD'].apply(lambda x: ''.join([ch for ch in x if ch.isalnum()])[:2].upper().ljust(2, '0'))

            siglado_df['DIST_CH'] = siglado_df['DISTRITO'].astype(int).astype(str).str.zfill(3)
            siglado_df['DIST_UID'] = siglado_df['ENT_CH'] + '-' + siglado_df['DIST_CH']

            # Ensure MR_DOMINANTE column (some downstream code checks MR_DOMINANTE)
            if 'MR_DOMINANTE' not in siglado_df.columns:
                siglado_df['MR_DOMINANTE'] = siglado_df['DOMINANTE']

            # Guardar temporalmente el siglado normalizado para que recompose_coalitions lo lea
            _sig_path = path_siglado + '.tmp_normalized.csv'
            siglado_df.to_csv(_sig_path, index=False)
            recomposed = recompose_coalitions(
                df=df,
                year=anio,
                chamber="diputados",
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
                chamber="diputados",
                rule="equal_residue_solo",
                siglado_path=None
            )
        
        # Suma nacional de votos por partido
        votos_partido = {p: int(recomposed[p].sum()) if p in recomposed.columns else 0 for p in partidos_base}
        print(f"[DEBUG] votos_partido Diputados (RECOMPUESTOS): {votos_partido}")

        indep = int(recomposed['CI'].sum()) if 'CI' in recomposed.columns else 0
        print(f"[DEBUG] Independientes Diputados: {indep}")
        from .core import mr_by_siglado
        try:
            mr, indep_mr = mr_by_siglado(
                winners_df=recomposed,
                group_keys=["ENTIDAD", "DISTRITO"],
                gp_col="MR_DOMINANTE" if "MR_DOMINANTE" in recomposed.columns else "DOMINANTE",
                parties=partidos_base
            )
        except Exception as e:
            print(f"[WARN] Error usando mr_by_siglado: {e}")
            # fallback: por votos
            ganadores_por_distrito = recomposed.groupby(['ENTIDAD','DISTRITO'])[partidos_base].sum().idxmax(axis=1)
            mr = ganadores_por_distrito.value_counts().to_dict()
            indep_mr = mr.get('CI', 0)

        mr_aligned = {p: int(mr.get(p, 0)) for p in partidos_base}
        print(f"[DEBUG] MR Diputados alineado: {mr_aligned}")

        # Umbral
        if umbral is None:
            umbral = 0.03
        if umbral >= 1:
            umbral = umbral / 100.0
        print(f"[DEBUG] Umbral usado para filtro: {umbral}")

        # Aplica umbral a votos recombinados
        total_votos_validos = sum(votos_partido.values())
        votos_ok = {p: int(votos_partido.get(p, 0)) if total_votos_validos > 0 and (votos_partido.get(p, 0)/total_votos_validos) >= umbral else 0 for p in partidos_base}
        ssd = {p: int(mr_aligned.get(p, 0)) for p in partidos_base}
        print(f"[DEBUG] votos_ok Diputados: {votos_ok}")
        print(f"[DEBUG] ssd Diputados: {ssd}")

        suma_votos_ok = sum(votos_ok.values())
        if suma_votos_ok == 0:
            print("[ERROR] Ningún partido pasa el umbral. Abortando.")
            return None

        # Determinar m (RP) y S (total) según sistema
        sistema_tipo = sistema.lower() if sistema else 'mixto'
        if sistema_tipo == 'mr':
            m = 0
            S = max_seats
        elif sistema_tipo == 'rp':
            m = max_seats
            S = max_seats
        else:
            m = rp_seats if rp_seats is not None else (S := max_seats - (mr_seats if mr_seats is not None else sum(ssd.values())))
            S = max_seats
        print(f"[DEBUG] sistema: {sistema_tipo}, m (RP): {m}, S (S): {S}, max_seats: {max_seats}")

        # Crear parámetros para assign_diputados
        # Para Plan A (mr_seats=0), no usar los ssd calculados
        effective_mr_seats = 0 if mr_seats == 0 else (sum(ssd.values()) if ssd else (mr_seats if mr_seats is not None else 300))
        
        params = DipParams(
            S=S,
            mr_seats=effective_mr_seats,
            threshold=umbral,
            quota_method=quota_method,
            divisor_method=divisor_method,
            use_divisor_for_rp=(divisor_method is not None),
            max_pp=0.08,
            max_seats=max_seats,
            overrep_cap=None
        )

        print(f"[DEBUG] Usando assign_diputados con params: S={params.S}, mr_seats={params.mr_seats}, threshold={params.threshold}")

        votos_series = pd.Series(votos_ok)
        result = assign_diputados(votos_series, ssd, params)

        ok_dict = {p: (votos_ok.get(p, 0) > 0 and votos_ok.get(p, 0) / sum(votos_ok.values()) >= umbral) for p in partidos_base} if sum(votos_ok.values()) > 0 else {p: False for p in partidos_base}

        res = {
            'mr': result['mr'],
            'rp': result['rp'],
            'tot': result['tot'],
            'ok': ok_dict,
            'votos': votos_ok,
            'votos_ok': {p: v for p, v in votos_ok.items() if ok_dict[p]}
        }

        if max_seats_per_party is not None and max_seats_per_party > 0:
            # Aplica tope de escaños por partido si es necesario
            for p in res['tot']:
                if res['tot'][p] > max_seats_per_party:
                    res['tot'][p] = max_seats_per_party
        return res

    except Exception as e:
        print(f"[ERROR] procesar_diputados_parquet: {e}")
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