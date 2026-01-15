"""
Prueba inline sin necesidad de terminal separada
"""
import time
print("Esperando 3 segundos para que el servidor esté listo...")
time.sleep(3)

import requests
import json

URL = "http://localhost:8001/procesar/diputados"

print("\n" + "="*80)
print("🧪 PRUEBA: Redistritación Geográfica con Eficiencias Reales")
print("="*80)

# Payload de prueba
payload = {
    "anio": 2024,
    "sistema": "mixto",
    "mr_seats": 300,
    "rp_seats": 100,
    "max_seats": 400,
    "aplicar_topes": True,
    "votos_redistribuidos": {
        "MORENA": 50.0,
        "PAN": 20.0,
        "PRI": 15.0,
        "PVEM": 8.0,
        "MC": 7.0
    }
}

# TEST 1: Modo proporcional
print("\n📊 TEST 1: Modo PROPORCIONAL (default)")
print("-" * 80)

payload1 = payload.copy()
payload1["redistritacion_geografica"] = False

try:
    r = requests.post(URL, json=payload1, timeout=30)
    if r.status_code == 200:
        data = r.json()
        print("✅ Respuesta exitosa")
        asig = data.get("asignaciones", {})
        print("\nMR por partido (modo proporcional):")
        for p in ["MORENA", "PAN", "PRI", "PVEM", "MC"]:
            if p in asig:
                print(f"  {p:10s}: {asig[p].get('MR', 0):3d} MR")
        prop_results = {p: asig[p].get('MR', 0) for p in ["MORENA", "PAN", "PRI", "PVEM", "MC"] if p in asig}
    else:
        print(f"❌ Error {r.status_code}: {r.text[:200]}")
        prop_results = None
except Exception as e:
    print(f"❌ Error: {e}")
    prop_results = None

# TEST 2: Modo geográfico
print("\n📍 TEST 2: Modo GEOGRÁFICO (con eficiencias reales por partido)")
print("-" * 80)

payload2 = payload.copy()
payload2["redistritacion_geografica"] = True

try:
    r = requests.post(URL, json=payload2, timeout=30)
    if r.status_code == 200:
        data = r.json()
        print("✅ Respuesta exitosa")
        asig = data.get("asignaciones", {})
        print("\nMR por partido (modo geográfico):")
        for p in ["MORENA", "PAN", "PRI", "PVEM", "MC"]:
            if p in asig:
                print(f"  {p:10s}: {asig[p].get('MR', 0):3d} MR")
        geo_results = {p: asig[p].get('MR', 0) for p in ["MORENA", "PAN", "PRI", "PVEM", "MC"] if p in asig}
    else:
        print(f"❌ Error {r.status_code}: {r.text[:200]}")
        geo_results = None
except Exception as e:
    print(f"❌ Error: {e}")
    geo_results = None

# Comparación
if prop_results and geo_results:
    print("\n📈 COMPARACIÓN")
    print("-" * 80)
    print(f"{'Partido':12s} | {'Proporcional':>12s} | {'Geográfico':>12s} | {'Diferencia':>11s}")
    print("-" * 80)
    for p in ["MORENA", "PAN", "PRI", "PVEM", "MC"]:
        prop_mr = prop_results.get(p, 0)
        geo_mr = geo_results.get(p, 0)
        diff = geo_mr - prop_mr
        diff_str = f"+{diff}" if diff > 0 else str(diff)
        print(f"{p:12s} | {prop_mr:12d} | {geo_mr:12d} | {diff_str:>11s}")
    
    print("\n💡 Interpretación:")
    print("  - Si diferencia es negativa: El partido necesita MÁS votos en modo geográfico")
    print("  - Si diferencia es positiva: El partido se beneficia de distribución geográfica")
    print("  - Basado en eficiencias REALES de la elección 2024")

print("\n" + "="*80)
print("✅ Pruebas completadas")
print("="*80)
