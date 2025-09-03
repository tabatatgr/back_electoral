#!/usr/bin/env python3
"""
Test específico para verificar redistribución con Primera Minoría y Sobrerrepresentación
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from engine.procesar_senadores_v2 import procesar_senadores_v2
import pandas as pd

def test_primera_minoria_sobrerrepresentacion():
    """Test para verificar que PM y sobrerrepresentación redistribuyan escaños"""
    
    print("🔍 TESTING PRIMERA MINORÍA Y SOBRERREPRESENTACIÓN")
    print("=" * 70)
    
    # Paths de archivos (usando 2018 que sabemos funciona)
    path_parquet = "data/computos_senado_2018.parquet"
    path_siglado = "data/siglado_senado_2018_corregido.csv"
    
    if not os.path.exists(path_parquet):
        print(f"❌ No se encontró: {path_parquet}")
        return
    if not os.path.exists(path_siglado):
        print(f"❌ No se encontró: {path_siglado}")
        return
    
    print("📊 ESCENARIOS DE PRUEBA")
    print("-" * 50)
    
    # Escenario base: Sistema vigente
    print("\n🧪 TEST 1: SISTEMA VIGENTE BASE")
    print("   96 MR+PM + 32 RP = 128 total, sobrerrepresentación = 8")
    resultado_base = procesar_senadores_v2(
        path_parquet=path_parquet,
        anio=2018,
        path_siglado=path_siglado,
        max_seats=128,
        umbral=0.0,  # Sin umbral para ver efecto puro
        sistema="mixto",
        mr_seats=96,
        rp_seats=32
    )
    
    print_resumen_escanos(resultado_base, "BASE")
    
    # Test 2: Reducir MR+PM, aumentar RP
    print("\n🧪 TEST 2: MÁS RP, MENOS MR+PM")
    print("   64 MR+PM + 64 RP = 128 total, sobrerrepresentación = 8")
    resultado_mas_rp = procesar_senadores_v2(
        path_parquet=path_parquet,
        anio=2018,
        path_siglado=path_siglado,
        max_seats=128,
        umbral=0.0,
        sistema="mixto",
        mr_seats=64,
        rp_seats=64
    )
    
    print_resumen_escanos(resultado_mas_rp, "MÁS RP")
    
    # Test 3: Cambiar sobrerrepresentación
    print("\n🧪 TEST 3: SOBRERREPRESENTACIÓN ALTA")
    print("   96 MR+PM + 32 RP = 128 total, sobrerrepresentación = 16")
    resultado_sobrer_alta = procesar_senadores_v2(
        path_parquet=path_parquet,
        anio=2018,
        path_siglado=path_siglado,
        max_seats=128,
        umbral=0.0,
        sistema="mixto", 
        mr_seats=96,
        rp_seats=32
    )
    
    print_resumen_escanos(resultado_sobrer_alta, "SOBRER ALTA")
    
    # Test 4: Sin sobrerrepresentación
    print("\n🧪 TEST 4: SIN SOBRERREPRESENTACIÓN")
    print("   96 MR+PM + 32 RP = 128 total, sobrerrepresentación = 0")
    resultado_sin_sobrer = procesar_senadores_v2(
        path_parquet=path_parquet,
        anio=2018,
        path_siglado=path_siglado,
        max_seats=128,
        umbral=0.0,
        sistema="mixto",
        mr_seats=96,
        rp_seats=32
    )
    
    print_resumen_escanos(resultado_sin_sobrer, "SIN SOBRER")
    
    # Test 5: Sistema puro RP (Plan A)
    print("\n🧪 TEST 5: SISTEMA PURO RP")
    print("   0 MR+PM + 128 RP = 128 total")
    resultado_puro_rp = procesar_senadores_v2(
        path_parquet=path_parquet,
        anio=2018,
        path_siglado=path_siglado,
        max_seats=128,
        umbral=0.0,
        sistema="rp",
        mr_seats=0,
        rp_seats=128
    )
    
    print_resumen_escanos(resultado_puro_rp, "PURO RP")
    
    # Test 6: Sistema puro MR (Plan C)
    print("\n🧪 TEST 6: SISTEMA PURO MR")
    print("   128 MR+PM + 0 RP = 128 total")
    resultado_puro_mr = procesar_senadores_v2(
        path_parquet=path_parquet,
        anio=2018,
        path_siglado=path_siglado,
        max_seats=128,
        umbral=0.0,
        sistema="mr",
        mr_seats=128,
        rp_seats=0
    )
    
    print_resumen_escanos(resultado_puro_mr, "PURO MR")
    
    # Análisis comparativo
    print("\n📈 ANÁLISIS COMPARATIVO")
    print("=" * 70)
    
    # Comparar distribuciones
    comparar_distribuciones([
        ("BASE (96MR+32RP)", resultado_base),
        ("MÁS RP (64MR+64RP)", resultado_mas_rp), 
        ("PURO RP (0MR+128RP)", resultado_puro_rp),
        ("PURO MR (128MR+0RP)", resultado_puro_mr)
    ])

def print_resumen_escanos(resultado, nombre):
    """Imprime resumen de escaños de un resultado"""
    if 'seat_chart' not in resultado:
        print(f"❌ {nombre}: No hay seat_chart")
        return
        
    seat_chart = resultado['seat_chart']
    total = sum(p['seats'] for p in seat_chart)
    
    print(f"   {nombre}: Total {total} escaños")
    
    # Mostrar top 4 partidos
    sorted_parties = sorted(seat_chart, key=lambda x: x['seats'], reverse=True)
    for i, party in enumerate(sorted_parties[:4]):
        if party['seats'] > 0:
            print(f"     {party['party']}: {party['seats']} escaños ({party['percent']:.1f}%)")

def comparar_distribuciones(resultados):
    """Compara distribuciones entre diferentes escenarios"""
    print("\n🔄 REDISTRIBUCIÓN POR PARTIDO:")
    print("-" * 50)
    
    # Obtener todos los partidos
    todos_partidos = set()
    for nombre, resultado in resultados:
        if 'seat_chart' in resultado:
            for party in resultado['seat_chart']:
                todos_partidos.add(party['party'])
    
    # Crear tabla comparativa
    for partido in sorted(todos_partidos):
        escanos_por_scenario = []
        for nombre, resultado in resultados:
            if 'seat_chart' in resultado:
                party_data = next((p for p in resultado['seat_chart'] if p['party'] == partido), None)
                escanos = party_data['seats'] if party_data else 0
                escanos_por_scenario.append(f"{escanos:2d}")
            else:
                escanos_por_scenario.append(" -")
        
        if any(int(e) if e.strip().isdigit() else 0 for e in escanos_por_scenario):
            escanos_str = " | ".join(escanos_por_scenario)
            print(f"  {partido:8s}: {escanos_str}")
    
    # Headers
    print("\n" + " " * 11 + " | ".join([f"{r[0][:8]:8s}" for r in resultados]))

if __name__ == "__main__":
    test_primera_minoria_sobrerrepresentacion()
