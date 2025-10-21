"""
Test simple para mosprint(f"\n REQUEST:")
print(f"  POST /procesar/diputados")
print(f"  pm_seats: {payload['pm_seats']}")
print(f"  escanos_totales: {payload['escanos_totales']}")

# Usar params en lugar de json
response = client.post("/procesar/diputados", params=payload)a respuesta exacta del endpoint con PM
"""
import sys
sys.path.insert(0, '.')

from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

print("\n" + "="*80)
print("TEST: Respuesta del endpoint /procesar/diputados con PM")
print("="*80)

# Request con PM
payload = {
    "plan": "personalizado",
    "anio": 2024,
    "sistema": "mr",
    "escanos_totales": 300,
    "pm_seats": 100,
    "umbral": 0.03
}

print("\n REQUEST:")
print(f"  POST /procesar/diputados")
print(f"  pm_seats: {payload['pm_seats']}")
print(f"  escanos_totales: {payload['escanos_totales']}")

response = client.post("/procesar/diputados", json=payload)

print(f"\n RESPONSE STATUS: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    
    print(f"\n ESTRUCTURA DE LA RESPUESTA:")
    print(f"  - plan: {data.get('plan')}")
    print(f"  - resultados: array de {len(data.get('resultados', []))} partidos")
    print(f"  - kpis: {len(data.get('kpis', {}))} indicadores")
    print(f"  - seat_chart: array de {len(data.get('seat_chart', []))} partidos")
    
    print(f"\n EJEMPLO DE 1 PARTIDO (estructura):")
    if data.get('resultados'):
        primer_partido = data['resultados'][0]
        print(f"  {{")
        for key, value in primer_partido.items():
            print(f"    '{key}': {value},")
        print(f"  }}")
    
    print(f"\n TOP 5 PARTIDOS:")
    print(f"  {'Partido':<12} {'MR':<6} {'PM':<6} {'RP':<6} {'Total':<6}")
    print("  " + "-"*42)
    
    for partido in sorted(data['resultados'], key=lambda x: x['total'], reverse=True)[:5]:
        print(f"  {partido['partido']:<12} {partido['mr']:<6} {partido['pm']:<6} {partido['rp']:<6} {partido['total']:<6}")
    
    # Calcular totales
    total_mr = sum(r['mr'] for r in data['resultados'])
    total_pm = sum(r['pm'] for r in data['resultados'])
    total_rp = sum(r['rp'] for r in data['resultados'])
    total_escanos = sum(r['total'] for r in data['resultados'])
    
    print("  " + "-"*42)
    print(f"  {'TOTAL':<12} {total_mr:<6} {total_pm:<6} {total_rp:<6} {total_escanos:<6}")
    
    print(f"\n VERIFICACION:")
    print(f"  MR efectivo: {total_mr} (esperado: ~200)")
    print(f"  PM asignado: {total_pm} (esperado: 100)")
    print(f"  Total: {total_escanos} (esperado: 300)")
    
    if total_pm == 100 and total_escanos == 300:
        print(f"\n  EXITO! Backend envia datos correctos")
    else:
        print(f"\n  ADVERTENCIA: Totales no coinciden")
    
    print(f"\n KPIs:")
    for key, value in data.get('kpis', {}).items():
        print(f"  {key}: {value}")

else:
    print(f"\n ERROR: {response.text}")

print("\n" + "="*80)
