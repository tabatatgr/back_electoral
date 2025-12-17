"""
Test simple para debug: ver qué valores llegan al endpoint
"""
import requests

API_URL = "http://localhost:8000/procesar/diputados"

print("\n" + "=" * 80)
print("TEST DEBUG: Sin límites (sobrerrepresentacion=None, max_seats_per_party=None)")
print("=" * 80)

params = {
    "anio": 2024,
    "plan": "personalizado",
    "sistema": "mixto",
    "escanos_totales": 500,
    "usar_coaliciones": "false",
    "reparto_mode": "divisor",
    "reparto_method": "dhondt",
    "aplicar_topes": "true",
    # No pasamos sobrerrepresentacion ni max_seats_per_party
    "mr_seats": 300,
    "rp_seats": 200,
    "umbral": 3.0
}

print("\nParámetros enviados:")
for k, v in params.items():
    print(f"  {k}: {v}")

print("\nEsperando respuesta...\n")
response = requests.post(API_URL, params=params, timeout=30)

print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    
    # Buscar MORENA
    if "resultados" in data:
        for p in data["resultados"]:
            if p.get("partido") == "MORENA":
                print(f"\n✅ MORENA encontrado:")
                print(f"   Total: {p.get('total')} escaños")
                print(f"   MR: {p.get('mr', 0)}")
                print(f"   PM: {p.get('pm', 0)}")
                print(f"   RP: {p.get('rp', 0)}")
                break
else:
    print(f"❌ ERROR: {response.json()}")

print("\n" + "=" * 80)
print("Ahora revisa los logs del servidor para ver [DEBUG] LÍMITES y [DEBUG] TYPE")
print("=" * 80)
