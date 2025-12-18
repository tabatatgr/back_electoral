"""
Script para verificar qué parámetros está recibiendo la API cuando se envía usar_coaliciones
Vamos a hacer requests y revisar los logs del servidor
"""

import requests

API_URL = "http://127.0.0.1:8000/procesar/diputados"

print("\n" + "="*80)
print("Haciendo request con usar_coaliciones=False")
print("Por favor REVISAR LOS LOGS DEL SERVIDOR para ver:")
print("  - Coaliciones detectadas pero DESACTIVADAS")
print("  - MR sin coaliciones calculado")
print("="*80 + "\n")

response = requests.post(
    f"{API_URL}?anio=2024&plan=vigente&aplicar_topes=false&usar_coaliciones=false",
    timeout=30
)

if response.status_code == 200:
    data = response.json()
    morena = data.get('resultados', {}).get('MORENA', {})
    print(f"\n✅ Respuesta recibida:")
    print(f"   MORENA: MR={morena.get('mr', 0)}, RP={morena.get('rp', 0)}, TOTAL={morena.get('total', 0)}")
    print(f"\n   Esperado: MR=163, RP=93, TOTAL=256")
    
    if morena.get('mr', 0) == 163:
        print("\n   ✅ MR ES CORRECTO!")
    else:
        print(f"\n   ❌ MR ES INCORRECTO (obtenido {morena.get('mr', 0)}, esperado 163)")
        print("\n   Revisar logs del servidor para ver si dice:")
        print("      'Coaliciones detectadas pero DESACTIVADAS - recalculando MR por votos individuales'")
else:
    print(f"❌ Error: {response.status_code}")
