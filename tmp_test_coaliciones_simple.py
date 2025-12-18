"""
Script simplificado para verificar el comportamiento del parámetro usar_coaliciones
"""

import requests
import json

API_URL = "http://127.0.0.1:8000/procesar/diputados"

# PRUEBA 1: usar_coaliciones=True
print("\n" + "="*80)
print("PRUEBA 1: usar_coaliciones=True")
print("="*80)

try:
    response1 = requests.post(
        f"{API_URL}?anio=2024&plan=vigente&aplicar_topes=false&usar_coaliciones=true",
        timeout=30
    )
    print(f"Status: {response1.status_code}")
    if response1.status_code == 200:
        resultado1 = response1.json()
        morena = resultado1.get('resultados', {}).get('MORENA', {})
        print(f"MORENA: MR={morena.get('mr', 0)}, RP={morena.get('rp', 0)}, TOTAL={morena.get('total', 0)}")
    else:
        print(f"Error: {response1.text[:500]}")
except Exception as e:
    print(f"Error de conexión: {e}")

# PRUEBA 2: usar_coaliciones=False
print("\n" + "="*80)
print("PRUEBA 2: usar_coaliciones=False")
print("="*80)

try:
    response2 = requests.post(
        f"{API_URL}?anio=2024&plan=vigente&aplicar_topes=false&usar_coaliciones=false",
        timeout=30
    )
    print(f"Status: {response2.status_code}")
    if response2.status_code == 200:
        resultado2 = response2.json()
        morena = resultado2.get('resultados', {}).get('MORENA', {})
        print(f"MORENA: MR={morena.get('mr', 0)}, RP={morena.get('rp', 0)}, TOTAL={morena.get('total', 0)}")
    else:
        print(f"Error: {response2.text[:500]}")
except Exception as e:
    print(f"Error de conexión: {e}")
