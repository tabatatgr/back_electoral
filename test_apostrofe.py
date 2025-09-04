#!/usr/bin/env python3
"""
Test rápido del apóstrofe
"""

import sys
sys.path.append('.')

from engine.procesar_diputados_v2 import asignar_rp_con_metodo
import numpy as np

def test_apostrofe():
    votos = np.array([1000, 800, 600, 400, 200])
    escanos = 10
    
    print("🧪 Test del apóstrofe:")
    result = asignar_rp_con_metodo(
        votos=votos, 
        escanos=escanos,
        quota_method=None,
        divisor_method="D'Hondt",
        seed=42
    )
    print(f"✅ D'Hondt: {result}")

if __name__ == "__main__":
    test_apostrofe()
