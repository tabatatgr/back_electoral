"""
Comparación CON y SIN coaliciones
400 escaños, 200 MR, 200 RP, SIN topes
"""

import requests
import json

API_URL = "http://127.0.0.1:8000/procesar/diputados"

# PRUEBA 1: CON coaliciones
print("\n" + "="*80)
print("PRUEBA 1: CON COALICIONES")
print("="*80)

payload1 = {
    "plan": "personalizado",
    "escanos_totales": 400,
    "sistema": "mixto",
    "mr_seats": 200,
    "rp_seats": 200,
    "aplicar_topes": False,
    "usar_coaliciones": True  # CON
}

response1 = requests.post(f"{API_URL}?anio=2024", json=payload1, timeout=30)

if response1.status_code == 200:
    data1 = response1.json()
    resultados1 = data1.get('resultados', [])
    if isinstance(resultados1, list):
        resultados1_dict = {r['partido']: r for r in resultados1}
    else:
        resultados1_dict = resultados1
    
    morena1 = resultados1_dict.get('MORENA', {})
    print(f"MORENA: MR={morena1.get('mr', 0)}, RP={morena1.get('rp', 0)}, TOTAL={morena1.get('total', 0)}")

# PRUEBA 2: SIN coaliciones
print("\n" + "="*80)
print("PRUEBA 2: SIN COALICIONES")
print("="*80)

payload2 = {
    "plan": "personalizado",
    "escanos_totales": 400,
    "sistema": "mixto",
    "mr_seats": 200,
    "rp_seats": 200,
    "aplicar_topes": False,
    "usar_coaliciones": False  # SIN
}

response2 = requests.post(f"{API_URL}?anio=2024", json=payload2, timeout=30)

if response2.status_code == 200:
    data2 = response2.json()
    resultados2 = data2.get('resultados', [])
    if isinstance(resultados2, list):
        resultados2_dict = {r['partido']: r for r in resultados2}
    else:
        resultados2_dict = resultados2
    
    morena2 = resultados2_dict.get('MORENA', {})
    print(f"MORENA: MR={morena2.get('mr', 0)}, RP={morena2.get('rp', 0)}, TOTAL={morena2.get('total', 0)}")

# COMPARACIÓN
print("\n" + "="*80)
print("COMPARACIÓN FINAL:")
print("="*80)

print(f"\nCON coaliciones:  MORENA MR={morena1.get('mr', 0)}, RP={morena1.get('rp', 0)}, TOTAL={morena1.get('total', 0)}")
print(f"SIN coaliciones:  MORENA MR={morena2.get('mr', 0)}, RP={morena2.get('rp', 0)}, TOTAL={morena2.get('total', 0)}")

print(f"\nDiferencia MR: {morena2.get('mr', 0) - morena1.get('mr', 0)} ({morena2.get('mr', 0)} - {morena1.get('mr', 0)})")
print(f"Diferencia RP: {morena2.get('rp', 0) - morena1.get('rp', 0)} ({morena2.get('rp', 0)} - {morena1.get('rp', 0)})")

if morena1.get('mr', 0) != morena2.get('mr', 0):
    print("\n✅ El MR SÍ CAMBIA cuando se apaga/enciende coaliciones")
    print(f"   Diferencia: {abs(morena2.get('mr', 0) - morena1.get('mr', 0))} escaños MR")
else:
    print("\n❌ El MR NO CAMBIA - el parámetro usar_coaliciones NO está funcionando")
