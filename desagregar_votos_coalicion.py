"""
CONTRAFACTUAL SERIO: Desagregar votos de coalición a partidos individuales
usando datos históricos 2021 como base para proporciones
"""
import pandas as pd
import numpy as np

def desagregar_votos_coalicion(df_2024, df_2021_referencia, coalicion_partidos=['MORENA', 'PT', 'PVEM']):
    """
    Desagrega votos de coalición 2024 usando proporciones de 2021 por distrito
    
    Lógica:
    - En 2021, MORENA+PT+PVEM también fueron en coalición, pero tenemos sus votos individuales
    - Usamos las proporciones relativas de 2021 para repartir los votos 2024
    - Si no hay datos 2021 para un distrito, usamos promedio estatal
    - Si no hay datos estatales, usamos promedio nacional
    """
    
    df_resultado = df_2024.copy()
    
    # Calcular proporciones nacionales 2021 como fallback
    votos_nac_2021 = {}
    for p in coalicion_partidos:
        if p in df_2021_referencia.columns:
            votos_nac_2021[p] = df_2021_referencia[p].sum()
    
    total_coalicion_2021 = sum(votos_nac_2021.values())
    prop_nacional = {p: votos_nac_2021.get(p, 0) / total_coalicion_2021 
                     for p in coalicion_partidos}
    
    print(f"Proporciones nacionales 2021 (fallback):")
    for p in coalicion_partidos:
        print(f"  {p}: {prop_nacional[p]*100:.2f}%")
    
    # Calcular proporciones por entidad 2021
    prop_por_entidad = {}
    if 'ENTIDAD' in df_2021_referencia.columns:
        for entidad in df_2021_referencia['ENTIDAD'].unique():
            df_ent = df_2021_referencia[df_2021_referencia['ENTIDAD'] == entidad]
            votos_ent = {}
            for p in coalicion_partidos:
                if p in df_ent.columns:
                    votos_ent[p] = df_ent[p].sum()
            total_ent = sum(votos_ent.values())
            if total_ent > 0:
                prop_por_entidad[entidad] = {p: votos_ent.get(p, 0) / total_ent 
                                              for p in coalicion_partidos}
    
    # Desagregar distrito por distrito
    print(f"\nDesagregando votos de coalición 2024...")
    distritos_procesados = 0
    distritos_con_datos_2021 = 0
    distritos_fallback_entidad = 0
    distritos_fallback_nacional = 0
    
    # Columnas de coalición en 2024
    col_coalicion = None
    for col_candidata in ['MORENA_PT_PVEM', 'MORENA+PT+PVEM', 'COALICION']:
        if col_candidata in df_2024.columns:
            col_coalicion = col_candidata
            break
    
    if not col_coalicion:
        print("  [WARN] No se encontró columna de coalición, usando votos individuales 2024")
        return df_resultado
    
    for idx, row in df_resultado.iterrows():
        entidad = row.get('ENTIDAD', '')
        distrito = row.get('DISTRITO', 0)
        votos_coal = row.get(col_coalicion, 0)
        
        if votos_coal <= 0:
            continue
        
        # Buscar datos 2021 para este distrito
        proporciones = None
        
        # 1. Intentar datos distrito específico 2021
        if 'ENTIDAD' in df_2021_referencia.columns and 'DISTRITO' in df_2021_referencia.columns:
            df_dist_2021 = df_2021_referencia[
                (df_2021_referencia['ENTIDAD'] == entidad) & 
                (df_2021_referencia['DISTRITO'] == distrito)
            ]
            
            if len(df_dist_2021) > 0:
                votos_dist = {}
                for p in coalicion_partidos:
                    if p in df_dist_2021.columns:
                        votos_dist[p] = df_dist_2021[p].sum()
                
                total_dist = sum(votos_dist.values())
                if total_dist > 0:
                    proporciones = {p: votos_dist.get(p, 0) / total_dist 
                                   for p in coalicion_partidos}
                    distritos_con_datos_2021 += 1
        
        # 2. Fallback: proporciones estatales
        if proporciones is None and entidad in prop_por_entidad:
            proporciones = prop_por_entidad[entidad]
            distritos_fallback_entidad += 1
        
        # 3. Fallback final: proporciones nacionales
        if proporciones is None:
            proporciones = prop_nacional
            distritos_fallback_nacional += 1
        
        # Desagregar votos
        for p in coalicion_partidos:
            prop = proporciones.get(p, 0)
            votos_desagregados = votos_coal * prop
            df_resultado.at[idx, p] = votos_desagregados
        
        distritos_procesados += 1
    
    print(f"  Distritos procesados: {distritos_procesados}")
    print(f"  Con datos distrito 2021: {distritos_con_datos_2021}")
    print(f"  Fallback entidad: {distritos_fallback_entidad}")
    print(f"  Fallback nacional: {distritos_fallback_nacional}")
    
    return df_resultado


# ==== PRUEBA ====
if __name__ == '__main__':
    print("="*80)
    print("TEST: Desagregación de votos de coalición")
    print("="*80)
    
    # Cargar datos
    df_2024 = pd.read_parquet('data/computos_diputados_2024.parquet')
    df_2021 = pd.read_parquet('data/computos_diputados_2021.parquet')
    
    # Normalizar columnas
    df_2024.columns = [c.upper().strip() for c in df_2024.columns]
    df_2021.columns = [c.upper().strip() for c in df_2021.columns]
    
    print("\n1. VOTOS ORIGINALES 2024 (con coalición):")
    print("-" * 60)
    for p in ['MORENA', 'PT', 'PVEM']:
        if p in df_2024.columns:
            votos = df_2024[p].sum()
            print(f"  {p:10} {votos:>15,.0f} votos")
    
    # Buscar columna de coalición
    col_coal = None
    for candidata in ['MORENA_PT_PVEM', 'MORENA+PT+PVEM', 'COALICION']:
        if candidata in df_2024.columns:
            col_coal = candidata
            break
    
    if col_coal:
        votos_coal = df_2024[col_coal].sum()
        print(f"  {col_coal:10} {votos_coal:>15,.0f} votos")
    
    print("\n2. VOTOS REFERENCIA 2021:")
    print("-" * 60)
    for p in ['MORENA', 'PT', 'PVEM']:
        if p in df_2021.columns:
            votos = df_2021[p].sum()
            print(f"  {p:10} {votos:>15,.0f} votos")
    
    # Desagregar
    print("\n3. DESAGREGACIÓN:")
    print("=" * 60)
    df_desagregado = desagregar_votos_coalicion(df_2024, df_2021)
    
    print("\n4. VOTOS DESAGREGADOS 2024:")
    print("-" * 60)
    for p in ['MORENA', 'PT', 'PVEM']:
        if p in df_desagregado.columns:
            votos = df_desagregado[p].sum()
            print(f"  {p:10} {votos:>15,.0f} votos")
    
    total_desagregado = sum(df_desagregado[p].sum() for p in ['MORENA', 'PT', 'PVEM'] 
                           if p in df_desagregado.columns)
    print(f"  {'TOTAL':10} {total_desagregado:>15,.0f} votos")
    
    if col_coal:
        diferencia = votos_coal - total_desagregado
        print(f"\n  Diferencia vs coalición original: {diferencia:+,.0f} votos")
        print(f"  Error relativo: {abs(diferencia)/votos_coal*100:.2f}%")
    
    # Exportar para inspección
    output_path = 'outputs/votos_desagregados_2024.parquet'
    df_desagregado.to_parquet(output_path)
    print(f"\n5. Datos desagregados exportados a: {output_path}")
