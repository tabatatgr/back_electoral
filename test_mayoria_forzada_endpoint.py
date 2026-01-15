"""
Test de integración para el endpoint GET /calcular/mayoria_forzada

Simula el flujo completo:
1. GET /calcular/mayoria_forzada -> obtiene configuración
2. POST /procesar/diputados -> aplica configuración
3. Verifica que el partido obtenga la mayoría deseada

Autor: Sistema Electoral v2.0
Fecha: 2024
"""

import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint_mayoria_simple():
    """Test 1: Mayoría simple para MORENA"""
    print("\n" + "="*80)
    print("TEST 1: Endpoint GET /calcular/mayoria_forzada - Mayoría SIMPLE")
    print("="*80)
    
    try:
        # Paso 1: Llamar al endpoint de mayoría forzada
        print("\nPaso 1: GET /calcular/mayoria_forzada")
        params = {
            "partido": "MORENA",
            "tipo_mayoria": "simple",
            "plan": "vigente",  # 300 MR + 100 RP
            "aplicar_topes": "true"
        }
        
        print(f"Parámetros: {params}")
        response = requests.get(f"{BASE_URL}/calcular/mayoria_forzada", params=params)
        
        if response.status_code != 200:
            print(f"✗ Error HTTP {response.status_code}")
            print(response.text)
            return False
        
        data = response.json()
        print(f"✓ Respuesta recibida")
        
        if not data.get('viable'):
            print(f"✗ Configuración no viable: {data.get('razon', 'Sin razón')}")
            return False
        
        print(f"\nObjetivo: {data['objetivo_escanos']} escaños")
        print(f"MR ganados: {data['detalle']['mr_ganados']}/{data['detalle']['mr_total']}")
        print(f"RP esperado: {data['detalle']['rp_esperado']}/{data['detalle']['rp_total']}")
        print(f"Votos: {data['detalle']['pct_votos']}%")
        
        # Paso 2: Usar esa configuración en procesar/diputados
        print("\nPaso 2: POST /procesar/diputados con la configuración")
        
        payload = {
            "anio": 2024,
            "aplicar_topes": True,
            "mr_distritos_manuales": data['mr_distritos_manuales'],
            "votos_custom": data['votos_custom']
        }
        
        print(f"Payload enviado:")
        print(f"  - mr_distritos_manuales: {data['mr_distritos_manuales']}")
        print(f"  - votos_custom: {data['votos_custom']}")
        
        response2 = requests.post(f"{BASE_URL}/procesar/diputados", json=payload)
        
        if response2.status_code != 200:
            print(f"✗ Error HTTP {response2.status_code}")
            print(response2.text)
            return False
        
        resultado = response2.json()
        print(f"✓ Procesamiento completado")
        
        # Paso 3: Verificar resultado
        print("\nPaso 3: Verificar que MORENA obtuvo mayoría simple (≥201)")
        
        partidos = resultado.get('partidos', {})
        morena_escanos = None
        
        for p in partidos:
            if p['partido'] == 'MORENA':
                morena_escanos = p['total']
                print(f"\nMORENA obtuvo: {morena_escanos} escaños")
                print(f"  - MR: {p['mr']}")
                print(f"  - RP: {p['rp']}")
                print(f"  - Coalición: {p['coalicion']}")
                break
        
        if morena_escanos is None:
            print(f"✗ No se encontró MORENA en resultados")
            return False
        
        if morena_escanos >= 201:
            print(f"\n✓ MORENA alcanzó mayoría simple ({morena_escanos} ≥ 201)")
            print(f"\n✓ TEST 1 PASADO")
            return True
        else:
            print(f"\n✗ MORENA no alcanzó mayoría simple ({morena_escanos} < 201)")
            print(f"\n✗ TEST 1 FALLADO")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n✗ ERROR: No se pudo conectar al servidor en {BASE_URL}")
        print(f"   Asegúrate de que el servidor esté corriendo: uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_endpoint_mayoria_calificada_con_topes():
    """Test 2: Mayoría calificada CON topes - debe rechazar"""
    print("\n" + "="*80)
    print("TEST 2: Endpoint - Mayoría CALIFICADA con topes (debe rechazar)")
    print("="*80)
    
    try:
        print("\nPaso 1: GET /calcular/mayoria_forzada")
        params = {
            "partido": "MORENA",
            "tipo_mayoria": "calificada",
            "plan": "vigente",  # 300 MR + 100 RP
            "aplicar_topes": "true"
        }
        
        print(f"Parámetros: {params}")
        response = requests.get(f"{BASE_URL}/calcular/mayoria_forzada", params=params)
        
        if response.status_code != 200:
            print(f"✗ Error HTTP {response.status_code}")
            return False
        
        data = response.json()
        print(f"✓ Respuesta recibida")
        
        if not data.get('viable'):
            print(f"✓ Correctamente rechazado: {data.get('razon', 'Sin razón')}")
            if 'sugerencia' in data:
                print(f"  Sugerencia: {data['sugerencia']}")
            print(f"\n✓ TEST 2 PASADO")
            return True
        else:
            print(f"✗ ERROR: No debería ser viable con topes")
            print(f"\n✗ TEST 2 FALLADO")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n✗ ERROR: No se pudo conectar al servidor en {BASE_URL}")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        return False

def test_endpoint_mayoria_calificada_sin_topes():
    """Test 3: Mayoría calificada SIN topes"""
    print("\n" + "="*80)
    print("TEST 3: Endpoint - Mayoría CALIFICADA sin topes")
    print("="*80)
    
    try:
        print("\nPaso 1: GET /calcular/mayoria_forzada")
        params = {
            "partido": "MORENA",
            "tipo_mayoria": "calificada",
            "plan": "judicatura",  # 200 MR + 200 RP
            "aplicar_topes": "false"
        }
        
        print(f"Parámetros: {params}")
        response = requests.get(f"{BASE_URL}/calcular/mayoria_forzada", params=params)
        
        if response.status_code != 200:
            print(f"✗ Error HTTP {response.status_code}")
            print(response.text)
            return False
        
        data = response.json()
        print(f"✓ Respuesta recibida")
        
        if not data.get('viable'):
            print(f"✗ Configuración no viable: {data.get('razon', 'Sin razón')}")
            return False
        
        print(f"\nObjetivo: {data['objetivo_escanos']} escaños")
        print(f"MR ganados: {data['detalle']['mr_ganados']}/{data['detalle']['mr_total']}")
        print(f"RP esperado: {data['detalle']['rp_esperado']}/{data['detalle']['rp_total']}")
        print(f"Votos: {data['detalle']['pct_votos']}%")
        
        if data.get('advertencias'):
            print("\n⚠️  Advertencias:")
            for adv in data['advertencias']:
                print(f"  - {adv}")
        
        print("\nPaso 2: POST /procesar/diputados con la configuración")
        
        payload = {
            "anio": 2024,
            "aplicar_topes": False,  # SIN TOPES
            "plan": "judicatura",
            "mr_distritos_manuales": data['mr_distritos_manuales'],
            "votos_custom": data['votos_custom']
        }
        
        response2 = requests.post(f"{BASE_URL}/procesar/diputados", json=payload)
        
        if response2.status_code != 200:
            print(f"✗ Error HTTP {response2.status_code}")
            print(response2.text)
            return False
        
        resultado = response2.json()
        print(f"✓ Procesamiento completado")
        
        print("\nPaso 3: Verificar que MORENA obtuvo mayoría calificada (≥267)")
        
        partidos = resultado.get('partidos', {})
        morena_escanos = None
        
        for p in partidos:
            if p['partido'] == 'MORENA':
                morena_escanos = p['total']
                print(f"\nMORENA obtuvo: {morena_escanos} escaños")
                print(f"  - MR: {p['mr']}")
                print(f"  - RP: {p['rp']}")
                break
        
        if morena_escanos is None:
            print(f"✗ No se encontró MORENA en resultados")
            return False
        
        if morena_escanos >= 267:
            print(f"\n✓ MORENA alcanzó mayoría calificada ({morena_escanos} ≥ 267)")
            print(f"\n✓ TEST 3 PASADO")
            return True
        else:
            print(f"\n✗ MORENA no alcanzó mayoría calificada ({morena_escanos} < 267)")
            print(f"\n✗ TEST 3 FALLADO")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n✗ ERROR: No se pudo conectar al servidor en {BASE_URL}")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecutar todos los tests de integración"""
    print("\n" + "="*80)
    print("TESTS DE INTEGRACIÓN - Endpoint /calcular/mayoria_forzada")
    print("="*80)
    print(f"\nServidor: {BASE_URL}")
    print("\nEstos tests verifican el flujo completo:")
    print("1. GET /calcular/mayoria_forzada -> obtiene configuración")
    print("2. POST /procesar/diputados -> aplica configuración")
    print("3. Verifica que el partido obtenga la mayoría deseada")
    print("\n⚠️  IMPORTANTE: El servidor debe estar corriendo en http://127.0.0.1:8000")
    print("   Comando: uvicorn main:app --reload")
    
    input("\nPresiona ENTER para continuar...")
    
    resultados = []
    
    # Test 1
    resultados.append(("Mayoría simple", test_endpoint_mayoria_simple()))
    
    # Test 2
    resultados.append(("Mayoría calificada CON topes", test_endpoint_mayoria_calificada_con_topes()))
    
    # Test 3
    resultados.append(("Mayoría calificada SIN topes", test_endpoint_mayoria_calificada_sin_topes()))
    
    # Resumen
    print("\n" + "="*80)
    print("RESUMEN DE TESTS DE INTEGRACIÓN")
    print("="*80)
    
    total_tests = len(resultados)
    tests_pasados = sum(1 for _, ok in resultados if ok)
    
    for nombre, ok in resultados:
        estado = "✓ PASADO" if ok else "✗ FALLADO"
        print(f"{estado}: {nombre}")
    
    print(f"\nTotal: {tests_pasados}/{total_tests} tests pasados")
    
    if tests_pasados == total_tests:
        print("\n🎉 TODOS LOS TESTS DE INTEGRACIÓN PASARON")
        print("\n✅ El endpoint GET /calcular/mayoria_forzada funciona correctamente")
        print("✅ La integración con POST /procesar/diputados es exitosa")
        print("✅ Los partidos alcanzan las mayorías forzadas correctamente")
        return 0
    else:
        print(f"\n❌ {total_tests - tests_pasados} tests fallaron")
        return 1

if __name__ == "__main__":
    sys.exit(main())
