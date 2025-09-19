import os
from datetime import datetime
from typing import List, Tuple, Dict

import pandas as pd
from engine.procesar_diputados_v2 import export_scenarios, extraer_coaliciones_de_siglado


def make_scenarios() -> List[Tuple[str, Dict]]:
    """Return the full list of scenarios including S=500, S=400 and S=300 variants."""
    scenarios = []

    # Restore the original 500-seat scenarios the user asked to keep
    scenarios += [
        ('500_300MR_200RP', dict(max_seats=500, sistema='mixto', mr_seats=None, rp_seats=200)),
        ('500_250MR_250RP', dict(max_seats=500, sistema='mixto', mr_seats=250, rp_seats=250)),
        ('500_300MR_200PM', dict(max_seats=500, sistema='mixto', mr_seats=300, rp_seats=200, usar_pm=True, pm_seats=200)),
        ('500_0MR_500RP', dict(max_seats=500, sistema='rp', mr_seats=0, rp_seats=500)),
        ('500_300MR_100RP_100PM', dict(max_seats=500, sistema='mixto', mr_seats=300, rp_seats=100, usar_pm=True, pm_seats=100)),
    ]

    # Add S=400 variants
    scenarios += [
        ('400_300MR_100PM', dict(max_seats=400, sistema='mixto', mr_seats=300, rp_seats=100, usar_pm=True, pm_seats=100)),
        ('400_300MR_100RP', dict(max_seats=400, sistema='mixto', mr_seats=300, rp_seats=100)),
        ('400_300MR_50RP_50PM', dict(max_seats=400, sistema='mixto', mr_seats=300, rp_seats=50, usar_pm=True, pm_seats=50)),
        ('400_200MR_200RP', dict(max_seats=400, sistema='mixto', mr_seats=200, rp_seats=200)),
        ('400_200MR_200PM', dict(max_seats=400, sistema='mixto', mr_seats=200, rp_seats=200, usar_pm=True, pm_seats=200)),
        ('400_400RP', dict(max_seats=400, sistema='rp', mr_seats=0, rp_seats=400)),
    ]

    # Add S=300 variants
    scenarios += [
        ('300_200MR_100RP', dict(max_seats=300, sistema='mixto', mr_seats=200, rp_seats=100)),
        ('300_200MR_100PM', dict(max_seats=300, sistema='mixto', mr_seats=200, rp_seats=100, usar_pm=True, pm_seats=100)),
        ('300_200MR_50PM_50RP', dict(max_seats=300, sistema='mixto', mr_seats=200, rp_seats=50, usar_pm=True, pm_seats=50)),
        ('300_300RP', dict(max_seats=300, sistema='rp', mr_seats=0, rp_seats=300)),
    ]

    return scenarios


def run_for_year(anio: int, out_dir: str = 'outputs') -> str:
    parquet = f'data/computos_diputados_{anio}.parquet'
    siglado = f'data/siglado-diputados-{anio}.csv'

    scenarios = make_scenarios()

    # Ensure output directory exists
    os.makedirs(out_dir, exist_ok=True)

    out = export_scenarios(parquet, siglado, scenarios, out_path=None, anio=anio, print_debug=False)

    # Post-process: add per-scenario coalition/solo summaries into a new Excel
    try:
        sheets = pd.read_excel(out, sheet_name=None)
        coaliciones = extraer_coaliciones_de_siglado(siglado, anio)

        # Build summary sheets
        summaries = {}
        parties_in_coalitions = set()
        for cname, plist in coaliciones.items():
            parties_in_coalitions.update(plist)

        for sheet_name, df in sheets.items():
            # Ensure expected columns
            cols = [c.lower() for c in df.columns]
            col_map = {c.lower(): c for c in df.columns}
            # normalize column access
            def g(col):
                return df[col_map[col]] if col in col_map else 0

            # compute coalition aggregates (mr/rp/pm/tot)
            rows = []
            for cname, plist in coaliciones.items():
                mask = df['partido'].isin(plist)
                mr = int(df.loc[mask, 'mr'].sum()) if 'mr' in df.columns else 0
                rp = int(df.loc[mask, 'rp'].sum()) if 'rp' in df.columns else 0
                pm = int(df.loc[mask, 'pm'].sum()) if 'pm' in df.columns else 0
                tot = int(df.loc[mask, 'tot'].sum()) if 'tot' in df.columns else 0
                rows.append({'group_type': 'coalicion', 'name': cname, 'mr': mr, 'rp': rp, 'pm': pm, 'tot': tot})

            # solo parties (not in any coalition)
            solo_mask = ~df['partido'].isin(parties_in_coalitions)
            for _, r in df.loc[solo_mask].iterrows():
                rows.append({'group_type': 'party', 'name': r['partido'], 'mr': int(r.get('mr', 0)), 'rp': int(r.get('rp', 0)), 'pm': int(r.get('pm', 0)), 'tot': int(r.get('tot', 0))})

            summaries[sheet_name + '_summary'] = pd.DataFrame(rows)

        # Write a new Excel that includes original sheets and summary sheets
        base, ext = os.path.splitext(out)
        out_with = f"{base}.with_summaries{ext}"
        with pd.ExcelWriter(out_with, engine='openpyxl') as writer:
            # original sheets
            for name, df in sheets.items():
                df.to_excel(writer, sheet_name=name, index=False)
            # summary sheets
            for name, sdf in summaries.items():
                # Excel sheet names max 31 chars
                writer.sheets
                safe = name[:31]
                sdf.to_excel(writer, sheet_name=safe, index=False)

        return out_with
    except Exception as e:
        print('Warning: no se pudo agregar resúmenes por coalición:', e)
        return out


if __name__ == '__main__':
    years = [2024, 2021]
    generated = []
    for y in years:
        print(f'Ejecutando escenario {y} con escenarios S=500/400/300')
        try:
            out = run_for_year(y)
            print('Exportado a', out)
            generated.append(out)
        except Exception as e:
            print(f'Error ejecutando para {y}:', e)

    if generated:
        print('\nGenerados:', ' '.join(generated))
