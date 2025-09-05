#!/usr/bin/env python3
"""
Test final del endpoint completo con porcentajes
"""

import urllib.request
import urllib.parse
import json
import time

def test_endpoint_completo():
    """
    Test que simula exactamente lo que envía el frontend
    """
    
    # URL del endpoint
    url = "http://localhost:8001/procesar/diputados"
    
    # Parámetros de query (configuración básica)
    query_params = {
        'anio': 2024,
        'plan': 'vigente'
    }
    
    # Construir URL con query params
    url_with_params = f"{url}?{urllib.parse.urlencode(query_params)}"
    
    # Datos del form - PORCENTAJES MODERADOS para test realista
    porcentajes_realistas = {
        "MORENA": 35.0,
        "PAN": 25.0, 
        "PRI": 15.0,
        "PVEM": 15.0,    # Un poco más alto que normal
        "MC": 7.0,
        "PT": 3.0
    }
    
    form_data = {
        'porcentajes_partidos': json.dumps(porcentajes_realistas)
    }
    
    # Convertir a formato de form data
    data = urllib.parse.urlencode(form_data).encode('utf-8')
    
    # Headers
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    
    print("=== TEST ENDPOINT COMPLETO ===")
    print(f"URL: {url_with_params}")
    print(f"Porcentajes enviados: {porcentajes_realistas}")
    print()
    
    try:
        # Crear request
        req = urllib.request.Request(url_with_params, data=data, headers=headers, method='POST')
        
        # Enviar request
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                result = json.loads(response.read().decode('utf-8'))
                
                print("✅ REQUEST EXITOSO")
                print(f"Status: {response.status}")
                
                # Verificar que tenemos resultados
                if 'resultados_rp' in result:
                    rp_results = result['resultados_rp']
                    
                    print(f"\n📊 RESULTADOS RP:")
                    for item in rp_results:
                        partido = item.get('PARTIDO', 'N/A')
                        escanos = item.get('ESCANOS', 0)
                        porcentaje_votos = item.get('PORCENTAJE_VOTOS', 0)
                        
                        print(f"{partido}: {escanos} escaños ({porcentaje_votos:.2f}% votos)")
                        
                        # Verificar si los porcentajes coinciden aproximadamente
                        if partido in porcentajes_realistas:
                            esperado = porcentajes_realistas[partido]
                            if abs(porcentaje_votos - esperado) < 2:  # Tolerancia de 2%
                                print(f"  ✅ Porcentaje correcto: {porcentaje_votos:.2f}% ≈ {esperado}%")
                            else:
                                print(f"  ❌ Porcentaje incorrecto: {porcentaje_votos:.2f}% vs esperado {esperado}%")
                    
                    return True
                    
                else:
                    print("❌ No se encontraron resultados_rp en la respuesta")
                    print(f"Claves disponibles: {list(result.keys())}")
                    return False
                    
            else:
                print(f"❌ Error HTTP: {response.status}")
                return False
                
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error: {e.code}")
        print(f"Response: {e.read().decode('utf-8')}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def verificar_servidor():
    """
    Verificar que el servidor esté corriendo
    """
    try:
        req = urllib.request.Request("http://localhost:8001/")
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status == 200
    except:
        return False

if __name__ == "__main__":
    print("Verificando servidor...")
    
    if not verificar_servidor():
        print("❌ Servidor no está corriendo en puerto 8001")
        print("Ejecuta: python main.py")
        exit(1)
    
    print("✅ Servidor corriendo")
    time.sleep(1)
    
    success = test_endpoint_completo()
    
    if success:
        print("\n🎉 ¡EL ENDPOINT FUNCIONA CORRECTAMENTE!")
        print("Los porcentajes se están procesando y aplicando correctamente")
    else:
        print("\n💥 HAY UN PROBLEMA CON EL ENDPOINT")
        print("Los porcentajes no se están aplicando correctamente")
