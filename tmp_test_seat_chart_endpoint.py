"""
Test para verificar qué devuelve el endpoint /seat-chart/diputados/2024
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_seat_chart_endpoint():
    print("=" * 80)
    print("TEST: Endpoint /seat-chart/diputados/2024")
    print("=" * 80)
    print()
    
    # Parámetros similares a los que usa el frontend
    params = {
        "plan": "vigente"
    }
    
    print(f"GET {BASE_URL}/seat-chart/diputados/2024")
    print(f"Params: {json.dumps(params, indent=2)}")
    print()
    
    try:
        response = requests.get(f"{BASE_URL}/seat-chart/diputados/2024", params=params, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print()
        
        if response.status_code != 200:
            print(f"❌ ERROR: {response.text}")
            return False
        
        data = response.json()
        
        print("📦 Estructura de respuesta:")
        print(json.dumps(list(data.keys()), indent=2))
        print()
        
        # Verificar que existe 'seats'
        if "seats" not in data:
            print("❌ ERROR: No hay 'seats' en la respuesta")
            return False
        
        seats = data["seats"]
        
        print(f"✓ {len(seats)} partidos en 'seats'")
        print()
        
        # Mostrar el primer partido completo
        if len(seats) > 0:
            primer_partido = seats[0]
            print("📦 Primer partido completo:")
            print(json.dumps(primer_partido, indent=2))
            print()
            
            # Verificar campos
            campos_esperados = ["party", "seats", "color", "percent", "votes", "mr", "pm", "rp"]
            campos_presentes = list(primer_partido.keys())
            campos_faltantes = [c for c in campos_esperados if c not in campos_presentes]
            
            print("Campos esperados:", campos_esperados)
            print("Campos presentes:", campos_presentes)
            
            if campos_faltantes:
                print(f"❌ Campos faltantes: {campos_faltantes}")
                return False
            else:
                print("✅ Todos los campos presentes")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se pudo conectar al backend")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    resultado = test_seat_chart_endpoint()
    print()
    print("=" * 80)
    if resultado:
        print("✅ TEST EXITOSO")
    else:
        print("❌ TEST FALLIDO")
    print("=" * 80)
