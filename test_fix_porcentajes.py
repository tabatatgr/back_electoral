#!/usr/bin/env python3
"""
Test para verificar que el fix de porcentajes_partidos funciona correctamente
"""

import urllib.request
import urllib.parse
import json

def test_fix_porcentajes():
    """
    Test que envía porcentajes extremos para verificar que el backend los procesa
    """
    
    # URL del endpoint
    url = "http://localhost:8001/procesar/diputados"
    
    # Parámetros de query (configuración básica)
    query_params = {
        'anio': 2024,
        'plan': 'vigente',
        'sistema': 'mixto'
    }
    
    # Construir URL con query params
    url_with_params = f"{url}?{urllib.parse.urlencode(query_params)}"
    
    # Datos del form (PORCENTAJES EXTREMOS)
    porcentajes_extremos = {
        "MORENA": 5.0,     # Dramáticamente bajo
        "PAN": 5.0,        # Dramáticamente bajo  
        "PRI": 5.0,        # Dramáticamente bajo
        "PVEM": 80.0,      # EXTREMADAMENTE ALTO
        "MC": 3.0,         # Bajo
        "PT": 2.0          # Muy bajo
    }
    
    form_data = {
        'porcentajes_partidos': json.dumps(porcentajes_extremos)
    }
    
    # Convertir a formato de form data
    data = urllib.parse.urlencode(form_data).encode('utf-8')
    
    # Headers
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    
    print("=== TEST FIX PORCENTAJES ===")
    print(f"URL: {url_with_params}")
    print(f"Form data: {form_data}")
    print(f"Porcentajes enviados: {porcentajes_extremos}")
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
                
                # Verificar que PVEM tiene muchos escaños (debido al 80%)
                if 'resultados_rp' in result:
                    rp_results = result['resultados_rp']
                    pvem_escanos = 0
                    
                    for item in rp_results:
                        if item.get('PARTIDO') == 'PVEM':
                            pvem_escanos = item.get('ESCANOS', 0)
                            break
                    
                    print(f"\n📊 RESULTADOS CLAVE:")
                    print(f"PVEM escaños (debería ser ~160 con 80%): {pvem_escanos}")
                    
                    if pvem_escanos > 100:
                        print("✅ ¡FIX FUNCIONANDO! PVEM tiene muchos escaños")
                        return True
                    else:
                        print("❌ FIX NO FUNCIONA: PVEM sigue con pocos escaños")
                        return False
                        
                else:
                    print("❌ No se encontraron resultados_rp en la respuesta")
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

if __name__ == "__main__":
    success = test_fix_porcentajes()
    if success:
        print("\n🎉 EL FIX DE PORCENTAJES FUNCIONA CORRECTAMENTE!")
    else:
        print("\n💥 EL FIX AÚN NO FUNCIONA, NECESITA MÁS TRABAJO")
