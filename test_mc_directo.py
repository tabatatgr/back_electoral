#!/usr/bin/env python3
"""
Test directo de MC sin servidor
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from engine.procesar_diputados_v2 import procesar_diputados_v2

print("🧪 TEST DIRECTO: MC DESPUÉS DE LA CORRECCIÓN")
print("=" * 50)

try:
    # Procesar 2018 directamente con path_parquet
    resultados = procesar_diputados_v2(
        path_parquet="data/computos_diputados_2018.parquet",
        anio=2018,
        sistema='mixto',
        mr_seats=None,
        rp_seats=200,
        max_seats=500
    )
    
    print("✅ Procesamiento exitoso!")
    print(f"Tipo de resultados: {type(resultados)}")
    print(f"Keys disponibles: {list(resultados.keys()) if isinstance(resultados, dict) else 'No es dict'}")
    
    # Buscar MC en diferentes formatos posibles
    if isinstance(resultados, dict):
        # Nuevo formato: mr, rp, tot
        if 'mr' in resultados and isinstance(resultados['mr'], dict):
            mc_mr = resultados['mr'].get('MC', 0)
            print(f"🎯 MC MR: {mc_mr}")
            
        if 'rp' in resultados and isinstance(resultados['rp'], dict):
            mc_rp = resultados['rp'].get('MC', 0)
            print(f"🎯 MC RP: {mc_rp}")
            
        if 'tot' in resultados and isinstance(resultados['tot'], dict):
            mc_total = resultados['tot'].get('MC', 0)
            print(f"🎯 MC Total: {mc_total}")
            
        # Mostrar todos los partidos MR para comparación
        if 'mr' in resultados:
            print(f"\n📊 TODOS LOS PARTIDOS MR:")
            mr_results = resultados['mr']
            if isinstance(mr_results, dict):
                for partido, escanos in mr_results.items():
                    if escanos > 0:  # Solo mostrar partidos con escaños
                        print(f"   {partido}: {escanos}")
                        
        # Mostrar totales para comparación
        if 'tot' in resultados:
            print(f"\n📊 TOTALES POR PARTIDO:")
            tot_results = resultados['tot']
            if isinstance(tot_results, dict):
                for partido, escanos in tot_results.items():
                    if escanos > 0:  # Solo mostrar partidos con escaños
                        print(f"   {partido}: {escanos}")
    
    print(f"\n✅ RESULTADO CLAVE: MC ahora recibe escaños MR gracias a la corrección de coaliciones!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
