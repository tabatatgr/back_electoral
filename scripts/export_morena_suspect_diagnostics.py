"""Exporta diagnóstico por distrito para los sospechosos listados en outputs/morena_mr_suspect.csv
Genera outputs/morena_mr_suspect_diagnostics.xlsx con una hoja 'suspects' que contiene:
 - ENTIDAD, DISTRITO, ganador_reportado, votos_por_partido, siglado_dom, siglado_coal, row_from_parquet (selected cols)
"""
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import pandas as pd
from engine.recomposicion import normalize_entidad_ascii
from engine.procesar_diputados_v2 import norm_ascii_up


def export_diagnostics(suspect_csv='outputs/morena_mr_suspect.csv', path_parquet='data/computos_diputados_2024.parquet', path_siglado='data/siglado-diputados-2024.csv'):
    if not os.path.exists(suspect_csv):
        raise FileNotFoundError(suspect_csv)
    if not os.path.exists(path_parquet):
        raise FileNotFoundError(path_parquet)
    if not os.path.exists(path_siglado):
        raise FileNotFoundError(path_siglado)

    suspects = pd.read_csv(suspect_csv, dtype=str, keep_default_na=False)
    suspects['DISTRITO'] = suspects['DISTRITO'].astype(int)

    # cargar recomposed para tener votos por partido
    df = pd.read_parquet(path_parquet)
    df.columns = [norm_ascii_up(c) for c in df.columns]
    df['ENTIDAD'] = df['ENTIDAD'].apply(lambda x: x.decode('utf-8') if isinstance(x, bytes) else x).apply(normalize_entidad_ascii)
    df['DISTRITO'] = pd.to_numeric(df['DISTRITO'], errors='coerce').fillna(0).astype(int)

    # recomponer para obtener votos por partido tal como se usan en el procesador
    from engine.recomposicion import recompose_coalitions
    recomposed = recompose_coalitions(df, year=2024, chamber='diputados', rule='equal_residue_siglado', siglado_path=path_siglado)

    # cargar siglado raw
    sig_raw = pd.read_csv(path_siglado, dtype=str, keep_default_na=False)
    sig_raw_cols = [c for c in sig_raw.columns]

    rows = []
    for _, s in suspects.iterrows():
        ent = s['ENTIDAD']
        dist = int(s['DISTRITO'])
        ent_norm = normalize_entidad_ascii(ent)

        # recomposed row
        rc_mask = (recomposed['ENTIDAD'] == ent_norm) & (recomposed['DISTRITO'] == dist)
        rc_row = recomposed[rc_mask]
        rc_ser = rc_row.iloc[0].to_dict() if len(rc_row) > 0 else {}

        # original parquet row
        pq_mask = (df['ENTIDAD'] == ent_norm) & (df['DISTRITO'] == dist)
        pq_row = df[pq_mask]
        pq_ser = pq_row.iloc[0].to_dict() if len(pq_row) > 0 else {}

        # siglado raw row(s)
        # try match by entidad or entidad_ascii and distrito
        sig_match = None
        if 'entidad_ascii' in sig_raw.columns:
            sig_mask = (norm_ascii_up(sig_raw['entidad_ascii']) == ent_norm) & (sig_raw['distrito'].astype(str).str.extract(r'(\d+)')[0].fillna('0').astype(int) == dist)
            sig_match = sig_raw[sig_mask]
        if (sig_match is None or len(sig_match)==0) and 'entidad' in sig_raw.columns:
            sig_mask = (norm_ascii_up(sig_raw['entidad']) == ent_norm) & (sig_raw['distrito'].astype(str).str.extract(r'(\d+)')[0].fillna('0').astype(int) == dist)
            sig_match = sig_raw[sig_mask]
        sig_ser = sig_match.iloc[0].to_dict() if sig_match is not None and len(sig_match)>0 else {}

        row = {
            'ENTIDAD': ent_norm,
            'DISTRITO': dist,
            'winner_col': s.get('winner_col',''),
            'partido_ganador': s.get('partido_ganador',''),
            'siglado_dom': s.get('siglado_dom',''),
            'siglado_coal': s.get('siglado_coal','')
        }

        # incluir votos por partido del recomposed (limitados a partidos comunes)
        for p in ['MORENA','PAN','PRI','PRD','PVEM','PT','MC','PES','NA','FXM','RSP']:
            row[f'votes_{p}'] = float(rc_ser.get(p, 0) or 0)
        # incluir few original parquet cols
        for c in ['TOTAL_BOLETAS']:
            row[c] = pq_ser.get(c,'')

        # incluir algunas columnas del siglado raw
        for c in sig_raw_cols:
            row[f'sig_{c}'] = sig_ser.get(c,'')

        rows.append(row)

    out_df = pd.DataFrame(rows)
    out_path = os.path.join(os.path.dirname(suspect_csv), '..', 'outputs', 'morena_mr_suspect_diagnostics.xlsx')
    out_path = os.path.abspath(out_path)
    out_dir = os.path.dirname(out_path)
    os.makedirs(out_dir, exist_ok=True)

    out_df.to_excel(out_path, index=False)
    print(f'[DONE] Diagnostics written to {out_path} ({len(out_df)} rows)')
    return out_path


if __name__ == '__main__':
    p = export_diagnostics()
    print(p)
