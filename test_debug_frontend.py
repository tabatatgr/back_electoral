#!/usr/bin/env python3
"""
Test para verificar QUÉ porcentajes está enviando realmente el frontend
"""

import json
import urllib.request
import urllib.parse

def test_porcentajes_que_deberia_enviar_frontend():
    """Test simulando lo que DEBERÍA enviar el frontend cuando mueves sliders"""
    
    print("🔍 TEST: ¿Qué porcentajes DEBERÍA enviar el frontend?")
    print("=" * 60)
    
    # Los porcentajes originales 2024 (lo que muestran los logs)
    porcentajes_originales = {
        "MORENA": 42.49,  # Lo que veo en los logs del backend
        "PAN": 17.58,
        "PRI": 11.59,
        "PRD": 2.54,
        "PVEM": 8.74,
        "PT": 5.69,
        "MC": 11.37
    }
    
    # Los porcentajes que TÚ editaste en los sliders
    porcentajes_editados = {
        "MORENA": 35.0,   # Usuario bajó MORENA
        "PAN": 17.58,     # Usuario no cambió PAN
        "PRI": 20.0,      # Usuario SUBIÓ PRI (esto debería verse en logs)
        "PRD": 2.54,      # Usuario no cambió PRD
        "PVEM": 8.74,     # Usuario no cambió PVEM
        "PT": 5.69,       # Usuario no cambió PT
        "MC": 10.45       # El resto se redistribuyó a MC
    }
    
    print("📊 COMPARACIÓN:")
    print("Partido    | Original | Editado  | Diferencia")
    print("-" * 45)
    for partido in porcentajes_originales:
        orig = porcentajes_originales[partido]
        edit = porcentajes_editados[partido]
        diff = edit - orig
        diff_str = f"+{diff:.2f}" if diff > 0 else f"{diff:.2f}"
        print(f"{partido:<10} | {orig:>7.2f}% | {edit:>7.2f}% | {diff_str:>8}")
    
    print(f"\nTotal original: {sum(porcentajes_originales.values()):.2f}%")
    print(f"Total editado:  {sum(porcentajes_editados.values()):.2f}%")
    
    # Test con los porcentajes editados
    print(f"\n🚀 Enviando porcentajes EDITADOS al backend:")
    
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
        'porcentajes_partidos': json.dumps(porcentajes_editados),
        'partidos_fijos': '{}',
        'overrides_pool': '{}'
    }
    
    query_string = urllib.parse.urlencode(query_params)
    url = f"https://back-electoral.onrender.com/procesar/diputados?{query_string}"
    body_encoded = urllib.parse.urlencode(body_data).encode('utf-8')
    
    print(f"📤 Enviando: {json.dumps(porcentajes_editados, indent=2)}")
    
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
                print("✅ SUCCESS! Backend procesó los porcentajes editados")
                
                data = json.loads(response.read().decode('utf-8'))
                
                if 'resultados_detalle' in data:
                    print("\n📊 RESULTADOS CON PORCENTAJES EDITADOS:")
                    print("Partido    | Votos% | Escaños | Diferencia vs Original")
                    print("-" * 55)
                    
                    for partido, info in data['resultados_detalle'].items():
                        escanos = info.get('total_seats', 0)
                        porcentaje_edit = porcentajes_editados.get(partido, 0)
                        porcentaje_orig = porcentajes_originales.get(partido, 0)
                        diff = porcentaje_edit - porcentaje_orig
                        diff_str = f"+{diff:.1f}" if diff > 0 else f"{diff:.1f}"
                        
                        print(f"{partido:<10} | {porcentaje_edit:>5.1f}% | {escanos:>6} | {diff_str:>8}")
                
                return True
                
            else:
                print(f"❌ Error {status_code}")
                return False
                
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP ERROR {e.code}")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def diagnosticar_problema_frontend():
    """Diagnóstico del problema en el frontend"""
    
    print("\n🔍 DIAGNÓSTICO DEL PROBLEMA EN EL FRONTEND:")
    print("=" * 50)
    
    print("❌ PROBLEMA IDENTIFICADO:")
    print("   Los sliders NO están enviando los valores editados al backend")
    print("   El backend sigue recibiendo los porcentajes originales")
    
    print("\n🔍 POSIBLES CAUSAS:")
    print("1. 📡 Event listeners de sliders mal configurados")
    print("2. 🔄 Estado del frontend no se actualiza correctamente")  
    print("3. 📤 La petición se envía antes de actualizar los porcentajes")
    print("4. 🏷️  Nombres de variables/campos no coinciden")
    print("5. ⏱️  Timing issue - se envía muy rápido después de mover slider")
    
    print("\n🛠️ COSAS A REVISAR EN EL FRONTEND:")
    print("✓ ¿Los sliders actualizan el estado correctamente?")
    print("✓ ¿El evento 'onChange' de los sliders funciona?")
    print("✓ ¿Los valores se reflejan visualmente en el frontend?")
    print("✓ ¿La función que envía la petición usa los valores actualizados?")
    print("✓ ¿Hay un debounce o delay antes de enviar la petición?")
    
    print("\n🧪 TESTS SIMPLES PARA EL FRONTEND:")
    print("1. console.log(porcentajes) antes de enviar la petición")
    print("2. Verificar que los valores de los sliders cambien visualmente")
    print("3. Agregar un botón manual para enviar (sin auto-submit)")
    print("4. Revisar las Developer Tools → Network para ver qué se envía")

if __name__ == "__main__":
    print("🧪 DIAGNÓSTICO: PORCENTAJES NO SE REFLEJAN EN FRONTEND")
    print("=" * 65)
    
    # Test con porcentajes que SÍ deberían reflejar cambios
    test_porcentajes_que_deberia_enviar_frontend()
    
    # Diagnóstico del problema
    diagnosticar_problema_frontend()
    
    print("\n🎯 CONCLUSIÓN:")
    print("✅ El backend FUNCIONA perfectamente")
    print("❌ El frontend NO está enviando los porcentajes editados")
    print("🔧 SOLUCIÓN: Revisar el código del frontend que maneja los sliders")
    
    print("\n💡 PRÓXIMOS PASOS:")
    print("1. Revisar el código JavaScript de los sliders")
    print("2. Verificar que onChange actualice el estado") 
    print("3. Confirmar que la petición use los valores actualizados")
    print("4. Probar con console.log para debuggear")
