"""
Debug detallado: ¿Por qué MORENA no recibe RP en 75MR/25RP?
"""
from engine.procesar_diputados_v2 import procesar_diputados_v2

print("="*80)
print("DEBUG: 2024 | 500 escaños | 75MR/25RP | CON coalición | SIN TOPES")
print("="*80)

resultado = procesar_diputados_v2(
    path_parquet='data/computos_diputados_2024.parquet',
    anio=2024,
    max_seats=500,
    mr_seats=375,  # 75% MR
    rp_seats=125,  # 25% RP
    usar_coaliciones=True,
    aplicar_topes=False,
    print_debug=False
)

print("\n📊 RESULTADOS FINALES:")
print("-" * 80)

# Listar todos los partidos
partidos_ordenados = sorted(resultado['tot'].items(), key=lambda x: x[1], reverse=True)

# Calcular total de votos para sacar porcentajes
total_votos = sum(resultado['votos'].values())

total_mr = 0
total_rp = 0
total_tot = 0

print(f"{'PARTIDO':<20} {'MR':>6} {'RP':>6} {'TOTAL':>6} {'MR+RP':>6} {'% VOTOS':>10}")
print("-" * 80)

for partido, tot in partidos_ordenados[:15]:  # Top 15
    mr = resultado['mr'].get(partido, 0)
    rp = resultado['rp'].get(partido, 0)
    votos = resultado['votos'].get(partido, 0)
    pct_votos = (votos / total_votos * 100) if total_votos > 0 else 0
    mr_plus_rp = mr + rp
    
    total_mr += mr
    total_rp += rp
    total_tot += tot
    
    if tot > 0 or pct_votos > 1:
        inconsistencia = " ⚠️" if mr_plus_rp != tot else ""
        print(f"{partido:<20} {mr:6d} {rp:6d} {tot:6d} {mr_plus_rp:6d} {pct_votos:9.2f}%{inconsistencia}")

print("-" * 80)
print(f"{'TOTAL':<20} {total_mr:6d} {total_rp:6d} {total_tot:6d}")

print("\n🔍 ANÁLISIS:")
print("-" * 80)

morena_mr = resultado['mr'].get('MORENA', 0)
morena_rp = resultado['rp'].get('MORENA', 0)
morena_tot = resultado['tot'].get('MORENA', 0)
morena_votos = resultado['votos'].get('MORENA', 0)
morena_pct = (morena_votos / total_votos * 100) if total_votos > 0 else 0

print(f"MORENA:")
print(f"  Votos: {morena_votos:,} ({morena_pct:.2f}%)")
print(f"  MR asignados: {morena_mr}")
print(f"  RP asignados: {morena_rp}")
print(f"  Total: {morena_tot}")
print(f"  MR + RP = {morena_mr + morena_rp}")

# Verificar si MORENA pasó el 3%
if 'ok' in resultado:
    ok_morena = resultado['ok'].get('MORENA', False)
    print(f"  Pasó umbral 3%: {ok_morena}")

print(f"\n⚠️ PROBLEMAS DETECTADOS:")

# Problema 1: RP = 0
if morena_rp == 0:
    print(f"  ❌ MORENA tiene RP=0 (debería recibir algo de los 125 RP disponibles)")
    print(f"  ❌ Con {morena_pct:.2f}% de votos, debería recibir ~{int(morena_pct/100 * 125)} RP")

# Problema 2: MR + RP ≠ TOTAL
if morena_mr + morena_rp != morena_tot:
    print(f"  ❌ ¡INCONSISTENCIA MATEMÁTICA! MR({morena_mr}) + RP({morena_rp}) = {morena_mr + morena_rp} ≠ TOTAL({morena_tot})")
    diferencia = morena_tot - (morena_mr + morena_rp)
    print(f"     Diferencia: {diferencia} escaños")

if morena_mr != 311:
    print(f"  ⚠️  MR reportado ({morena_mr}) != MR esperado (311)")
    print(f"     Esto sugiere que se cortaron {311 - morena_mr} MR")

print("\n" + "="*80)
