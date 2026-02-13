"""
Análisis de Posicionamiento Individual en Distritos Perdidos por SHH

Este script analiza los distritos donde la coalición SHH (MORENA+PT+PVEM) perdió
en 2024, determinando cuál partido de SHH quedó MEJOR POSICIONADO en el ranking
individual de TODOS los partidos (sin importar coalición).

CONCEPTO CLAVE:
- "Ganador por coalición" = suma de votos de partidos aliados
- "Ranking individual" = cada partido ordenado por votos, SIN coaliciones

EJEMPLO:
Un distrito puede tener:
  Por coalición: FCM gana (PAN+PRI+PRD = 80,000) vs SHH pierde (MORENA+PT+PVEM = 70,000)
  Ranking individual: 1º MORENA (55,000), 2º PAN (40,000), 3º PRI (25,000), etc.
  
Resultado: FCM ganó como coalición, pero MORENA fue 1º en el ranking individual.
- mejor_partido_shh = MORENA (el mejor de los 3 partidos SHH)
- posicion_shh = 1 (MORENA quedó en primer lugar del ranking individual)

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
print("ANÁLISIS: MEJOR PARTIDO SHH EN DISTRITOS PERDIDOS")
print("=" * 80)
print("\nConcepto: Aunque SHH perdió como COALICIÓN, identificamos cuál partido")
print("de SHH (MORENA, PT o PVEM) quedó MEJOR en el ranking individual de")
print("TODOS los partidos.")
print("\nNota: 'posicion_shh' puede ser 1, 2, 3, 4... según dónde quedó el mejor")
print("partido de SHH en el ranking. Posición 1 = fue el partido MÁS votado de todos.")
print("=" * 80)

# Almacenar resultados
mejor_partido_por_distrito = Counter()  # Cuántas veces cada partido fue el mejor de SHH
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
        # mejor_partido_shh = cuál de los 3 (MORENA, PT, PVEM) quedó primero
        # posicion_shh = en qué lugar del ranking general quedó ese partido (1, 2, 3, 4...)
        mejor_partido_shh = None
        posicion_shh = None
        
        for pos, (partido, votos) in enumerate(ranking_partidos, start=1):
            if partido in SHH:
                mejor_partido_shh = partido
                posicion_shh = pos
                break
        
        detalle = {
            'entidad': entidad,
            'distrito': distrito,
            'ganador_coalicion': ganador_coal,
            'mejor_partido_shh': mejor_partido_shh,  # MORENA, PT o PVEM (el mejor de los 3)
            'posicion_shh': posicion_shh,  # Posición en ranking general: 1, 2, 3, 4...
            'votos_morena': row.get('MORENA', 0),
            'votos_pt': row.get('PT', 0),
            'votos_pvem': row.get('PVEM', 0),
            'votos_shh_total': votos_shh,
            'votos_fcm_total': votos_fcm,
            'votos_mc_total': votos_mc
        }
        
        detalle_por_distrito.append(detalle)
        
        if mejor_partido_shh:
            mejor_partido_por_distrito[mejor_partido_shh] += 1

# DataFrame
df_detalle = pd.DataFrame(detalle_por_distrito)

print(f"\n📊 RESUMEN:")
print(f"   Total distritos donde SHH perdió: {len(df_detalle)}")
print()
print("📊 MEJOR PARTIDO DE SHH EN CADA DISTRITO PERDIDO:")
print("   (Cuál de los 3 partidos de SHH tuvo más votos)")
for partido in ['MORENA', 'PT', 'PVEM']:
    count = mejor_partido_por_distrito.get(partido, 0)
    pct = (count / len(df_detalle) * 100) if len(df_detalle) > 0 else 0
    print(f"   {partido:6s}: {count:3d} distritos ({pct:5.1f}%)")

# Mostrar distribución de posiciones
print("\n📊 POSICIÓN EN RANKING GENERAL (todos los partidos):")
print("   (En qué lugar quedó el mejor partido de SHH)")
posiciones = df_detalle['posicion_shh'].value_counts().sort_index()
for pos, count in posiciones.items():
    pct = (count / len(df_detalle) * 100)
    lugar = {1: '1er', 2: '2do', 3: '3er', 4: '4to'}.get(pos, f'{pos}º')
    print(f"   {lugar} lugar: {count:3d} distritos ({pct:5.1f}%)")
    if pos == 1:
        print(f"        → El mejor partido de SHH tuvo MÁS votos que cualquier otro")
    elif pos == 2:
        print(f"        → Solo 1 partido (de cualquier coalición) tuvo más votos")

# Guardar CSV
df_detalle.to_csv('analisis_segundos_lugares_shh.csv', index=False, encoding='utf-8-sig')
print(f"\n✅ CSV guardado: analisis_segundos_lugares_shh.csv")
print(f"   Columnas:")
print(f"   - mejor_partido_shh: Cuál de los 3 (MORENA/PT/PVEM) tuvo más votos")
print(f"   - posicion_shh: En qué lugar quedó en el ranking de TODOS los partidos")

# Tabla markdown
print("\n| Partido | Distritos donde fue el mejor de SHH | % |")
print("|---------|------------------------------------:|--:|")
for partido in ['MORENA', 'PT', 'PVEM']:
    count = mejor_partido_por_distrito.get(partido, 0)
    pct = (count / len(df_detalle) * 100) if len(df_detalle) > 0 else 0
    print(f"| {partido} | {count} | {pct:.1f}% |")
print(f"| **TOTAL** | **{len(df_detalle)}** | **100%** |")
