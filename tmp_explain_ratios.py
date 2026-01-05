"""
Explicación: Ratio promedio PONDERADO vs SIMPLE
"""

# Ejemplo con datos ficticios
partidos = [
    {"partido": "MORENA", "votos_%": 45.0, "escanos_%": 64.0},  # Sobrerrepresentado
    {"partido": "PAN", "votos_%": 18.0, "escanos_%": 14.5},     # Subrepresentado
    {"partido": "PRI", "votos_%": 12.0, "escanos_%": 7.0},      # Subrepresentado
    {"partido": "MC", "votos_%": 11.0, "escanos_%": 7.5},       # Subrepresentado
    {"partido": "PVEM", "votos_%": 7.0, "escanos_%": 4.75},     # Subrepresentado
    {"partido": "PT", "votos_%": 4.0, "escanos_%": 2.25},       # Subrepresentado
]

print("=" * 80)
print("📊 EJEMPLO: MORENA sobrerrepresentado, todos los demás subrepresentados")
print("=" * 80)
print(f"\n{'Partido':<10} {'Votos %':>10} {'Escaños %':>10} {'Ratio':>10}")
print("-" * 80)

ratios = []
for p in partidos:
    ratio = p["escanos_%"] / p["votos_%"]
    ratios.append(ratio)
    print(f"{p['partido']:<10} {p['votos_%']:>9.1f}% {p['escanos_%']:>9.1f}% {ratio:>9.4f}")

print("\n" + "=" * 80)
print("🧮 MÉTODO ACTUAL (promedio PONDERADO por votos):")
print("=" * 80)

suma_ratios_ponderados = sum(p["escanos_%"] / p["votos_%"] * p["votos_%"] for p in partidos)
suma_votos = sum(p["votos_%"] for p in partidos)
ratio_ponderado = suma_ratios_ponderados / suma_votos

print(f"Σ(ratio × votos_%) / Σ(votos_%) = {suma_ratios_ponderados:.4f} / {suma_votos:.1f}")
print(f"= {ratio_ponderado:.4f}")
print("\n❌ Problema: Siempre da ~1.0 porque es matemáticamente (Σ escaños) / (Σ votos)")

print("\n" + "=" * 80)
print("✅ MÉTODO CORRECTO (promedio SIMPLE de ratios):")
print("=" * 80)

import statistics
ratio_simple = statistics.mean(ratios)
desviacion = statistics.stdev(ratios)

print(f"mean([{', '.join(f'{r:.4f}' for r in ratios)}])")
print(f"= {ratio_simple:.4f}")
print(f"\nDesviación estándar: {desviacion:.4f}")
print(f"Coeficiente de variación: {desviacion/ratio_simple:.4f}")

print("\n" + "=" * 80)
print("💡 INTERPRETACIÓN:")
print("=" * 80)
print(f"• Ratio promedio simple = {ratio_simple:.4f}")
print(f"  → Valor perfecto sería 1.0 (cada partido tiene escaños proporcionales a votos)")
print(f"  → Valores > 1.0 indican sobrerrepresentación promedio")
print(f"  → Valores < 1.0 indican subrepresentación promedio")
print(f"\n• Desviación estándar = {desviacion:.4f}")
print(f"  → Qué tan dispersos están los ratios")
print(f"  → Valores más altos = más desproporcionalidad entre partidos")

print("\n" + "=" * 80)
print("🔧 LO QUE HAY QUE CAMBIAR EN main.py:")
print("=" * 80)
print("En la función calcular_ratios_proporcionalidad():")
print("")
print("ANTES (ponderado):")
print("  ratio_promedio = np.average(ratios, weights=pesos)")
print("")
print("DESPUÉS (simple):")
print("  ratio_promedio = np.mean(ratios)")
print("")
print("✅ Esto SÍ dará valores diferentes de 1.0 cuando hay desproporcionalidad")
