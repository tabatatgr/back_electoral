"""
Test simple para generar logs en el servidor
"""

import requests

response = requests.post(
    "http://127.0.0.1:8000/procesar/diputados?anio=2024",
    json={
        "plan": "personalizado",
        "escanos_totales": 400,
        "sistema": "mixto",
        "mr_seats": 200,
        "rp_seats": 200,
        "aplicar_topes": False,
        "usar_coaliciones": False
    },
    timeout=30
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    morena = [r for r in data['resultados'] if r['partido'] == 'MORENA'][0]
    print(f"MORENA: MR={morena['mr']}, RP={morena['rp']}, TOTAL={morena['total']}")
    print("\n⚠️  Revisar los logs del servidor para ver los parámetros enviados al motor")
