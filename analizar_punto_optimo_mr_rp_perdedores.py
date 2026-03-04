"""
Análisis del Punto Óptimo: Sistema MR + RP Normal + RP Mejores Perdedores

Sistema Electoral Mexicano:
1. 300 distritos MR (Mayoría Relativa)
2. Primera vuelta RP: 100 asientos (proporcional normal)
3. Segunda vuelta RP: 100 asientos (mejores perdedores - requiere haber perdido distritos)

Pregunta: ¿Cuál es el punto óptimo antes de quedarte sin posibilidad de asignar
          asientos de mejores perdedores?

Respuesta: 200 distritos MR (67% de victoria)
"""

import pandas as pd
import os

# Cargar datos
DATA_FILE = 'data/computos_diputados_2024.parquet'

if not os.path.exists(DATA_FILE):
    print(f"❌ Archivo no encontrado: {DATA_FILE}")
    print("Este script requiere datos de 2024")
    exit(1)

df = pd.read_parquet(DATA_FILE)

# Cargar mapeo de circunscripciones
MAPEO_FILE = 'mapeo_circunscripciones.csv'
if os.path.exists(MAPEO_FILE):
    mapeo = pd.read_csv(MAPEO_FILE)
    # Crear diccionario estado -> circunscripción
    estado_a_circ = dict(zip(mapeo['ESTADO'], mapeo['CIRCUNSCRIPCION']))
else:
    print(f"⚠️ No se encontró {MAPEO_FILE}, usando mapeo manual")
    # Mapeo manual de estados a circunscripciones
    estado_a_circ = {
        'AGUASCALIENTES': '2ª', 'BAJA CALIFORNIA': '1ª', 'BAJA CALIFORNIA SUR': '1ª',
        'CAMPECHE': '3ª', 'COAHUILA': '2ª', 'COLIMA': '5ª', 'CHIAPAS': '3ª',
        'CHIHUAHUA': '1ª', 'CIUDAD DE MÉXICO': '4ª', 'DURANGO': '1ª',
        'GUANAJUATO': '2ª', 'GUERRERO': '4ª', 'HIDALGO': '4ª', 'JALISCO': '1ª',
        'MÉXICO': '5ª', 'MICHOACÁN': '5ª', 'MORELOS': '4ª', 'NAYARIT': '1ª',
        'NUEVO LEÓN': '2ª', 'OAXACA': '3ª', 'PUEBLA': '4ª', 'QUERÉTARO': '5ª',
        'QUINTANA ROO': '3ª', 'SAN LUIS POTOSÍ': '2ª', 'SINALOA': '1ª',
        'SONORA': '1ª', 'TABASCO': '3ª', 'TAMAULIPAS': '2ª', 'TLAXCALA': '4ª',
        'VERACRUZ': '3ª', 'YUCATÁN': '3ª', 'ZACATECAS': '2ª'
    }

# Agregar columna de circunscripción
df['CIRCUNSCRIPCION'] = df['ENTIDAD_NORM'].map(estado_a_circ)

# Definir coaliciones
SHH = ['MORENA', 'PT', 'PVEM']  # Sigamos Haciendo Historia
FCM = ['PAN', 'PRI', 'PRD']      # Fuerza y Corazón por México
MC_PARTIDOS = ['MC']

print("=" * 80)
print("ANÁLISIS DEL PUNTO ÓPTIMO")
print("Sistema: 300 MR + 100 RP Normal + 100 RP Mejores Perdedores")
print("=" * 80)

# Estructura de circunscripciones
distritos_por_circ = {
    '1ª': 61,  # Guadalajara
    '2ª': 59,  # Monterrey
    '3ª': 60,  # Xalapa
    '4ª': 61,  # CDMX
    '5ª': 59   # Toluca
}

print("\n📊 ESTRUCTURA DEL SISTEMA:")
print(f"   • 5 Circunscripciones plurinominales")
print(f"   • 300 distritos MR total")
print(f"   • Distribución: 1ª(61), 2ª(59), 3ª(60), 4ª(61), 5ª(59)")
print(f"   • 100 asientos RP normal (proporcional a votos)")
print(f"   • 100 asientos RP mejores perdedores (de distritos perdidos)")
print(f"   • Límite constitucional: 300 diputados máximo por partido")

# Calcular ganadores por coalición en cada distrito
resultados = []

for idx, row in df.iterrows():
    entidad = row.get('ENTIDAD_NORM', '')
    distrito = row['DISTRITO']
    circ = row.get('CIRCUNSCRIPCION', '')
    
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
    
    resultados.append({
        'entidad': entidad,
        'distrito': distrito,
        'circunscripcion': circ,
        'ganador_coalicion': ganador_coal,
        'votos_shh': votos_shh,
        'votos_fcm': votos_fcm,
        'votos_mc': votos_mc
    })

df_resultados = pd.DataFrame(resultados)

# Contar MR ganados por coalición y circunscripción
print("\n" + "=" * 80)
print("ANÁLISIS 2024: MORENA (SHH) - Caso Real")
print("=" * 80)

mr_por_circ = df_resultados[df_resultados['ganador_coalicion'] == 'SHH'].groupby('circunscripcion').size()

print("\n📊 DISTRIBUCIÓN MR GANADOS POR SHH (2024):")
print()

total_mr_shh = 0
total_perdidos_shh = 0

for circ in ['1ª', '2ª', '3ª', '4ª', '5ª']:
    mr_ganados = mr_por_circ.get(circ, 0)
    total_distritos = distritos_por_circ[circ]
    mr_perdidos = total_distritos - mr_ganados
    
    # Calcular óptimo (para 20 mejores perdedores por circ)
    mr_optimo = total_distritos - 20
    
    estado = "✅ OK" if mr_ganados <= mr_optimo else "❌ EXCEDE"
    diferencia = mr_ganados - mr_optimo
    
    print(f"   {circ} Circunscripción:")
    print(f"      • Total distritos: {total_distritos}")
    print(f"      • MR ganados: {mr_ganados}")
    print(f"      • MR perdidos: {mr_perdidos}")
    print(f"      • MR óptimo: {mr_optimo} (para 20 mejores perdedores)")
    if diferencia > 0:
        print(f"      • Diferencia: +{diferencia} sobre óptimo {estado}")
        print(f"      • ⚠️ Solo {mr_perdidos} perdedores disponibles (necesita 20)")
    else:
        print(f"      • {estado} - Suficientes perdedores")
    print()
    
    total_mr_shh += mr_ganados
    total_perdidos_shh += mr_perdidos

print(f"📊 TOTAL SHH:")
print(f"   • MR ganados: {total_mr_shh}")
print(f"   • MR perdidos: {total_perdidos_shh}")
print(f"   • MR óptimo: 200 (para 100 mejores perdedores)")
print(f"   • Diferencia: +{total_mr_shh - 200}")
print()

if total_mr_shh > 200:
    print(f"   ⚠️ SHH ganó {total_mr_shh} MR (arriba del óptimo de 200)")
    print(f"   ⚠️ Solo {total_perdidos_shh} perdedores disponibles (no los 100 completos)")
else:
    print(f"   ✅ SHH está abajo del óptimo, puede recibir asignación completa")

# Calcular límite constitucional
print("\n" + "=" * 80)
print("LÍMITE CONSTITUCIONAL (300 DIPUTADOS MÁXIMO)")
print("=" * 80)
print()
print(f"   SHH (2024):")
print(f"   • MR: {total_mr_shh}")
print(f"   • Mejores perdedores disponibles: {total_perdidos_shh}")
print(f"   • Total MR + MP: {total_mr_shh + total_perdidos_shh}")
print()

if total_mr_shh + total_perdidos_shh <= 300:
    espacio_rp = 300 - total_mr_shh - total_perdidos_shh
    print(f"   ✅ Dentro del límite constitucional")
    print(f"   • Espacio para RP normal: {espacio_rp} asientos")
else:
    exceso = (total_mr_shh + total_perdidos_shh) - 300
    print(f"   ⚠️ Excede límite por {exceso} asientos")
    print(f"   • Debe reducir mejores perdedores a: {300 - total_mr_shh}")

# Tabla de escenarios
print("\n" + "=" * 80)
print("TABLA DE ESCENARIOS: PUNTO ÓPTIMO")
print("=" * 80)
print()
print("Escenario: ¿Cuántos MR puedes ganar antes de quedarte sin mejores perdedores?")
print()
print(f"{'MR Ganados':<15} {'Perdidos':<12} {'MP Posibles':<15} {'Puede 100 MP?':<15} {'Total Seats':<15}")
print("-" * 80)

escenarios = [0, 50, 100, 150, 200, 210, 220, 230, 240, 250, 260, 270, 280, 290, 300]

for mr in escenarios:
    perdidos = 300 - mr
    mp_posibles = min(perdidos, 100)  # Máximo 100 mejores perdedores
    puede_100 = "✅ SÍ" if mp_posibles == 100 else "❌ NO"
    
    # Calcular total asumiendo RP normal también
    # Pero limitado por 300 constitucional
    total_sin_limite = mr + 100 + mp_posibles  # MR + RP normal + MP
    total_con_limite = min(total_sin_limite, 300)
    
    marca = ""
    if mr == 200:
        marca = " ⭐ ÓPTIMO"
    elif mr == total_mr_shh:
        marca = " 📍 MORENA 2024"
    
    print(f"{mr:<15} {perdidos:<12} {mp_posibles:<15} {puede_100:<15} {total_con_limite:<15}{marca}")

print()
print("⭐ PUNTO ÓPTIMO: 200 MR")
print("   • Ganas 200 distritos → Pierdes 100 distritos")
print("   • 100 pérdidas = Exactamente suficiente para 100 mejores perdedores")
print("   • Maximiza MR manteniendo capacidad completa de mejores perdedores")
print()
print("   Después de 200 MR, empiezas a quedarte sin perdedores!")

# Óptimo por circunscripción
print("\n" + "=" * 80)
print("PUNTO ÓPTIMO POR CIRCUNSCRIPCIÓN")
print("=" * 80)
print()
print("Para asignar 20 mejores perdedores por circunscripción:")
print()
print(f"{'Circunscripción':<20} {'Distritos':<12} {'MR Óptimo':<12} {'Perdidos':<12}")
print("-" * 60)

for circ in ['1ª', '2ª', '3ª', '4ª', '5ª']:
    total_dist = distritos_por_circ[circ]
    mr_opt = total_dist - 20
    perdidos_opt = 20
    
    print(f"{circ:<20} {total_dist:<12} {mr_opt:<12} {perdidos_opt:<12}")

print()
print("Si ganas MÁS que el MR óptimo en una circunscripción,")
print("te quedas sin suficientes perdedores para los 20 mejores perdedores.")

# Resumen final
print("\n" + "=" * 80)
print("RESUMEN EJECUTIVO")
print("=" * 80)
print()
print("PREGUNTA:")
print("¿A partir de cuántos distritos ganados te quedas sin perdedores para acomodar?")
print()
print("RESPUESTA:")
print("🎯 PUNTO ÓPTIMO: 200 Distritos MR (67% tasa de victoria)")
print()
print("FÓRMULA:")
print("   MR_óptimo = Distritos_totales - RP_mejores_perdedores")
print("   MR_óptimo = 300 - 100 = 200 MR")
print()
print("POR QUÉ:")
print("   • Antes de 200 MR: Puedes recibir asignación completa (100 MP)")
print("   • En 200 MR: Exactamente en óptimo (100 pérdidas = 100 MP)")
print("   • Después de 200 MR: Empiezas a quedarte sin perdedores")
print()
print("PERO:")
print("   • El límite constitucional (300 total) es frecuentemente más restrictivo")
print("   • Con 200 MR + 100 RP normal + 100 MP = 400 (excede 300)")
print("   • Óptimo real considerando límite: rango 100-200 MR")
print()
print("CASO MORENA 2024:")
print(f"   • Ganó {total_mr_shh} MR (arriba del óptimo de 200)")
print(f"   • Solo {total_perdidos_shh} perdedores disponibles")
print(f"   • Insuficiente para los 100 mejores perdedores completos")
print(f"   • Ya en límite constitucional: {total_mr_shh} + {total_perdidos_shh} ≈ 300")
print()
print("=" * 80)
