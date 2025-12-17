"""
DIAGNÓSTICO: ¿Por qué MORENA tiene 247 en vez de 257 escaños?

Paso 1: Verificar conteo de MR (Mayoría Relativa)
- Motor dice: 160 MR
- Verificar: ¿Cuántos distritos ganó MORENA realmente?
"""

import pandas as pd
from engine.siglado import asignar_mr_recompose

print("="*80)
print("DIAGNÓSTICO 1: Conteo de MR (Mayoría Relativa)")
print("="*80)

# Cargar datos de votos
print("\n📊 Cargando datos de votos por distrito...")
df_votos = pd.read_parquet("data/computos_diputados_2024.parquet")
print(f"   Total filas en datos: {len(df_votos)}")

# Cargar siglado
print("\n📋 Cargando siglado oficial...")
df_siglado = pd.read_csv("data/siglado-diputados-2024.csv")
print(f"   Total filas en siglado: {len(df_siglado)}")
print(f"   Distritos únicos: {df_siglado.groupby(['entidad', 'distrito']).ngroups}")

# Procesar MR usando la función del motor
print("\n🔍 Procesando ganadores de MR con la función del motor...")
try:
    mr_result = asignar_mr_recompose(
        df=df_votos,
        anio=2024,
        path_siglado="data/siglado-diputados-2024.csv",
        usar_coaliciones=True  # Usar coaliciones como en el sistema vigente
    )
    
    print("\n✅ Procesamiento completado")
    
    # Contar ganadores por partido
    if isinstance(mr_result, dict):
        print("\n📈 Ganadores de MR por partido:")
        print("-" * 40)
        total = 0
        for partido, escanos in sorted(mr_result.items(), key=lambda x: x[1], reverse=True):
            print(f"  {partido:<12} {escanos:>3} distritos")
            total += escanos
        print("-" * 40)
        print(f"  {'TOTAL':<12} {total:>3} distritos")
        
        morena_mr = mr_result.get('MORENA', 0)
        
        print(f"\n🎯 MORENA ganó {morena_mr} distritos de MR")
        print(f"   Motor reporta: 160 MR")
        
        if morena_mr == 160:
            print(f"   ✅ CORRECTO: El conteo de MR coincide")
        else:
            print(f"   ❌ DISCREPANCIA: Diferencia de {abs(morena_mr - 160)} distritos")
            print(f"   📍 El problema NO está en el conteo de MR")
    else:
        print(f"\n⚠️ Formato inesperado: {type(mr_result)}")
        print(f"   Contenido: {mr_result}")
        
except Exception as e:
    print(f"\n❌ ERROR al procesar MR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("CONCLUSIÓN PASO 1:")
print("="*80)
print("Si MR = 160 es correcto, entonces el problema está en:")
print("  - Asignación de RP (Representación Proporcional)")
print("  - O aplicación de topes constitucionales")
