#!/usr/bin/env python3
"""
Test para verificar que se corrigió el IndexError en umbrales de senado
"""

import requests
import time

BASE_URL = "https://back-electoral.onrender.com"

def test_umbral_bug_fix():
    """Test específico para el bug de IndexError con umbrales"""
    
    print("=== TEST: Verificación de IndexError Bug Fix ===\n")
    
    umbrales_test = [0.01, 0.03, 0.05, 0.10, 0.15]
    
    for umbral in umbrales_test:
        print(f"🧪 TEST UMBRAL: {umbral*100}%")
        
        params = {
            "anio": 2018,
            "plan": "personalizado",
            "sistema": "mixto",
            "mr_seats": 64,
            "pm_seats": 32,  # Nuevo parámetro
            "rp_seats": 32,
            "umbral": umbral,
            "escanos_totales": 128
        }
        
        try:
            response = requests.post(f"{BASE_URL}/procesar/senado", params=params, timeout=30)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                total_escanos = sum(p['seats'] for p in data.get('seat_chart', []))
                partidos_con_escanos = len([p for p in data.get('seat_chart', []) if p['seats'] > 0])
                
                print(f"   ✅ Total escaños: {total_escanos}")
                print(f"   📊 Partidos con escaños: {partidos_con_escanos}")
                
                # Mostrar distribución
                for p in data.get('seat_chart', []):
                    if p['seats'] > 0:
                        print(f"       {p['party']}: {p['seats']} escaños")
                        
            elif response.status_code == 500:
                error_text = response.text
                if "IndexError" in error_text:
                    print(f"   ❌ INDEXERROR AÚN PRESENTE: {error_text}")
                else:
                    print(f"   ⚠️ Error 500 (no IndexError): {error_text}")
            else:
                print(f"   ⚠️ Status inesperado: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        print()
        time.sleep(1)  # Evitar rate limiting
    
    # Test extremo: umbral muy alto (20%)
    print("🔥 TEST EXTREMO: Umbral 20% (debería eliminar casi todos los partidos)")
    
    params_extremo = {
        "anio": 2018,
        "plan": "personalizado",
        "sistema": "mixto", 
        "mr_seats": 64,
        "pm_seats": 32,
        "rp_seats": 32,
        "umbral": 0.20,  # 20% - muy alto
        "escanos_totales": 128
    }
    
    try:
        response = requests.post(f"{BASE_URL}/procesar/senado", params=params_extremo, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            partidos_sobrevivientes = [p for p in data.get('seat_chart', []) if p['seats'] > 0]
            print(f"   ✅ Partidos que superan 20%: {len(partidos_sobrevivientes)}")
            
            for p in partidos_sobrevivientes:
                print(f"       {p['party']}: {p['seats']} escaños")
        else:
            print(f"   Status: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    test_umbral_bug_fix()
