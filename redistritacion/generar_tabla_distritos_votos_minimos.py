"""
Genera tabla de distritos MR ganados por estado si MORENA obtuviera 
los votos mínimos necesarios calculados con eficiencia 1.1

Usa los porcentajes del CSV votos_minimos_morena.csv:
- 300-100 CON TOPES: 47.0% votos
- 300-100 SIN TOPES: 62.5% votos  
- 200-200 SIN TOPES: 64.0% votos
- 240-160 SIN TOPES: 63.5% votos
- 240-160 CON TOPES: 47.5% votos
"""

import sys
import os
import pandas as pd
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from redistritacion.modulos.reparto_distritos import repartir_distritos_hare
from redistritacion.modulos.distritacion import cargar_secciones_ine

def calcular_distritos_por_estado_con_votos_minimos(mr_total: int, pct_votos: float, eficiencia: float = 1.1):
    """
    Calcula cuántos distritos MR ganaría MORENA por estado si obtuviera 
    el porcentaje de votos mínimos necesario.
    
    Args:
        mr_total: Total de distritos MR (300, 200 o 240)
        pct_votos: Porcentaje de votos nacional (47.0, 62.5, 64.0, 63.5, 47.5)
        eficiencia: Factor de concentración geográfica (default 1.1 = +10%)
    
    Returns:
        DataFrame con columnas: ESTADO, DISTRITOS_TOTALES, DISTRITOS_MORENA
    """
    # Cargar datos reales de 2024
    data_path = Path(__file__).parent.parent / 'data' / 'computos_diputados_2024.parquet'
    computos_dip = pd.read_parquet(data_path)
    
    # Calcular votos por distrito
    votos_por_distrito = computos_dip.groupby('DISTRITO').agg({
        'MORENA': 'sum',
        'VOTOS_TOTALES': 'sum'
    }).reset_index()
    
    # Calcular % MORENA por distrito
    votos_por_distrito['PCT_MORENA'] = (
        votos_por_distrito['MORENA'] / votos_por_distrito['VOTOS_TOTALES'] * 100
    )
    
    # Agregar estado (extraer de DISTRITO: "01 - AGUASCALIENTES")
    votos_por_distrito['ESTADO'] = votos_por_distrito['DISTRITO'].str.split(' - ').str[1]
    
    # Cargar secciones para redistritación por población
    secciones = cargar_secciones_ine()
    poblacion_por_estado = secciones.groupby('ENTIDAD')['POBTOT'].sum().to_dict()
    
    # Repartir distritos según escenario usando método Hare
    asignacion_distritos = repartir_distritos_hare(
        poblacion_estados=poblacion_por_estado,
        n_distritos=mr_total,
        piso_constitucional=2
    )
    
    # Convertir a DataFrame
    distritos_por_estado = pd.DataFrame([
        {'ESTADO': estado.upper(), 'DISTRITOS_TOTALES': num}
        for estado, num in asignacion_distritos.items()
    ])
    
    # Simular votación con el porcentaje mínimo necesario
    # Calculamos cuántos distritos ganaría MORENA si obtuviera pct_votos% con eficiencia
    resultados = []
    
    for _, estado_row in distritos_por_estado.iterrows():
        estado = estado_row['ESTADO']
        total_distritos = estado_row['DISTRITOS_TOTALES']
        
        # Obtener distritos del estado
        distritos_estado = votos_por_distrito[votos_por_distrito['ESTADO'] == estado].copy()
        
        if len(distritos_estado) == 0:
            # Estado sin datos, asumir 0
            resultados.append({
                'ESTADO': estado,
                'DISTRITOS_TOTALES': total_distritos,
                'DISTRITOS_MORENA': 0
            })
            continue
        
        # Calcular nuevo % MORENA ajustado proporcionalmente
        # Si MORENA pasó de 42.49% a pct_votos%, multiplicamos por el factor
        factor_aumento = pct_votos / 42.49
        distritos_estado['PCT_MORENA_AJUSTADO'] = (
            distritos_estado['PCT_MORENA'] * factor_aumento * eficiencia
        )
        
        # Ordenar por PCT_MORENA_AJUSTADO descendente
        distritos_estado_sorted = distritos_estado.sort_values(
            'PCT_MORENA_AJUSTADO', 
            ascending=False
        )
        
        # Tomar los distritos más fuertes del estado
        # hasta completar total_distritos para ese estado
        top_distritos = distritos_estado_sorted.head(total_distritos)
        
        # Contar victorias (donde supera 50% con el ajuste)
        # Umbral conservador: necesita > 50% para ganar
        morena_gana = (top_distritos['PCT_MORENA_AJUSTADO'] > 50).sum()
        
        resultados.append({
            'ESTADO': estado,
            'DISTRITOS_TOTALES': total_distritos,
            'DISTRITOS_MORENA': morena_gana
        })
    
    return pd.DataFrame(resultados)


def generar_tabla_votos_minimos():
    """
    Genera tabla consolidada con distritos ganados por estado en cada escenario
    usando los votos mínimos necesarios calculados.
    """
    # Escenarios con votos mínimos de votos_minimos_morena.csv (eficiencia 1.1)
    escenarios = [
        ('300-100 CON TOPES', 300, 47.0),
        ('300-100 SIN TOPES', 300, 62.5),
        ('200-200 SIN TOPES', 200, 64.0),
        ('240-160 SIN TOPES', 240, 63.5),
        ('240-160 CON TOPES', 240, 47.5)
    ]
    
    print("="*120)
    print("DISTRITOS MR GANADOS POR MORENA POR ESTADO CON VOTOS MÍNIMOS")
    print("Simulación con porcentajes necesarios para cada objetivo (eficiencia +10%)")
    print("="*120)
    
    # Calcular para cada escenario
    resultados_por_escenario = {}
    
    for nombre, mr_total, pct_votos in escenarios:
        print(f"\nCalculando {nombre} con {pct_votos}% de votos...")
        df = calcular_distritos_por_estado_con_votos_minimos(mr_total, pct_votos)
        resultados_por_escenario[nombre] = df
    
    # Crear tabla consolidada
    # Empezar con el primer escenario
    primer_escenario = escenarios[0][0]
    df_consolidado = resultados_por_escenario[primer_escenario][['ESTADO', 'DISTRITOS_TOTALES']].copy()
    df_consolidado.columns = ['ESTADO', 'TOTAL_300']
    
    # Agregar columnas de cada escenario
    for nombre, mr_total, pct_votos in escenarios:
        df_esc = resultados_por_escenario[nombre]
        
        # Columna de total de distritos para este escenario
        col_total = f'TOTAL_{mr_total}'
        if col_total not in df_consolidado.columns:
            df_consolidado = df_consolidado.merge(
                df_esc[['ESTADO', 'DISTRITOS_TOTALES']].rename(
                    columns={'DISTRITOS_TOTALES': col_total}
                ),
                on='ESTADO',
                how='outer'
            )
        
        # Columna de distritos ganados por MORENA
        col_morena = nombre.replace(' ', '_').replace('-', '_')
        df_consolidado = df_consolidado.merge(
            df_esc[['ESTADO', 'DISTRITOS_MORENA']].rename(
                columns={'DISTRITOS_MORENA': col_morena}
            ),
            on='ESTADO',
            how='outer'
        )
    
    # Simplificar: una sola columna de total por configuración
    df_final = pd.DataFrame()
    df_final['ESTADO'] = df_consolidado['ESTADO']
    
    # Para cada escenario, agregar formato "Total / MORENA"
    for nombre, mr_total, _ in escenarios:
        col_total = f'TOTAL_{mr_total}'
        col_morena = nombre.replace(' ', '_').replace('-', '_')
        
        if col_total in df_consolidado.columns:
            df_final[f'TOTAL_{mr_total}'] = df_consolidado[col_total]
        df_final[nombre] = df_consolidado[col_morena]
    
    # Eliminar columnas duplicadas de TOTAL
    # Mantener solo las necesarias: TOTAL_300, TOTAL_200, TOTAL_240
    columnas_finales = ['ESTADO']
    
    # Agregar columnas por escenario
    for nombre, mr_total, pct_votos in escenarios:
        # Primera vez que vemos esta configuración, agregar columna TOTAL
        if f'TOTAL_{mr_total}' not in columnas_finales:
            columnas_finales.append(f'TOTAL_{mr_total}')
        columnas_finales.append(nombre)
    
    # Reorganizar
    df_final = df_final[columnas_finales]
    
    # Calcular totales nacionales
    total_row = {'ESTADO': 'TOTAL NACIONAL'}
    for col in df_final.columns:
        if col != 'ESTADO':
            total_row[col] = df_final[col].sum()
    
    df_final = pd.concat([df_final, pd.DataFrame([total_row])], ignore_index=True)
    
    # Mostrar tabla
    print("\n" + "="*120)
    print("TABLA CONSOLIDADA POR ESTADO Y ESCENARIO")
    print("="*120)
    print("\nFormato: Columnas TOTAL_XXX = distritos del estado | Columnas escenario = distritos MORENA")
    print()
    
    # Header personalizado
    print(f"{'ESTADO':<25}", end='')
    print(f"{'300 MR':>8}", end='')
    print(f"{'47.0%':>8}", end='')
    print(f"{'62.5%':>8}", end='')
    print(f"{'200 MR':>8}", end='')
    print(f"{'64.0%':>8}", end='')
    print(f"{'240 MR':>8}", end='')
    print(f"{'63.5%':>8}", end='')
    print(f"{'47.5%':>8}")
    
    print(f"{'':25}", end='')
    print(f"{'Total':>8}", end='')
    print(f"{'CON T':>8}", end='')
    print(f"{'SIN T':>8}", end='')
    print(f"{'Total':>8}", end='')
    print(f"{'SIN T':>8}", end='')
    print(f"{'Total':>8}", end='')
    print(f"{'SIN T':>8}", end='')
    print(f"{'CON T':>8}")
    print("-"*120)
    
    # Datos
    for _, row in df_final.iterrows():
        print(f"{row['ESTADO']:<25}", end='')
        
        # 300 MR
        print(f"{int(row['TOTAL_300']):>8}", end='')
        print(f"{int(row['300_100_CON_TOPES']):>8}", end='')
        print(f"{int(row['300_100_SIN_TOPES']):>8}", end='')
        
        # 200 MR
        print(f"{int(row['TOTAL_200']):>8}", end='')
        print(f"{int(row['200_200_SIN_TOPES']):>8}", end='')
        
        # 240 MR
        print(f"{int(row['TOTAL_240']):>8}", end='')
        print(f"{int(row['240_160_SIN_TOPES']):>8}", end='')
        print(f"{int(row['240_160_CON_TOPES']):>8}")
    
    print("="*120)
    
    # Guardar CSV
    output_path = 'redistritacion/outputs/distritos_votos_minimos_por_estado.csv'
    df_final.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n✓ Tabla guardada en: {output_path}")
    
    print("\n" + "="*120)
    print("NOTA:")
    print("- Porcentajes mostrados = votos mínimos necesarios con eficiencia +10%")
    print("- CON T = CON TOPES (mayoría simple) | SIN T = SIN TOPES (mayoría calificada)")
    print("- Total = distritos totales del estado en esa configuración")
    print("- Números bajo % = distritos que MORENA ganaría con ese porcentaje de votos")
    print("="*120)


if __name__ == '__main__':
    generar_tabla_votos_minimos()
