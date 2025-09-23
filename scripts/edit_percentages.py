"""scripts/edit_percentages.py

Herramienta mínima para editar/inyectar porcentajes de votos por partido y ejecutar
`procesar_diputados_v2`.

Uso rápido desde línea de comandos (pwsh):
  $env:PYTHONPATH = '.'; python .\scripts\edit_percentages.py --file my_perc.json

El JSON esperado es un objeto partido -> porcentaje (puede sumar 100 o 1.0). Si no suma 100,
el script normaliza y avisa.

El script devuelve un resumen impreso en stdout y opcionalmente guarda el resultado en
outputs/last_run_preview.json
"""
import argparse
import json
import os
import sys
from datetime import datetime

# asegurarnos que el repo está en PYTHONPATH
sys.path.insert(0, os.getcwd())

from engine.procesar_diputados_v2 import procesar_diputados_v2, parties_for


def load_perc(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError('JSON debe ser un objeto partido->porcentaje')
    return data


def normalize_perc(d):
    vals = list(d.values())
    s = sum(vals)
    if s == 0:
        raise ValueError('La suma de porcentajes es 0')
    # aceptar percentuales en 0..1 o 0..100
    if all(v <= 1 for v in vals):
        # asumimos fracciones (suma ~1)
        factor = 1.0/s
    else:
        factor = 100.0/s
    return {k: float(v)*factor for k, v in d.items()}, factor


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--file', '-f', help='Archivo JSON con partido->porcentaje', required=True)
    p.add_argument('--anio', type=int, default=2024)
    p.add_argument('--max-seats', type=int, default=128)
    p.add_argument('--sistema', choices=['rp','mr','mixto'], default='rp')
    p.add_argument('--umbral', type=float, default=3.0, help='Umbral en porcentaje (ej. 3 -> 3%)')
    p.add_argument('--out', help='Guardar resumen a archivo JSON en outputs/', default=None)
    args = p.parse_args()

    perc = load_perc(args.file)
    try:
        norm, factor = normalize_perc(perc)
    except ValueError as e:
        print('ERROR:', e)
        sys.exit(1)

    if abs(sum(norm.values()) - (100.0 if factor >= 1 else 1.0)) > 1e-6:
        # normalizamos para que sumen exactamente 100
        s = sum(norm.values())
        norm = {k: v* (100.0/s) for k, v in norm.items()}

    parties = parties_for(args.anio)

    # Convertir a formato esperado por procesar_diputados_v2: mapa partido->porcentaje
    # procesar_diputados_v2 acepta porcentajes en 0..100 (según usos previos)
    votos_redistribuidos = {k: norm.get(k, 0.0) for k in parties}

    print('Ejecutando procesar_diputados_v2 con sistema=%s, anio=%s, max_seats=%d' % (
        args.sistema, args.anio, args.max_seats))
    print('Sum porcentajes:', sum(votos_redistribuidos.values()))

    res = procesar_diputados_v2(
        path_parquet='data/computos_diputados_2024.parquet',
        path_siglado='data/siglado-diputados-2024.csv',
        anio=args.anio,
        max_seats=args.max_seats,
        sistema=args.sistema,
        mr_seats=0 if args.sistema=='rp' else int(args.max_seats*0.25),
        rp_seats=args.max_seats if args.sistema=='rp' else int(args.max_seats*0.75),
        umbral=args.umbral,
        usar_coaliciones=True,
        votos_redistribuidos=votos_redistribuidos,
        print_debug=False
    )

    summary = {
        'keys': list(res.keys()),
        'sum_votos': sum(res.get('votos', {}).values()) if res.get('votos') else None,
        'sum_tot_seats': sum(res.get('tot', {}).values()) if res.get('tot') else None,
        'meta_keys': list(res.get('meta', {}).keys()) if res.get('meta') else None
    }

    print('\nResumen:')
    print(json.dumps(summary, indent=2))

    if args.out:
        # Allow user to pass either a filename relative to outputs/ or a path
        candidate = args.out
        if os.path.isabs(candidate):
            fname = candidate
        else:
            # If user included 'outputs/' prefix, respect it; otherwise place inside outputs/
            if candidate.startswith('outputs' + os.sep) or candidate.startswith('outputs/'):
                fname = candidate
            else:
                fname = os.path.join('outputs', candidate)

        parent = os.path.dirname(fname) or '.'
        if parent:
            os.makedirs(parent, exist_ok=True)

        # Guardar el resultado completo para facilitar inspección (mr, rp, votos, etc.)
        to_dump = {
            'params': vars(args),
            'summary': summary,
            'result_meta': res.get('meta'),
            'result_full': res
        }
        with open(fname, 'w', encoding='utf-8') as f:
            json.dump(to_dump, f, default=str, indent=2)
        print('Guardado resumen en', fname)


if __name__ == '__main__':
    main()
