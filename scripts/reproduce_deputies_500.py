import json
import traceback
import sys
from fastapi.testclient import TestClient

# Asegurar que el directorio raíz del proyecto esté en sys.path para poder importar main
sys.path.insert(0, r"c:\Users\pablo\OneDrive\Documentos\GitHub\back_electoral")
import main

client = TestClient(main.app)

# Construir un override simple: solo Jalisco (id 14) con MORENA +1 (y un estado de respaldo para evitar total=0)
mr_por_estado = {
    "14": {"MORENA": 3, "MC": 0, "PAN": 0, "PRI": 0, "PRD": 0, "PVEM": 0, "PT": 0},
    "1": {"MORENA": 0, "MC": 0, "PAN": 0, "PRI": 0, "PRD": 0, "PVEM": 0, "PT": 1}
}

payload = {
    "plan": "vigente",
    # En el endpoint main.py el campo esperado es mr_distritos_por_estado (string JSON o dict)
    "mr_distritos_por_estado": json.dumps(mr_por_estado)
}

print("Posting payload to /procesar/diputados:")
print(json.dumps(payload, indent=2)[:1000])

try:
    # 'anio' es un parámetro de query en el endpoint
    resp = client.post('/procesar/diputados?anio=2024', json=payload)
    print("Status code:", resp.status_code)
    try:
        print(json.dumps(resp.json(), indent=2)[:4000])
    except Exception:
        print("Response text:")
        print(resp.text[:4000])
except Exception as e:
    print("Exception raised when calling endpoint:")
    traceback.print_exc()
