#!/usr/bin/env python3
"""
Test para capturar el error exacto al editar porcentajes
"""

import json
import urllib.request
import urllib.parse
import traceback

def test_con_logs_detallados():
    """Test con logs detallados para ver el error exacto"""
    
    print("🔍 TEST: Capturar error exacto con porcentajes")
    print("=" * 60)
    
    # Datos de prueba simplificados
    porcentajes = {
        "MORENA": 50.0,
        "PAN": 30.0,
        "PRI": 20.0
    }
    
    # Parámetros mínimos
    query_params = {
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
    
    body_data = {
        'porcentajes_partidos': json.dumps(porcentajes),
        'partidos_fijos': '{}',
        'overrides_pool': '{}'
    }
    
    query_string = urllib.parse.urlencode(query_params)
    url = f"https://back-electoral.onrender.com/procesar/diputados?{query_string}"
    body_encoded = urllib.parse.urlencode(body_data).encode('utf-8')
    
    print(f"📊 Datos enviados:")
    print(f"   Porcentajes: {porcentajes}")
    print(f"   URL: {url}")
    print(f"   Body: {body_data}")
    
    try:
        req = urllib.request.Request(
            url,
            data=body_encoded,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            },
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=60) as response:
            status_code = response.getcode()
            response_data = response.read().decode('utf-8')
            
            print(f"📬 Status: {status_code}")
            
            if status_code == 200:
                print("✅ SUCCESS!")
                data = json.loads(response_data)
                print(f"Keys: {list(data.keys())}")
            else:
                print(f"❌ Error {status_code}")
                print(f"Response: {response_data}")
                
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP ERROR {e.code}")
        
        # Leer el error completo
        try:
            error_data = e.read().decode('utf-8')
            print(f"📄 Error completo del servidor:")
            print(error_data)
            
            # Intentar parsear como JSON para ver detalles
            try:
                error_json = json.loads(error_data)
                print(f"\n🔍 Error parseado:")
                for key, value in error_json.items():
                    print(f"   {key}: {value}")
            except:
                print("No es JSON válido")
                
        except Exception as read_error:
            print(f"Error leyendo respuesta de error: {read_error}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        traceback.print_exc()

def test_parametros_independientes():
    """Test de cada parámetro por separado para identificar el problemático"""
    
    print("\n🔍 TEST: Parámetros independientes")
    print("=" * 60)
    
    # Test 1: Solo con plan personalizado (sin porcentajes)
    print("\n1️⃣ Solo plan personalizado (sin porcentajes):")
    test_simple_request({
        'anio': '2024',
        'plan': 'personalizado',
        'mr_seats': '300',
        'rp_seats': '200'
    }, {})
    
    # Test 2: Agregar porcentajes vacíos
    print("\n2️⃣ Con porcentajes vacíos:")
    test_simple_request({
        'anio': '2024',
        'plan': 'personalizado',
        'mr_seats': '300',
        'rp_seats': '200'
    }, {
        'porcentajes_partidos': '{}',
        'partidos_fijos': '{}',
        'overrides_pool': '{}'
    })
    
    # Test 3: Con un solo partido
    print("\n3️⃣ Con un solo partido:")
    test_simple_request({
        'anio': '2024',
        'plan': 'personalizado',
        'mr_seats': '300',
        'rp_seats': '200'
    }, {
        'porcentajes_partidos': '{"MORENA": 100.0}',
        'partidos_fijos': '{}',
        'overrides_pool': '{}'
    })
    
    # Test 4: Con partidos principales 2024
    print("\n4️⃣ Con partidos principales 2024:")
    test_simple_request({
        'anio': '2024',
        'plan': 'personalizado',
        'mr_seats': '300',
        'rp_seats': '200'
    }, {
        'porcentajes_partidos': '{"MORENA": 50.0, "PAN": 30.0, "PRI": 20.0}',
        'partidos_fijos': '{}',
        'overrides_pool': '{}'
    })

def test_simple_request(query_params, body_data):
    """Función auxiliar para hacer requests simples"""
    
    query_string = urllib.parse.urlencode(query_params)
    url = f"https://back-electoral.onrender.com/procesar/diputados?{query_string}"
    body_encoded = urllib.parse.urlencode(body_data).encode('utf-8') if body_data else b''
    
    try:
        req = urllib.request.Request(
            url,
            data=body_encoded if body_data else None,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            },
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            status_code = response.getcode()
            
            if status_code == 200:
                print(f"   ✅ Status {status_code} - FUNCIONA")
            else:
                print(f"   ❌ Status {status_code} - ERROR")
                
    except urllib.error.HTTPError as e:
        print(f"   ❌ HTTP ERROR {e.code}")
        if e.code == 500:
            try:
                error_data = e.read().decode('utf-8')
                # Solo mostrar primera línea del error
                first_line = error_data.split('\n')[0][:100]
                print(f"   📄 Error: {first_line}...")
            except:
                pass
        
    except Exception as e:
        print(f"   ❌ Exception: {type(e).__name__}: {e}")

if __name__ == "__main__":
    print("🧪 DIAGNÓSTICO DETALLADO: EDITAR PORCENTAJES")
    print("=" * 70)
    
    # Test principal con logs detallados
    test_con_logs_detallados()
    
    # Test de parámetros independientes
    test_parametros_independientes()
    
    print("\n🎯 Esto nos ayudará a identificar EXACTAMENTE dónde falla")
    print("el procesamiento de porcentajes en el backend.")
