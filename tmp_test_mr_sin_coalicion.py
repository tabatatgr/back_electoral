"""
Test: ¿Qué pasa si calculamos MR sin coalición?
Es decir, solo contando votos de MORENA individual vs PAN individual vs PRI individual
"""

import pandas as pd

# Cargar votos 2024
df = pd.read_parquet('data/computos_diputados_2024.parquet')

print("=== PRIMEROS 10 DISTRITOS ===")
print("Comparando: MORENA solo vs coalición MORENA+PT+PVEM\n")

partidos_clave = ['MORENA', 'PT', 'PVEM', 'PAN', 'PRI', 'PRD', 'MC']

# Calcular ganadores
ganadores_individual = []
ganadores_coalicion = []

for idx, row in df.head(20).iterrows():
    entidad = row['ENTIDAD']
    distrito = row['DISTRITO']
    
    # Votos individuales
    votos_ind = {p: row.get(p, 0) for p in partidos_clave}
    ganador_ind = max(votos_ind, key=votos_ind.get)
    votos_ganador_ind = votos_ind[ganador_ind]
    
    # Votos con coalición (MORENA+PT+PVEM)
    votos_coal_morena = row.get('MORENA', 0) + row.get('PT', 0) + row.get('PVEM', 0)
    votos_coal_pan = row.get('PAN', 0) + row.get('PRI', 0) + row.get('PRD', 0)
    votos_coal_mc = row.get('MC', 0)
    
    votos_coal = {
        'MORENA+PT+PVEM': votos_coal_morena,
        'PAN+PRI+PRD': votos_coal_pan,
        'MC': votos_coal_mc
    }
    ganador_coal = max(votos_coal, key=votos_coal.get)
    votos_ganador_coal = votos_coal[ganador_coal]
    
    print(f"{entidad} DF-{distrito}:")
    print(f"  SIN coalición: {ganador_ind} ({votos_ganador_ind:,} votos)")
    print(f"  CON coalición: {ganador_coal} ({votos_ganador_coal:,} votos)")
    
    if ganador_ind != ganador_coal.split('+')[0]:
        print(f"  ⚠️ CAMBIO DE GANADOR!")
    print()
    
    ganadores_individual.append(ganador_ind)
    ganadores_coalicion.append(ganador_coal)

# Contar totales
from collections import Counter
print("\n=== RESUMEN (primeros 20 distritos) ===")
print("\nSIN coalición:")
for partido, count in Counter(ganadores_individual).most_common():
    print(f"  {partido}: {count}")

print("\nCON coalición:")
for coalicion, count in Counter(ganadores_coalicion).most_common():
    print(f"  {coalicion}: {count}")

# Ahora hacer el cálculo completo
print("\n" + "="*60)
print("=== CÁLCULO COMPLETO 300 DISTRITOS ===")
print("="*60)

ganadores_ind_full = []
ganadores_coal_full = []

for idx, row in df.iterrows():
    # Votos individuales
    votos_ind = {p: row.get(p, 0) for p in partidos_clave}
    ganador_ind = max(votos_ind, key=votos_ind.get)
    ganadores_ind_full.append(ganador_ind)
    
    # Votos con coalición
    votos_coal_morena = row.get('MORENA', 0) + row.get('PT', 0) + row.get('PVEM', 0)
    votos_coal_pan = row.get('PAN', 0) + row.get('PRI', 0) + row.get('PRD', 0)
    votos_coal_mc = row.get('MC', 0)
    
    votos_coal = {
        'MORENA+PT+PVEM': votos_coal_morena,
        'PAN+PRI+PRD': votos_coal_pan,
        'MC': votos_coal_mc
    }
    ganador_coal = max(votos_coal, key=votos_coal.get)
    ganadores_coal_full.append(ganador_coal)

print("\n📊 DISTRIBUCIÓN MR - SIN COALICIÓN (solo votos individuales):")
for partido, count in sorted(Counter(ganadores_ind_full).items(), key=lambda x: x[1], reverse=True):
    print(f"  {partido}: {count} distritos")

print("\n📊 DISTRIBUCIÓN MR - CON COALICIÓN (sumando aliados):")
for coalicion, count in sorted(Counter(ganadores_coal_full).items(), key=lambda x: x[1], reverse=True):
    print(f"  {coalicion}: {count} distritos")

# Calcular diferencia
print("\n🔍 IMPACTO DE LA COALICIÓN:")
morena_sin = Counter(ganadores_ind_full)['MORENA']
morena_con = Counter(ganadores_coal_full)['MORENA+PT+PVEM']
print(f"  MORENA sin coalición: {morena_sin} distritos MR")
print(f"  Coalición con aliados: {morena_con} distritos MR")
print(f"  Ganancia por coalición: +{morena_con - morena_sin} distritos")
print(f"  Incremento: {((morena_con - morena_sin) / morena_sin * 100):.1f}%")
