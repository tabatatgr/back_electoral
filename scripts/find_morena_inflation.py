"""Detecta distritos MR asignados a MORENA donde los postuladores/siglado no eran solo MORENA.
Escribe 'outputs/morena_mr_suspect.csv' y muestra un resumen.
"""
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import pandas as pd
from engine.recomposicion import recompose_coalitions, _load_siglado_dip, normalize_entidad_ascii
from engine.procesar_diputados_v2 import cols_candidaturas_anio_con_coaliciones, partidos_de_col, norm_ascii_up, extraer_coaliciones_de_siglado


def find_suspects(path_parquet='data/computos_diputados_2024.parquet', path_siglado='data/siglado-diputados-2024.csv', anio=2024):
    if not os.path.exists(path_parquet):
        raise FileNotFoundError(path_parquet)
    if not os.path.exists(path_siglado):
        raise FileNotFoundError(path_siglado)

    print('[INFO] Leyendo parquet...')
    df = pd.read_parquet(path_parquet)
    df.columns = [norm_ascii_up(c) for c in df.columns]
    df['ENTIDAD'] = df['ENTIDAD'].apply(lambda x: x.decode('utf-8') if isinstance(x, bytes) else x).apply(normalize_entidad_ascii)
    df['DISTRITO'] = pd.to_numeric(df['DISTRITO'], errors='coerce').fillna(0).astype(int)

    print('[INFO] Recomponiendo coaliciones con siglado...')
    recomposed = recompose_coalitions(df, year=anio, chamber='diputados', rule='equal_residue_siglado', siglado_path=path_siglado)

    print('[INFO] Cargando siglado map...')
    sig_map = _load_siglado_dip(path_siglado)
    # mapa de coaliciones canonical: key normalizada con '_' (como hace extraer_coaliciones_de_siglado)
    coal_map = extraer_coaliciones_de_siglado(path_siglado, anio)

    candidaturas = cols_candidaturas_anio_con_coaliciones(recomposed, anio)

    suspects = []
    total_mr_morena = 0

    for _, row in recomposed.iterrows():
        entidad = row['ENTIDAD']
        distrito = int(row['DISTRITO'])

        # Encontrar columna ganadora
        max_v = -1
        winner_col = None
        for col in candidaturas:
            if col in row and row[col] > max_v:
                max_v = row[col]
                winner_col = col

        # Determinar partido ganador según reglas (coalición -> usar siglado si aplica)
        partido_ganador = None
        postuladores = []
        coalition_tokens = []

        if winner_col is None:
            continue

        # Normalizar winner_col para comparaciones simples
        winner_norm = norm_ascii_up(str(winner_col)).replace(' ', '_')

        # Si es coalición conocida (tiene '_') o nombre largo, intentar parse tokens
        coalition_tokens = partidos_de_col(winner_col)
        coalition_tokens = [norm_ascii_up(str(t)) for t in coalition_tokens if t]

        # Buscar en sig_map
        entidad_key = normalize_entidad_ascii(entidad)
        mask = (sig_map['entidad_key'] == entidad_key) & (sig_map['distrito'] == distrito)
        hit = sig_map[mask]
        siglado_dom = ''
        siglado_coal = ''
        if len(hit) > 0:
            # tomar primer match
            siglado_dom = norm_ascii_up(str(hit.iloc[0]['dominante']))
            siglado_coal = norm_ascii_up(str(hit.iloc[0].get('coalicion_key', '') or ''))
            # mapear coalicion_key a la clave usada en extraer_coaliciones_de_siglado (underscores)
            coal_key_underscore = siglado_coal.replace(' ', '_') if siglado_coal else ''
            postuladores = []
            if coal_key_underscore and coal_key_underscore in coal_map:
                postuladores = [norm_ascii_up(p) for p in coal_map[coal_key_underscore]]
            elif siglado_dom:
                postuladores = [siglado_dom]

        # Decidir ganador: si winner_col corresponde a coalición (más de 1 token)
        if len(coalition_tokens) >= 2:
            # Si siglado tiene dominante y pertenece a la coalición, usarlo
            if siglado_dom and siglado_dom in coalition_tokens:
                partido_ganador = siglado_dom
            else:
                # fallback: partido con más votos entre tokens
                votos = {p: float(row.get(p, 0) or 0) for p in coalition_tokens}
                if votos:
                    partido_ganador = max(votos, key=votos.get)
                else:
                    partido_ganador = coalition_tokens[0]
        else:
            # Partido individual
            partido_ganador = norm_ascii_up(str(winner_col))

        # Normalizar postuladores list por fila
        postuladores_set = set(postuladores)

        # Contar MR de Morena y marcar sospechosos cuando el dominio del siglado no sea MORENA
        if partido_ganador == 'MORENA':
            total_mr_morena += 1
            # Si no hay info de siglado, no marcar. Si hay postuladores y alguno no es MORENA, sospechoso.
            if len(postuladores_set) == 0:
                pass
            else:
                if any(p != 'MORENA' for p in postuladores_set):
                    suspects.append({
                        'ENTIDAD': entidad,
                        'DISTRITO': distrito,
                        'winner_col': winner_col,
                        'partido_ganador': partido_ganador,
                        'siglado_dom': siglado_dom,
                        'siglado_coal': siglado_coal,
                        'postuladores': list(postuladores_set),
                        'coalition_tokens': coalition_tokens,
                        'votos_morena': float(row.get('MORENA', 0) or 0),
                        'votos_otros_en_coal': {p: float(row.get(p, 0) or 0) for p in coalition_tokens}
                    })

    out_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs')
    os.makedirs(out_dir, exist_ok=True)
    out_csv = os.path.join(out_dir, 'morena_mr_suspect.csv')
    pd.DataFrame(suspects).to_csv(out_csv, index=False, encoding='utf-8')

    print(f"[RESULT] Total MR asignados a MORENA: {total_mr_morena}")
    print(f"[RESULT] Distritos sospechosos (MORENA pero postuladores != ['MORENA']): {len(suspects)}")
    print(f"[RESULT] CSV escrito: {out_csv}")

    return suspects


if __name__ == '__main__':
    s = find_suspects()
    if s and len(s) > 0:
        print('[SAMPLE] Primeros 10 sospechosos:')
        import json
        print(json.dumps(s[:10], indent=2))
    else:
        print('[INFO] No se detectaron sospechosos con la regla aplicada.')
