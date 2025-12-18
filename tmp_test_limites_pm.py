"""
Prueba del nuevo endpoint /calcular-limites-pm
"""

import requests

API_URL = "http://127.0.0.1:8000/calcular-limites-pm"

print("\n" + "="*80)
print("🧪 PRUEBA DEL ENDPOINT /calcular-limites-pm")
print("="*80)

# TEST 1: Sistema mixto con escanos_totales y mr_seats específicos
print("\n1️⃣  Sistema mixto: 400 escaños, 200 MR")
response1 = requests.get(
    API_URL,
    params={
        "sistema": "mixto",
        "escanos_totales": 400,
        "mr_seats": 200
    }
)
if response1.status_code == 200:
    data1 = response1.json()
    print(f"   Max PM: {data1['max_pm']}")
    print(f"   Descripción: {data1['descripcion']}")
else:
    print(f"   ❌ Error: {response1.status_code}")

# TEST 2: Sistema MR puro con 300 escaños
print("\n2️⃣  Sistema MR puro: 300 escaños")
response2 = requests.get(
    API_URL,
    params={
        "sistema": "mr",
        "escanos_totales": 300
    }
)
if response2.status_code == 200:
    data2 = response2.json()
    print(f"   Max PM: {data2['max_pm']}")
    print(f"   Descripción: {data2['descripcion']}")

# TEST 3: Sistema MR puro con 500 escaños
print("\n3️⃣  Sistema MR puro: 500 escaños")
response3 = requests.get(
    API_URL,
    params={
        "sistema": "mr",
        "escanos_totales": 500
    }
)
if response3.status_code == 200:
    data3 = response3.json()
    print(f"   Max PM: {data3['max_pm']}")
    print(f"   Descripción: {data3['descripcion']}")

# TEST 4: Sistema RP puro (no permite PM)
print("\n4️⃣  Sistema RP puro")
response4 = requests.get(
    API_URL,
    params={
        "sistema": "rp",
        "escanos_totales": 300
    }
)
if response4.status_code == 200:
    data4 = response4.json()
    print(f"   Max PM: {data4['max_pm']}")
    print(f"   Descripción: {data4['descripcion']}")
    print(f"   Válido: {data4['valido']}")

# TEST 5: Sistema mixto solo con escanos_totales (default 60/40)
print("\n5️⃣  Sistema mixto: 600 escaños (sin especificar MR)")
response5 = requests.get(
    API_URL,
    params={
        "sistema": "mixto",
        "escanos_totales": 600
    }
)
if response5.status_code == 200:
    data5 = response5.json()
    print(f"   Max PM: {data5['max_pm']}")
    print(f"   Descripción: {data5['descripcion']}")

print("\n" + "="*80)
print("RESUMEN:")
print("="*80)
print("\n✅ El frontend puede llamar a este endpoint para obtener el límite dinámico")
print("   Ejemplo: GET /calcular-limites-pm?sistema=mixto&escanos_totales=400&mr_seats=200")
print("\n📋 El frontend debería:")
print("   1. Llamar a este endpoint cuando el usuario cambie sistema/escaños")
print("   2. Usar max_pm para limitar el slider/input de Primera Minoría")
print("   3. Mostrar 'descripcion' como ayuda al usuario")
