"""
Calcular cuántos RP le corresponden a PVEM según su % de votos
Usando método Hare (quota = votos_totales / escaños_disponibles)
"""

import pandas as pd

# Votos nacionales 2024
votos = {
    'MORENA': 24_286_412,
    'PAN': 10_049_424,
    'PVEM': 4_993_902,
    'PT': 3_254_709,
    'PRI': 6_623_752,
    'MC': 6_497_404,
    'PRD': 1_449_655
}

total_votos = sum(votos.values())
escanos_rp = 200  # Sistema vigente: 200 RP

print("=" * 80)
print("CÁLCULO DE RP CON MÉTODO HARE - 2024")
print("=" * 80)

print(f"\n📊 Total de votos válidos: {total_votos:,}")
print(f"📊 Escaños RP a distribuir: {escanos_rp}")

# Calcular quota Hare
quota_hare = total_votos / escanos_rp
print(f"\n🔢 Cuota Hare: {quota_hare:,.2f} votos por escaño")

print("\n" + "=" * 80)
print("ASIGNACIÓN INICIAL (votos / cuota)")
print("=" * 80)

resultados = []
for partido, v in votos.items():
    pct = (v / total_votos) * 100
    escanos_iniciales = int(v / quota_hare)  # Parte entera
    residuo = (v / quota_hare) - escanos_iniciales  # Parte decimal
    
    resultados.append({
        'partido': partido,
        'votos': v,
        'pct': pct,
        'escanos_iniciales': escanos_iniciales,
        'residuo': residuo
    })
    
    print(f"{partido:8s}: {v:12,} votos ({pct:5.2f}%) → {escanos_iniciales:3d} escaños (residuo: {residuo:.4f})")

df_resultados = pd.DataFrame(resultados)

escanos_asignados = df_resultados['escanos_iniciales'].sum()
escanos_restantes = escanos_rp - escanos_asignados

print(f"\n📊 Escaños asignados en primera ronda: {escanos_asignados}")
print(f"📊 Escaños restantes a distribuir: {escanos_restantes}")

print("\n" + "=" * 80)
print("DISTRIBUCIÓN DE ESCAÑOS RESTANTES (por residuo más alto)")
print("=" * 80)

# Ordenar por residuo descendente
df_resultados_sorted = df_resultados.sort_values('residuo', ascending=False).copy()

# Asignar escaños restantes
escanos_finales = df_resultados_sorted['escanos_iniciales'].values.copy()
for i in range(escanos_restantes):
    escanos_finales[i] += 1
    partido_beneficiado = df_resultados_sorted.iloc[i]['partido']
    residuo_beneficiado = df_resultados_sorted.iloc[i]['residuo']
    print(f"  Escaño #{i+1} → {partido_beneficiado} (residuo: {residuo_beneficiado:.4f})")

df_resultados_sorted['escanos_finales'] = escanos_finales

print("\n" + "=" * 80)
print("RESULTADO FINAL")
print("=" * 80)

df_final = df_resultados_sorted.sort_values('escanos_finales', ascending=False)

print(f"\n{'Partido':10s} {'Votos':>12s} {'%':>7s} {'RP':>5s}")
print("-" * 40)
for _, row in df_final.iterrows():
    print(f"{row['partido']:10s} {row['votos']:12,.0f} {row['pct']:6.2f}% {row['escanos_finales']:5.0f}")

print("-" * 40)
print(f"{'TOTAL':10s} {total_votos:12,} {'100.00%':>7s} {int(df_final['escanos_finales'].sum()):5d}")

print("\n" + "=" * 80)
print("🎯 PVEM ESPECÍFICAMENTE:")
print("=" * 80)

pvem_data = df_final[df_final['partido'] == 'PVEM'].iloc[0]
print(f"  Votos: {pvem_data['votos']:,.0f} ({pvem_data['pct']:.2f}%)")
print(f"  RP que le corresponde (Hare): {int(pvem_data['escanos_finales'])} escaños")
print(f"  RP que da el motor: 18 escaños")
print(f"  DIFERENCIA: {18 - int(pvem_data['escanos_finales'])} escaños DE MÁS")

print("\n" + "=" * 80)
print("💡 CONCLUSIÓN:")
print("=" * 80)

pvem_correcto = int(pvem_data['escanos_finales'])
pvem_motor = 18
diferencia = pvem_motor - pvem_correcto

if diferencia > 0:
    print(f"\n⚠️  PVEM está recibiendo {diferencia} escaños RP DE MÁS")
    print(f"   Debería recibir: {pvem_correcto} RP")
    print(f"   El motor le da: {pvem_motor} RP")
    print(f"\n   Si PVEM tiene 58 MR (distritos ganados):")
    print(f"   Total PVEM debería ser: 58 MR + {pvem_correcto} RP = {58 + pvem_correcto} escaños")
    print(f"   Total PVEM oficial: 60 escaños")
    print(f"   Total PVEM motor: 58 MR + 18 RP = 76 escaños")
