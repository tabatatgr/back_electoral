#!/usr/bin/env python3
"""
Test para verificar el nuevo sistema de reparto EXCLUSIVO (cuota O divisor)
"""

import sys
sys.path.append('.')

from engine.procesar_diputados_v2 import procesar_diputados_v2

def test_sistema_reparto_exclusivo():
    """Test para verificar que el sistema solo usa cuota O divisor, no ambos"""
    
    print(" TEST SISTEMA DE REPARTO EXCLUSIVO")
    print("=" * 50)
    print("Probando: Modo cuota vs Modo divisor")
    print()
    
    # Configuración base para diputados personalizado
    config_base = {
        "path_parquet": "data/computos_diputados_2018.parquet",
        "anio": 2018,
        "path_siglado": "data/siglado-diputados-2018.csv",
        "max_seats": 300,
        "sistema": "rp",  # Solo RP para ver claramente el efecto
        "mr_seats": 0,
        "rp_seats": 300,
        "umbral": 0.03,
        "usar_coaliciones": True
    }
    
    print(" MODO CUOTA - HARE")
    try:
        resultado_cuota = procesar_diputados_v2(
            **config_base,
            quota_method="hare",
            divisor_method=None  # ⬅ DEBE SER None cuando usas cuota
        )
        
        if resultado_cuota and 'tot' in resultado_cuota:
            escanos_cuota = resultado_cuota['tot']
            total_cuota = sum(escanos_cuota.values())
            print(f"    Total escaños (Cuota Hare): {total_cuota}")
            print(f"    Top 3: {dict(list(sorted(escanos_cuota.items(), key=lambda x: x[1], reverse=True))[:3])}")
        else:
            print(f"    Error en resultado con cuota")
            
    except Exception as e:
        print(f"    Error con cuota: {e}")
    
    print()
    print(" MODO DIVISOR - D'HONDT")
    try:
        resultado_divisor = procesar_diputados_v2(
            **config_base,
            quota_method=None,  #  DEBE SER None cuando usas divisor
            divisor_method="dhondt"
        )
        
        if resultado_divisor and 'tot' in resultado_divisor:
            escanos_divisor = resultado_divisor['tot']
            total_divisor = sum(escanos_divisor.values())
            print(f"    Total escaños (Divisor D'Hondt): {total_divisor}")
            print(f"   Top 3: {dict(list(sorted(escanos_divisor.items(), key=lambda x: x[1], reverse=True))[:3])}")
        else:
            print(f"    Error en resultado con divisor")
            
    except Exception as e:
        print(f"    Error con divisor: {e}")
    
    print()
    print(" COMPARACIÓN DE RESULTADOS:")
    
    try:
        if resultado_cuota and resultado_divisor:
            escanos_cuota = resultado_cuota['tot']
            escanos_divisor = resultado_divisor['tot']
            
            print("   Partido | Cuota HARE | Divisor D'HONDT | Diferencia")
            print("   --------|------------|-----------------|----------")
            
            partidos = set(escanos_cuota.keys()) | set(escanos_divisor.keys())
            cambios_detectados = False
            
            for partido in sorted(partidos):
                cuota = escanos_cuota.get(partido, 0)
                divisor = escanos_divisor.get(partido, 0)
                diff = divisor - cuota
                
                if diff != 0:
                    cambios_detectados = True
                    print(f"   {partido:7} | {cuota:10} | {divisor:15} | {diff:+9}")
                else:
                    print(f"   {partido:7} | {cuota:10} | {divisor:15} | {diff:9}")
            
            if cambios_detectados:
                print()
                print("    FUNCIONA: Cuota vs Divisor producen resultados diferentes")
                print("    El sistema de reparto exclusivo está funcionando")
            else:
                print()
                print("     IGUALES: Los métodos producen resultados idénticos")
                print("    Esto puede ser normal con estos datos específicos")
    
    except Exception as e:
        print(f"    Error comparando resultados: {e}")

    print()
    print(" PROBANDO OTROS MÉTODOS:")
    
    # Test Cuota Droop
    print("\n CUOTA DROOP vs D'HONDT")
    try:
        resultado_droop = procesar_diputados_v2(
            **config_base,
            quota_method="droop",
            divisor_method=None
        )
        
        if resultado_droop and 'tot' in resultado_droop:
            escanos_droop = resultado_droop['tot']
            total_droop = sum(escanos_droop.values())
            print(f"    Cuota Droop: {total_droop} escaños")
            
            # Comparar Droop vs D'Hondt
            top_droop = dict(list(sorted(escanos_droop.items(), key=lambda x: x[1], reverse=True))[:3])
            print(f"    Top 3 Droop: {top_droop}")
            
            if resultado_divisor and 'tot' in resultado_divisor:
                top_dhondt = dict(list(sorted(resultado_divisor['tot'].items(), key=lambda x: x[1], reverse=True))[:3])
                print(f"    Top 3 D'Hondt: {top_dhondt}")
        
    except Exception as e:
        print(f"    Error con Droop: {e}")

if __name__ == "__main__":
    test_sistema_reparto_exclusivo()
