import json
import traceback
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, r"c:\Users\pablo\OneDrive\Documentos\GitHub\back_electoral")
import main

client = TestClient(main.app)

mr_por_estado = {
    "14": {"MORENA": 3, "MC": 0, "PAN": 0, "PRI": 0, "PRD": 0, "PVEM": 0, "PT": 0},
    "1": {"MORENA": 0, "MC": 0, "PAN": 0, "PRI": 0, "PRD": 0, "PVEM": 0, "PT": 1}
}

payload = {
    "plan": "vigente",
    "mr_distritos_por_estado": mr_por_estado
}

print("Posting payload to /procesar/senado (TestClient):")
try:
    resp = client.post('/procesar/senado?anio=2024', json=payload)
    print("Status code:", resp.status_code)
    try:
        rj = resp.json()
        print("meta.mr_por_estado keys:", list(rj.get('meta', {}).get('mr_por_estado', {}).keys()))
        print("JALISCO entry:", rj.get('meta', {}).get('mr_por_estado', {}).get('JALISCO'))
    except Exception:
        print("Response text:")
        print(resp.text[:4000])
except Exception:
    traceback.print_exc()
