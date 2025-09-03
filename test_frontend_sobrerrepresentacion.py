"""
Test para verificar cómo implementar la sobrerrepresentación en el frontend
"""

import requests
import json

def test_sobrerrepresentacion_frontend():
    """
    Test para verificar si la sobrerrepresentación se puede pasar desde el frontend
    """
    print("🔍 TEST: Verificando implementación de sobrerrepresentación en el frontend")
    print("=" * 80)
    
    # URL base del API
    base_url = "http://localhost:8001"
    
    # Verificar que el servidor esté corriendo
    try:
        health_response = requests.get(f"{base_url}/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ Servidor no está corriendo. Inicia el servidor con: python main.py")
            return
    except:
        print("❌ No se puede conectar al servidor. Inicia el servidor con: python main.py")
        return
    
    print("✅ Servidor está corriendo")
    
    # 1. Verificar endpoint de diputados actual
    print("\n📊 CASO 1: ENDPOINT ACTUAL DE DIPUTADOS")
    print("-" * 50)
    
    payload_actual = {
        "anio": 2018,
        "plan": "vigente"
    }
    
    try:
        response = requests.post(f"{base_url}/procesar/diputados", json=payload_actual, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint actual funciona")
            
            # Analizar la respuesta
            if "resultados" in data:
                print(f"   • Se procesaron {len(data['resultados'])} partidos")
                
                # Verificar si hay información de sobrerrepresentación
                for partido in data['resultados'][:3]:  # Solo los top 3
                    nombre = partido.get('partido', 'N/A')
                    votos_pct = partido.get('porcentaje_votos', 0)
                    escanos_pct = partido.get('porcentaje_escanos', 0)
                    sobrer = escanos_pct - votos_pct
                    
                    print(f"   • {nombre}: {votos_pct:.1f}% votos → {escanos_pct:.1f}% escaños (sobrer: {sobrer:+.1f}%)")
            
            # Verificar si existe campo de sobrerrepresentación en la respuesta
            if "sobrerrepresentacion" in data:
                print(f"   • Campo sobrerrepresentación encontrado: {data['sobrerrepresentacion']}")
            else:
                print("   ⚠️  No hay campo 'sobrerrepresentacion' en la respuesta")
                
        else:
            print(f"❌ Error en endpoint: {response.status_code}")
            print(f"   Mensaje: {response.text}")
            
    except Exception as e:
        print(f"❌ Error llamando al endpoint: {e}")
    
    # 2. Probar con parámetros adicionales
    print("\n📊 CASO 2: INTENTANDO PASAR SOBRERREPRESENTACIÓN")
    print("-" * 50)
    
    payload_con_sobrer = {
        "anio": 2018,
        "plan": "personalizado",
        "sistema": "mixto",
        "escanos_totales": 500,
        "mr_seats": 300,
        "rp_seats": 200,
        "umbral": 0.03,
        "max_seats_per_party": 300,
        "sobrerrepresentacion": 0.08  # Intentar pasar 8%
    }
    
    try:
        response = requests.post(f"{base_url}/procesar/diputados", json=payload_con_sobrer, timeout=30)
        
        if response.status_code == 200:
            print("✅ Endpoint acepta parámetros adicionales")
            data = response.json()
            
            # Verificar si se aplicó la sobrerrepresentación
            if "resultados" in data:
                morena_data = None
                for partido in data['resultados']:
                    if partido.get('partido') == 'MORENA':
                        morena_data = partido
                        break
                
                if morena_data:
                    votos_pct = morena_data.get('porcentaje_votos', 0)
                    escanos_pct = morena_data.get('porcentaje_escanos', 0)
                    sobrer = escanos_pct - votos_pct
                    
                    print(f"   • MORENA: {votos_pct:.1f}% votos → {escanos_pct:.1f}% escaños (sobrer: {sobrer:+.1f}%)")
                    
                    if sobrer <= 8.5:  # Permitir un poco de margen
                        print("   ✅ Parece que la sobrerrepresentación se aplicó")
                    else:
                        print("   ⚠️  MORENA sigue con alta sobrerrepresentación")
                        
        else:
            print(f"❌ Error con parámetros adicionales: {response.status_code}")
            print(f"   Mensaje: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 3. Verificar documentación de la API
    print("\n📊 CASO 3: VERIFICANDO DOCUMENTACIÓN")
    print("-" * 50)
    
    try:
        docs_response = requests.get(f"{base_url}/docs", timeout=5)
        if docs_response.status_code == 200:
            print("✅ Documentación disponible en: http://localhost:8001/docs")
        else:
            print("⚠️  Documentación no disponible")
    except:
        print("⚠️  No se puede acceder a la documentación")
    
    # 4. Recomendaciones para el frontend
    print("\n💡 RECOMENDACIONES PARA EL FRONTEND")
    print("=" * 50)
    
    print("1. CAMPO FALTANTE EN API:")
    print("   • Agregar parámetro 'sobrerrepresentacion' al endpoint /procesar/diputados")
    print("   • Tipo: float (0.04 = 4%, 0.08 = 8%)")
    
    print("\n2. VERIFICACIÓN EN FRONTEND:")
    print("   • Comprobar el campo 'porcentaje_escanos' vs 'porcentaje_votos' en resultados")
    print("   • Calcular: sobrerrepresentacion = porcentaje_escanos - porcentaje_votos")
    print("   • Validar que ningún partido supere el límite establecido")
    
    print("\n3. IMPLEMENTACIÓN SUGERIDA:")
    print("   • Slider en UI: 'Límite de sobrerrepresentación (%)'")
    print("   • Rango: 0% a 15% (típico 4%-8%)")
    print("   • Enviar como decimal: 8% → 0.08")
    
    print("\n4. VALIDACIÓN VISUAL:")
    print("   • Mostrar en tabla: 'Sobrerrepresentación (%)'")
    print("   • Color rojo si supera el límite")
    print("   • Verde si está dentro del límite")
    
    print("\n5. CÓDIGO DE VERIFICACIÓN SUGERIDO:")
    print("""
    // En el frontend (JavaScript)
    const verificarSobrerrepresentacion = (resultados, limite) => {
        return resultados.map(partido => ({
            ...partido,
            sobrerrepresentacion: partido.porcentaje_escanos - partido.porcentaje_votos,
            dentroDeLimite: (partido.porcentaje_escanos - partido.porcentaje_votos) <= limite
        }));
    };
    
    // Ejemplo de uso
    const limite = 8; // 8%
    const resultadosConValidacion = verificarSobrerrepresentacion(resultados, limite);
    """)

def test_estructura_respuesta_api():
    """
    Verificar qué campos están disponibles en la respuesta actual
    """
    print("\n🔬 ANÁLISIS DE ESTRUCTURA DE RESPUESTA")
    print("=" * 50)
    
    base_url = "http://localhost:8001"
    
    payload = {
        "anio": 2018,
        "plan": "vigente"
    }
    
    try:
        response = requests.post(f"{base_url}/procesar/diputados", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            print("📋 CAMPOS PRINCIPALES:")
            for key in data.keys():
                print(f"   • {key}: {type(data[key]).__name__}")
            
            if "resultados" in data and len(data["resultados"]) > 0:
                print("\n📋 CAMPOS POR PARTIDO:")
                primer_partido = data["resultados"][0]
                for key, value in primer_partido.items():
                    print(f"   • {key}: {type(value).__name__} = {value}")
                    
            return data
        else:
            print(f"❌ Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    test_sobrerrepresentacion_frontend()
    data = test_estructura_respuesta_api()
