#!/usr/bin/env python3
"""
Test para confirmar valores correctos de senado
"""

import requests

BASE_URL = "https://back-electoral.onrender.com"

def test_senado_values():
    """Test con valores correctos de senado"""
    
    print("=== TEST: Valores correctos senado ===")
    
    # Test 1: Senado vigente con valores correctos
    print("\n1. SENADO VIGENTE (sistema mixto):")
    print("   - MR+PM: 96 escaños (64 MR + 32 PM)")
    print("   - RP: 32 escaños") 
    print("   - Total: 128 escaños")
    
    params_vigente = {
        "anio": 2018,
        "plan": "vigente",
        "escanos_totales": 128
    }
    
    response = requests.post(f"{BASE_URL}/procesar/senado", params=params_vigente, timeout=30)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        total = sum(p['seats'] for p in data.get('seat_chart', []))
        print(f"   ✅ Total escaños: {total}")
    
    # Test 2: Senado personalizado con valores mixto correctos
    print("\n2. SENADO PERSONALIZADO (sistema mixto):")
    print("   - mr_seats: 96 (64 MR + 32 PM)")
    print("   - rp_seats: 32")
    print("   - Total: 128")
    
    params_mixto = {
        "anio": 2018,
        "plan": "personalizado",
        "sistema": "mixto",
        "mr_seats": 96,  # 64 MR + 32 PM
        "rp_seats": 32,
        "umbral": 0.03,
        "escanos_totales": 128
    }
    
    response = requests.post(f"{BASE_URL}/procesar/senado", params=params_mixto, timeout=30)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        total = sum(p['seats'] for p in data.get('seat_chart', []))
        print(f"   ✅ Total escaños: {total}")
        
        # Mostrar distribución
        for p in data.get('seat_chart', [])[:5]:  # Primeros 5 partidos
            print(f"   {p['party']}: {p['seats']} escaños")
    else:
        print(f"   ❌ Error: {response.text}")
    
    # Test 3: Valores incorrectos (como envía el frontend)
    print("\n3. VALORES INCORRECTOS (como frontend actual):")
    print("   - mr_seats: 64 (incorrecto)")
    print("   - rp_seats: 64 (incorrecto)")
    
    params_incorrecto = {
        "anio": 2018,
        "plan": "personalizado", 
        "sistema": "mixto",
        "mr_seats": 64,  # INCORRECTO
        "rp_seats": 64,  # INCORRECTO
        "umbral": 0.03,
        "escanos_totales": 128
    }
    
    response = requests.post(f"{BASE_URL}/procesar/senado", params=params_incorrecto, timeout=30)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        total = sum(p['seats'] for p in data.get('seat_chart', []))
        print(f"   ⚠️ Total escaños: {total} (debería ser 128)")

if __name__ == "__main__":
    test_senado_values()
