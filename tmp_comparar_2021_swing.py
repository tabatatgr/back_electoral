"""
Script temporal para comparar 2021 vs 2021_SWING
"""
import pandas as pd

# Leer CSV más reciente
df = pd.read_csv('outputs/escenarios_morena_CON_TOPES_20251028_143319.csv')

print("="*80)
print("COMPARACIÓN 2021 vs 2021_SWING")
print("="*80)

# Filtrar por año
df_2021 = df[df['anio'] == '2021'].sort_values(['escanos_totales', 'config_mr_rp', 'usa_coaliciones']).reset_index(drop=True)
df_swing = df[df['anio'] == '2021_SWING'].sort_values(['escanos_totales', 'config_mr_rp', 'usa_coaliciones']).reset_index(drop=True)

print(f"\nTotal escenarios 2021: {len(df_2021)}")
print(f"Total escenarios 2021_SWING: {len(df_swing)}")

# Comparar los primeros 5 escenarios
print("\n" + "="*80)
print("PRIMEROS 5 ESCENARIOS - COMPARACIÓN DETALLADA")
print("="*80)

for i in range(min(5, len(df_2021))):
    esc_2021 = df_2021.iloc[i]
    esc_swing = df_swing.iloc[i]
    
    print(f"\n[{i+1}] {esc_2021['escanos_totales']} escaños | {esc_2021['config_mr_rp']} | {'CON' if esc_2021['usa_coaliciones'] else 'SIN'} coalición")
    print(f"    2021:       MORENA={esc_2021['morena_escanos']:3d} ({esc_2021['morena_pct']:5.2f}%) | Coalición={esc_2021['coalicion_escanos']:3d}")
    print(f"    2021_SWING: MORENA={esc_swing['morena_escanos']:3d} ({esc_swing['morena_pct']:5.2f}%) | Coalición={esc_swing['coalicion_escanos']:3d}")
    
    diff_morena = esc_swing['morena_escanos'] - esc_2021['morena_escanos']
    diff_coal = esc_swing['coalicion_escanos'] - esc_2021['coalicion_escanos']
    
    if diff_morena == 0 and diff_coal == 0:
        print(f"    → ⚠️ IGUALES (sin cambio)")
    else:
        print(f"    → ✓ DIFERENCIA: MORENA {diff_morena:+d}, Coalición {diff_coal:+d}")

# Verificar cuántos escenarios son diferentes
diferentes = 0
for i in range(len(df_2021)):
    if df_2021.iloc[i]['morena_escanos'] != df_swing.iloc[i]['morena_escanos']:
        diferentes += 1

print("\n" + "="*80)
print(f"RESUMEN: {diferentes}/{len(df_2021)} escenarios son DIFERENTES")
if diferentes == 0:
    print("⚠️ PROBLEMA: TODOS los escenarios 2021_SWING son IGUALES a 2021")
    print("   El swing NO se está aplicando correctamente")
else:
    print(f"✓ OK: El swing está afectando {diferentes/len(df_2021)*100:.1f}% de los escenarios")
print("="*80)
