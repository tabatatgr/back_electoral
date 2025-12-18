"""
Script para probar la API CON coaliciones y SIN topes
Debe devolver MORENA ~248 según CSV SIN_TOPES
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
    "usar_coaliciones": True,      # <- CON coaliciones
    "aplicar_topes": False         # <- SIN topes
}

print("="*80)
print("PRUEBA: CON COALICIONES + SIN TOPES")
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
        
        # Calcular coalición
        coal_total = morena_total + totales.get('PT', {}).get('total', 0) + totales.get('PVEM', {}).get('total', 0)
        
        print("\n" + "="*80)
        print("COMPARACIÓN CON CSV SIN_TOPES")
        print("="*80)
        print(f"CSV esperado (2024, 400, 50MR_50RP, CON):  MORENA MR=161  RP=87  TOTAL=248  COALICIÓN=282")
        print(f"API respuesta:                              MORENA MR={morena_mr:3d}  RP={morena_rp:3d}  TOTAL={morena_total:3d}  COALICIÓN={coal_total:3d}")
        
        if morena_total == 248 and morena_mr == 161 and morena_rp == 87:
            print("\n✅ COINCIDE EXACTAMENTE CON CSV")
        else:
            print(f"\n❌ DISCREPANCIA:")
            print(f"   MR: {morena_mr} vs 161 (diff: {morena_mr - 161:+d})")
            print(f"   RP: {morena_rp} vs 87 (diff: {morena_rp - 87:+d})")
            print(f"   TOTAL: {morena_total} vs 248 (diff: {morena_total - 248:+d})")
            print(f"   COALICIÓN: {coal_total} vs 282 (diff: {coal_total - 282:+d})")
        
        # Guardar respuesta completa
        with open('tmp_debug_con_coal_sin_topes.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("\n💾 Respuesta completa guardada en: tmp_debug_con_coal_sin_topes.json")
        
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
