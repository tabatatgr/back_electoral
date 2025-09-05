#!/usr/bin/env python3
"""
Test: Los porcentajes deben funcionar con CUALQUIER sistema electoral
"""

import json
import urllib.request
import urllib.parse

def test_porcentajes_con_todos_los_sistemas():
    """Test: Los porcentajes deben funcionar con MR, RP y Mixto"""
    
    print("🎯 TEST: Porcentajes con TODOS los sistemas electorales")
    print("=" * 60)
    
    # Porcentajes de prueba
    porcentajes = {
        "MORENA": 40.0,
        "PAN": 30.0,
        "PRI": 20.0,
        "MC": 10.0
    }
    
    # Diferentes sistemas que DEBEN funcionar
    sistemas = [
        {
            "nombre": "Mayoría Relativa (MR)",
            "params": {
                'sistema': 'mr',
                'mr_seats': '500',
                'rp_seats': '0'
            }
        },
        {
            "nombre": "Representación Proporcional (RP)",
            "params": {
                'sistema': 'rp', 
                'mr_seats': '0',
                'rp_seats': '500'
            }
        },
        {
            "nombre": "Sistema Mixto",
            "params": {
                'sistema': 'mixto',
                'mr_seats': '300',
                'rp_seats': '200'
            }
        }
    ]
    
    resultados = []
    
    for sistema in sistemas:
        print(f"\n📊 Probando: {sistema['nombre']}")
        
        # Parámetros base
        query_params = {
            'anio': '2024',
            'plan': 'personalizado',
            'escanos_totales': '500',
            'umbral': '0.03',
            'sobrerrepresentacion': '8',
            'reparto_mode': 'cuota',
            'reparto_method': 'hare',
            'usar_coaliciones': 'true'
        }
        
        # Agregar parámetros específicos del sistema
        query_params.update(sistema['params'])
        
        body_data = {
            'porcentajes_partidos': json.dumps(porcentajes),
            'partidos_fijos': '{}',
            'overrides_pool': '{}'
        }
        
        # Hacer request
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
                
                if status_code == 200:
                    print(f"   ✅ FUNCIONA - {sistema['nombre']}")
                    resultados.append((sistema['nombre'], True, "OK"))
                else:
                    print(f"   ❌ Error {status_code} - {sistema['nombre']}")
                    resultados.append((sistema['nombre'], False, f"HTTP {status_code}"))
                    
        except urllib.error.HTTPError as e:
            print(f"   ❌ HTTP ERROR {e.code} - {sistema['nombre']}")
            resultados.append((sistema['nombre'], False, f"HTTP {e.code}"))
            
        except Exception as e:
            print(f"   ❌ ERROR - {sistema['nombre']}: {e}")
            resultados.append((sistema['nombre'], False, f"Exception: {e}"))
    
    return resultados

def test_sin_especificar_sistema():
    """Test: ¿Qué pasa si no especificamos sistema en absoluto?"""
    
    print("\n🔍 TEST: Sin especificar sistema (debería usar default)")
    print("=" * 55)
    
    porcentajes = {
        "MORENA": 40.0,
        "PAN": 30.0,
        "PRI": 20.0,
        "MC": 10.0
    }
    
    # SIN parámetro 'sistema' - debería usar un default
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
        # SIN 'sistema' - el backend debería inferirlo o usar default
    }
    
    body_data = {
        'porcentajes_partidos': json.dumps(porcentajes),
        'partidos_fijos': '{}',
        'overrides_pool': '{}'
    }
    
    query_string = urllib.parse.urlencode(query_params)
    url = f"https://back-electoral.onrender.com/procesar/diputados?{query_string}"
    body_encoded = urllib.parse.urlencode(body_data).encode('utf-8')
    
    print("   Parámetros: sin 'sistema' especificado")
    
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
                print("   ✅ FUNCIONA - Backend infiere sistema correctamente")
                return True
            else:
                print(f"   ❌ Error {status_code}")
                return False
                
    except urllib.error.HTTPError as e:
        print(f"   ❌ HTTP ERROR {e.code}")
        print("   💡 PROBLEMA: Backend no puede inferir sistema automáticamente")
        return False
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

def test_logica_de_inferencia():
    """Test: Probar si el backend puede inferir sistema desde mr_seats/rp_seats"""
    
    print("\n🔍 TEST: ¿Backend infiere sistema desde mr_seats/rp_seats?")
    print("=" * 55)
    
    porcentajes = {
        "MORENA": 40.0,
        "PAN": 30.0,
        "PRI": 20.0,
        "MC": 10.0
    }
    
    tests_inferencia = [
        {
            "nombre": "Solo MR (mr_seats=500, rp_seats=0)",
            "params": {'mr_seats': '500', 'rp_seats': '0'},
            "esperado": "Debería inferir sistema='mr'"
        },
        {
            "nombre": "Solo RP (mr_seats=0, rp_seats=500)",
            "params": {'mr_seats': '0', 'rp_seats': '500'},
            "esperado": "Debería inferir sistema='rp'"
        },
        {
            "nombre": "Mixto (mr_seats=300, rp_seats=200)",
            "params": {'mr_seats': '300', 'rp_seats': '200'},
            "esperado": "Debería inferir sistema='mixto'"
        }
    ]
    
    for test in tests_inferencia:
        print(f"\n📝 {test['nombre']}")
        print(f"   {test['esperado']}")
        
        query_params = {
            'anio': '2024',
            'plan': 'personalizado',
            'escanos_totales': '500',
            'umbral': '0.03',
            'sobrerrepresentacion': '8',
            'reparto_mode': 'cuota',
            'reparto_method': 'hare',
            'usar_coaliciones': 'true'
        }
        
        query_params.update(test['params'])
        
        body_data = {
            'porcentajes_partidos': json.dumps(porcentajes),
            'partidos_fijos': '{}',
            'overrides_pool': '{}'
        }
        
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
                
                if status_code == 200:
                    print(f"   ✅ FUNCIONA")
                else:
                    print(f"   ❌ Error {status_code}")
                    
        except urllib.error.HTTPError as e:
            print(f"   ❌ HTTP ERROR {e.code}")
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")

if __name__ == "__main__":
    print("🧪 TEST COMPLETO: PORCENTAJES CON TODOS LOS SISTEMAS")
    print("=" * 65)
    
    # Test 1: Porcentajes con sistemas explícitos
    resultados = test_porcentajes_con_todos_los_sistemas()
    
    # Test 2: Sin especificar sistema
    sin_sistema_ok = test_sin_especificar_sistema()
    
    # Test 3: Lógica de inferencia
    test_logica_de_inferencia()
    
    print("\n🎯 RESUMEN DE RESULTADOS:")
    print("=" * 30)
    for nombre, funciona, detalle in resultados:
        estado = "✅" if funciona else "❌"
        print(f"{estado} {nombre}: {detalle}")
    
    print(f"\n📊 ANÁLISIS:")
    sistemas_ok = sum(1 for _, funciona, _ in resultados if funciona)
    total_sistemas = len(resultados)
    
    if sistemas_ok == total_sistemas:
        print("✅ PERFECTO: Los porcentajes funcionan con TODOS los sistemas")
    elif sistemas_ok > 0:
        print(f"⚠️  PARCIAL: Funciona con {sistemas_ok}/{total_sistemas} sistemas")
        print("💡 PROBLEMA: El backend tiene lógica inconsistente")
    else:
        print("❌ CRÍTICO: No funciona con ningún sistema")
        print("💡 PROBLEMA: Error fundamental en el procesamiento de porcentajes")
    
    print(f"\n💡 RECOMENDACIÓN:")
    print("El backend debería:")
    print("1. Permitir porcentajes con CUALQUIER sistema (MR, RP, Mixto)")
    print("2. Inferir automáticamente el sistema desde mr_seats/rp_seats")
    print("3. No requerir parámetro 'sistema' explícito")
