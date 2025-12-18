"""
Probar diferentes combinaciones de parámetros para encontrar cuál causa el +1 RP
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.procesar_diputados_v2 import procesar_diputados_v2

def test_config(name, **kwargs):
    print(f"\n{'='*80}")
    print(f"TEST: {name}")
    print(f"{'='*80}")
    
    resultado = procesar_diputados_v2(
        path_parquet="data/computos_diputados_2024.parquet",
        anio=2024,
        path_siglado="data/siglado-diputados-2024.csv",
        print_debug=False,
        **kwargs
    )
    
    morena_mr = resultado['mr'].get('MORENA', 0)
    morena_rp = resultado['rp'].get('MORENA', 0)
    morena_total = resultado['tot'].get('MORENA', 0)
    total_rp = sum(resultado['rp'].values())
    
    print(f"MORENA: MR={morena_mr}, RP={morena_rp}, TOTAL={morena_total}")
    print(f"Total RP: {total_rp}")
    
    if morena_rp == 93:
        print("✅ RP CORRECTO (93)")
    elif morena_rp == 94:
        print("❌ RP INCORRECTO (+1 extra)")
    else:
        print(f"⚠️  RP inesperado: {morena_rp}")
    
    return morena_rp

# TEST 1: Configuración mínima (lo que sabemos que funciona)
rp1 = test_config(
    "Mínima (script directo anterior)",
    max_seats=400,
    sistema="mixto",
    mr_seats=200,
    rp_seats=200,
    pm_seats=0,
    umbral=0.03,
    max_seats_per_party=None,
    sobrerrepresentacion=None,
    aplicar_topes=False,
    quota_method="hare",
    divisor_method=None,
    usar_coaliciones=False,
    votos_redistribuidos=None,
    seed=42
)

# TEST 2: Con max_seats_per_party=None explícito (igual que TEST 1)
rp2 = test_config(
    "Con max_seats_per_party=None explícito",
    max_seats=400,
    sistema="mixto",
    mr_seats=200,
    rp_seats=200,
    pm_seats=0,
    umbral=0.03,
    max_seats_per_party=None,
    sobrerrepresentacion=None,
    aplicar_topes=False,
    quota_method="hare",
    divisor_method=None,
    usar_coaliciones=False,
    votos_redistribuidos=None,
    seed=42
)

# TEST 3: Sin especificar max_seats (como lo hace el API cuando usa plan personalizado)
rp3 = test_config(
    "Sin especificar max_seats explícitamente",
    sistema="mixto",
    mr_seats=200,
    rp_seats=200,
    pm_seats=0,
    umbral=0.03,
    max_seats_per_party=None,
    sobrerrepresentacion=None,
    aplicar_topes=False,
    quota_method="hare",
    divisor_method=None,
    usar_coaliciones=False,
    votos_redistribuidos=None,
    seed=42
)

# TEST 4: Con umbral None (por defecto 0.03 interno)
rp4 = test_config(
    "Con umbral=None (default interno)",
    max_seats=400,
    sistema="mixto",
    mr_seats=200,
    rp_seats=200,
    pm_seats=0,
    umbral=None,
    max_seats_per_party=None,
    sobrerrepresentacion=None,
    aplicar_topes=False,
    quota_method="hare",
    divisor_method=None,
    usar_coaliciones=False,
    votos_redistribuidos=None,
    seed=42
)

print(f"\n{'='*80}")
print("RESUMEN:")
print(f"{'='*80}")
print(f"TEST 1 (Mínima): RP={rp1}")
print(f"TEST 2 (max_seats_per_party=None): RP={rp2}")
print(f"TEST 3 (Sin max_seats): RP={rp3}")
print(f"TEST 4 (umbral=None): RP={rp4}")

if all(rp == 93 for rp in [rp1, rp2, rp3, rp4]):
    print("\n✅ Todas las configuraciones dan RP=93 correcto")
    print("   El problema debe estar en otro parámetro que la API pasa diferente")
elif any(rp == 94 for rp in [rp1, rp2, rp3, rp4]):
    print("\n❌ Alguna configuración produce el +1 RP:")
    if rp3 == 94:
        print("   → Sin max_seats explícito causa el problema")
    if rp4 == 94:
        print("   → umbral=None causa el problema")
