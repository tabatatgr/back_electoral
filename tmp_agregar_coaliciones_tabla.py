"""
Agrega totales de coaliciones a la tabla comparativa
- Coalición MORENA: MORENA + PT + PVEM
- Coalición PAN: PAN + PRI + PRD
"""
import pandas as pd
from datetime import datetime

# Leer la tabla más reciente
df = pd.read_csv('outputs/comparativa_2021_vs_2024_CORREGIDO_20260105_160842.csv')

print("="*80)
print("AGREGANDO COALICIONES A LA TABLA")
print("="*80)

# Definir coaliciones
coalicion_morena = ['MORENA', 'PT', 'PVEM']
coalicion_pan = ['PAN', 'PRI', 'PRD']

# Crear filas para coaliciones
filas_coaliciones = []

for anio in df['Año'].unique():
    for escenario in df['Escenario'].unique():
        # Filtrar datos para este año y escenario
        subset = df[(df['Año'] == anio) & (df['Escenario'] == escenario)]
        
        # COALICIÓN MORENA
        morena_partidos = subset[subset['Partido'].isin(coalicion_morena)]
        if len(morena_partidos) > 0:
            coalicion_morena_row = {
                'Año': anio,
                'Escenario': escenario,
                'Partido': 'COALICIÓN_MORENA',
                'Votos_%': morena_partidos['Votos_%'].sum(),
                'MR': morena_partidos['MR'].sum(),
                'PM': morena_partidos['PM'].sum(),
                'RP': morena_partidos['RP'].sum(),
                'Total': morena_partidos['Total'].sum()
            }
            
            # Agregar columnas de diferencias si existen
            for col in df.columns:
                if col.startswith('Diff_'):
                    coalicion_morena_row[col] = morena_partidos[col].iloc[0] if col in morena_partidos.columns else 0
            
            filas_coaliciones.append(coalicion_morena_row)
        
        # COALICIÓN PAN
        pan_partidos = subset[subset['Partido'].isin(coalicion_pan)]
        if len(pan_partidos) > 0:
            coalicion_pan_row = {
                'Año': anio,
                'Escenario': escenario,
                'Partido': 'COALICIÓN_PAN',
                'Votos_%': pan_partidos['Votos_%'].sum(),
                'MR': pan_partidos['MR'].sum(),
                'PM': pan_partidos['PM'].sum(),
                'RP': pan_partidos['RP'].sum(),
                'Total': pan_partidos['Total'].sum()
            }
            
            # Agregar columnas de diferencias si existen
            for col in df.columns:
                if col.startswith('Diff_'):
                    coalicion_pan_row[col] = pan_partidos[col].iloc[0] if col in pan_partidos.columns else 0
            
            filas_coaliciones.append(coalicion_pan_row)

# Crear DataFrame con coaliciones
df_coaliciones = pd.DataFrame(filas_coaliciones)

# Combinar con la tabla original
df_completo = pd.concat([df, df_coaliciones], ignore_index=True)

# Ordenar por Año, Escenario, y Partido
orden_partidos = ['PAN', 'PRI', 'PRD', 'COALICIÓN_PAN', 'PVEM', 'PT', 'MC', 'MORENA', 'COALICIÓN_MORENA', 'PES', 'RSP', 'FXM']
df_completo['Partido_orden'] = df_completo['Partido'].apply(
    lambda x: orden_partidos.index(x) if x in orden_partidos else 999
)
df_completo = df_completo.sort_values(['Año', 'Escenario', 'Partido_orden'])
df_completo = df_completo.drop('Partido_orden', axis=1)

# Guardar tabla completa
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_file = f'outputs/comparativa_2021_vs_2024_CON_COALICIONES_{timestamp}.csv'
df_completo.to_csv(output_file, index=False)

print(f"\n✓ Tabla con coaliciones guardada: {output_file}")
print(f"  Total filas: {len(df_completo)}")

# Mostrar resumen de coaliciones
print("\n" + "="*80)
print("RESUMEN COALICIONES")
print("="*80)

for anio in sorted(df_completo['Año'].unique()):
    print(f"\n{'='*80}")
    print(f"AÑO {anio}")
    print(f"{'='*80}")
    
    for escenario in df_completo['Escenario'].unique():
        print(f"\n{escenario}:")
        print("-" * 60)
        
        subset = df_completo[(df_completo['Año'] == anio) & (df_completo['Escenario'] == escenario)]
        
        # Mostrar coaliciones
        for coalicion in ['COALICIÓN_MORENA', 'COALICIÓN_PAN']:
            coal_data = subset[subset['Partido'] == coalicion]
            if len(coal_data) > 0:
                row = coal_data.iloc[0]
                print(f"  {coalicion:<20} Votos: {row['Votos_%']:>6.2f}%  MR: {row['MR']:>3}  PM: {row['PM']:>3}  RP: {row['RP']:>3}  Total: {row['Total']:>3}")

# Calcular diferencias entre coaliciones 2024 - 2021
print("\n" + "="*80)
print("DIFERENCIAS 2024 vs 2021 (POR COALICIÓN)")
print("="*80)

for escenario in df_completo['Escenario'].unique():
    print(f"\n{escenario}:")
    print("-" * 60)
    
    for coalicion in ['COALICIÓN_MORENA', 'COALICIÓN_PAN']:
        coal_2021 = df_completo[(df_completo['Año'] == 2021) & 
                                (df_completo['Escenario'] == escenario) & 
                                (df_completo['Partido'] == coalicion)]
        coal_2024 = df_completo[(df_completo['Año'] == 2024) & 
                                (df_completo['Escenario'] == escenario) & 
                                (df_completo['Partido'] == coalicion)]
        
        if len(coal_2021) > 0 and len(coal_2024) > 0:
            r2021 = coal_2021.iloc[0]
            r2024 = coal_2024.iloc[0]
            
            diff_votos = r2024['Votos_%'] - r2021['Votos_%']
            diff_mr = r2024['MR'] - r2021['MR']
            diff_pm = r2024['PM'] - r2021['PM']
            diff_rp = r2024['RP'] - r2021['RP']
            diff_total = r2024['Total'] - r2021['Total']
            
            signo_votos = '+' if diff_votos >= 0 else ''
            signo_mr = '+' if diff_mr >= 0 else ''
            signo_pm = '+' if diff_pm >= 0 else ''
            signo_rp = '+' if diff_rp >= 0 else ''
            signo_total = '+' if diff_total >= 0 else ''
            
            print(f"  {coalicion:<20} Votos: {signo_votos}{diff_votos:>6.2f}%  MR: {signo_mr}{diff_mr:>3}  PM: {signo_pm}{diff_pm:>3}  RP: {signo_rp}{diff_rp:>3}  Total: {signo_total}{diff_total:>3}")

print("\n✓ Análisis completado")
