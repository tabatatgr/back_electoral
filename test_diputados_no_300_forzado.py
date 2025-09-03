#!/usr/bin/env python3
"""
Test para verificar que los 300 escaños ya NO se fuercen en diputados MR puro
"""

import sys
sys.path.append('.')

from engine.procesar_diputados_v2 import procesar_diputados_v2

def test_diputados_mr_no_300_forzado():
    """Test para verificar que MR puro en diputados ya no fuerza 300 escaños"""
    
    print("🔍 TEST DIPUTADOS MR PURO - NO FORZAR 300 ESCAÑOS")
    print("=" * 60)
    
    configs = [
        {"escanos": 200, "descripcion": "200 escaños MR puro"},
        {"escanos": 250, "descripcion": "250 escaños MR puro"},
        {"escanos": 400, "descripcion": "400 escaños MR puro"},
        {"escanos": 500, "descripcion": "500 escaños MR puro"}
    ]
    
    for config in configs:
        escanos_totales = config["escanos"]
        print(f"📊 {config['descripcion']}")
        print(f"   Configuración: {escanos_totales} escaños MR puro")
        
        try:
            resultado = procesar_diputados_v2(
                path_parquet="data/computos_diputados_2018.parquet",
                anio=2018,
                path_siglado="data/siglado-diputados-2018.csv",
                sistema="mixto",  # Usar mixto pero con RP=0
                mr_seats=escanos_totales,  # El número que queremos
                rp_seats=0,  # RP = 0 para MR puro
                max_seats=escanos_totales,  # Total debe coincidir
                umbral=0.03,
                print_debug=True
            )
            
            if resultado:
                total_calculado = sum(resultado.get('tot', {}).values())
                
                print(f"   ✅ Total calculado: {total_calculado}")
                print(f"   🎯 Total solicitado: {escanos_totales}")
                
                if total_calculado == escanos_totales:
                    print(f"   ✅ CORRECTO: Respeta los {escanos_totales} escaños configurados")
                elif total_calculado == 300:
                    print(f"   ❌ ERROR: Sigue forzando 300 escaños (ignoró configuración)")
                else:
                    print(f"   ⚠️  RARO: Dio {total_calculado} escaños (ni 300 ni {escanos_totales})")
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
            
        print()
    
    print("💡 Si todos muestran '✅ CORRECTO', entonces YA NO se fuerzan 300 escaños")

if __name__ == "__main__":
    test_diputados_mr_no_300_forzado()
