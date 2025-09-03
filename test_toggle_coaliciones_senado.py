#!/usr/bin/env python3
"""
Test para verificar que el toggle de coaliciones funciona en SENADO
"""

import sys
sys.path.append('.')

from engine.procesar_senadores_v2 import procesar_senadores_v2

def test_toggle_coaliciones_senado():
    """Test para verificar que el toggle de coaliciones cambia los resultados en SENADO"""
    
    print("🔍 TEST TOGGLE DE COALICIONES - SENADO")
    print("=" * 55)
    print("Probando: coaliciones ON vs coaliciones OFF en senado")
    print()
    
    # Configuración base para senado
    config_base = {
        "path_parquet": "data/computos_senado_2018.parquet",
        "anio": 2018,
        "path_siglado": "data/siglado_senado_2018_corregido.csv",
        "sistema": "mixto",
        "mr_seats": 64,
        "rp_seats": 64,
        "max_seats": 128,
        "umbral": 0.03
    }
    
    print("📊 SENADO COALICIONES ON (usar siglado)")
    try:
        resultado_con_coaliciones = procesar_senadores_v2(
            **config_base,
            usar_coaliciones=True
        )
        
        if resultado_con_coaliciones and 'tot' in resultado_con_coaliciones:
            escanos_con = resultado_con_coaliciones['tot']
            total_con = sum(escanos_con.values())
            print(f"   ✅ Total escaños: {total_con}")
            print(f"   📈 Distribución: {dict(escanos_con)}")
        else:
            print(f"   ❌ Error en resultado con coaliciones")
            
    except Exception as e:
        print(f"   ❌ Error con coaliciones: {e}")
    
    print()
    print("📊 SENADO COALICIONES OFF (partido individual)")
    try:
        resultado_sin_coaliciones = procesar_senadores_v2(
            **config_base,
            usar_coaliciones=False
        )
        
        if resultado_sin_coaliciones and 'tot' in resultado_sin_coaliciones:
            escanos_sin = resultado_sin_coaliciones['tot']
            total_sin = sum(escanos_sin.values())
            print(f"   ✅ Total escaños: {total_sin}")
            print(f"   📈 Distribución: {dict(escanos_sin)}")
        else:
            print(f"   ❌ Error en resultado sin coaliciones")
            
    except Exception as e:
        print(f"   ❌ Error sin coaliciones: {e}")
    
    print()
    print("🔄 COMPARACIÓN DE RESULTADOS SENADO:")
    
    try:
        if resultado_con_coaliciones and resultado_sin_coaliciones:
            escanos_con = resultado_con_coaliciones['tot']
            escanos_sin = resultado_sin_coaliciones['tot']
            
            print("   Partido | CON coaliciones | SIN coaliciones | Diferencia")
            print("   --------|-----------------|-----------------|----------")
            
            partidos = set(escanos_con.keys()) | set(escanos_sin.keys())
            cambios_detectados = False
            
            for partido in sorted(partidos):
                con = escanos_con.get(partido, 0)
                sin = escanos_sin.get(partido, 0)
                diff = sin - con
                
                if diff != 0:
                    cambios_detectados = True
                    print(f"   Partido {partido:2} | {con:15} | {sin:15} | {diff:+9}")
                else:
                    print(f"   Partido {partido:2} | {con:15} | {sin:15} | {diff:9}")
            
            if cambios_detectados:
                print()
                print("   ✅ FUNCIONA: Las coaliciones ON/OFF producen resultados diferentes en SENADO")
                print("   💡 El toggle está funcionando correctamente para senado")
            else:
                print()
                print("   ⚠️  PROBLEMA: Los resultados son idénticos en SENADO")
                print("   ❌ El toggle no está funcionando para senado")
        
    except Exception as e:
        print(f"   ❌ Error comparando resultados: {e}")

if __name__ == "__main__":
    test_toggle_coaliciones_senado()
