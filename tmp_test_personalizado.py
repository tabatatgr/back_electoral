"""
Simula lo que hace el frontend cuando selecciona "Personalizado" y compara respuestas con/sin votos_custom
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("TEST: Personalizado - SIN votos_custom")
params1 = {
    "anio": 2024,
    "sistema": "mixto",
    "plan": "personalizado",
    "usar_coaliciones": True,
    "escanos_totales": 500,
    "mr_seats": 300,
    "rp_seats": 200
}
resp1 = requests.post(f"{BASE_URL}/procesar/diputados", params=params1, timeout=30)
print("Status:", resp1.status_code)
try:
    print(json.dumps(resp1.json(), indent=2)[:1000])
except Exception:
    print("No JSON or too large")

print('\n' + '='*60 + '\n')

print("TEST: Personalizado - CON votos_custom")
params2 = params1.copy()
params2["plan"] = "personalizado"

body = {
    "votos_custom": {
        "MORENA": 30000000,
        "PAN": 8000000,
        "PRI": 5000000,
        "PVEM": 4000000,
        "PT": 3000000,
        "MC": 6000000,
        "PRD": 1000000
    }
}
resp2 = requests.post(f"{BASE_URL}/procesar/diputados", params=params2, json=body, timeout=30)
print("Status:", resp2.status_code)
try:
    print(json.dumps(resp2.json(), indent=2)[:1000])
except Exception:
    print("No JSON or too large")
