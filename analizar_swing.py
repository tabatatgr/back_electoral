"""
Análisis de Swing Electoral por Distrito Federal
Este script analiza los resultados de swing calculados entre elecciones locales y federales 2021
"""

import pandas as pd
import numpy as np
from datetime import datetime

# Configuración
SWING_FILE = "outputs/swing/swings_por_df_20251022_142907.csv"
EQUIV_FILE = "outputs/swing/tabla_equivalencia_seccion_df.csv"
OUTPUT_DIR = "outputs/swing"

def cargar_datos():
    """Carga los archivos de swing"""
    print("=" * 80)
    print("ANÁLISIS DE SWING ELECTORAL")
    print("=" * 80)
    
    swing_df = pd.read_csv(SWING_FILE)
    equiv_df = pd.read_csv(EQUIV_FILE)
    
    print(f"\n[INFO] Datos cargados:")
    print(f"  - Swing: {len(swing_df)} distritos")
    print(f"  - Equivalencias: {len(equiv_df)} secciones")
    
    return swing_df, equiv_df

def analizar_patrones(swing_df):
    """Analiza patrones generales de swing"""
    print("\n" + "=" * 80)
    print("1. PATRONES GENERALES")
    print("=" * 80)
    
    partidos = ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA']
    columnas_swing = [f'swing_{p}' for p in partidos]
    
    # Estadísticas por partido (global)
    print("\nSWING PROMEDIO NACIONAL (83 distritos):")
    for partido in partidos:
        col = f'swing_{partido}'
        # Filtrar valores -100 (falta de datos)
        datos_validos = swing_df[swing_df[col] > -99][col]
        if len(datos_validos) > 0:
            promedio = datos_validos.mean()
            mediana = datos_validos.median()
            std = datos_validos.std()
            distritos = len(datos_validos)
            print(f"  {partido:8s}: {promedio:+7.2f}% (mediana: {mediana:+7.2f}%, std: {std:6.2f}%, n={distritos})")
    
    # Distritos con datos incompletos
    print("\nDISTRITOS CON DATOS FALTANTES (-100%):")
    for partido in partidos:
        col = f'swing_{partido}'
        faltantes = swing_df[swing_df[col] <= -99]
        if len(faltantes) > 0:
            print(f"  {partido}: {len(faltantes)} distritos")
            estados_afectados = faltantes['NOMBRE_ESTADO'].value_counts()
            for estado, count in estados_afectados.items():
                print(f"    - {estado}: {count}")

def analizar_por_estado(swing_df):
    """Analiza swing por estado"""
    print("\n" + "=" * 80)
    print("2. ANÁLISIS POR ESTADO")
    print("=" * 80)
    
    estados = swing_df['NOMBRE_ESTADO'].unique()
    partidos = ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA']
    
    for estado in sorted(estados):
        df_estado = swing_df[swing_df['NOMBRE_ESTADO'] == estado]
        anio = df_estado['AÑO_ELECCION'].iloc[0]
        
        print(f"\n{estado.upper()} ({anio}):")
        print(f"  Distritos federales: {len(df_estado)}")
        
        # Swing por partido
        print("  Swing promedio por partido:")
        for partido in partidos:
            col = f'swing_{partido}'
            datos_validos = df_estado[df_estado[col] > -99][col]
            if len(datos_validos) > 0:
                promedio = datos_validos.mean()
                min_val = datos_validos.min()
                max_val = datos_validos.max()
                print(f"    {partido:8s}: {promedio:+7.2f}% (rango: {min_val:+7.2f}% a {max_val:+7.2f}%)")

def identificar_competitivos(swing_df):
    """Identifica distritos más competitivos"""
    print("\n" + "=" * 80)
    print("3. DISTRITOS COMPETITIVOS (Mayor variabilidad)")
    print("=" * 80)
    
    partidos = ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA']
    columnas_swing = [f'swing_{p}' for p in partidos]
    
    # Calcular desviación estándar del swing por distrito
    swing_df['swing_std'] = swing_df[columnas_swing].std(axis=1)
    
    # Top 10 más variables
    top_competitivos = swing_df.nlargest(10, 'swing_std')[
        ['NOMBRE_ESTADO', 'ENTIDAD', 'DF_2021', 'swing_std'] + columnas_swing
    ]
    
    print("\nTop 10 distritos con mayor variabilidad de swing:")
    for idx, row in top_competitivos.iterrows():
        print(f"\n  {row['NOMBRE_ESTADO']} - DF {int(row['DF_2021'])} (std: {row['swing_std']:.2f})")
        for partido in partidos:
            swing_val = row[f'swing_{partido}']
            if swing_val > -99:
                print(f"    {partido}: {swing_val:+7.2f}%")

def identificar_cambios_dramaticos(swing_df):
    """Identifica cambios drásticos por partido"""
    print("\n" + "=" * 80)
    print("4. CAMBIOS MÁS DRÁSTICOS")
    print("=" * 80)
    
    partidos = ['PAN', 'PRI', 'PRD', 'MC', 'MORENA']
    
    for partido in partidos:
        col = f'swing_{partido}'
        datos_validos = swing_df[swing_df[col] > -99]
        
        if len(datos_validos) == 0:
            continue
        
        print(f"\n{partido}:")
        
        # Mayor pérdida
        peor = datos_validos.nsmallest(3, col)[['NOMBRE_ESTADO', 'ENTIDAD', 'DF_2021', col]]
        print("  Mayor pérdida:")
        for idx, row in peor.iterrows():
            print(f"    {row['NOMBRE_ESTADO']} DF-{int(row['DF_2021'])}: {row[col]:+.2f}%")
        
        # Mayor ganancia
        mejor = datos_validos.nlargest(3, col)[['NOMBRE_ESTADO', 'ENTIDAD', 'DF_2021', col]]
        print("  Mayor ganancia:")
        for idx, row in mejor.iterrows():
            print(f"    {row['NOMBRE_ESTADO']} DF-{int(row['DF_2021'])}: {row[col]:+.2f}%")

def comparar_coaliciones(swing_df):
    """Compara swing de coaliciones"""
    print("\n" + "=" * 80)
    print("5. ANÁLISIS DE COALICIONES")
    print("=" * 80)
    
    # Filtrar datos válidos
    datos_validos = swing_df.copy()
    for col in ['swing_PAN', 'swing_PRI', 'swing_PRD', 'swing_PT', 'swing_MORENA']:
        datos_validos = datos_validos[datos_validos[col] > -99]
    
    if len(datos_validos) == 0:
        print("\n[WARN] No hay suficientes datos para análisis de coaliciones")
        return
    
    # Simular coaliciones (suma ponderada de swing)
    datos_validos['swing_Va_x_Mex'] = (
        datos_validos['swing_PAN'] + 
        datos_validos['swing_PRI'] + 
        datos_validos['swing_PRD']
    ) / 3
    
    datos_validos['swing_Juntos'] = (
        datos_validos['swing_PT'] + 
        datos_validos['swing_MORENA']
    ) / 2
    
    print("\nSWING PROMEDIO DE COALICIONES:")
    print(f"  Va por México (PAN+PRI+PRD): {datos_validos['swing_Va_x_Mex'].mean():+.2f}%")
    print(f"  Juntos (PT+MORENA):          {datos_validos['swing_Juntos'].mean():+.2f}%")
    
    # Estados con mejor desempeño para cada coalición
    print("\nMEJORES ESTADOS POR COALICIÓN:")
    
    print("\n  Va por México:")
    mejores_vxm = datos_validos.groupby('NOMBRE_ESTADO')['swing_Va_x_Mex'].mean().sort_values(ascending=False).head(3)
    for estado, swing in mejores_vxm.items():
        print(f"    {estado}: {swing:+.2f}%")
    
    print("\n  Juntos (PT+MORENA):")
    mejores_juntos = datos_validos.groupby('NOMBRE_ESTADO')['swing_Juntos'].mean().sort_values(ascending=False).head(3)
    for estado, swing in mejores_juntos.items():
        print(f"    {estado}: {swing:+.2f}%")

def generar_recomendaciones(swing_df):
    """Genera recomendaciones para aplicar swing"""
    print("\n" + "=" * 80)
    print("6. RECOMENDACIONES DE USO")
    print("=" * 80)
    
    partidos = ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA']
    
    print("\nPara usar estos datos en predicciones de escaños:")
    print()
    print("1. AJUSTE DE VOTOS POR DISTRITO:")
    print("   votos_ajustados = votos_2021 * (1 + swing/100)")
    print()
    print("2. LIMITACIONES:")
    print("   - Solo 83 de 300 distritos tienen datos (27.7%)")
    print("   - 8 estados de 32 (25%)")
    print("   - Algunos partidos sin datos en ciertos estados (MC, PVEM en varios)")
    print()
    print("3. APLICACIÓN RECOMENDADA:")
    
    # Calcular confiabilidad por partido
    print("\n   Por partido (basado en cobertura de datos):")
    for partido in partidos:
        col = f'swing_{partido}'
        datos_validos = swing_df[swing_df[col] > -99]
        cobertura = len(datos_validos) / len(swing_df) * 100
        
        if cobertura >= 80:
            recomendacion = "USAR - Buena cobertura"
        elif cobertura >= 50:
            recomendacion = "USAR CON CAUTELA - Cobertura media"
        else:
            recomendacion = "NO USAR - Cobertura insuficiente"
        
        print(f"   {partido:8s}: {cobertura:5.1f}% cobertura -> {recomendacion}")
    
    print("\n4. ESTRATEGIA ALTERNATIVA:")
    print("   - Para distritos SIN datos: usar swing promedio estatal")
    print("   - Para estados SIN datos: usar swing promedio nacional")
    print("   - Aplicar factor de confianza (0.5-1.0) según cobertura")

def exportar_resumen(swing_df):
    """Exporta resumen ejecutivo"""
    print("\n" + "=" * 80)
    print("7. EXPORTANDO RESÚMENES")
    print("=" * 80)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Resumen por estado y partido
    partidos = ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA']
    resumen_rows = []
    
    for estado in sorted(swing_df['NOMBRE_ESTADO'].unique()):
        df_estado = swing_df[swing_df['NOMBRE_ESTADO'] == estado]
        row = {'ESTADO': estado, 'DISTRITOS': len(df_estado)}
        
        for partido in partidos:
            col = f'swing_{partido}'
            datos_validos = df_estado[df_estado[col] > -99][col]
            if len(datos_validos) > 0:
                row[f'{partido}_swing_prom'] = datos_validos.mean()
                row[f'{partido}_n'] = len(datos_validos)
            else:
                row[f'{partido}_swing_prom'] = np.nan
                row[f'{partido}_n'] = 0
        
        resumen_rows.append(row)
    
    resumen_df = pd.DataFrame(resumen_rows)
    output_file = f"{OUTPUT_DIR}/resumen_swing_ejecutivo_{timestamp}.csv"
    resumen_df.to_csv(output_file, index=False)
    print(f"\n[OK] Resumen ejecutivo guardado: {output_file}")
    
    # Archivo de distritos recomendados para ajuste
    distritos_recomendados = []
    for idx, row in swing_df.iterrows():
        distrito_info = {
            'ENTIDAD': row['ENTIDAD'],
            'DF': row['DF_2021'],
            'NOMBRE_ESTADO': row['NOMBRE_ESTADO'],
            'usar_swing': 'SI'
        }
        
        # Verificar si tiene datos suficientes
        partidos_validos = sum([
            1 for p in ['PAN', 'PRI', 'PRD', 'MC', 'MORENA'] 
            if row[f'swing_{p}'] > -99
        ])
        
        if partidos_validos < 3:
            distrito_info['usar_swing'] = 'NO - Datos insuficientes'
        
        distritos_recomendados.append(distrito_info)
    
    recom_df = pd.DataFrame(distritos_recomendados)
    output_recom = f"{OUTPUT_DIR}/distritos_usar_swing_{timestamp}.csv"
    recom_df.to_csv(output_recom, index=False)
    print(f"[OK] Recomendaciones por distrito: {output_recom}")
    
    # Estadísticas
    print(f"\n[INFO] De {len(recom_df)} distritos:")
    print(f"  - Recomendados para ajuste: {(recom_df['usar_swing'] == 'SI').sum()}")
    print(f"  - NO recomendados: {(recom_df['usar_swing'] != 'SI').sum()}")

def main():
    """Función principal"""
    try:
        # Cargar datos
        swing_df, equiv_df = cargar_datos()
        
        # Análisis
        analizar_patrones(swing_df)
        analizar_por_estado(swing_df)
        identificar_competitivos(swing_df)
        identificar_cambios_dramaticos(swing_df)
        comparar_coaliciones(swing_df)
        generar_recomendaciones(swing_df)
        exportar_resumen(swing_df)
        
        print("\n" + "=" * 80)
        print("[OK] Análisis completado")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
