#!/usr/bin/env python3
"""
Comparación entre nuestro sistema actual y el script de ejemplo
"""

import sys
sys.path.append('.')

# Script de ejemplo del usuario
from test_script_ejemplo import allocate_quota, allocate_divisor

# Nuestro sistema actual
from engine.procesar_diputados_v2 import procesar_diputados_v2

def comparar_metodos():
    """Comparar nuestro sistema vs script de ejemplo"""
    
    print("🔍 COMPARACIÓN: NUESTRO SISTEMA vs SCRIPT DE EJEMPLO")
    print("=" * 60)
    
    # Datos de prueba - México 2018 RP simplificado
    votos_ejemplo = {
        "MORENA": 21741037,
        "PAN": 10165244,
        "PRI": 9112625,
        "PRD": 3163824,
        "PVEM": 2623767,
        "PT": 2595279,
        "MC": 258125,
        "PES": 626393,
        "NA": 89844
    }
    
    escanos = 200
    umbral = 0.03
    
    print("📊 MÉTODO CUOTA HARE")
    print("-" * 30)
    
    # Script de ejemplo
    resultado_ejemplo_hare = allocate_quota(votos_ejemplo, escanos, quota_method="hare", threshold=umbral)
    
    # Nuestro sistema actual - RP puro con Hare
    try:
        resultado_nuestro_hare = procesar_diputados_v2(
            path_parquet="data/computos_diputados_2018.parquet",
            anio=2018,
            path_siglado="data/siglado-diputados-2018.csv",
            max_seats=200,
            sistema="rp",  # Solo RP
            mr_seats=0,
            rp_seats=200,
            quota_method="hare",
            divisor_method=None,  # Solo cuota
            umbral=0.03,
            usar_coaliciones=False  # Sin coaliciones para comparar directo
        )
        
        if resultado_nuestro_hare and 'tot' in resultado_nuestro_hare:
            escanos_nuestro_hare = resultado_nuestro_hare['tot']
        else:
            escanos_nuestro_hare = {}
            
    except Exception as e:
        print(f"❌ Error en nuestro sistema Hare: {e}")
        escanos_nuestro_hare = {}
    
    print("Partido | Script | Nuestro | Diferencia")
    print("--------|--------|---------|----------")
    for partido in sorted(votos_ejemplo.keys()):
        ejemplo = resultado_ejemplo_hare.get(partido, 0)
        nuestro = escanos_nuestro_hare.get(partido, 0)
        diff = nuestro - ejemplo
        print(f"{partido:7} | {ejemplo:6} | {nuestro:7} | {diff:+9}")
    
    print()
    print("📊 MÉTODO DIVISOR D'HONDT")
    print("-" * 30)
    
    # Script de ejemplo
    resultado_ejemplo_dhondt = allocate_divisor(votos_ejemplo, escanos, divisor_method="dhondt", threshold=umbral)
    
    # Nuestro sistema actual - RP puro con D'Hondt
    try:
        resultado_nuestro_dhondt = procesar_diputados_v2(
            path_parquet="data/computos_diputados_2018.parquet",
            anio=2018,
            path_siglado="data/siglado-diputados-2018.csv",
            max_seats=200,
            sistema="rp",  # Solo RP
            mr_seats=0,
            rp_seats=200,
            quota_method=None,  # Solo divisor
            divisor_method="dhondt",
            umbral=0.03,
            usar_coaliciones=False  # Sin coaliciones para comparar directo
        )
        
        if resultado_nuestro_dhondt and 'tot' in resultado_nuestro_dhondt:
            escanos_nuestro_dhondt = resultado_nuestro_dhondt['tot']
        else:
            escanos_nuestro_dhondt = {}
            
    except Exception as e:
        print(f"❌ Error en nuestro sistema D'Hondt: {e}")
        escanos_nuestro_dhondt = {}
    
    print("Partido | Script | Nuestro | Diferencia")
    print("--------|--------|---------|----------")
    for partido in sorted(votos_ejemplo.keys()):
        ejemplo = resultado_ejemplo_dhondt.get(partido, 0)
        nuestro = escanos_nuestro_dhondt.get(partido, 0)
        diff = nuestro - ejemplo
        print(f"{partido:7} | {ejemplo:6} | {nuestro:7} | {diff:+9}")
    
    print()
    print("📋 VERIFICACIONES:")
    
    # Verificar totales
    total_ejemplo_hare = sum(resultado_ejemplo_hare.values())
    total_nuestro_hare = sum(escanos_nuestro_hare.values())
    total_ejemplo_dhondt = sum(resultado_ejemplo_dhondt.values())
    total_nuestro_dhondt = sum(escanos_nuestro_dhondt.values())
    
    print(f"Hare - Script: {total_ejemplo_hare}, Nuestro: {total_nuestro_hare}")
    print(f"D'Hondt - Script: {total_ejemplo_dhondt}, Nuestro: {total_nuestro_dhondt}")
    
    # Verificar coincidencias
    coincidencias_hare = sum(1 for p in votos_ejemplo.keys() 
                           if resultado_ejemplo_hare.get(p, 0) == escanos_nuestro_hare.get(p, 0))
    
    coincidencias_dhondt = sum(1 for p in votos_ejemplo.keys() 
                             if resultado_ejemplo_dhondt.get(p, 0) == escanos_nuestro_dhondt.get(p, 0))
    
    total_partidos = len(votos_ejemplo)
    
    print(f"✅ Hare - Coincidencias: {coincidencias_hare}/{total_partidos}")
    print(f"✅ D'Hondt - Coincidencias: {coincidencias_dhondt}/{total_partidos}")
    
    if coincidencias_hare == total_partidos:
        print("🎉 HARE: ¡Nuestro sistema coincide perfectamente con el script!")
    else:
        print("⚠️ HARE: Hay diferencias entre nuestro sistema y el script")
        
    if coincidencias_dhondt == total_partidos:
        print("🎉 D'HONDT: ¡Nuestro sistema coincide perfectamente con el script!")
    else:
        print("⚠️ D'HONDT: Hay diferencias entre nuestro sistema y el script")

if __name__ == "__main__":
    comparar_metodos()
