"""
Verificación completa: CON y SIN coaliciones
"""

import requests

API_URL = "http://127.0.0.1:8000/procesar/diputados"

print("\n" + "="*80)
print("🧪 VERIFICACIÓN COMPLETA - CON Y SIN COALICIONES")
print("="*80)

# TEST 1: SIN coaliciones
print("\n1️⃣  SIN COALICIONES")
print("-"*80)

response1 = requests.post(
    f"{API_URL}?anio=2024",
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

if response1.status_code == 200:
    data1 = response1.json()
    morena1 = [r for r in data1['resultados'] if r['partido'] == 'MORENA'][0]
    print(f"MORENA: MR={morena1['mr']}, RP={morena1['rp']}, TOTAL={morena1['total']}")
    print(f"Esperado: MR=163, RP=93, TOTAL=256")
    
    if morena1['total'] == 256:
        print("✅ CORRECTO")
    else:
        print(f"❌ INCORRECTO (obtenido {morena1['total']})")

# TEST 2: CON coaliciones
print("\n2️⃣  CON COALICIONES")
print("-"*80)

response2 = requests.post(
    f"{API_URL}?anio=2024",
    json={
        "plan": "personalizado",
        "escanos_totales": 400,
        "sistema": "mixto",
        "mr_seats": 200,
        "rp_seats": 200,
        "aplicar_topes": False,
        "usar_coaliciones": True
    },
    timeout=30
)

if response2.status_code == 200:
    data2 = response2.json()
    morena2 = [r for r in data2['resultados'] if r['partido'] == 'MORENA'][0]
    print(f"MORENA: MR={morena2['mr']}, RP={morena2['rp']}, TOTAL={morena2['total']}")
    print(f"Esperado: MR=161, RP=87, TOTAL=248")
    
    if morena2['total'] == 248:
        print("✅ CORRECTO")
    else:
        print(f"❌ INCORRECTO (obtenido {morena2['total']})")

# RESUMEN
print("\n" + "="*80)
print("RESUMEN FINAL:")
print("="*80)

sin_ok = morena1['total'] == 256 if response1.status_code == 200 else False
con_ok = morena2['total'] == 248 if response2.status_code == 200 else False

print(f"\nSIN coaliciones: {'✅ 256' if sin_ok else '❌ ' + str(morena1['total'])}")
print(f"CON coaliciones: {'✅ 248' if con_ok else '❌ ' + str(morena2['total'])}")

if sin_ok and con_ok:
    print("\n🎉🎉🎉 TODO FUNCIONA CORRECTAMENTE!")
    print("El frontend ahora mostrará los valores correctos")
else:
    print("\n⚠️  Hay algún problema pendiente")
