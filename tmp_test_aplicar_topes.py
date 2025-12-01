"""
Test para verificar que aplicar_topes=False realmente desactiva los topes
"""
from engine.procesar_diputados_v2 import procesar_diputados_v2

print("="*60)
print("TEST: Verificar que aplicar_topes funciona")
print("="*60)

# Test con topes
print("\n1. CON TOPES (aplicar_topes=True):")
resultado_con = procesar_diputados_v2(
    path_parquet='data/computos_diputados_2024.parquet',
    anio=2024,
    max_seats=500,
    mr_seats=250,
    rp_seats=250,
    usar_coaliciones=True,
    aplicar_topes=True
)

morena_con = resultado_con['tot'].get('MORENA', 0)
print(f"   MORENA: {morena_con} escaños")

# Test sin topes
print("\n2. SIN TOPES (aplicar_topes=False):")
resultado_sin = procesar_diputados_v2(
    path_parquet='data/computos_diputados_2024.parquet',
    anio=2024,
    max_seats=500,
    mr_seats=250,
    rp_seats=250,
    usar_coaliciones=True,
    aplicar_topes=False
)

morena_sin = resultado_sin['tot'].get('MORENA', 0)
print(f"   MORENA: {morena_sin} escaños")

print("\n" + "="*60)
print("COMPARACIÓN:")
print(f"   CON topes:  {morena_con} escaños")
print(f"   SIN topes:  {morena_sin} escaños")
print(f"   Diferencia: {morena_sin - morena_con:+d} escaños")
print("="*60)

if morena_con == morena_sin:
    print("\n❌ ERROR: Los resultados son IDÉNTICOS!")
    print("   El parámetro aplicar_topes NO está funcionando")
else:
    print(f"\n✅ OK: Los resultados son DIFERENTES")
    print(f"   SIN topes tiene {morena_sin - morena_con:+d} escaños más")
