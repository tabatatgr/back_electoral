#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug: ¿Por qué 50MR_50RP y 75MR_25RP dan los mismos escaños?
"""

from engine.procesar_diputados_v2 import procesar_diputados_v2

def test_configuraciones_2024():
    """
    Probar ambas configuraciones con debug activado
    """
    
    print("="*80)
    print("TEST: 2024 - 500 ESCAÑOS - COMPARAR 50/50 vs 75/25")
    print("="*80)
    
    # Configuración 1: 50% MR / 50% RP
    print("\n" + "="*80)
    print("CONFIGURACIÓN 1: 50MR_50RP (250 MR + 250 RP = 500)")
    print("="*80)
    
    resultado_50_50 = procesar_diputados_v2(
        path_parquet="data/computos_diputados_2024.parquet",
        anio=2024,
        path_siglado="data/siglado-diputados-2024.csv",
        max_seats=500,
        sistema="mixto",
        mr_seats=250,
        rp_seats=250,
        umbral=0.03,
        quota_method="hare",
        usar_coaliciones=True,
        print_debug=True
    )
    
    print("\n[RESULTADOS 50MR_50RP]")
    print(f"MORENA: {resultado_50_50['tot'].get('MORENA', 0)} escaños")
    print(f"  MR: {resultado_50_50['mr'].get('MORENA', 0)}")
    print(f"  RP: {resultado_50_50['rp'].get('MORENA', 0)}")
    
    # Configuración 2: 75% MR / 25% RP
    print("\n" + "="*80)
    print("CONFIGURACIÓN 2: 75MR_25RP (375 MR + 125 RP = 500)")
    print("="*80)
    
    resultado_75_25 = procesar_diputados_v2(
        path_parquet="data/computos_diputados_2024.parquet",
        anio=2024,
        path_siglado="data/siglado-diputados-2024.csv",
        max_seats=500,
        sistema="mixto",
        mr_seats=375,
        rp_seats=125,
        umbral=0.03,
        quota_method="hare",
        usar_coaliciones=True,
        print_debug=True
    )
    
    print("\n[RESULTADOS 75MR_25RP]")
    print(f"MORENA: {resultado_75_25['tot'].get('MORENA', 0)} escaños")
    print(f"  MR: {resultado_75_25['mr'].get('MORENA', 0)}")
    print(f"  RP: {resultado_75_25['rp'].get('MORENA', 0)}")
    
    # Comparación
    print("\n" + "="*80)
    print("COMPARACIÓN")
    print("="*80)
    
    print(f"\n{'Config':15s} | {'MR Solicitado':>15s} | {'RP Solicitado':>15s} | {'MORENA Total':>15s} | {'MORENA MR':>12s} | {'MORENA RP':>12s}")
    print("-"*95)
    print(f"{'50MR_50RP':15s} | {250:>15d} | {250:>15d} | {resultado_50_50['tot'].get('MORENA', 0):>15d} | {resultado_50_50['mr'].get('MORENA', 0):>12d} | {resultado_50_50['rp'].get('MORENA', 0):>12d}")
    print(f"{'75MR_25RP':15s} | {375:>15d} | {125:>15d} | {resultado_75_25['tot'].get('MORENA', 0):>15d} | {resultado_75_25['mr'].get('MORENA', 0):>12d} | {resultado_75_25['rp'].get('MORENA', 0):>12d}")
    
    if resultado_50_50['tot'].get('MORENA', 0) == resultado_75_25['tot'].get('MORENA', 0):
        print("\n[X] PROBLEMA: MORENA tiene los MISMOS escaños totales en ambas configuraciones")
        print("    Esto sugiere que el parámetro mr_seats/rp_seats NO está siendo respetado")
    else:
        print("\n[OK] Las configuraciones producen resultados DIFERENTES (correcto)")

if __name__ == "__main__":
    test_configuraciones_2024()
