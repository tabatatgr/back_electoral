#!/usr/bin/env python3
"""
Test directo sin servidor para verificar la lógica de porcentajes_partidos
"""

import sys
import os
import json

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar la función del engine directamente
from engine.procesar_diputados_v2 import procesar_diputados_v2

def test_porcentajes_directo():
    """
    Test directo de la función procesar_diputados con porcentajes extremos
    """
    
    print("=== TEST DIRECTO PORCENTAJES ===")
    
    # Parámetros básicos
    anio = 2024
    plan = "vigente"
    
    # Porcentajes extremos para test
    porcentajes_extremos = {
        "MORENA": 5.0,
        "PAN": 5.0, 
        "PRI": 5.0,
        "PVEM": 80.0,  # EXTREMADAMENTE ALTO
        "MC": 3.0,
        "PT": 2.0
    }
    
    print(f"Año: {anio}")
    print(f"Plan: {plan}")
    print(f"Porcentajes enviados: {porcentajes_extremos}")
    print()
    
    try:
        # Llamar directamente a la función del engine
        resultado = procesar_diputados_v2(
            path_parquet=f"data/computos_diputados_{anio}.parquet",
            anio=anio,
            max_seats=500,
            sistema="mixto",
            mr_seats=None,
            rp_seats=200,
            umbral=0.03,
            max_seats_per_party=300,
            quota_method="hare",
            usar_coaliciones=True,
            votos_redistribuidos=porcentajes_extremos  # Pasar porcentajes directamente
        )
        
        print("✅ FUNCIÓN EJECUTADA EXITOSAMENTE")
        
        # Mostrar todas las claves disponibles
        print(f"Claves disponibles en resultado: {list(resultado.keys())}")
        
        # Verificar resultados de RP
        if 'rp' in resultado:
            rp_results = resultado['rp']
            
            print(f"\n📊 RESULTADOS RP:")
            print(f"Tipo de datos: {type(rp_results)}")
            
            # Si es DataFrame, mostrar como tal
            if hasattr(rp_results, 'iterrows'):
                pvem_escanos = 0
                
                for idx, row in rp_results.iterrows():
                    partido = row.get('PARTIDO', 'N/A')
                    escanos = row.get('ESCANOS', 0)
                    porcentaje = row.get('PORCENTAJE_VOTOS', 0)
                    
                    print(f"{partido}: {escanos} escaños ({porcentaje:.2f}% votos)")
                    
                    if partido == 'PVEM':
                        pvem_escanos = escanos
                        
            # Si es lista de dicts
            elif isinstance(rp_results, list):
                pvem_escanos = 0
                
                for item in rp_results:
                    partido = item.get('PARTIDO', 'N/A')
                    escanos = item.get('ESCANOS', 0)
                    porcentaje = item.get('PORCENTAJE_VOTOS', 0)
                    
                    print(f"{partido}: {escanos} escaños ({porcentaje:.2f}% votos)")
                    
                    if partido == 'PVEM':
                        pvem_escanos = escanos
            # Si es diccionario directo {partido: escanos}
            elif isinstance(rp_results, dict):
                pvem_escanos = 0
                
                print("Resultados por partido:")
                for partido, escanos in rp_results.items():
                    print(f"{partido}: {escanos} escaños")
                    
                    if partido == 'PVEM':
                        pvem_escanos = escanos
                        
            else:
                print(f"Estructura de datos no reconocida: {rp_results}")
                return False
            
            print(f"\n🔍 ANÁLISIS:")
            print(f"PVEM escaños: {pvem_escanos}")
            
            if pvem_escanos > 100:
                print("✅ ¡PORCENTAJES FUNCIONAN! PVEM tiene muchos escaños")
                return True
            else:
                print("❌ PORCENTAJES NO FUNCIONAN: PVEM sigue con pocos escaños")
                print("El backend no está usando los porcentajes personalizados")
                return False
                
        else:
            print("❌ No se encontraron resultados 'rp'")
            return False
            
    except Exception as e:
        print(f"❌ Error en la función: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sin_porcentajes():
    """
    Test de control: ejecutar sin porcentajes para comparar
    """
    
    print("\n=== TEST DE CONTROL (SIN PORCENTAJES) ===")
    
    try:
        resultado = procesar_diputados_v2(
            path_parquet=f"data/computos_diputados_2024.parquet",
            anio=2024,
            max_seats=500,
            sistema="mixto",
            mr_seats=None,
            rp_seats=200,
            umbral=0.03,
            max_seats_per_party=300,
            quota_method="hare",
            usar_coaliciones=True,
            votos_redistribuidos=None  # SIN porcentajes
        )
        
        if 'rp' in resultado:
            rp_results = resultado['rp']
            
            print("\n📊 RESULTADOS SIN PORCENTAJES:")
            
            # Manejar DataFrame o lista
            if hasattr(rp_results, 'iterrows'):
                for idx, row in rp_results.iterrows():
                    partido = row.get('PARTIDO', 'N/A')
                    escanos = row.get('ESCANOS', 0)
                    porcentaje = row.get('PORCENTAJE_VOTOS', 0)
                    
                    if partido == 'PVEM':
                        print(f"PVEM (normal): {escanos} escaños ({porcentaje:.2f}% votos)")
                        return escanos
            elif isinstance(rp_results, list):
                for item in rp_results:
                    partido = item.get('PARTIDO', 'N/A')
                    escanos = item.get('ESCANOS', 0)
                    porcentaje = item.get('PORCENTAJE_VOTOS', 0)
                    
                    if partido == 'PVEM':
                        print(f"PVEM (normal): {escanos} escaños ({porcentaje:.2f}% votos)")
                        return escanos
            elif isinstance(rp_results, dict):
                for partido, escanos in rp_results.items():
                    if partido == 'PVEM':
                        print(f"PVEM (normal): {escanos} escaños")
                        return escanos
                    
    except Exception as e:
        print(f"❌ Error en test de control: {e}")
        return None

if __name__ == "__main__":
    # Test con porcentajes extremos
    test_con_porcentajes = test_porcentajes_directo()
    
    # Test de control sin porcentajes
    escanos_normales = test_sin_porcentajes()
    
    print(f"\n🎯 RESUMEN:")
    if test_con_porcentajes:
        print("✅ Los porcentajes personalizados SÍ están funcionando")
    else:
        print("❌ Los porcentajes personalizados NO están funcionando")
        print("Esto significa que el parámetro no se está pasando correctamente")
        
    if escanos_normales:
        print(f"PVEM normal: {escanos_normales} escaños")
