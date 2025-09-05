#!/usr/bin/env python3
"""
Test extremo para confirmar que el backend ignora porcentajes_partidos
"""

import json
import urllib.request
import urllib.parse

def test_extremo_backend_ignora_porcentajes():
    """Test con porcentajes EXTREMOS para confirmar si el backend los ignora"""
    
    print("🚨 TEST EXTREMO: ¿Backend ignora porcentajes_partidos?")
    print("=" * 60)
    
    # Porcentajes EXTREMOS que deberían ser obvios si funcionan
    porcentajes_extremos = {
        "PVEM": 95.0,    # ¡95%! Debería dominar totalmente
        "MORENA": 2.0,   # Casi nada
        "PAN": 1.0,      # Casi nada
        "PRI": 1.0,      # Casi nada
        "MC": 1.0,       # Casi nada
        "PT": 0.0,       # Cero
        "PRD": 0.0       # Cero
    }
    
    print("📊 PORCENTAJES EXTREMOS ENVIADOS:")
    for partido, porcentaje in porcentajes_extremos.items():
        print(f"   {partido}: {porcentaje}% {'🚀' if porcentaje > 50 else '📉'}")
    
    print(f"\n💡 CON ESTOS PORCENTAJES:")
    print(f"   PVEM debería tener: ~122 escaños de 128 (95%)")
    print(f"   MORENA debería tener: ~3 escaños (2%)")
    print(f"   PT/PRD deberían tener: 0 escaños (0%)")
    
    # Enviar al backend
    query_params = {
        'anio': '2024',
        'plan': 'personalizado',
        'umbral': '0',
        'sobrerrepresentacion': '8',
        'sistema': 'mixto',
        'mr_seats': '64',
        'rp_seats': '64',
        'escanos_totales': '128',
        'reparto_mode': 'cuota',
        'reparto_method': 'hare',
        'usar_coaliciones': 'true'
    }
    
    body_data = {
        'porcentajes_partidos': json.dumps(porcentajes_extremos),
        'partidos_fijos': '{}',
        'overrides_pool': '{}'
    }
    
    query_string = urllib.parse.urlencode(query_params)
    url = f"https://back-electoral.onrender.com/procesar/diputados?{query_string}"
    body_encoded = urllib.parse.urlencode(body_data).encode('utf-8')
    
    print(f"\n🚀 Enviando porcentajes EXTREMOS...")
    
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
                data = json.loads(response.read().decode('utf-8'))
                
                print(f"\n📬 RESPUESTA DEL BACKEND:")
                
                if 'resultados_detalle' in data:
                    print("Partido | Enviado | Recibido | ¿Funciona?")
                    print("-" * 45)
                    
                    total_escanos = 0
                    backend_funciona = True
                    
                    for partido, info in data['resultados_detalle'].items():
                        escanos = info.get('total_seats', 0)
                        porcentaje_enviado = porcentajes_extremos.get(partido, 0)
                        escanos_esperados = int(128 * porcentaje_enviado / 100)
                        
                        diferencia = abs(escanos - escanos_esperados)
                        funciona = "✅" if diferencia <= 3 else "❌"  # Tolerancia de ±3
                        
                        if diferencia > 3:
                            backend_funciona = False
                        
                        print(f"{partido:<7} | {porcentaje_enviado:>6.1f}% | {escanos:>7} | {funciona}")
                        total_escanos += escanos
                    
                    print(f"\nTotal escaños: {total_escanos}")
                    
                    # Verificación específica
                    pvem_escanos = data['resultados_detalle'].get('PVEM', {}).get('total_seats', 0)
                    morena_escanos = data['resultados_detalle'].get('MORENA', {}).get('total_seats', 0)
                    
                    print(f"\n🔍 VERIFICACIÓN CRÍTICA:")
                    if pvem_escanos > 100:  # Con 95% debería tener ~122
                        print(f"✅ PVEM: {pvem_escanos} escaños - BACKEND FUNCIONA")
                    else:
                        print(f"❌ PVEM: {pvem_escanos} escaños - BACKEND IGNORA PORCENTAJES")
                        print(f"   (Debería tener ~122 con 95% de votos)")
                    
                    if morena_escanos < 10:  # Con 2% debería tener ~3
                        print(f"✅ MORENA: {morena_escanos} escaños - Correcto para 2%")
                    else:
                        print(f"❌ MORENA: {morena_escanos} escaños - Demasiado para 2%")
                    
                    return backend_funciona
                
            else:
                print(f"❌ Error {status_code}")
                return False
                
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP ERROR {e.code}")
        try:
            error_data = e.read().decode('utf-8')
            print(f"Error: {error_data[:200]}...")
        except:
            pass
        return False
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_sin_porcentajes_baseline():
    """Test sin porcentajes para comparar baseline"""
    
    print("\n🔍 TEST BASELINE: Sin porcentajes (datos originales)")
    print("=" * 55)
    
    query_params = {
        'anio': '2024',
        'plan': 'personalizado',
        'umbral': '0',
        'sobrerrepresentacion': '8',
        'sistema': 'mixto',
        'mr_seats': '64',
        'rp_seats': '64',
        'escanos_totales': '128',
        'reparto_mode': 'cuota',
        'reparto_method': 'hare',
        'usar_coaliciones': 'true'
    }
    
    # SIN porcentajes_partidos
    body_data = {}
    
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
                data = json.loads(response.read().decode('utf-8'))
                
                print("📊 RESULTADOS BASELINE (sin porcentajes):")
                if 'resultados_detalle' in data:
                    for partido, info in data['resultados_detalle'].items():
                        escanos = info.get('total_seats', 0)
                        print(f"   {partido}: {escanos} escaños")
                        
                return data
                
    except Exception as e:
        print(f"❌ Error en baseline: {e}")
        return None

if __name__ == "__main__":
    print("🧪 TEST DEFINITIVO: ¿BACKEND IGNORA PORCENTAJES?")
    print("=" * 60)
    
    # Test 1: Baseline sin porcentajes
    baseline = test_sin_porcentajes_baseline()
    
    # Test 2: Con porcentajes extremos
    funciona = test_extremo_backend_ignora_porcentajes()
    
    print("\n🎯 DIAGNÓSTICO FINAL:")
    if funciona:
        print("✅ EL BACKEND SÍ PROCESA LOS PORCENTAJES")
        print("💡 El problema podría estar en otro lado")
    else:
        print("❌ EL BACKEND IGNORA COMPLETAMENTE LOS PORCENTAJES")
        print("🔧 CAUSAS POSIBLES:")
        print("   1. El deploy no se aplicó")
        print("   2. Hay caché en el servidor")
        print("   3. El código lee de otro parámetro")
        print("   4. Hay un bug en el procesamiento")
        print("\n💡 SOLUCIÓN:")
        print("   Revisar logs del servidor para ver si está leyendo 'porcentajes_partidos'")
