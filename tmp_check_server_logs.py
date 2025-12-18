"""
Script para hacer request y forzar logs detallados en el servidor
REVISAR LA CONSOLA DEL SERVIDOR para ver los parámetros
"""

import requests
import json

print("\n🔍 Haciendo request a la API...")
print("📋 REVISA LA CONSOLA DEL SERVIDOR para ver:")
print("   [DEBUG] ========== PARÁMETROS PARA MOTOR ==========")
print()

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

if response.status_code == 200:
    data = response.json()
    morena = [r for r in data['resultados'] if r['partido'] == 'MORENA'][0]
    print(f"✅ API Response: MORENA MR={morena['mr']}, RP={morena['rp']}, TOTAL={morena['total']}")
    print(f"   Esperado: MR=163, RP=93, TOTAL=256")
    
    if morena['total'] == 256:
        print("\n✅✅ CORRECTO! La API ahora coincide con el motor")
    else:
        print(f"\n❌ INCORRECTO! API da {morena['total']}, esperado 256")
        print("\n📋 Revisa los logs del servidor para ver los parámetros exactos")
else:
    print(f"❌ Error: {response.status_code}")
