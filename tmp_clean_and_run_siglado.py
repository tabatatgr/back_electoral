import os
import pandas as pd
from engine.procesar_diputados_v2 import procesar_diputados_v2

SIGLADO = 'data/siglado-diputados-2024.csv'
CLEAN = 'data/siglado-diputados-2024.clean.csv'
PARQUET = 'data/computos_diputados_2024.parquet'

print('Leyendo siglado original...')
df = pd.read_csv(SIGLADO)
print('Filas originales:', len(df))

# Normalizar entidad_ascii: strip y upper
if 'entidad_ascii' in df.columns:
    df['entidad_ascii'] = df['entidad_ascii'].astype(str).str.strip().str.upper()
else:
    df['entidad_ascii'] = df['entidad'].astype(str).str.strip().str.upper()

# Asegurar distrito como int
try:
    df['distrito'] = df['distrito'].astype(int)
except Exception:
    df['distrito'] = pd.to_numeric(df['distrito'], errors='coerce').fillna(0).astype(int)

# Agrupar por entidad_ascii,distrito y tomar la moda para coalicion y grupo_parlamentario
agg = df.groupby(['entidad_ascii', 'distrito']).agg({'coalicion': lambda x: x.mode().iloc[0] if len(x.mode())>0 else x.iloc[0],
                                                      'grupo_parlamentario': lambda x: x.mode().iloc[0] if len(x.mode())>0 else x.iloc[0]}).reset_index()

print('Filas luego de agrupar (pares únicos):', len(agg))
agg.to_csv(CLEAN, index=False)
print('Guardado siglado limpio en', CLEAN)

# Respaldar original y sobrescribir con limpio para que el procesador use la versión normalizada
backup = SIGLADO + '.bak'
print('\nRespaldando original en', backup)
try:
    if os.path.exists(backup):
        os.remove(backup)
    os.replace(SIGLADO, backup)
    os.replace(CLEAN, SIGLADO)
    replaced = True
except Exception as e:
    print('Error al respaldar/sobrescribir siglado:', e)
    replaced = False

try:
    print('\nEjecutando motor sin forzar MR (mr_seats=None)...')
    res = procesar_diputados_v2(path_parquet=PARQUET, anio=2024, path_siglado=SIGLADO, max_seats=500, sistema='mixto', mr_seats=None, rp_seats=None, usar_coaliciones=True, print_debug=True)

    # Imprimir resumen compacto
    print('\nResumen MR/RP/TOT por partido:')
    mr = res.get('mr', {})
    rp = res.get('rp', {})
    tot = res.get('tot', {})

    def print_top(d, title):
        print(f'-- {title} --')
        for p, v in sorted(d.items(), key=lambda x: -x[1])[:20]:
            print(f'{p}: {v}')

    print_top(mr, 'MR')
    print_top(rp, 'RP')
    print_top(tot, 'TOT')

    print('\nSuma totales reportada:', sum(tot.values()) if tot else 'N/A')
    print('Entrada meta (req_id):', res.get('meta', {}).get('req_id'))

finally:
    # Restaurar original
    if replaced:
        try:
            print('\nRestaurando archivo siglado original desde backup...')
            if os.path.exists(SIGLADO):
                os.remove(SIGLADO)
            os.replace(backup, SIGLADO)
            print('Restaurado.')
        except Exception as e:
            print('Error al restaurar original:', e)
