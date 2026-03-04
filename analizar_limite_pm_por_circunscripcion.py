"""
Análisis: Límite de Distritos MR por Circunscripción para Recibir PM

Pregunta: Si se asignan 100 PM (mejores perdedores) por circunscripción,
          a partir de cuántos distritos MR ganados te quedas sin perdedores?

Sistema:
- 5 Circunscripciones plurinominales
- 300 distritos MR total
- 100 PM a distribuir por circunscripción (20 por circ?)
- Límite constitucional: Máximo 300 diputados totales por partido
"""

import pandas as pd
from collections import defaultdict

print("=" * 80)
print("ANÁLISIS: LÍMITE DE PERDEDORES POR CIRCUNSCRIPCIÓN PARA ASIGNAR PM")
print("=" * 80)

# Cargar mapeo de circunscripciones
mapeo = pd.read_csv('mapeo_circunscripciones.csv')

# Estructura de circunscripciones
print("\n📊 ESTRUCTURA DE CIRCUNSCRIPCIONES:")
print("\nCircunscripción | Estados | Distritos")
print("-" * 50)

circ_stats = mapeo.groupby('CIRCUNSCRIPCION').agg({
    'ENTIDAD': 'count',
    'DISTRITOS': 'sum'
}).rename(columns={'ENTIDAD': 'Estados', 'DISTRITOS': 'Total_Distritos'})

for circ in sorted(circ_stats.index):
    estados = circ_stats.loc[circ, 'Estados']
    distritos = circ_stats.loc[circ, 'Total_Distritos']
    print(f"{circ}ª Circunsc. | {estados:2d} estados | {distritos:2d} distritos")

print(f"\nTOTAL: {circ_stats['Total_Distritos'].sum()} distritos")

# Cargar datos 2024
parquet = pd.read_parquet('data/computos_diputados_2024.parquet')

# Normalizar nombres de entidades
NORMALIZACION = {
    'AGUASCALIENTES': 'AGUASCALIENTES',
    'BAJA CALIFORNIA': 'BAJA CALIFORNIA',
    'BAJA CALIFORNIA SUR': 'BAJA CALIFORNIA SUR',
    'CAMPECHE': 'CAMPECHE',
    'CHIAPAS': 'CHIAPAS',
    'CHIHUAHUA': 'CHIHUAHUA',
    'CIUDAD DE MEXICO': 'CIUDAD DE MEXICO',
    'COAHUILA': 'COAHUILA',
    'COLIMA': 'COLIMA',
    'DURANGO': 'DURANGO',
    'GUANAJUATO': 'GUANAJUATO',
    'GUERRERO': 'GUERRERO',
    'HIDALGO': 'HIDALGO',
    'JALISCO': 'JALISCO',
    'MEXICO': 'MEXICO',
    'MICHOACAN': 'MICHOACAN',
    'MORELOS': 'MORELOS',
    'NAYARIT': 'NAYARIT',
    'NUEVO LEON': 'NUEVO LEON',
    'OAXACA': 'OAXACA',
    'PUEBLA': 'PUEBLA',
    'QUERETARO': 'QUERETARO',
    'QUINTANA ROO': 'QUINTANA ROO',
    'SAN LUIS POTOSI': 'SAN LUIS POTOSI',
    'SINALOA': 'SINALOA',
    'SONORA': 'SONORA',
    'TABASCO': 'TABASCO',
    'TAMAULIPAS': 'TAMAULIPAS',
    'TLAXCALA': 'TLAXCALA',
    'VERACRUZ': 'VERACRUZ',
    'YUCATAN': 'YUCATAN',
    'ZACATECAS': 'ZACATECAS'
}

# Merge parquet con circunscripciones
parquet['ENTIDAD_NORM'] = parquet['ENTIDAD'].str.upper().str.strip()
mapeo['ENTIDAD_NORM'] = mapeo['ENTIDAD'].str.upper().str.strip()

# Merge
data = parquet.merge(mapeo[['ENTIDAD_NORM', 'CIRCUNSCRIPCION']], 
                     on='ENTIDAD_NORM', how='left')

# Definir coaliciones
SHH = ['MORENA', 'PT', 'PVEM']
FCM = ['PAN', 'PRI', 'PRD']

# Calcular ganador MR por coalición en cada distrito
mr_por_coalicion_circ = defaultdict(lambda: defaultdict(int))

for idx, row in data.iterrows():
    circ = row['CIRCUNSCRIPCION']
    
    # Votos por coalición
    votos_shh = sum(row.get(p, 0) for p in SHH)
    votos_fcm = sum(row.get(p, 0) for p in FCM)
    votos_mc = row.get('MC', 0)
    
    # Ganador
    votos_coaliciones = {
        'SHH': votos_shh,
        'FCM': votos_fcm,
        'MC': votos_mc
    }
    ganador = max(votos_coaliciones, key=votos_coaliciones.get)
    
    mr_por_coalicion_circ[circ][ganador] += 1

# Análisis de límite
print("\n" + "=" * 80)
print("ANÁLISIS: ¿CUÁNTOS PERDEDORES DISPONIBLES POR CIRCUNSCRIPCIÓN? (2024)")
print("=" * 80)

# Supongamos 20 PM por circunscripción (100 / 5 = 20)
PM_POR_CIRC = 20

print(f"\nSuPUESTO: {PM_POR_CIRC} PM por circunscripción (100 total / 5)")
print("\nCirc | Distritos | Coalición | MR Ganados | Perdidos | PM Disponibles")
print("-" * 75)

resultado_pm = defaultdict(lambda: defaultdict(int))

for circ in sorted([1, 2, 3, 4, 5]):
    total_dist = circ_stats.loc[circ, 'Total_Distritos']
    
    for coal in ['SHH', 'FCM', 'MC']:
        mr_ganados = mr_por_coalicion_circ[circ].get(coal, 0)
        perdidos = total_dist - mr_ganados
        pm_disponibles = perdidos
        
        resultado_pm[circ][coal] = pm_disponibles
        
        # Alerta si no hay suficientes perdedores
        alerta = " ⚠️ INSUFICIENTE" if pm_disponibles < PM_POR_CIRC else ""
        
        print(f"{circ}ª   | {total_dist:2d}        | {coal:3s}       | "
              f"{mr_ganados:2d}         | {perdidos:2d}       | {pm_disponibles:2d}{alerta}")

# Resumen: ¿A partir de cuántos MR te quedas sin perdedores?
print("\n" + "=" * 80)
print(f"RESPUESTA: ¿A PARTIR DE CUÁNTOS MR TE QUEDAS SIN PERDEDORES?")
print("=" * 80)

print(f"\nPara recibir {PM_POR_CIRC} PM completos en una circunscripción:")
print("\nCircunscripción | Distritos | Umbral MR | Fórmula")
print("-" * 65)

for circ in sorted([1, 2, 3, 4, 5]):
    total_dist = int(circ_stats.loc[circ, 'Total_Distritos'])
    umbral = total_dist - PM_POR_CIRC
    print(f"{circ}ª              | {total_dist:2d}        | ≤ {umbral:2d}      | "
          f"(Puedes ganar hasta {umbral} y recibir {PM_POR_CIRC} PM)")

print("\n💡 INTERPRETACIÓN:")
print(f"   Si ganas MÁS de estos umbrales → Te quedas sin perdedores suficientes")
print(f"   Si ganas TODOS los distritos → 0 perdedores, 0 PM posibles")

# Caso real MORENA 2024
print("\n" + "=" * 80)
print("CASO REAL: MORENA 2024")
print("=" * 80)

morena_mr_total = sum(mr_por_coalicion_circ[c]['SHH'] for c in [1,2,3,4,5])
print(f"\nMORENA (SHH) ganó {morena_mr_total} distritos MR en total")
print("\nDistribución por circunscripción:")
print("\nCirc | MR Ganados | Perdidos | PM Disponibles | ¿Suficiente para 20 PM?")
print("-" * 75)

total_pm_posible = 0
for circ in sorted([1, 2, 3, 4, 5]):
    mr = mr_por_coalicion_circ[circ]['SHH']
    total_dist = int(circ_stats.loc[circ, 'Total_Distritos'])
    perdidos = total_dist - mr
    pm_disp = perdidos
    total_pm_posible += pm_disp
    
    suficiente = "✅ SÍ" if pm_disp >= PM_POR_CIRC else f"❌ NO (faltan {PM_POR_CIRC - pm_disp})"
    
    print(f"{circ}ª   | {mr:2d}         | {perdidos:2d}       | {pm_disp:2d}             | {suficiente}")

print(f"\nTOTAL PM MÁXIMO POSIBLE PARA MORENA: {total_pm_posible}")
print(f"PM A ASIGNAR SI PROPORCIONAL: ~{PM_POR_CIRC * 5} = 100")
print(f"DIFERENCIA: MORENA NO TIENE SUFICIENTES PERDEDORES en ninguna circunscripción")

# Límite constitucional de 300
print("\n" + "=" * 80)
print("LÍMITE CONSTITUCIONAL: MÁXIMO 300 DIPUTADOS")
print("=" * 80)

print(f"\nMORENA 2024:")
print(f"  MR: {morena_mr_total}")
print(f"  PM máximo (por perdedores): {total_pm_posible}")
print(f"  Total MR + PM: {morena_mr_total + total_pm_posible}")
print(f"  RP disponible antes de límite: {300 - morena_mr_total - total_pm_posible}")

if morena_mr_total + total_pm_posible >= 300:
    print(f"\n⚠️ MORENA ya alcanzaría ~300 solo con MR+PM")
    print(f"   No hay espacio para RP bajo límite constitucional")
else:
    print(f"\n✅ MORENA tendría espacio para RP")

print("\n" + "=" * 80)
print("CONCLUSIÓN")
print("=" * 80)

print(f"""
La respuesta a tu pregunta:

1. UMBRAL GENERAL: 
   - Circunscripción con 60 distritos: Si ganas más de {60 - PM_POR_CIRC} → Te quedas sin perdedores
   - Formula: Umbral_MR = Distritos_circunscripción - PM_a_asignar

2. CASO MORENA 2024:
   - Ganó {morena_mr_total} MR (demasiados en cada circunscripción)
   - Solo tiene {total_pm_posible} perdedores totales
   - No puede recibir 100 PM proporcionales (solo max {total_pm_posible})
   
3. IMPLICACIÓN:
   - Cuando un partido DOMINA MR, se queda sin perdedores
   - Los PM deben ir a otros partidos con más derrotas
   - O cambiar el sistema de asignación de PM
""")
