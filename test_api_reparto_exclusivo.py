#!/usr/bin/env python3
"""
Test para verificar el nuevo API con reparto exclusivo
"""

import requests
import json

def test_api_reparto_exclusivo():
    """Test del API con el nuevo sistema de reparto exclusivo"""
    
    print("🔍 TEST API REPARTO EXCLUSIVO")
    print("=" * 40)
    
    base_url = "http://localhost:8001"
    
    # Configuración base para plan personalizado
    config_base = {
        "anio": 2018,
        "plan": "personalizado",
        "escanos_totales": 300,
        "sistema": "rp",  # Solo RP para ver el efecto claramente
        "umbral": 0.03,
        "usar_coaliciones": True
    }
    
    print("📊 TEST 1: MODO CUOTA - HARE")
    try:
        response_cuota = requests.post(
            f"{base_url}/procesar/diputados",
            json={
                **config_base,
                "reparto_mode": "cuota",
                "reparto_method": "hare"
            }
        )
        
        if response_cuota.status_code == 200:
            data_cuota = response_cuota.json()
            if 'seats' in data_cuota:
                total_cuota = sum([s['seats'] for s in data_cuota['seats']])
                print(f"   ✅ Total escaños (Cuota Hare): {total_cuota}")
                top_3 = sorted(data_cuota['seats'], key=lambda x: x['seats'], reverse=True)[:3]
                print(f"   📈 Top 3: {[(p['party'], p['seats']) for p in top_3]}")
            else:
                print(f"   ⚠️  Respuesta sin 'seats': {list(data_cuota.keys())}")
        else:
            print(f"   ❌ Error HTTP {response_cuota.status_code}: {response_cuota.text}")
            
    except Exception as e:
        print(f"   ❌ Error con cuota: {e}")
    
    print()
    print("📊 TEST 2: MODO DIVISOR - D'HONDT")
    try:
        response_divisor = requests.post(
            f"{base_url}/procesar/diputados",
            json={
                **config_base,
                "reparto_mode": "divisor",
                "reparto_method": "dhondt"
            }
        )
        
        if response_divisor.status_code == 200:
            data_divisor = response_divisor.json()
            if 'seats' in data_divisor:
                total_divisor = sum([s['seats'] for s in data_divisor['seats']])
                print(f"   ✅ Total escaños (Divisor D'Hondt): {total_divisor}")
                top_3 = sorted(data_divisor['seats'], key=lambda x: x['seats'], reverse=True)[:3]
                print(f"   📈 Top 3: {[(p['party'], p['seats']) for p in top_3]}")
            else:
                print(f"   ⚠️  Respuesta sin 'seats': {list(data_divisor.keys())}")
        else:
            print(f"   ❌ Error HTTP {response_divisor.status_code}: {response_divisor.text}")
            
    except Exception as e:
        print(f"   ❌ Error con divisor: {e}")
    
    print()
    print("📊 TEST 3: MODO CUOTA - DROOP")
    try:
        response_droop = requests.post(
            f"{base_url}/procesar/diputados",
            json={
                **config_base,
                "reparto_mode": "cuota",
                "reparto_method": "droop"
            }
        )
        
        if response_droop.status_code == 200:
            data_droop = response_droop.json()
            if 'seats' in data_droop:
                total_droop = sum([s['seats'] for s in data_droop['seats']])
                print(f"   ✅ Total escaños (Cuota Droop): {total_droop}")
                top_3 = sorted(data_droop['seats'], key=lambda x: x['seats'], reverse=True)[:3]
                print(f"   📈 Top 3: {[(p['party'], p['seats']) for p in top_3]}")
            else:
                print(f"   ⚠️  Respuesta sin 'seats': {list(data_droop.keys())}")
        else:
            print(f"   ❌ Error HTTP {response_droop.status_code}: {response_droop.text}")
            
    except Exception as e:
        print(f"   ❌ Error con droop: {e}")

    print()
    print("📊 TEST 4: ERROR - MODO INVÁLIDO")
    try:
        response_error = requests.post(
            f"{base_url}/procesar/diputados",
            json={
                **config_base,
                "reparto_mode": "invalido",
                "reparto_method": "hare"
            }
        )
        
        if response_error.status_code != 200:
            print(f"   ✅ Error esperado HTTP {response_error.status_code}")
            print(f"   📝 Mensaje: {response_error.json().get('detail', 'Sin detalle')}")
        else:
            print(f"   ⚠️  Debería haber fallado pero no lo hizo")
            
    except Exception as e:
        print(f"   ❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_api_reparto_exclusivo()
