"""
Script de diagnóstico para investigar por qué PRD recibe escaños RP en Senado 2024
"""

import pandas as pd
from engine.procesar_senadores_v2 import procesar_senadores_v2

print("=" * 80)
print("DIAGNÓSTICO: PRD recibiendo RP en Senado 2024")
print("=" * 80)

# Ejecutar procesamiento de senadores 2024 (escenario vigente)
resultado = procesar_senadores_v2(
    path_parquet='data/computos_senado_2024.parquet',
    anio=2024,
    path_siglado='data/siglado-senado-2024.csv',
    max_seats=128,
    umbral=0.03,
    sistema='mixto'
)

print("\n1️⃣ VOTOS NACIONALES (antes de umbral)")
print("-" * 80)
votos = resultado.get('votos', {})
total_votos = sum(votos.values())

for partido in ['MORENA', 'PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC']:
    v = votos.get(partido, 0)
    pct = (v / total_votos * 100) if total_votos > 0 else 0
    print(f"{partido:8s}: {v:>12,} votos ({pct:>6.2f}%)")

print(f"\n{'TOTAL':8s}: {total_votos:>12,} votos")

print("\n2️⃣ VOTOS OK (después de umbral 3%)")
print("-" * 80)
votos_ok = resultado.get('votos_ok', {})

for partido in ['MORENA', 'PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC']:
    v = votos_ok.get(partido, 0)
    pct = (v / total_votos * 100) if total_votos > 0 else 0
    supera = "✅" if pct >= 3.0 else "❌"
    print(f"{partido:8s}: {v:>12,} votos ({pct:>6.2f}%) {supera}")

print("\n3️⃣ RESULTADO ESCAÑOS")
print("-" * 80)
mr = resultado.get('mr', {})
rp = resultado.get('rp', {})
tot = resultado.get('tot', {})

print(f"{'Partido':8s} {'MR+PM':>8s} {'RP':>6s} {'TOTAL':>8s}")
print("-" * 35)
for partido in ['MORENA', 'PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC']:
    m = mr.get(partido, 0)
    r = rp.get(partido, 0)
    t = tot.get(partido, 0)
    alerta = " ⚠️ " if partido == 'PRD' and r > 0 else ""
    print(f"{partido:8s} {m:>8d} {r:>6d} {t:>8d}{alerta}")

total_mr = sum(mr.values())
total_rp = sum(rp.values())
total_tot = sum(tot.values())
print("-" * 35)
print(f"{'TOTAL':8s} {total_mr:>8d} {total_rp:>6d} {total_tot:>8d}")

print("\n4️⃣ DIAGNÓSTICO PRD")
print("-" * 80)
prd_votos = votos.get('PRD', 0)
prd_pct = (prd_votos / total_votos * 100) if total_votos > 0 else 0
prd_votos_ok = votos_ok.get('PRD', 0)
prd_rp = rp.get('PRD', 0)

print(f"Votos PRD:           {prd_votos:>12,} ({prd_pct:.2f}%)")
print(f"Votos OK (post-3%):  {prd_votos_ok:>12,}")
print(f"RP asignado:         {prd_rp:>12d}")

if prd_pct < 3.0 and prd_rp > 0:
    print("\n🔴 PROBLEMA DETECTADO:")
    print(f"   PRD tiene {prd_pct:.2f}% de votos (< 3% umbral)")
    print(f"   Pero recibió {prd_rp} escaños de RP")
    print("\n💡 POSIBLES CAUSAS:")
    print("   1. Votos de coalición siendo contados para PRD")
    print("   2. Recomposición/desagregación asignando votos extra a PRD")
    print("   3. Bug en aplicación del umbral en assign_senadores()")
    
elif prd_pct >= 3.0 and prd_rp > 0:
    print("\n✅ COMPORTAMIENTO ESPERADO:")
    print(f"   PRD superó el umbral ({prd_pct:.2f}% >= 3%)")
    print(f"   Por lo tanto, recibir {prd_rp} escaños de RP es correcto")
    
elif prd_pct < 3.0 and prd_rp == 0:
    print("\n✅ COMPORTAMIENTO CORRECTO:")
    print(f"   PRD no superó el umbral ({prd_pct:.2f}% < 3%)")
    print(f"   Correctamente no recibió escaños de RP")

print("\n5️⃣ VERIFICACIÓN UMBRAL (OK dict)")
print("-" * 80)
ok_dict = resultado.get('ok', {})
for partido in ['MORENA', 'PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC']:
    supera = ok_dict.get(partido, False)
    print(f"{partido:8s}: {supera}")

print("\n" + "=" * 80)
print("FIN DEL DIAGNÓSTICO")
print("=" * 80)
