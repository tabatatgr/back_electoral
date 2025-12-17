"""
Test: Sistema VIGENTE real 2024 (sin límite de 8%)
Para comparar con el escenario hipotético de 8% límite
"""

from engine.procesar_diputados_v2 import procesar_diputados_v2

print("="*80)
print("SISTEMA VIGENTE 2024 (sin límite de sobrerrepresentación)")
print("="*80)

resultado = procesar_diputados_v2(
    path_parquet="data/computos_diputados_2024.parquet",
    anio=2024,
    path_siglado="data/siglado-diputados-2024.csv",
    max_seats=500,
    sistema="mixto",
    mr_seats=None,  # Deja que el sistema calcule del siglado
    rp_seats=200,   # 200 RP fijos
    pm_seats=0,     # Sin PM
    umbral=0.03,
    max_seats_per_party=300,  # Límite constitucional de 300
    sobrerrepresentacion=None,  # ← SIN límite % (solo tope absoluto de 300)
    aplicar_topes=True,
    quota_method="hare",
    divisor_method=None,
    usar_coaliciones=True,  # Usar votos reales de coalición
    votos_redistribuidos=None,
    print_debug=False
)

if resultado and resultado.get('status') == 'success':
    partidos = resultado.get('resultados_partidos', [])
    
    morena = next((p for p in partidos if p['PARTIDO'] == 'MORENA'), None)
    
    print("\n" + "="*80)
    print("RESULTADO SISTEMA VIGENTE:")
    print("="*80)
    
    if morena:
        morena_mr = morena.get('MR', 0)
        morena_rp = morena.get('RP', 0)
        morena_total = morena.get('TOTAL', 0)
        
        print(f"\nMORENA:")
        print(f"  MR: {morena_mr}")
        print(f"  RP: {morena_rp}")
        print(f"  TOTAL: {morena_total}")
        
        print(f"\n📊 Comparación:")
        print(f"  Sistema vigente (sin límite %):  {morena_total} escaños")
        print(f"  Con límite 8% (hipotético):      248 escaños")
        print(f"  Diferencia:                       {morena_total - 248} escaños")
        
        if morena_total == 300:
            print(f"\n✅ MORENA alcanza el tope absoluto de 300 escaños")
        elif morena_total > 248:
            print(f"\n⚠️ MORENA excede los 248 escaños que tendría con límite del 8%")
        else:
            print(f"\n🤔 MORENA obtiene menos de 248 escaños (inesperado)")
    else:
        print("❌ ERROR: No se encontró MORENA en los resultados")
else:
    print("❌ ERROR en el procesamiento")
    print(resultado)
