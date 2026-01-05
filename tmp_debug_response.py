"""
Debug simple para ver qué responde el API
"""
import requests
import json

payload = {
    "anio": "2024",
    "plan": "personalizado",
    "escanos_totales": 400,
    "sistema": "mixto",
    "mr_seats": 200,
    "rp_seats": 200,
    "aplicar_topes": False,
    "usar_coaliciones": False,
    "umbral": 0.0
}

try:
    response = requests.post("http://localhost:8000/procesar/diputados", json=payload, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"\nResponse:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False)[:2000])
except Exception as e:
    print(f"Error: {e}")
