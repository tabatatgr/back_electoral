"""
Verificar que 2021 vs 2021_SWING sean diferentes en el CSV recién generado
"""
import pandas as pd

# Leer el CSV más reciente
csv_path = 'outputs/escenarios_morena_CON_TOPES_20251028_151932.csv'
df = pd.read_csv(csv_path)

print(f"📊 VERIFICANDO: {csv_path.split('/')[-1]}")
print(f"Total escenarios: {len(df)}")
print(f"Años: {sorted(df['anio'].unique())}\n")

# Filtrar 2021 y 2021_SWING
df_2021 = df[df['anio'] == '2021'].reset_index(drop=True)
df_2021_swing = df[df['anio'] == '2021_SWING'].reset_index(drop=True)

print(f"Escenarios 2021: {len(df_2021)}")
print(f"Escenarios 2021_SWING: {len(df_2021_swing)}\n")

# Comparar lado a lado
print("="*100)
print("COMPARACIÓN 2021 vs 2021_SWING (primeros 5 escenarios)")
print("="*100)

for idx in range(min(5, len(df_2021))):
    r1 = df_2021.iloc[idx]
    r2 = df_2021_swing.iloc[idx]
    
    diff_escanos = r2['morena_total'] - r1['morena_total']
    diff_votos = r2['morena_votos_pct'] - r1['morena_votos_pct']
    
    print(f"\n[{idx+1}] {r1['total_escanos']} escaños | {r1['configuracion']} | {r1['usar_coaliciones']}")
    print(f"     2021:       MORENA {r1['morena_total']:3d} escaños ({r1['morena_votos_pct']:5.2f}%) | MR:{r1['morena_mr']:3d} + RP:{r1['morena_rp']:3d}")
    print(f"     2021_SWING: MORENA {r2['morena_total']:3d} escaños ({r2['morena_votos_pct']:5.2f}%) | MR:{r2['morena_mr']:3d} + RP:{r2['morena_rp']:3d}")
    print(f"     DIFERENCIA: {diff_escanos:+3d} escaños ({diff_votos:+5.2f}%)")

# Resumen estadístico
print("\n" + "="*100)
print("RESUMEN ESTADÍSTICO DE TODAS LAS COMPARACIONES")
print("="*100)

diferencias = []
for idx in range(len(df_2021)):
    r1 = df_2021.iloc[idx]
    r2 = df_2021_swing.iloc[idx]
    
    diferencias.append({
        'diff_escanos': r2['morena_total'] - r1['morena_total'],
        'diff_votos_pct': r2['morena_votos_pct'] - r1['morena_votos_pct']
    })

df_diff = pd.DataFrame(diferencias)

print(f"\n✅ Escenarios con DIFERENCIA en escaños: {(df_diff['diff_escanos'] != 0).sum()}/{len(df_diff)}")
print(f"✅ Escenarios con DIFERENCIA en votos:   {(df_diff['diff_votos_pct'].abs() > 0.01).sum()}/{len(df_diff)}")

print(f"\nDiferencia en escaños:")
print(f"  Mínima: {df_diff['diff_escanos'].min():+d}")
print(f"  Máxima: {df_diff['diff_escanos'].max():+d}")
print(f"  Promedio: {df_diff['diff_escanos'].mean():+.2f}")

print(f"\nDiferencia en votos %:")
print(f"  Mínima: {df_diff['diff_votos_pct'].min():+.2f}%")
print(f"  Máxima: {df_diff['diff_votos_pct'].max():+.2f}%")
print(f"  Promedio: {df_diff['diff_votos_pct'].mean():+.2f}%")

# Verificación final
if (df_diff['diff_escanos'] == 0).all() and (df_diff['diff_votos_pct'].abs() <= 0.01).all():
    print("\n❌ ERROR: NO HAY DIFERENCIAS - 2021 y 2021_SWING son IDÉNTICOS!")
else:
    print(f"\n✅ ÉXITO: El swing SÍ está funcionando - hay diferencias entre 2021 y 2021_SWING! 🎉")
