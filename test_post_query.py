#!/usr/bin/env python3
"""
Test para confirmar el formato correcto de requests
"""

import requests

# URL base del backend
BASE_URL = "https://back-electoral.onrender.com"

def test_correct_format():
    """Test del formato correcto para POST con query params"""
    
    print("=== TEST: POST con query parameters ===")
    
    # Test SENADO - POST con query params
    url_senado = f"{BASE_URL}/procesar/senado"
    params_senado = {
        "anio": 2018,
        "plan": "vigente", 
        "escanos_totales": 128
    }
    
    try:
        response = requests.post(url_senado, params=params_senado, timeout=30)
        print(f"SENADO - Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ SENADO funciona con POST + query params")
        else:
            print(f"❌ SENADO Error: {response.text}")
    except Exception as e:
        print(f"❌ SENADO Exception: {e}")
    
    # Test DIPUTADOS - POST con query params
    url_diputados = f"{BASE_URL}/procesar/diputados"
    params_diputados = {
        "anio": 2018,
        "plan": "vigente",
        "escanos_totales": 500
    }
    
    try:
        response = requests.post(url_diputados, params=params_diputados, timeout=30)
        print(f"DIPUTADOS - Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ DIPUTADOS funciona con POST + query params")
        else:
            print(f"❌ DIPUTADOS Error: {response.text}")
    except Exception as e:
        print(f"❌ DIPUTADOS Exception: {e}")

if __name__ == "__main__":
    test_correct_format()
