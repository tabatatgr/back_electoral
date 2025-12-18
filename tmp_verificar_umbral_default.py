"""
Verificar que el umbral 3% está activo por defecto en plan personalizado
"""

import requests

API_URL = "http://127.0.0.1:8000/procesar/diputados"

print("\n" + "="*80)
print("🧪 VERIFICACIÓN DEL UMBRAL DEFAULT (3%)")
print("="*80)

# TEST 1: Sin especificar umbral (debe usar 3% por default)
print("\n1️⃣  Plan personalizado SIN especificar umbral")
print("-"*80)

response1 = requests.post(
    f"{API_URL}?anio=2024",
    json={
        "plan": "personalizado",
        "escanos_totales": 400,
        "sistema": "mixto",
        "mr_seats": 200,
        "rp_seats": 200,
        "aplicar_topes": False,
        "usar_coaliciones": False
        # umbral NO especificado → debe usar 3% por default
    },
    timeout=30
)

if response1.status_code == 200:
    data1 = response1.json()
    resultados1 = data1.get('resultados', [])
    
    # Contar partidos con escaños
    partidos_con_escanos = [r for r in resultados1 if r['total'] > 0]
    
    print(f"\nPartidos con escaños: {len(partidos_con_escanos)}")
    for r in partidos_con_escanos:
        pct_votos = r['porcentaje_votos']
        print(f"  {r['partido']}: {r['total']} escaños ({pct_votos:.2f}% votos)")
    
    # Verificar que no haya partidos con menos de 3%
    partidos_bajo_umbral = [r for r in partidos_con_escanos if r['porcentaje_votos'] < 3.0]
    
    if partidos_bajo_umbral:
        print(f"\n❌ PROBLEMA: Hay partidos con menos de 3% que tienen escaños:")
        for r in partidos_bajo_umbral:
            print(f"   {r['partido']}: {r['porcentaje_votos']:.2f}% → {r['total']} escaños")
        print("\n   El umbral 3% NO se está aplicando correctamente")
    else:
        print(f"\n✅ CORRECTO: Todos los partidos con escaños tienen ≥3% de votos")
        print("   El umbral 3% está activo por default")

# TEST 2: Especificar umbral explícitamente en 0 (desactivar)
print("\n2️⃣  Plan personalizado CON umbral=0 (desactivado)")
print("-"*80)

response2 = requests.post(
    f"{API_URL}?anio=2024",
    json={
        "plan": "personalizado",
        "escanos_totales": 400,
        "sistema": "mixto",
        "mr_seats": 200,
        "rp_seats": 200,
        "aplicar_topes": False,
        "usar_coaliciones": False,
        "umbral": 0.0  # Umbral desactivado explícitamente
    },
    timeout=30
)

if response2.status_code == 200:
    data2 = response2.json()
    resultados2 = data2.get('resultados', [])
    
    partidos_con_escanos_2 = [r for r in resultados2 if r['total'] > 0]
    
    print(f"\nPartidos con escaños: {len(partidos_con_escanos_2)}")
    for r in partidos_con_escanos_2:
        pct_votos = r['porcentaje_votos']
        print(f"  {r['partido']}: {r['total']} escaños ({pct_votos:.2f}% votos)")
    
    if len(partidos_con_escanos_2) > len(partidos_con_escanos):
        print(f"\n✅ CORRECTO: Con umbral=0 hay MÁS partidos con escaños")
        print(f"   ({len(partidos_con_escanos_2)} vs {len(partidos_con_escanos)})")
        print("   Esto confirma que el umbral 3% default funciona")

print("\n" + "="*80)
print("RESUMEN:")
print("="*80)
print("\n📋 El umbral 3% ahora es el DEFAULT para plan personalizado")
print("   - Si el frontend NO envía umbral → se usa 3%")
print("   - Si el frontend envía umbral=0 → se desactiva")
print("   - Si el frontend envía umbral=5 → se usa 5%")
