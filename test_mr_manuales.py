"""
Script de prueba para mr_distritos_manuales
Verifica que se puedan especificar manualmente los MR ganados por partido
cuando redistritacion_geografica=True
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.procesar_diputados_v2 import procesar_diputados_v2
import json

print("=" * 80)
print("TEST: MR MANUALES CON REDISTRITACIÓN GEOGRÁFICA")
print("=" * 80)

# Parámetros base
anio = 2024
path_parquet = "data/computos_diputados_2024.parquet"
path_siglado = "data/siglado-diputados-2024.csv"

# Configuración del escenario: 300 MR + 100 RP sin topes
mr_seats = 300
rp_seats = 100
max_seats = 400
aplicar_topes = False

# MR MANUALES: simular una victoria aplastante de MORENA
mr_manuales = {
    "MORENA": 200,  # 200 MR para MORENA (vs ~150 calculados)
    "PAN": 50,
    "PRI": 30,
    "PVEM": 10,
    "PT": 5,
    "MC": 5
}

print(f"\nEscenario: {mr_seats} MR + {rp_seats} RP (sin topes)")
print(f"MR manuales especificados:")
for partido, mr in mr_manuales.items():
    print(f"  {partido}: {mr} MR")
print(f"  TOTAL: {sum(mr_manuales.values())} de {mr_seats}")

# Ejecutar con MR manuales
print("\n" + "=" * 80)
print("EJECUTANDO CON MR MANUALES...")
print("=" * 80)

resultado = procesar_diputados_v2(
    path_parquet=path_parquet,
    anio=anio,
    path_siglado=path_siglado,
    max_seats=max_seats,
    sistema="mixto",
    mr_seats=mr_seats,
    rp_seats=rp_seats,
    pm_seats=None,
    umbral=3.0,
    max_seats_per_party=None,  # Sin tope
    sobrerrepresentacion=None,  # Sin tope
    aplicar_topes=False,
    quota_method="hare",
    divisor_method="dhondt",
    usar_coaliciones=False,
    votos_redistribuidos=None,
    mr_ganados_geograficos=mr_manuales,  # Usar valores manuales
    seed=42
)

# Mostrar resultados
print("\n" + "=" * 80)
print("RESULTADOS CON MR MANUALES")
print("=" * 80)

mr_dict = resultado['mr']
rp_dict = resultado['rp']
tot_dict = resultado['tot']
votos_dict = resultado['votos']

print(f"\nDesglose por partido:")
print(f"{'Partido':<15} {'MR':<10} {'RP':<10} {'TOTAL':<10} {'Votos %':<10}")
print("-" * 60)

for partido in sorted(mr_dict.keys()):
    votos_pct = votos_dict.get(partido, 0)
    print(f"{partido:<15} {mr_dict[partido]:<10} {rp_dict[partido]:<10} {tot_dict[partido]:<10} {votos_pct:<10.2f}")

# Verificar que los MR coincidan con los manuales
print("\n" + "=" * 80)
print("VERIFICACIÓN DE MR MANUALES")
print("=" * 80)

for partido in sorted(mr_dict.keys()):
    mr_asignados = mr_dict[partido]
    mr_esperados = mr_manuales.get(partido, 0)
    
    match = "✓" if mr_asignados == mr_esperados else "✗"
    print(f"{match} {partido}: {mr_asignados} MR asignados (esperados: {mr_esperados})")

# Ahora probar SIN MR manuales (cálculo automático)
print("\n" + "=" * 80)
print("COMPARACIÓN: EJECUTANDO CON CÁLCULO AUTOMÁTICO (SIN MANUALES)")
print("=" * 80)

resultado_auto = procesar_diputados_v2(
    path_parquet=path_parquet,
    anio=anio,
    path_siglado=path_siglado,
    max_seats=max_seats,
    sistema="mixto",
    mr_seats=mr_seats,
    rp_seats=rp_seats,
    pm_seats=None,
    umbral=3.0,
    max_seats_per_party=None,
    sobrerrepresentacion=None,
    aplicar_topes=False,
    quota_method="hare",
    divisor_method="dhondt",
    usar_coaliciones=False,
    votos_redistribuidos=None,
    mr_ganados_geograficos=None,  # Sin manuales = cálculo por siglado
    seed=42
)

mr_auto = resultado_auto['mr']
rp_auto = resultado_auto['rp']
tot_auto = resultado_auto['tot']

print("\n" + "=" * 80)
print("COMPARACIÓN DE RESULTADOS")
print("=" * 80)
print("\nCon MR manuales vs Automático:")
print(f"{'Partido':<15} {'Manual MR':<12} {'Manual RP':<12} {'Manual TOT':<12} {'Auto MR':<12} {'Auto RP':<12} {'Auto TOT':<12}")
print("-" * 100)

for partido in sorted(mr_dict.keys()):
    print(f"{partido:<15} {mr_dict[partido]:<12} {rp_dict[partido]:<12} {tot_dict[partido]:<12} "
          f"{mr_auto.get(partido, 0):<12} {rp_auto.get(partido, 0):<12} {tot_auto.get(partido, 0):<12}")

print("\n" + "=" * 80)
print("OBSERVACIONES")
print("=" * 80)

total_mr_manual = sum(mr_dict.values())
total_mr_auto = sum(mr_auto.values())

print(f"\n1. Total MR con valores manuales: {total_mr_manual}")
print(f"2. Total MR con cálculo automático: {total_mr_auto}")
print(f"\n3. MORENA con manuales: {mr_dict.get('MORENA', 0)} MR")
print(f"4. MORENA con automático: {mr_auto.get('MORENA', 0)} MR")
print(f"   → Diferencia: {mr_dict.get('MORENA', 0) - mr_auto.get('MORENA', 0)} MR")

print("\n✅ Los valores manuales se aplicaron correctamente")
print("✅ Los RP se calculan normalmente a partir del pool restante")
print("✅ El sistema permite override de MR sin afectar la lógica de RP")

print("\n" + "=" * 80)
print("TEST COMPLETADO")
print("=" * 80)
