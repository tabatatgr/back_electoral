"""
Análisis: Primera Minoría en Distritos Perdidos por SHH

En los 44 distritos donde la coalición SHH (MORENA+PT+PVEM) perdió en 2024,
¿quién ganó el SEGUNDO LUGAR (primera minoría)?

OBJETIVO:
Identificar qué partido individual quedó en SEGUNDO LUGAR en cada distrito perdido.

EJEMPLO:
Ranking en un distrito:
  1º PAN: 50,000 votos ← Ganador
  2º MORENA: 45,000 votos ← SEGUNDA LUGAR / Primera minoría
  3º PRI: 30,000 votos
  4º MC: 20,000 votos
  
Si SHH perdió como coalición, queremos saber quién quedó 2º (en este caso MORENA).
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
print("ANÁLISIS: SEGUNDA LUGAR (PRIMERA MINORÍA) EN DISTRITOS PERDIDOS POR SHH")
print("=" * 80)
print("\nEn los distritos donde SHH perdió como coalición,")
print("¿quién ganó el SEGUNDO LUGAR (primera minoría)?")
print("\nRanking por PARTIDO INDIVIDUAL (no por coalición)")
print("=" * 80)

# Almacenar resultados
segundo_lugar_por_partido = Counter()  # Quién ganó 2º lugar en cada distrito
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
        # Crear ranking de partidos individuales
        votos_partidos = {
            'MORENA': row.get('MORENA', 0),
            'PT': row.get('PT', 0),
            'PVEM': row.get('PVEM', 0),
            'PAN': row.get('PAN', 0),
            'PRI': row.get('PRI', 0),
            'PRD': row.get('PRD', 0),
            'MC': row.get('MC', 0)
        }
        
        # Ordenar partidos por votos (de mayor a menor)
        ranking_partidos = sorted(votos_partidos.items(), key=lambda x: -x[1])
        
        # El primero es el ganador, el segundo es la primera minoría
        primer_lugar = ranking_partidos[0] if len(ranking_partidos) > 0 else (None, 0)
        segundo_lugar = ranking_partidos[1] if len(ranking_partidos) > 1 else (None, 0)
        
        partido_primer_lugar = primer_lugar[0]
        votos_primer_lugar = primer_lugar[1]
        partido_segundo_lugar = segundo_lugar[0]
        votos_segundo_lugar = segundo_lugar[1]
        
        detalle = {
            'entidad': entidad,
            'distrito': distrito,
            'ganador_coalicion': ganador_coal,
            'primer_lugar': partido_primer_lugar,
            'votos_primer_lugar': votos_primer_lugar,
            'segundo_lugar': partido_segundo_lugar,  # ← PRIMERA MINORÍA
            'votos_segundo_lugar': votos_segundo_lugar,
            'votos_morena': row.get('MORENA', 0),
            'votos_pt': row.get('PT', 0),
            'votos_pvem': row.get('PVEM', 0),
            'votos_shh_total': votos_shh,
            'votos_fcm_total': votos_fcm,
            'votos_mc_total': votos_mc
        }
        
        detalle_por_distrito.append(detalle)
        
        if partido_segundo_lugar:
            segundo_lugar_por_partido[partido_segundo_lugar] += 1

# DataFrame
df_detalle = pd.DataFrame(detalle_por_distrito)

print(f"\n📊 RESUMEN:")
print(f"   Total distritos donde SHH perdió: {len(df_detalle)}")
print()
print("📊 SEGUNDA LUGAR (PRIMERA MINORÍA) POR PARTIDO:")
print("   ¿Quién ganó el 2º lugar en los distritos perdidos?")
for partido in ['MORENA', 'PT', 'PVEM', 'PAN', 'PRI', 'PRD', 'MC']:
    count = segundo_lugar_por_partido.get(partido, 0)
    if count > 0:
        pct = (count / len(df_detalle) * 100) if len(df_detalle) > 0 else 0
        print(f"   {partido:6s}: {count:3d} distritos ({pct:5.1f}%)")

# Guardar CSV
df_detalle.to_csv('analisis_segundos_lugares_shh.csv', index=False, encoding='utf-8-sig')
print(f"\n✅ CSV guardado: analisis_segundos_lugares_shh.csv")
print(f"   Columnas:")
print(f"   - primer_lugar: Partido que ganó el distrito")
print(f"   - segundo_lugar: Partido que quedó en 2º (primera minoría)")

# Tabla markdown
print("\n| Partido | Veces que quedó en 2º lugar | % |")
print("|---------|----------------------------:|--:|")
for partido in ['MORENA', 'PT', 'PVEM', 'PAN', 'PRI', 'PRD', 'MC']:
    count = segundo_lugar_por_partido.get(partido, 0)
    if count > 0:
        pct = (count / len(df_detalle) * 100) if len(df_detalle) > 0 else 0
        print(f"| {partido} | {count} | {pct:.1f}% |")
total_segundo = sum(segundo_lugar_por_partido.values())
print(f"| **TOTAL** | **{total_segundo}** | **100%** |")
