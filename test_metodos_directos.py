#!/usr/bin/env python3
"""
Test específico para verificar que los métodos de reparto funcionen correctamente
"""

import sys
sys.path.append('.')
import numpy as np

# Importar funciones directamente
from engine.core import largest_remainder, divisor_apportionment
from engine.procesar_diputados_v2 import asignar_rp_con_metodo

def test_metodos_directos():
    """Test directo de los métodos de asignación"""
    
    print("🔍 TEST MÉTODOS DE ASIGNACIÓN DIRECTOS")
    print("=" * 45)
    
    # Datos de prueba simplificados
    votos = np.array([
        21741037,  # MORENA
        10165244,  # PAN  
        9112625,   # PRI
        3163824,   # PRD
        2623767,   # PVEM
        2595279,   # PT
        258125,    # MC
        626393,    # PES
        89844      # NA
    ], dtype=float)
    
    partidos = ["MORENA", "PAN", "PRI", "PRD", "PVEM", "PT", "MC", "PES", "NA"]
    escanos = 200
    umbral = 0.03
    
    print(f"📊 Votos totales: {int(np.sum(votos)):,}")
    print(f"🎯 Escaños: {escanos}")
    print(f"🚪 Umbral: {umbral*100}%")
    print()
    
    # Aplicar umbral
    total_votos = np.sum(votos)
    umbral_votos = votos / total_votos >= umbral
    votos_elegibles = votos.copy()
    votos_elegibles[~umbral_votos] = 0
    
    print("📋 PARTIDOS QUE PASAN UMBRAL:")
    for i, partido in enumerate(partidos):
        if umbral_votos[i]:
            pct = (votos[i] / total_votos) * 100
            print(f"   ✅ {partido}: {int(votos[i]):,} votos ({pct:.2f}%)")
        else:
            pct = (votos[i] / total_votos) * 100
            print(f"   ❌ {partido}: {int(votos[i]):,} votos ({pct:.2f}%) - Bajo umbral")
    print()
    
    print("1️⃣ MÉTODO CUOTA HARE (core.py)")
    resultado_hare_core = largest_remainder(votos_elegibles, escanos, "hare")
    total_hare_core = int(np.sum(resultado_hare_core))
    print(f"   ✅ Total: {total_hare_core}")
    for i, partido in enumerate(partidos):
        if resultado_hare_core[i] > 0:
            print(f"   📈 {partido}: {int(resultado_hare_core[i])}")
    
    print()
    print("2️⃣ MÉTODO DIVISOR D'HONDT (core.py)")
    resultado_dhondt_core = divisor_apportionment(votos_elegibles, escanos, "dhondt")
    total_dhondt_core = int(np.sum(resultado_dhondt_core))
    print(f"   ✅ Total: {total_dhondt_core}")
    for i, partido in enumerate(partidos):
        if resultado_dhondt_core[i] > 0:
            print(f"   📈 {partido}: {int(resultado_dhondt_core[i])}")
    
    print()
    print("3️⃣ FUNCIÓN WRAPPER - MODO CUOTA")
    resultado_wrapper_cuota = asignar_rp_con_metodo(
        votos=votos_elegibles,
        escanos=escanos,
        quota_method="hare",
        divisor_method=None
    )
    total_wrapper_cuota = int(np.sum(resultado_wrapper_cuota))
    print(f"   ✅ Total: {total_wrapper_cuota}")
    for i, partido in enumerate(partidos):
        if resultado_wrapper_cuota[i] > 0:
            print(f"   📈 {partido}: {int(resultado_wrapper_cuota[i])}")
    
    print()
    print("4️⃣ FUNCIÓN WRAPPER - MODO DIVISOR")
    resultado_wrapper_divisor = asignar_rp_con_metodo(
        votos=votos_elegibles,
        escanos=escanos,
        quota_method=None,
        divisor_method="dhondt"
    )
    total_wrapper_divisor = int(np.sum(resultado_wrapper_divisor))
    print(f"   ✅ Total: {total_wrapper_divisor}")
    for i, partido in enumerate(partidos):
        if resultado_wrapper_divisor[i] > 0:
            print(f"   📈 {partido}: {int(resultado_wrapper_divisor[i])}")
    
    print()
    print("🔄 VERIFICACIONES:")
    
    # Verificar que core.py y wrapper dan los mismos resultados
    coincidencias_hare = np.array_equal(resultado_hare_core, resultado_wrapper_cuota)
    coincidencias_dhondt = np.array_equal(resultado_dhondt_core, resultado_wrapper_divisor)
    
    if coincidencias_hare:
        print("   ✅ HARE: core.py y wrapper coinciden perfectamente")
    else:
        print("   ❌ HARE: Diferencias entre core.py y wrapper")
        for i, partido in enumerate(partidos):
            if resultado_hare_core[i] != resultado_wrapper_cuota[i]:
                print(f"      {partido}: core={resultado_hare_core[i]}, wrapper={resultado_wrapper_cuota[i]}")
    
    if coincidencias_dhondt:
        print("   ✅ D'HONDT: core.py y wrapper coinciden perfectamente")
    else:
        print("   ❌ D'HONDT: Diferencias entre core.py y wrapper")
        for i, partido in enumerate(partidos):
            if resultado_dhondt_core[i] != resultado_wrapper_divisor[i]:
                print(f"      {partido}: core={resultado_dhondt_core[i]}, wrapper={resultado_wrapper_divisor[i]}")

if __name__ == "__main__":
    test_metodos_directos()
