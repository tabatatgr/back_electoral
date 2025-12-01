"""
Recálculo de Swing Electoral con Coaliciones
Versión mejorada que maneja correctamente coaliciones en elecciones locales
"""

import pandas as pd
import numpy as np
import glob
import os
from datetime import datetime

# Configuración
SWING_ORIGINAL = "outputs/swing/swings_por_df_20251022_142907.csv"
VOTOS_LOCALES_DIR = "estados_swing"
OUTPUT_DIR = "outputs/swing"

# Mapeo de coaliciones comunes
COALICIONES = {
    'PVEM_PT_MORENA': ['PVEM', 'PT', 'MORENA'],
    'PAN_PRI_PRD': ['PAN', 'PRI', 'PRD'],
    'PAN_PRI_PRD_NAEM': ['PAN', 'PRI', 'PRD'],  # NAEM = Nueva Alianza Estado de México
    'PT_MORENA': ['PT', 'MORENA'],
    'MORENA_PT': ['PT', 'MORENA'],
}

def detectar_coaliciones_en_csv(csv_path):
    """Detecta qué coaliciones existen en un CSV"""
    try:
        df = pd.read_csv(csv_path, nrows=1)
        df.columns = [c.upper().strip() for c in df.columns]
        
        coaliciones_encontradas = {}
        for col in df.columns:
            if col in COALICIONES:
                coaliciones_encontradas[col] = COALICIONES[col]
        
        return coaliciones_encontradas, df.columns.tolist()
    except Exception as e:
        print(f"  [ERROR] {csv_path}: {e}")
        return {}, []

def analizar_estructura_votos_locales():
    """Analiza la estructura de todos los CSVs de votos locales"""
    print("=" * 80)
    print("ANÁLISIS DE ESTRUCTURA DE VOTOS LOCALES")
    print("=" * 80)
    
    archivos_csv = glob.glob(f"{VOTOS_LOCALES_DIR}/*_SEE_GOB_*_SEC.csv")
    
    resultado = {}
    
    for archivo in sorted(archivos_csv):
        estado = os.path.basename(archivo).split('_')[3]
        anio = os.path.basename(archivo).split('_')[0]
        
        coaliciones, columnas = detectar_coaliciones_en_csv(archivo)
        
        # Detectar partidos individuales
        partidos_ind = []
        for partido in ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA']:
            if partido in columnas:
                partidos_ind.append(partido)
        
        resultado[estado] = {
            'archivo': archivo,
            'anio': anio,
            'coaliciones': coaliciones,
            'partidos_individuales': partidos_ind
        }
        
        print(f"\n{estado} ({anio}):")
        print(f"  Partidos individuales: {', '.join(partidos_ind) if partidos_ind else 'NINGUNO'}")
        if coaliciones:
            print(f"  Coaliciones:")
            for coal, partes in coaliciones.items():
                print(f"    - {coal} ({'+'.join(partes)})")
    
    return resultado

def recalcular_swing_coaliciones(estructura):
    """Recalcula swing considerando coaliciones"""
    print("\n" + "=" * 80)
    print("RECÁLCULO DE SWING CON COALICIONES")
    print("=" * 80)
    
    # Cargar swing original
    swing_df = pd.read_csv(SWING_ORIGINAL)
    
    # Agregar columnas de coaliciones
    swing_df['swing_JUNTOS_PT_MORENA'] = np.nan
    swing_df['swing_VA_X_MEX_PAN_PRI_PRD'] = np.nan
    
    # Calcular para cada distrito
    for idx, row in swing_df.iterrows():
        estado = row['NOMBRE_ESTADO']
        
        # Juntos Hacemos Historia (PT + MORENA)
        if row['PT_fed_2021'] > 0 and row['MORENA_fed_2021'] > 0:
            fed_juntos = row['PT_fed_2021'] + row['MORENA_fed_2021']
            local_juntos = row['PT_local'] + row['MORENA_local']
            
            if fed_juntos > 0 and local_juntos > 0:
                swing_df.at[idx, 'swing_JUNTOS_PT_MORENA'] = (local_juntos / fed_juntos - 1) * 100
        
        # Va por México (PAN + PRI + PRD)
        if row['PAN_fed_2021'] > 0 and row['PRI_fed_2021'] > 0 and row['PRD_fed_2021'] > 0:
            fed_vxm = row['PAN_fed_2021'] + row['PRI_fed_2021'] + row['PRD_fed_2021']
            local_vxm = row['PAN_local'] + row['PRI_local'] + row['PRD_local']
            
            if fed_vxm > 0 and local_vxm > 0:
                swing_df.at[idx, 'swing_VA_X_MEX_PAN_PRI_PRD'] = (local_vxm / fed_vxm - 1) * 100
    
    return swing_df

def generar_reporte_coaliciones(swing_df):
    """Genera reporte comparando swing individual vs coalición"""
    print("\n" + "=" * 80)
    print("COMPARACIÓN: SWING INDIVIDUAL vs COALICIÓN")
    print("=" * 80)
    
    estados = swing_df['NOMBRE_ESTADO'].unique()
    
    for estado in sorted(estados):
        df_estado = swing_df[swing_df['NOMBRE_ESTADO'] == estado]
        
        # Swing individual promedio
        swing_pt_ind = df_estado[df_estado['swing_PT'] > -99]['swing_PT'].mean()
        swing_morena_ind = df_estado[df_estado['swing_MORENA'] > -99]['swing_MORENA'].mean()
        
        # Swing coalición
        swing_juntos = df_estado[df_estado['swing_JUNTOS_PT_MORENA'].notna()]['swing_JUNTOS_PT_MORENA'].mean()
        
        if not pd.isna(swing_juntos):
            print(f"\n{estado}:")
            if not pd.isna(swing_pt_ind):
                print(f"  PT individual:        {swing_pt_ind:+7.1f}%")
            if not pd.isna(swing_morena_ind):
                print(f"  MORENA individual:    {swing_morena_ind:+7.1f}%")
            print(f"  PT+MORENA coalición:  {swing_juntos:+7.1f}%")
            
            # Calcular desviación
            if not pd.isna(swing_pt_ind) and not pd.isna(swing_morena_ind):
                prom_ind = (swing_pt_ind + swing_morena_ind) / 2
                diferencia = abs(swing_juntos - prom_ind)
                if diferencia > 50:
                    print(f"  [!] Diferencia: {diferencia:.1f}pp - USAR COALICIÓN")

def analizar_coahuila_corregido(swing_df):
    """Analiza Coahuila con swing de coalición"""
    print("\n" + "=" * 80)
    print("COAHUILA: ANÁLISIS CON COALICIÓN PT+MORENA")
    print("=" * 80)
    
    coah = swing_df[swing_df['NOMBRE_ESTADO'] == 'Coahuila'][
        ['DF_2021', 'swing_PT', 'swing_MORENA', 'swing_JUNTOS_PT_MORENA']
    ].copy()
    
    print("\nComparación por distrito:")
    print(coah.to_string(index=False))
    
    print("\n[OK] CORRECCIÓN:")
    print(f"  Swing PT individual:        {coah['swing_PT'].mean():+7.1f}% (INCORRECTO - rotación)")
    print(f"  Swing MORENA individual:    {coah['swing_MORENA'].mean():+7.1f}% (INCORRECTO - rotación)")
    print(f"  Swing PT+MORENA coalición:  {coah['swing_JUNTOS_PT_MORENA'].mean():+7.1f}% (CORRECTO)")
    
    print("\nRECOMENDACIÓN:")
    print("  Para Coahuila, usar swing de COALICIÓN PT+MORENA")
    print("  Ignorar swing individual de PT y MORENA")

def exportar_swing_corregido(swing_df):
    """Exporta swing corregido con coaliciones"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Seleccionar columnas relevantes
    columnas_exportar = [
        'NOMBRE_ESTADO', 'ENTIDAD', 'DF_2021', 'AÑO_ELECCION',
        'swing_PAN', 'swing_PRI', 'swing_PRD',
        'swing_PVEM', 'swing_PT', 'swing_MC', 'swing_MORENA',
        'swing_VA_X_MEX_PAN_PRI_PRD', 'swing_JUNTOS_PT_MORENA'
    ]
    
    swing_export = swing_df[columnas_exportar].copy()
    
    # Exportar
    output_file = f"{OUTPUT_DIR}/swing_con_coaliciones_{timestamp}.csv"
    swing_export.to_csv(output_file, index=False)
    print(f"\n[OK] Swing corregido exportado: {output_file}")
    
    # Resumen por estado
    resumen_rows = []
    for estado in sorted(swing_df['NOMBRE_ESTADO'].unique()):
        df_estado = swing_df[swing_df['NOMBRE_ESTADO'] == estado]
        
        row = {
            'ESTADO': estado,
            'DISTRITOS': len(df_estado),
            'swing_PAN_prom': df_estado[df_estado['swing_PAN'] > -99]['swing_PAN'].mean(),
            'swing_PRI_prom': df_estado[df_estado['swing_PRI'] > -99]['swing_PRI'].mean(),
            'swing_PRD_prom': df_estado[df_estado['swing_PRD'] > -99]['swing_PRD'].mean(),
            'swing_VxM_prom': df_estado['swing_VA_X_MEX_PAN_PRI_PRD'].mean(),
            'swing_JUNTOS_prom': df_estado['swing_JUNTOS_PT_MORENA'].mean(),
        }
        resumen_rows.append(row)
    
    resumen_df = pd.DataFrame(resumen_rows)
    output_resumen = f"{OUTPUT_DIR}/swing_coaliciones_resumen_{timestamp}.csv"
    resumen_df.to_csv(output_resumen, index=False)
    print(f"[OK] Resumen por estado: {output_resumen}")
    
    return swing_export, resumen_df

def generar_recomendaciones_finales(estructura, swing_df):
    """Genera recomendaciones finales de uso"""
    print("\n" + "=" * 80)
    print("RECOMENDACIONES FINALES")
    print("=" * 80)
    
    print("\n1. POR ESTADO:")
    
    for estado_key, info in estructura.items():
        estado_nombre = {
            'AGS': 'Aguascalientes',
            'COAH': 'Coahuila',
            'DGO': 'Durango',
            'HGO': 'Hidalgo',
            'MEX': 'México',
            'OAX': 'Oaxaca',
            'QROO': 'Quintana Roo',
            'TAMPS': 'Tamaulipas'
        }.get(estado_key, estado_key)
        
        print(f"\n  {estado_nombre}:")
        
        if 'PVEM_PT_MORENA' in info['coaliciones']:
            print(f"    [!] Coalición PVEM+PT+MORENA en local")
            print(f"    -> NO usar swing individual de PVEM, PT, MORENA")
            print(f"    -> USAR swing de coalición completa")
        elif len(info['partidos_individuales']) >= 5:
            print(f"    [OK] Partidos individuales: {', '.join(info['partidos_individuales'])}")
            print(f"    -> USAR swing individual con cautela")
            print(f"    -> Considerar coalición PT+MORENA para estabilidad")
        else:
            print(f"    [!] Estructura mixta")
            print(f"    -> Revisar caso por caso")
    
    print("\n2. POR COALICIÓN:")
    print("\n  JUNTOS HACEMOS HISTORIA (PT+MORENA):")
    swing_juntos_prom = swing_df['swing_JUNTOS_PT_MORENA'].mean()
    print(f"    Swing promedio: {swing_juntos_prom:+.1f}%")
    print(f"    Recomendación: USAR en lugar de PT/MORENA individual")
    print(f"    Razón: Evita distorsiones por rotación de candidatos")
    
    print("\n  VA POR MÉXICO (PAN+PRI+PRD):")
    swing_vxm_prom = swing_df['swing_VA_X_MEX_PAN_PRI_PRD'].mean()
    print(f"    Swing promedio: {swing_vxm_prom:+.1f}%")
    print(f"    Recomendación: Opcional (partidos tienen swing individual confiable)")
    print(f"    Usar si quieres modelar coalición completa")
    
    print("\n3. IMPLEMENTACIÓN EN MODELO:")
    print("""
    # Pseudocódigo
    if estado == 'Coahuila':
        votos_juntos_ajustados = (votos_PT + votos_MORENA) * (1 + swing_JUNTOS/100)
        distribuir proporcionalmente entre PT y MORENA
    
    elif estado == 'México':
        # No aplicar swing individual (datos faltantes)
        usar_promedio_nacional o mantener_votos_2021
    
    else:
        # Usar swing individual con factor de confianza
        votos_ajustados = votos_2021 * (1 + swing_individual/100)
    """)

def main():
    """Función principal"""
    try:
        print("=" * 80)
        print("ANÁLISIS DE COALICIONES EN SWING ELECTORAL")
        print("=" * 80)
        
        # 1. Analizar estructura de CSVs
        estructura = analizar_estructura_votos_locales()
        
        # 2. Recalcular swing con coaliciones
        swing_corregido = recalcular_swing_coaliciones(estructura)
        
        # 3. Comparar individual vs coalición
        generar_reporte_coaliciones(swing_corregido)
        
        # 4. Análisis específico de Coahuila
        analizar_coahuila_corregido(swing_corregido)
        
        # 5. Exportar resultados
        swing_export, resumen_df = exportar_swing_corregido(swing_corregido)
        
        # 6. Recomendaciones finales
        generar_recomendaciones_finales(estructura, swing_corregido)
        
        print("\n" + "=" * 80)
        print("[OK] Análisis completado")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


