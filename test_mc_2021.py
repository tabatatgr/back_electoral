#!/usr/bin/env python3
"""
Script para probar directamente el caso de diputados 2021
"""

import sys
import os
sys.path.append(os.path.abspath('.'))

from engine.procesar_diputados_v2 import procesar_diputados_v2

def test_diputados_2021():
    """Prueba específica para diputados 2021"""
    
    print("=" * 60)
    print("PROBANDO DIPUTADOS 2021 - PLAN VIGENTE")
    print("=" * 60)
    
    # Parámetros del plan vigente
    path_parquet = "data/computos_diputados_2021.parquet"
    path_siglado = "data/siglado-diputados-2021.csv"
    
    # Verificar archivos
    if not os.path.exists(path_parquet):
        print(f"❌ No existe: {path_parquet}")
        return
    if not os.path.exists(path_siglado):
        print(f"❌ No existe: {path_siglado}")
        return
    
    print(f"✅ Archivos encontrados")
    print(f"   - Parquet: {path_parquet}")
    print(f"   - Siglado: {path_siglado}")
    
    try:
        print("\n🔄 Procesando con plan VIGENTE...")
        resultado = procesar_diputados_v2(
            path_parquet=path_parquet,
            anio=2021,
            path_siglado=path_siglado,
            max_seats=500,
            sistema="mixto",
            mr_seats=None,  # NO forzar MR, usar cálculo real del siglado
            rp_seats=200,   # SÍ forzar 200 RP como en la realidad
            umbral=0.03,
            max_seats_per_party=300,
            quota_method="hare",
            divisor_method=None,
            print_debug=True
        )
        
        print("\n📊 RESULTADOS:")
        print("-" * 30)
        
        # Mostrar resultados totales
        total_dict = resultado.get('tot', {})
        votos_dict = resultado.get('votos', {})
        mr_dict = resultado.get('mr', {})
        rp_dict = resultado.get('rp', {})
        
        total_escanos = sum(total_dict.values())
        total_votos = sum(votos_dict.values())
        
        print(f"Total escaños: {total_escanos}")
        print(f"Total votos: {total_votos:,}")
        
        # Mostrar por partido (ordenado por escaños)
        partidos_ordenados = sorted(total_dict.items(), key=lambda x: x[1], reverse=True)
        
        print(f"\n{'Partido':<8} {'MR':<4} {'RP':<4} {'Tot':<4} {'%Esc':<6} {'Votos':<12} {'%Vot':<6}")
        print("-" * 60)
        
        for partido, escanos in partidos_ordenados:
            if escanos > 0:
                mr = mr_dict.get(partido, 0)
                rp = rp_dict.get(partido, 0)
                votos = votos_dict.get(partido, 0)
                pct_esc = (escanos / total_escanos) * 100 if total_escanos > 0 else 0
                pct_vot = (votos / total_votos) * 100 if total_votos > 0 else 0
                
                print(f"{partido:<8} {mr:<4} {rp:<4} {escanos:<4} {pct_esc:<6.1f} {votos:<12,} {pct_vot:<6.1f}")
        
        # Revisar específicamente MC
        mc_escanos = total_dict.get('MC', 0)
        mc_votos = votos_dict.get('MC', 0)
        mc_mr = mr_dict.get('MC', 0)
        mc_rp = rp_dict.get('MC', 0)
        
        print(f"\n🔍 ANÁLISIS DE MC:")
        print(f"   - Escaños MR: {mc_mr}")
        print(f"   - Escaños RP: {mc_rp}")
        print(f"   - Total escaños: {mc_escanos}")
        print(f"   - Votos: {mc_votos:,}")
        if total_votos > 0:
            print(f"   - % de votos: {(mc_votos/total_votos)*100:.2f}%")
        if total_escanos > 0:
            print(f"   - % de escaños: {(mc_escanos/total_escanos)*100:.2f}%")
        
        # Verificar si está aplicando tope
        if mc_escanos >= 300:
            print(f"   ⚠️  MC tiene {mc_escanos} escaños - ¿Tope aplicado?")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_diputados_2021()
