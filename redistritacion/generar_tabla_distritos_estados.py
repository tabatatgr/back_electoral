"""
Genera tabla de distritos ganados por MORENA por estado en cada escenario.

Usa:
1. Redistritación real de cada escenario (outputs de generar_escenarios_comparativos.py)
2. Votación real de MORENA 2024
3. Calcula proporcionalmente cuántos distritos ganaría por estado

Escenarios:
- 300-100 (actual)
- 200-200
- 240-160
"""

import sys
import pandas as pd
from pathlib import Path

# Agregar path del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

from redistritacion.modulos.reparto_distritos import repartir_distritos_hare
from redistritacion.modulos.distritacion import cargar_secciones_ine


def calcular_distritos_morena_por_estado(escenario_nombre, mr_total, pct_votos_morena=42.49, eficiencia=1.1):
    """
    Calcula cuántos distritos ganaría MORENA por estado en un escenario.
    
    Args:
        escenario_nombre: Nombre del escenario
        mr_total: Total de distritos MR en el escenario
        pct_votos_morena: % de votos de MORENA (default: 42.49% real 2024)
        eficiencia: Factor de conversión votos→distritos (1.1 = +10% por geografía)
    
    Returns:
        DataFrame con distribución por estado
    """
    # Cargar secciones para población
    secciones = cargar_secciones_ine()
    
    # Calcular población por estado
    poblacion_por_estado = secciones.groupby('ENTIDAD')['POBTOT'].sum().to_dict()
    
    # Repartir distritos usando método Hare (igual que en generar_escenarios_comparativos.py)
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
            pct_morena_estado = (votos_morena / votos_totales * 100) if votos_totales > 0 else 0
        else:
            pct_morena_estado = pct_votos_morena  # Default nacional
        
        distritos_totales = asignacion_distritos.get(entidad_id, 0)
        
        # Calcular distritos ganados con eficiencia
        # pct_morena_estado × eficiencia × distritos_totales
        distritos_ganados = int(distritos_totales * (pct_morena_estado / 100) * eficiencia)
        distritos_ganados = min(distritos_ganados, distritos_totales)  # No puede ganar más del total
        
        votos_por_estado.append({
            'ENTIDAD_ID': entidad_id,
            'ESTADO': nombre,
            'DISTRITOS_TOTALES': distritos_totales,
            'PCT_MORENA': pct_morena_estado,
            'DISTRITOS_MORENA': distritos_ganados,
            'PCT_DISTRITOS': (distritos_ganados / distritos_totales * 100) if distritos_totales > 0 else 0
        })
    
    df = pd.DataFrame(votos_por_estado)
    df = df[df['DISTRITOS_TOTALES'] > 0]  # Solo estados con distritos
    df = df.sort_values('ENTIDAD_ID')
    
    return df


def generar_tabla_comparativa_estados():
    """
    Genera tabla comparativa de distritos ganados por MORENA por estado en cada escenario.
    Usa objetivos calculados con eficiencia 1.1 (+10% geográfica) del análisis de votos mínimos.
    """
    
    # Escenarios con objetivos REALISTAS (eficiencia 1.1 del CSV votos_minimos_morena.csv)
    # CON TOPES: Mayoría simple (calificada imposible matemáticamente con tope 8%)
    # SIN TOPES: Mayoría calificada (objetivo de reformas constitucionales)
    escenarios = [
        # (nombre, mr_total, tipo_mayoria, mr_necesarios, rp_necesarios, pct_votos_necesario)
        ('300-100 CON TOPES', 300, 'SIMPLE', 155, 47, 47.0),      # 155 MR para 47% votos → 201 total
        ('300-100 SIN TOPES', 300, 'CALIFICADA', 206, 62, 62.5),  # 206 MR para 62.5% votos → 267 total
        ('200-200 SIN TOPES', 200, 'CALIFICADA', 140, 128, 64.0), # 140 MR para 64% votos → 267 total
        ('240-160 SIN TOPES', 240, 'CALIFICADA', 167, 101, 63.5), # 167 MR para 63.5% votos → 267 total
        ('240-160 CON TOPES', 240, 'SIMPLE', 125, 76, 47.5)       # 125 MR para 47.5% votos → 201 total
    ]
    
    print("="*150)
    print("DISTRIBUCIÓN DE DISTRITOS MR GANADOS POR MORENA POR ESTADO")
    print("Votación real 2024: 42.49% | Eficiencia geográfica: +10% (realista)")
    print("="*150)
    
    # Mostrar objetivos de mayoría
    print("\nOBJETIVOS DE MAYORÍA CON VOTOS MÍNIMOS (Eficiencia +10%):")
    print("-"*150)
    print(f"{'Escenario':<25} {'Tipo':<12} {'Votos %':<10} {'MR Nec.':<10} {'RP Nec.':<10} {'Total':<10}")
    print("-"*150)
    for nombre, mr_total, tipo_mayoria, mr_necesarios, rp_necesarios, pct_votos in escenarios:
        total_objetivo = 201 if tipo_mayoria == 'SIMPLE' else 267
        print(f"{nombre:<25} {tipo_mayoria:<12} {pct_votos:<10.1f} {mr_necesarios:<10} {rp_necesarios:<10} {total_objetivo:<10}")
    print("="*150)
    
    # Calcular para cada escenario
    todos_df = {}
    
    for nombre, mr_total, tipo_mayoria, mr_necesarios, rp_necesarios, pct_votos in escenarios:
        print(f"\nCalculando {nombre}...")
        df = calcular_distritos_morena_por_estado(nombre, mr_total)
        todos_df[nombre] = df
    
    # Crear tabla pivote combinada
    print("\n" + "="*140)
    print("TABLA COMPARATIVA POR ESTADO")
    print("="*140)
    
    # Obtener lista de estados (usar el primer escenario)
    primer_escenario = escenarios[0][0]
    df_base = todos_df[primer_escenario]
    
    # Header
    print(f"\n{'ESTADO':<25} ", end='')
    for nombre, _, _, _, _, _ in escenarios:
        print(f"{nombre:>18} ", end='')
    print()
    print(f"{'':25} ", end='')
    for nombre, mr_total, tipo_mayoria, mr_necesarios, _, _ in escenarios:
        print(f"{'Tot/Mor (Obj)':>18} ", end='')
    print()
    print("-"*140)
    
    # Por cada estado
    totales_por_escenario = {nombre: {'total': 0, 'morena': 0} for nombre, _, _, _, _, _ in escenarios}
    
    for _, row in df_base.iterrows():
        estado = row['ESTADO']
        print(f"{estado:<25} ", end='')
        
        for nombre, _, tipo_mayoria, mr_necesarios, _, _ in escenarios:
            df_esc = todos_df[nombre]
            fila = df_esc[df_esc['ESTADO'] == estado]
            
            if len(fila) > 0:
                total = int(fila['DISTRITOS_TOTALES'].values[0])
                morena = int(fila['DISTRITOS_MORENA'].values[0])
                pct = fila['PCT_DISTRITOS'].values[0]
                
                totales_por_escenario[nombre]['total'] += total
                totales_por_escenario[nombre]['morena'] += morena
                
                # Mostrar con indicador de cumplimiento
                print(f"{total:>2}/{morena:>2} ", end='')
            else:
                print(f"{'N/A':>18} ", end='')
        
        print()
    
    # Totales
    print("-"*140)
    print(f"{'TOTAL NACIONAL':<25} ", end='')
    for nombre, mr_total, tipo_mayoria, mr_necesarios, _, _ in escenarios:
        total = totales_por_escenario[nombre]['total']
        morena = totales_por_escenario[nombre]['morena']
        pct = (morena / total * 100) if total > 0 else 0
        
        # Indicador de cumplimiento
        cumple = "✓" if morena >= mr_necesarios else "✗"
        print(f"{total:>2}/{morena:>2} ({mr_necesarios:>3}){cumple} ", end='')
    print()
    print(f"{'(Objetivo MR necesario)':<25} ", end='')
    for nombre, _, tipo_mayoria, mr_necesarios, _, _ in escenarios:
        total = totales_por_escenario[nombre]['total']
        morena = totales_por_escenario[nombre]['morena']
        faltante = max(0, mr_necesarios - morena)
        print(f"{'Faltan: ' + str(faltante):>18} ", end='')
    print()
    print("="*140)
    
    # Guardar CSV detallado
    print("\n" + "="*140)
    print("GUARDANDO RESULTADOS DETALLADOS")
    print("="*140)
    
    for nombre, _, _, _, _, _ in escenarios:
        df = todos_df[nombre]
        output_path = f'redistritacion/outputs/distritos_morena_{nombre.replace(" ", "_").replace("-", "_")}.csv'
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"✓ {nombre}: {output_path}")
    
    # Crear tabla pivote consolidada
    dfs_consolidados = []
    
    for nombre, _, tipo_mayoria, mr_necesarios, rp_necesarios, pct_votos in escenarios:
        df = todos_df[nombre].copy()
        df['ESCENARIO'] = nombre
        df['TIPO_MAYORIA'] = tipo_mayoria
        df['MR_NECESARIOS'] = mr_necesarios
        df['RP_NECESARIOS'] = rp_necesarios
        df['PCT_VOTOS_NECESARIO'] = pct_votos
        dfs_consolidados.append(df)
    
    df_consolidado = pd.concat(dfs_consolidados, ignore_index=True)
    output_consolidado = 'redistritacion/outputs/distritos_morena_comparativa.csv'
    df_consolidado.to_csv(output_consolidado, index=False, encoding='utf-8-sig')
    print(f"✓ Consolidado: {output_consolidado}")
    
    # Resumen
    print("\n" + "="*140)
    print("RESUMEN POR ESCENARIO")
    print("="*140)
    
    for nombre, mr_total, tipo_mayoria, mr_necesarios, rp_necesarios, pct_votos in escenarios:
        total = totales_por_escenario[nombre]['total']
        morena = totales_por_escenario[nombre]['morena']
        otros = total - morena
        pct_morena = (morena / total * 100) if total > 0 else 0
        faltante = max(0, mr_necesarios - morena)
        
        # Calcular escaños totales
        total_escanos = mr_total + (100 if mr_total == 300 else 200 if mr_total == 200 else 160)
        mayoria_total = 201 if tipo_mayoria == 'SIMPLE' else 267
        rp_disponibles = total_escanos - mr_total
        rp_necesarios = mayoria_total - mr_necesarios
        
        print(f"\n{nombre}:")
        print(f"  Objetivo: Mayoría {tipo_mayoria} = {mayoria_total} escaños totales")
        print(f"  Necesita: {mr_necesarios} MR + {rp_necesarios} RP")
        print(f"  Total distritos MR: {total}")
        print(f"  MORENA ganaría: {morena} ({pct_morena:.1f}%)")
        if morena >= mr_necesarios:
            print(f"  ✓ CUMPLE objetivo MR (sobran {morena - mr_necesarios})")
        else:
            print(f"  ✗ NO CUMPLE objetivo MR (faltan {faltante})")
        print(f"  Otros partidos: {otros} ({100-pct_morena:.1f}%)")
    
    print("\n" + "="*140)
    print("NOTA: Estimación con eficiencia geográfica +10% (concentración favorable)")
    print("Votación base: 42.49% (MORENA 2024 sin coalición)")
    print("CON TOPES: Solo mayoría simple posible (tope 8% limita a ~201 escaños)")
    print("SIN TOPES: Mayoría calificada teórica para reformas constitucionales (~267 escaños)")
    print("="*140)


if __name__ == '__main__':
    generar_tabla_comparativa_estados()
