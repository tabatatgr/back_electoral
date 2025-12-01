"""
Test: Verificar que el límite de sobrerrepresentación del 8% se aplica 
correctamente en TODOS los sistemas electorales (MR puro, RP puro, y mixto)
"""
import sys
import os
import pandas as pd
import numpy as np

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.procesar_diputados_v2 import procesar_diputados_v2

def test_limite_sobrerrepresentacion():
    """
    Prueba que el límite de 8% sobrerrepresentación se aplique en:
    1. Sistema MR puro (100% MR, 0% RP)
    2. Sistema RP puro (0% MR, 100% RP)
    3. Sistema mixto (50% MR, 50% RP)
    """
    
    # Usar datos reales de 2024 CON siglado
    path_parquet = 'data/computos_diputados_2024.parquet'
    path_siglado = 'data/siglado-diputados-2024.csv'
    
    partidos_base = ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA', 'PES', 'RSP', 'FXM']
    
    print("=" * 80)
    print("TEST: Límite de sobrerrepresentación del 8% constitucional")
    print("=" * 80)
    print("\nUsando datos reales de 2024 con siglado")
    print("MORENA obtuvo ~42.49% de votos nacionales")
    print("Límite esperado: floor((0.4249 + 0.08) × 500) = 252 escaños")
    print()
    
    # Caso 1: MR PURO (100% MR, 0% RP)
    print("\n" + "="*80)
    print("CASO 1: SISTEMA MR PURO (100% MR, 0% RP)")
    print("="*80)
    
    resultado_mr = procesar_diputados_v2(
        path_parquet=path_parquet,
        path_siglado=path_siglado,
        partidos_base=partidos_base,
        anio=2024,
        max_seats=500,
        mr_seats=500,  # 100% MR
        rp_seats=0,    # 0% RP
        aplicar_topes=True,  # CON topes constitucionales
        umbral=0.03,
        sobrerrepresentacion=8.0,
        seed=42,
        print_debug=False
    )
    
    # Extraer del diccionario de totales
    escanos_morena_mr = resultado_mr['tot']['MORENA']
    mr_morena = resultado_mr['mr']['MORENA']
    rp_morena = resultado_mr['rp']['MORENA']
    
    print(f"\nMORENA escaños MR puro:")
    print(f"  MR: {mr_morena}")
    print(f"  RP: {rp_morena}")
    print(f"  TOTAL: {escanos_morena_mr}")
    print(f"¿Respeta límite de 252? {escanos_morena_mr <= 252} {'[OK]' if escanos_morena_mr <= 252 else '[FAIL]'}")
    
    # Caso 2: RP PURO (0% MR, 100% RP)
    print("\n" + "="*80)
    print("CASO 2: SISTEMA RP PURO (0% MR, 100% RP)")
    print("="*80)
    
    resultado_rp = procesar_diputados_v2(
        path_parquet=path_parquet,
        path_siglado=path_siglado,
        partidos_base=partidos_base,
        anio=2024,
        max_seats=500,
        mr_seats=0,    # 0% MR
        rp_seats=500,  # 100% RP
        aplicar_topes=True,
        umbral=0.03,
        sobrerrepresentacion=8.0,
        seed=42,
        print_debug=False
    )
    
    # Extraer del diccionario de totales
    escanos_morena_rp = resultado_rp['tot']['MORENA']
    mr_morena_rp = resultado_rp['mr']['MORENA']
    rp_morena_rp = resultado_rp['rp']['MORENA']
    
    print(f"\nMORENA escaños RP puro:")
    print(f"  MR: {mr_morena_rp}")
    print(f"  RP: {rp_morena_rp}")
    print(f"  TOTAL: {escanos_morena_rp}")
    print(f"¿Respeta límite de 252? {escanos_morena_rp <= 252} {'[OK]' if escanos_morena_rp <= 252 else '[FAIL]'}")
    
    # Caso 3: MIXTO (50% MR, 50% RP)
    print("\n" + "="*80)
    print("CASO 3: SISTEMA MIXTO (50% MR, 50% RP)")
    print("="*80)
    
    resultado_mixto = procesar_diputados_v2(
        path_parquet=path_parquet,
        path_siglado=path_siglado,
        partidos_base=partidos_base,
        anio=2024,
        max_seats=500,
        mr_seats=250,  # 50% MR
        rp_seats=250,  # 50% RP
        aplicar_topes=True,
        umbral=0.03,
        sobrerrepresentacion=8.0,
        seed=42,
        print_debug=False
    )
    
    # Extraer del diccionario de totales
    escanos_morena_mixto = resultado_mixto['tot']['MORENA']
    mr_morena_mixto = resultado_mixto['mr']['MORENA']
    rp_morena_mixto = resultado_mixto['rp']['MORENA']
    
    print(f"\nMORENA escaños mixto:")
    print(f"  MR: {mr_morena_mixto}")
    print(f"  RP: {rp_morena_mixto}")
    print(f"  TOTAL: {escanos_morena_mixto}")
    print(f"¿Respeta límite de 252? {escanos_morena_mixto <= 252} {'[OK]' if escanos_morena_mixto <= 252 else '[FAIL]'}")
    
    # Resumen final
    print("\n" + "="*80)
    print("RESUMEN")
    print("="*80)
    print(f"MR puro (500 MR):      {escanos_morena_mr} escaños {'[OK]' if escanos_morena_mr <= 252 else '[FAIL]'}")
    print(f"RP puro (500 RP):      {escanos_morena_rp} escaños {'[OK]' if escanos_morena_rp <= 252 else '[FAIL]'}")
    print(f"Mixto (250 MR+250 RP): {escanos_morena_mixto} escaños {'[OK]' if escanos_morena_mixto <= 252 else '[FAIL]'}")
    print()
    
    # Verificar que todos pasen
    todos_ok = (escanos_morena_mr <= 252 and 
                escanos_morena_rp <= 252 and 
                escanos_morena_mixto <= 252)
    
    if todos_ok:
        print("[OK][OK][OK] ÉXITO: El límite de 8% se aplica correctamente en TODOS los sistemas [OK][OK][OK]")
        print("\nEl límite constitucional funciona para:")
        print("  - Sistemas de MR puro (solo mayoría relativa)")
        print("  - Sistemas de RP puro (solo representación proporcional)")
        print("  - Sistemas mixtos (MR + RP combinados)")
        print("\nEsto garantiza que ningún partido exceda el 8% de sobrerrepresentación")
        print("independientemente del sistema electoral usado.")
    else:
        print("[FAIL][FAIL][FAIL] ERROR: El límite NO se aplica correctamente en todos los sistemas [FAIL][FAIL][FAIL]")
    
    return todos_ok

if __name__ == '__main__':
    try:
        exito = test_limite_sobrerrepresentacion()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\n[FAIL] ERROR durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

