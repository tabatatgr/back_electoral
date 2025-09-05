#!/usr/bin/env python3
"""
Test específico para la funcionalidad de EDITAR PORCENTAJES POR PARTIDO
"""

import json
import urllib.request
import urllib.parse
import traceback

def test_editar_porcentajes_partido():
    """Test con porcentajes simples para verificar el problema"""
    
    print("🔍 TEST: Porcentajes de votos simples")
    print("=" * 50)
    
    # Test 1: Datos básicos que deberían funcionar
    test_data = {
        "MORENA": 40.0,
        "PAN": 30.0, 
        "PRI": 20.0,
        "MC": 10.0
    }
    
    print(f"📊 Datos de prueba: {test_data}")
    print(f"📊 Suma total: {sum(test_data.values())}%")
    
    # Parámetros mínimos
    params = {
        'anio': '2024',
        'plan': 'personalizado',
        'mr_seats': '300',
        'rp_seats': '200', 
        'escanos_totales': '500',
        'umbral': '0.03',
        'sobrerrepresentacion': '8',
        'reparto_mode': 'cuota',
        'reparto_method': 'hare',
        'usar_coaliciones': 'true'
    }
    
    # Body data
    body_data = {
        'porcentajes_partidos': json.dumps(test_data),
        'partidos_fijos': '{}',
        'overrides_pool': '{}'
    }
    
    try:
        print("\n🚀 Enviando request...")
        print(f"URL: https://back-electoral.onrender.com/procesar/diputados")
        print(f"Query params: {params}")
        print(f"Body data: {body_data}")
        
        response = requests.post(
            "https://back-electoral.onrender.com/procesar/diputados",
            params=params,
            data=body_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        print(f"\n📬 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! Los porcentajes funcionan correctamente")
            data = response.json()
            print(f"✅ Keys en respuesta: {list(data.keys())}")
            
            if 'resultados_detalle' in data:
                print("✅ Resultados detalle disponible")
                for partido, info in data['resultados_detalle'].items():
                    print(f"   {partido}: {info.get('total_seats', 0)} escaños")
            
        elif response.status_code == 500:
            print("❌ ERROR HTTP 500 - Error interno del servidor")
            print("📄 Respuesta del servidor:")
            print(response.text)
            
        elif response.status_code == 422:
            print("❌ ERROR HTTP 422 - Parámetros incorrectos")
            print("📄 Respuesta del servidor:")
            print(response.text)
            
        else:
            print(f"❌ ERROR HTTP {response.status_code}")
            print("📄 Respuesta del servidor:")
            print(response.text)
            
    except Exception as e:
        print(f"❌ ERROR DE CONEXIÓN: {e}")
        traceback.print_exc()

def test_porcentajes_diferentes_formatos():
    """Test con diferentes formatos de porcentajes"""
    
    print("\n🔍 TEST: Diferentes formatos de porcentajes")
    print("=" * 50)
    
    tests = [
        {
            "nombre": "Porcentajes enteros",
            "datos": {"MORENA": 40, "PAN": 30, "PRI": 20, "MC": 10}
        },
        {
            "nombre": "Porcentajes decimales",
            "datos": {"MORENA": 40.5, "PAN": 29.3, "PRI": 20.2, "MC": 10.0}
        },
        {
            "nombre": "Suma no es 100%",
            "datos": {"MORENA": 35, "PAN": 25, "PRI": 15, "MC": 10}  # Suma = 85%
        },
        {
            "nombre": "Solo partidos principales 2024",
            "datos": {"MORENA": 42.0, "PAN": 28.0, "PRI": 15.0, "MC": 12.0, "PVEM": 3.0}
        }
    ]
    
    for test in tests:
        print(f"\n📊 {test['nombre']}")
        print(f"   Datos: {test['datos']}")
        print(f"   Suma: {sum(test['datos'].values())}%")
        
        # Usar mismo formato que el test anterior
        body_data = {
            'porcentajes_partidos': json.dumps(test['datos']),
            'partidos_fijos': '{}',
            'overrides_pool': '{}'
        }
        
        params = {
            'anio': '2024',
            'plan': 'personalizado', 
            'mr_seats': '300',
            'rp_seats': '200',
            'escanos_totales': '500',
            'umbral': '0.03',
            'sobrerrepresentacion': '8',
            'reparto_mode': 'cuota',
            'reparto_method': 'hare',
            'usar_coaliciones': 'true'
        }
        
        try:
            response = requests.post(
                "https://back-electoral.onrender.com/procesar/diputados",
                params=params,
                data=body_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"   ✅ Status: {response.status_code} - FUNCIONA")
            else:
                print(f"   ❌ Status: {response.status_code} - ERROR")
                # Solo mostrar primeras líneas del error
                error_lines = response.text.split('\n')[:3]
                print(f"   📄 Error: {error_lines}")
                
        except Exception as e:
            print(f"   ❌ Excepción: {e}")

def test_sin_porcentajes():
    """Test sin porcentajes para verificar que el backend funciona sin ellos"""
    
    print("\n🔍 TEST: Sin porcentajes (datos reales)")
    print("=" * 50)
    
    params = {
        'anio': '2024',
        'plan': 'vigente'  # Usar plan vigente sin modificaciones
    }
    
    try:
        response = requests.post(
            "https://back-electoral.onrender.com/procesar/diputados",
            params=params,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        print(f"📬 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Backend funciona correctamente SIN porcentajes personalizados")
            data = response.json()
            print(f"✅ Keys disponibles: {list(data.keys())}")
        else:
            print(f"❌ ERROR: Backend falla incluso sin porcentajes personalizados")
            print(f"📄 Respuesta: {response.text[:500]}...")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    print("🧪 DIAGNÓSTICO DE PORCENTAJES DE VOTOS")
    print("=" * 60)
    
    # Test 1: Sin porcentajes (baseline)
    test_sin_porcentajes()
    
    # Test 2: Porcentajes simples
    test_porcentajes_simples()
    
    # Test 3: Diferentes formatos
    test_porcentajes_diferentes_formatos()
    
    print("\n🎯 CONCLUSIÓN:")
    print("Si el test SIN porcentajes funciona pero CON porcentajes falla,")
    print("entonces el problema está en el procesamiento de porcentajes_partidos")
    print("en el backend.")
