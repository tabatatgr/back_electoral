"""Reconstruye la lista de distritos (ENTIDAD+DISTRITO) desde el CSV de siglado.
Escribe dos archivos en outputs/:
 - distritos_from_siglado_<anio>.csv : filas con ENTIDAD (normalizada), DISTRITO (int), y la fila original del siglado
 - distritos_summary_<anio>.csv : resumen por ENTIDAD con conteo de distritos

Usa engine.recomposicion para normalizar ENTIDAD y cargar el siglado.
"""
import os
import sys
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from engine import recomposicion


def rebuild_from_siglado(path_siglado: str, anio: int):
    if not os.path.exists(path_siglado):
        raise FileNotFoundError(f"Siglado no encontrado: {path_siglado}")

    # Cargar usando el loader canónico (retorna entidad_key y distrito)
    df_sig = recomposicion._load_siglado_dip(path_siglado)

    # Normalizar ENTIDAD usando la función pública
    df_sig['entidad_normalizada'] = df_sig['entidad_key'].map(recomposicion.normalize_entidad_ascii)

    # Sort y unique
    df_out = df_sig[['entidad_normalizada','distrito']].drop_duplicates().sort_values(['entidad_normalizada','distrito']).reset_index(drop=True)

    out_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs')
    os.makedirs(out_dir, exist_ok=True)

    out_csv = os.path.join(out_dir, f'distritos_from_siglado_{anio}.csv')
    summary_csv = os.path.join(out_dir, f'distritos_summary_{anio}.csv')

    df_out.to_csv(out_csv, index=False, encoding='utf-8')

    summary = df_out.groupby('entidad_normalizada')['distrito'].count().reset_index()
    summary.columns = ['entidad_normalizada','num_distritos']
    summary.to_csv(summary_csv, index=False, encoding='utf-8')

    print(f"Escritos: {out_csv} ({len(df_out)} filas), {summary_csv} ({len(summary)} entidades)")


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--anio', type=int, default=2024)
    p.add_argument('--siglado', type=str, default=f"data/siglado-diputados-2024.csv")
    args = p.parse_args()
    rebuild_from_siglado(args.siglado, args.anio)
