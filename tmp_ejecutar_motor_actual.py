"""
EJECUTAR EL MOTOR ACTUAL Y VER QUÉ PASA
"""

import sys
sys.path.insert(0, 'engine')

from procesar_diputados_v2 import procesar_diputados

resultado = procesar_diputados(
    anio=2024,
    max_seats_per_party=300,
    usar_sobrerrepresentacion=False,
    usar_coaliciones=True,
    print_debug=False
)

print("=" * 80)
print("RESULTADO DEL MOTOR ACTUAL")
print("=" * 80)

print(f"\n{'Partido':<10} {'MR':>10} {'RP':>10} {'Total':>10}")
print("-" * 45)

for partido in sorted(resultado.keys()):
    if partido != 'coaliciones':
        mr = resultado[partido].get('mr', 0)
        rp = resultado[partido].get('rp', 0)
        total = resultado[partido].get('total', 0)
        print(f"{partido:<10} {mr:>10} {rp:>10} {total:>10}")

# Totales
total_mr = sum(resultado[p].get('mr', 0) for p in resultado if p != 'coaliciones')
total_rp = sum(resultado[p].get('rp', 0) for p in resultado if p != 'coaliciones')
total_total = sum(resultado[p].get('total', 0) for p in resultado if p != 'coaliciones')

print("-" * 45)
print(f"{'TOTAL':<10} {total_mr:>10} {total_rp:>10} {total_total:>10}")

print("\n" + "=" * 80)
print("COMPARACIÓN CON OFICIALES")
print("=" * 80)

oficiales = {
    'MORENA': 257,
    'PAN': 71,
    'PVEM': 60,
    'PT': 47,
    'PRI': 36,
    'MC': 27,
    'PRD': 1,
    'IND': 1
}

print(f"\n{'Partido':<10} {'Motor':>10} {'Oficial':>10} {'Dif':>10}")
print("-" * 45)

for partido in sorted(oficiales.keys()):
    motor_val = resultado.get(partido, {}).get('total', 0)
    oficial_val = oficiales.get(partido, 0)
    dif = motor_val - oficial_val
    marca = "✅" if dif == 0 else "⚠️"
    print(f"{partido:<10} {motor_val:>10} {oficial_val:>10} {dif:>10} {marca}")
