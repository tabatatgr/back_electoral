#!/usr/bin/env python3
"""
Test específico para la funcionalidad de EDITAR PORCENTAJES POR PARTIDO
"""

import json
import urllib.request
import urllib.parse
import traceback

def test_editar_porcentajes_partido():
    """Test específico para verificar la edición de porcentajes por partido"""
    
    print("🎯 TEST: Editar porcentajes por partido")
    print("=" * 50)
    
    # Datos de prueba: porcentajes editados por el usuario
    porcentajes_editados = {
        "MORENA": 35.0,  # Usuario cambió de 42% a 35%
        "PAN": 25.0,     # Usuario cambió de 21% a 25% 
        "PRI": 20.0,     # Usuario cambió de 11% a 20%
        "MC": 15.0,      # Usuario cambió de 10% a 15%
        "PVEM": 5.0      # Usuario cambió de 8% a 5%
    }
    
    print(f"📊 Porcentajes editados por el usuario:")
    for partido, porcentaje in porcentajes_editados.items():
        print(f"   {partido}: {porcentaje}%")
    
    total = sum(porcentajes_editados.values())
    print(f"📊 Total: {total}%")
    
    # Parámetros exactos como los envía el frontend
    query_params = {
        'anio': '2024',
        'plan': 'personalizado',
        'mr_seats': '300',
        'rp_seats': '200',
        'escanos_totales': '500',
        'umbral': '0.03',
        'sobrerrepresentacion': '8',  # Sin tilde
        'reparto_mode': 'cuota',
        'reparto_method': 'hare',
        'usar_coaliciones': 'true'
    }
    
    # Body data (lo que va en el POST)
    body_data = {
        'porcentajes_partidos': json.dumps(porcentajes_editados),
        'partidos_fijos': '{}',
        'overrides_pool': '{}'
    }
    
    # Construir URL
    query_string = urllib.parse.urlencode(query_params)
    url = f"https://back-electoral.onrender.com/procesar/diputados?{query_string}"
    
    # Preparar datos del body
    body_encoded = urllib.parse.urlencode(body_data).encode('utf-8')
    
    print(f"\n🚀 Enviando request...")
    print(f"URL: {url}")
    print(f"Body: {body_data}")
    
    try:
        # Crear request
        req = urllib.request.Request(
            url,
            data=body_encoded,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            },
            method='POST'
        )
        
        # Enviar request
        with urllib.request.urlopen(req, timeout=30) as response:
            status_code = response.getcode()
            response_data = response.read().decode('utf-8')
            
            print(f"\n📬 Status Code: {status_code}")
            
            if status_code == 200:
                print("✅ SUCCESS! Los porcentajes editados funcionan correctamente")
                try:
                    data = json.loads(response_data)
                    print(f"✅ Keys en respuesta: {list(data.keys())}")
                    
                    if 'resultados_detalle' in data:
                        print("✅ Resultados detalle:")
                        for partido, info in data['resultados_detalle'].items():
                            escanos = info.get('total_seats', 0)
                            porcentaje_original = porcentajes_editados.get(partido, 0)
                            print(f"   {partido}: {escanos} escaños (de {porcentaje_original}% votos)")
                        
                except json.JSONDecodeError:
                    print("⚠️  Respuesta no es JSON válido")
                    print(f"📄 Primeros 200 chars: {response_data[:200]}...")
            
            else:
                print(f"❌ ERROR HTTP {status_code}")
                print(f"📄 Respuesta: {response_data[:500]}...")
                
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP ERROR {e.code}")
        error_data = e.read().decode('utf-8')
        print(f"📄 Error del servidor: {error_data[:500]}...")
        
        if e.code == 500:
            print("\n🔍 ANÁLISIS DEL ERROR 500:")
            print("- El frontend está enviando los datos correctamente")
            print("- El problema está en el procesamiento interno del backend")
            print("- Específicamente en el manejo de 'porcentajes_partidos'")
            
    except urllib.error.URLError as e:
        print(f"❌ CONNECTION ERROR: {e}")
        
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        traceback.print_exc()

def test_formato_alternativo():
    """Test con formato alternativo de porcentajes"""
    
    print("\n🔍 TEST: Formato alternativo de porcentajes")
    print("=" * 50)
    
    # Mismo test pero usando 'votos_custom' en lugar de 'porcentajes_partidos'
    porcentajes_editados = {
        "MORENA": 35.0,
        "PAN": 25.0,
        "PRI": 20.0,
        "MC": 15.0,
        "PVEM": 5.0
    }
    
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
    
    # Probar con 'votos_custom' en lugar de 'porcentajes_partidos'
    body_data = {
        'votos_custom': json.dumps(porcentajes_editados),  # Cambio aquí
        'partidos_fijos': '{}',
        'overrides_pool': '{}'
    }
    
    query_string = urllib.parse.urlencode(query_params)
    url = f"https://back-electoral.onrender.com/procesar/diputados?{query_string}"
    body_encoded = urllib.parse.urlencode(body_data).encode('utf-8')
    
    print(f"🔄 Probando con 'votos_custom' en lugar de 'porcentajes_partidos'...")
    
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
                print("✅ SUCCESS! El parámetro 'votos_custom' SÍ funciona")
                print("💡 SOLUCIÓN: Usar 'votos_custom' en lugar de 'porcentajes_partidos'")
            else:
                print(f"❌ Status: {status_code} - También falla con 'votos_custom'")
                
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP ERROR {e.code} - También falla con 'votos_custom'")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    print("🧪 DIAGNÓSTICO: EDITAR PORCENTAJES POR PARTIDO")
    print("=" * 60)
    
    # Test principal: verificar funcionalidad de edición de porcentajes
    test_editar_porcentajes_partido()
    
    # Test alternativo: probar con otro parámetro
    test_formato_alternativo()
    
    print("\n🎯 OBJETIVO:")
    print("Identificar por qué falla la edición de porcentajes por partido")
    print("cuando todo lo demás funciona correctamente.")
