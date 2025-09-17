# Runner to invoke procesar_diputados_v2 with legacy postuladores flag and dump ssd_used
import os
from engine.procesar_diputados_v2 import procesar_diputados_v2

# Activate global legacy flag used by the processor
import engine.procesar_diputados_v2 as procmod
setattr(procmod, '__LEGACY_POSTULADORES_FLAG__', True)

if __name__ == '__main__':
    print('Running procesar_diputados_v2 with legacy_postuladores enabled...')
    res = procesar_diputados_v2(
        path_parquet='data/computos_diputados_2024.parquet',
        path_siglado='data/siglado-diputados-2024.corrected.csv',
        print_debug=False
    )
    # Try to extract the MR vector used (it should be in res['meta'] or in returned structure of seats)
    # We will try common keys and write outputs/ssd_used.csv
    import pandas as pd
    outp = 'outputs'
    os.makedirs(outp, exist_ok=True)
    ssd = None
    # Look in common places
    if isinstance(res, dict):
        if 'meta' in res and isinstance(res['meta'], dict):
            if 'ssd' in res['meta']:
                ssd = res['meta']['ssd']
        if 'seats' in res and isinstance(res['seats'], dict):
            # not MR vector
            pass
    # As fallback, try to import engine.procesar_diputados_v2.mr_aligned if present
    try:
        ssd = getattr(procmod, 'LAST_SSD_USED', None) or ssd
    except Exception:
        pass

    if ssd is not None:
        df = pd.DataFrame(list(ssd.items()), columns=['party','mr_used'])
        df.to_csv(os.path.join(outp, 'ssd_used.csv'), index=False)
        print('Wrote outputs/ssd_used.csv')
    else:
        print('No MR vector (ssd) found in result; check processor to instrument LAST_SSD_USED')
    print('Done')
