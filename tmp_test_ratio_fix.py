"""
Verificar que ratio_promedio ahora SÍ varía con la desproporcionalidad
"""
import requests
import json

print("=" * 80)
print("🧪 PRUEBA: Ratio promedio SIMPLE (ya no siempre es 1.0)")
print("=" * 80)

# Prueba 1: Sistema muy desproporcional (sin coaliciones, sin topes)
print("\n1️⃣  Sistema DESPROPORCIONAL (sin coaliciones, sin topes)")
print("-" * 80)

payload1 = {
    "anio": "2024",
    "plan": "personalizado",
    "escanos_totales": 400,
    "sistema": "mixto",
    "mr_seats": 200,
    "rp_seats": 200,
    "aplicar_topes": False,
    "usar_coaliciones": False,
    "umbral": 0.0
}

try:
    r1 = requests.post("http://localhost:8000/procesar/diputados", json=payload1, timeout=10)
    data1 = r1.json()
    
    print(f"\n📊 Partidos con escaños:")
    for p in data1["resultados"]:
        if p["escanos_totales"] > 0:
            ratio = p["porcentaje_escanos"] / p["porcentaje_votos"] if p["porcentaje_votos"] > 0 else 0
            print(f"  {p['partido']:<10} Votos: {p['porcentaje_votos']:5.2f}%  Escaños: {p['porcentaje_escanos']:5.2f}%  Ratio: {ratio:.4f}")
    
    metricas1 = data1["metricas_proporcionalidad"]
    print(f"\n✅ Métricas:")
    print(f"   ratio_promedio: {metricas1['ratio_promedio']}")
    print(f"   desviacion_estandar: {metricas1['desviacion_estandar']}")
    print(f"   coeficiente_variacion: {metricas1['coeficiente_variacion']}")
    print(f"   gallagher_index: {data1.get('gallagher_index', 'N/A')}")
    
except Exception as e:
    print(f"❌ Error: {e}")

# Prueba 2: Sistema más proporcional (con coaliciones, con topes)
print("\n\n2️⃣  Sistema MÁS PROPORCIONAL (con coaliciones, con topes)")
print("-" * 80)

payload2 = {
    "anio": "2024",
    "plan": "personalizado",
    "escanos_totales": 400,
    "sistema": "mixto",
    "mr_seats": 200,
    "rp_seats": 200,
    "aplicar_topes": True,
    "usar_coaliciones": True,
    "umbral": 0.03,
    "sobrerrepresentacion": True
}

try:
    r2 = requests.post("http://localhost:8000/procesar/diputados", json=payload2, timeout=10)
    data2 = r2.json()
    
    print(f"\n📊 Partidos con escaños:")
    for p in data2["resultados"]:
        if p["escanos_totales"] > 0:
            ratio = p["porcentaje_escanos"] / p["porcentaje_votos"] if p["porcentaje_votos"] > 0 else 0
            print(f"  {p['partido']:<10} Votos: {p['porcentaje_votos']:5.2f}%  Escaños: {p['porcentaje_escanos']:5.2f}%  Ratio: {ratio:.4f}")
    
    metricas2 = data2["metricas_proporcionalidad"]
    print(f"\n✅ Métricas:")
    print(f"   ratio_promedio: {metricas2['ratio_promedio']}")
    print(f"   desviacion_estandar: {metricas2['desviacion_estandar']}")
    print(f"   coeficiente_variacion: {metricas2['coeficiente_variacion']}")
    print(f"   gallagher_index: {data2.get('gallagher_index', 'N/A')}")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 80)
print("📊 COMPARACIÓN:")
print("=" * 80)
try:
    print(f"Sistema DESPROPORCIONAL:")
    print(f"  ratio_promedio: {metricas1['ratio_promedio']} (esperado: != 1.0)")
    print(f"  Gallagher: {data1.get('gallagher_index', 'N/A')}")
    print(f"\nSistema MÁS PROPORCIONAL:")
    print(f"  ratio_promedio: {metricas2['ratio_promedio']} (esperado: más cercano a 1.0)")
    print(f"  Gallagher: {data2.get('gallagher_index', 'N/A')}")
    
    if metricas1['ratio_promedio'] != 1.0:
        print(f"\n✅ ¡ÉXITO! ratio_promedio YA NO es siempre 1.0")
        print(f"   Ahora refleja correctamente la (des)proporcionalidad del sistema")
    else:
        print(f"\n⚠️  Hmm, ratio_promedio sigue siendo 1.0")
        print(f"   Verifica que el servidor se haya reiniciado con los cambios")
except:
    pass
