#!/usr/bin/env python3
"""
Test simplificado de redistribución PM y sobrerrepresentación
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from engine.procesar_senadores_v2 import procesar_senadores_v2

def test_redistribucion_simple():
    """Test simple para ver redistribución clara"""
    
    print("🔍 REDISTRIBUCIÓN PRIMERA MINORÍA Y SOBRERREPRESENTACIÓN")
    print("=" * 70)
    
    # Configuración base
    path_parquet = "data/computos_senado_2018.parquet"
    path_siglado = "data/siglado_senado_2018_corregido.csv"
    
    if not os.path.exists(path_parquet) or not os.path.exists(path_siglado):
        print("❌ Archivos no encontrados")
        return
    
    scenarios = [
        ("VIGENTE: 96MR+32RP", {"mr_seats": 96, "rp_seats": 32}),
        ("BALANCEADO: 64MR+64RP", {"mr_seats": 64, "rp_seats": 64}), 
        ("MÁS RP: 32MR+96RP", {"mr_seats": 32, "rp_seats": 96}),
        ("TODO RP: 0MR+128RP", {"mr_seats": 0, "rp_seats": 128}),
        ("TODO MR: 128MR+0RP", {"mr_seats": 128, "rp_seats": 0})
    ]
    
    resultados = {}
    
    for nombre, config in scenarios:
        print(f"\n🧪 {nombre}")
        resultado = procesar_senadores_v2(
            path_parquet=path_parquet,
            anio=2018,
            path_siglado=path_siglado,
            max_seats=128,
            umbral=0.0,
            sistema="mixto" if config["mr_seats"] > 0 and config["rp_seats"] > 0 else "rp" if config["rp_seats"] == 128 else "mr",
            **config
        )
        
        if 'seat_chart' in resultado:
            total = sum(p['seats'] for p in resultado['seat_chart'])
            print(f"   Total: {total} escaños")
            resultados[nombre] = resultado['seat_chart']
        else:
            print("   ❌ Error en seat_chart")
    
    # Tabla comparativa
    print(f"\n📊 TABLA COMPARATIVA DE REDISTRIBUCIÓN")
    print("=" * 70)
    
    # Obtener todos los partidos
    partidos = set()
    for seat_chart in resultados.values():
        for party in seat_chart:
            partidos.add(party['party'])
    
    # Header
    scenarios_names = [name.split(":")[0] for name, _ in scenarios]
    print(f"{'PARTIDO':<8} | " + " | ".join(f"{name:>8}" for name in scenarios_names))
    print("-" * (10 + len(scenarios_names) * 11))
    
    # Datos por partido
    for partido in sorted(partidos):
        if partido in ['PES', 'NA']:  # Saltar partidos muy pequeños
            continue
            
        fila = f"{partido:<8} | "
        escanos_por_scenario = []
        
        for nombre, _ in scenarios:
            if nombre in resultados:
                party_data = next((p for p in resultados[nombre] if p['party'] == partido), None)
                escanos = party_data['seats'] if party_data else 0
                escanos_por_scenario.append(f"{escanos:>8}")
            else:
                escanos_por_scenario.append(f"{'--':>8}")
        
        fila += " | ".join(escanos_por_scenario)
        print(fila)
    
    # Análisis de cambios
    print(f"\n🔄 ANÁLISIS DE CAMBIOS:")
    print("-" * 50)
    
    if "VIGENTE: 96MR+32RP" in resultados and "TODO RP: 0MR+128RP" in resultados:
        vigente = {p['party']: p['seats'] for p in resultados["VIGENTE: 96MR+32RP"]}
        todo_rp = {p['party']: p['seats'] for p in resultados["TODO RP: 0MR+128RP"]}
        
        print("Cambios VIGENTE → TODO RP:")
        for partido in ['MORENA', 'PAN', 'PRI', 'PRD']:
            v = vigente.get(partido, 0)
            r = todo_rp.get(partido, 0)
            diff = r - v
            print(f"  {partido}: {v} → {r} ({diff:+d})")

if __name__ == "__main__":
    test_redistribucion_simple()
