"""
Script para diagnosticar por qué ratio_promedio siempre es ~1.0
"""
import requests
import json

# Configuración prueba extrema: 400 escaños, sin coaliciones, sin topes
payload = {
    "anio": "2024",
    "plan": "personalizado",
    "escanos_totales": 400,
    "sistema": "mixto",
    "mr_seats": 200,
    "rp_seats": 200,
    "aplicar_topes": False,
    "usar_coaliciones": False,
    "umbral": 0.0  # SIN umbral para maximizar diferencias
}

print("=" * 80)
print("🔍 DIAGNÓSTICO: ¿Por qué ratio_promedio siempre es ~1.0?")
print("=" * 80)

response = requests.post("http://localhost:8000/procesar/diputados", json=payload)
data = response.json()

# Mostrar resultados detallados
print("\n📊 Resultados por partido:")
print("-" * 80)
print(f"{'Partido':<10} {'Votos %':>10} {'Escaños %':>10} {'Ratio':>10} {'Escaños':>10}")
print("-" * 80)

resultados = data["resultados"]
total_votos_pct = 0
total_escanos_pct = 0
suma_ratios_ponderados = 0

for r in resultados:
    if r["escanos_totales"] > 0:
        votos_pct = r["porcentaje_votos"]
        escanos_pct = r["porcentaje_escanos"]
        ratio = escanos_pct / votos_pct if votos_pct > 0 else 0
        
        print(f"{r['partido']:<10} {votos_pct:>9.2f}% {escanos_pct:>9.2f}% {ratio:>9.4f} {r['escanos_totales']:>10}")
        
        # Acumular para verificar matemática
        total_votos_pct += votos_pct
        total_escanos_pct += escanos_pct
        suma_ratios_ponderados += ratio * votos_pct

print("-" * 80)
print(f"{'TOTAL':<10} {total_votos_pct:>9.2f}% {total_escanos_pct:>9.2f}%")

# Cálculo manual del ratio promedio ponderado
ratio_promedio_manual = suma_ratios_ponderados / total_votos_pct if total_votos_pct > 0 else 0

print("\n" + "=" * 80)
print("📐 MATEMÁTICA DEL RATIO PROMEDIO PONDERADO:")
print("=" * 80)
print(f"Suma de (ratio_i × votos_%_i) = {suma_ratios_ponderados:.4f}")
print(f"Total votos % = {total_votos_pct:.2f}%")
print(f"Ratio promedio = {suma_ratios_ponderados:.4f} / {total_votos_pct:.2f} = {ratio_promedio_manual:.4f}")

print("\n" + "=" * 80)
print("🔬 ¿POR QUÉ SIEMPRE ES ~1.0?")
print("=" * 80)
print("El ratio promedio PONDERADO se calcula así:")
print("  ratio_promedio = Σ(ratio_i × peso_i) / Σ(peso_i)")
print("")
print("Donde:")
print("  - ratio_i = (escaños_% / votos_%) del partido i")
print("  - peso_i = votos_% del partido i")
print("")
print("Sustituyendo ratio_i:")
print("  ratio_promedio = Σ((escaños_%_i / votos_%_i) × votos_%_i) / Σ(votos_%_i)")
print("                 = Σ(escaños_%_i) / Σ(votos_%_i)")
print("                 = total_escaños_% / total_votos_%")
print("")
print("Si consideramos TODOS los partidos (con o sin escaños):")
print("  - Σ(votos_%_i) = 100%")
print("  - Σ(escaños_%_i) = 100%")
print("  - ratio_promedio = 100% / 100% = 1.0")
print("")
print("⚠️  CONCLUSIÓN: El ratio promedio ponderado por votos SIEMPRE será ~1.0")
print("    porque matemáticamente es (total escaños) / (total votos) = 1")
print("")

print("=" * 80)
print("💡 SOLUCIÓN: Usar métricas que SÍ varían con la desproporcionalidad")
print("=" * 80)
print("Opciones más útiles:")
print("  1. Índice de Gallagher (ya lo tienes)")
print("  2. Desviación estándar de ratios (ya lo tienes)")
print("  3. Coeficiente de variación (ya lo tienes)")
print("  4. Ratio MAX/MIN de sobrerrepresentación")
print("  5. Número de partidos sobre/subrepresentados")
print("")

# Mostrar métricas actuales
metricas = data["metricas_proporcionalidad"]
print(f"\n📊 Métricas actuales del API:")
print(f"   - ratio_promedio: {metricas['ratio_promedio']} (siempre ~1.0 ❌)")
print(f"   - desviacion_estandar: {metricas['desviacion_estandar']} (SÍ varía ✅)")
print(f"   - coeficiente_variacion: {metricas['coeficiente_variacion']} (SÍ varía ✅)")
print(f"   - gallagher_index: {data.get('gallagher_index', 'N/A')} (SÍ varía ✅)")
print("")
print("✅ Recomendación: Eliminar 'ratio_promedio' del response o reemplazarlo")
print("   por una métrica más útil (ej: ratio máximo o rango de ratios)")
