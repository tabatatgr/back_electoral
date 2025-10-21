"""
Script de prueba para verificar que PM (primera minoría) funciona correctamente
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_pm_simple():
    """Test 1: Sistema MR con 100 PM de 300 total"""
    print("\n" + "="*80)
    print("TEST 1: Sistema MR puro con PM")
    print("="*80)
    
    payload = {
        "plan": "personalizado",
        "anio": 2024,
        "sistema": "mr",
        "escanos_totales": 300,
        "pm_seats": 100,  # 100 escaños de primera minoría
        "umbral": 0.03
    }
    
    print(f"\n📤 Request:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(f"{BASE_URL}/procesar/diputados", json=payload, timeout=60)
        print(f"\n📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Verificar que el resultado tiene los campos esperados
            if "resultados" in data and len(data["resultados"]) > 0:
                print(f"\n✅ Respuesta exitosa con {len(data['resultados'])} partidos")
                print(f"\n📊 Resultados por partido:")
                print(f"{'Partido':<15} {'MR':<8} {'PM':<8} {'RP':<8} {'Total':<8}")
                print("-" * 55)
                
                total_mr = 0
                total_pm = 0
                total_rp = 0
                total_escanos = 0
                
                for resultado in sorted(data["resultados"], key=lambda x: x["total"], reverse=True):
                    partido = resultado["partido"]
                    mr = resultado.get("mr", 0)
                    pm = resultado.get("pm", 0)
                    rp = resultado.get("rp", 0)
                    total = resultado["total"]
                    
                    if total > 0:  # Solo mostrar partidos con escaños
                        print(f"{partido:<15} {mr:<8} {pm:<8} {rp:<8} {total:<8}")
                        total_mr += mr
                        total_pm += pm
                        total_rp += rp
                        total_escanos += total
                
                print("-" * 55)
                print(f"{'TOTAL':<15} {total_mr:<8} {total_pm:<8} {total_rp:<8} {total_escanos:<8}")
                
                # Verificaciones
                print(f"\n🔍 Verificaciones:")
                print(f"   • Total PM solicitado: 100")
                print(f"   • Total PM asignado: {total_pm}")
                print(f"   • Total MR + PM + RP: {total_escanos}")
                print(f"   • Total esperado: 300")
                
                if total_pm == 100:
                    print(f"   ✅ PM asignado correctamente!")
                else:
                    print(f"   ⚠️  PM no coincide (esperado: 100, obtenido: {total_pm})")
                
                if total_escanos == 300:
                    print(f"   ✅ Total de escaños correcto!")
                else:
                    print(f"   ⚠️  Total no coincide (esperado: 300, obtenido: {total_escanos})")
                
                # Verificar que PM > 0 para al menos un partido
                partidos_con_pm = [r for r in data["resultados"] if r.get("pm", 0) > 0]
                print(f"   • Partidos con PM: {len(partidos_con_pm)}")
                
                if len(partidos_con_pm) > 0:
                    print(f"   ✅ Al menos un partido tiene escaños PM!")
                else:
                    print(f"   ❌ Ningún partido tiene PM - algo falló")
                
            else:
                print("❌ Respuesta sin resultados")
                print(json.dumps(data, indent=2))
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"❌ Error en la petición: {e}")
        import traceback
        traceback.print_exc()


def test_pm_mixto():
    """Test 2: Sistema mixto con PM"""
    print("\n" + "="*80)
    print("TEST 2: Sistema mixto con PM (200 MR + 100 RP + 50 PM)")
    print("="*80)
    
    payload = {
        "plan": "personalizado",
        "anio": 2024,
        "sistema": "mixto",
        "escanos_totales": 300,
        "mr_seats": 200,
        "rp_seats": 100,
        "pm_seats": 50,  # 50 PM que salen de los 200 MR → 150 MR efectivo
        "umbral": 0.03
    }
    
    print(f"\n📤 Request:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(f"{BASE_URL}/procesar/diputados", json=payload, timeout=60)
        print(f"\n📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if "resultados" in data and len(data["resultados"]) > 0:
                print(f"\n✅ Respuesta exitosa")
                print(f"\n📊 Resumen:")
                
                total_mr = sum(r.get("mr", 0) for r in data["resultados"])
                total_pm = sum(r.get("pm", 0) for r in data["resultados"])
                total_rp = sum(r.get("rp", 0) for r in data["resultados"])
                total = sum(r["total"] for r in data["resultados"])
                
                print(f"   • MR efectivo: {total_mr} (esperado: ~150)")
                print(f"   • PM: {total_pm} (esperado: 50)")
                print(f"   • RP: {total_rp} (esperado: 100)")
                print(f"   • Total: {total} (esperado: 300)")
                
                if total_pm == 50:
                    print(f"   ✅ PM correcto!")
                if abs(total_rp - 100) < 5:  # Margen de 5 por ajustes
                    print(f"   ✅ RP aproximadamente correcto!")
                if total == 300:
                    print(f"   ✅ Total correcto!")
            else:
                print("❌ Respuesta sin resultados")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"❌ Error: {e}")


def test_pm_validacion():
    """Test 3: Validación - PM mayor que MR debe fallar"""
    print("\n" + "="*80)
    print("TEST 3: Validación - PM > MR debe dar error")
    print("="*80)
    
    payload = {
        "plan": "personalizado",
        "anio": 2024,
        "sistema": "mr",
        "escanos_totales": 300,
        "pm_seats": 350,  # ❌ Más que el total - debe fallar
        "umbral": 0.03
    }
    
    print(f"\n📤 Request con PM=350 (mayor que total=300):")
    
    try:
        response = requests.post(f"{BASE_URL}/procesar/diputados", json=payload, timeout=60)
        print(f"\n📥 Response Status: {response.status_code}")
        
        if response.status_code == 400:
            print(f"✅ Error esperado (400) - Validación funcionó!")
            print(f"Mensaje: {response.json().get('detail', 'N/A')}")
        else:
            print(f"⚠️  Respuesta inesperada: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("🚀 Iniciando pruebas de PM (Primera Minoría)")
    print("Asegúrate de que el servidor esté corriendo en http://localhost:8000")
    
    # Ejecutar tests
    test_pm_simple()
    test_pm_mixto()
    test_pm_validacion()
    
    print("\n" + "="*80)
    print("✨ Pruebas completadas")
    print("="*80)
