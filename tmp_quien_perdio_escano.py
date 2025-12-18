"""
Encontrar qué partido tiene -1 RP en la API vs motor directo
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.procesar_diputados_v2 import procesar_diputados_v2
import requests

# MOTOR DIRECTO
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

# API
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

data_api = response_api.json()
resultados_api = data_api.get('resultados', [])

print("\n" + "="*80)
print("DIFERENCIAS RP POR PARTIDO:")
print("="*80)
print(f"\n{'Partido':<10} {'Motor':<10} {'API':<10} {'Diferencia':<12}")
print("-"*80)

diferencias = {}

for partido in sorted(resultado_motor['tot'].keys()):
    rp_motor = resultado_motor['rp'].get(partido, 0)
    rp_api_data = [r for r in resultados_api if r['partido'] == partido]
    rp_api = rp_api_data[0]['rp'] if rp_api_data else 0
    
    diff = rp_api - rp_motor
    diferencias[partido] = diff
    
    if diff != 0:
        symbol = "🔴" if diff < 0 else "🟢"
        print(f"{partido:<10} {rp_motor:<10} {rp_api:<10} {diff:+3}  {symbol}")
    else:
        print(f"{partido:<10} {rp_motor:<10} {rp_api:<10} {diff:+3}")

print("\n" + "="*80)
print("RESUMEN:")
print("="*80)

partidos_mas = [p for p, d in diferencias.items() if d > 0]
partidos_menos = [p for p, d in diferencias.items() if d < 0]

if partidos_mas:
    print(f"\n🟢 Partidos con MÁS RP en API:")
    for p in partidos_mas:
        print(f"   {p}: {diferencias[p]:+d}")

if partidos_menos:
    print(f"\n🔴 Partidos con MENOS RP en API:")
    for p in partidos_menos:
        print(f"   {p}: {diferencias[p]:+d}")

print(f"\n📊 Suma de diferencias: {sum(diferencias.values())} (debería ser 0)")
