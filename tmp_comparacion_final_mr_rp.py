"""
COMPARACIÓN FINAL: MR calculado + RP calculado vs Oficial
"""

import pandas as pd

print("=" * 80)
print("COMPARACIÓN MR+RP vs OFICIAL 2024")
print("=" * 80)

# MR calculados con lógica correcta
mr_calculados = {
    'MORENA': 126,
    'PAN': 38,
    'PRD': 13,
    'PRI': 24,
    'PT': 38,
    'PVEM': 58,
    'MC': 3
}

# RP calculados con Hare (ya verificados correctos)
rp_calculados = {
    'MORENA': 85,
    'PAN': 35,
    'PRD': 5,
    'PRI': 23,
    'PT': 11,
    'PVEM': 18,
    'MC': 23
}

# Oficiales (del archivo escaños_resumen)
oficiales = {
    'MORENA': 257,
    'PAN': 71,
    'PRD': 1,
    'PRI': 36,
    'PT': 47,
    'PVEM': 60,
    'MC': 27,
    'IND': 1
}

# Calcular total (MR + RP)
total_calculado = {}
for partido in mr_calculados:
    mr = mr_calculados.get(partido, 0)
    rp = rp_calculados.get(partido, 0)
    total_calculado[partido] = mr + rp

print(f"\n{'Partido':<10} {'MR':<10} {'RP':<10} {'Total':<10} {'Oficial':<10} {'Diferencia':<15}")
print("=" * 80)

total_mr = 0
total_rp = 0
total_calc = 0
total_of = 0
diferencias = {}

for partido in sorted(oficiales.keys()):
    mr = mr_calculados.get(partido, 0)
    rp = rp_calculados.get(partido, 0)
    calc = total_calculado.get(partido, 0)
    of = oficiales.get(partido, 0)
    dif = calc - of
    
    diferencias[partido] = dif
    
    total_mr += mr
    total_rp += rp
    total_calc += calc
    total_of += of
    
    status = "✓" if dif == 0 else f"⚠️ {dif:+d}"
    
    print(f"{partido:<10} {mr:<10} {rp:<10} {calc:<10} {of:<10} {status:<15}")

print("=" * 80)
print(f"{'TOTAL':<10} {total_mr:<10} {total_rp:<10} {total_calc:<10} {total_of:<10}")

print("\n" + "=" * 80)
print("RESUMEN DE DIFERENCIAS")
print("=" * 80)

for partido, dif in sorted(diferencias.items(), key=lambda x: abs(x[1]), reverse=True):
    if dif != 0:
        print(f"  {partido}: {dif:+d} escaños")

# Calcular MR implícito de oficiales
print("\n" + "=" * 80)
print("MR IMPLÍCITO (Oficial Total - RP Calculado)")
print("=" * 80)

print(f"\n{'Partido':<10} {'Of. Total':<12} {'RP (Hare)':<12} {'MR Implícito':<15} {'MR Calculado':<15} {'Dif':<10}")
print("=" * 80)

for partido in sorted(oficiales.keys()):
    of_total = oficiales.get(partido, 0)
    rp = rp_calculados.get(partido, 0)
    mr_implicito = of_total - rp
    mr_calc = mr_calculados.get(partido, 0)
    dif_mr = mr_calc - mr_implicito
    
    if partido != 'IND':  # IND no tiene RP
        status = "✓" if dif_mr == 0 else f"⚠️ {dif_mr:+d}"
        print(f"{partido:<10} {of_total:<12} {rp:<12} {mr_implicito:<15} {mr_calc:<15} {status:<10}")
