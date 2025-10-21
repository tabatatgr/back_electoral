"""
Demo: Respuesta exacta del backend con PM para el frontend
"""
import json

# Esta es la respuesta que el BACKEND envía al FRONTEND
# cuando haces: POST /procesar/diputados?anio=2024&plan=personalizado&sistema=mr&escanos_totales=300&pm_seats=100

respuesta_ejemplo = {
    "plan": "personalizado",
    
    # ARRAY DE RESULTADOS - AQUÍ ESTÁ TODO LO QUE NECESITAS
    "resultados": [
        {
            "partido": "MORENA",
            "votos": 22905421,
            
            # 🎯 DESGLOSE DE ESCAÑOS:
            "mr": 107,      # MR efectivo (de los 200 MR disponibles)
            "pm": 15,       # PM (de los 100 PM solicitados)
            "rp": 0,        # RP (0 en este caso)
            "total": 122,   # TOTAL = 107 + 15 + 0
            
            "porcentaje_votos": 38.52,
            "porcentaje_escanos": 40.67
        },
        {
            "partido": "PAN",
            "votos": 14328493,
            "mr": 22,
            "pm": 35,       # PAN fue 2do en muchos distritos
            "rp": 0,
            "total": 57,
            "porcentaje_votos": 24.11,
            "porcentaje_escanos": 19.0
        },
        {
            "partido": "PVEM",
            "votos": 8931245,
            "mr": 39,
            "pm": 9,
            "rp": 0,
            "total": 48,
            "porcentaje_votos": 15.02,
            "porcentaje_escanos": 16.0
        },
        {
            "partido": "PT",
            "votos": 6542891,
            "mr": 26,
            "pm": 5,
            "rp": 0,
            "total": 31,
            "porcentaje_votos": 11.01,
            "porcentaje_escanos": 10.33
        },
        {
            "partido": "PRI",
            "votos": 3891234,
            "mr": 6,
            "pm": 19,       # PRI fue 2do en varios distritos
            "rp": 0,
            "total": 25,
            "porcentaje_votos": 6.55,
            "porcentaje_escanos": 8.33
        },
        {
            "partido": "MC",
            "votos": 2456789,
            "mr": 0,        # MC no ganó ningún distrito
            "pm": 17,       # Pero fue 2do en 17 distritos
            "rp": 0,
            "total": 17,
            "porcentaje_votos": 4.13,
            "porcentaje_escanos": 5.67
        }
    ],
    
    # KPIs GENERALES
    "kpis": {
        "total_votos": 59455073,
        "total_escanos": 300,
        "gallagher": 4.23,
        "mae_votos_vs_escanos": 2.1,
        "ratio_promedio": 1.05,
        "desviacion_proporcionalidad": 1.8,
        "partidos_con_escanos": 6
    },
    
    # DATOS PARA GRÁFICAS
    "seat_chart": [
        {
            "party": "MORENA",
            "seats": 122,
            "color": "#A0522D",
            "percent": 40.67,
            "votes": 22905421
        },
        {
            "party": "PAN",
            "seats": 57,
            "color": "#0066CC",
            "percent": 19.0,
            "votes": 14328493
        }
        # ... más partidos
    ]
}

print("\n" + "="*80)
print("RESPUESTA DEL BACKEND AL FRONTEND")
print("="*80)

print("\n📊 ESTRUCTURA JSON COMPLETA:")
print(json.dumps(respuesta_ejemplo, indent=2, ensure_ascii=False))

print("\n" + "="*80)
print("INTERPRETACIÓN PARA EL FRONTEND")
print("="*80)

print("\n🎯 POR CADA PARTIDO RECIBES:")
print("  - partido (string): Nombre del partido")
print("  - votos (number): Total de votos")
print("  - mr (number): Escaños de Mayoría Relativa efectivos")
print("  - pm (number): Escaños de Primera Minoría (2dos lugares)")
print("  - rp (number): Escaños de Representación Proporcional")
print("  - total (number): mr + pm + rp")
print("  - porcentaje_votos (number)")
print("  - porcentaje_escanos (number)")

print("\n📋 TABLA DE EJEMPLO:")
print(f"{'Partido':<12} {'MR':<8} {'PM':<8} {'RP':<8} {'Total':<8}")
print("-" * 52)

total_mr = 0
total_pm = 0
total_rp = 0
total_escanos = 0

for r in respuesta_ejemplo['resultados']:
    print(f"{r['partido']:<12} {r['mr']:<8} {r['pm']:<8} {r['rp']:<8} {r['total']:<8}")
    total_mr += r['mr']
    total_pm += r['pm']
    total_rp += r['rp']
    total_escanos += r['total']

print("-" * 52)
print(f"{'TOTAL':<12} {total_mr:<8} {total_pm:<8} {total_rp:<8} {total_escanos:<8}")

print("\n✅ VERIFICACIÓN:")
print(f"  MR efectivo: {total_mr} (200 de 300 - 100 PM)")
print(f"  PM asignado: {total_pm} (100 solicitados)")
print(f"  RP: {total_rp}")
print(f"  Total: {total_escanos} (= escanos_totales)")

print("\n💡 PARA TU FRONTEND:")
print("  1. Haces request: POST /procesar/diputados?anio=2024&pm_seats=100&...")
print("  2. Recibes este JSON completo")
print("  3. Iteras sobre data.resultados[]")
print("  4. Cada partido tiene: .mr, .pm, .rp, .total")
print("  5. Muestras en tabla o gráfica")
print("  6. ¡Listo!")

print("\n" + "="*80)
