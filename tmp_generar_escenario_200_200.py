"""
Genera escenario especial: 400 escaños (200 MR + 200 RP) con datos 2024
SIN cláusula de sobrerrepresentación
Desglose completo por partido (MR + RP)
"""
import pandas as pd
from datetime import datetime
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.procesar_diputados_v2 import procesar_diputados_v2

def generar_escenario_200_200():
    """
    Genera escenario 200 MR + 200 RP con datos 2024 SIN topes
    """
    print("=" * 80)
    print("GENERANDO ESCENARIO ESPECIAL: 200 MR + 200 RP (2024, SIN TOPES)")
    print("=" * 80)
    print()
    
    # Configuración
    path_parquet = 'data/computos_diputados_2024.parquet'
    path_siglado = 'data/siglado-diputados-2024.csv'
    # Solo partidos que participaron en 2024
    partidos_base = ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA']
    
    # Parámetros del escenario
    total_escanos = 400
    mr_seats = 200
    rp_seats = 200
    
    print(f"Configuración:")
    print(f"  Total escaños: {total_escanos}")
    print(f"  MR (Mayoría Relativa): {mr_seats}")
    print(f"  RP (Representación Proporcional): {rp_seats}")
    print(f"  Año: 2024")
    print(f"  Topes constitucionales: DESACTIVADOS")
    print()
    
    # Modo CON coaliciones
    print("Procesando CON coaliciones...")
    resultado_con = procesar_diputados_v2(
        path_parquet=path_parquet,
        path_siglado=path_siglado,
        partidos_base=partidos_base,
        anio=2024,
        max_seats=total_escanos,
        mr_seats=mr_seats,
        rp_seats=rp_seats,
        aplicar_topes=False,  # SIN topes de sobrerrepresentación
        umbral=0.03,
        sobrerrepresentacion=8.0,  # No se aplica porque aplicar_topes=False
        usar_coaliciones=True,
        seed=42,
        print_debug=False
    )
    
    # Modo SIN coaliciones
    print("Procesando SIN coaliciones...")
    resultado_sin = procesar_diputados_v2(
        path_parquet=path_parquet,
        path_siglado=path_siglado,
        partidos_base=partidos_base,
        anio=2024,
        max_seats=total_escanos,
        mr_seats=mr_seats,
        rp_seats=rp_seats,
        aplicar_topes=False,  # SIN topes de sobrerrepresentación
        umbral=0.03,
        sobrerrepresentacion=8.0,
        usar_coaliciones=False,
        seed=42,
        print_debug=False
    )
    
    print()
    print("=" * 80)
    print("RESULTADOS")
    print("=" * 80)
    print()
    
    # Preparar datos para CSV
    resultados = []
    
    for modo, resultado in [('CON', resultado_con), ('SIN', resultado_sin)]:
        print(f"\n{'='*80}")
        print(f"MODO: {modo} coaliciones")
        print(f"{'='*80}")
        print()
        
        # Obtener diccionarios de resultados
        mr_dict = resultado['mr']
        rp_dict = resultado['rp']
        tot_dict = resultado['tot']
        votos_dict = resultado['votos']
        
        # Calcular total de votos para porcentajes
        total_votos = sum(votos_dict.values())
        
        # Header de tabla
        print(f"{'PARTIDO':<10} {'VOTOS %':>10} {'MR':>8} {'RP':>8} {'TOTAL':>8} {'% ESCAÑOS':>10}")
        print("-" * 80)
        
        # Datos por partido
        for partido in partidos_base:
            mr = mr_dict.get(partido, 0)
            rp = rp_dict.get(partido, 0)
            total = tot_dict.get(partido, 0)
            votos = votos_dict.get(partido, 0)
            votos_pct = (votos / total_votos * 100) if total_votos > 0 else 0
            escanos_pct = (total / total_escanos * 100) if total_escanos > 0 else 0
            
            print(f"{partido:<10} {votos_pct:>9.2f}% {mr:>8} {rp:>8} {total:>8} {escanos_pct:>9.2f}%")
            
            # Guardar para CSV
            resultados.append({
                'coalicion': modo,
                'partido': partido,
                'votos': votos,
                'votos_pct': round(votos_pct, 2),
                'mr': mr,
                'rp': rp,
                'total': total,
                'escanos_pct': round(escanos_pct, 2)
            })
        
        # Totales
        total_mr = sum(mr_dict.values())
        total_rp = sum(rp_dict.values())
        total_total = sum(tot_dict.values())
        
        print("-" * 80)
        print(f"{'TOTAL':<10} {'':<10} {total_mr:>8} {total_rp:>8} {total_total:>8} {'100.00':>9}%")
        print()
        
        # Mayorías (solo para MORENA y coalición oficialista)
        morena_total = tot_dict.get('MORENA', 0)
        
        # Coalición oficialista 2024: MORENA + PT + PVEM
        coalicion_partidos = ['MORENA', 'PT', 'PVEM']
        coalicion_total = sum(tot_dict.get(p, 0) for p in coalicion_partidos)
        
        print(f"Mayorías:")
        print(f"  MORENA: {morena_total} escaños ({morena_total/total_escanos*100:.1f}%)")
        print(f"    Simple (>50%): {'SÍ' if morena_total > total_escanos/2 else 'NO'}")
        print(f"    Calificada (>=66.67%): {'SÍ' if morena_total >= (total_escanos * 2/3) else 'NO'}")
        print()
        print(f"  Coalición MORENA+PT+PVEM: {coalicion_total} escaños ({coalicion_total/total_escanos*100:.1f}%)")
        print(f"    Simple (>50%): {'SÍ' if coalicion_total > total_escanos/2 else 'NO'}")
        print(f"    Calificada (>=66.67%): {'SÍ' if coalicion_total >= (total_escanos * 2/3) else 'NO'}")
    
    # Guardar CSV
    df = pd.DataFrame(resultados)
    
    # Reordenar columnas
    df = df[['coalicion', 'partido', 'votos', 'votos_pct', 'mr', 'rp', 'total', 'escanos_pct']]
    
    # Generar nombre de archivo con timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = f'outputs/escenario_200MR_200RP_2024_SIN_TOPES_{timestamp}.csv'
    
    df.to_csv(output_path, index=False)
    
    print()
    print("=" * 80)
    print(f"✓ Archivo generado: {output_path}")
    print("=" * 80)
    print()
    print(f"Total filas: {len(df)}")
    print(f"Partidos: {len(partidos_base)}")
    print(f"Modos: CON y SIN coaliciones")
    print()
    
    return output_path

if __name__ == '__main__':
    try:
        output = generar_escenario_200_200()
        print("\n✓ Generación exitosa")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
