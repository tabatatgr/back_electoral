"""
LÓGICA CORRECTA DEL SIGLADO:
1. El siglado lista quién PUEDE recibir escaños en cada distrito
2. Si gana alguien que NO está en siglado, el escaño va a quien SÍ esté
3. Si hay múltiples en siglado, se asigna según quién tenga más votos entre los listados
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
print("LÓGICA CORRECTA: Asignar escaños según siglado")
print("=" * 80)

print("\n📋 REGLA:")
print("1. Calcular qué coalición ganó (FCM, SHH, o MC)")
print("2. Buscar en siglado qué partidos están listados para ese distrito")
print("3. Si la coalición ganadora tiene entrada en siglado → usar ese partido")
print("4. Si NO tiene entrada → asignar al que SÍ esté en el siglado")

print("\n" + "=" * 80)
print("MUESTRA: Primeros 10 distritos")
print("=" * 80)

for idx in range(min(10, len(parquet))):
    distrito_data = parquet.iloc[idx]
    entidad = distrito_data['ENTIDAD_NORM']
    distrito_num = distrito_data['DISTRITO']
    
    # Calcular votos de coaliciones
    votos_fcm = sum(distrito_data.get(p, 0) for p in FCM)
    votos_shh = sum(distrito_data.get(p, 0) for p in SHH)
    votos_mc = distrito_data.get('MC', 0)
    
    # Determinar ganador por VOTOS
    if votos_fcm > votos_shh and votos_fcm > votos_mc:
        ganador_coalicion = 'FCM'
    elif votos_shh > votos_fcm and votos_shh > votos_mc:
        ganador_coalicion = 'SHH'
    else:
        ganador_coalicion = 'MC'
    
    # Buscar en siglado qué partidos están listados
    mask = (siglado['entidad_norm'] == entidad) & (siglado['distrito'] == distrito_num)
    siglado_distrito = siglado[mask]
    
    # Extraer partidos por coalición en el siglado
    partidos_fcm_siglado = siglado_distrito[siglado_distrito['coalicion'].str.upper().str.contains('FUERZA', na=False)]
    partidos_shh_siglado = siglado_distrito[siglado_distrito['coalicion'].str.upper().str.contains('SIGAMOS', na=False)]
    
    partido_asignado = None
    explicacion = ""
    
    # REGLA: Si el ganador está en siglado, usar su partido
    if ganador_coalicion == 'FCM' and len(partidos_fcm_siglado) > 0:
        partido_asignado = partidos_fcm_siglado.iloc[0]['grupo_parlamentario']
        explicacion = f"FCM ganó y ESTÁ en siglado → {partido_asignado}"
    elif ganador_coalicion == 'SHH' and len(partidos_shh_siglado) > 0:
        partido_asignado = partidos_shh_siglado.iloc[0]['grupo_parlamentario']
        explicacion = f"SHH ganó y ESTÁ en siglado → {partido_asignado}"
    elif ganador_coalicion == 'MC':
        # MC compite individual
        partido_asignado = 'MC'
        explicacion = "MC ganó (individual)"
    else:
        # El ganador NO está en siglado → asignar al que SÍ esté
        if len(partidos_fcm_siglado) > 0:
            partido_asignado = partidos_fcm_siglado.iloc[0]['grupo_parlamentario']
            explicacion = f"{ganador_coalicion} ganó pero NO está en siglado → va para FCM: {partido_asignado}"
        elif len(partidos_shh_siglado) > 0:
            partido_asignado = partidos_shh_siglado.iloc[0]['grupo_parlamentario']
            explicacion = f"{ganador_coalicion} ganó pero NO está en siglado → va para SHH: {partido_asignado}"
        else:
            # Caso extraño: no hay nadie en siglado
            explicacion = f"{ganador_coalicion} ganó pero siglado está VACÍO"
    
    print(f"\n📍 {entidad}-{distrito_num}")
    print(f"   FCM: {votos_fcm:>10,.0f} | SHH: {votos_shh:>10,.0f} | MC: {votos_mc:>10,.0f}")
    print(f"   Ganador votos: {ganador_coalicion}")
    print(f"   En siglado: FCM={'✓' if len(partidos_fcm_siglado) > 0 else '✗'} | SHH={'✓' if len(partidos_shh_siglado) > 0 else '✗'}")
    print(f"   → {explicacion}")

print("\n" + "=" * 80)
print("CONTEO COMPLETO CON LÓGICA CORRECTA")
print("=" * 80)

conteo_final = {}

for idx in range(len(parquet)):
    distrito_data = parquet.iloc[idx]
    entidad = distrito_data['ENTIDAD_NORM']
    distrito_num = distrito_data['DISTRITO']
    
    # Calcular votos
    votos_fcm = sum(distrito_data.get(p, 0) for p in FCM)
    votos_shh = sum(distrito_data.get(p, 0) for p in SHH)
    votos_mc = distrito_data.get('MC', 0)
    
    # Ganador
    if votos_fcm > votos_shh and votos_fcm > votos_mc:
        ganador_coalicion = 'FCM'
    elif votos_shh > votos_fcm and votos_shh > votos_mc:
        ganador_coalicion = 'SHH'
    else:
        ganador_coalicion = 'MC'
    
    # Siglado
    mask = (siglado['entidad_norm'] == entidad) & (siglado['distrito'] == distrito_num)
    siglado_distrito = siglado[mask]
    
    partidos_fcm_siglado = siglado_distrito[siglado_distrito['coalicion'].str.upper().str.contains('FUERZA', na=False)]
    partidos_shh_siglado = siglado_distrito[siglado_distrito['coalicion'].str.upper().str.contains('SIGAMOS', na=False)]
    
    partido_asignado = None
    
    if ganador_coalicion == 'FCM' and len(partidos_fcm_siglado) > 0:
        partido_asignado = partidos_fcm_siglado.iloc[0]['grupo_parlamentario']
    elif ganador_coalicion == 'SHH' and len(partidos_shh_siglado) > 0:
        partido_asignado = partidos_shh_siglado.iloc[0]['grupo_parlamentario']
    elif ganador_coalicion == 'MC':
        partido_asignado = 'MC'
    else:
        # Ganador NO en siglado → va al que SÍ esté
        if len(partidos_fcm_siglado) > 0:
            partido_asignado = partidos_fcm_siglado.iloc[0]['grupo_parlamentario']
        elif len(partidos_shh_siglado) > 0:
            partido_asignado = partidos_shh_siglado.iloc[0]['grupo_parlamentario']
    
    if partido_asignado:
        conteo_final[partido_asignado] = conteo_final.get(partido_asignado, 0) + 1

print("\n📊 MR por partido (lógica correcta):")
for partido in sorted(conteo_final.keys()):
    print(f"   {partido:10s}: {conteo_final[partido]:>3}")

print(f"\n   {'TOTAL':10s}: {sum(conteo_final.values()):>3}")

print("\n" + "=" * 80)
print("COMPARACIÓN FINAL")
print("=" * 80)

# Datos del siglado
siglado_conteo = siglado['grupo_parlamentario'].value_counts().to_dict()

# Datos oficiales (total - RP)
oficial_mr = {
    'MORENA': 257 - 85,
    'PAN': 71 - 35,
    'PVEM': 60 - 18,
    'PT': 47 - 11,
    'PRI': 36 - 23,
    'MC': 27 - 23,
    'PRD': max(1, 1)
}

print(f"\n{'Partido':<10} {'Mi Cálculo':>12} {'Siglado':>10} {'Oficial':>10} {'Diff Oficial':>13}")
print("-" * 60)

todos_partidos = set(conteo_final.keys()) | set(siglado_conteo.keys()) | set(oficial_mr.keys())
for partido in sorted(todos_partidos):
    mi_calc = conteo_final.get(partido, 0)
    siglado_val = siglado_conteo.get(partido, 0)
    oficial_val = oficial_mr.get(partido, 0)
    diff = mi_calc - oficial_val
    marca = "✅" if diff == 0 else "⚠️"
    print(f"{partido:<10} {mi_calc:>12} {siglado_val:>10} {oficial_val:>10} {diff:>12} {marca}")

print("\n" + "=" * 80)
print("💡 CONCLUSIÓN:")
print("=" * 80)

mi_total = sum(conteo_final.values())
oficial_total = sum(v for v in oficial_mr.values() if v > 0)

print(f"\nMi cálculo procesa: {mi_total} distritos (de 300)")

if mi_total == 300:
    print("✅ Todos los distritos procesados")
else:
    print(f"⚠️  Faltan {300 - mi_total} distritos por procesar")

diff_total = sum(abs(conteo_final.get(p, 0) - oficial_mr.get(p, 0)) for p in todos_partidos)

if diff_total < 20:
    print(f"\n✅ Mi cálculo está MUY CERCA del oficial (diff total: {diff_total})")
else:
    print(f"\n⚠️  Aún hay diferencias significativas (diff total: {diff_total})")
