#!/usr/bin/env python3
"""
Debug específico para el problema del umbral en senado
"""

import requests
import json
import time

# URL base del backend
BASE_URL = "https://back-electoral.onrender.com"

def test_senado_umbral():
    """Prueba diferentes configuraciones de umbral en senado"""
    
    # Test 1: Senado vigente (sin umbral personalizado)
    print("=== TEST 1: Senado Vigente ===")
    url_vigente = f"{BASE_URL}/procesar/senado"
    params_vigente = {"anio": 2018, "plan": "vigente", "escanos_totales": 128}
    try:
        response = requests.post(url_vigente, params=params_vigente, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Partidos en seat_chart: {len(data.get('seat_chart', []))}")
            total_escanos = sum(p['seats'] for p in data.get('seat_chart', []))
            print(f"Total escaños: {total_escanos}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error en request: {e}")
    
    time.sleep(2)
    
    # Test 2: Senado personalizado con umbral 0% (sin filtro)
    print("\n=== TEST 2: Senado Personalizado Umbral 0% ===")
    url_senado = f"{BASE_URL}/procesar/senado"
    params_0 = {
        "anio": 2018, 
        "plan": "personalizado", 
        "umbral": 0.0, 
        "sistema": "mixto", 
        "mr_seats": 96, 
        "rp_seats": 32, 
        "escanos_totales": 128
    }
    try:
        response = requests.post(url_senado, params=params_0, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Partidos en seat_chart: {len(data.get('seat_chart', []))}")
            total_escanos = sum(p['seats'] for p in data.get('seat_chart', []))
            print(f"Total escaños: {total_escanos}")
            
            # Mostrar partidos
            for partido in data.get('seat_chart', []):
                print(f"  {partido['party']}: {partido['seats']} escaños ({partido['percent']}%)")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error en request: {e}")
    
    time.sleep(2)
    
    # Test 3: Senado personalizado con umbral 3%
    print("\n=== TEST 3: Senado Personalizado Umbral 3% ===")
    params_3 = {
        "anio": 2018, 
        "plan": "personalizado", 
        "umbral": 0.03, 
        "sistema": "mixto", 
        "mr_seats": 96, 
        "rp_seats": 32, 
        "escanos_totales": 128
    }
    try:
        response = requests.post(url_senado, params=params_3, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Partidos en seat_chart: {len(data.get('seat_chart', []))}")
            total_escanos = sum(p['seats'] for p in data.get('seat_chart', []))
            print(f"Total escaños: {total_escanos}")
            
            # Mostrar partidos
            for partido in data.get('seat_chart', []):
                print(f"  {partido['party']}: {partido['seats']} escaños ({partido['percent']}%)")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error en request: {e}")
    
    time.sleep(2)
    
    # Test 4: Senado personalizado con umbral 5% (más restrictivo)
    print("\n=== TEST 4: Senado Personalizado Umbral 5% ===")
    params_5 = {
        "anio": 2018, 
        "plan": "personalizado", 
        "umbral": 0.05, 
        "sistema": "mixto", 
        "mr_seats": 96, 
        "rp_seats": 32, 
        "escanos_totales": 128
    }
    try:
        response = requests.post(url_senado, params=params_5, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Partidos en seat_chart: {len(data.get('seat_chart', []))}")
            total_escanos = sum(p['seats'] for p in data.get('seat_chart', []))
            print(f"Total escaños: {total_escanos}")
            
            # Mostrar partidos
            for partido in data.get('seat_chart', []):
                print(f"  {partido['party']}: {partido['seats']} escaños ({partido['percent']}%)")
                
            # Revisar si hay partidos sin escaños
            partidos_sin_escanos = [p for p in data.get('seat_chart', []) if p['seats'] == 0]
            print(f"Partidos sin escaños: {len(partidos_sin_escanos)}")
            
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error en request: {e}")

if __name__ == "__main__":
    test_senado_umbral()
