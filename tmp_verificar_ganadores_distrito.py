"""
Verificar distrito por distrito: ¿El motor está identificando correctamente 
el ganador según los votos del parquet?
"""

import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(__file__))

# Cargar datos
parquet = pd.read_parquet('data/computos_diputados_2024.parquet')
siglado = pd.read_csv('data/siglado-diputados-2024.csv')

print("=" * 80)
print("VERIFICACIÓN DISTRITO POR DISTRITO")
print("=" * 80)

# Normalizar nombres de columnas
parquet.columns = [c.upper() for c in parquet.columns]
siglado.columns = [c.lower() for c in siglado.columns]

print(f"\n📊 Parquet: {len(parquet)} distritos")
print(f"📊 Siglado: {len(siglado)} filas")

# Identificar columnas de partidos en el parquet
partidos = ['MORENA', 'PAN', 'PRI', 'PRD', 'PT', 'PVEM', 'MC']
partidos_en_parquet = [p for p in partidos if p in parquet.columns]

print(f"\n🔍 Partidos encontrados en parquet: {partidos_en_parquet}")

# Normalizar entidades
def normalizar_entidad(ent):
    return str(ent).upper().strip().replace('É', 'E').replace('Á', 'A').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')

parquet['ENTIDAD_NORM'] = parquet['ENTIDAD'].apply(normalizar_entidad)
siglado['entidad_norm'] = siglado['entidad_ascii'].apply(normalizar_entidad) if 'entidad_ascii' in siglado.columns else siglado['entidad'].apply(normalizar_entidad)

print("\n" + "=" * 80)
print("MUESTRA: Primeros 10 distritos")
print("=" * 80)

discrepancias = []

for idx in range(min(10, len(parquet))):
    distrito_data = parquet.iloc[idx]
    entidad = distrito_data['ENTIDAD_NORM']
    distrito_num = distrito_data['DISTRITO']
    
    # Calcular ganador según votos
    votos_partidos = {p: distrito_data.get(p, 0) for p in partidos_en_parquet}
    ganador_motor = max(votos_partidos, key=votos_partidos.get)
    votos_ganador = votos_partidos[ganador_motor]
    
    # Buscar en siglado qué dice
    mask = (siglado['entidad_norm'] == entidad) & (siglado['distrito'] == distrito_num)
    siglado_distrito = siglado[mask]
    
    partidos_siglado = siglado_distrito['grupo_parlamentario'].unique() if len(siglado_distrito) > 0 else []
    
    print(f"\n📍 {entidad}-{distrito_num}")
    print(f"   Ganador según votos: {ganador_motor} ({votos_ganador:,} votos)")
    print(f"   Partidos en siglado: {list(partidos_siglado)}")
    
    # Ver todos los votos
    print(f"   Votos por partido:")
    for p in sorted(votos_partidos.keys(), key=lambda x: votos_partidos[x], reverse=True):
        v = votos_partidos[p]
        marca = "👑" if p == ganador_motor else "  "
        print(f"     {marca} {p}: {v:,}")
    
    # Verificar si el ganador está en el siglado
    if ganador_motor not in partidos_siglado:
        print(f"   ⚠️  DISCREPANCIA: Ganador {ganador_motor} NO está en siglado: {list(partidos_siglado)}")
        discrepancias.append({
            'entidad': entidad,
            'distrito': distrito_num,
            'ganador_motor': ganador_motor,
            'partidos_siglado': list(partidos_siglado)
        })

print("\n" + "=" * 80)
print("CONTEO TOTAL DE MR POR PARTIDO (según votos del parquet)")
print("=" * 80)

conteo_mr_motor = {}
for idx in range(len(parquet)):
    distrito_data = parquet.iloc[idx]
    votos_partidos = {p: distrito_data.get(p, 0) for p in partidos_en_parquet}
    ganador = max(votos_partidos, key=votos_partidos.get)
    conteo_mr_motor[ganador] = conteo_mr_motor.get(ganador, 0) + 1

print("\nMR por partido (calculado desde votos):")
for partido in sorted(conteo_mr_motor.keys()):
    print(f"  {partido}: {conteo_mr_motor[partido]}")

print(f"\nTotal MR: {sum(conteo_mr_motor.values())}")

print("\n" + "=" * 80)
print("COMPARACIÓN CON SIGLADO")
print("=" * 80)

conteo_siglado = siglado['grupo_parlamentario'].value_counts().to_dict()

print(f"\n{'Partido':<10} {'Votos Parquet':>15} {'Siglado':>10} {'Diferencia':>12}")
print("-" * 50)

todos_partidos = set(conteo_mr_motor.keys()) | set(conteo_siglado.keys())
for partido in sorted(todos_partidos):
    motor = conteo_mr_motor.get(partido, 0)
    siglado_count = conteo_siglado.get(partido, 0)
    diff = motor - siglado_count
    marca = "⚠️" if diff != 0 else "✅"
    print(f"{partido:<10} {motor:>15} {siglado_count:>10} {diff:>11} {marca}")

print("\n" + "=" * 80)
print("💡 CONCLUSIÓN:")
print("=" * 80)

diff_total = sum(abs(conteo_mr_motor.get(p, 0) - conteo_siglado.get(p, 0)) for p in todos_partidos)

if diff_total == 0:
    print("\n✅ El cálculo desde votos del parquet COINCIDE con el siglado")
else:
    print(f"\n⚠️  Hay {diff_total} diferencias entre el cálculo desde votos y el siglado")
    print("\nEsto significa que:")
    print("1. O el parquet tiene votos diferentes a los oficiales")
    print("2. O el siglado fue ajustado manualmente después de contar votos")
    print("3. O hay distritos con circunstancias especiales (recuentos, impugnaciones, etc.)")

if len(discrepancias) > 0:
    print(f"\n⚠️  Encontradas {len(discrepancias)} discrepancias en la muestra de 10 distritos")
