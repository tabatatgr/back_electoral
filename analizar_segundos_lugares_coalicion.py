"""
Análisis de Segundos Lugares en Distritos Perdidos por SHH

Este script analiza los distritos donde la coalición SHH (MORENA+PT+PVEM) perdió
en 2024, determinando cuál partido de SHH quedó mejor posicionado en cada uno.

CONCEPTO CLAVE:
- "Ganador por coalición" = suma de votos de partidos aliados
- "Posición individual" = ranking de cada partido por separado

EJEMPLO:
Un distrito puede tener:
  Por coalición: FCM gana (PAN+PRI+PRD = 80,000) vs SHH pierde (MORENA+PT+PVEM = 70,000)
  Por partido individual: MORENA 1º (55,000) > PAN 2º (40,000) > PRI 3º (25,000)...
  
Resultado: FCM ganó como coalición, pero MORENA fue 1º individualmente.
La columna 'posicion_shh' = 1 (porque MORENA quedó en primer lugar del ranking individual)

Ver README_analisis_segundos_lugares.md para más detalles.
"""

import pandas as pd
from collections import Counter

# Cargar datos
parquet = pd.read_parquet('data/computos_diputados_2024.parquet')

# Definir coaliciones
FCM = ['PAN', 'PRI', 'PRD']  # Fuerza y Corazón por México
SHH = ['MORENA', 'PT', 'PVEM']  # Sigamos Haciendo Historia
MC = ['MC']

print("=" * 80)
print("ANÁLISIS: SEGUNDOS LUGARES EN DISTRITOS PERDIDOS POR MORENA+PT+PVEM")
print("=" * 80)
print("\nConcepto: Aunque SHH perdió como COALICIÓN, analizamos qué partido")
print("individual de SHH (MORENA, PT o PVEM) quedó mejor en el ranking de")
print("TODOS los partidos (no solo de SHH).")
print("\nEjemplo: Si MORENA fue 1º individual pero SHH perdió como coalición,")
print("significa que FCM sumó más votos totales aunque ningún partido de FCM")
print("individualmente superó a MORENA.")
print("=" * 80)

# Almacenar resultados
segundo_lugar_por_partido = Counter()
detalle_por_distrito = []

for idx, row in parquet.iterrows():
    entidad = row.get('ENTIDAD_NORM', row.get('ENTIDAD', ''))
    distrito = row['DISTRITO']
    
    # Calcular votos por coalición
    votos_shh = sum(row.get(p, 0) for p in SHH)
    votos_fcm = sum(row.get(p, 0) for p in FCM)
    votos_mc = row.get('MC', 0)
    
    # Determinar ganador por coalición
    votos_coaliciones = {
        'SHH': votos_shh,
        'FCM': votos_fcm,
        'MC': votos_mc
    }
    ganador_coal = max(votos_coaliciones, key=votos_coaliciones.get)
    
    # ¿La coalición SHH perdió?
    if ganador_coal != 'SHH':
        # Crear ranking de partidos individuales (no por coalición)
        # Esto nos permite ver qué partido individual quedó mejor,
        # independientemente del resultado por coalición
        votos_partidos = {
            'MORENA': row.get('MORENA', 0),
            'PT': row.get('PT', 0),
            'PVEM': row.get('PVEM', 0),
            'PAN': row.get('PAN', 0),
            'PRI': row.get('PRI', 0),
            'PRD': row.get('PRD', 0),
            'MC': row.get('MC', 0)
        }
        
        ranking_partidos = sorted(votos_partidos.items(), key=lambda x: -x[1])
        
        # Buscar el partido de SHH mejor posicionado en el ranking de TODOS los partidos
        # posicion_shh = en qué lugar quedó (1=primero, 2=segundo, 3=tercero, etc.)
        # Ejemplo: Si MORENA tiene más votos que cualquier otro partido, posicion_shh=1
        #          incluso si SHH perdió como coalición
        partido_shh_mejor_posicionado = None
        posicion_shh = None
        
        for pos, (partido, votos) in enumerate(ranking_partidos, start=1):
            if partido in SHH:
                partido_shh_mejor_posicionado = partido
                posicion_shh = pos
                break
        
        detalle = {
            'entidad': entidad,
            'distrito': distrito,
            'ganador_coalicion': ganador_coal,
            'partido_shh_2do': partido_shh_mejor_posicionado,
            'posicion_shh': posicion_shh,  # Posición en ranking de TODOS los partidos (1, 2, 3, etc.)
            'votos_morena': row.get('MORENA', 0),
            'votos_pt': row.get('PT', 0),
            'votos_pvem': row.get('PVEM', 0),
            'votos_shh_total': votos_shh,
            'votos_fcm_total': votos_fcm,
            'votos_mc_total': votos_mc
        }
        
        detalle_por_distrito.append(detalle)
        
        if partido_shh_mejor_posicionado:
            segundo_lugar_por_partido[partido_shh_mejor_posicionado] += 1

# DataFrame
df_detalle = pd.DataFrame(detalle_por_distrito)

print(f"\n📊 RESUMEN:")
print(f"   Total distritos donde SHH perdió: {len(df_detalle)}")
print()
print("📊 PARTIDO DE SHH MEJOR POSICIONADO:")
print("   (Cuál partido de SHH quedó primero en el ranking individual)")
for partido in ['MORENA', 'PT', 'PVEM']:
    count = segundo_lugar_por_partido.get(partido, 0)
    pct = (count / len(df_detalle) * 100) if len(df_detalle) > 0 else 0
    print(f"   {partido:6s}: {count:3d} distritos ({pct:5.1f}%)")

# Mostrar distribución de posiciones
print("\n📊 DISTRIBUCIÓN POR POSICIÓN INDIVIDUAL:")
print("   (En qué lugar del ranking quedó el mejor partido de SHH)")
posiciones = df_detalle['posicion_shh'].value_counts().sort_index()
for pos, count in posiciones.items():
    pct = (count / len(df_detalle) * 100)
    lugar = {1: '1er', 2: '2do', 3: '3er', 4: '4to'}.get(pos, f'{pos}º')
    print(f"   {lugar} lugar: {count:3d} distritos ({pct:5.1f}%)")
    if pos == 1:
        print(f"        (El partido de SHH tuvo MÁS votos que cualquier otro partido)")
    elif pos == 2:
        print(f"        (Solo 1 partido tuvo más votos que el mejor de SHH)")

# Guardar CSV
df_detalle.to_csv('analisis_segundos_lugares_shh.csv', index=False, encoding='utf-8-sig')
print(f"\n✅ CSV guardado: analisis_segundos_lugares_shh.csv")

# Tabla markdown
print("\n| Partido | Distritos 2º lugar | % |")
print("|---------|-------------------:|--:|")
for partido in ['MORENA', 'PT', 'PVEM']:
    count = segundo_lugar_por_partido.get(partido, 0)
    pct = (count / len(df_detalle) * 100) if len(df_detalle) > 0 else 0
    print(f"| {partido} | {count} | {pct:.1f}% |")
print(f"| **TOTAL** | **{len(df_detalle)}** | **100%** |")
