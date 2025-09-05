#!/usr/bin/env python3
"""
Test que simula EXACTAMENTE el comportamiento del frontend cuando se mueven sliders
"""

import json
import urllib.request
import urllib.parse

def simular_frontend_moviendo_sliders():
    """Simula exactamente lo que pasa cuando un usuario mueve sliders en el frontend"""
    
    print("🎯 SIMULACIÓN: Usuario mueve sliders en el frontend")
    print("=" * 60)
    
    # Paso 1: Estado inicial (como cuando carga la página)
    print("\n1️⃣ Estado inicial del frontend:")
    porcentajes_iniciales = {
        "MORENA": 42.1,  # Porcentajes reales de 2024
        "PAN": 21.7,
        "PRI": 11.8,
        "MC": 10.3,
        "PVEM": 8.1,
        "PT": 3.2,
        "PRD": 2.8
    }
    print(f"   Porcentajes iniciales: {porcentajes_iniciales}")
    
    # Paso 2: Usuario mueve slider de MORENA de 42.1% a 35%
    print("\n2️⃣ Usuario mueve slider de MORENA:")
    print("   MORENA: 42.1% → 35.0%")
    
    # Paso 3: Frontend re-balancea automáticamente los demás
    porcentajes_despues_slider = {
        "MORENA": 35.0,  # Usuario cambió esto
        "PAN": 23.6,     # Frontend re-calculó proporcionalmente
        "PRI": 12.8,     # Frontend re-calculó proporcionalmente
        "MC": 11.2,      # Frontend re-calculó proporcionalmente
        "PVEM": 8.8,     # Frontend re-calculó proporcionalmente
        "PT": 3.5,       # Frontend re-calculó proporcionalmente
        "PRD": 3.1       # Frontend re-calculó proporcionalmente
    }
    
    total_nuevo = sum(porcentajes_despues_slider.values())
    print(f"   Nuevos porcentajes: {porcentajes_despues_slider}")
    print(f"   Total: {total_nuevo}%")
    
    # Paso 4: Frontend envía la petición AL BACKEND
    print("\n3️⃣ Frontend envía petición al backend:")
    
    # Parámetros exactos que debería enviar el frontend
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
        'usar_coaliciones': 'true',
        'sistema': 'mixto'  # CLAVE: Este parámetro es necesario
    }
    
    body_data = {
        'porcentajes_partidos': json.dumps(porcentajes_despues_slider),
        'partidos_fijos': '{}',
        'overrides_pool': '{}'
    }
    
    print(f"   Query params: {dict(list(query_params.items())[:5])}... (+{len(query_params)-5} más)")
    print(f"   Body data: porcentajes_partidos={len(porcentajes_despues_slider)} partidos")
    
    # Enviar petición
    query_string = urllib.parse.urlencode(query_params)
    url = f"https://back-electoral.onrender.com/procesar/diputados?{query_string}"
    body_encoded = urllib.parse.urlencode(body_data).encode('utf-8')
    
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
        
        with urllib.request.urlopen(req, timeout=30) as response:
            status_code = response.getcode()
            response_data = response.read().decode('utf-8')
            
            print(f"\n📬 Respuesta del backend:")
            print(f"   Status: {status_code}")
            
            if status_code == 200:
                print("✅ SUCCESS! El backend procesó correctamente los porcentajes del slider")
                
                data = json.loads(response_data)
                print(f"   Keys disponibles: {list(data.keys())}")
                
                # Mostrar resultados
                if 'resultados_detalle' in data:
                    print("   📊 Resultados por partido:")
                    for partido, info in data['resultados_detalle'].items():
                        escanos = info.get('total_seats', 0)
                        porcentaje_votos = porcentajes_despues_slider.get(partido, 0)
                        print(f"      {partido}: {escanos} escaños ({porcentaje_votos}% votos)")
                        
                return True
                
            else:
                print(f"❌ Error {status_code}")
                print(f"   Respuesta: {response_data[:200]}...")
                return False
                
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP ERROR {e.code}")
        
        try:
            error_data = e.read().decode('utf-8')
            print(f"   Error: {error_data}")
        except:
            pass
            
        return False
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_sin_sistema_parametro():
    """Test sin el parámetro 'sistema' para ver si ese es el problema"""
    
    print("\n🔍 TEST: ¿Falla si no se envía el parámetro 'sistema'?")
    print("=" * 50)
    
    porcentajes = {
        "MORENA": 35.0,
        "PAN": 25.0,
        "PRI": 20.0,
        "MC": 15.0,
        "PVEM": 5.0
    }
    
    # SIN el parámetro 'sistema'
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
        # 'sistema': 'mixto'  <-- SIN ESTE PARÁMETRO
    }
    
    body_data = {
        'porcentajes_partidos': json.dumps(porcentajes),
        'partidos_fijos': '{}',
        'overrides_pool': '{}'
    }
    
    query_string = urllib.parse.urlencode(query_params)
    url = f"https://back-electoral.onrender.com/procesar/diputados?{query_string}"
    body_encoded = urllib.parse.urlencode(body_data).encode('utf-8')
    
    print("   SIN parámetro 'sistema'...")
    
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
        
        with urllib.request.urlopen(req, timeout=30) as response:
            status_code = response.getcode()
            
            if status_code == 200:
                print("   ✅ Funciona sin 'sistema'")
                return True
            else:
                print(f"   ❌ Error {status_code}")
                return False
                
    except urllib.error.HTTPError as e:
        print(f"   ❌ HTTP ERROR {e.code}")
        print(f"   💡 CAUSA PROBABLE: El frontend no está enviando 'sistema': 'mixto'")
        return False

if __name__ == "__main__":
    print("🧪 SIMULACIÓN COMPLETA DEL FRONTEND")
    print("=" * 40)
    
    # Test 1: Simular comportamiento completo del frontend
    frontend_ok = simular_frontend_moviendo_sliders()
    
    # Test 2: Verificar si el problema es falta del parámetro 'sistema'
    sin_sistema_ok = test_sin_sistema_parametro()
    
    print("\n🎯 DIAGNÓSTICO FINAL:")
    if frontend_ok:
        print("✅ Los porcentajes SÍ funcionan cuando se envían correctamente")
        print("💡 POSIBLE CAUSA: El frontend no está enviando 'sistema': 'mixto'")
        print("💡 SOLUCIÓN: Agregar 'sistema': 'mixto' en la petición del frontend")
    
    if not sin_sistema_ok:
        print("🔍 CONFIRMADO: El problema es que falta 'sistema': 'mixto'")
        print("📝 ACCIÓN: Revisar el código del frontend y agregar ese parámetro")
    
    print("\n📋 PARA EL FRONTEND:")
    print("   Asegúrate de incluir 'sistema': 'mixto' en los query params")
    print("   cuando uses plan: 'personalizado'")
