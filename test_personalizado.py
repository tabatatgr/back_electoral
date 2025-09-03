#!/usr/bin/env python3
"""
Test plan personalizado - Debug de parámetros
"""

import requests
import json

def test_personalizado():
    print("🧪 TEST PLAN PERSONALIZADO")
    print("=" * 50)
    
    # Test 1: Plan personalizado con parámetros específicos
    params = {
        "anio": 2024,
        "plan": "personalizado",
        "sistema": "mixto",
        "escanos_totales": 400,
        "mr_seats": 100,
        "rp_seats": 300,
        "umbral": 0.05,
        "max_seats_per_party": 250
    }
    
    print(f"📤 Enviando parámetros:")
    for key, value in params.items():
        print(f"   {key}: {value}")
    
    try:
        print(f"\n🌐 Enviando POST a: http://localhost:8001/procesar/diputados")
        response = requests.post("http://localhost:8001/procesar/diputados", params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response exitoso")
            print(f"📊 Respuesta tipo: {type(data)}")
            
            # Si es el formato nuevo con resultados
            if isinstance(data, dict) and 'resultados' in data:
                total_escanos = sum(r['total'] for r in data['resultados'])
                print(f"📊 Total escaños: {total_escanos}")
                
                print(f"\n📋 Top 5 partidos:")
                for resultado in data['resultados'][:5]:
                    print(f"   {resultado['partido']}: {resultado['total']} (MR: {resultado['mr']}, RP: {resultado['rp']})")
                    
            # Si es formato directo partido->escaños
            elif isinstance(data, dict):
                total_escanos = sum(data.values())
                print(f"📊 Total escaños: {total_escanos}")
                
                for partido, escanos in list(data.items())[:5]:
                    if escanos > 0:
                        print(f"   {partido}: {escanos}")
                        
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Servidor no disponible en localhost:8001")
        print("💡 Asegúrate de ejecutar: python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_personalizado()
