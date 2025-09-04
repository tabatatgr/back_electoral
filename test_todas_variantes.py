#!/usr/bin/env python3
"""
Test completo de todas las variantes de nombres que puede enviar el frontend
"""

import sys
sys.path.append('.')

from engine.procesar_diputados_v2 import asignar_rp_con_metodo
import numpy as np

def test_todas_las_variantes():
    """Test exhaustivo de todas las variantes"""
    votos = np.array([1000, 800, 600, 400, 200])
    escanos = 10
    
    print("🧪 Test COMPLETO - Todas las variantes del frontend:")
    
    # Test métodos de DIVISOR
    print(f"\n📊 MÉTODOS DE DIVISOR:")
    divisor_variants = [
        "dhondt",
        "d_hondt", 
        "D'Hondt",
        "sainte_lague",
        "sainte-lague", 
        "saintelague",
        "SAINTE_LAGUE",
        "webster",
        "WEBSTER",
        "Webster"
    ]
    
    divisor_results = {}
    for method in divisor_variants:
        print(f"\n🔍 Probando divisor: '{method}'")
        try:
            result = asignar_rp_con_metodo(
                votos=votos, 
                escanos=escanos,
                quota_method=None,
                divisor_method=method,
                seed=42
            )
            divisor_results[method] = result
            print(f"✅ {method}: {result}")
        except Exception as e:
            print(f"❌ {method}: ERROR - {e}")
            divisor_results[method] = None
    
    # Test métodos de CUOTA  
    print(f"\n📊 MÉTODOS DE CUOTA:")
    quota_variants = [
        "hare",
        "HARE",
        "Hare",
        "droop", 
        "DROOP",
        "Droop",
        "imperiali",
        "IMPERIALI", 
        "Imperiali",
        "hb"
    ]
    
    quota_results = {}
    for method in quota_variants:
        print(f"\n🔍 Probando cuota: '{method}'")
        try:
            result = asignar_rp_con_metodo(
                votos=votos, 
                escanos=escanos,
                quota_method=method,
                divisor_method=None,
                seed=42
            )
            quota_results[method] = result
            print(f"✅ {method}: {result}")
        except Exception as e:
            print(f"❌ {method}: ERROR - {e}")
            quota_results[method] = None
    
    # Análisis de resultados
    print(f"\n📈 ANÁLISIS DE RESULTADOS:")
    
    # Agrupar resultados iguales para divisores
    dhondt_group = []
    sainte_group = []
    for method, result in divisor_results.items():
        if result is not None:
            if "dhondt" in method.lower() or "d_hondt" in method.lower():
                dhondt_group.append((method, result))
            else:
                sainte_group.append((method, result))
    
    print(f"\n🎯 Grupo D'Hondt ({len(dhondt_group)} variantes):")
    for method, result in dhondt_group:
        print(f"   {method}: {result}")
    
    print(f"\n🎯 Grupo Sainte-Laguë/Webster ({len(sainte_group)} variantes):")
    for method, result in sainte_group:
        print(f"   {method}: {result}")
    
    # Verificar consistencia
    dhondt_consistent = len(set(str(r) for _, r in dhondt_group)) <= 1
    sainte_consistent = len(set(str(r) for _, r in sainte_group)) <= 1
    
    print(f"\n✅ Consistencia D'Hondt: {'SÍ' if dhondt_consistent else 'NO'}")
    print(f"✅ Consistencia Sainte-Laguë: {'SÍ' if sainte_consistent else 'NO'}")
    
    # Verificar cuotas
    hare_results = [r for m, r in quota_results.items() if 'hare' in m.lower() and r is not None]
    droop_results = [r for m, r in quota_results.items() if 'droop' in m.lower() and r is not None]
    imperiali_results = [r for m, r in quota_results.items() if 'imperiali' in m.lower() and r is not None]
    
    hare_consistent = len(set(str(r) for r in hare_results)) <= 1
    droop_consistent = len(set(str(r) for r in droop_results)) <= 1 
    imperiali_consistent = len(set(str(r) for r in imperiali_results)) <= 1
    
    print(f"✅ Consistencia Hare: {'SÍ' if hare_consistent else 'NO'}")
    print(f"✅ Consistencia Droop: {'SÍ' if droop_consistent else 'NO'}")
    print(f"✅ Consistencia Imperiali: {'SÍ' if imperiali_consistent else 'NO'}")

if __name__ == "__main__":
    test_todas_las_variantes()
