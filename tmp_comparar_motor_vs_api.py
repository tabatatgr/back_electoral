"""
Comparar exactamente lo que devuelve el motor con print_debug
cuando lo llamo directamente vs cuando la API lo llama
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.procesar_diputados_v2 import procesar_diputados_v2
import requests

print("\n" + "="*80)
print("COMPARACIÓN MOTOR DIRECTO vs API")
print("="*80)

# 1. MOTOR DIRECTO
print("\n1️⃣  MOTOR DIRECTO (400 escaños, SIN coaliciones, SIN topes)")
print("-"*80)

resultado_motor = procesar_diputados_v2(
    path_parquet="data/computos_diputados_2024.parquet",
    anio=2024,
    path_siglado="data/siglado-diputados-2024.csv",
    max_seats=400,
    sistema="mixto",
    mr_seats=200,
    rp_seats=200,
    pm_seats=0,
    umbral=0.03,
    max_seats_per_party=None,
    sobrerrepresentacion=None,
    aplicar_topes=False,
    quota_method="hare",
    divisor_method=None,
    usar_coaliciones=False,
    votos_redistribuidos=None,
    seed=42,
    print_debug=False
)

morena_motor_mr = resultado_motor['mr'].get('MORENA', 0)
morena_motor_rp = resultado_motor['rp'].get('MORENA', 0)
morena_motor_total = resultado_motor['tot'].get('MORENA', 0)

print(f"MORENA Motor: MR={morena_motor_mr}, RP={morena_motor_rp}, TOTAL={morena_motor_total}")
print(f"Total RP Motor: {sum(resultado_motor['rp'].values())}")

# 2. API
print("\n2️⃣  API (400 escaños, SIN coaliciones, SIN topes)")
print("-"*80)

response_api = requests.post(
    "http://127.0.0.1:8000/procesar/diputados?anio=2024",
    json={
        "plan": "personalizado",
        "escanos_totales": 400,
        "sistema": "mixto",
        "mr_seats": 200,
        "rp_seats": 200,
        "aplicar_topes": False,
        "usar_coaliciones": False
    },
    timeout=30
)

if response_api.status_code == 200:
    data_api = response_api.json()
    resultados_api = data_api.get('resultados', [])
    morena_api = [r for r in resultados_api if r['partido'] == 'MORENA'][0]
    
    morena_api_mr = morena_api['mr']
    morena_api_rp = morena_api['rp']
    morena_api_total = morena_api['total']
    
    total_rp_api = sum(r['rp'] for r in resultados_api)
    
    print(f"MORENA API: MR={morena_api_mr}, RP={morena_api_rp}, TOTAL={morena_api_total}")
    print(f"Total RP API: {total_rp_api}")
    
    # COMPARACIÓN
    print("\n" + "="*80)
    print("COMPARACIÓN:")
    print("="*80)
    
    print(f"\n                MR      RP     TOTAL")
    print(f"Motor Directo: {morena_motor_mr:3}     {morena_motor_rp:3}     {morena_motor_total:3}")
    print(f"API:           {morena_api_mr:3}     {morena_api_rp:3}     {morena_api_total:3}")
    print(f"Diferencia:    {morena_api_mr - morena_motor_mr:+3}     {morena_api_rp - morena_motor_rp:+3}     {morena_api_total - morena_motor_total:+3}")
    
    if morena_api_rp == morena_motor_rp:
        print("\n✅ RP COINCIDE - No hay discrepancia")
    else:
        diff_rp = morena_api_rp - morena_motor_rp
        print(f"\n❌ DISCREPANCIA RP: API tiene {diff_rp:+d} escaño(s) de más")
        print("\n🔍 POSIBLES CAUSAS:")
        print("   1. La API está pasando parámetros diferentes al motor")
        print("   2. Hay un ajuste post-procesamiento en la API")
        print("   3. La API está usando un archivo siglado diferente")
        print("   4. Hay un redondeo o ajuste en transformar_resultado_a_formato_frontend")
        
        # Verificar si los totales coinciden
        total_motor = sum(resultado_motor['tot'].values())
        total_api = sum(r['total'] for r in resultados_api)
        print(f"\n   Total escaños Motor: {total_motor}")
        print(f"   Total escaños API: {total_api}")
        
        if total_api != total_motor:
            print(f"   ⚠️  El total de escaños también difiere ({total_api} vs {total_motor})")
        
else:
    print(f"❌ Error API: {response_api.status_code}")
