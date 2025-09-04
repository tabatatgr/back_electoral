import requests
import json

# Test del endpoint de partidos
base_url = "https://back-electoral.onrender.com"  # o tu URL local

def test_partidos_endpoint():
    print("🧪 Probando endpoint /partidos/por-anio")
    
    # Test 1: Diputados 2024
    try:
        url = f"{base_url}/partidos/por-anio?anio=2024&camara=diputados"
        print(f"📡 GET {url}")
        
        response = requests.get(url, timeout=30)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Éxito! {len(data.get('partidos', []))} partidos encontrados")
            
            # Mostrar primeros 3 partidos
            for i, partido in enumerate(data.get('partidos', [])[:3]):
                print(f"  {i+1}. {partido['partido']}: {partido['porcentaje_vigente']}%")
                
        else:
            print(f"❌ Error {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

    # Test 2: Parámetros incorrectos
    try:
        print("\n🧪 Probando parámetros incorrectos...")
        url = f"{base_url}/partidos/por-anio?anio=2025&camara=diputados"  # Año que no existe
        response = requests.get(url, timeout=10)
        print(f"📊 Status para año inexistente: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ Error 400 esperado para año inexistente")
        else:
            print(f"⚠️  Status inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_partidos_endpoint()
