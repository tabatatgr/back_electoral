"""
Análisis del Sistema Electoral Correcto:
MR (300) + RP sin ganadores (100) + RP mejores perdedores/segundos lugares (100)

Sistema:
1. 300 MR - Ganadores directos por distrito
2. 100 RP - Proporcional, pero EXCLUYENDO ganadores de MR
3. 100 RP Mejores Perdedores - Para SEGUNDOS LUGARES por circunscripción

Pregunta: ¿Cuántos distritos puedes ganar antes de quedarte sin segundos lugares?
"""

import pandas as pd
import os
from collections import Counter

# Cargar datos
DATA_FILE = 'data/computos_diputados_2024.parquet'

if not os.path.exists(DATA_FILE):
    print(f"❌ Archivo no encontrado: {DATA_FILE}")
    print("Este análisis requiere datos de 2024")
    exit(1)

df = pd.read_parquet(DATA_FILE)

# Definir coaliciones
SHH = ['MORENA', 'PT', 'PVEM']
FCM = ['PAN', 'PRI', 'PRD']

print("=" * 80)
print("ANÁLISIS DEL SISTEMA ELECTORAL CORRECTO")
print("300 MR + 100 RP (sin ganadores) + 100 RP Mejores Perdedores (segundos lugares)")
print("=" * 80)

print("\n📊 SISTEMA:")
print("   1. 300 MR - Se calcula normal (ganadores por distrito)")
print("   2. 100 RP - Proporcional, pero SE QUITAN a ganadores de MR")
print("   3. 100 RP Mejores Perdedores - Van a SEGUNDOS LUGARES")
print()
print("   CLAVE: Para recibir 'mejores perdedores', debes haber quedado en")
print("          SEGUNDO LUGAR en distritos (no solo perder)")

# Analizar cada distrito
resultados_por_distrito = []

for idx, row in df.iterrows():
    entidad = row.get('ENTIDAD_NORM', '')
    distrito = row['DISTRITO']
    
    # Votos por coalición
    votos_shh = sum(row.get(p, 0) for p in SHH)
    votos_fcm = sum(row.get(p, 0) for p in FCM)
    votos_mc = row.get('MC', 0)
    
    # Ranking de coaliciones
    coaliciones = [
        ('SHH', votos_shh),
        ('FCM', votos_fcm),
        ('MC', votos_mc)
    ]
    coaliciones_ordenadas = sorted(coaliciones, key=lambda x: -x[1])
    
    primer_lugar = coaliciones_ordenadas[0][0]
    segundo_lugar = coaliciones_ordenadas[1][0]
    tercer_lugar = coaliciones_ordenadas[2][0]
    
    resultados_por_distrito.append({
        'entidad': entidad,
        'distrito': distrito,
        'primer_lugar': primer_lugar,
        'segundo_lugar': segundo_lugar,
        'tercer_lugar': tercer_lugar,
        'votos_1ro': coaliciones_ordenadas[0][1],
        'votos_2do': coaliciones_ordenadas[1][1],
        'votos_3ro': coaliciones_ordenadas[2][1]
    })

df_res = pd.DataFrame(resultados_por_distrito)

# Contar primeros y segundos lugares
print("\n" + "=" * 80)
print("ANÁLISIS 2024: PRIMEROS Y SEGUNDOS LUGARES POR COALICIÓN")
print("=" * 80)

primeros = Counter(df_res['primer_lugar'])
segundos = Counter(df_res['segundo_lugar'])
terceros = Counter(df_res['tercer_lugar'])

print("\n📊 PRIMEROS LUGARES (300 MR):")
for coal in ['SHH', 'FCM', 'MC']:
    count = primeros.get(coal, 0)
    pct = (count / 300 * 100)
    print(f"   {coal:6s}: {count:3d} distritos ({pct:5.1f}%)")

print("\n📊 SEGUNDOS LUGARES (Para Mejores Perdedores):")
for coal in ['SHH', 'FCM', 'MC']:
    count = segundos.get(coal, 0)
    pct = (count / 300 * 100)
    print(f"   {coal:6s}: {count:3d} distritos ({pct:5.1f}%)")

print("\n📊 TERCEROS LUGARES:")
for coal in ['SHH', 'FCM', 'MC']:
    count = terceros.get(coal, 0)
    pct = (count / 300 * 100)
    print(f"   {coal:6s}: {count:3d} distritos ({pct:5.1f}%)")

# Análisis del punto óptimo
print("\n" + "=" * 80)
print("ANÁLISIS DEL PUNTO ÓPTIMO")
print("=" * 80)

print("\nPREGUNTA:")
print("¿Cuántos distritos puedes ganar (1er lugar) antes de quedarte sin")
print("segundos lugares para acomodar los 100 escaños de mejores perdedores?")

print("\n💡 INSIGHT CLAVE:")
print("   • Si ganas un distrito → NO puedes ser segundo en ese distrito")
print("   • Necesitas haber quedado en SEGUNDO LUGAR en suficientes distritos")
print("   • Para 100 escaños de mejores perdedores, necesitas ~100 segundos lugares")

# Análisis por coalición
print("\n" + "=" * 80)
print("ANÁLISIS POR COALICIÓN (2024)")
print("=" * 80)

for coal in ['SHH', 'FCM', 'MC']:
    primeros_coal = primeros.get(coal, 0)
    segundos_coal = segundos.get(coal, 0)
    terceros_coal = terceros.get(coal, 0)
    
    print(f"\n{coal}:")
    print(f"   • Primeros lugares (MR): {primeros_coal}")
    print(f"   • Segundos lugares: {segundos_coal}")
    print(f"   • Terceros lugares: {terceros_coal}")
    print(f"   • Total distritos: {primeros_coal + segundos_coal + terceros_coal}")
    
    # Análisis de capacidad
    if segundos_coal >= 100:
        print(f"   ✅ Suficientes segundos lugares para 100 escaños de mejores perdedores")
    else:
        print(f"   ⚠️ Solo {segundos_coal} segundos lugares (máximo {segundos_coal} de mejores perdedores)")
    
    # Balance óptimo
    if primeros_coal <= 200 and segundos_coal >= 100:
        print(f"   ⭐ ÓPTIMO: Balance perfecto entre MR y segundos lugares")
    elif primeros_coal > 200:
        print(f"   ⚠️ Demasiados primeros lugares → Pocos segundos lugares")
    else:
        print(f"   💡 Podría ganar más MR manteniendo segundos lugares")

# Escenarios teóricos
print("\n" + "=" * 80)
print("ESCENARIOS TEÓRICOS")
print("=" * 80)

print("\n¿Qué pasa si ganas diferentes cantidades de distritos?")
print()
print(f"{'1ros (MR)':<12} {'2dos':<12} {'3ros':<12} {'Puede 100 MP?':<20} {'Comentario':<30}")
print("-" * 90)

escenarios = [
    (0, 300, 0, "✅ SÍ", "Todos segundos → Max mejores perdedores"),
    (50, 200, 50, "✅ SÍ", "Balance excelente"),
    (100, 150, 50, "✅ SÍ", "Aún suficientes segundos"),
    (150, 100, 50, "✅ SÍ (justo)", "En el límite"),
    (200, 100, 0, "✅ SÍ (justo)", "⭐ ÓPTIMO: 200 MR + 100 2dos"),
    (220, 80, 0, "❌ NO (80)", "Insuficientes segundos"),
    (250, 50, 0, "❌ NO (50)", "Muy pocos segundos"),
    (300, 0, 0, "❌ NO (0)", "Sin segundos lugares"),
]

for prim, seg, terc, puede, com in escenarios:
    print(f"{prim:<12} {seg:<12} {terc:<12} {puede:<20} {com:<30}")

print("\n💡 CONCLUSIÓN:")
print("   PUNTO ÓPTIMO: 200 distritos en primer lugar (MR)")
print("   • Ganas 200 → Quedas segundo en 100 → Puedes recibir los 100 MP")
print("   • Después de 200 primeros, empiezas a quedarte sin segundos lugares")

# Análisis real 2024
print("\n" + "=" * 80)
print("CASO REAL 2024")
print("=" * 80)

print("\nSHH (MORENA+PT+PVEM):")
shh_1ros = primeros.get('SHH', 0)
shh_2dos = segundos.get('SHH', 0)
print(f"   • Ganó {shh_1ros} distritos (1er lugar)")
print(f"   • Quedó 2do en {shh_2dos} distritos")
print()

if shh_1ros < 200:
    print(f"   ✅ DEBAJO del óptimo de 200")
    print(f"   • Tiene {shh_2dos} segundos lugares")
    if shh_2dos >= 100:
        print(f"   • ✅ Suficientes para recibir 100 escaños de mejores perdedores")
    else:
        print(f"   • ⚠️ Solo puede recibir {shh_2dos} escaños de mejores perdedores (no 100)")
else:
    print(f"   ⚠️ ARRIBA del óptimo de 200")
    print(f"   • Solo {shh_2dos} segundos lugares disponibles")
    print(f"   • Máximo {shh_2dos} escaños de mejores perdedores (no 100)")

print("\nFCM (PAN+PRI+PRD):")
fcm_1ros = primeros.get('FCM', 0)
fcm_2dos = segundos.get('FCM', 0)
print(f"   • Ganó {fcm_1ros} distritos (1er lugar)")
print(f"   • Quedó 2do en {fcm_2dos} distritos")
if fcm_2dos >= 100:
    print(f"   • ✅ Suficientes segundos lugares para 100 MP")
else:
    print(f"   • Máximo {fcm_2dos} escaños de mejores perdedores")

print("\nMC:")
mc_1ros = primeros.get('MC', 0)
mc_2dos = segundos.get('MC', 0)
print(f"   • Ganó {mc_1ros} distritos (1er lugar)")
print(f"   • Quedó 2do en {mc_2dos} distritos")
if mc_2dos >= 100:
    print(f"   • ✅ Suficientes segundos lugares para 100 MP")
else:
    print(f"   • Máximo {mc_2dos} escaños de mejores perdedores")

# Resumen final
print("\n" + "=" * 80)
print("RESUMEN EJECUTIVO")
print("=" * 80)

print("\n🎯 RESPUESTA A LA PREGUNTA:")
print()
print("   ¿A partir de cuántos distritos ganados te quedas sin")
print("   segundos lugares para acomodar los 100 mejores perdedores?")
print()
print("   RESPUESTA: A partir de 201 distritos ganados en 1er lugar")
print()
print("   PUNTO ÓPTIMO: 200 distritos en 1er lugar")
print("   • Ganas 200 distritos → Quedas 2do en hasta 100 distritos")
print("   • Puedes recibir los 100 escaños de mejores perdedores completos")
print("   • 200 MR + hasta 100 RP + hasta 100 MP = hasta 400 total")
print("   • (Limitado por tope constitucional de 300)")
print()
print("   DESPUÉS DE 200:")
print("   • Ganas 220 → Solo ~80 segundos lugares → Max 80 MP")
print("   • Ganas 250 → Solo ~50 segundos lugares → Max 50 MP")
print("   • Ganas 300 → 0 segundos lugares → 0 MP")

print("\n" + "=" * 80)

# Guardar CSV con detalles
output_csv = 'analisis_primeros_segundos_lugares_2024.csv'
df_res.to_csv(output_csv, index=False, encoding='utf-8-sig')
print(f"\n✅ Archivo guardado: {output_csv}")
print(f"   Contiene todos los distritos con 1er, 2do y 3er lugar")
