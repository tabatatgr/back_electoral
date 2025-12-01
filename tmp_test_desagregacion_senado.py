#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test de desagregación de votos para SENADO
Validar que usar_coaliciones=False implemente el contrafactual correctamente
"""

from engine.procesar_senadores_v2 import procesar_senadores_v2

def test_desagregacion_senado():
    """
    Test con configuración real del Senado 2024:
    - 64 MR (2 por entidad)
    - 32 PM (1 por entidad)  
    - 32 RP
    Total: 128 senadores
    """
    
    print("="*80)
    print("TEST DESAGREGACIÓN SENADO - 2024")
    print("="*80)
    
    # Configuración real del Senado
    config = {
        'escanos_mr_total': 64,  # 2 por entidad
        'escanos_pm': 32,        # 1 por entidad
        'escanos_rp': 32,        # RP nacional
        'anio': 2024
    }
    
    print(f"\nConfiguración: {config['escanos_mr_total']} MR + {config['escanos_pm']} PM + {config['escanos_rp']} RP = 128 total")
    
    # Test 1: CON coaliciones
    print("\n" + "="*80)
    print("ESCENARIO 1: CON COALICIONES (usar_coaliciones=True)")
    print("="*80)
    
    result_con = procesar_senadores_v2(
        path_parquet="data/computos_senado_2024.parquet",
        path_siglado="data/siglado-senado-2024.csv",
        anio=config['anio'],
        mr_seats=config['escanos_mr_total'],
        pm_seats=config['escanos_pm'],
        rp_seats=config['escanos_rp'],
        divisor_method="dhondt",
        usar_coaliciones=True
    )
    
    print("\n" + "-"*80)
    print("RESULTADOS CON COALICIONES:")
    print("-"*80)
    
    totales_con = {}
    for item in result_con['seat_chart']:
        partido = item['party']
        escanos = item['seats']
        percent = item['percent']
        totales_con[partido] = escanos
        if escanos > 0:
            print(f"{partido:15s}: {escanos:3d} escaños ({percent:5.2f}%)")
    
    # Calcular bloque
    bloque_con = totales_con.get('MORENA', 0) + totales_con.get('PT', 0) + totales_con.get('PVEM', 0)
    print(f"\n{'BLOQUE COALICIÓN':15s}: {bloque_con:3d} escaños ({bloque_con/128*100:5.2f}%)")
    
    # Test 2: SIN coaliciones (contrafactual)
    print("\n" + "="*80)
    print("ESCENARIO 2: SIN COALICIONES - CONTRAFACTUAL (usar_coaliciones=False)")
    print("="*80)
    
    result_sin = procesar_senadores_v2(
        path_parquet="data/computos_senado_2024.parquet",
        path_siglado="data/siglado-senado-2024.csv",
        anio=config['anio'],
        mr_seats=config['escanos_mr_total'],
        pm_seats=config['escanos_pm'],
        rp_seats=config['escanos_rp'],
        divisor_method="dhondt",
        usar_coaliciones=False
    )
    
    print("\n" + "-"*80)
    print("RESULTADOS SIN COALICIONES (competencia separada):")
    print("-"*80)
    
    totales_sin = {}
    for item in result_sin['seat_chart']:
        partido = item['party']
        escanos = item['seats']
        percent = item['percent']
        totales_sin[partido] = escanos
        if escanos > 0:
            print(f"{partido:15s}: {escanos:3d} escaños ({percent:5.2f}%)")
    
    # Calcular bloque
    bloque_sin = totales_sin.get('MORENA', 0) + totales_sin.get('PT', 0) + totales_sin.get('PVEM', 0)
    print(f"\n{'BLOQUE (separados)':15s}: {bloque_sin:3d} escaños ({bloque_sin/128*100:5.2f}%)")
    
    # Comparación
    print("\n" + "="*80)
    print("COMPARACIÓN: DIFERENCIAS ENTRE CON Y SIN COALICIÓN")
    print("="*80)
    
    partidos_relevantes = ['MORENA', 'PT', 'PVEM', 'PAN', 'PRI', 'MC']
    
    print(f"\n{'PARTIDO':15s} | {'CON':>6s} | {'SIN':>6s} | {'DELTA':>6s} | {'D %':>6s}")
    print("-" * 60)
    
    for partido in partidos_relevantes:
        con = totales_con.get(partido, 0)
        sin = totales_sin.get(partido, 0)
        delta = sin - con
        delta_pct = ((sin - con) / 128 * 100) if con != sin else 0.0
        signo = "+" if delta > 0 else ""
        print(f"{partido:15s} | {con:6d} | {sin:6d} | {signo}{delta:5d} | {signo}{delta_pct:5.1f}%")
    
    print("-" * 60)
    print(f"{'BLOQUE':15s} | {bloque_con:6d} | {bloque_sin:6d} | {bloque_sin-bloque_con:+6d} | {(bloque_sin-bloque_con)/128*100:+6.1f}%")
    
    # Validación
    print("\n" + "="*80)
    print("VALIDACIÓN")
    print("="*80)
    
    morena_con = totales_con.get('MORENA', 0)
    morena_sin = totales_sin.get('MORENA', 0)
    
    if morena_con == morena_sin:
        print(f"\n[X] FALLO: MORENA tiene los MISMOS escaños ({morena_con}) en ambos escenarios")
        print("   La desagregación de votos NO está funcionando correctamente")
        return False
    else:
        diferencia = morena_sin - morena_con
        print(f"\n[OK] ÉXITO: MORENA tiene DIFERENTES escaños:")
        print(f"   CON coalición: {morena_con} escaños")
        print(f"   SIN coalición: {morena_sin} escaños")
        print(f"   Diferencia: {diferencia:+d} escaños ({diferencia/128*100:+.1f}%)")
        print("\n   La desagregación de votos está funcionando correctamente")
        return True

if __name__ == "__main__":
    try:
        exito = test_desagregacion_senado()
        if exito:
            print("\n" + "="*80)
            print("TEST COMPLETADO EXITOSAMENTE")
            print("="*80)
        else:
            print("\n" + "="*80)
            print("TEST FALLÓ - REVISAR IMPLEMENTACIÓN")
            print("="*80)
    except Exception as e:
        print(f"\n[X] ERROR durante el test: {e}")
        import traceback
        traceback.print_exc()
