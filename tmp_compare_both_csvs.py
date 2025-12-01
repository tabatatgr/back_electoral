"""
Comparar 2021 vs 2021_SWING en ambos CSVs
"""
import pandas as pd

def comparar_csv(csv_path, nombre):
    print(f"\n{'='*80}")
    print(f"ANALIZANDO: {nombre}")
    print(f"{'='*80}")
    
    df = pd.read_csv(csv_path)
    
    print(f"Total escenarios: {len(df)}")
    print(f"Años únicos: {sorted(df['anio'].unique())}")
    
    # Filtrar 2021 y 2021_SWING
    df_2021 = df[df['anio'] == '2021'].copy()
    df_2021_swing = df[df['anio'] == '2021_SWING'].copy()
    
    print(f"Escenarios 2021: {len(df_2021)}")
    print(f"Escenarios 2021_SWING: {len(df_2021_swing)}")
    
    if len(df_2021) == 0 or len(df_2021_swing) == 0:
        print("\n[ERROR] No se encontraron escenarios 2021 o 2021_SWING")
        return
    
    # Detectar nombres de columnas
    if 'morena_votos_pct' in df.columns:
        col_votos = 'morena_votos_pct'
    elif 'morena_pct' in df.columns:
        col_votos = 'morena_pct'
    else:
        print("[ERROR] No se encontró columna de votos MORENA")
        return
    
    # Comparar todas las filas
    comparaciones = []
    for idx in range(len(df_2021)):
        r1 = df_2021.iloc[idx]
        r2 = df_2021_swing.iloc[idx]
        
        diff_escanos = r2['morena_total'] - r1['morena_total']
        diff_votos = r2[col_votos] - r1[col_votos]
        
        comparaciones.append({
            'idx': idx,
            '2021_morena': r1['morena_total'],
            '2021_swing_morena': r2['morena_total'],
            'diff_escanos': diff_escanos,
            '2021_votos': r1[col_votos],
            '2021_swing_votos': r2[col_votos],
            'diff_votos': diff_votos
        })
    
    df_comp = pd.DataFrame(comparaciones)
    
    # ¿Hay alguna diferencia?
    tiene_diferencias = (df_comp['diff_escanos'] != 0).any() or (df_comp['diff_votos'].abs() > 0.01).any()
    
    print(f"\n{'='*80}")
    if tiene_diferencias:
        print(f"✓ SÍ HAY DIFERENCIAS entre 2021 y 2021_SWING")
        print(f"{'='*80}")
        print(f"\nEscenarios con diferencias en escaños: {(df_comp['diff_escanos'] != 0).sum()}/{len(df_comp)}")
        print(f"Escenarios con diferencias en votos: {(df_comp['diff_votos'].abs() > 0.01).sum()}/{len(df_comp)}")
        
        print("\nEjemplos de diferencias (primeros 5):")
        print(df_comp[df_comp['diff_escanos'] != 0].head(5).to_string())
    else:
        print(f"✗ NO HAY DIFERENCIAS - 2021 y 2021_SWING son IDÉNTICOS")
        print(f"{'='*80}")
        print("\n[PROBLEMA] El swing NO se está aplicando correctamente!")
        print("\nPrimeras 5 comparaciones:")
        print(df_comp.head().to_string())

# Analizar CON TOPES
comparar_csv('outputs/escenarios_morena_CON_TOPES_20251028_143319.csv', 'CON TOPES')

# Analizar SIN TOPES  
comparar_csv('outputs/escenarios_morena_SIN_TOPES_20251028_143521.csv', 'SIN TOPES')
