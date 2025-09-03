"""
Test simple para verificar que la sobrerrepresentación funciona
"""

import requests
import json

# Test directo de API
def test_api_sobrerrepresentacion_simple():
    print("🔍 TEST: API con sobrerrepresentación")
    print("=" * 50)
    
    base_url = "http://localhost:8001"
    
    # Test sin sobrerrepresentación
    payload_sin = {
        "anio": 2024,
        "plan": "personalizado",
        "sistema": "mixto",
        "mr_seats": 300,
        "rp_seats": 200,
        "umbral": 3.0
    }
    
    print("📤 Request SIN sobrerrepresentación...")
    try:
        response_sin = requests.post(f"{base_url}/procesar/diputados", json=payload_sin, timeout=30)
        
        if response_sin.status_code == 200:
            data_sin = response_sin.json()
            print("✅ Request SIN sobrerrepresentación exitoso")
            
            morena_sin = next((r['total'] for r in data_sin['resultados'] if r['partido'] == 'MORENA'), 0)
            pan_sin = next((r['total'] for r in data_sin['resultados'] if r['partido'] == 'PAN'), 0)
            pri_sin = next((r['total'] for r in data_sin['resultados'] if r['partido'] == 'PRI'), 0)
            
            print(f"   MORENA: {morena_sin}, PAN: {pan_sin}, PRI: {pri_sin}")
        else:
            print(f"❌ Error: {response_sin.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en request SIN sobrerrepresentación: {e}")
        return False
    
    # Test con sobrerrepresentación
    payload_con = {
        "anio": 2024,
        "plan": "personalizado",
        "sistema": "mixto",
        "mr_seats": 300,
        "rp_seats": 200,
        "umbral": 3.0,
        "sobrerrepresentacion": 8.0  # AQUÍ ESTÁ EL PARÁMETRO
    }
    
    print("\n📤 Request CON sobrerrepresentación 8%...")
    try:
        response_con = requests.post(f"{base_url}/procesar/diputados", json=payload_con, timeout=30)
        
        if response_con.status_code == 200:
            data_con = response_con.json()
            print("✅ Request CON sobrerrepresentación exitoso")
            
            morena_con = next((r['total'] for r in data_con['resultados'] if r['partido'] == 'MORENA'), 0)
            pan_con = next((r['total'] for r in data_con['resultados'] if r['partido'] == 'PAN'), 0)
            pri_con = next((r['total'] for r in data_con['resultados'] if r['partido'] == 'PRI'), 0)
            
            print(f"   MORENA: {morena_con}, PAN: {pan_con}, PRI: {pri_con}")
            
            # Comparar
            print(f"\n📊 COMPARACIÓN:")
            print(f"   MORENA: {morena_sin} → {morena_con} ({morena_con - morena_sin:+d})")
            print(f"   PAN: {pan_sin} → {pan_con} ({pan_con - pan_sin:+d})")
            print(f"   PRI: {pri_sin} → {pri_con} ({pri_con - pri_sin:+d})")
            
            if morena_con != morena_sin or pan_con != pan_sin or pri_con != pri_sin:
                print("   ✅ LA SOBRERREPRESENTACIÓN SÍ FUNCIONA EN LA API")
                return True
            else:
                print("   ❌ LA SOBRERREPRESENTACIÓN NO TIENE EFECTO EN LA API")
                return False
                
        else:
            print(f"❌ Error: {response_con.status_code}")
            print(response_con.text)
            return False
            
    except Exception as e:
        print(f"❌ Error en request CON sobrerrepresentación: {e}")
        return False

if __name__ == "__main__":
    # Verificar que el servidor esté funcionando
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            print("🟢 Servidor funcionando en puerto 8001")
            resultado = test_api_sobrerrepresentacion_simple()
            
            if resultado:
                print("\n🎉 SOBRERREPRESENTACIÓN IMPLEMENTADA EXITOSAMENTE")
            else:
                print("\n⚠️  VERIFICAR IMPLEMENTACIÓN")
        else:
            print("❌ Servidor no responde correctamente")
    except:
        print("❌ No se puede conectar al servidor en puerto 8001")
        print("💡 Ejecutar: python main.py")
