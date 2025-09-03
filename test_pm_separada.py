#!/usr/bin/env python3
"""
Test de la nueva funcionalidad de primera minoría separada
"""

import requests
import json

BASE_URL = "https://back-electoral.onrender.com"

def test_pm_separada():
    """Test de primera minoría como parámetro separado"""
    
    print("=== TEST: Primera Minoría Separada ===\n")
    
    # Test 1: Sin primera minoría (PM = 0)
    print("1. SIN PRIMERA MINORÍA:")
    print("   - MR: 64, PM: 0, RP: 64")
    print("   - Total: 128")
    
    params_sin_pm = {
        "anio": 2018,
        "plan": "personalizado",
        "sistema": "mixto",
        "mr_seats": 64,     # Solo mayoría relativa
        "pm_seats": 0,      # Sin primera minoría  
        "rp_seats": 64,     # Más RP para compensar
        "umbral": 0.03
    }
    
    try:
        response = requests.post(f"{BASE_URL}/procesar/senado", params=params_sin_pm, timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            total = sum(p['seats'] for p in data.get('seat_chart', []))
            print(f"   ✅ Total escaños: {total}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print()
    
    # Test 2: Con primera minoría (PM = 32)
    print("2. CON PRIMERA MINORÍA:")
    print("   - MR: 64, PM: 32, RP: 32") 
    print("   - Total: 128")
    
    params_con_pm = {
        "anio": 2018,
        "plan": "personalizado",
        "sistema": "mixto",
        "mr_seats": 64,     # Solo mayoría relativa
        "pm_seats": 32,     # Primera minoría activa
        "rp_seats": 32,     # RP estándar
        "umbral": 0.03
    }
    
    try:
        response = requests.post(f"{BASE_URL}/procesar/senado", params=params_con_pm, timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            total = sum(p['seats'] for p in data.get('seat_chart', []))
            print(f"   ✅ Total escaños: {total}")
            
            # Mostrar primeros partidos
            for p in data.get('seat_chart', [])[:3]:
                print(f"   {p['party']}: {p['seats']} escaños")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print()
    
    # Test 3: Configuración personalizada diferente
    print("3. CONFIGURACIÓN PERSONALIZADA:")
    print("   - MR: 48, PM: 16, RP: 64")
    print("   - Total: 128")
    
    params_custom = {
        "anio": 2018,
        "plan": "personalizado", 
        "sistema": "mixto",
        "mr_seats": 48,     # Menos mayoría relativa
        "pm_seats": 16,     # Menos primera minoría
        "rp_seats": 64,     # Más proporcional
        "umbral": 0.05      # Umbral más alto
    }
    
    try:
        response = requests.post(f"{BASE_URL}/procesar/senado", params=params_custom, timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            total = sum(p['seats'] for p in data.get('seat_chart', []))
            print(f"   ✅ Total escaños: {total}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    test_pm_separada()
