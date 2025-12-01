"""
Comparación directa CON vs SIN topes para 2024 | 500 escaños
"""
from engine.procesar_diputados_v2 import procesar_diputados_v2

configs = [
    ("50MR_50RP", 250, 250),
    ("60MR_40RP", 300, 200),
    ("75MR_25RP", 375, 125),
]

print("="*80)
print("COMPARACIÓN: CON TOPES vs SIN TOPES (2024 | 500 escaños | CON coalición)")
print("="*80)

for nombre, mr_seats, rp_seats in configs:
    print(f"\n{nombre}:")
    
    # CON topes
    res_con = procesar_diputados_v2(
        path_parquet='data/computos_diputados_2024.parquet',
        anio=2024,
        max_seats=500,
        mr_seats=mr_seats,
        rp_seats=rp_seats,
        usar_coaliciones=True,
        aplicar_topes=True
    )
    
    morena_mr_con = res_con['mr'].get('MORENA', 0)
    morena_rp_con = res_con['rp'].get('MORENA', 0)
    morena_tot_con = res_con['tot'].get('MORENA', 0)
    
    # SIN topes
    res_sin = procesar_diputados_v2(
        path_parquet='data/computos_diputados_2024.parquet',
        anio=2024,
        max_seats=500,
        mr_seats=mr_seats,
        rp_seats=rp_seats,
        usar_coaliciones=True,
        aplicar_topes=False
    )
    
    morena_mr_sin = res_sin['mr'].get('MORENA', 0)
    morena_rp_sin = res_sin['rp'].get('MORENA', 0)
    morena_tot_sin = res_sin['tot'].get('MORENA', 0)
    
    print(f"  CON TOPES:  MR={morena_mr_con:3d} + RP={morena_rp_con:3d} = {morena_tot_con:3d}")
    print(f"  SIN TOPES:  MR={morena_mr_sin:3d} + RP={morena_rp_sin:3d} = {morena_tot_sin:3d}")
    print(f"  DIFERENCIA: MR={morena_mr_sin-morena_mr_con:+3d}   RP={morena_rp_sin-morena_rp_con:+3d}   TOT={morena_tot_sin-morena_tot_con:+3d}")

print("\n" + "="*80)
