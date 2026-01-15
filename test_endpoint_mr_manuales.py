"""
Test de integración completo del endpoint /procesar/diputados
con el parámetro mr_distritos_manuales
"""

import requests
import json

# URL del servidor (ajustar si es necesario)
BASE_URL = "http://localhost:8000"

def test_mr_manuales_endpoint():
    print("=" * 80)
    print("TEST DE INTEGRACIÓN: mr_distritos_manuales en endpoint")
    print("=" * 80)
    
    # Test 1: Con MR manuales
    print("\n[TEST 1] Ejecutando con MR manuales...")
    
    mr_manuales = {
        "MORENA": 200,
        "PAN": 50,
        "PRI": 30,
        "PVEM": 10,
        "PT": 5,
        "MC": 5
    }
    
    payload = {
        "anio": 2024,
        "plan": "300_100_sin_topes",
        "mr_distritos_manuales": json.dumps(mr_manuales)
    }
    
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/procesar/diputados", json=payload)
        
        if response.status_code == 200:
            resultado = response.json()
            print("\n✅ Respuesta exitosa (200)")
            print(f"\nResultados MR:")
            for partido, mr in resultado['mr'].items():
                mr_esperado = mr_manuales.get(partido, 0)
                match = "✓" if mr == mr_esperado else "✗"
                print(f"  {match} {partido}: {mr} MR (esperado: {mr_esperado})")
        else:
            print(f"\n❌ Error: HTTP {response.status_code}")
            print(f"Respuesta: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("\n⚠️  No se pudo conectar al servidor")
        print("   Asegúrate de que el servidor esté corriendo en", BASE_URL)
        print("   Puedes iniciarlo con: uvicorn main:app --reload")
        return
    
    # Test 2: Sin MR manuales (automático)
    print("\n" + "=" * 80)
    print("[TEST 2] Ejecutando sin MR manuales (cálculo automático)...")
    
    payload_auto = {
        "anio": 2024,
        "plan": "300_100_sin_topes"
        # Sin mr_distritos_manuales
    }
    
    print(f"Payload: {json.dumps(payload_auto, indent=2)}")
    
    try:
        response_auto = requests.post(f"{BASE_URL}/procesar/diputados", json=payload_auto)
        
        if response_auto.status_code == 200:
            resultado_auto = response_auto.json()
            print("\n✅ Respuesta exitosa (200)")
            print(f"\nResultados MR (automáticos):")
            for partido, mr in resultado_auto['mr'].items():
                print(f"  {partido}: {mr} MR")
        else:
            print(f"\n❌ Error: HTTP {response_auto.status_code}")
            print(f"Respuesta: {response_auto.text}")
    
    except requests.exceptions.ConnectionError:
        print("\n⚠️  No se pudo conectar al servidor")
        return
    
    # Test 3: Validación de suma excedida
    print("\n" + "=" * 80)
    print("[TEST 3] Validando error cuando suma de MR excede total...")
    
    mr_invalidos = {
        "MORENA": 250,
        "PAN": 100,
        "PRI": 80  # Total: 430 > 300
    }
    
    payload_invalido = {
        "anio": 2024,
        "plan": "300_100_sin_topes",
        "mr_distritos_manuales": json.dumps(mr_invalidos)
    }
    
    print(f"Payload: {json.dumps(payload_invalido, indent=2)}")
    
    try:
        response_invalido = requests.post(f"{BASE_URL}/procesar/diputados", json=payload_invalido)
        
        if response_invalido.status_code == 400:
            print("\n✅ Validación correcta: HTTP 400 (Bad Request)")
            print(f"Mensaje de error: {response_invalido.json().get('detail', '')}")
        else:
            print(f"\n❌ Se esperaba HTTP 400, pero se obtuvo: {response_invalido.status_code}")
    
    except requests.exceptions.ConnectionError:
        print("\n⚠️  No se pudo conectar al servidor")
        return
    
    # Test 4: JSON inválido
    print("\n" + "=" * 80)
    print("[TEST 4] Validando error con JSON inválido...")
    
    payload_json_invalido = {
        "anio": 2024,
        "plan": "300_100_sin_topes",
        "mr_distritos_manuales": "esto no es un json valido"
    }
    
    print(f"Payload: {json.dumps(payload_json_invalido, indent=2)}")
    
    try:
        response_json_invalido = requests.post(f"{BASE_URL}/procesar/diputados", json=payload_json_invalido)
        
        if response_json_invalido.status_code == 400:
            print("\n✅ Validación correcta: HTTP 400 (Bad Request)")
            print(f"Mensaje de error: {response_json_invalido.json().get('detail', '')}")
        else:
            print(f"\n❌ Se esperaba HTTP 400, pero se obtuvo: {response_json_invalido.status_code}")
    
    except requests.exceptions.ConnectionError:
        print("\n⚠️  No se pudo conectar al servidor")
        return
    
    print("\n" + "=" * 80)
    print("TESTS DE INTEGRACIÓN COMPLETADOS")
    print("=" * 80)

if __name__ == "__main__":
    test_mr_manuales_endpoint()
