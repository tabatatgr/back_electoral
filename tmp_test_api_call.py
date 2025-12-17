"""
Script para hacer una petición al endpoint y ver exactamente qué devuelve
"""
import requests
import json

url = "http://127.0.0.1:8000/procesar/diputados"

params = {
    "anio": 2024,
    "plan": "personalizado",
    "sistema": "mixto",
    "max_seats": 400,
    "mr_seats": 200,
    "rp_seats": 200,
    "usar_coaliciones": True,
    "aplicar_topes": True,
    "sobrerrepresentacion": 8.0  # ← CLÁUSULA DEL 8%
}

print("="*80)
print("PETICIÓN AL ENDPOINT")
print("="*80)
print(f"URL: {url}")
print(f"Parámetros: {json.dumps(params, indent=2)}")

try:
    # Usar query params, no JSON body
    response = requests.post(url, params=params, timeout=30)
    
    print(f"\nEstado: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        print("\n" + "="*80)
        print("RESPUESTA (RESUMEN)")
        print("="*80)
        
        if 'tot' in data:
            print("\n📊 ESCAÑOS TOTALES:")
            for p, v in sorted(data['tot'].items(), key=lambda x: -x[1]):
                print(f"  {p:10s}: {v:3d}")
            
            morena = data['tot'].get('MORENA', 0)
            coal = morena + data['tot'].get('PT', 0) + data['tot'].get('PVEM', 0)
            print(f"\n  MORENA: {morena} ({morena/400*100:.1f}%)")
            print(f"  COALICIÓN: {coal} ({coal/400*100:.1f}%)")
        
        # Guardar respuesta completa
        with open('tmp_respuesta_endpoint.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("\n✅ Respuesta completa guardada en: tmp_respuesta_endpoint.json")
        
    else:
        print(f"\n❌ Error: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ No se pudo conectar. ¿Está el servidor corriendo?")
    print("   Ejecuta: python -m uvicorn main:app --port 8000")
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "="*80)
