"""
Calcula totales por coalición y estadísticas de votos
a partir de la tabla comparativa 2021 vs 2024
"""
import pandas as pd
import numpy as np

# Leer la tabla más reciente
import os
import glob

# Buscar el archivo más reciente
pattern = 'outputs/comparativa_2021_vs_2024_CORREGIDO_*.csv'
files = glob.glob(pattern)
if not files:
    print("❌ No se encontró ningún archivo de comparativa")
    exit(1)

latest_file = max(files, key=os.path.getctime)
print(f"📁 Leyendo: {latest_file}\n")

df = pd.read_csv(latest_file)

# Definir coaliciones
coalicion_morena = ['MORENA', 'PT', 'PVEM']
coalicion_pan = ['PAN', 'PRI', 'PRD']

print("="*80)
print("ANÁLISIS POR COALICIONES - 2021 vs 2024")
print("="*80)
print()

# Calcular para cada escenario
escenarios = df['Escenario'].unique()

for escenario in escenarios:
    print(f"\n{'='*80}")
    print(f"📊 Escenario: {escenario}")
    print(f"{'='*80}\n")
    
    for anio in [2021, 2024]:
        df_filtrado = df[(df['Escenario'] == escenario) & (df['Año'] == anio)]
        
        # Coalición MORENA
        morena_coal = df_filtrado[df_filtrado['Partido'].isin(coalicion_morena)]
        morena_mr = morena_coal['MR'].sum()
        morena_pm = morena_coal['PM'].sum()
        morena_rp = morena_coal['RP'].sum()
        morena_total = morena_coal['Total'].sum()
        morena_votos = morena_coal['Votos_%'].sum()
        
        # Coalición PAN
        pan_coal = df_filtrado[df_filtrado['Partido'].isin(coalicion_pan)]
        pan_mr = pan_coal['MR'].sum()
        pan_pm = pan_coal['PM'].sum()
        pan_rp = pan_coal['RP'].sum()
        pan_total = pan_coal['Total'].sum()
        pan_votos = pan_coal['Votos_%'].sum()
        
        # MC (independiente)
        mc = df_filtrado[df_filtrado['Partido'] == 'MC']
        mc_total = mc['Total'].sum() if not mc.empty else 0
        mc_votos = mc['Votos_%'].sum() if not mc.empty else 0
        
        print(f"  Año {anio}:")
        print(f"  {'-'*76}")
        print(f"  {'Coalición':<25} {'Votos %':>10} {'MR':>6} {'PM':>6} {'RP':>6} {'Total':>8}")
        print(f"  {'-'*76}")
        print(f"  {'MORENA + PT + PVEM':<25} {morena_votos:>9.2f}% {morena_mr:>6} {morena_pm:>6} {morena_rp:>6} {morena_total:>8}")
        print(f"  {'PAN + PRI + PRD':<25} {pan_votos:>9.2f}% {pan_mr:>6} {pan_pm:>6} {pan_rp:>6} {pan_total:>8}")
        print(f"  {'MC (independiente)':<25} {mc_votos:>9.2f}% {'-':>6} {'-':>6} {'-':>6} {mc_total:>8}")
        print(f"  {'-'*76}")
        print(f"  {'Diferencia (MORENA - PAN)':<25} {morena_votos-pan_votos:>9.2f}% {morena_mr-pan_mr:>6} {morena_pm-pan_pm:>6} {morena_rp-pan_rp:>6} {morena_total-pan_total:>8}")
        print()

print("\n" + "="*80)
print("📈 ESTADÍSTICAS DE VOTOS POR COALICIÓN (2021-2024)")
print("="*80)
print()

# Calcular estadísticas de votos agregados
for escenario in escenarios:
    df_esc = df[df['Escenario'] == escenario]
    
    # MORENA coalición
    morena_2021 = df_esc[(df_esc['Año'] == 2021) & (df_esc['Partido'].isin(coalicion_morena))]['Votos_%'].sum()
    morena_2024 = df_esc[(df_esc['Año'] == 2024) & (df_esc['Partido'].isin(coalicion_morena))]['Votos_%'].sum()
    
    # PAN coalición
    pan_2021 = df_esc[(df_esc['Año'] == 2021) & (df_esc['Partido'].isin(coalicion_pan))]['Votos_%'].sum()
    pan_2024 = df_esc[(df_esc['Año'] == 2024) & (df_esc['Partido'].isin(coalicion_pan))]['Votos_%'].sum()
    
    # MC
    mc_2021 = df_esc[(df_esc['Año'] == 2021) & (df_esc['Partido'] == 'MC')]['Votos_%'].sum()
    mc_2024 = df_esc[(df_esc['Año'] == 2024) & (df_esc['Partido'] == 'MC')]['Votos_%'].sum()
    
    print(f"\n{escenario}:")
    print(f"  {'Coalición':<25} {'2021':>10} {'2024':>10} {'Promedio':>10} {'Rango':>15} {'Cambio':>10}")
    print(f"  {'-'*85}")
    
    # MORENA
    morena_prom = (morena_2021 + morena_2024) / 2
    morena_rango = f"{min(morena_2021, morena_2024):.2f}%-{max(morena_2021, morena_2024):.2f}%"
    morena_cambio = morena_2024 - morena_2021
    print(f"  {'MORENA + PT + PVEM':<25} {morena_2021:>9.2f}% {morena_2024:>9.2f}% {morena_prom:>9.2f}% {morena_rango:>15} {morena_cambio:>+9.2f}%")
    
    # PAN
    pan_prom = (pan_2021 + pan_2024) / 2
    pan_rango = f"{min(pan_2021, pan_2024):.2f}%-{max(pan_2021, pan_2024):.2f}%"
    pan_cambio = pan_2024 - pan_2021
    print(f"  {'PAN + PRI + PRD':<25} {pan_2021:>9.2f}% {pan_2024:>9.2f}% {pan_prom:>9.2f}% {pan_rango:>15} {pan_cambio:>+9.2f}%")
    
    # MC
    mc_prom = (mc_2021 + mc_2024) / 2
    mc_rango = f"{min(mc_2021, mc_2024):.2f}%-{max(mc_2021, mc_2024):.2f}%"
    mc_cambio = mc_2024 - mc_2021
    print(f"  {'MC':<25} {mc_2021:>9.2f}% {mc_2024:>9.2f}% {mc_prom:>9.2f}% {mc_rango:>15} {mc_cambio:>+9.2f}%")

# Resumen consolidado (promedio de todos los escenarios)
print("\n" + "="*80)
print("📊 RESUMEN CONSOLIDADO (Promedio de todos los escenarios)")
print("="*80)
print()

# Calcular promedios globales
morena_votos_2021 = []
morena_votos_2024 = []
pan_votos_2021 = []
pan_votos_2024 = []

for escenario in escenarios:
    df_esc = df[df['Escenario'] == escenario]
    
    morena_votos_2021.append(df_esc[(df_esc['Año'] == 2021) & (df_esc['Partido'].isin(coalicion_morena))]['Votos_%'].sum())
    morena_votos_2024.append(df_esc[(df_esc['Año'] == 2024) & (df_esc['Partido'].isin(coalicion_morena))]['Votos_%'].sum())
    pan_votos_2021.append(df_esc[(df_esc['Año'] == 2021) & (df_esc['Partido'].isin(coalicion_pan))]['Votos_%'].sum())
    pan_votos_2024.append(df_esc[(df_esc['Año'] == 2024) & (df_esc['Partido'].isin(coalicion_pan))]['Votos_%'].sum())

print(f"{'Coalición':<25} {'Promedio 2021':>15} {'Promedio 2024':>15} {'Cambio':>12}")
print(f"{'-'*70}")

# MORENA
morena_avg_2021 = np.mean(morena_votos_2021)
morena_avg_2024 = np.mean(morena_votos_2024)
morena_avg_cambio = morena_avg_2024 - morena_avg_2021
print(f"{'MORENA + PT + PVEM':<25} {morena_avg_2021:>14.2f}% {morena_avg_2024:>14.2f}% {morena_avg_cambio:>+11.2f}%")

# PAN
pan_avg_2021 = np.mean(pan_votos_2021)
pan_avg_2024 = np.mean(pan_votos_2024)
pan_avg_cambio = pan_avg_2024 - pan_avg_2021
print(f"{'PAN + PRI + PRD':<25} {pan_avg_2021:>14.2f}% {pan_avg_2024:>14.2f}% {pan_avg_cambio:>+11.2f}%")

print()
print("="*80)
print("✅ Análisis completado")
print("="*80)
