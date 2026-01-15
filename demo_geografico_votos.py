"""
Demo simple: Redistritación geográfica por defecto con votos personalizados
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.procesar_diputados_v2 import procesar_diputados_v2
from redistritacion.modulos.reparto_distritos import repartir_distritos_hare
from redistritacion.modulos.distritacion import cargar_secciones_ine
from engine.calcular_eficiencia_real import calcular_eficiencia_partidos
import pandas as pd

print("=" * 80)
print("DEMO: Escenario 300-100 con Votos Personalizados")
print("=" * 80)

# Escenario de ejemplo: Elecciones 2027 proyectadas
votos_proyectados = {
    "MORENA": 38.0,   # Baja respecto a 2024
    "PAN": 22.0,      # Sube
    "PRI": 15.0,      # Sube
    "MC": 15.0,       # Sube mucho
    "PVEM": 7.0,      # Baja
    "PT": 3.0         # Baja
}

print(f"\n📊 Proyección de votos 2027:")
for partido, votos in sorted(votos_proyectados.items(), key=lambda x: x[1], reverse=True):
    print(f"  {partido}: {votos}%")

# Calcular MR geográficos con las proyecciones
print(f"\n🌍 Calculando MR con redistritación geográfica...")

anio = 2024  # Usar eficiencias de 2024
mr_seats = 300

# Paso 1: Eficiencias históricas
eficiencias = calcular_eficiencia_partidos(anio, usar_coaliciones=True)
print(f"\nEficiencias históricas (2024):")
for partido in sorted(votos_proyectados.keys()):
    ef = eficiencias.get(partido, 0.0)
    print(f"  {partido}: {ef:.3f}")

# Paso 2: Reparto de distritos por población
secciones = cargar_secciones_ine()
poblacion_por_estado = secciones.groupby('ENTIDAD')['POBTOT'].sum().to_dict()

asignacion_distritos = repartir_distritos_hare(
    poblacion_estados=poblacion_por_estado,
    n_distritos=mr_seats,
    piso_constitucional=2
)

print(f"\nDistritos por estado (top 5):")
top_estados = sorted(asignacion_distritos.items(), key=lambda x: x[1], reverse=True)[:5]
estado_nombres_inv = {
    1: 'Aguascalientes', 2: 'Baja California', 9: 'CDMX',
    11: 'Guanajuato', 14: 'Jalisco', 15: 'México', 19: 'Nuevo León'
}
for estado_id, distritos in top_estados:
    nombre = estado_nombres_inv.get(estado_id, f"Estado {estado_id}")
    print(f"  {nombre}: {distritos} distritos")

# Paso 3: Calcular MR por partido
df_votos = pd.read_parquet("data/computos_diputados_2024.parquet")

estado_nombres = {
    1: 'AGUASCALIENTES', 2: 'BAJA CALIFORNIA', 3: 'BAJA CALIFORNIA SUR',
    4: 'CAMPECHE', 5: 'CHIAPAS', 6: 'CHIHUAHUA', 7: 'COAHUILA',
    8: 'COLIMA', 9: 'CIUDAD DE MEXICO', 10: 'DURANGO', 11: 'GUANAJUATO',
    12: 'GUERRERO', 13: 'HIDALGO', 14: 'JALISCO', 15: 'MEXICO',
    16: 'MICHOACAN', 17: 'MORELOS', 18: 'NAYARIT', 19: 'NUEVO LEON',
    20: 'OAXACA', 21: 'PUEBLA', 22: 'QUERETARO', 23: 'QUINTANA ROO',
    24: 'SAN LUIS POTOSI', 25: 'SINALOA', 26: 'SONORA', 27: 'TABASCO',
    28: 'TAMAULIPAS', 29: 'TLAXCALA', 30: 'VERACRUZ', 31: 'YUCATAN',
    32: 'ZACATECAS'
}

df_votos['ENTIDAD_NOMBRE'] = df_votos['ENTIDAD'].str.strip().str.upper()

mr_ganados_geograficos = {}

for partido in votos_proyectados.keys():
    pct_nacional = votos_proyectados[partido]
    eficiencia_partido = eficiencias.get(partido, 1.0)
    
    total_mr_ganados = 0
    
    for entidad_id, nombre in estado_nombres.items():
        df_estado = df_votos[df_votos['ENTIDAD_NOMBRE'] == nombre]
        
        if len(df_estado) == 0:
            df_estado = df_votos[df_votos['ENTIDAD_NOMBRE'].str.contains(nombre.split()[0], na=False)]
        
        if len(df_estado) > 0 and partido in df_estado.columns:
            votos_partido = df_estado[partido].sum()
            votos_totales = df_estado['TOTAL_BOLETAS'].sum()
            pct_estado_real = (votos_partido / votos_totales * 100) if votos_totales > 0 else 0
            
            # Escalar con proyección nacional
            pct_real_nacional = (df_votos[partido].sum() / df_votos['TOTAL_BOLETAS'].sum() * 100)
            
            if pct_real_nacional > 0:
                factor_escala = pct_nacional / pct_real_nacional
                pct_estado = pct_estado_real * factor_escala
            else:
                pct_estado = pct_nacional
        else:
            pct_estado = pct_nacional
        
        distritos_totales = asignacion_distritos.get(entidad_id, 0)
        distritos_ganados = int(distritos_totales * (pct_estado / 100) * eficiencia_partido)
        distritos_ganados = min(distritos_ganados, distritos_totales)
        
        total_mr_ganados += distritos_ganados
    
    mr_ganados_geograficos[partido] = total_mr_ganados

print(f"\nMR ganados (redistritación geográfica):")
for partido, mr in sorted(mr_ganados_geograficos.items(), key=lambda x: x[1], reverse=True):
    print(f"  {partido}: {mr} MR")

# Paso 4: Ejecutar el motor completo (300 MR + 100 RP)
print(f"\n🔧 Ejecutando motor completo (300 MR + 100 RP)...")

resultado = procesar_diputados_v2(
    path_parquet="data/computos_diputados_2024.parquet",
    anio=2024,
    path_siglado="data/siglado-diputados-2024.csv",
    max_seats=400,
    sistema="mixto",
    mr_seats=300,
    rp_seats=100,
    pm_seats=None,
    umbral=3.0,
    max_seats_per_party=None,
    sobrerrepresentacion=None,
    aplicar_topes=False,
    quota_method="hare",
    divisor_method="dhondt",
    usar_coaliciones=True,
    votos_redistribuidos=votos_proyectados,
    mr_ganados_geograficos=mr_ganados_geograficos,
    seed=42
)

# Mostrar resultados finales
print(f"\n" + "=" * 80)
print("RESULTADOS FINALES: 300 MR + 100 RP = 400 TOTAL")
print("=" * 80)

print(f"\n{'Partido':<12} {'Votos %':<10} {'MR':<8} {'RP':<8} {'TOTAL':<8} {'% Cámara':<10}")
print("-" * 70)

total_escanos = sum(resultado['tot'].values())

for partido in sorted(resultado['tot'].keys(), key=lambda p: resultado['tot'][p], reverse=True):
    votos_pct = votos_proyectados.get(partido, 0)
    mr = resultado['mr'][partido]
    rp = resultado['rp'][partido]
    total = resultado['tot'][partido]
    pct_camara = (total / total_escanos * 100) if total_escanos > 0 else 0
    
    if total > 0:
        print(f"{partido:<12} {votos_pct:<10.1f} {mr:<8} {rp:<8} {total:<8} {pct_camara:<10.1f}")

print("-" * 70)
print(f"{'TOTAL':<12} {sum(votos_proyectados.values()):<10.1f} {sum(resultado['mr'].values()):<8} "
      f"{sum(resultado['rp'].values()):<8} {total_escanos:<8} {'100.0':<10}")

# Análisis
print(f"\n" + "=" * 80)
print("ANÁLISIS")
print("=" * 80)

print(f"\n📊 Observaciones:")

# Partido con más MR
partido_mas_mr = max(resultado['mr'].items(), key=lambda x: x[1])
print(f"1. {partido_mas_mr[0]} gana más MR: {partido_mas_mr[1]} distritos")

# Partido más eficiente
eficiencias_efectivas = {}
for partido in votos_proyectados.keys():
    if votos_proyectados[partido] > 0:
        mr_pct = (resultado['mr'][partido] / 300 * 100)
        votos_pct = votos_proyectados[partido]
        eficiencias_efectivas[partido] = mr_pct / votos_pct

partido_mas_eficiente = max(eficiencias_efectivas.items(), key=lambda x: x[1])
print(f"2. {partido_mas_eficiente[0]} es el más eficiente: {partido_mas_eficiente[1]:.2f}x")

# Mayoría absoluta
mayoria_absoluta = 201  # 50% + 1 de 400
partido_con_mayoria = [p for p in resultado['tot'].keys() if resultado['tot'][p] >= mayoria_absoluta]
if partido_con_mayoria:
    print(f"3. ✅ {partido_con_mayoria[0]} tiene MAYORÍA ABSOLUTA ({resultado['tot'][partido_con_mayoria[0]]} escaños)")
else:
    print(f"3. ❌ NINGÚN partido tiene mayoría absoluta (se requieren {mayoria_absoluta} escaños)")

# Coalición necesaria
if not partido_con_mayoria:
    partido_mayor = max(resultado['tot'].items(), key=lambda x: x[1])
    escanos_faltantes = mayoria_absoluta - partido_mayor[1]
    print(f"4. {partido_mayor[0]} necesita {escanos_faltantes} escaños más para mayoría")
    
    # Buscar aliado potencial
    otros_partidos = [(p, resultado['tot'][p]) for p in resultado['tot'].keys() 
                      if p != partido_mayor[0] and resultado['tot'][p] > 0]
    otros_partidos.sort(key=lambda x: x[1], reverse=True)
    
    for aliado, escanos in otros_partidos:
        if partido_mayor[1] + escanos >= mayoria_absoluta:
            print(f"   → Alianza con {aliado} ({escanos} escaños) = {partido_mayor[1] + escanos} escaños ✅")
            break

print(f"\n" + "=" * 80)
print("✅ DEMO COMPLETADA")
print("=" * 80)
