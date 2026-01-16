"""
Genera tabla comparativa 2021 vs 2024 con 4 escenarios
VERSIÓN DINÁMICA: Recalcula todos los valores cuando cambian parámetros
"""
import pandas as pd
from datetime import datetime
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.procesar_diputados_v2 import procesar_diputados_v2

def calcular_escenario_dinamico(anio, mr_seats, rp_seats, pm_seats, 
                               votos_redistribuidos=None, usar_coaliciones=True,
                               aplicar_topes=True, print_debug=False):
    """
    Calcula un escenario completo de forma dinámica
    
    Args:
        anio: Año electoral (2021, 2024)
        mr_seats: Escaños de Mayoría Relativa
        rp_seats: Escaños de Representación Proporcional
        pm_seats: Escaños de Plurinominales Mixtos
        votos_redistribuidos: Dict con porcentajes ajustados por sliders {partido: porcentaje}
        usar_coaliciones: Activar coaliciones
        aplicar_topes: Aplicar topes constitucionales
        print_debug: Imprimir debug
    
    Returns:
        Dict con resultados completos
    """
    # Paths según el año
    path_parquet = f'data/computos_diputados_{anio}.parquet'
    path_siglado = f'data/siglado-diputados-{anio}.csv'
    
    # Partidos según año
    if anio == 2021:
        partidos_base = ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA', 'PES', 'RSP', 'FXM']
    else:  # 2024
        partidos_base = ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA']
    
    # Calcular total de escaños
    max_seats = mr_seats + rp_seats + pm_seats
    
    # Ejecutar motor con votos redistribuidos si aplica
    resultado = procesar_diputados_v2(
        path_parquet=path_parquet,
        path_siglado=path_siglado,
        partidos_base=partidos_base,
        anio=anio,
        max_seats=max_seats,
        mr_seats=mr_seats,
        pm_seats=pm_seats,
        rp_seats=rp_seats,
        aplicar_topes=aplicar_topes,
        umbral=0.03,
        sobrerrepresentacion=8.0,
        max_seats_per_party=300,
        usar_coaliciones=usar_coaliciones,
        votos_redistribuidos=votos_redistribuidos,  # NUEVO: pasar votos ajustados
        seed=42,
        print_debug=print_debug
    )
    
    # Extraer resultados
    mr_dict = resultado['mr']
    pm_dict = resultado.get('pm', {})
    rp_dict = resultado['rp']
    tot_dict = resultado['tot']
    votos_dict = resultado['votos']
    
    # Calcular porcentajes de votos
    total_votos = sum(votos_dict.values())
    votos_pct = {p: (votos_dict[p] / total_votos * 100) if total_votos > 0 else 0 
                 for p in partidos_base}
    
    # Calcular porcentajes de escaños
    escanos_pct = {p: (tot_dict[p] / max_seats * 100) if max_seats > 0 else 0 
                   for p in partidos_base}
    
    # Calcular totales de coaliciones
    if anio == 2021:
        coal_morena = ['MORENA', 'PT', 'PVEM']
        coal_pan = ['PAN', 'PRI', 'PRD']
    else:  # 2024
        coal_morena = ['MORENA', 'PT', 'PVEM']
        coal_pan = ['PAN', 'PRI', 'PRD']
    
    coal_morena_total = sum(tot_dict.get(p, 0) for p in coal_morena)
    coal_pan_total = sum(tot_dict.get(p, 0) for p in coal_pan)
    
    coal_morena_votos = sum(votos_dict.get(p, 0) for p in coal_morena)
    coal_pan_votos = sum(votos_dict.get(p, 0) for p in coal_pan)
    
    # Calcular mayorías
    morena_total = tot_dict.get('MORENA', 0)
    mayoria_simple = max_seats / 2
    mayoria_calificada = (max_seats * 2) / 3
    
    return {
        'partidos': partidos_base,
        'mr': mr_dict,
        'pm': pm_dict,
        'rp': rp_dict,
        'tot': tot_dict,
        'votos': votos_dict,
        'votos_pct': votos_pct,
        'escanos_pct': escanos_pct,
        'total_escanos': max_seats,
        'coalicion_morena': {
            'escanos': coal_morena_total,
            'votos': coal_morena_votos,
            'pct_escanos': (coal_morena_total / max_seats * 100) if max_seats > 0 else 0,
            'pct_votos': (coal_morena_votos / total_votos * 100) if total_votos > 0 else 0,
            'mayoria_simple': coal_morena_total > mayoria_simple,
            'mayoria_calificada': coal_morena_total >= mayoria_calificada
        },
        'coalicion_pan': {
            'escanos': coal_pan_total,
            'votos': coal_pan_votos,
            'pct_escanos': (coal_pan_total / max_seats * 100) if max_seats > 0 else 0,
            'pct_votos': (coal_pan_votos / total_votos * 100) if total_votos > 0 else 0
        },
        'morena_solo': {
            'escanos': morena_total,
            'pct_escanos': (morena_total / max_seats * 100) if max_seats > 0 else 0,
            'mayoria_simple': morena_total > mayoria_simple,
            'mayoria_calificada': morena_total >= mayoria_calificada
        },
        'umbrales': {
            'mayoria_simple': int(mayoria_simple) + 1,
            'mayoria_calificada': int(mayoria_calificada)
        }
    }


def generar_tabla_comparativa_dinamica(escenarios_config, votos_redistribuidos=None):
    """
    Genera tabla comparativa con cálculo dinámico
    
    Args:
        escenarios_config: Lista de configs [{nombre, mr_seats, rp_seats, pm_seats}, ...]
        votos_redistribuidos: Dict con ajustes de sliders {partido: porcentaje}
    
    Returns:
        DataFrame con resultados
    """
    print("=" * 80)
    print("GENERANDO TABLA COMPARATIVA DINÁMICA")
    print("=" * 80)
    
    if votos_redistribuidos:
        print("\nAjustes de votos aplicados:")
        for partido, pct in votos_redistribuidos.items():
            print(f"  {partido}: {pct:.2f}%")
    
    resultados = []
    
    for config in escenarios_config:
        nombre = config['nombre']
        mr_seats = config['mr_seats']
        rp_seats = config['rp_seats']
        pm_seats = config.get('pm_seats', 0)
        
        print(f"\n{'='*80}")
        print(f"Escenario: {nombre}")
        print(f"  MR: {mr_seats}, RP: {rp_seats}, PM: {pm_seats}")
        print(f"{'='*80}")
        
        for anio in [2021, 2024]:
            print(f"\n  Calculando {anio}...")
            
            resultado = calcular_escenario_dinamico(
                anio=anio,
                mr_seats=mr_seats,
                rp_seats=rp_seats,
                pm_seats=pm_seats,
                votos_redistribuidos=votos_redistribuidos,
                usar_coaliciones=True,
                aplicar_topes=True,
                print_debug=False
            )
            
            # Guardar resultados por partido
            for partido in resultado['partidos']:
                resultados.append({
                    'Año': anio,
                    'Escenario': nombre,
                    'Partido': partido,
                    'Votos_%': round(resultado['votos_pct'][partido], 2),
                    'MR': resultado['mr'].get(partido, 0),
                    'PM': resultado['pm'].get(partido, 0),
                    'RP': resultado['rp'].get(partido, 0),
                    'Total': resultado['tot'].get(partido, 0),
                    'Escaños_%': round(resultado['escanos_pct'][partido], 2)
                })
            
            # Guardar resultados de coaliciones
            resultados.append({
                'Año': anio,
                'Escenario': nombre,
                'Partido': 'COALICIÓN MORENA+PT+PVEM',
                'Votos_%': round(resultado['coalicion_morena']['pct_votos'], 2),
                'MR': sum(resultado['mr'].get(p, 0) for p in ['MORENA', 'PT', 'PVEM']),
                'PM': sum(resultado['pm'].get(p, 0) for p in ['MORENA', 'PT', 'PVEM']),
                'RP': sum(resultado['rp'].get(p, 0) for p in ['MORENA', 'PT', 'PVEM']),
                'Total': resultado['coalicion_morena']['escanos'],
                'Escaños_%': round(resultado['coalicion_morena']['pct_escanos'], 2)
            })
            
            print(f"    [OK] MORENA: {resultado['morena_solo']['escanos']} escaños")
            print(f"    [OK] Coalición: {resultado['coalicion_morena']['escanos']} escaños")
    
    # Crear DataFrame
    df = pd.DataFrame(resultados)
    
    # Guardar CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = f'outputs/comparativa_DINAMICA_{timestamp}.csv'
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"\n{'='*80}")
    print("[OK] TABLA GENERADA EXITOSAMENTE")
    print(f"{'='*80}")
    print(f"Archivo: {output_path}")
    print(f"Total filas: {len(df)}")
    
    return output_path


if __name__ == '__main__':
    # Definir escenarios
    escenarios = [
        {'nombre': 'MR 200 - RP 200', 'mr_seats': 200, 'rp_seats': 200, 'pm_seats': 0},
        {'nombre': 'MR 300 - RP 100', 'mr_seats': 300, 'rp_seats': 100, 'pm_seats': 0},
        {'nombre': 'MR 200 - PM 200', 'mr_seats': 200, 'rp_seats': 0, 'pm_seats': 200},
        {'nombre': 'MR 300 - PM 100', 'mr_seats': 300, 'rp_seats': 0, 'pm_seats': 100}
    ]
    
    # EJEMPLO: Ajuste de votos por sliders (comentar si no se usa)
    # votos_ajustados = {
    #     'MORENA': 42.0,
    #     'PAN': 18.0,
    #     'PRI': 12.0,
    #     'PRD': 3.0,
    #     'PVEM': 9.0,
    #     'PT': 6.0,
    #     'MC': 10.0
    # }
    
    # Generar sin ajustes (usa votos reales)
    output = generar_tabla_comparativa_dinamica(escenarios, votos_redistribuidos=None)
    
    print("\n[OK] Generación exitosa")
    sys.exit(0)
    # =========================================================================
    # AGREGAR COLUMNA DE PORCENTAJE DE ESCAÑOS
    # =========================================================================
    print("\nCalculando porcentaje de escaños...")
    
    # Total de escaños siempre es 400
    total_escanos = 400
    df['Escaños_%'] = (df['Total'] / total_escanos * 100).round(2)
    
    print(f"[OK] Columna 'Escaños_%' agregada")
    
    # Guardar CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = f'outputs/comparativa_2021_vs_2024_CORREGIDO_{timestamp}.csv'
    
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"\n{'='*80}")
    print("[OK] TABLA GENERADA EXITOSAMENTE")
    print(f"{'='*80}")
    print(f"Archivo: {output_path}")
    print(f"Total filas: {len(df)}")
    print(f"Años: {sorted(df['Año'].unique())}")
    print(f"Escenarios: {len(escenarios)}")
    print()
    
    # Mostrar preview
    print("Vista previa (primeras 20 filas):")
    print(df.head(20).to_string())
    
    return output_path

if __name__ == '__main__':
    try:
        output = generar_tabla_comparativa()
        print("\n[OK] Generacion exitosa")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

