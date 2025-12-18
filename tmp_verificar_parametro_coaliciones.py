"""
Script para verificar qué parámetro usar_coaliciones está recibiendo la API
"""

import requests
import json

API_URL = "http://127.0.0.1:8000/procesar/diputados"

# PRUEBA 1: Enviar usar_coaliciones=True explícitamente
print("\n" + "="*80)
print("PRUEBA 1: Enviando usar_coaliciones=True")
print("="*80)

payload1 = {
    "anio": 2024,
    "plan": "vigente",
    "aplicar_topes": False,
    "usar_coaliciones": True  # ← ENCENDIDO
}

response1 = requests.post(API_URL, json=payload1)
if response1.status_code == 200:
    resultado1 = response1.json()
    morena_total_1 = resultado1.get('resultados', {}).get('MORENA', {}).get('total', 0)
    morena_mr_1 = resultado1.get('resultados', {}).get('MORENA', {}).get('mr', 0)
    morena_rp_1 = resultado1.get('resultados', {}).get('MORENA', {}).get('rp', 0)
    print(f"✅ MORENA: MR={morena_mr_1}, RP={morena_rp_1}, TOTAL={morena_total_1}")
else:
    print(f"❌ Error: {response1.status_code}")

# PRUEBA 2: Enviar usar_coaliciones=False explícitamente
print("\n" + "="*80)
print("PRUEBA 2: Enviando usar_coaliciones=False")
print("="*80)

payload2 = {
    "anio": 2024,
    "plan": "vigente",
    "aplicar_topes": False,
    "usar_coaliciones": False  # ← APAGADO
}

response2 = requests.post(API_URL, json=payload2)
if response2.status_code == 200:
    resultado2 = response2.json()
    morena_total_2 = resultado2.get('resultados', {}).get('MORENA', {}).get('total', 0)
    morena_mr_2 = resultado2.get('resultados', {}).get('MORENA', {}).get('mr', 0)
    morena_rp_2 = resultado2.get('resultados', {}).get('MORENA', {}).get('rp', 0)
    print(f"✅ MORENA: MR={morena_mr_2}, RP={morena_rp_2}, TOTAL={morena_total_2}")
else:
    print(f"❌ Error: {response2.status_code}")

# COMPARACIÓN
print("\n" + "="*80)
print("COMPARACIÓN:")
print("="*80)
print(f"CON coaliciones (True):  MORENA TOTAL = {morena_total_1} (MR={morena_mr_1}, RP={morena_rp_1})")
print(f"SIN coaliciones (False): MORENA TOTAL = {morena_total_2} (MR={morena_mr_2}, RP={morena_rp_2})")
print(f"\nESPERADO (según CSV):")
print(f"CON coaliciones:  MORENA TOTAL = 248 (MR=161, RP=87)")
print(f"SIN coaliciones:  MORENA TOTAL = 256 (MR=163, RP=93)")

# DIAGNÓSTICO
print("\n" + "="*80)
print("DIAGNÓSTICO:")
print("="*80)

if morena_mr_1 == morena_mr_2:
    print("❌ PROBLEMA CONFIRMADO: El MR NO CAMBIA entre True/False")
    print("   Esto significa que el parámetro usar_coaliciones NO se está aplicando correctamente")
    print(f"   MR debería ser 161 (CON) y 163 (SIN), pero ambos dan {morena_mr_1}")
elif abs(morena_mr_1 - 161) <= 1 and abs(morena_mr_2 - 163) <= 1:
    print("✅ El parámetro usar_coaliciones SÍ se está aplicando (MR cambia correctamente)")
    print("   El problema puede ser solo el +1 RP")
else:
    print(f"⚠️  Patrón inesperado: MR={morena_mr_1} (CON) vs MR={morena_mr_2} (SIN)")
