"""
Test con configuración 300 MR (real) para ver el convenio de coalición
"""
from engine.procesar_diputados_v2 import procesar_diputados_v2

print("="*60)
print("TEST: 300 MR + 200 RP (configuración real 2024)")
print("="*60)

# SIN coalición
print("\n[1/2] SIN coalición (votos individuales)...")
resultado_sin = procesar_diputados_v2(
    path_parquet='data/computos_diputados_2024.parquet',
    anio=2024,
    path_siglado='data/siglado-diputados-2024.csv',
    max_seats=500,
    sistema='mixto',
    mr_seats=300,  # <- 300 MR real
    rp_seats=200,
    umbral=0.03,
    quota_method='hare',
    usar_coaliciones=False,
    print_debug=False
)

# CON coalición
print("\n[2/2] CON coalición (convenio aplicado)...")
resultado_con = procesar_diputados_v2(
    path_parquet='data/computos_diputados_2024.parquet',
    anio=2024,
    path_siglado='data/siglado-diputados-2024.csv',
    max_seats=500,
    sistema='mixto',
    mr_seats=300,  # <- 300 MR real
    rp_seats=200,
    umbral=0.03,
    quota_method='hare',
    usar_coaliciones=True,
    print_debug=False
)

print("\n" + "="*60)
print("RESULTADOS - MR (Mayoría Relativa)")
print("="*60)

print("\nSIN COALICIÓN:")
print(f"  MORENA MR: {resultado_sin['mr']['MORENA']}")
print(f"  PT MR:     {resultado_sin['mr']['PT']}")
print(f"  PVEM MR:   {resultado_sin['mr']['PVEM']}")
print(f"  PAN MR:    {resultado_sin['mr']['PAN']}")
print(f"  ---")
print(f"  Total coalición: {resultado_sin['mr']['MORENA'] + resultado_sin['mr']['PT'] + resultado_sin['mr']['PVEM']}")

print("\nCON COALICIÓN (convenio):")
print(f"  MORENA MR: {resultado_con['mr']['MORENA']}")
print(f"  PT MR:     {resultado_con['mr']['PT']}")
print(f"  PVEM MR:   {resultado_con['mr']['PVEM']}")
print(f"  PAN MR:    {resultado_con['mr']['PAN']}")
print(f"  ---")
print(f"  Total coalición: {resultado_con['mr']['MORENA'] + resultado_con['mr']['PT'] + resultado_con['mr']['PVEM']}")

print("\nESPERADO (del siglado real):")
print(f"  MORENA MR: 148")
print(f"  PT MR:     46")
print(f"  PVEM MR:   71")
print(f"  ---")
print(f"  Total coalición: 265")

print("\nANÁLISIS:")
diff_mr = resultado_sin['mr']['MORENA'] - resultado_con['mr']['MORENA']
print(f"  Diferencia MORENA MR (sin - con): {diff_mr:+d}")
print(f"  ¿MORENA pierde MR en convenio?: {diff_mr > 0}")
print(f"  ¿PT y PVEM ganan MR en convenio?: {resultado_con['mr']['PT'] > resultado_sin['mr']['PT'] and resultado_con['mr']['PVEM'] > resultado_sin['mr']['PVEM']}")

print("\n" + "="*60)
print("RESULTADOS - TOTAL")
print("="*60)

print("\nSIN COALICIÓN:")
print(f"  MORENA: {resultado_sin['tot']['MORENA']} (MR={resultado_sin['mr']['MORENA']}, RP={resultado_sin['rp']['MORENA']})")
print(f"  PT:     {resultado_sin['tot']['PT']} (MR={resultado_sin['mr']['PT']}, RP={resultado_sin['rp']['PT']})")
print(f"  PVEM:   {resultado_sin['tot']['PVEM']} (MR={resultado_sin['mr']['PVEM']}, RP={resultado_sin['rp']['PVEM']})")

print("\nCON COALICIÓN:")
print(f"  MORENA: {resultado_con['tot']['MORENA']} (MR={resultado_con['mr']['MORENA']}, RP={resultado_con['rp']['MORENA']})")
print(f"  PT:     {resultado_con['tot']['PT']} (MR={resultado_con['mr']['PT']}, RP={resultado_con['rp']['PT']})")
print(f"  PVEM:   {resultado_con['tot']['PVEM']} (MR={resultado_con['mr']['PVEM']}, RP={resultado_con['rp']['PVEM']})")
