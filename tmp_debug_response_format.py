"""
Script para verificar el formato de respuesta y el parámetro usar_coaliciones
"""

import requests
import json

API_URL = "http://127.0.0.1:8000/procesar/diputados"

# PRUEBA 1: usar_coaliciones=True
print("\n" + "="*80)
print("PRUEBA 1: usar_coaliciones=True")
print("="*80)

try:
    response1 = requests.post(
        f"{API_URL}?anio=2024&plan=vigente&aplicar_topes=false&usar_coaliciones=true",
        timeout=30
    )
    print(f"Status: {response1.status_code}")
    if response1.status_code == 200:
        resultado1 = response1.json()
        print(f"Tipo de respuesta: {type(resultado1)}")
        
        if isinstance(resultado1, list):
            print(f"Es una lista con {len(resultado1)} elementos")
            if len(resultado1) > 0:
                print(f"Primer elemento: {json.dumps(resultado1[0], indent=2)[:500]}")
                # Buscar MORENA
                morena_data = [r for r in resultado1 if r.get('partido') == 'MORENA']
                if morena_data:
                    morena = morena_data[0]
                    print(f"\nMORENA encontrado: MR={morena.get('mr', 0)}, RP={morena.get('rp', 0)}, TOTAL={morena.get('total', 0)}")
        elif isinstance(resultado1, dict):
            print(f"Claves disponibles: {list(resultado1.keys())}")
            
    else:
        print(f"Error: {response1.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

# PRUEBA 2: usar_coaliciones=False
print("\n" + "="*80)
print("PRUEBA 2: usar_coaliciones=False")
print("="*80)

try:
    response2 = requests.post(
        f"{API_URL}?anio=2024&plan=vigente&aplicar_topes=false&usar_coaliciones=false",
        timeout=30
    )
    print(f"Status: {response2.status_code}")
    if response2.status_code == 200:
        resultado2 = response2.json()
        print(f"Tipo de respuesta: {type(resultado2)}")
        
        if isinstance(resultado2, list):
            print(f"Es una lista con {len(resultado2)} elementos")
            if len(resultado2) > 0:
                # Buscar MORENA
                morena_data = [r for r in resultado2 if r.get('partido') == 'MORENA']
                if morena_data:
                    morena = morena_data[0]
                    print(f"\nMORENA encontrado: MR={morena.get('mr', 0)}, RP={morena.get('rp', 0)}, TOTAL={morena.get('total', 0)}")
        elif isinstance(resultado2, dict):
            print(f"Claves disponibles: {list(resultado2.keys())}")
            
    else:
        print(f"Error: {response2.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
