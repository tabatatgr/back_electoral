"""
MÓDULO C: Tabla Puente

Crea tabla de mapeo entre cartografía original (300 distritos) y nueva (N distritos).
Permite reagregar votos por sección según la nueva distritación.

Input:
- Distritación original: INE_SECCION_2020.csv (ENTIDAD, DISTRITO, SECCION)
- Distritación nueva: Resultado de MÓDULO B (ENTIDAD, SECCION, DISTRITO_NEW)
- Votos por sección: computos_diputados_{anio}.parquet

Output:
- Tabla puente: (ENTIDAD, SECCION, DISTRITO_OLD, DISTRITO_NEW)
- Votos reagregados: votos por DISTRITO_NEW
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from pathlib import Path


def crear_tabla_puente(
    secciones_con_distrito_new: pd.DataFrame,
    print_debug: bool = False
) -> pd.DataFrame:
    """
    Crea tabla de mapeo entre distritos originales y nuevos.
    
    Args:
        secciones_con_distrito_new: DataFrame con columnas:
            - ENTIDAD (int): ID de estado
            - SECCION (int): ID de sección
            - DISTRITO (int): Distrito original INE 2017
            - DISTRITO_NEW (int): Distrito nuevo asignado
        print_debug: Mostrar logs
    
    Returns:
        DataFrame con tabla puente completa
    """
    if print_debug:
        print("\n[TABLA PUENTE] Creando mapeo distrito_old → distrito_new")
    
    # Validar columnas requeridas
    required = ['ENTIDAD', 'SECCION', 'DISTRITO', 'DISTRITO_NEW']
    missing = [c for c in required if c not in secciones_con_distrito_new.columns]
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {missing}")
    
    # Crear tabla puente
    puente = secciones_con_distrito_new[required].copy()
    
    # Renombrar para claridad
    puente = puente.rename(columns={
        'DISTRITO': 'DISTRITO_OLD',
        'DISTRITO_NEW': 'DISTRITO_NEW'
    })
    
    if print_debug:
        print(f"  Secciones mapeadas: {len(puente):,}")
        print(f"  Estados: {puente['ENTIDAD'].nunique()}")
        print(f"  Distritos originales: {puente['DISTRITO_OLD'].nunique()}")
        print(f"  Distritos nuevos: {puente['DISTRITO_NEW'].nunique()}")
        
        # Verificar integridad
        sin_distrito_new = puente[puente['DISTRITO_NEW'] == 0]
        if len(sin_distrito_new) > 0:
            print(f"  ⚠ Advertencia: {len(sin_distrito_new)} secciones sin DISTRITO_NEW")
    
    return puente


def reagregar_votos_por_distrito_new(
    votos_distrito_wide: pd.DataFrame,
    tabla_puente: pd.DataFrame,
    print_debug: bool = False
) -> pd.DataFrame:
    """
    Reagrega votos por partido según la nueva distritación.
    
    NOTA: El parquet de votos viene en formato WIDE (una fila por distrito, partidos en columnas).
    Necesitamos mapear DISTRITO_OLD → DISTRITO_NEW y reagregar.
    
    Args:
        votos_distrito_wide: DataFrame de votos formato WIDE:
            - ENTIDAD (str)
            - DISTRITO (int)  # Distrito original
            - [partidos...] (columnas de votos)
        tabla_puente: Resultado de crear_tabla_puente()
        print_debug: Mostrar logs
    
    Returns:
        DataFrame con votos reagregados por DISTRITO_NEW (formato WIDE)
    """
    if print_debug:
        print("\n[REAGREGACIÓN] Reagrupando votos por DISTRITO_NEW")
        print(f"  Input shape: {votos_distrito_wide.shape}")
        print(f"  Columnas: {votos_distrito_wide.columns.tolist()[:10]}")
    
    # El archivo viene con ENTIDAD, DISTRITO como filas y partidos como columnas
    # Necesitamos mapear cada DISTRITO_OLD a secciones, luego a DISTRITO_NEW
    
    # Primero, vamos a cargar votos por sección (no por distrito)
    # Pero como solo tenemos votos agregados por distrito, necesitamos
    # desagregar proporcionalmente por sección
    
    # SIMPLIFICACIÓN: Usar tabla puente para mapear distritos viejos → nuevos
    # Crear mapeo de (ENTIDAD, DISTRITO_OLD) → lista de DISTRITO_NEW
    
    from redistritacion.modulos.distritacion import cargar_secciones_ine
    
    # Cargar datos de secciones para hacer el mapeo
    secciones_ine = cargar_secciones_ine()
    
    # Necesitamos votos por SECCION, no por DISTRITO
    # Como solo tenemos votos agregados, vamos a hacer una aproximación:
    # Redistribuir los votos de cada distrito viejo entre los distritos nuevos
    # según cuántas secciones de ese distrito viejo van a cada distrito nuevo
    
    # 1. Contar secciones por (ENTIDAD, DISTRITO_OLD, DISTRITO_NEW)
    conteo_secciones = tabla_puente.groupby(
        ['ENTIDAD', 'DISTRITO_OLD', 'DISTRITO_NEW']
    ).size().reset_index(name='N_SECCIONES')
    
    if print_debug:
        print(f"  Mapeo distrito_old → distrito_new: {len(conteo_secciones)} combinaciones")
    
    # 2. Normalizar nombres de entidades en votos_distrito_wide
    # El parquet usa nombres de texto, la tabla puente usa IDs numéricos
    from engine.procesar_diputados_v2 import normalize_entidad_ascii
    
    # Crear mapeo de nombre → ID
    estados_map = {
        'AGUASCALIENTES': 1, 'BAJA CALIFORNIA': 2, 'BAJA CALIFORNIA SUR': 3,
        'CAMPECHE': 4, 'CHIAPAS': 5, 'CHIHUAHUA': 6, 'CIUDAD DE MEXICO': 9,
        'COAHUILA': 7, 'COLIMA': 8, 'DURANGO': 10, 'GUANAJUATO': 11,
        'GUERRERO': 12, 'HIDALGO': 13, 'JALISCO': 14, 'MEXICO': 15,
        'MICHOACAN': 16, 'MORELOS': 17, 'NAYARIT': 18, 'NUEVO LEON': 19,
        'OAXACA': 20, 'PUEBLA': 21, 'QUERETARO': 22, 'QUINTANA ROO': 23,
        'SAN LUIS POTOSI': 24, 'SINALOA': 25, 'SONORA': 26, 'TABASCO': 27,
        'TAMAULIPAS': 28, 'TLAXCALA': 29, 'VERACRUZ': 30, 'YUCATAN': 31,
        'ZACATECAS': 32
    }
    
    votos_df = votos_distrito_wide.copy()
    votos_df['ENTIDAD_NORM'] = votos_df['ENTIDAD'].apply(normalize_entidad_ascii)
    votos_df['ENTIDAD_ID'] = votos_df['ENTIDAD_NORM'].map(estados_map)
    
    # 3. Merge para obtener proporción de secciones
    votos_con_mapeo = votos_df.merge(
        conteo_secciones,
        left_on=['ENTIDAD_ID', 'DISTRITO'],
        right_on=['ENTIDAD', 'DISTRITO_OLD'],
        how='left'
    )
    
    if print_debug:
        sin_mapeo = votos_con_mapeo[votos_con_mapeo['DISTRITO_NEW'].isna()]
        if len(sin_mapeo) > 0:
            print(f"  ⚠ {len(sin_mapeo)} distritos sin mapeo (probablemente fuera de muestra)")
    
    # Eliminar distritos sin mapeo
    votos_con_mapeo = votos_con_mapeo[votos_con_mapeo['DISTRITO_NEW'].notna()]
    
    # 4. Calcular total de secciones por distrito viejo
    total_secc_por_dist = conteo_secciones.groupby(
        ['ENTIDAD', 'DISTRITO_OLD']
    )['N_SECCIONES'].sum().reset_index(name='TOTAL_SECCIONES')
    
    votos_con_mapeo = votos_con_mapeo.merge(
        total_secc_por_dist,
        left_on=['ENTIDAD_ID', 'DISTRITO'],
        right_on=['ENTIDAD', 'DISTRITO_OLD'],
        how='left',
        suffixes=('', '_total')
    )
    
    # 5. Calcular proporción
    votos_con_mapeo['PROPORCION'] = votos_con_mapeo['N_SECCIONES'] / votos_con_mapeo['TOTAL_SECCIONES']
    
    # 6. Distribuir votos proporcionalmente
    partidos_cols = [c for c in votos_df.columns if c not in ['ENTIDAD', 'DISTRITO', 'ENTIDAD_NORM', 'ENTIDAD_ID', 'TOTAL_BOLETAS']]
    
    for partido in partidos_cols:
        if partido in votos_con_mapeo.columns:
            votos_con_mapeo[f'{partido}_NEW'] = votos_con_mapeo[partido] * votos_con_mapeo['PROPORCION']
    
    # 7. Reagregar por DISTRITO_NEW
    group_cols = ['ENTIDAD_ID', 'DISTRITO_NEW']
    agg_dict = {f'{p}_NEW': 'sum' for p in partidos_cols if f'{p}_NEW' in votos_con_mapeo.columns}
    
    votos_reagregados = votos_con_mapeo.groupby(group_cols, as_index=False).agg(agg_dict)
    
    # Renombrar columnas de vuelta
    rename_dict = {f'{p}_NEW': p for p in partidos_cols}
    votos_reagregados = votos_reagregados.rename(columns=rename_dict)
    
    # Renombrar DISTRITO_NEW → DISTRITO para compatibilidad
    votos_reagregados = votos_reagregados.rename(columns={
        'ENTIDAD_ID': 'ENTIDAD_ID_NUM',
        'DISTRITO_NEW': 'DISTRITO'
    })
    
    # Mapear ID → nombre de entidad
    id_to_estado = {v: k for k, v in estados_map.items()}
    votos_reagregados['ENTIDAD'] = votos_reagregados['ENTIDAD_ID_NUM'].map(id_to_estado)
    votos_reagregados = votos_reagregados.drop(columns=['ENTIDAD_ID_NUM'])
    
    # Reordenar columnas
    cols_order = ['ENTIDAD', 'DISTRITO'] + [c for c in votos_reagregados.columns if c not in ['ENTIDAD', 'DISTRITO']]
    votos_reagregados = votos_reagregados[cols_order]
    
    if print_debug:
        print(f"  ✓ Votos reagregados")
        print(f"  Distritos nuevos: {votos_reagregados['DISTRITO'].nunique()}")
        print(f"  Estados: {votos_reagregados['ENTIDAD'].nunique()}")
        print(f"  Output shape: {votos_reagregados.shape}")
    
    return votos_reagregados


def generar_siglado_new(
    votos_reagregados: pd.DataFrame,
    print_debug: bool = False
) -> pd.DataFrame:
    """
    Genera archivo siglado (ganadores por distrito) con nueva cartografía.
    
    Args:
        votos_reagregados: DataFrame formato WIDE (ENTIDAD, DISTRITO, [partidos...])
        print_debug: Mostrar logs
    
    Returns:
        DataFrame con ganadores por DISTRITO (formato compatible con motor)
    """
    if print_debug:
        print("\n[SIGLADO NEW] Calculando ganadores por distrito nuevo")
    
    # Identificar columnas de partidos
    partido_cols = [c for c in votos_reagregados.columns if c not in ['ENTIDAD', 'DISTRITO']]
    
    # Encontrar ganador por distrito
    ganadores = []
    for _, row in votos_reagregados.iterrows():
        votos_partidos = {p: row[p] for p in partido_cols if not pd.isna(row[p])}
        ganador = max(votos_partidos, key=votos_partidos.get)
        votos_ganador = votos_partidos[ganador]
        
        ganadores.append({
            'ENTIDAD': row['ENTIDAD'],
            'DISTRITO': int(row['DISTRITO']),
            'grupo_parlamentario': ganador,
            'VOTOS': votos_ganador,
            'coalicion': '',
            'tipo_eleccion': 'MR'
        })
    
    siglado_new = pd.DataFrame(ganadores)
    
    if print_debug:
        print(f"  Ganadores calculados: {len(siglado_new)}")
        print(f"\nDistribución por partido:")
        dist = siglado_new['grupo_parlamentario'].value_counts()
        for partido, count in dist.items():
            print(f"    {partido}: {count}")
    
    return siglado_new


def guardar_votos_reagregados(
    votos_reagregados: pd.DataFrame,
    output_path: str,
    print_debug: bool = False
):
    """
    Guarda votos reagregados en formato parquet compatible con motor electoral.
    
    Args:
        votos_reagregados: Resultado de reagregar_votos_por_distrito_new()
        output_path: Ruta para guardar (debe terminar en .parquet)
        print_debug: Mostrar logs
    """
    if print_debug:
        print(f"\n[GUARDAR] Exportando votos reagregados a {output_path}")
    
    # Asegurar que el directorio existe
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Guardar en parquet
    votos_reagregados.to_parquet(output_path, index=False)
    
    if print_debug:
        print(f"  ✓ Guardado: {len(votos_reagregados):,} registros")


# ==============================================================================
# PIPELINE COMPLETO
# ==============================================================================

def pipeline_tabla_puente(
    distritacion_resultado: Dict[int, pd.DataFrame],  # {entidad_id: secciones_con_DISTRITO_NEW}
    votos_parquet_path: str,
    output_dir: str = 'redistritacion/outputs',
    escenario_nombre: str = 'reforma_200_200',
    print_debug: bool = False
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Pipeline completo: distritación → tabla puente → votos reagregados → siglado.
    
    Args:
        distritacion_resultado: Dict con DataFrames de distritación por estado
        votos_parquet_path: Ruta a computos_diputados_{anio}.parquet
        output_dir: Directorio para outputs
        escenario_nombre: Nombre del escenario
        print_debug: Mostrar logs
    
    Returns:
        (tabla_puente, votos_reagregados, siglado_new)
    """
    if print_debug:
        print("="*80)
        print("PIPELINE TABLA PUENTE Y REAGREGACIÓN")
        print("="*80)
    
    # 1. Cargar secciones INE con distrito original
    if print_debug:
        print("\n[1/5] Cargando secciones INE con distrito original...")
    
    from redistritacion.modulos.distritacion import cargar_secciones_ine
    secciones_ine = cargar_secciones_ine()
    
    # 2. Combinar todas las distritaciones nuevas
    if print_debug:
        print("\n[2/5] Combinando distritaciones por estado...")
    
    todas_secciones = []
    for entidad_id, secciones_estado in distritacion_resultado.items():
        todas_secciones.append(secciones_estado)
    
    secciones_con_distrito_new = pd.concat(todas_secciones, ignore_index=True)
    
    if print_debug:
        print(f"  Total secciones: {len(secciones_con_distrito_new):,}")
    
    # 3. Crear tabla puente
    if print_debug:
        print("\n[3/5] Creando tabla puente...")
    
    tabla_puente = crear_tabla_puente(secciones_con_distrito_new, print_debug)
    
    # Guardar tabla puente
    puente_path = f"{output_dir}/tabla_puente_{escenario_nombre}.csv"
    Path(puente_path).parent.mkdir(parents=True, exist_ok=True)
    tabla_puente.to_csv(puente_path, index=False)
    if print_debug:
        print(f"  ✓ Guardado: {puente_path}")
    
    # 4. Cargar votos y reagregar
    if print_debug:
        print("\n[4/5] Cargando votos originales...")
    
    votos_df = pd.read_parquet(votos_parquet_path)
    
    # Reagregar por distrito nuevo
    votos_reagregados = reagregar_votos_por_distrito_new(votos_df, tabla_puente, print_debug)
    
    # Guardar votos reagregados
    votos_path = f"{output_dir}/votos_reagregados_{escenario_nombre}.parquet"
    guardar_votos_reagregados(votos_reagregados, votos_path, print_debug)
    
    # 5. Generar siglado
    if print_debug:
        print("\n[5/5] Generando siglado con ganadores...")
    
    siglado_new = generar_siglado_new(votos_reagregados, print_debug)
    
    # Guardar siglado
    siglado_path = f"{output_dir}/siglado_{escenario_nombre}.csv"
    siglado_new.to_csv(siglado_path, index=False, encoding='utf-8-sig')
    if print_debug:
        print(f"  ✓ Guardado: {siglado_path}")
    
    if print_debug:
        print("\n" + "="*80)
        print("PIPELINE COMPLETADO")
        print("="*80)
    
    return tabla_puente, votos_reagregados, siglado_new


# ==============================================================================
# EJEMPLO DE USO
# ==============================================================================

if __name__ == '__main__':
    # Esto se llamará desde el script de integración
    pass
