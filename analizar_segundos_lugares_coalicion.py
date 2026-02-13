"""
Análisis: De los 44 distritos donde perdió MORENA+PT+PVEM,
¿en cuántos quedó cada partido (MORENA, PT, PVEM) en 2º lugar?
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
        
        ranking_partidos = sorted(votos_partidos.items(), key=lambda x: -x[1])
        
        # Buscar el partido de SHH mejor posicionado
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
            'posicion_shh': posicion_shh,
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
for partido in ['MORENA', 'PT', 'PVEM']:
    count = segundo_lugar_por_partido.get(partido, 0)
    pct = (count / len(df_detalle) * 100) if len(df_detalle) > 0 else 0
    print(f"   {partido:6s}: {count:3d} distritos ({pct:5.1f}%)")

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
