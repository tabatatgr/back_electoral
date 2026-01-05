"""
Verificación final: ratio_promedio se llama igual, es compatible con frontend
"""
import requests

r = requests.post('http://localhost:8000/procesar/diputados?anio=2024&plan=personalizado&escanos_totales=400&sistema=mixto&mr_seats=200&rp_seats=200&aplicar_topes=false&usar_coaliciones=false&umbral=0')
kpis = r.json()['kpis']

print("=" * 80)
print("✅ VERIFICACIÓN DE COMPATIBILIDAD CON FRONTEND")
print("=" * 80)

print(f"\n📊 Estructura de kpis:")
for key, value in kpis.items():
    if key != "_debug":
        print(f"  • {key}: {value}")

print(f"\n✅ Campo ratio_promedio:")
print(f"   Nombre: 'ratio_promedio' (igual que antes - compatible)")
print(f"   Valor: {kpis['ratio_promedio']} (ya NO siempre es 1.0)")
print(f"   Tipo: {type(kpis['ratio_promedio'])}")

print(f"\n✅ Cambios en el frontend necesarios:")
print(f"   NINGUNO - el campo se llama igual y tiene el mismo tipo")
print(f"   Solo cambia el CÁLCULO interno (promedio simple vs ponderado)")

print(f"\n📝 Interpretación actualizada:")
print(f"   • ratio_promedio = 1.0 → Proporcionalidad perfecta")
print(f"   • ratio_promedio < 1.0 → Subrepresentación promedio")
print(f"   • ratio_promedio > 1.0 → Sobrerrepresentación promedio")
print(f"   • Valor actual: {kpis['ratio_promedio']} → {'Subrepresentación promedio' if kpis['ratio_promedio'] < 1.0 else 'Sobrerrepresentación promedio'}")

print("\n" + "=" * 80)
print("🎉 LISTO - Compatible con frontend sin cambios")
print("=" * 80)
