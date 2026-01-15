"""
Genera tabla SIMPLE por estado con distritos ganados por MORENA.

Formato:
- Columna 1: Estado
- Columna 2: Total distritos (300 MR)
- Columna 3: Distritos MORENA con 47.0% (300-100 CON TOPES)
- Columna 4: Distritos MORENA con 62.5% (300-100 SIN TOPES)
- Columna 5: Total distritos (200 MR)
- Columna 6: Distritos MORENA con 64.0% (200-200 SIN TOPES)
- Columna 7: Total distritos (240 MR)
- Columna 8: Distritos MORENA con 63.5% (240-160 SIN TOPES)
- Columna 9: Distritos MORENA con 47.5% (240-160 CON TOPES)

Usa los datos ya calculados del script generar_tabla_distritos_estados.py
"""

import sys
import pandas as pd
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from redistritacion.modulos.reparto_distritos import repartir_distritos_hare
from redistritacion.modulos.distritacion import cargar_secciones_ine


def calcular_distritos_morena_por_estado(escenario_nombre, mr_total, pct_votos_morena, eficiencia=1.1):
    """
    Calcula cuántos distritos ganaría MORENA por estado en un escenario.
    
    Args:
        escenario_nombre: Nombre del escenario
        mr_total: Total de distritos MR en el escenario
        pct_votos_morena: % de votos de MORENA
        eficiencia: Factor de conversión votos→distritos (1.1 = +10% por geografía)
    
    Returns:
        DataFrame con distribución por estado
    """
    # Cargar secciones para población
    secciones = cargar_secciones_ine()
    
    # Calcular población por estado
    poblacion_por_estado = secciones.groupby('ENTIDAD')['POBTOT'].sum().to_dict()
    
    # Repartir distritos usando método Hare
    asignacion_distritos = repartir_distritos_hare(
        poblacion_estados=poblacion_por_estado,
        n_distritos=mr_total,
        piso_constitucional=2
    )
    
    # Cargar votos reales de MORENA 2024 por estado
    df_votos = pd.read_parquet('data/computos_diputados_2024.parquet')
    
    # Mapeo de nombres de estados
    estado_nombres = {
        1: 'AGUASCALIENTES',
        2: 'BAJA CALIFORNIA',
        3: 'BAJA CALIFORNIA SUR',
        4: 'CAMPECHE',
        5: 'CHIAPAS',
        6: 'CHIHUAHUA',
        7: 'COAHUILA',
        8: 'COLIMA',
        9: 'CIUDAD DE MEXICO',
        10: 'DURANGO',
        11: 'GUANAJUATO',
        12: 'GUERRERO',
        13: 'HIDALGO',
        14: 'JALISCO',
        15: 'MEXICO',
        16: 'MICHOACAN',
        17: 'MORELOS',
        18: 'NAYARIT',
        19: 'NUEVO LEON',
        20: 'OAXACA',
        21: 'PUEBLA',
        22: 'QUERETARO',
        23: 'QUINTANA ROO',
        24: 'SAN LUIS POTOSI',
        25: 'SINALOA',
        26: 'SONORA',
        27: 'TABASCO',
        28: 'TAMAULIPAS',
        29: 'TLAXCALA',
        30: 'VERACRUZ',
        31: 'YUCATAN',
        32: 'ZACATECAS'
    }
    
    # Normalizar nombres en df_votos
    df_votos['ENTIDAD_NOMBRE'] = df_votos['ENTIDAD'].str.strip().str.upper()
    
    # Calcular factor de escalamiento: de 42.49% real a pct_votos_morena necesario
    factor_escala = pct_votos_morena / 42.49
    
    # Calcular votación de MORENA por estado
    votos_por_estado = []
    
    for entidad_id, nombre in estado_nombres.items():
        # Buscar en df_votos
        df_estado = df_votos[df_votos['ENTIDAD_NOMBRE'] == nombre]
        
        if len(df_estado) == 0:
            # Probar variantes del nombre
            df_estado = df_votos[df_votos['ENTIDAD_NOMBRE'].str.contains(nombre.split()[0], na=False)]
        
        if len(df_estado) > 0:
            votos_morena = df_estado['MORENA'].sum()
            votos_totales = df_estado['TOTAL_BOLETAS'].sum()
            pct_morena_estado_real = (votos_morena / votos_totales * 100) if votos_totales > 0 else 0
            # Escalar proporcionalmente
            pct_morena_estado = pct_morena_estado_real * factor_escala
        else:
            pct_morena_estado = pct_votos_morena  # Default nacional
        
        distritos_totales = asignacion_distritos.get(entidad_id, 0)
        
        # Calcular distritos ganados con eficiencia
        # pct_morena_estado × eficiencia × distritos_totales / 100
        distritos_ganados = int(distritos_totales * (pct_morena_estado / 100) * eficiencia)
        distritos_ganados = min(distritos_ganados, distritos_totales)  # No puede ganar más del total
        
        votos_por_estado.append({
            'ENTIDAD_ID': entidad_id,
            'ESTADO': nombre,
            'DISTRITOS_TOTALES': distritos_totales,
            'DISTRITOS_MORENA': distritos_ganados
        })
    
    df = pd.DataFrame(votos_por_estado)
    df = df[df['DISTRITOS_TOTALES'] > 0]  # Solo estados con distritos
    df = df.sort_values('ENTIDAD_ID')
    
    return df


def generar_tabla_simple():
    """
    Genera tabla simple: Estado | Total | MORENA por escenario
    Usa los votos mínimos REALES del CSV con redistritación.
    """
    # Cargar votos mínimos del CSV (con redistritación real)
    votos_minimos_df = pd.read_csv('redistritacion/outputs/votos_minimos_morena.csv')
    
    # Filtrar eficiencia 1.1 (realista)
    votos_ef11 = votos_minimos_df[votos_minimos_df['eficiencia_val'] == 1.1]
    
    # Extraer porcentajes para cada escenario
    # Para CON TOPES usamos mayoría simple, para SIN TOPES usamos mayoría calificada
    escenarios = []
    
    for _, row in votos_ef11.iterrows():
        nombre = row['escenario']
        mr_total = int(row['mr_total'])
        
        # Determinar qué mayoría usar
        if 'CON TOPES' in nombre:
            # CON TOPES: mayoría simple (calificada imposible por tope 8%)
            pct_votos = row['mayoria_simple_votos']
        else:
            # SIN TOPES: mayoría calificada (objetivo máximo)
            pct_votos = row['mayoria_calificada_votos']
        
        escenarios.append((nombre, mr_total, pct_votos))
    
    print("="*160)
    print("DISTRITOS MR GANADOS POR MORENA POR ESTADO CON VOTOS MÍNIMOS (Redistritación Real + Eficiencia +10%)")
    print("="*160)
    print("\nUsando votos mínimos del CSV votos_minimos_morena.csv")
    print("  - CON TOPES: Objetivo mayoría SIMPLE (201 escaños)")
    print("  - SIN TOPES: Objetivo mayoría CALIFICADA (267 escaños)")
    print("\nCalculando escenarios...")
    
    # Calcular cada escenario
    datos_escenarios = {}
    for nombre, mr_total, pct_votos in escenarios:
        print(f"  {nombre}: {pct_votos:.1f}% votos...")
        df = calcular_distritos_morena_por_estado(nombre, mr_total, pct_votos)
        datos_escenarios[nombre] = df
    
    # Construir tabla consolidada
    # Usar el primer escenario como base
    df_final = datos_escenarios['300-100 CON TOPES'][['ESTADO']].copy()
    
    # Agregar columnas por configuración de MR
    # Para 300 MR: total + CON TOPES + SIN TOPES
    df_300_con = datos_escenarios['300-100 CON TOPES']
    df_300_sin = datos_escenarios['300-100 SIN TOPES']
    
    df_final = df_final.merge(
        df_300_con[['ESTADO', 'DISTRITOS_TOTALES']].rename(
            columns={'DISTRITOS_TOTALES': 'TOTAL_300'}
        ),
        on='ESTADO',
        how='left'
    )
    df_final = df_final.merge(
        df_300_con[['ESTADO', 'DISTRITOS_MORENA']].rename(
            columns={'DISTRITOS_MORENA': 'MORENA_300_CON'}
        ),
        on='ESTADO',
        how='left'
    )
    df_final = df_final.merge(
        df_300_sin[['ESTADO', 'DISTRITOS_MORENA']].rename(
            columns={'DISTRITOS_MORENA': 'MORENA_300_SIN'}
        ),
        on='ESTADO',
        how='left'
    )
    
    # Para 200 MR: total + SIN TOPES
    df_200 = datos_escenarios['200-200 SIN TOPES']
    df_final = df_final.merge(
        df_200[['ESTADO', 'DISTRITOS_TOTALES']].rename(
            columns={'DISTRITOS_TOTALES': 'TOTAL_200'}
        ),
        on='ESTADO',
        how='left'
    )
    df_final = df_final.merge(
        df_200[['ESTADO', 'DISTRITOS_MORENA']].rename(
            columns={'DISTRITOS_MORENA': 'MORENA_200_SIN'}
        ),
        on='ESTADO',
        how='left'
    )
    
    # Para 240 MR: total + SIN TOPES + CON TOPES
    df_240_sin = datos_escenarios['240-160 SIN TOPES']
    df_240_con = datos_escenarios['240-160 CON TOPES']
    
    df_final = df_final.merge(
        df_240_sin[['ESTADO', 'DISTRITOS_TOTALES']].rename(
            columns={'DISTRITOS_TOTALES': 'TOTAL_240'}
        ),
        on='ESTADO',
        how='left'
    )
    df_final = df_final.merge(
        df_240_sin[['ESTADO', 'DISTRITOS_MORENA']].rename(
            columns={'DISTRITOS_MORENA': 'MORENA_240_SIN'}
        ),
        on='ESTADO',
        how='left'
    )
    df_final = df_final.merge(
        df_240_con[['ESTADO', 'DISTRITOS_MORENA']].rename(
            columns={'DISTRITOS_MORENA': 'MORENA_240_CON'}
        ),
        on='ESTADO',
        how='left'
    )
    
    # Rellenar NaN con 0
    df_final = df_final.fillna(0).astype({
        'TOTAL_300': int,
        'MORENA_300_CON': int,
        'MORENA_300_SIN': int,
        'TOTAL_200': int,
        'MORENA_200_SIN': int,
        'TOTAL_240': int,
        'MORENA_240_SIN': int,
        'MORENA_240_CON': int
    })
    
    # Calcular totales
    total_row = {'ESTADO': 'TOTAL NACIONAL'}
    for col in df_final.columns:
        if col != 'ESTADO':
            total_row[col] = df_final[col].sum()
    
    df_final = pd.concat([df_final, pd.DataFrame([total_row])], ignore_index=True)
    
    # Mostrar tabla
    print("\n" + "="*160)
    print("TABLA POR ESTADO Y ESCENARIO")
    print("="*160)
    print()
    
    # Header
    print(f"{'ESTADO':<25}", end='')
    print(f"{'300 MR':>10}", end='')
    print(f"{'50.0%':>10}", end='')
    print(f"{'66.5%':>10}", end='')
    print(f"{'200 MR':>10}", end='')
    print(f"{'67.0%':>10}", end='')
    print(f"{'240 MR':>10}", end='')
    print(f"{'67.0%':>10}", end='')
    print(f"{'52.0%':>10}")
    
    print(f"{'':25}", end='')
    print(f"{'Total':>10}", end='')
    print(f"{'CON T':>10}", end='')
    print(f"{'SIN T':>10}", end='')
    print(f"{'Total':>10}", end='')
    print(f"{'SIN T':>10}", end='')
    print(f"{'Total':>10}", end='')
    print(f"{'SIN T':>10}", end='')
    print(f"{'CON T':>10}")
    print("-"*160)
    
    # Datos
    for _, row in df_final.iterrows():
        estado = row['ESTADO']
        if len(estado) > 24:
            estado = estado[:24]
        
        print(f"{estado:<25}", end='')
        print(f"{row['TOTAL_300']:>10}", end='')
        print(f"{row['MORENA_300_CON']:>10}", end='')
        print(f"{row['MORENA_300_SIN']:>10}", end='')
        print(f"{row['TOTAL_200']:>10}", end='')
        print(f"{row['MORENA_200_SIN']:>10}", end='')
        print(f"{row['TOTAL_240']:>10}", end='')
        print(f"{row['MORENA_240_SIN']:>10}", end='')
        print(f"{row['MORENA_240_CON']:>10}")
    
    print("="*160)
    
    # Guardar CSV
    output_path = 'redistritacion/outputs/tabla_simple_distritos_votos_minimos.csv'
    df_final.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n✓ Tabla guardada en: {output_path}")
    
    print("\n" + "="*160)
    print("LEYENDA:")
    print("  300 MR = Configuración con 300 distritos MR + 100 RP")
    print("  200 MR = Configuración con 200 distritos MR + 200 RP")
    print("  240 MR = Configuración con 240 distritos MR + 160 RP")
    print()
    print("  VOTOS MÍNIMOS NECESARIOS (con redistritación REAL y eficiencia +10%):")
    print("    50.0% = Mayoría SIMPLE con 300 MR CON TOPES (153 MR + 50 RP = 203 escaños)")
    print("    66.5% = Mayoría CALIFICADA con 300 MR SIN TOPES (201 MR + 66 RP = 267 escaños)")
    print("    67.0% = Mayoría CALIFICADA con 200 MR SIN TOPES (134 MR + 134 RP = 268 escaños)")
    print("    67.0% = Mayoría CALIFICADA con 240 MR SIN TOPES (161 MR + 107 RP = 268 escaños)")
    print("    52.0% = Mayoría SIMPLE con 240 MR CON TOPES (118 MR + 83 RP = 201 escaños)")
    print()
    print("  CON T = CON TOPES (límite 8%) | SIN T = SIN TOPES")
    print("  Total = Distritos totales del estado | Números = Distritos que gana MORENA")
    print()
    print("  ⚠️  NOTA: Estos cálculos usan REDISTRITACIÓN REAL por población (método Hare)")
    print("     Los votos mínimos son MÁS ALTOS que con proporcionalidad simple.")
    print("="*160)


if __name__ == '__main__':
    generar_tabla_simple()
