#!/usr/bin/env python3
"""
Test específico para verificar redistribución de escaños con umbral
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from engine.procesar_senadores_v2 import asigna_senado_RP

def test_redistribucion_umbral():
    """Test para verificar que los escaños se redistribuyen correctamente"""
    
    print("🔍 TESTING REDISTRIBUCIÓN DE ESCAÑOS CON UMBRAL")
    print("=" * 60)
    
    # Caso de prueba: 5 partidos, algunos no cumplen umbral
    votos_test = {
        'MORENA': 21000000,  # ~42% - SÍ cumple
        'PAN': 10000000,    # ~20% - SÍ cumple  
        'PRI': 9000000,     # ~18% - SÍ cumple
        'PRD': 3000000,     # ~6% - SÍ cumple
        'PVEM': 2500000,    # ~5% - SÍ cumple
        'MC': 1500000,      # ~3% - límite
        'PT': 1000000,      # ~2% - NO cumple 3%
        'PES': 500000,      # ~1% - NO cumple 3%
        'NA': 200000        # ~0.4% - NO cumple 3%
    }
    
    total_votos = sum(votos_test.values())
    print(f"📊 VOTOS ORIGINALES:")
    for partido, votos in votos_test.items():
        pct = (votos / total_votos) * 100
        print(f"  {partido}: {votos:,} votos ({pct:.1f}%)")
    
    print(f"\nTotal votos: {total_votos:,}")
    
    # Test 1: Sin umbral (0%)
    print(f"\n🧪 TEST 1: SIN UMBRAL (0%)")
    print("-" * 40)
    resultado_sin_umbral = asigna_senado_RP(votos_test, threshold=0.0, escanos_rp=32)
    total_sin_umbral = sum(resultado_sin_umbral.values())
    
    print(f"Escaños asignados:")
    for partido, escanos in resultado_sin_umbral.items():
        if escanos > 0:
            print(f"  {partido}: {escanos} escaños")
    print(f"Total escaños: {total_sin_umbral}")
    
    # Test 2: Con umbral 3%
    print(f"\n🧪 TEST 2: CON UMBRAL 3%")
    print("-" * 40)
    resultado_con_umbral = asigna_senado_RP(votos_test, threshold=0.03, escanos_rp=32)
    total_con_umbral = sum(resultado_con_umbral.values())
    
    print(f"Escaños asignados:")
    for partido, escanos in resultado_con_umbral.items():
        if escanos > 0:
            print(f"  {partido}: {escanos} escaños")
    print(f"Total escaños: {total_con_umbral}")
    
    # Test 3: Con umbral alto 5%
    print(f"\n🧪 TEST 3: CON UMBRAL ALTO 5%")
    print("-" * 40)
    resultado_umbral_alto = asigna_senado_RP(votos_test, threshold=0.05, escanos_rp=32)
    total_umbral_alto = sum(resultado_umbral_alto.values())
    
    print(f"Escaños asignados:")
    for partido, escanos in resultado_umbral_alto.items():
        if escanos > 0:
            print(f"  {partido}: {escanos} escaños")
    print(f"Total escaños: {total_umbral_alto}")
    
    # Análisis de redistribución
    print(f"\n📈 ANÁLISIS DE REDISTRIBUCIÓN")
    print("=" * 60)
    
    print(f"¿Se mantiene el total de escaños?")
    print(f"  Sin umbral: {total_sin_umbral} escaños")
    print(f"  Con umbral 3%: {total_con_umbral} escaños")
    print(f"  Con umbral 5%: {total_umbral_alto} escaños")
    
    if total_con_umbral == 32:
        print("✅ CORRECTO: Se redistribuyen los escaños de partidos eliminados")
    else:
        print("❌ ERROR: Se pierden escaños cuando se aplica umbral")
    
    # Comparar ganadores vs perdedores
    print(f"\n🔄 REDISTRIBUCIÓN DETALLADA (3% vs sin umbral):")
    for partido in votos_test.keys():
        sin = resultado_sin_umbral[partido]
        con = resultado_con_umbral[partido]
        diff = con - sin
        if diff != 0:
            print(f"  {partido}: {sin} → {con} ({diff:+d})")

if __name__ == "__main__":
    test_redistribucion_umbral()
