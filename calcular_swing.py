"""
Script para calcular swing electoral por distrito federal

Proceso:
1. Leer shapefiles (.shp) de BGD por estado
2. Extraer equivalencia: ENTIDAD + SECCIÓN → DISTRITO FEDERAL (DF_2021)
3. Leer votos por sección de elecciones locales (SEE_GOB_*_SEC.csv)
4. Leer votos federales 2021 (computos_diputados_2021.parquet)
5. Calcular swing = (votos_locales - votos_federales) / votos_federales * 100
6. Exportar resultados

Estados con swing:
- Aguascalientes (2022)
- Durango (2022)
- Hidalgo (2022)
- Oaxaca (2022)
- Quintana Roo (2022)
- Tamaulipas (2022)
- Coahuila (2023)
- Estado de México (2023)
"""

import pandas as pd
import geopandas as gpd
import os
import glob
from pathlib import Path
import numpy as np
from datetime import datetime

# ============================================
# CONFIGURACIÓN
# ============================================

# Directorio base donde están los shapefiles de BGD
SHAPEFILE_DIR = "estados_swing"

# Directorio donde están los archivos de votos por sección  
VOTOS_SECCION_DIR = "estados_swing"

# Archivo de votos federales 2021
VOTOS_FEDERALES_2021 = "data/computos_diputados_2021.parquet"

# Directorio de salida
OUTPUT_DIR = "outputs/swing"

# Estados con swing (nombre y CVE_ENT)
ESTADOS_SWING = {
    "01": {"nombre": "Aguascalientes", "año": 2022},
    "10": {"nombre": "Durango", "año": 2022},
    "13": {"nombre": "Hidalgo", "año": 2022},
    "20": {"nombre": "Oaxaca", "año": 2022},
    "23": {"nombre": "Quintana Roo", "año": 2022},
    "28": {"nombre": "Tamaulipas", "año": 2022},
    "05": {"nombre": "Coahuila", "año": 2023},
    "15": {"nombre": "México", "año": 2023}
}


# ============================================
# PASO 1: EXTRAER EQUIVALENCIA SECCIÓN → DF
# ============================================

def buscar_shapefiles_seccion_df(base_dir):
    """
    Busca shapefiles SECCION.shp que contengan columnas CVE_ENT, SECCION y CVE_DF
    Ignora otros tipos de shapefiles (vocales, RFE, manzanas, etc.)
    """
    print(f"\n[INFO] Buscando shapefiles SECCION.shp en: {base_dir}")
    
    if not os.path.exists(base_dir):
        print(f"[ERROR] No existe el directorio: {base_dir}")
        return []
    
    # Buscar específicamente archivos SECCION.shp
    shapefiles = glob.glob(f"{base_dir}/**/SECCION.shp", recursive=True)
    print(f"[INFO] Encontrados {len(shapefiles)} archivos SECCION.shp")
    
    shapefiles_validos = []
    
    for shp_path in shapefiles:
        try:
            # Leer solo el schema (sin cargar geometrías)
            gdf = gpd.read_file(shp_path, rows=1)
            columnas = [c.upper() for c in gdf.columns]
            
            # Verificar si tiene las columnas necesarias
            tiene_entidad = any(c in columnas for c in ['CVE_ENT', 'ENTIDAD', 'CVE_ENTIDAD'])
            tiene_seccion = any(c in columnas for c in ['SECCION', 'CVE_SEC'])
            tiene_df = any(c in columnas for c in ['CVE_DF', 'DISTRITO', 'DF', 'DISTRITO_F'])
            
            if tiene_entidad and tiene_seccion and tiene_df:
                estado_dir = os.path.basename(os.path.dirname(shp_path))
                print(f"  [OK] {estado_dir}/SECCION.shp")
                shapefiles_validos.append(shp_path)
            else:
                print(f"  [X] {shp_path} - Faltan columnas: {columnas}")
        
        except Exception as e:
            print(f"  [X] {shp_path} - Error: {e}")
    
    print(f"\n[INFO] Shapefiles válidos encontrados: {len(shapefiles_validos)}")
    return shapefiles_validos


def extraer_equivalencias_seccion_df(shapefiles):
    """
    Extrae la tabla de equivalencia ENTIDAD + SECCIÓN → DF_2021
    de todos los shapefiles válidos
    """
    print("\n[INFO] Extrayendo equivalencias SECCIÓN → DF...")
    
    tablas = []
    
    for shp_path in shapefiles:
        try:
            # Leer shapefile
            gdf = gpd.read_file(shp_path)
            
            # Normalizar nombres de columnas
            gdf.columns = [c.upper() for c in gdf.columns]
            
            # Identificar columnas (pueden variar según el archivo)
            col_entidad = next((c for c in gdf.columns if c in ['CVE_ENT', 'ENTIDAD', 'CVE_ENTIDAD']), None)
            col_seccion = next((c for c in gdf.columns if c in ['SECCION', 'CVE_SEC']), None)
            col_df = next((c for c in gdf.columns if c in ['CVE_DF', 'DISTRITO', 'DF', 'DISTRITO_F']), None)
            
            if not all([col_entidad, col_seccion, col_df]):
                print(f"  [WARN] {os.path.basename(shp_path)} - Falta alguna columna")
                continue
            
            # Extraer tabla
            df = pd.DataFrame({
                'ENTIDAD': gdf[col_entidad].astype(str).str.zfill(2),
                'SECCION': gdf[col_seccion].astype(int),
                'DF_2021': gdf[col_df].astype(int)
            })
            
            # Eliminar duplicados
            df = df.drop_duplicates()
            
            estado = df['ENTIDAD'].iloc[0] if len(df) > 0 else 'UNK'
            nombre_estado = ESTADOS_SWING.get(estado, {}).get('nombre', estado)
            
            print(f"  [OK] {nombre_estado} ({estado}): {len(df)} secciones")
            tablas.append(df)
        
        except Exception as e:
            print(f"  [X] {os.path.basename(shp_path)} - Error: {e}")
    
    # Concatenar todas las tablas
    if tablas:
        tabla_maestra = pd.concat(tablas, ignore_index=True)
        tabla_maestra = tabla_maestra.drop_duplicates()
        print(f"\n[INFO] Tabla maestra: {len(tabla_maestra)} registros únicos")
        return tabla_maestra
    else:
        print("\n[ERROR] No se pudo generar la tabla maestra")
        return None


# ============================================
# PASO 2: LEER VOTOS POR SECCIÓN (LOCALES)
# ============================================

def leer_votos_locales(votos_dir):
    """
    Lee archivos SEE_GOB_*_SEC.csv de votos por sección de elecciones locales
    """
    print(f"\n[INFO] Leyendo votos locales desde: {votos_dir}")
    
    if not os.path.exists(votos_dir):
        print(f"[ERROR] No existe el directorio: {votos_dir}")
        return None
    
    # Buscar archivos de votos por sección (en el directorio raíz)
    archivos_votos = glob.glob(f"{votos_dir}/*SEE_GOB_*_SEC.csv")
    
    print(f"[INFO] Encontrados {len(archivos_votos)} archivos de votos")
    
    if not archivos_votos:
        print("[ERROR] No se encontraron archivos de votos por sección")
        return None
    
    votos_locales = []
    
    for archivo in archivos_votos:
        try:
            # Leer CSV
            df = pd.read_csv(archivo, encoding='latin-1')
            
            # Normalizar columnas
            df.columns = [c.upper().strip() for c in df.columns]
            
            # Asegurar que SECCION sea string con ceros a la izquierda si es necesario
            if 'SECCION' in df.columns:
                df['SECCION'] = df['SECCION'].astype(int)
            
            # Asegurar que ID_ESTADO sea string de 2 dígitos
            if 'ID_ESTADO' in df.columns:
                df['ENTIDAD'] = df['ID_ESTADO'].astype(str).str.zfill(2)
            
            print(f"  [OK] {os.path.basename(archivo)}: {len(df)} registros")
            votos_locales.append(df)
        
        except Exception as e:
            print(f"  [X] {os.path.basename(archivo)} - Error: {e}")
            import traceback
            traceback.print_exc()
    
    if votos_locales:
        df_votos = pd.concat(votos_locales, ignore_index=True)
        print(f"\n[INFO] Total votos locales: {len(df_votos)} registros")
        return df_votos
    else:
        return None


# ============================================
# PASO 3: LEER VOTOS FEDERALES 2021
# ============================================

def leer_votos_federales_2021(path_parquet):
    """
    Lee votos federales de 2021 por distrito
    """
    print(f"\n[INFO] Leyendo votos federales 2021: {path_parquet}")
    
    if not os.path.exists(path_parquet):
        print(f"[ERROR] No existe: {path_parquet}")
        return None
    
    df = pd.read_parquet(path_parquet)
    print(f"[INFO] Votos federales 2021: {len(df)} registros")
    
    return df


# ============================================
# PASO 4: CALCULAR SWING
# ============================================

def calcular_swing(votos_locales_df, votos_federales_df, equivalencias_df):
    """
    Calcula el swing por distrito federal:
    swing = (votos_locales - votos_federales) / votos_federales * 100
    """
    print("\n[INFO] Calculando swing por distrito federal...")
    
    # Asegurarse de que las columnas existen
    if equivalencias_df is None or votos_locales_df is None or votos_federales_df is None:
        print("[ERROR] Faltan datos necesarios para calcular swing")
        return None
    
    # PASO 1: Unir votos locales con equivalencias SECCIÓN → DF
    print("[INFO] Uniendo votos locales con equivalencias SECCIÓN → DF...")
    
    votos_con_df = votos_locales_df.merge(
        equivalencias_df,
        on=['ENTIDAD', 'SECCION'],
        how='inner'
    )
    
    print(f"  Registros después de unir: {len(votos_con_df)}")
    print(f"  Secciones sin match: {len(votos_locales_df) - len(votos_con_df)}")
    
    # PASO 2: Identificar columnas de partidos en votos locales
    columnas_partidos = ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA']
    columnas_disponibles = [c for c in columnas_partidos if c in votos_con_df.columns]
    
    print(f"[INFO] Partidos encontrados en votos locales: {columnas_disponibles}")
    
    # Convertir a numérico
    for partido in columnas_disponibles:
        votos_con_df[partido] = pd.to_numeric(votos_con_df[partido], errors='coerce').fillna(0)
    
    # PASO 3: Agregar votos locales por DF
    print("[INFO] Agregando votos locales por DF...")
    
    votos_locales_por_df = votos_con_df.groupby(['ENTIDAD', 'DF_2021'])[columnas_disponibles].sum().reset_index()
    
    print(f"  Distritos únicos: {len(votos_locales_por_df)}")
    
    # PASO 4: Filtrar votos federales solo de estados con swing
    print("[INFO] Filtrando votos federales 2021 de estados con swing...")
    
    entidades_swing = list(ESTADOS_SWING.keys())
    votos_federales_filtrados = votos_federales_df[
        votos_federales_df['ENTIDAD'].str.upper().isin([ESTADOS_SWING[e]['nombre'].upper() for e in entidades_swing])
    ].copy()
    
    # Mapear nombre de entidad a código
    nombre_a_codigo = {v['nombre'].upper(): k for k, v in ESTADOS_SWING.items()}
    votos_federales_filtrados['ENTIDAD_COD'] = votos_federales_filtrados['ENTIDAD'].str.upper().map(nombre_a_codigo)
    
    # Renombrar DISTRITO a DF_2021 para hacer el join
    votos_federales_filtrados = votos_federales_filtrados.rename(columns={'DISTRITO': 'DF_2021'})
    
    print(f"  Registros de votos federales: {len(votos_federales_filtrados)}")
    
    # PASO 5: Unir votos locales con federales
    print("[INFO] Uniendo votos locales con federales por DF...")
    
    swing_df = votos_locales_por_df.merge(
        votos_federales_filtrados[['ENTIDAD_COD', 'DF_2021'] + columnas_disponibles],
        left_on=['ENTIDAD', 'DF_2021'],
        right_on=['ENTIDAD_COD', 'DF_2021'],
        how='inner',
        suffixes=('_local', '_fed_2021')
    )
    
    print(f"  Distritos con ambos datos: {len(swing_df)}")
    
    # PASO 6: Calcular swing por partido
    print("[INFO] Calculando swing...")
    
    for partido in columnas_disponibles:
        col_local = f'{partido}_local'
        col_fed = f'{partido}_fed_2021'
        
        if col_local in swing_df.columns and col_fed in swing_df.columns:
            # swing = ((local - federal) / federal) * 100
            swing_df[f'swing_{partido}'] = (
                (swing_df[col_local] - swing_df[col_fed]) / 
                swing_df[col_fed].replace(0, np.nan)
            ) * 100
            
            # Rellenar infinitos y NaN
            swing_df[f'swing_{partido}'] = swing_df[f'swing_{partido}'].replace([np.inf, -np.inf], np.nan).fillna(0)
    
    # PASO 7: Añadir metadatos
    swing_df['NOMBRE_ESTADO'] = swing_df['ENTIDAD'].map(lambda x: ESTADOS_SWING.get(x, {}).get('nombre', x))
    swing_df['AÑO_ELECCION'] = swing_df['ENTIDAD'].map(lambda x: ESTADOS_SWING.get(x, {}).get('año', ''))
    
    # Reordenar columnas
    columnas_info = ['NOMBRE_ESTADO', 'ENTIDAD', 'DF_2021', 'AÑO_ELECCION']
    columnas_swing = [c for c in swing_df.columns if c.startswith('swing_')]
    columnas_votos_local = [c for c in swing_df.columns if c.endswith('_local')]
    columnas_votos_fed = [c for c in swing_df.columns if c.endswith('_fed_2021')]
    
    swing_df = swing_df[columnas_info + columnas_swing + columnas_votos_local + columnas_votos_fed]
    
    print(f"[INFO] Swing calculado para {len(swing_df)} distritos")
    
    return swing_df


# ============================================
# FUNCIÓN PRINCIPAL
# ============================================

def main():
    """
    Pipeline completo para calcular swing electoral
    """
    print("=" * 80)
    print("CÁLCULO DE SWING ELECTORAL POR DISTRITO FEDERAL")
    print("=" * 80)
    
    # Crear directorio de salida
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # PASO 1: Extraer equivalencia SECCIÓN → DF desde shapefiles
    shapefiles_validos = buscar_shapefiles_seccion_df(SHAPEFILE_DIR)
    
    if not shapefiles_validos:
        print("\n[ERROR] No se encontraron shapefiles válidos")
        print("\n[INSTRUCCIONES]:")
        print(f"1. Descarga los shapefiles de BGD para los 8 estados con swing")
        print(f"2. Colócalos en: {SHAPEFILE_DIR}")
        print(f"3. Estructura esperada: {SHAPEFILE_DIR}/[estado]/[archivos .shp]")
        print(f"4. Los shapefiles deben contener columnas: CVE_ENT, SECCION, CVE_DF")
        return
    
    # Extraer tabla de equivalencias
    equivalencias = extraer_equivalencias_seccion_df(shapefiles_validos)
    
    if equivalencias is not None:
        # Guardar tabla maestra
        output_equiv = f"{OUTPUT_DIR}/tabla_equivalencia_seccion_df.csv"
        equivalencias.to_csv(output_equiv, index=False)
        print(f"\n[[OK]] Tabla de equivalencias guardada: {output_equiv}")
        
        # Mostrar preview
        print("\n[PREVIEW - Primeras 10 filas]:")
        print(equivalencias.head(10))
        
        # Estadísticas por estado
        print("\n[ESTADÍSTICAS POR ESTADO]:")
        resumen = equivalencias.groupby('ENTIDAD').agg({
            'SECCION': 'count',
            'DF_2021': 'nunique'
        }).rename(columns={'SECCION': 'num_secciones', 'DF_2021': 'num_distritos'})
        
        for entidad, row in resumen.iterrows():
            nombre = ESTADOS_SWING.get(entidad, {}).get('nombre', entidad)
            print(f"  • {nombre} ({entidad}): {row['num_secciones']} secciones, "
                  f"{row['num_distritos']} distritos")
    
    # PASO 2: Leer votos locales
    votos_locales = leer_votos_locales(VOTOS_SECCION_DIR)
    
    # PASO 3: Leer votos federales 2021
    votos_federales = leer_votos_federales_2021(VOTOS_FEDERALES_2021)
    
    # PASO 4: Calcular swing
    if equivalencias is not None and votos_locales is not None and votos_federales is not None:
        swing_df = calcular_swing(votos_locales, votos_federales, equivalencias)
        
        if swing_df is not None:
            # Guardar resultados
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_swing = f"{OUTPUT_DIR}/swings_por_df_{timestamp}.csv"
            swing_df.to_csv(output_swing, index=False)
            
            print(f"\n[[OK]] Swing calculado y guardado: {output_swing}")
            
            # Mostrar preview
            print("\n[PREVIEW - Primeras 10 filas]:")
            pd.set_option('display.max_columns', None)
            pd.set_option('display.width', None)
            print(swing_df.head(10))
            
            # Estadísticas de swing por estado y partido
            print("\n[ESTADÍSTICAS DE SWING]:")
            columnas_swing = [c for c in swing_df.columns if c.startswith('swing_')]
            
            for estado in swing_df['NOMBRE_ESTADO'].unique():
                print(f"\n  {estado}:")
                estado_df = swing_df[swing_df['NOMBRE_ESTADO'] == estado]
                
                for col_swing in columnas_swing:
                    partido = col_swing.replace('swing_', '')
                    swing_promedio = estado_df[col_swing].mean()
                    print(f"    • {partido}: {swing_promedio:+.2f}% promedio")
            
            # Exportar también versión agregada por estado
            swing_por_estado = swing_df.groupby('NOMBRE_ESTADO')[columnas_swing].mean().reset_index()
            output_estado = f"{OUTPUT_DIR}/swing_promedio_por_estado_{timestamp}.csv"
            swing_por_estado.to_csv(output_estado, index=False)
            print(f"\n[OK] Swing promedio por estado guardado: {output_estado}")
    
    print("\n" + "=" * 80)
    print("[OK] Proceso completado")
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] Error en el proceso: {e}")
        import traceback
        traceback.print_exc()

