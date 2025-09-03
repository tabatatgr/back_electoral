#!/usr/bin/env python3
"""
Test para verificar que el toggle de coaliciones funciona correctamente
"""

import sys
sys.path.append('.')

from engine.procesar_diputados_v2 import procesar_diputados_v2

def test_toggle_coaliciones():
    """Test para verificar que el toggle de coaliciones cambia los resultados"""
    
    print("🔍 TEST TOGGLE DE COALICIONES")
    print("=" * 50)
    print("Probando: coaliciones ON vs coaliciones OFF")
    print()
    
    # Configuración base
    config_base = {
        "path_parquet": "data/computos_diputados_2018.parquet",
        "anio": 2018,
        "path_siglado": "data/siglado-diputados-2018.csv",
        "sistema": "mixto",
        "mr_seats": 300,
        "rp_seats": 200,
        "max_seats": 500,
        "umbral": 0.03,
        "print_debug": True
    }
    
    print("📊 COALICIONES ON (actual - usar siglado)")
    try:
        resultado_con_coaliciones = procesar_diputados_v2(
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
    print("📊 COALICIONES OFF (nuevo - partido individual gana)")
    try:
        resultado_sin_coaliciones = procesar_diputados_v2(
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
    print("🔄 COMPARACIÓN DE RESULTADOS:")
    
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
                print("   ✅ FUNCIONA: Las coaliciones ON/OFF producen resultados diferentes")
                print("   💡 El toggle está funcionando correctamente")
            else:
                print()
                print("   ⚠️  PROBLEMA: Los resultados son idénticos")
                print("   ❌ El toggle no está funcionando")
        
    except Exception as e:
        print(f"   ❌ Error comparando resultados: {e}")

if __name__ == "__main__":
    test_toggle_coaliciones()
