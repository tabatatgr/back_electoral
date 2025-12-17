"""
Análisis correcto del siglado 2024: contar distritos únicos por entidad-distrito
"""

import pandas as pd

# Cargar siglado 2024
siglado = pd.read_csv('data/siglado-diputados-2024.csv')

print("=" * 80)
print("ANÁLISIS CORRECTO DEL SIGLADO 2024")
print("=" * 80)

# Crear identificador único por entidad+distrito
siglado['entidad_distrito'] = siglado['entidad'] + '_' + siglado['distrito'].astype(str)

distritos_unicos = siglado['entidad_distrito'].nunique()
print(f"\n📊 Distritos únicos (entidad + distrito): {distritos_unicos}")

print("\n" + "=" * 80)
print("DISTRIBUCIÓN DE MR POR GRUPO PARLAMENTARIO")
print("=" * 80)

# Contar por grupo parlamentario
conteo_gp = siglado['grupo_parlamentario'].value_counts().sort_values(ascending=False)
print("\n" + conteo_gp.to_string())

print(f"\n✅ Total filas: {conteo_gp.sum()}")

print("\n" + "=" * 80)
print("ANÁLISIS POR COALICIÓN")
print("=" * 80)

# SIGAMOS HACIENDO HISTORIA
sigamos = siglado[siglado['coalicion'] == 'SIGAMOS HACIENDO HISTORIA']
print(f"\n🟢 SIGAMOS HACIENDO HISTORIA: {len(sigamos)} filas")
print("   Distribución:")
print(sigamos['grupo_parlamentario'].value_counts().to_string())

total_sigamos = len(sigamos['entidad_distrito'].unique())
print(f"   Distritos únicos: {total_sigamos}")

# FUERZA Y CORAZON POR MEXICO
fuerza = siglado[siglado['coalicion'] == 'FUERZA Y CORAZON POR MEXICO']
print(f"\n🔵 FUERZA Y CORAZON POR MEXICO: {len(fuerza)} filas")
print("   Distribución:")
print(fuerza['grupo_parlamentario'].value_counts().to_string())

total_fuerza = len(fuerza['entidad_distrito'].unique())
print(f"   Distritos únicos: {total_fuerza}")

print("\n" + "=" * 80)
print("🎯 COMPARACIÓN CON DATOS OFICIALES Y MOTOR")
print("=" * 80)

resultados = {
    'MORENA': {'siglado': 142, 'motor': 160, 'oficial_mr': 257 - 85},  # 257 total - 85 RP = 172 MR
    'PAN': {'siglado': 114, 'motor': 33, 'oficial_mr': 71 - 35},  # 71 total - 35 RP = 36 MR
    'PVEM': {'siglado': 71, 'motor': 58, 'oficial_mr': 60 - 18},  # 60 total - 18 RP = 42 MR
    'PT': {'siglado': 46, 'motor': 38, 'oficial_mr': 47 - 11},  # 47 total - 11 RP = 36 MR
    'PRI': {'siglado': 111, 'motor': 9, 'oficial_mr': 36 - 23},  # 36 total - 23 RP = 13 MR
    'MC': {'siglado': 0, 'motor': 1, 'oficial_mr': 27 - 23},  # 27 total - 23 RP = 4 MR
    'PRD': {'siglado': 69, 'motor': 0, 'oficial_mr': 1 - 5},  # 1 total - 5 RP = -4 ??? (no tiene sentido)
}

print(f"\n{'Partido':<8} {'Siglado':>8} {'Motor':>8} {'Oficial MR':>12} {'Siglado-Motor':>15} {'Siglado-Oficial':>18}")
print("-" * 90)

for partido, datos in resultados.items():
    siglado_val = datos['siglado']
    motor_val = datos['motor']
    oficial_val = datos['oficial_mr']
    diff_motor = siglado_val - motor_val
    diff_oficial = siglado_val - oficial_val
    
    print(f"{partido:<8} {siglado_val:>8} {motor_val:>8} {oficial_val:>12} {diff_motor:>15} {diff_oficial:>18}")

print("\n" + "=" * 80)
print("💡 HALLAZGOS CLAVE:")
print("=" * 80)

print("\n1. SIGLADO dice:")
print("   - PVEM: 71 MR")
print("   - MORENA: 142 MR")
print("   - PT: 46 MR")

print("\n2. MOTOR da:")
print("   - PVEM: 58 MR")
print("   - MORENA: 160 MR")
print("   - PT: 38 MR")

print("\n3. OFICIAL debería ser (basado en oficial total - RP calculado):")
print("   - PVEM: 42 MR (60 total - 18 RP)")
print("   - MORENA: 172 MR (257 total - 85 RP)")
print("   - PT: 36 MR (47 total - 11 RP)")

print("\n⚠️  INCONSISTENCIA:")
print("   - El SIGLADO no coincide con el MOTOR")
print("   - Ni el SIGLADO ni el MOTOR coinciden con el OFICIAL")
print("\n   PREGUNTA: ¿El motor está procesando correctamente el siglado?")
print("   Si no lo hace, ¿dónde está el error?")
