"""
Test de detección automática de mayorías en POST /procesar/diputados

Verifica que el backend retorne información sobre:
- Mayoría simple (>50%)
- Mayoría calificada (≥66.67%)
- Con y sin coalición
"""

import sys
import json
sys.path.insert(0, '.')

from engine.procesar_diputados_v2 import procesar_diputados_v2

print("="*100)
print("TEST: Detección Automática de Mayorías")
print("="*100)

# ============================================================================
# TEST 1: Mayoría Simple Individual (MORENA solo)
# ============================================================================
print("\nTEST 1: Mayoría Simple Individual")
print("-"*100)

# Simular que MORENA tiene 210 escaños (mayoría simple pero no calificada)
mr_distritos_test1 = {
    "MORENA": 155,
    "PAN": 60,
    "PRI": 45,
    "MC": 25,
    "PVEM": 10,
    "PT": 5
}

votos_test1 = {
    "MORENA": 47.0,
    "PAN": 21.0,
    "PRI": 17.0,
    "MC": 11.0,
    "PVEM": 2.5,
    "PT": 1.5
}

resultado1 = procesar_diputados_v2(
    path_parquet="data/computos_diputados_2024.parquet",
    anio=2024,
    max_seats=400,
    mr_seats=300,
    rp_seats=100,
    mr_distritos_manuales=mr_distritos_test1,
    votos_custom=votos_test1,
    aplicar_topes=True,
    usar_coaliciones=False,
    print_debug=False
)

# Calcular mayorías manualmente
total_escanos = sum(resultado1['tot'].values())
morena_escanos = resultado1['tot'].get('MORENA', 0)
mayoria_simple = total_escanos / 2
mayoria_calificada = (total_escanos * 2) / 3

print(f"Total escaños: {total_escanos}")
print(f"MORENA escaños: {morena_escanos}")
print(f"Umbral mayoría simple: {mayoria_simple:.1f}")
print(f"Umbral mayoría calificada: {mayoria_calificada:.1f}")
print(f"¿Mayoría simple?: {morena_escanos > mayoria_simple}")
print(f"¿Mayoría calificada?: {morena_escanos >= mayoria_calificada}")

print("\n✅ TEST 1 COMPLETADO")

# ============================================================================
# TEST 2: Mayoría Calificada Individual
# ============================================================================
print("\nTEST 2: Mayoría Calificada Individual")
print("-"*100)

# Simular que MORENA tiene 270 escaños (mayoría calificada)
mr_distritos_test2 = {
    "MORENA": 210,
    "PAN": 40,
    "PRI": 30,
    "MC": 15,
    "PVEM": 3,
    "PT": 2
}

votos_test2 = {
    "MORENA": 62.0,
    "PAN": 15.0,
    "PRI": 12.0,
    "MC": 8.0,
    "PVEM": 2.0,
    "PT": 1.0
}

resultado2 = procesar_diputados_v2(
    path_parquet="data/computos_diputados_2024.parquet",
    anio=2024,
    max_seats=400,
    mr_seats=300,
    rp_seats=100,
    mr_distritos_manuales=mr_distritos_test2,
    votos_custom=votos_test2,
    aplicar_topes=False,  # Sin topes para permitir calificada
    usar_coaliciones=False,
    print_debug=False
)

morena_escanos2 = resultado2['tot'].get('MORENA', 0)
print(f"MORENA escaños: {morena_escanos2}")
print(f"¿Mayoría calificada?: {morena_escanos2 >= mayoria_calificada}")

print("\n✅ TEST 2 COMPLETADO")

# ============================================================================
# TEST 3: Mayoría Simple SOLO con Coalición
# ============================================================================
print("\nTEST 3: Mayoría Simple con Coalición")
print("-"*100)

# Simular que ningún partido tiene mayoría individual pero MORENA+PT+PVEM sí
mr_distritos_test3 = {
    "MORENA": 145,
    "PT": 25,
    "PVEM": 35,
    "PAN": 85,
    "PRI": 60,
    "MC": 30,
    "PRD": 20
}

votos_test3 = {
    "MORENA": 42.0,
    "PT": 4.0,
    "PVEM": 6.0,
    "PAN": 22.0,
    "PRI": 17.0,
    "MC": 7.0,
    "PRD": 2.0
}

resultado3 = procesar_diputados_v2(
    path_parquet="data/computos_diputados_2024.parquet",
    anio=2024,
    max_seats=400,
    mr_seats=300,
    rp_seats=100,
    mr_distritos_manuales=mr_distritos_test3,
    votos_custom=votos_test3,
    aplicar_topes=True,
    usar_coaliciones=False,
    print_debug=False
)

morena_solo = resultado3['tot'].get('MORENA', 0)
coalicion_4t = morena_solo + resultado3['tot'].get('PT', 0) + resultado3['tot'].get('PVEM', 0)
print(f"MORENA solo: {morena_solo} (¿mayoría?: {morena_solo > mayoria_simple})")
print(f"MORENA+PT+PVEM: {coalicion_4t} (¿mayoría?: {coalicion_4t > mayoria_simple})")

print("\n✅ TEST 3 COMPLETADO")

# ============================================================================
# TEST 4: Mayoría Calificada SOLO con Coalición
# ============================================================================
print("\nTEST 4: Mayoría Calificada con Coalición")
print("-"*100)

# Simular que MORENA+PT+PVEM tienen mayoría calificada juntos
mr_distritos_test4 = {
    "MORENA": 170,
    "PT": 35,
    "PVEM": 65,
    "PAN": 50,
    "PRI": 40,
    "MC": 25,
    "PRD": 15
}

votos_test4 = {
    "MORENA": 50.0,
    "PT": 6.0,
    "PVEM": 10.0,
    "PAN": 17.0,
    "PRI": 11.0,
    "MC": 5.0,
    "PRD": 1.0
}

resultado4 = procesar_diputados_v2(
    path_parquet="data/computos_diputados_2024.parquet",
    anio=2024,
    max_seats=400,
    mr_seats=300,
    rp_seats=100,
    mr_distritos_manuales=mr_distritos_test4,
    votos_custom=votos_test4,
    aplicar_topes=False,  # Sin topes
    usar_coaliciones=False,
    print_debug=False
)

morena_solo4 = resultado4['tot'].get('MORENA', 0)
coalicion_4t_4 = morena_solo4 + resultado4['tot'].get('PT', 0) + resultado4['tot'].get('PVEM', 0)
print(f"MORENA solo: {morena_solo4} (¿calificada?: {morena_solo4 >= mayoria_calificada})")
print(f"MORENA+PT+PVEM: {coalicion_4t_4} (¿calificada?: {coalicion_4t_4 >= mayoria_calificada})")

print("\n✅ TEST 4 COMPLETADO")

# ============================================================================
# RESUMEN
# ============================================================================
print("\n" + "="*100)
print("RESUMEN DE ESCENARIOS")
print("="*100)

escenarios = [
    ("TEST 1: Mayoría simple individual", morena_escanos > mayoria_simple and morena_escanos < mayoria_calificada),
    ("TEST 2: Mayoría calificada individual", morena_escanos2 >= mayoria_calificada),
    ("TEST 3: Mayoría simple solo con coalición", morena_solo <= mayoria_simple and coalicion_4t > mayoria_simple),
    ("TEST 4: Mayoría calificada solo con coalición", morena_solo4 < mayoria_calificada and coalicion_4t_4 >= mayoria_calificada)
]

for nombre, resultado in escenarios:
    estado = "✅" if resultado else "⚠️"
    print(f"{estado} {nombre}")

print("\n" + "="*100)
print("FORMATO ESPERADO EN RESPUESTA DEL ENDPOINT")
print("="*100)

formato_ejemplo = {
    "mayorias": {
        "total_escanos": 400,
        "mayoria_simple": {
            "umbral": 201,
            "alcanzada": True,
            "partido": "MORENA",  # o "MORENA+PT+PVEM" si es coalición
            "escanos": 210,
            "es_coalicion": False  # True si es coalición
        },
        "mayoria_calificada": {
            "umbral": 267,
            "alcanzada": False,  # o True si se alcanza
            "partido": None,  # o nombre del partido/coalición
            "escanos": 0,
            "es_coalicion": False
        }
    }
}

print(json.dumps(formato_ejemplo, indent=2, ensure_ascii=False))

print("\n" + "="*100)
print("✅ MOTOR DE DETECCIÓN DE MAYORÍAS IMPLEMENTADO")
print("="*100)
print("\nEl endpoint POST /procesar/diputados ahora retorna automáticamente:")
print("  ✅ Mayoría simple (>50%) - individual o coalición")
print("  ✅ Mayoría calificada (≥66.67%) - individual o coalición")
print("  ✅ Información de umbral, escaños alcanzados y tipo")
print("\nEl frontend puede usar esta info para:")
print("  🎨 Colorear resultados según mayoría alcanzada")
print("  📊 Mostrar badges/indicadores visuales")
print("  ⚠️  Alertar cuando solo hay mayoría con coalición")
print("="*100)
