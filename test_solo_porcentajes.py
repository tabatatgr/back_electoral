#!/usr/bin/env python3
"""
Test específico: Plan personalizado funciona, pero falla al agregar porcentajes
"""

import json
import urllib.request
import urllib.parse

def test_plan_personalizado_sin_porcentajes():
    """Test: Plan personalizado que SÍ funciona (sin porcentajes)"""
    
    print("✅ TEST: Plan personalizado SIN porcentajes (debería funcionar)")
    print("=" * 60)
    
    query_params = {
        'anio': '2024',
        'plan': 'personalizado',
        'mr_seats': '300',
        'rp_seats': '200',
        'sistema': 'mixto',  # Este parámetro hace que funcione
        'umbral': '0.03',
        'sobrerrepresentacion': '8',
        'reparto_mode': 'cuota',
        'reparto_method': 'hare',
        'usar_coaliciones': 'true'
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
                print("✅ SÍ FUNCIONA - Plan personalizado sin porcentajes")
                return True
            else:
                print(f"❌ Error {status_code}")
                return False
                
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP ERROR {e.code}")
        return False

def test_plan_personalizado_con_porcentajes():
    """Test: MISMO plan personalizado pero AGREGANDO porcentajes"""
    
    print("\n❌ TEST: MISMO plan personalizado CON porcentajes (debería fallar)")
    print("=" * 60)
    
    # EXACTAMENTE los mismos parámetros que el test anterior
    query_params = {
        'anio': '2024',
        'plan': 'personalizado',
        'mr_seats': '300',
        'rp_seats': '200',
        'sistema': 'mixto',  # Mismo parámetro que funciona
        'umbral': '0.03',
        'sobrerrepresentacion': '8',
        'reparto_mode': 'cuota',
        'reparto_method': 'hare',
        'usar_coaliciones': 'true'
    }
    
    # ÚNICA DIFERENCIA: agregar porcentajes en el body
    body_data = {
        'porcentajes_partidos': json.dumps({
            "MORENA": 40.0,
            "PAN": 30.0,
            "PRI": 20.0,
            "MC": 10.0
        }),
        'partidos_fijos': '{}',
        'overrides_pool': '{}'
    }
    
    query_string = urllib.parse.urlencode(query_params)
    url = f"https://back-electoral.onrender.com/procesar/diputados?{query_string}"
    body_encoded = urllib.parse.urlencode(body_data).encode('utf-8')
    
    print(f"📊 ÚNICA DIFERENCIA: agregar porcentajes = {body_data['porcentajes_partidos']}")
    
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
                print("🤔 EXTRAÑO: También funciona CON porcentajes")
                print("💡 Entonces el problema podría ser otro...")
                return True
            else:
                print(f"❌ Error {status_code} - Confirma que es problema de porcentajes")
                return False
                
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP ERROR {e.code} - Confirma que es problema de porcentajes")
        
        # Capturar error exacto
        try:
            error_data = e.read().decode('utf-8')
            print(f"📄 Error exacto: {error_data}")
        except:
            pass
            
        return False

def test_diferentes_formas_porcentajes():
    """Test diferentes formas de enviar porcentajes"""
    
    print("\n🔍 TEST: Diferentes formas de enviar porcentajes")
    print("=" * 50)
    
    base_params = {
        'anio': '2024',
        'plan': 'personalizado',
        'mr_seats': '300',
        'rp_seats': '200',
        'sistema': 'mixto',
        'umbral': '0.03',
        'sobrerrepresentacion': '8',
        'reparto_mode': 'cuota',
        'reparto_method': 'hare',
        'usar_coaliciones': 'true'
    }
    
    # Diferentes formas de enviar porcentajes
    tests = [
        {
            "nombre": "porcentajes_partidos en body",
            "body": {
                'porcentajes_partidos': '{"MORENA": 50.0, "PAN": 50.0}'
            }
        },
        {
            "nombre": "votos_custom en body", 
            "body": {
                'votos_custom': '{"MORENA": 50.0, "PAN": 50.0}'
            }
        },
        {
            "nombre": "porcentajes_partidos en query",
            "query_extra": {
                'porcentajes_partidos': '{"MORENA": 50.0, "PAN": 50.0}'
            },
            "body": {}
        }
    ]
    
    for test in tests:
        print(f"\n📝 {test['nombre']}:")
        
        # Construir query params
        query_params = base_params.copy()
        if 'query_extra' in test:
            query_params.update(test['query_extra'])
        
        query_string = urllib.parse.urlencode(query_params)
        url = f"https://back-electoral.onrender.com/procesar/diputados?{query_string}"
        
        # Construir body
        body_data = test.get('body', {})
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
                    print(f"   ✅ FUNCIONA")
                else:
                    print(f"   ❌ Error {status_code}")
                    
        except urllib.error.HTTPError as e:
            print(f"   ❌ HTTP ERROR {e.code}")

if __name__ == "__main__":
    print("🎯 TEST ESPECÍFICO: ¿Los porcentajes rompen un plan que funciona?")
    print("=" * 70)
    
    # Test 1: Plan personalizado sin porcentajes (debería funcionar)
    sin_porcentajes_ok = test_plan_personalizado_sin_porcentajes()
    
    # Test 2: MISMO plan pero con porcentajes (debería fallar según tu experiencia)
    con_porcentajes_ok = test_plan_personalizado_con_porcentajes()
    
    # Test 3: Diferentes formas de enviar porcentajes
    test_diferentes_formas_porcentajes()
    
    print("\n🎯 CONCLUSIÓN:")
    if sin_porcentajes_ok and not con_porcentajes_ok:
        print("✅ CONFIRMADO: Los porcentajes SÍ rompen el plan personalizado")
        print("💡 PRÓXIMO PASO: Revisar cómo procesa 'porcentajes_partidos' el backend")
    elif sin_porcentajes_ok and con_porcentajes_ok:
        print("🤔 EXTRAÑO: Ambos funcionan - el problema podría ser otro")
    else:
        print("❌ Problema más profundo - ni siquiera funciona sin porcentajes")
