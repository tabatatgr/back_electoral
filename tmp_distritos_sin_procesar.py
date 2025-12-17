"""
Encontrar los 42 distritos que no se procesaron
"""

import pandas as pd

# Cargar datos
parquet = pd.read_parquet('data/computos_diputados_2024.parquet')
siglado = pd.read_csv('data/siglado-diputados-2024.csv')

# Normalizar
parquet.columns = [c.upper() for c in parquet.columns]
siglado.columns = [c.lower() for c in siglado.columns]

def normalizar_entidad(ent):
    return str(ent).upper().strip().replace('É', 'E').replace('Á', 'A').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')

parquet['ENTIDAD_NORM'] = parquet['ENTIDAD'].apply(normalizar_entidad)
siglado['entidad_norm'] = siglado['entidad_ascii'].apply(normalizar_entidad) if 'entidad_ascii' in siglado.columns else siglado['entidad'].apply(normalizar_entidad)

FCM = ['PAN', 'PRI', 'PRD']
SHH = ['MORENA', 'PT', 'PVEM']

print("=" * 80)
print("DISTRITOS NO PROCESADOS (sin entrada en siglado)")
print("=" * 80)

distritos_sin_procesar = []

for idx in range(len(parquet)):
    distrito_data = parquet.iloc[idx]
    entidad = distrito_data['ENTIDAD_NORM']
    distrito_num = distrito_data['DISTRITO']
    
    # Calcular votos
    votos_fcm = sum(distrito_data.get(p, 0) for p in FCM)
    votos_shh = sum(distrito_data.get(p, 0) for p in SHH)
    votos_mc = distrito_data.get('MC', 0)
    
    # Determinar ganador
    if votos_fcm > votos_shh and votos_fcm > votos_mc:
        ganador_coalicion = 'FCM'
        nombre_coalicion = 'FUERZA Y CORAZON POR MEXICO'
    elif votos_shh > votos_fcm and votos_shh > votos_mc:
        ganador_coalicion = 'SHH'
        nombre_coalicion = 'SIGAMOS HACIENDO HISTORIA'
    else:
        ganador_coalicion = 'MC'
        nombre_coalicion = 'MC'
    
    # Buscar en siglado
    mask = (siglado['entidad_norm'] == entidad) & (siglado['distrito'] == distrito_num)
    siglado_distrito = siglado[mask]
    
    partido_asignado = None
    
    if ganador_coalicion == 'MC':
        partido_asignado = 'MC'
    else:
        # Buscar en siglado
        if ganador_coalicion == 'FCM':
            fila = siglado_distrito[siglado_distrito['coalicion'].str.upper().str.contains('FUERZA', na=False)]
        else:  # SHH
            fila = siglado_distrito[siglado_distrito['coalicion'].str.upper().str.contains('SIGAMOS', na=False)]
        
        if len(fila) > 0:
            partido_asignado = fila.iloc[0]['grupo_parlamentario']
    
    if partido_asignado is None:
        distritos_sin_procesar.append({
            'entidad': entidad,
            'distrito': distrito_num,
            'ganador_coalicion': ganador_coalicion,
            'votos_fcm': votos_fcm,
            'votos_shh': votos_shh,
            'votos_mc': votos_mc,
            'filas_siglado': len(siglado_distrito),
            'siglado': siglado_distrito[['coalicion', 'grupo_parlamentario']].to_dict('records') if len(siglado_distrito) > 0 else []
        })

print(f"\n⚠️  Total distritos sin procesar: {len(distritos_sin_procesar)}")

if len(distritos_sin_procesar) > 0:
    print("\n📋 Primeros 10 distritos sin procesar:")
    for d in distritos_sin_procesar[:10]:
        print(f"\n   {d['entidad']}-{d['distrito']}")
        print(f"     Ganador: {d['ganador_coalicion']}")
        print(f"     FCM: {d['votos_fcm']:,.0f} | SHH: {d['votos_shh']:,.0f} | MC: {d['votos_mc']:,.0f}")
        print(f"     Filas en siglado: {d['filas_siglado']}")
        if d['siglado']:
            for fila in d['siglado']:
                print(f"       - {fila['coalicion']}: {fila['grupo_parlamentario']}")

print("\n" + "=" * 80)
print("💡 ANÁLISIS:")
print("=" * 80)

# Contar por ganador
ganadores_sin_procesar = {}
for d in distritos_sin_procesar:
    g = d['ganador_coalicion']
    ganadores_sin_procesar[g] = ganadores_sin_procesar.get(g, 0) + 1

print(f"\nDistritos sin procesar por ganador:")
for g, count in ganadores_sin_procesar.items():
    print(f"   {g}: {count}")

print("\nPosibles causas:")
print("1. El siglado no tiene entrada para esa coalición en ese distrito")
print("2. El distrito ganó con una coalición pero no hay registro en siglado")
print("3. Problemas de normalización de nombres de entidades")
