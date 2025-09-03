#!/usr/bin/env python3

import requests
import json

print("🧪 TESTING ENDPOINT DESPUÉS DE LA CORRECCIÓN")
print("=" * 50)

# Test del endpoint real
response = requests.get('http://localhost:8001/diputados?anio=2018&plan=vigente')
if response.status_code == 200:
    data = response.json()
    print('✅ ENDPOINT FUNCIONANDO')
    print(f'MC Total: {data.get("MC", "N/A")}')
    
    # Buscar MC en resultados detallados si están disponibles
    if 'detalle' in data:
        mc_mr = data['detalle'].get('MR', {}).get('MC', 0)
        mc_rp = data['detalle'].get('RP', {}).get('MC', 0)
        print(f'MC MR: {mc_mr}')
        print(f'MC RP: {mc_rp}')
    else:
        print('Datos disponibles:', list(data.keys()))
        # Imprimir toda la respuesta para ver la estructura
        print('Estructura completa:')
        print(json.dumps(data, indent=2))
else:
    print(f'❌ Error: {response.status_code}')
    print(response.text)
