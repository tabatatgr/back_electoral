#!/usr/bin/env python3
"""
Test para verificar que el fix de sainte_lague funciona
"""

# Importar la función arreglada
import sys
sys.path.append('.')

from engine.procesar_diputados_v2 import asignar_rp_con_metodo
import numpy as np

def test_sainte_lague_variants():
    """Test todas las variantes de Sainte-Laguë"""
    votos = np.array([1000, 800, 600, 400, 200])
    escanos = 10
    
    print("🧪 Probando variantes de Sainte-Laguë:")
    
    variants = [
        "sainte_lague",    # Con guión bajo (frontend)
        "sainte-lague",    # Con guión (frontend alt)
        "saintelague",     # Sin guión (core.py)
        "SAINTE_LAGUE",    # Mayúsculas
    ]
    
    results = {}
    
    for variant in variants:
        print(f"\n🔍 Probando: '{variant}'")
        try:
            result = asignar_rp_con_metodo(
                votos=votos, 
                escanos=escanos,
                quota_method=None,
                divisor_method=variant,
                seed=42
            )
            results[variant] = result
            print(f"✅ Resultado: {result}")
        except Exception as e:
            print(f"❌ Error: {e}")
            results[variant] = None
    
    # Verificar que todas las variantes dan el mismo resultado
    valid_results = [r for r in results.values() if r is not None]
    
    if len(valid_results) > 1:
        first_result = valid_results[0]
        all_same = all(np.array_equal(first_result, result) for result in valid_results)
        
        if all_same:
            print(f"\n✅ ¡PERFECTO! Todas las variantes dan el mismo resultado:")
            print(f"   Resultado: {first_result}")
        else:
            print(f"\n❌ ERROR: Las variantes dan resultados diferentes")
            for variant, result in results.items():
                print(f"   {variant}: {result}")
    else:
        print(f"\n❌ Solo {len(valid_results)} variante(s) funcionaron")

if __name__ == "__main__":
    test_sainte_lague_variants()
