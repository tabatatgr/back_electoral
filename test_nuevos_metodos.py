#!/usr/bin/env python3
"""
Test para verificar que Webster e Imperiali funcionan
"""

import sys
sys.path.append('.')

from engine.procesar_diputados_v2 import asignar_rp_con_metodo
import numpy as np

def test_nuevos_metodos():
    """Test Webster e Imperiali"""
    votos = np.array([1000, 800, 600, 400, 200])
    escanos = 10
    
    print("🧪 Probando métodos nuevos:")
    
    # Test Webster (debe ser igual que Sainte-Laguë)
    print(f"\n🔍 Probando Webster:")
    webster_result = asignar_rp_con_metodo(
        votos=votos, 
        escanos=escanos,
        quota_method=None,
        divisor_method="webster",
        seed=42
    )
    print(f"✅ Webster: {webster_result}")
    
    print(f"\n🔍 Probando Sainte-Laguë (para comparar):")
    sl_result = asignar_rp_con_metodo(
        votos=votos, 
        escanos=escanos,
        quota_method=None,
        divisor_method="sainte_lague",
        seed=42
    )
    print(f"✅ Sainte-Laguë: {sl_result}")
    
    # Verificar que Webster = Sainte-Laguë
    if np.array_equal(webster_result, sl_result):
        print(f"✅ ¡PERFECTO! Webster = Sainte-Laguë")
    else:
        print(f"❌ ERROR: Webster ≠ Sainte-Laguë")
    
    # Test Imperiali
    print(f"\n🔍 Probando Imperiali:")
    imperiali_result = asignar_rp_con_metodo(
        votos=votos, 
        escanos=escanos,
        quota_method="imperiali",
        divisor_method=None,
        seed=42
    )
    print(f"✅ Imperiali: {imperiali_result}")
    
    # Test Hare (para comparar)
    print(f"\n🔍 Probando Hare (para comparar):")
    hare_result = asignar_rp_con_metodo(
        votos=votos, 
        escanos=escanos,
        quota_method="hare",
        divisor_method=None,
        seed=42
    )
    print(f"✅ Hare: {hare_result}")
    
    print(f"\n📊 Resumen:")
    print(f"   Votos:      {votos}")
    print(f"   Webster:    {webster_result}")
    print(f"   Sainte-L.:  {sl_result}")
    print(f"   Imperiali:  {imperiali_result}")
    print(f"   Hare:       {hare_result}")

if __name__ == "__main__":
    test_nuevos_metodos()
