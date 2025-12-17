"""
Test para verificar que aplicar_topes ahora se respeta desde el frontend
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("TEST: Verificar que aplicar_topes funciona desde el endpoint")
print("=" * 80)

# Test 1: CON TOPES (aplicar_topes=True, default)
print("\n1️⃣ CON TOPES (aplicar_topes=True)")
print("-" * 80)

params1 = {
    "anio": 2024,
    "plan": "personalizado",
    "sistema": "mixto",
    "escanos_totales": 500,
    "mr_seats": 300,
    "rp_seats": 200,
    "sobrerrepresentacion": 8.0,  # Límite constitucional del 8%
    "aplicar_topes": "true",  # CON topes
    "usar_coaliciones": "false"
}

try:
    resp1 = requests.post(f"{BASE_URL}/procesar/diputados", params=params1, timeout=30)
    if resp1.status_code == 200:
        data1 = resp1.json()
        # Buscar MORENA en resultados o seat_chart
        morena1 = None
        if "resultados" in data1:
            for p in data1["resultados"]:
                if p.get("partido") == "MORENA":
                    morena1 = p
                    break
        
        if morena1:
            print(f"✅ MORENA (CON topes):")
            print(f"   Total: {morena1.get('total')} escaños")
            print(f"   MR: {morena1.get('mr', 0)}")
            print(f"   PM: {morena1.get('pm', 0)}")
            print(f"   RP: {morena1.get('rp', 0)}")
            escanos_con_topes = morena1.get('total')
        else:
            print("❌ MORENA no encontrado en resultados")
            escanos_con_topes = None
    else:
        print(f"❌ Error {resp1.status_code}: {resp1.text[:200]}")
        escanos_con_topes = None
except Exception as e:
    print(f"❌ Error en request: {e}")
    escanos_con_topes = None

# Test 2: SIN TOPES (aplicar_topes=False)
print("\n2️⃣ SIN TOPES (aplicar_topes=False)")
print("-" * 80)

params2 = params1.copy()
params2["aplicar_topes"] = "false"  # SIN topes

try:
    resp2 = requests.post(f"{BASE_URL}/procesar/diputados", params=params2, timeout=30)
    if resp2.status_code == 200:
        data2 = resp2.json()
        morena2 = None
        if "resultados" in data2:
            for p in data2["resultados"]:
                if p.get("partido") == "MORENA":
                    morena2 = p
                    break
        
        if morena2:
            print(f"✅ MORENA (SIN topes):")
            print(f"   Total: {morena2.get('total')} escaños")
            print(f"   MR: {morena2.get('mr', 0)}")
            print(f"   PM: {morena2.get('pm', 0)}")
            print(f"   RP: {morena2.get('rp', 0)}")
            escanos_sin_topes = morena2.get('total')
        else:
            print("❌ MORENA no encontrado en resultados")
            escanos_sin_topes = None
    else:
        print(f"❌ Error {resp2.status_code}: {resp2.text[:200]}")
        escanos_sin_topes = None
except Exception as e:
    print(f"❌ Error en request: {e}")
    escanos_sin_topes = None

# Comparación
print("\n" + "=" * 80)
print("COMPARACIÓN:")
print("=" * 80)

if escanos_con_topes and escanos_sin_topes:
    print(f"CON topes:  {escanos_con_topes} escaños (debe ser ≤252 por el 8%)")
    print(f"SIN topes:  {escanos_sin_topes} escaños (puede ser >252)")
    
    if escanos_sin_topes > escanos_con_topes:
        print("\n✅ ¡FUNCIONA! El parámetro aplicar_topes ahora se respeta")
        print(f"   Diferencia: +{escanos_sin_topes - escanos_con_topes} escaños sin topes")
    elif escanos_con_topes == escanos_sin_topes:
        print("\n⚠️  ADVERTENCIA: Ambos dan el mismo resultado")
        print("   Esto puede ser normal si MORENA no alcanza el límite del 8%")
    else:
        print("\n❌ ERROR: Sin topes da MENOS escaños que con topes (imposible)")
else:
    print("❌ No se pudieron comparar los resultados")

print("\n" + "=" * 80)
