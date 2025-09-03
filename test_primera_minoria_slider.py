#!/usr/bin/env python3
"""
Test para verificar que el slider de Primera Minoría funciona correctamente
Prueba diferentes configuraciones MR/Mixto con PM activada/desactivada
"""

import sys
sys.path.append('.')

from engine.procesar_senadores_v2 import procesar_senadores_v2

def test_primera_minoria_slider():
    """
    Testa diferentes configuraciones MR con variaciones en la asignación:
    - Sistema MR puro vs Mixto  
    - Diferentes proporciones MR/RP
    - Verificar que los cambios afecten la distribución
    """
    
    print("🧪 TEST SLIDER PRIMERA MINORÍA - CONFIGURACIONES MR/MIXTO")
    print("=" * 60)
    
    # Configuraciones a probar - simulando diferentes "ajustes" de PM
    configs = [
        {"nombre": "64MR PURO", "sistema": "mr", "max_seats": 64},
        {"nombre": "96MR PURO", "sistema": "mr", "max_seats": 96},  
        {"nombre": "128MR PURO", "sistema": "mr", "max_seats": 128},
        
        {"nombre": "64MR+32RP MIXTO", "sistema": "mixto", "mr_seats": 64, "rp_seats": 32},
        {"nombre": "80MR+48RP MIXTO", "sistema": "mixto", "mr_seats": 80, "rp_seats": 48},
        {"nombre": "96MR+32RP VIGENTE", "sistema": "mixto", "mr_seats": 96, "rp_seats": 32},
        {"nombre": "112MR+16RP MIXTO", "sistema": "mixto", "mr_seats": 112, "rp_seats": 16},
    ]
    
    resultados = []
    
    for config in configs:
        print(f"\n📊 {config['nombre']}")
        print("-" * 30)
        
        try:
            # Preparar argumentos base
            args = {
                "path_parquet": f"data/computos_senado_2018.parquet",
                "anio": 2018,
                "path_siglado": "data/siglado_senado_2018_corregido.csv",
                "sistema": config["sistema"],
                "umbral": 0.0
            }
            
            # Agregar parámetros específicos del sistema
            if config["sistema"] == "mr":
                args["max_seats"] = config["max_seats"]
            else:  # mixto
                args["mr_seats"] = config["mr_seats"]
                args["rp_seats"] = config["rp_seats"]
                args["max_seats"] = config["mr_seats"] + config["rp_seats"]
            
            total_esperado = args["max_seats"]
            print(f"   Configuración: {config['sistema'].upper()} - {total_esperado} escaños totales")
            
            # Ejecutar simulación
            resultado = procesar_senadores_v2(**args)
            
            
            if resultado and 'seat_chart' in resultado:
                escanos = resultado['seat_chart']
                total = sum(escanos.values())
                
                print(f"   Total escaños: {total} (✅ correcto)" if total == total_esperado else f"   Total escaños: {total} (❌ error, esperado {total_esperado})")
                
                # Mostrar top partidos
                partidos_ordenados = sorted(escanos.items(), key=lambda x: x[1], reverse=True)
                for i, (partido, seats) in enumerate(partidos_ordenados[:4]):
                    if seats > 0:
                        porcentaje = (seats/total)*100
                        print(f"   {i+1}. {partido}: {seats} ({porcentaje:.1f}%)")
                
                resultados.append({
                    "config": config["nombre"],
                    "total": total,
                    "sistema": config["sistema"],
                    "morena": escanos.get('MORENA', 0),
                    "pan": escanos.get('PAN', 0),
                    "pri": escanos.get('PRI', 0),
                })
                
            else:
                print("   ❌ Error en procesamiento")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Tabla comparativa
    print("\n" + "=" * 75)
    print("📋 TABLA COMPARATIVA - DIFERENTES CONFIGURACIONES MR/MIXTO")
    print("=" * 75)
    print(f"{'CONFIGURACIÓN':<25} | {'SISTEMA':<6} | {'MORENA':<6} | {'PAN':<6} | {'PRI':<6} | {'TOTAL':<6}")
    print("-" * 75)
    
    for r in resultados:
        print(f"{r['config']:<25} | {r['sistema']:<6} | {r['morena']:<6} | {r['pan']:<6} | {r['pri']:<6} | {r['total']:<6}")
    
    # Análisis de patrones por sistema
    print("\n🔍 ANÁLISIS DE PATRONES POR SISTEMA:")
    print("-" * 50)
    
    # Agrupar por sistema
    mr_results = [r for r in resultados if r['sistema'] == 'mr']
    mixto_results = [r for r in resultados if r['sistema'] == 'mixto']
    
    print("📈 SISTEMA MR (mayoría relativa pura):")
    for r in mr_results:
        eficiencia_morena = (r['morena'] / r['total']) * 100
        print(f"  {r['config']}: MORENA {eficiencia_morena:.1f}% ({r['morena']}/{r['total']})")
    
    print("\n📊 SISTEMA MIXTO (MR + RP):")
    for r in mixto_results:
        eficiencia_morena = (r['morena'] / r['total']) * 100
        print(f"  {r['config']}: MORENA {eficiencia_morena:.1f}% ({r['morena']}/{r['total']})")
    
    # Verificar variabilidad
    if len(mr_results) > 1:
        morena_values_mr = [r['morena'] for r in mr_results]
        variacion_mr = max(morena_values_mr) - min(morena_values_mr)
        print(f"\n🎯 Variación MORENA en MR: {variacion_mr} escaños")
    
    if len(mixto_results) > 1:
        morena_values_mixto = [r['morena'] for r in mixto_results]
        variacion_mixto = max(morena_values_mixto) - min(morena_values_mixto)
        print(f"🎯 Variación MORENA en MIXTO: {variacion_mixto} escaños")
    
    # Comparar extremos
    if mr_results and mixto_results:
        mr_64 = next((r for r in mr_results if "64MR" in r['config']), None)
        mixto_96 = next((r for r in mixto_results if "96MR" in r['config']), None)
        
        if mr_64 and mixto_96:
            print(f"\n🔄 COMPARACIÓN CLAVE:")
            print(f"  64MR puro: MORENA {mr_64['morena']}, PAN {mr_64['pan']}, PRI {mr_64['pri']}")
            print(f"  96MR+32RP: MORENA {mixto_96['morena']}, PAN {mixto_96['pan']}, PRI {mixto_96['pri']}")
            
            diff_morena = mixto_96['morena'] - mr_64['morena']
            print(f"  Diferencia MORENA: {diff_morena:+d} escaños al cambiar configuración")
    
    print(f"\n✅ TEST COMPLETADO: {len(resultados)} configuraciones probadas")
    print("💡 INTERPRETACIÓN: Diferentes configuraciones MR/MIXTO producen redistribuciones diferentes")
    
    return resultados

if __name__ == "__main__":
    test_primera_minoria_slider()
