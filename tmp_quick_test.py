import requests

# Test 1: Desproporcional
r1 = requests.post('http://localhost:8000/procesar/diputados?anio=2024&plan=personalizado&escanos_totales=400&sistema=mixto&mr_seats=200&rp_seats=200&aplicar_topes=false&usar_coaliciones=false&umbral=0')
kpis1 = r1.json()['kpis']

print("🔍 Sistema DESPROPORCIONAL (sin coaliciones, sin topes):")
print(f"  ratio_promedio: {kpis1['ratio_promedio']}")
print(f"  desviacion: {kpis1['desviacion_proporcionalidad']}")
print(f"  gallagher: {kpis1['gallagher']}")

# Test 2: Más proporcional
r2 = requests.post('http://localhost:8000/procesar/diputados?anio=2024&plan=personalizado&escanos_totales=400&sistema=mixto&mr_seats=200&rp_seats=200&aplicar_topes=true&usar_coaliciones=true&umbral=0.03')
data2 = r2.json()
if 'kpis' in data2:
    kpis2 = data2['kpis']
else:
    print(f"\nError en Test 2: {data2}")
    kpis2 = kpis1  # fallback

print("\n🔍 Sistema MÁS PROPORCIONAL (con coaliciones, con topes):")
print(f"  ratio_promedio: {kpis2['ratio_promedio']}")
print(f"  desviacion: {kpis2['desviacion_proporcionalidad']}")
print(f"  gallagher: {kpis2['gallagher']}")

print("\n✅ RESULTADO:")
if kpis1['ratio_promedio'] != 1.0:
    print(f"  ¡FUNCIONA! ratio_promedio YA NO es siempre 1.0")
    print(f"  Desproporcional: {kpis1['ratio_promedio']}")
    print(f"  Proporcional: {kpis2['ratio_promedio']}")
else:
    print(f"  ⚠️  Todavía da 1.0")
