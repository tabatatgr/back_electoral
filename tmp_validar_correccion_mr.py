"""
Test: Verificar corrección de MR sin coaliciones
"""
from engine.procesar_diputados_v2 import procesar_diputados_v2

print("="*60)
print("PROBANDO CORRECCIÓN: MR SIN COALICIONES")
print("="*60)

# Procesar SIN coalición (ahora debería calcular por votos directos)
print("\n[1/2] Procesando SIN coalición...")
resultado_sin = procesar_diputados_v2(
    path_parquet='data/computos_diputados_2024.parquet',
    anio=2024,
    path_siglado='data/siglado-diputados-2024.csv',
    max_seats=500,
    sistema='mixto',
    mr_seats=250,
    rp_seats=250,
    umbral=0.03,
    quota_method='hare',
    usar_coaliciones=False,
    print_debug=False
)

print("\n[2/2] Procesando CON coalición...")
resultado_con = procesar_diputados_v2(
    path_parquet='data/computos_diputados_2024.parquet',
    anio=2024,
    path_siglado='data/siglado-diputados-2024.csv',
    max_seats=500,
    sistema='mixto',
    mr_seats=250,
    rp_seats=250,
    umbral=0.03,
    quota_method='hare',
    usar_coaliciones=True,
    print_debug=False
)

print("\n" + "="*60)
print("RESULTADOS COMPARATIVOS")
print("="*60)

print("\n📊 SIN COALICIÓN (votos individuales):")
print(f"  MORENA: {resultado_sin['tot']['MORENA']} total (MR={resultado_sin['mr']['MORENA']}, RP={resultado_sin['rp']['MORENA']})")
print(f"  PT:     {resultado_sin['tot']['PT']} total (MR={resultado_sin['mr']['PT']}, RP={resultado_sin['rp']['PT']})")
print(f"  PVEM:   {resultado_sin['tot']['PVEM']} total (MR={resultado_sin['mr']['PVEM']}, RP={resultado_sin['rp']['PVEM']})")
print(f"  PAN:    {resultado_sin['tot']['PAN']} total (MR={resultado_sin['mr']['PAN']}, RP={resultado_sin['rp']['PAN']})")
print(f"  PRI:    {resultado_sin['tot']['PRI']} total (MR={resultado_sin['mr']['PRI']}, RP={resultado_sin['rp']['PRI']})")
print(f"  ---")
print(f"  Coalición virtual: {resultado_sin['tot']['MORENA'] + resultado_sin['tot']['PT'] + resultado_sin['tot']['PVEM']}")

print("\n📊 CON COALICIÓN (convenio aplicado):")
print(f"  MORENA: {resultado_con['tot']['MORENA']} total (MR={resultado_con['mr']['MORENA']}, RP={resultado_con['rp']['MORENA']})")
print(f"  PT:     {resultado_con['tot']['PT']} total (MR={resultado_con['mr']['PT']}, RP={resultado_con['rp']['PT']})")
print(f"  PVEM:   {resultado_con['tot']['PVEM']} total (MR={resultado_con['mr']['PVEM']}, RP={resultado_con['rp']['PVEM']})")
print(f"  PAN:    {resultado_con['tot']['PAN']} total (MR={resultado_con['mr']['PAN']}, RP={resultado_con['rp']['PAN']})")
print(f"  PRI:    {resultado_con['tot']['PRI']} total (MR={resultado_con['mr']['PRI']}, RP={resultado_con['rp']['PRI']})")
print(f"  ---")
print(f"  Coalición real: {resultado_con['tot']['MORENA'] + resultado_con['tot']['PT'] + resultado_con['tot']['PVEM']}")

print("\n🔍 DIFERENCIAS:")
diff_morena_mr = resultado_sin['mr']['MORENA'] - resultado_con['mr']['MORENA']
diff_morena_tot = resultado_sin['tot']['MORENA'] - resultado_con['tot']['MORENA']
diff_coal_mr = (resultado_sin['mr']['MORENA'] + resultado_sin['mr']['PT'] + resultado_sin['mr']['PVEM']) - \
               (resultado_con['mr']['MORENA'] + resultado_con['mr']['PT'] + resultado_con['mr']['PVEM'])
diff_coal_tot = (resultado_sin['tot']['MORENA'] + resultado_sin['tot']['PT'] + resultado_sin['tot']['PVEM']) - \
                (resultado_con['tot']['MORENA'] + resultado_con['tot']['PT'] + resultado_con['tot']['PVEM'])

print(f"  MORENA pierde en MR por convenio: {diff_morena_mr:+d} distritos")
print(f"  MORENA pierde en TOTAL por convenio: {diff_morena_tot:+d} escaños")
print(f"  Coalición gana en MR (bloque): {diff_coal_mr:+d} distritos")
print(f"  Coalición en TOTAL (bloque): {diff_coal_tot:+d} escaños")

print("\n✅ VALIDACIÓN:")
print(f"  ¿MORENA tiene menos MR con coalición? {resultado_con['mr']['MORENA'] < resultado_sin['mr']['MORENA']}")
print(f"  ¿PT y PVEM tienen más MR con coalición? {resultado_con['mr']['PT'] > 0 and resultado_con['mr']['PVEM'] > 0}")
print(f"  ¿Coalición mantiene similar total? {abs(diff_coal_tot) < 10}")

print("\n" + "="*60)
