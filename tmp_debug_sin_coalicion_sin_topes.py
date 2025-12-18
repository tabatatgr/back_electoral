"""
Script para probar la API sin coaliciones y sin topes
Debe devolver MORENA ~256 según CSV SIN_TOPES
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
    "usar_coaliciones": False,     # <- SIN coaliciones
    "aplicar_topes": False         # <- SIN topes
    # NO enviar 'sobrerrepresentacion'
}

print("="*80)
print("PRUEBA: SIN COALICIONES + SIN TOPES")
print("="*80)
print(f"URL: {url}")
print(f"Parámetros:\n{json.dumps(params, indent=2)}")
print()

try:
    r = requests.post(url, params=params, timeout=60)
    
    print(f"Status: {r.status_code}")
    
    if r.ok:
        data = r.json()
        
        print("\n" + "="*80)
        print("RESULTADO")
        print("="*80)
        
        # Extraer totales
        totales = {}
        for partido in data['resultados']:
            p = partido['partido']
            totales[p] = {
                'mr': partido['mr'],
                'rp': partido['rp'],
                'total': partido['total']
            }
        
        print("\n📊 ESCAÑOS POR PARTIDO:")
        for p in ['MORENA', 'PT', 'PVEM', 'PAN', 'PRI', 'PRD', 'MC']:
            if p in totales:
                info = totales[p]
                print(f"  {p:10s}: MR={info['mr']:3d}  RP={info['rp']:3d}  TOTAL={info['total']:3d}")
        
        # Comparar con CSV esperado
        morena_total = totales.get('MORENA', {}).get('total', 0)
        morena_mr = totales.get('MORENA', {}).get('mr', 0)
        morena_rp = totales.get('MORENA', {}).get('rp', 0)
        
        print("\n" + "="*80)
        print("COMPARACIÓN CON CSV SIN_TOPES")
        print("="*80)
        print(f"CSV esperado (2024, 400, 50MR_50RP, SIN):  MORENA MR=163  RP=93  TOTAL=256")
        print(f"API respuesta:                              MORENA MR={morena_mr:3d}  RP={morena_rp:3d}  TOTAL={morena_total:3d}")
        
        if morena_total == 256 and morena_mr == 163 and morena_rp == 93:
            print("\n✅ COINCIDE EXACTAMENTE CON CSV")
        else:
            print(f"\n❌ DISCREPANCIA:")
            print(f"   MR: {morena_mr} vs 163 (diff: {morena_mr - 163:+d})")
            print(f"   RP: {morena_rp} vs 93 (diff: {morena_rp - 93:+d})")
            print(f"   TOTAL: {morena_total} vs 256 (diff: {morena_total - 256:+d})")
        
        # Guardar respuesta completa
        with open('tmp_debug_sin_coal_sin_topes.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("\n💾 Respuesta completa guardada en: tmp_debug_sin_coal_sin_topes.json")
        
    else:
        print(f"\n❌ Error HTTP {r.status_code}")
        print(r.text)
        
except requests.exceptions.ConnectionError:
    print("\n❌ No se pudo conectar al servidor")
    print("   ¿Está corriendo el servidor en http://127.0.0.1:8000 ?")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
