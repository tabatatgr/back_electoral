"""
Test para verificar que seat_chart incluye desglose MR/PM/RP
"""
import requests
import json

# URL del backend
BASE_URL = "http://localhost:8000"

def test_seat_chart_desglose():
    """
    Prueba que el endpoint /simulate devuelve seat_chart con desglose MR/PM/RP
    """
    print("=" * 80)
    print("TEST: Verificar desglose MR/PM/RP en seat_chart")
    print("=" * 80)
    print()
    
    # Datos de prueba - simulación simple
    payload = {
        "anio": 2024,
        "max_seats": 500,
        "mr_seats": 300,
        "rp_seats": 200,
        "umbral": 0.03,
        "sobrerrepresentacion": 8.0,
        "aplicar_topes": True,
        "usar_coaliciones": False,
        "votos_redistribuidos": {
            "MORENA": 24286412,
            "PAN": 10049424,
            "PRI": 6623752,
            "PVEM": 4993902,
            "PT": 3254709,
            "MC": 6497404,
            "PRD": 1449655
        }
    }
    
    print(f"Enviando POST a {BASE_URL}/simulate")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print()
    
    try:
        response = requests.post(f"{BASE_URL}/simulate", json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print()
        
        if response.status_code != 200:
            print(f"❌ ERROR: {response.text}")
            return False
        
        data = response.json()
        
        # Verificar que existe seat_chart
        if "seat_chart" not in data:
            print("❌ ERROR: No hay 'seat_chart' en la respuesta")
            return False
        
        seat_chart = data["seat_chart"]
        
        print(f"✓ seat_chart recibido con {len(seat_chart)} partidos")
        print()
        
        # Verificar estructura de cada partido
        print("Verificando estructura de seat_chart:")
        print("-" * 80)
        print(f"{'Partido':<12} {'Votos %':>10} {'MR':>6} {'PM':>6} {'RP':>6} {'Total':>6} {'Suma':>6}")
        print("-" * 80)
        
        todos_ok = True
        for item in seat_chart:
            partido = item.get("party", "???")
            seats = item.get("seats", 0)
            percent = item.get("percent", 0)
            votes = item.get("votes", 0)
            
            # Campos nuevos
            mr = item.get("mr")
            pm = item.get("pm")
            rp = item.get("rp")
            
            # Verificar que existen los campos
            if mr is None or pm is None or rp is None:
                print(f"❌ {partido:<12} - Faltan campos MR/PM/RP")
                todos_ok = False
                continue
            
            # Verificar suma
            suma = mr + pm + rp
            match = "✓" if suma == seats else "✗"
            
            print(f"{partido:<12} {percent:>9.2f}% {mr:>6} {pm:>6} {rp:>6} {seats:>6} {suma:>6} {match}")
            
            if suma != seats:
                print(f"  ⚠️  WARNING: MR + PM + RP ({suma}) != seats ({seats})")
                todos_ok = False
        
        print("-" * 80)
        print()
        
        if todos_ok:
            print("✅ ÉXITO: Todos los partidos tienen desglose MR/PM/RP correcto")
            print()
            
            # Mostrar ejemplo de un partido
            if len(seat_chart) > 0:
                ejemplo = seat_chart[0]
                print("Ejemplo de estructura (primer partido):")
                print(json.dumps(ejemplo, indent=2, ensure_ascii=False))
        else:
            print("❌ ERROR: Hay inconsistencias en el desglose")
        
        return todos_ok
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se pudo conectar al backend")
        print(f"   Asegúrate de que el servidor esté corriendo en {BASE_URL}")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print()
    print("NOTA: Asegúrate de que el backend esté corriendo en http://localhost:8000")
    print("      Ejecuta: uvicorn main:app --reload")
    print()
    input("Presiona ENTER para continuar...")
    print()
    
    resultado = test_seat_chart_desglose()
    
    print()
    print("=" * 80)
    if resultado:
        print("✅ TEST EXITOSO")
    else:
        print("❌ TEST FALLIDO")
    print("=" * 80)
