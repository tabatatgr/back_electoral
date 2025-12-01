"""
Investigación de Outliers en Swing Electoral
Analiza casos con swing extremo (>1000%) para identificar posibles errores o anomalías
"""

import pandas as pd
import numpy as np

# Configuración
SWING_FILE = "outputs/swing/swings_por_df_20251022_142907.csv"
VOTOS_LOCALES_DIR = "estados_swing"
EQUIVALENCIAS_FILE = "outputs/swing/tabla_equivalencia_seccion_df.csv"
VOTOS_FEDERALES = "data/computos_diputados_2021.parquet"

def cargar_datos():
    """Carga todos los datos necesarios"""
    print("=" * 80)
    print("INVESTIGACIÓN DE OUTLIERS EN SWING ELECTORAL")
    print("=" * 80)
    
    swing_df = pd.read_csv(SWING_FILE)
    equiv_df = pd.read_csv(EQUIVALENCIAS_FILE)
    fed_df = pd.read_parquet(VOTOS_FEDERALES)
    
    return swing_df, equiv_df, fed_df

def identificar_outliers(swing_df, umbral=500):
    """Identifica distritos con swing extremo"""
    print(f"\n[INFO] Buscando outliers (swing > {umbral}%)...")
    
    partidos = ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA']
    outliers = []
    
    for partido in partidos:
        col = f'swing_{partido}'
        df_extremos = swing_df[swing_df[col] > umbral]
        
        if len(df_extremos) > 0:
            print(f"\n{partido}: {len(df_extremos)} casos")
            for idx, row in df_extremos.iterrows():
                outliers.append({
                    'ESTADO': row['NOMBRE_ESTADO'],
                    'DF': row['DF_2021'],
                    'PARTIDO': partido,
                    'SWING': row[col],
                    'VOTOS_LOCAL': row[f'{partido}_local'],
                    'VOTOS_FED_2021': row[f'{partido}_fed_2021']
                })
                print(f"  {row['NOMBRE_ESTADO']} DF-{int(row['DF_2021'])}: "
                      f"{row[col]:+.1f}% (Fed: {row[f'{partido}_fed_2021']:.0f} → "
                      f"Local: {row[f'{partido}_local']:.0f})")
    
    return pd.DataFrame(outliers)

def analizar_coahuila_df3(swing_df, equiv_df):
    """Análisis detallado de Coahuila DF-3"""
    print("\n" + "=" * 80)
    print("CASO 1: COAHUILA DF-3 (PT +3,797%)")
    print("=" * 80)
    
    # Obtener datos del distrito
    df_caso = swing_df[(swing_df['NOMBRE_ESTADO'] == 'Coahuila') & 
                       (swing_df['DF_2021'] == 3)].iloc[0]
    
    print("\n1. RESUMEN DEL DISTRITO:")
    print(f"   Estado: {df_caso['NOMBRE_ESTADO']}")
    print(f"   DF: {df_caso['DF_2021']}")
    print(f"   Año elección local: {df_caso['AÑO_ELECCION']}")
    
    print("\n2. COMPARACIÓN PT vs MORENA:")
    print(f"   PT Fed 2021:      {df_caso['PT_fed_2021']:>8.0f} votos")
    print(f"   PT Local 2023:    {df_caso['PT_local']:>8.0f} votos (+{(df_caso['PT_local']/df_caso['PT_fed_2021']-1)*100:.1f}%)")
    print(f"   MORENA Fed 2021:  {df_caso['MORENA_fed_2021']:>8.0f} votos")
    print(f"   MORENA Local 2023:{df_caso['MORENA_local']:>8.0f} votos ({(df_caso['MORENA_local']/df_caso['MORENA_fed_2021']-1)*100:.1f}%)")
    
    # Sumar PT + MORENA
    coalicion_fed = df_caso['PT_fed_2021'] + df_caso['MORENA_fed_2021']
    coalicion_local = df_caso['PT_local'] + df_caso['MORENA_local']
    
    print(f"\n3. COALICIÓN PT+MORENA:")
    print(f"   Fed 2021:  {coalicion_fed:>8.0f} votos")
    print(f"   Local 2023:{coalicion_local:>8.0f} votos ({(coalicion_local/coalicion_fed-1)*100:+.1f}%)")
    print(f"   → Swing coalición: {(coalicion_local/coalicion_fed-1)*100:+.1f}%")
    
    print("\n4. HIPÓTESIS:")
    if abs((coalicion_local/coalicion_fed-1)*100) < 50:
        print("   ✓ ROTACIÓN DE CANDIDATOS: Los votos se movieron entre PT y MORENA")
        print("     - 2021: Candidato fuerte bajo MORENA")
        print("     - 2023: Candidato fuerte bajo PT")
        print("     - La coalición mantiene votos similares")
    else:
        print("   ⚠ CRECIMIENTO REAL: La coalición creció significativamente")
    
    # Analizar secciones del distrito
    print("\n5. SECCIONES DEL DISTRITO:")
    secciones_df3 = equiv_df[(equiv_df['ENTIDAD'] == '05') & 
                             (equiv_df['DF_2021'] == 3)]
    print(f"   Total secciones: {len(secciones_df3)}")
    print(f"   Rango: {secciones_df3['SECCION'].min()} - {secciones_df3['SECCION'].max()}")
    
    # Cargar votos locales de Coahuila
    try:
        votos_local = pd.read_csv(f"{VOTOS_LOCALES_DIR}/2023_SEE_GOB_COAH_SEC.csv")
        votos_local.columns = [c.upper().strip() for c in votos_local.columns]
        
        # Filtrar secciones del DF-3
        votos_df3 = votos_local[votos_local['SECCION'].isin(secciones_df3['SECCION'])]
        
        print(f"\n6. VOTOS LOCALES 2023 (DF-3):")
        print(f"   Secciones con datos: {len(votos_df3)}")
        
        if 'PT' in votos_df3.columns and 'MORENA' in votos_df3.columns:
            pt_por_seccion = votos_df3.groupby('SECCION')['PT'].sum().sort_values(ascending=False)
            morena_por_seccion = votos_df3.groupby('SECCION')['MORENA'].sum().sort_values(ascending=False)
            
            print(f"\n   Top 5 secciones PT:")
            for seccion, votos in pt_por_seccion.head(5).items():
                print(f"     Sección {seccion}: {votos:>6.0f} votos")
            
            print(f"\n   Top 5 secciones MORENA:")
            for seccion, votos in morena_por_seccion.head(5).items():
                print(f"     Sección {seccion}: {votos:>6.0f} votos")
            
            # Verificar si hay secciones con PT/MORENA muy dispares
            votos_df3_agg = votos_df3.groupby('SECCION')[['PT', 'MORENA']].sum()
            votos_df3_agg['ratio_PT_MORENA'] = votos_df3_agg['PT'] / (votos_df3_agg['MORENA'] + 1)
            
            print(f"\n7. ANÁLISIS DE RATIOS PT/MORENA POR SECCIÓN:")
            print(f"   Ratio promedio: {votos_df3_agg['ratio_PT_MORENA'].mean():.2f}")
            print(f"   Ratio mediana:  {votos_df3_agg['ratio_PT_MORENA'].median():.2f}")
            print(f"   Ratio max:      {votos_df3_agg['ratio_PT_MORENA'].max():.2f}")
            
            secciones_pt_dominante = votos_df3_agg[votos_df3_agg['ratio_PT_MORENA'] > 2]
            print(f"\n   Secciones donde PT > 2x MORENA: {len(secciones_pt_dominante)}")
            if len(secciones_pt_dominante) > 0:
                print(f"   Representan {len(secciones_pt_dominante)/len(votos_df3_agg)*100:.1f}% del distrito")
    
    except Exception as e:
        print(f"\n   [ERROR] No se pudieron cargar votos locales: {e}")
    
    print("\n8. DIAGNÓSTICO:")
    print("   Causa más probable: ROTACIÓN DE CANDIDATURA entre PT y MORENA")
    print("   - En 2023 el candidato/a fuerte se registró bajo PT en lugar de MORENA")
    print("   - La coalición mantiene fuerza similar, pero cambia la distribución interna")
    
    print("\n9. RECOMENDACIÓN:")
    print("   Para modelado de swing, considerar:")
    print("   a) Usar swing de la COALICIÓN (PT+MORENA) en lugar de individual")
    print("   b) O excluir PT/MORENA de Coahuila del análisis de swing")
    print("   c) Aplicar factor de confianza bajo (0.3) a este distrito")

def analizar_quintana_roo_pvem(swing_df, equiv_df):
    """Análisis de Quintana Roo con PVEM extremo"""
    print("\n" + "=" * 80)
    print("CASO 2: QUINTANA ROO - PVEM (+289% a +676%)")
    print("=" * 80)
    
    qroo_pvem = swing_df[swing_df['NOMBRE_ESTADO'] == 'Quintana Roo'][
        ['DF_2021', 'PVEM_local', 'PVEM_fed_2021', 'swing_PVEM', 
         'MC_local', 'MC_fed_2021', 'swing_MC']
    ]
    
    print("\nResumen PVEM y MC en Quintana Roo:")
    print(qroo_pvem.to_string(index=False))
    
    print("\n1. OBSERVACIONES:")
    total_pvem_fed = qroo_pvem['PVEM_fed_2021'].sum()
    total_pvem_local = qroo_pvem['PVEM_local'].sum()
    total_mc_fed = qroo_pvem['MC_fed_2021'].sum()
    total_mc_local = qroo_pvem['MC_local'].sum()
    
    print(f"   PVEM estatal: {total_pvem_fed:.0f} → {total_pvem_local:.0f} (+{(total_pvem_local/total_pvem_fed-1)*100:.1f}%)")
    print(f"   MC estatal:   {total_mc_fed:.0f} → {total_mc_local:.0f} (+{(total_mc_local/total_mc_fed-1)*100:.1f}%)")
    
    print("\n2. HIPÓTESIS:")
    print("   - PVEM y MC pueden haber tenido candidatos locales muy fuertes")
    print("   - O hubo cambio en alianzas (PVEM salió de coalición con MORENA)")
    print("   - MC suele tener crecimiento en elecciones locales vs federales")
    
    print("\n3. RECOMENDACIÓN:")
    print("   - Verificar si PVEM/MC fueron en coalición en 2021 federal")
    print("   - Si el crecimiento es consistente en los 4 distritos, es real")
    print("   - Aplicar factor de confianza medio (0.6-0.7)")

def analizar_mexico_faltantes(swing_df):
    """Analiza por qué México tiene -100% en varios partidos"""
    print("\n" + "=" * 80)
    print("CASO 3: MÉXICO - Datos faltantes (-100%)")
    print("=" * 80)
    
    mex_df = swing_df[swing_df['NOMBRE_ESTADO'] == 'México']
    
    print(f"\nTotal distritos de México: {len(mex_df)}")
    
    partidos = ['PVEM', 'PT', 'MC', 'MORENA']
    for partido in partidos:
        col = f'swing_{partido}'
        faltantes = mex_df[mex_df[col] == -100.0]
        print(f"\n{partido}:")
        print(f"  Distritos con -100%: {len(faltantes)} de {len(mex_df)}")
        
        if len(faltantes) > 0:
            # Verificar votos locales
            col_local = f'{partido}_local'
            if col_local in mex_df.columns:
                votos_local = mex_df[col_local].sum()
                print(f"  Votos locales totales: {votos_local:.0f}")
                if votos_local == 0 or pd.isna(votos_local):
                    print(f"  → Causa: No hay votos locales de {partido} en México 2023")
    
    print("\n1. DIAGNÓSTICO:")
    print("   Causa probable: En elecciones locales 2023 de México,")
    print("   varios partidos NO participaron o fueron en COALICIÓN")
    
    print("\n2. VERIFICAR:")
    try:
        votos_mex = pd.read_csv(f"{VOTOS_LOCALES_DIR}/2023_SEE_GOB_MEX_SEC.csv")
        votos_mex.columns = [c.upper().strip() for c in votos_mex.columns]
        print(f"\n   Columnas en archivo local: {list(votos_mex.columns)}")
        
        # Ver si hay columnas de coaliciones
        cols_coalicion = [c for c in votos_mex.columns if 'COAL' in c or 'ALIANZA' in c]
        if cols_coalicion:
            print(f"\n   Coaliciones detectadas: {cols_coalicion}")
    except Exception as e:
        print(f"\n   [ERROR] No se pudo leer archivo: {e}")
    
    print("\n3. RECOMENDACIÓN:")
    print("   - Excluir México del análisis de swing para PVEM, PT, MC, MORENA")
    print("   - O desagregar coaliciones si el CSV las incluye")

def generar_reporte_limpieza(swing_df):
    """Genera reporte con recomendaciones de limpieza"""
    print("\n" + "=" * 80)
    print("REPORTE DE LIMPIEZA DE DATOS")
    print("=" * 80)
    
    outliers_extremos = []
    partidos = ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA']
    
    for idx, row in swing_df.iterrows():
        for partido in partidos:
            swing_val = row[f'swing_{partido}']
            
            # Criterios de outlier
            es_outlier = False
            razon = ""
            accion = ""
            
            if swing_val > 1000:
                es_outlier = True
                razon = f"Swing extremo: {swing_val:.1f}%"
                accion = "REVISAR - Posible rotación de candidatos o error"
            elif swing_val == -100:
                es_outlier = True
                razon = "Datos faltantes"
                accion = "EXCLUIR - Sin datos locales"
            elif abs(swing_val) > 500:
                es_outlier = True
                razon = f"Swing muy alto: {swing_val:.1f}%"
                accion = "VERIFICAR - Cambio significativo"
            
            if es_outlier:
                outliers_extremos.append({
                    'ESTADO': row['NOMBRE_ESTADO'],
                    'DF': row['DF_2021'],
                    'PARTIDO': partido,
                    'SWING': swing_val,
                    'VOTOS_LOCAL': row[f'{partido}_local'],
                    'VOTOS_FED': row[f'{partido}_fed_2021'],
                    'RAZON': razon,
                    'ACCION': accion
                })
    
    outliers_df = pd.DataFrame(outliers_extremos)
    
    print(f"\nTotal casos detectados: {len(outliers_df)}")
    print(f"\nPor tipo de acción:")
    print(outliers_df['ACCION'].value_counts())
    
    # Exportar
    output_file = "outputs/swing/outliers_detectados.csv"
    outliers_df.to_csv(output_file, index=False)
    print(f"\n[OK] Reporte exportado: {output_file}")
    
    return outliers_df

def main():
    """Función principal"""
    try:
        # Cargar datos
        swing_df, equiv_df, fed_df = cargar_datos()
        
        # 1. Identificar outliers
        outliers_df = identificar_outliers(swing_df, umbral=500)
        
        # 2. Casos específicos
        analizar_coahuila_df3(swing_df, equiv_df)
        analizar_quintana_roo_pvem(swing_df, equiv_df)
        analizar_mexico_faltantes(swing_df)
        
        # 3. Reporte de limpieza
        outliers_reporte = generar_reporte_limpieza(swing_df)
        
        print("\n" + "=" * 80)
        print("[OK] Investigación completada")
        print("=" * 80)
        
        print("\nRESUMEN EJECUTIVO:")
        print("1. Coahuila PT: Rotación de candidatos entre PT y MORENA")
        print("2. Quintana Roo PVEM/MC: Crecimiento real o candidatos locales fuertes")
        print("3. México -100%: Partidos en coalición en elecciones locales")
        print("\nRECOMENDACIÓN: Usar swing de coaliciones en lugar de partidos individuales")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
