"""
Comparar 2021 vs 2021_SWING en el CSV CON TOPES
"""
import pandas as pd

# Leer CSV
csv_path = 'outputs/escenarios_morena_SIN_TOPES_20251028_143521.csv'
df = pd.read_csv(csv_path)

print(f"Total escenarios: {len(df)}")
print(f"\nAños únicos: {sorted(df['anio'].unique())}")

# Filtrar 2021 y 2021_SWING
df_2021 = df[df['anio'] == '2021'].copy()
df_2021_swing = df[df['anio'] == '2021_SWING'].copy()

print(f"\nEscenarios 2021: {len(df_2021)}")
print(f"Escenarios 2021_SWING: {len(df_2021_swing)}")

if len(df_2021) == 0 or len(df_2021_swing) == 0:
    print("\n[ERROR] No se encontraron escenarios 2021 o 2021_SWING")
else:
    # Comparar primer escenario
    print("\n" + "="*80)
    print("COMPARACIÓN 2021 vs 2021_SWING - Primer escenario")
    print("="*80)
    
    r1 = df_2021.iloc[0]
    r2 = df_2021_swing.iloc[0]
    
    print(f"\n2021:")
    print(f"  Config: {r1['total_escanos']} escaños, {r1['configuracion']}, coal={r1['usar_coaliciones']}")
    print(f"  MORENA: {r1['morena_total']} escaños ({r1['morena_votos_pct']:.2f}%)")
    print(f"  MR: {r1['morena_mr']}, RP: {r1['morena_rp']}")
    
    print(f"\n2021_SWING:")
    print(f"  Config: {r2['total_escanos']} escaños, {r2['configuracion']}, coal={r2['usar_coaliciones']}")
    print(f"  MORENA: {r2['morena_total']} escaños ({r2['morena_votos_pct']:.2f}%)")
    print(f"  MR: {r2['morena_mr']}, RP: {r2['morena_rp']}")
    
    print(f"\nDIFERENCIA:")
    print(f"  Escaños: {r2['morena_total'] - r1['morena_total']:+d}")
    print(f"  Votos %: {r2['morena_votos_pct'] - r1['morena_votos_pct']:+.2f}%")
    
    # Verificar si TODAS las filas son iguales
    print("\n" + "="*80)
    print("VERIFICANDO TODAS LAS COMPARACIONES")
    print("="*80)
    
    comparaciones = []
    for idx in range(len(df_2021)):
        r1 = df_2021.iloc[idx]
        r2 = df_2021_swing.iloc[idx]
        
        diff_escanos = r2['morena_total'] - r1['morena_total']
        diff_votos = r2['morena_votos_pct'] - r1['morena_votos_pct']
        
        comparaciones.append({
            'config': f"{r1['total_escanos']}_{r1['configuracion']}_{r1['usar_coaliciones']}",
            'diff_escanos': diff_escanos,
            'diff_votos': diff_votos,
            '2021_morena': r1['morena_total'],
            '2021_swing_morena': r2['morena_total']
        })
    
    df_comp = pd.DataFrame(comparaciones)
    
    # ¿Hay alguna diferencia?
    tiene_diferencias = (df_comp['diff_escanos'] != 0).any() or (df_comp['diff_votos'].abs() > 0.01).any()
    
    if tiene_diferencias:
        print(f"\n✓ SÍ HAY DIFERENCIAS entre 2021 y 2021_SWING")
        print(f"\nEscenarios con diferencias en escaños: {(df_comp['diff_escanos'] != 0).sum()}/{len(df_comp)}")
        print(f"Escenarios con diferencias en votos: {(df_comp['diff_votos'].abs() > 0.01).sum()}/{len(df_comp)}")
        
        print("\nEjemplos de diferencias:")
        print(df_comp[df_comp['diff_escanos'] != 0].head(5))
    else:
        print(f"\n✗ NO HAY DIFERENCIAS - 2021 y 2021_SWING son IDÉNTICOS")
        print("\nPrimeras 5 comparaciones:")
        print(df_comp.head())
        print("\n[PROBLEMA] El swing NO se está aplicando correctamente!")
