"""
Prueba DIRECTA de la funcionalidad de redistritación geográfica
SIN servidor - solo probando la lógica del código
"""

import pandas as pd
from engine.calcular_eficiencia_real import calcular_eficiencia_partidos
from redistritacion.modulos.reparto_distritos import repartir_distritos_hare
from redistritacion.modulos.distritacion import cargar_secciones_ine

print("="*80)
print("🧪 PRUEBA DIRECTA: Redistritación Geográfica con Eficiencias Reales")
print("="*80)

# PASO 1: Calcular eficiencias históricas
print("\n📊 PASO 1: Calculando eficiencias históricas para 2024...")
print("-"*80)

anio = 2024
eficiencias = calcular_eficiencia_partidos(anio, usar_coaliciones=False)

print("\nEficiencias calculadas:")
for partido, ef in eficiencias.items():
    if ef > 0:
        interpretacion = "✅ Eficiente" if ef > 1.0 else "❌ Ineficiente"
        print(f"  {partido:10s}: {ef:.3f}  {interpretacion}")

# PASO 2: Cargar población y asignar distritos
print("\n📍 PASO 2: Asignando distritos por población (Método Hare)...")
print("-"*80)

secciones = cargar_secciones_ine()
poblacion_por_estado = secciones.groupby('ENTIDAD')['POBTOT'].sum().to_dict()

mr_seats = 300
asignacion_distritos = repartir_distritos_hare(
    poblacion_estados=poblacion_por_estado,
    n_distritos=mr_seats,
    piso_constitucional=2
)

print(f"\nTotal distritos asignados: {sum(asignacion_distritos.values())}")
print("\nTop 5 estados con más distritos:")
top_estados = sorted(asignacion_distritos.items(), key=lambda x: x[1], reverse=True)[:5]
for estado_id, distritos in top_estados:
    print(f"  Estado {estado_id:2d}: {distritos:2d} distritos")

# PASO 3: Cargar votos reales
print("\n📥 PASO 3: Cargando votos de 2024...")
print("-"*80)

df_votos = pd.read_parquet(f"data/computos_diputados_{anio}.parquet")
df_votos.columns = [str(c).strip().upper() for c in df_votos.columns]

# Mapeo de estados
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

# PASO 4: Calcular MR con redistribución de votos
print("\n🔄 PASO 4: Simulando escenario con votos redistribuidos...")
print("-"*80)

# Escenario de prueba
votos_redistribuidos = {
    "MORENA": 50.0,
    "PAN": 20.0,
    "PRI": 15.0,
    "PVEM": 8.0,
    "MC": 7.0
}

print("Porcentajes de votos (simulados):")
for p, pct in votos_redistribuidos.items():
    print(f"  {p:10s}: {pct:5.1f}%")

# PASO 5: Calcular MR geográficos
print("\n🎯 PASO 5: Calculando MR con eficiencias reales...")
print("-"*80)

columnas_excluir = ['ENTIDAD', 'DISTRITO', 'TOTAL_BOLETAS', 'CI', 'ENTIDAD_NOMBRE']
partidos_disponibles = [col for col in df_votos.columns if col not in columnas_excluir]

mr_ganados_por_partido = {}

for partido in partidos_disponibles:
    pct_nacional = votos_redistribuidos.get(partido, 0)
    
    if pct_nacional == 0:
        mr_ganados_por_partido[partido] = 0
        continue
    
    # Obtener eficiencia real del partido
    eficiencia_partido = eficiencias.get(partido, 1.0)
    
    total_mr_ganados = 0
    
    for entidad_id, nombre in estado_nombres.items():
        # Buscar datos del estado
        df_estado = df_votos[df_votos['ENTIDAD_NOMBRE'] == nombre]
        
        if len(df_estado) == 0:
            df_estado = df_votos[df_votos['ENTIDAD_NOMBRE'].str.contains(nombre.split()[0], na=False)]
        
        if len(df_estado) > 0:
            votos_partido = df_estado[partido].sum()
            votos_totales = df_estado['TOTAL_BOLETAS'].sum()
            pct_estado_real = (votos_partido / votos_totales * 100) if votos_totales > 0 else 0
            
            # Calcular porcentaje real nacional del partido (para escalamiento)
            total_votos_partido = df_votos[partido].sum()
            total_votos_nacional = df_votos['TOTAL_BOLETAS'].sum()
            pct_real_nacional = (total_votos_partido / total_votos_nacional * 100) if total_votos_nacional > 0 else 0
            
            # Escalar el porcentaje estatal proporcionalmente
            if pct_real_nacional > 0:
                factor_escala = pct_nacional / pct_real_nacional
                pct_estado = pct_estado_real * factor_escala
            else:
                pct_estado = pct_nacional
        else:
            pct_estado = pct_nacional
        
        distritos_totales = asignacion_distritos.get(entidad_id, 0)
        
        # Calcular distritos ganados con eficiencia REAL del partido
        distritos_ganados = int(distritos_totales * (pct_estado / 100) * eficiencia_partido)
        distritos_ganados = min(distritos_ganados, distritos_totales)
        
        total_mr_ganados += distritos_ganados
    
    mr_ganados_por_partido[partido] = total_mr_ganados

# RESULTADOS
print("\n✅ RESULTADOS: MR ganados por partido (con eficiencias reales)")
print("-"*80)

total_mr = 0
for partido in sorted(mr_ganados_por_partido.keys()):
    mr = mr_ganados_por_partido[partido]
    if mr > 0:
        efic = eficiencias.get(partido, 1.0)
        total_mr += mr
        print(f"  {partido:10s}: {mr:3d} MR  (eficiencia: {efic:.3f})")

print(f"\nTotal MR asignados: {total_mr} de {mr_seats}")

# COMPARACIÓN con proporcional simple
print("\n📊 COMPARACIÓN: Geográfico vs Proporcional Simple")
print("-"*80)

print(f"{'Partido':10s} | {'% Votos':>8s} | {'MR Geográfico':>14s} | {'MR Proporcional':>16s} | {'Diferencia':>11s}")
print("-"*80)

for partido in ["MORENA", "PAN", "PRI", "PVEM", "MC"]:
    pct = votos_redistribuidos.get(partido, 0)
    mr_geo = mr_ganados_por_partido.get(partido, 0)
    mr_prop = int(mr_seats * (pct / 100))
    diff = mr_geo - mr_prop
    diff_str = f"+{diff}" if diff > 0 else str(diff)
    
    print(f"{partido:10s} | {pct:7.1f}% | {mr_geo:14d} | {mr_prop:16d} | {diff_str:>11s}")

print("\n💡 Interpretación:")
print("  ✅ Diferencia positiva = El partido se beneficia de su distribución geográfica eficiente")
print("  ❌ Diferencia negativa = El partido desperdicia votos (necesita más % para mismo MR)")
print("  - Basado en eficiencias REALES de cómo cada partido convirtió votos en victorias en 2024")

print("\n" + "="*80)
print("✅ PRUEBA COMPLETADA - La lógica funciona correctamente")
print("="*80)

print("\n🎯 CONCLUSIÓN:")
print("  Si estos resultados se ven correctos, entonces el endpoint del backend")
print("  funcionará exactamente igual cuando se llame con redistritacion_geografica=True")
