"""
Prueba directa del endpoint: 400 escaños, mitad MR (200), mitad RP (200)
SIN coaliciones, SIN topes
"""

import requests
import json

API_URL = "http://127.0.0.1:8000/procesar/diputados"

print("\n" + "="*80)
print("PRUEBA: 400 escaños, 200 MR, 200 RP, SIN coaliciones, SIN topes")
print("="*80)

payload = {
    "anio": 2024,
    "plan": "personalizado",
    "escanos_totales": 400,
    "sistema": "mixto",
    "mr_seats": 200,
    "rp_seats": 200,
    "aplicar_topes": False,
    "usar_coaliciones": False
}

print(f"\nEnviando payload:")
print(json.dumps(payload, indent=2))

response = requests.post(f"{API_URL}?anio=2024", json=payload, timeout=30)

print(f"\nStatus: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    resultados = data.get('resultados', {})
    
    # Convertir lista a dict si es necesario
    if isinstance(resultados, list):
        resultados_dict = {r['partido']: r for r in resultados}
    else:
        resultados_dict = resultados
    
    print("\n" + "="*80)
    print("RESULTADOS:")
    print("="*80)
    
    # Mostrar top partidos
    for partido in ['MORENA', 'PAN', 'PRI', 'MC', 'PT', 'PVEM']:
        if partido in resultados_dict:
            p_data = resultados_dict[partido]
            mr = p_data.get('mr', 0)
            rp = p_data.get('rp', 0)
            total = p_data.get('total', 0)
            print(f"{partido:8} -> MR: {mr:3}, RP: {rp:3}, TOTAL: {total:3}")
    
    # Verificar totales
    print("\n" + "="*80)
    print("VERIFICACIÓN:")
    print("="*80)
    
    if isinstance(resultados, list):
        total_mr = sum(p.get('mr', 0) for p in resultados)
        total_rp = sum(p.get('rp', 0) for p in resultados)
        total_escanos = sum(p.get('total', 0) for p in resultados)
    else:
        total_mr = sum(p.get('mr', 0) for p in resultados.values())
        total_rp = sum(p.get('rp', 0) for p in resultados.values())
        total_escanos = sum(p.get('total', 0) for p in resultados.values())
    
    print(f"Total MR:     {total_mr} (esperado: 200)")
    print(f"Total RP:     {total_rp} (esperado: 200)")
    print(f"Total Escaños: {total_escanos} (esperado: 400)")
    
    if total_mr == 200 and total_rp == 200 and total_escanos == 400:
        print("\n✅ TOTALES CORRECTOS")
    else:
        print("\n❌ TOTALES INCORRECTOS")
    
else:
    print(f"\n❌ Error {response.status_code}")
    print(response.text[:1000])
