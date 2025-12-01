"""
Verificar cálculo de mayorías simple y calificada
"""
import pandas as pd
import math

csv_path = 'outputs/escenarios_morena_CON_TOPES_20251028_153103.csv'
df = pd.read_csv(csv_path)

print("="*100)
print("VERIFICACIÓN DE CÁLCULO DE MAYORÍAS")
print("="*100)

# Mostrar algunos ejemplos
print("\nPrimeros 10 escenarios:")
print("-"*100)

for idx in range(10):
    row = df.iloc[idx]
    escanos = row['total_escanos']
    coal_tot = row['coalicion_total']
    coal_pct = row['coalicion_pct_escanos']
    mayoria_simple = row['mayoria_simple']
    mayoria_calif = row['mayoria_calificada']
    
    # Calcular umbrales
    umbral_simple = escanos / 2  # Más de 50%
    umbral_calif = math.ceil(escanos * 2 / 3)  # 2/3
    
    print(f"\n[{idx+1}] {row['anio']} | {escanos} escaños | {row['configuracion']} | {row['usar_coaliciones']}")
    print(f"    Coalición: {coal_tot} escaños ({coal_pct:.1f}%)")
    print(f"    Umbral simple: > {umbral_simple:.1f} ({umbral_simple/escanos*100:.1f}%)")
    print(f"    Umbral calificada: >= {umbral_calif} ({umbral_calif/escanos*100:.1f}%)")
    print(f"    ✓ Mayoría simple: {mayoria_simple} (tiene {coal_tot} > {umbral_simple}? {coal_tot > umbral_simple})")
    print(f"    ✓ Mayoría calificada: {mayoria_calif} (tiene {coal_tot} >= {umbral_calif}? {coal_tot >= umbral_calif})")
    
    # Verificar que sea correcto
    esperado_simple = coal_tot > umbral_simple
    esperado_calif = coal_tot >= umbral_calif
    
    if mayoria_simple != esperado_simple or mayoria_calif != esperado_calif:
        print(f"    ❌ ERROR: Mayoría simple esperada={esperado_simple}, obtenida={mayoria_simple}")
        print(f"    ❌ ERROR: Mayoría calificada esperada={esperado_calif}, obtenida={mayoria_calif}")
    else:
        print(f"    ✅ CORRECTO")

# Buscar casos de mayoría calificada
print("\n" + "="*100)
print("CASOS CON MAYORÍA CALIFICADA (2/3)")
print("="*100)

df_calif = df[df['mayoria_calificada'] == True]
print(f"\nTotal escenarios con mayoría calificada: {len(df_calif)}/{len(df)}")

if len(df_calif) > 0:
    print("\nEjemplos:")
    for idx, row in df_calif.head(5).iterrows():
        umbral = math.ceil(row['total_escanos'] * 2 / 3)
        print(f"  {row['anio']} | {row['total_escanos']} escaños | {row['configuracion']} | {row['usar_coaliciones']}")
        print(f"    Coalición: {row['coalicion_total']} escaños >= {umbral} (2/3) ✓")

# Buscar casos sin mayoría simple
print("\n" + "="*100)
print("CASOS SIN MAYORÍA SIMPLE (MINORÍA)")
print("="*100)

df_minoria = df[df['mayoria_simple'] == False]
print(f"\nTotal escenarios sin mayoría simple: {len(df_minoria)}/{len(df)}")

if len(df_minoria) > 0:
    print("\nEjemplos:")
    for idx, row in df_minoria.head(5).iterrows():
        umbral = row['total_escanos'] / 2
        print(f"  {row['anio']} | {row['total_escanos']} escaños | {row['configuracion']} | {row['usar_coaliciones']}")
        print(f"    Coalición: {row['coalicion_total']} escaños <= {umbral} (50%) ✗")
