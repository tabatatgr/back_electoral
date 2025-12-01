import pandas as pd
import math

df = pd.read_csv('outputs/escenarios_morena_CON_TOPES_20251028_153103.csv')

print("Casos con mayoría calificada:", len(df[df['mayoria_calificada']==True]))
print("Casos con mayoría simple:", len(df[df['mayoria_simple']==True]))
print("Casos sin mayoría:", len(df[df['mayoria_simple']==False]))

print("\nEjemplo MAYORÍA CALIFICADA:")
row = df[df['mayoria_calificada']==True].iloc[0]
umbral = math.ceil(row['total_escanos']*2/3)
print(f"  {row['anio']} | {row['total_escanos']} escaños | {row['configuracion']} | {row['usar_coaliciones']}")
print(f"  Coalición: {row['coalicion_total']} escaños ({row['coalicion_pct_escanos']:.1f}%) >= {umbral} (2/3) ✓")

print("\nEjemplo MINORÍA:")
if len(df[df['mayoria_simple']==False]) > 0:
    row = df[df['mayoria_simple']==False].iloc[0]
    umbral = row['total_escanos']/2
    print(f"  {row['anio']} | {row['total_escanos']} escaños | {row['configuracion']} | {row['usar_coaliciones']}")
    print(f"  Coalición: {row['coalicion_total']} escaños ({row['coalicion_pct_escanos']:.1f}%) <= {umbral} (50%) ✗")
