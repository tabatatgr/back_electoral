"""
Prueba simple y directa del endpoint de redistritación geográfica
"""

import requests
import json

# Probar modo proporcional primero
print("\n" + "="*80)
print("PRUEBA 1: Modo PROPORCIONAL (actual)")
print("="*80)

payload_prop = {
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
    },
    "redistritacion_geografica": False
}

try:
    print(f"\nEnviando request a http://localhost:8001/procesar/diputados...")
    response = requests.post(
        "http://localhost:8001/procesar/diputados",
        json=payload_prop,
        timeout=60
    )
    
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ Modo proporcional funcionó correctamente!")
        
        if "asignaciones" in data:
            asignaciones = data["asignaciones"]
            print("\nAsignaciones MR:")
            for partido in ["MORENA", "PAN", "PRI", "PVEM", "MC"]:
                if partido in asignaciones:
                    mr = asignaciones[partido].get("MR", 0)
                    print(f"  {partido}: {mr} MR")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text[:500])
        
except Exception as e:
    print(f"❌ Error en request: {e}")

# Ahora probar modo geográfico
print("\n" + "="*80)
print("PRUEBA 2: Modo GEOGRÁFICO (nuevo con eficiencias reales)")
print("="*80)

payload_geo = payload_prop.copy()
payload_geo["redistritacion_geografica"] = True

try:
    print(f"\nEnviando request a http://localhost:8001/procesar/diputados...")
    response = requests.post(
        "http://localhost:8001/procesar/diputados",
        json=payload_geo,
        timeout=60
    )
    
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ Modo geográfico funcionó correctamente!")
        
        if "asignaciones" in data:
            asignaciones = data["asignaciones"]
            print("\nAsignaciones MR:")
            for partido in ["MORENA", "PAN", "PRI", "PVEM", "MC"]:
                if partido in asignaciones:
                    mr = asignaciones[partido].get("MR", 0)
                    print(f"  {partido}: {mr} MR")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text[:500])
        
except Exception as e:
    print(f"❌ Error en request: {e}")

print("\n" + "="*80)
print("Pruebas completadas")
print("="*80)
