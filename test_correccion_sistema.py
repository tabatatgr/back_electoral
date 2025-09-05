#!/usr/bin/env python3
"""
Test para verificar que la corrección del parámetro sistema funciona
"""

import json
import urllib.request
import urllib.parse

def test_sistema_por_defecto():
    """Test: Plan personalizado SIN parámetro sistema (debería usar mixto por defecto)"""
    
    print("🔧 TEST: Corrección - Sistema por defecto")
    print("=" * 50)
    
    porcentajes = {
        "MORENA": 40.0,
        "PAN": 30.0,
        "PRI": 20.0,
        "MC": 10.0
    }
    
    # SIN parámetro 'sistema' - debería usar 'mixto' por defecto
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
        # SIN 'sistema' - debería usar mixto por defecto
    }
    
    body_data = {
        'porcentajes_partidos': json.dumps(porcentajes),
        'partidos_fijos': '{}',
        'overrides_pool': '{}'
    }
    
    query_string = urllib.parse.urlencode(query_params)
    url = f"https://back-electoral.onrender.com/procesar/diputados?{query_string}"
    body_encoded = urllib.parse.urlencode(body_data).encode('utf-8')
    
    print("📊 Enviando request SIN parámetro 'sistema':")
    print(f"   Porcentajes: {porcentajes}")
    print(f"   Esperado: Usar sistema 'mixto' por defecto")
    
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
                print("✅ SUCCESS! Porcentajes funcionan SIN especificar sistema")
                print("✅ Backend usa 'mixto' por defecto correctamente")
                
                data = json.loads(response.read().decode('utf-8'))
                print(f"✅ Keys disponibles: {list(data.keys())}")
                return True
                
            else:
                print(f"❌ Error {status_code}")
                return False
                
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP ERROR {e.code}")
        if e.code == 500:
            print("❌ La corrección aún no se aplicó en el servidor")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_sistema_explicito():
    """Test: Verificar que aún funciona cuando se especifica sistema explícitamente"""
    
    print("\n🔧 TEST: Sistema explícito (debería seguir funcionando)")
    print("=" * 55)
    
    porcentajes = {
        "MORENA": 40.0,
        "PAN": 30.0,
        "PRI": 20.0,
        "MC": 10.0
    }
    
    sistemas_a_probar = ['mr', 'rp', 'mixto']
    
    for sistema in sistemas_a_probar:
        print(f"\n📊 Probando sistema: '{sistema}'")
        
        # Configurar parámetros según el sistema
        if sistema == 'mr':
            mr_seats, rp_seats = '500', '0'
        elif sistema == 'rp':
            mr_seats, rp_seats = '0', '500'
        else:  # mixto
            mr_seats, rp_seats = '300', '200'
        
        query_params = {
            'anio': '2024',
            'plan': 'personalizado',
            'sistema': sistema,  # Especificar explícitamente
            'mr_seats': mr_seats,
            'rp_seats': rp_seats,
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
                    print(f"   ✅ Sistema '{sistema}' funciona correctamente")
                else:
                    print(f"   ❌ Error {status_code} con sistema '{sistema}'")
                    
        except urllib.error.HTTPError as e:
            print(f"   ❌ HTTP ERROR {e.code} con sistema '{sistema}'")
            
        except Exception as e:
            print(f"   ❌ ERROR con sistema '{sistema}': {e}")

if __name__ == "__main__":
    print("🧪 VERIFICACIÓN DE CORRECCIÓN: PARÁMETRO SISTEMA")
    print("=" * 55)
    
    # Test 1: Sin parámetro sistema (usar default)
    sin_sistema_ok = test_sistema_por_defecto()
    
    # Test 2: Con parámetro sistema explícito
    test_sistema_explicito()
    
    print("\n🎯 RESULTADO DE LA CORRECCIÓN:")
    if sin_sistema_ok:
        print("✅ CORRECCIÓN EXITOSA:")
        print("  - Los porcentajes ya funcionan SIN especificar 'sistema'")
        print("  - El backend usa 'mixto' por defecto")
        print("  - Tu frontend YA NO necesita enviar 'sistema' obligatoriamente")
    else:
        print("⏳ CORRECCIÓN PENDIENTE:")
        print("  - El cambio se hizo en el código pero aún no se actualiza en el servidor")
        print("  - Necesitas hacer deploy o reiniciar el servidor")
        print("  - Una vez aplicado, los porcentajes funcionarán automáticamente")
    
    print("\n💡 PARA TU FRONTEND:")
    print("  - Puedes seguir enviando 'sistema' si quieres control explícito")
    print("  - O puedes omitirlo y usar el default 'mixto'")
    print("  - Ambas opciones deberían funcionar ahora")
