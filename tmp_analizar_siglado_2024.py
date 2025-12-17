"""
Analizar el siglado 2024: ¿A qué partidos se asignaron los escaños de MR?
"""

import pandas as pd

# Cargar siglado 2024
siglado = pd.read_csv('data/siglado-diputados-2024.csv')

print("=" * 80)
print("ANÁLISIS DEL SIGLADO 2024 - DISTRIBUCIÓN DE MR")
print("=" * 80)

print(f"\n📊 Total filas en siglado: {len(siglado)}")

# ¿Cuántos distritos únicos hay?
distritos_unicos = siglado['distrito'].nunique()
print(f"📊 Distritos únicos: {distritos_unicos}")

# Ver coaliciones
print("\n📊 Coaliciones presentes:")
print(siglado['coalicion'].value_counts())

# Ver distribución por grupo parlamentario
print("\n" + "=" * 80)
print("DISTRIBUCIÓN DE MR POR GRUPO PARLAMENTARIO (según siglado)")
print("=" * 80)

conteo_gp = siglado['grupo_parlamentario'].value_counts().sort_values(ascending=False)
print("\n" + conteo_gp.to_string())

print("\n" + "=" * 80)
print("ANÁLISIS DETALLADO")
print("=" * 80)

# Separar por coalición
sigamos = siglado[siglado['coalicion'] == 'SIGAMOS HACIENDO HISTORIA']
fuerza = siglado[siglado['coalicion'] == 'FUERZA Y CORAZON POR MEXICO']

print(f"\n🟢 SIGAMOS HACIENDO HISTORIA (MORENA-PT-PVEM): {len(sigamos)} distritos")
print("   Distribución interna:")
print(sigamos['grupo_parlamentario'].value_counts().to_string())

print(f"\n🔵 FUERZA Y CORAZON POR MEXICO (PAN-PRI-PRD): {len(fuerza)} distritos")
print("   Distribución interna:")
print(fuerza['grupo_parlamentario'].value_counts().to_string())

print("\n" + "=" * 80)
print("🎯 PVEM ESPECÍFICAMENTE:")
print("=" * 80)

pvem_mr = conteo_gp.get('PVEM', 0)
print(f"\n  MR según siglado: {pvem_mr} distritos")
print(f"  MR según motor: 58 distritos")
print(f"  MR esperado (60 total - 18 RP): 42 distritos")

if pvem_mr == 58:
    print("\n  ✅ El siglado SÍ dice que PVEM ganó 58 distritos")
    print("     Pero esto es INCORRECTO si el oficial es 60 total (60 - 18 RP = 42 MR)")
elif pvem_mr == 42:
    print("\n  ✅ El siglado dice correctamente que PVEM ganó 42 distritos")
    print("     Esto coincide con 60 total - 18 RP = 42 MR")
else:
    print(f"\n  ⚠️  El siglado dice {pvem_mr} distritos (no coincide con ninguna expectativa)")

print("\n" + "=" * 80)
print("💡 HIPÓTESIS:")
print("=" * 80)

print("\nPosibles explicaciones:")
print("1. El siglado está INCORRECTO (asigna mal los escaños entre MORENA/PT/PVEM)")
print("2. El motor está procesando CORRECTAMENTE el siglado incorrecto")
print("3. Los datos oficiales no coinciden con el siglado")
print("\nSi el siglado dice PVEM=58, MORENA=160, PT=38, entonces el motor está")
print("leyendo correctamente el siglado, pero el SIGLADO está mal distribuido.")
