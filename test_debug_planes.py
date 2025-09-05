#!/usr/bin/env python3
"""
Test para verificar si el problema está en el plan personalizado o en general
"""

import json
import urllib.request
import urllib.parse

def test_plan_vigente():
    """Test con plan vigente (debería funcionar)"""
    
    print("🔍 TEST: Plan vigente (baseline)")
    print("=" * 40)
    
    query_params = {
        'anio': '2024',
        'plan': 'vigente'
    }
    
    query_string = urllib.parse.urlencode(query_params)
    url = f"https://back-electoral.onrender.com/procesar/diputados?{query_string}"
    
    try:
        req = urllib.request.Request(
            url,
            method='POST',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            status_code = response.getcode()
            
            if status_code == 200:
                print("✅ Plan vigente FUNCIONA correctamente")
                data = json.loads(response.read().decode('utf-8'))
                print(f"✅ Keys disponibles: {list(data.keys())}")
                return True
            else:
                print(f"❌ Error {status_code} - Plan vigente también falla")
                return False
                
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP ERROR {e.code} - Plan vigente también falla")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_otros_planes():
    """Test con otros planes predefinidos"""
    
    print("\n🔍 TEST: Otros planes predefinidos")
    print("=" * 40)
    
    planes = ['plan_a', 'plan_c']
    
    for plan in planes:
        print(f"\n📋 Probando plan: {plan}")
        
        query_params = {
            'anio': '2024', 
            'plan': plan
        }
        
        query_string = urllib.parse.urlencode(query_params)
        url = f"https://back-electoral.onrender.com/procesar/diputados?{query_string}"
        
        try:
            req = urllib.request.Request(
                url,
                method='POST',
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json'
                }
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                status_code = response.getcode()
                
                if status_code == 200:
                    print(f"   ✅ {plan} FUNCIONA")
                else:
                    print(f"   ❌ {plan} Error {status_code}")
                    
        except urllib.error.HTTPError as e:
            print(f"   ❌ {plan} HTTP ERROR {e.code}")
            
        except Exception as e:
            print(f"   ❌ {plan} ERROR: {e}")

def test_plan_personalizado_minimo():
    """Test con plan personalizado pero parámetros mínimos válidos"""
    
    print("\n🔍 TEST: Plan personalizado con parámetros mínimos")
    print("=" * 50)
    
    # Diferentes combinaciones de parámetros para plan personalizado
    tests = [
        {
            "nombre": "Solo año y plan",
            "params": {
                'anio': '2024',
                'plan': 'personalizado'
            }
        },
        {
            "nombre": "Con escaños totales",
            "params": {
                'anio': '2024',
                'plan': 'personalizado',
                'escanos_totales': '500'
            }
        },
        {
            "nombre": "Con MR y RP",
            "params": {
                'anio': '2024',
                'plan': 'personalizado',
                'mr_seats': '300',
                'rp_seats': '200'
            }
        },
        {
            "nombre": "Con sistema mixto",
            "params": {
                'anio': '2024',
                'plan': 'personalizado',
                'mr_seats': '300',
                'rp_seats': '200',
                'sistema': 'mixto'
            }
        }
    ]
    
    for test in tests:
        print(f"\n📝 {test['nombre']}:")
        
        query_string = urllib.parse.urlencode(test['params'])
        url = f"https://back-electoral.onrender.com/procesar/diputados?{query_string}"
        
        try:
            req = urllib.request.Request(
                url,
                method='POST',
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json'
                }
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                status_code = response.getcode()
                
                if status_code == 200:
                    print(f"   ✅ FUNCIONA")
                else:
                    print(f"   ❌ Error {status_code}")
                    
        except urllib.error.HTTPError as e:
            print(f"   ❌ HTTP ERROR {e.code}")
            if e.code == 500:
                try:
                    error_data = e.read().decode('utf-8')
                    print(f"   📄 Error: {error_data[:100]}...")
                except:
                    pass
                    
        except Exception as e:
            print(f"   ❌ ERROR: {e}")

if __name__ == "__main__":
    print("🧪 DIAGNÓSTICO: IDENTIFICAR ORIGEN DEL PROBLEMA")
    print("=" * 55)
    
    # Test 1: Plan vigente (debería funcionar)
    vigente_ok = test_plan_vigente()
    
    # Test 2: Otros planes predefinidos
    test_otros_planes()
    
    # Test 3: Plan personalizado con diferentes parámetros
    test_plan_personalizado_minimo()
    
    print("\n🎯 CONCLUSIÓN:")
    if vigente_ok:
        print("✅ El backend funciona con planes predefinidos")
        print("❌ El problema está específicamente en el plan PERSONALIZADO")
        print("💡 SOLUCIÓN: Revisar la lógica de plan personalizado en el backend")
    else:
        print("❌ El backend tiene problemas generales, no solo con porcentajes")
        print("💡 SOLUCIÓN: Revisar la configuración general del servidor")
