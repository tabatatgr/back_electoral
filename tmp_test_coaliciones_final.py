"""
Script final para verificar si usar_coaliciones está funcionando
"""

import requests
import json

API_URL = "http://127.0.0.1:8000/procesar/diputados"

# PRUEBA 1: usar_coaliciones=True
print("\n" + "="*80)
print("PRUEBA 1: usar_coaliciones=True (CON coaliciones)")
print("="*80)

response1 = requests.post(
    f"{API_URL}?anio=2024&plan=vigente&aplicar_topes=false&usar_coaliciones=true",
    timeout=30
)

if response1.status_code == 200:
    data1 = response1.json()
    resultados1 = data1.get('resultados', {})
    
    # resultados puede ser dict o list
    if isinstance(resultados1, list):
        morena1 = [r for r in resultados1 if r.get('partido') == 'MORENA'][0]
    else:
        morena1 = resultados1.get('MORENA', {})
    
    mr1 = morena1.get('mr', 0)
    rp1 = morena1.get('rp', 0)
    total1 = morena1.get('total', 0)
    
    print(f"MORENA: MR={mr1}, RP={rp1}, TOTAL={total1}")
    print(f"CSV esperado: MR=161, RP=87, TOTAL=248")
    
    if mr1 == 161:
        print("✅ MR correcto (161)")
    else:
        print(f"❌ MR incorrecto: {mr1} (esperado 161)")

# PRUEBA 2: usar_coaliciones=False
print("\n" + "="*80)
print("PRUEBA 2: usar_coaliciones=False (SIN coaliciones)")
print("="*80)

response2 = requests.post(
    f"{API_URL}?anio=2024&plan=vigente&aplicar_topes=false&usar_coaliciones=false",
    timeout=30
)

if response2.status_code == 200:
    data2 = response2.json()
    resultados2 = data2.get('resultados', {})
    
    # resultados puede ser dict o list
    if isinstance(resultados2, list):
        morena2 = [r for r in resultados2 if r.get('partido') == 'MORENA'][0]
    else:
        morena2 = resultados2.get('MORENA', {})
    
    mr2 = morena2.get('mr', 0)
    rp2 = morena2.get('rp', 0)
    total2 = morena2.get('total', 0)
    
    print(f"MORENA: MR={mr2}, RP={rp2}, TOTAL={total2}")
    print(f"CSV esperado: MR=163, RP=93, TOTAL=256")
    
    if mr2 == 163:
        print("✅ MR correcto (163)")
    else:
        print(f"❌ MR incorrecto: {mr2} (esperado 163)")

# COMPARACIÓN Y DIAGNÓSTICO
print("\n" + "="*80)
print("DIAGNÓSTICO FINAL:")
print("="*80)

print(f"\nCON coaliciones:  MORENA = MR:{mr1}, RP:{rp1}, TOTAL:{total1}")
print(f"SIN coaliciones:  MORENA = MR:{mr2}, RP:{rp2}, TOTAL:{total2}")

if mr1 == mr2:
    print("\n❌❌❌ PROBLEMA CONFIRMADO:")
    print("   El MR NO CAMBIA cuando se apaga/enciende coaliciones")
    print(f"   Ambos casos dan MR={mr1}")
    print("   Esto significa que el parámetro usar_coaliciones NO se está aplicando")
    print("\n   CAUSA PROBABLE:")
    print("   - El frontend no está enviando el parámetro correctamente")
    print("   - O el backend no lo está procesando correctamente")
elif mr1 == 161 and mr2 == 163:
    print("\n✅ El parámetro usar_coaliciones SÍ FUNCIONA:")
    print("   MR cambia correctamente de 161 (CON) a 163 (SIN)")
    
    if rp1 == 87 and rp2 == 93:
        print("   ✅✅ RP también es correcto!")
        print("   API coincide EXACTAMENTE con CSV")
    else:
        print(f"   ⚠️  Hay discrepancia en RP:")
        print(f"   Esperado: RP=87 (CON), RP=93 (SIN)")
        print(f"   Obtenido: RP={rp1} (CON), RP={rp2} (SIN)")
else:
    print(f"\n⚠️  Patrón inesperado:")
    print(f"   MR CON coaliciones: {mr1} (esperado 161)")
    print(f"   MR SIN coaliciones: {mr2} (esperado 163)")
