"""
Entender QUÉ representa el siglado.
¿Por qué tiene múltiples partidos por distrito pero NO incluye al ganador según votos?
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

print("=" * 80)
print("ANÁLISIS: ¿Qué representa el siglado?")
print("=" * 80)

# Caso de estudio: AGUASCALIENTES-1
entidad = 'AGUASCALIENTES'
distrito = 1

print(f"\n📍 Caso de estudio: {entidad}-{distrito}")
print("=" * 80)

# Votos del parquet
distrito_data = parquet[(parquet['ENTIDAD_NORM'] == entidad) & (parquet['DISTRITO'] == distrito)].iloc[0]

partidos = ['MORENA', 'PAN', 'PRI', 'PRD', 'PT', 'PVEM', 'MC']
votos_partidos = {p: distrito_data.get(p, 0) for p in partidos}

print("\n📊 VOTOS POR PARTIDO (desde parquet):")
for p in sorted(votos_partidos.keys(), key=lambda x: votos_partidos[x], reverse=True):
    v = votos_partidos[p]
    print(f"   {p:8s}: {v:>10,.0f}")

ganador_votos = max(votos_partidos, key=votos_partidos.get)
print(f"\n👑 GANADOR SEGÚN VOTOS: {ganador_votos} ({votos_partidos[ganador_votos]:,.0f})")

# ¿Qué dice el siglado?
siglado_distrito = siglado[(siglado['entidad_norm'] == entidad) & (siglado['distrito'] == distrito)]

print(f"\n📋 SIGLADO para este distrito ({len(siglado_distrito)} filas):")
print(siglado_distrito[['entidad', 'distrito', 'coalicion', 'grupo_parlamentario']].to_string(index=False))

# Hipótesis: ¿El siglado representa quién POSTULÓ candidatos en coalición?
print("\n" + "=" * 80)
print("💡 HIPÓTESIS: ¿El siglado muestra quién GANÓ según la COALICIÓN?")
print("=" * 80)

# Ver si hay columnas de coaliciones en el parquet
coaliciones_cols = [c for c in parquet.columns if 'COALICION' in c or 'SIGAMOS' in c or 'FUERZA' in c]
print(f"\nColumnas de coaliciones en parquet: {coaliciones_cols}")

if coaliciones_cols:
    print("\n📊 VOTOS DE COALICIONES:")
    for col in coaliciones_cols:
        votos = distrito_data.get(col, 0)
        print(f"   {col}: {votos:>10,.0f}")
    
    # Calcular ganador considerando coaliciones
    votos_todos = {**votos_partidos}
    for col in coaliciones_cols:
        votos_todos[col] = distrito_data.get(col, 0)
    
    ganador_con_coalicion = max(votos_todos, key=votos_todos.get)
    print(f"\n👑 GANADOR (con coaliciones): {ganador_con_coalicion} ({votos_todos[ganador_con_coalicion]:,.0f})")

print("\n" + "=" * 80)
print("💡 INTERPRETACIÓN DEL SIGLADO:")
print("=" * 80)

print("""
El siglado parece tener la siguiente estructura:
1. Lista los distritos donde cada COALICIÓN compitió
2. Para cada distrito, indica qué PARTIDO de la coalición se lleva el escaño
3. NO lista a todos los partidos que compitieron, solo los de las coaliciones ganadoras

Ejemplo AGUASCALIENTES-1:
- Siglado dice: FUERZA Y CORAZON POR MEXICO → PRI
               SIGAMOS HACIENDO HISTORIA → PVEM
  
Esto significa:
- En este distrito compitieron 2 COALICIONES
- Si gana FCM (PAN-PRI-PRD), el escaño va para PRI
- Si gana SHH (MORENA-PT-PVEM), el escaño va para PVEM

Pero según los VOTOS INDIVIDUALES del parquet:
- PAN ganó con 76,287 votos (no está en siglado porque compitió en coalición)
""")

print("\n" + "=" * 80)
print("🔍 VERIFICACIÓN: ¿Hay columnas de coaliciones en el parquet?")
print("=" * 80)

print(f"\nColumnas del parquet:")
for col in sorted(parquet.columns):
    print(f"   {col}")
