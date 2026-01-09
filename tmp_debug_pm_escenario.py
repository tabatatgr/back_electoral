"""
Debug: Verificar qué está pasando en escenario MR 200 - PM 200
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.procesar_diputados_v2 import procesar_diputados_v2

# Configuración escenario MR 200 - PM 200
resultado = procesar_diputados_v2(
    path_parquet='data/computos_diputados_2024.parquet',
    path_siglado='data/siglado-diputados-2024.csv',
    partidos_base=['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA'],
    anio=2024,
    max_seats=400,
    mr_seats=200,
    pm_seats=200,  # ← Primera Minoría
    rp_seats=0,    # ← SIN RP
    aplicar_topes=True,
    umbral=0.03,
    sobrerrepresentacion=8.0,
    max_seats_per_party=300,
    usar_coaliciones=True,
    seed=42,
    print_debug=True  # ACTIVAR DEBUG
)

print("\n" + "="*80)
print("RESULTADO ESCENARIO MR 200 - PM 200")
print("="*80)

mr_dict = resultado['mr']
pm_dict = resultado['pm']
rp_dict = resultado['rp']
tot_dict = resultado['tot']

print(f"\n{'Partido':<10} {'MR':>5} {'PM':>5} {'RP':>5} {'Total':>7}")
print("-" * 40)

for partido in ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA']:
    mr = mr_dict.get(partido, 0)
    pm = pm_dict.get(partido, 0)
    rp = rp_dict.get(partido, 0)
    total = tot_dict.get(partido, 0)
    print(f"{partido:<10} {mr:>5} {pm:>5} {rp:>5} {total:>7}")

print(f"\n{'TOTAL':<10} {sum(mr_dict.values()):>5} {sum(pm_dict.values()):>5} {sum(rp_dict.values()):>5} {sum(tot_dict.values()):>7}")

# Verificar PRD específicamente
prd_votos_pct = resultado['votos']['PRD'] / sum(resultado['votos'].values()) * 100
print(f"\nPRD: {prd_votos_pct:.2f}% votos")
print(f"PRD MR: {mr_dict['PRD']}")
print(f"PRD PM: {pm_dict['PRD']}")
print(f"PRD RP: {rp_dict['PRD']} ← DEBERÍA SER 0")
print(f"PRD Total: {tot_dict['PRD']}")
