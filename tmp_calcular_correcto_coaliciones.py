"""
Verificar si el motor está calculando correctamente las coaliciones
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

# Definir coaliciones
FCM = ['PAN', 'PRI', 'PRD']  # FUERZA Y CORAZON POR MEXICO
SHH = ['MORENA', 'PT', 'PVEM']  # SIGAMOS HACIENDO HISTORIA

print("=" * 80)
print("CÁLCULO CORRECTO DE GANADORES CON COALICIONES")
print("=" * 80)

print("\n🔍 Coaliciones:")
print(f"   FCM (Fuerza y Corazón por México): {', '.join(FCM)}")
print(f"   SHH (Sigamos Haciendo Historia): {', '.join(SHH)}")

print("\n" + "=" * 80)
print("MUESTRA: Primeros 10 distritos")
print("=" * 80)

conteo_por_coalicion = {'FCM': 0, 'SHH': 0, 'OTRO': 0}
conteo_por_partido = {}

for idx in range(min(10, len(parquet))):
    distrito_data = parquet.iloc[idx]
    entidad = distrito_data['ENTIDAD_NORM']
    distrito_num = distrito_data['DISTRITO']
    
    # Calcular votos de coaliciones
    votos_fcm = sum(distrito_data.get(p, 0) for p in FCM)
    votos_shh = sum(distrito_data.get(p, 0) for p in SHH)
    votos_mc = distrito_data.get('MC', 0)
    
    # Determinar ganador
    if votos_fcm > votos_shh and votos_fcm > votos_mc:
        ganador_coalicion = 'FCM'
    elif votos_shh > votos_fcm and votos_shh > votos_mc:
        ganador_coalicion = 'SHH'
    elif votos_mc > votos_fcm and votos_mc > votos_shh:
        ganador_coalicion = 'MC'
    else:
        ganador_coalicion = 'EMPATE'
    
    # Buscar en siglado qué partido se lleva el escaño
    mask = (siglado['entidad_norm'] == entidad) & (siglado['distrito'] == distrito_num)
    siglado_distrito = siglado[mask]
    
    # Buscar el grupo_parlamentario para la coalición ganadora
    partido_asignado = None
    if ganador_coalicion in ['FCM', 'SHH']:
        coalicion_nombre = 'FUERZA Y CORAZON POR MEXICO' if ganador_coalicion == 'FCM' else 'SIGAMOS HACIENDO HISTORIA'
        fila_coalicion = siglado_distrito[siglado_distrito['coalicion'].str.upper().str.contains(coalicion_nombre.upper(), na=False)]
        if len(fila_coalicion) > 0:
            partido_asignado = fila_coalicion.iloc[0]['grupo_parlamentario']
    elif ganador_coalicion == 'MC':
        partido_asignado = 'MC'
    
    print(f"\n📍 {entidad}-{distrito_num}")
    print(f"   FCM: {votos_fcm:>10,.0f} ({', '.join(f'{p}={distrito_data.get(p, 0):,.0f}' for p in FCM)})")
    print(f"   SHH: {votos_shh:>10,.0f} ({', '.join(f'{p}={distrito_data.get(p, 0):,.0f}' for p in SHH)})")
    print(f"   MC:  {votos_mc:>10,.0f}")
    print(f"   👑 Ganador: {ganador_coalicion}")
    print(f"   📋 Partido asignado (según siglado): {partido_asignado}")
    
    if partido_asignado:
        conteo_por_partido[partido_asignado] = conteo_por_partido.get(partido_asignado, 0) + 1

print("\n" + "=" * 80)
print("CONTEO COMPLETO EN LOS 300 DISTRITOS")
print("=" * 80)

# Hacer el conteo completo
conteo_completo = {}
for idx in range(len(parquet)):
    distrito_data = parquet.iloc[idx]
    entidad = distrito_data['ENTIDAD_NORM']
    distrito_num = distrito_data['DISTRITO']
    
    # Calcular votos de coaliciones
    votos_fcm = sum(distrito_data.get(p, 0) for p in FCM)
    votos_shh = sum(distrito_data.get(p, 0) for p in SHH)
    votos_mc = distrito_data.get('MC', 0)
    
    # Determinar ganador
    if votos_fcm > votos_shh and votos_fcm > votos_mc:
        ganador_coalicion = 'FCM'
    elif votos_shh > votos_fcm and votos_shh > votos_mc:
        ganador_coalicion = 'SHH'
    else:
        ganador_coalicion = 'MC'
    
    # Buscar en siglado
    mask = (siglado['entidad_norm'] == entidad) & (siglado['distrito'] == distrito_num)
    siglado_distrito = siglado[mask]
    
    partido_asignado = None
    if ganador_coalicion == 'FCM':
        fila = siglado_distrito[siglado_distrito['coalicion'].str.upper().str.contains('FUERZA', na=False)]
        if len(fila) > 0:
            partido_asignado = fila.iloc[0]['grupo_parlamentario']
    elif ganador_coalicion == 'SHH':
        fila = siglado_distrito[siglado_distrito['coalicion'].str.upper().str.contains('SIGAMOS', na=False)]
        if len(fila) > 0:
            partido_asignado = fila.iloc[0]['grupo_parlamentario']
    else:
        partido_asignado = 'MC'
    
    if partido_asignado:
        conteo_completo[partido_asignado] = conteo_completo.get(partido_asignado, 0) + 1

print("\n📊 MR por partido (calculando correctamente con coaliciones):")
for partido in sorted(conteo_completo.keys()):
    print(f"   {partido:10s}: {conteo_completo[partido]:>3}")

print(f"\n   {'TOTAL':10s}: {sum(conteo_completo.values()):>3}")

print("\n" + "=" * 80)
print("COMPARACIÓN CON MOTOR Y OFICIAL")
print("=" * 80)

# Datos del motor (de diagnostico anterior)
motor = {'MORENA': 160, 'PVEM': 58, 'PT': 38, 'PAN': 33, 'PRI': 9, 'MC': 1, 'PRD': 0}

# Datos oficiales (total - RP)
oficial = {
    'MORENA': 257 - 85,  # 172
    'PAN': 71 - 35,      # 36
    'PVEM': 60 - 18,     # 42
    'PT': 47 - 11,       # 36
    'PRI': 36 - 23,      # 13
    'MC': 27 - 23,       # 4
    'PRD': 1 - 5         # -4 (no tiene sentido, PRD debe tener 0 MR)
}

print(f"\n{'Partido':<10} {'Correcto':>10} {'Motor':>10} {'Oficial':>10}")
print("-" * 45)

todos_partidos = set(conteo_completo.keys()) | set(motor.keys()) | set(oficial.keys())
for partido in sorted(todos_partidos):
    correcto = conteo_completo.get(partido, 0)
    motor_val = motor.get(partido, 0)
    oficial_val = oficial.get(partido, 0)
    print(f"{partido:<10} {correcto:>10} {motor_val:>10} {oficial_val:>10}")

print("\n" + "=" * 80)
print("💡 CONCLUSIÓN:")
print("=" * 80)

print("""
Si calculamos correctamente sumando votos de coaliciones:
1. Sumamos PAN+PRI+PRD para FCM
2. Sumamos MORENA+PT+PVEM para SHH
3. Comparamos con MC individual
4. Asignamos según grupo_parlamentario del siglado

¿Esto coincide con los datos oficiales?
""")
