"""
Comparación detallada: parámetros que usa la API vs el script generador de CSVs
"""

print("="*80)
print("COMPARACIÓN DE PARÁMETROS")
print("="*80)
print()

print("SCRIPT GENERADOR DE CSVs (tmp_generate_escenarios_sin_topes.py):")
print("-" * 40)
print("""
procesar_diputados_v2(
    path_parquet=path_parquet,
    path_siglado=path_siglado,
    anio=anio,
    max_seats=escanos_totales,
    mr_seats=mr_escanos,
    rp_seats=rp_escanos,
    usar_coaliciones=coalicion['usar'],
    aplicar_topes=False
)
""")
print("Parámetros NO especificados (usan defaults):")
print("  - partidos_base: None (usa parties_for(anio))")
print("  - sistema: 'mixto' (default)")
print("  - pm_seats: None")
print("  - regla_electoral: None")
print("  - quota_method: 'hare' (DEFAULT)")
print("  - divisor_method: 'dhondt' (DEFAULT)")
print("  - umbral: None (usa 0.03 como default)")
print("  - max_seats_per_party: None")
print("  - sobrerrepresentacion: None")
print("  - votos_redistribuidos: None")
print("  - seed: None")
print("  - print_debug: False")
print()

print("=" * 80)
print("API (main.py procesar_diputados POST):")
print("-" * 40)
print("""
procesar_diputados_v2(
    path_parquet=path_parquet,
    anio=anio,
    path_siglado=path_siglado,
    max_seats=max_seats,
    sistema=sistema_final,
    mr_seats=mr_seats_final,
    rp_seats=rp_seats_final,
    pm_seats=pm_seats_final,
    umbral=umbral_final,
    max_seats_per_party=max_seats_per_party_final,
    sobrerrepresentacion=sobrerrepresentacion,
    aplicar_topes=aplicar_topes,
    quota_method=quota_method_final,
    divisor_method=divisor_method_final,
    usar_coaliciones=usar_coaliciones,
    votos_redistribuidos=votos_redistribuidos,
    print_debug=True
)
""")
print("Parámetros explícitos que PUEDEN diferir:")
print("  - sistema: explícito (recibido del frontend)")
print("  - pm_seats: explícito (default 0)")
print("  - umbral: explícito (default 0.03)")
print("  - max_seats_per_party: explícito (puede ser None o un valor)")
print("  - sobrerrepresentacion: explícito (puede ser None o 8.0)")
print("  - quota_method: explícito según reparto_mode")
print("  - divisor_method: explícito según reparto_mode")
print("  - votos_redistribuidos: explícito (puede tener datos)")
print("  - print_debug: True")
print()

print("=" * 80)
print("🔍 POSIBLES CAUSAS DE LA DISCREPANCIA +1 RP")
print("=" * 80)
print()
print("1. SEED para desempates en RP:")
print("   - Script CSV: seed=None → desempate puede variar")
print("   - API: seed=None también, PERO puede haber diferencia")
print("      en el orden de ejecución o estado del RNG")
print()
print("2. QUOTA_METHOD / DIVISOR_METHOD:")
print("   - Script CSV: usa defaults ('hare' y 'dhondt')")
print("   - API: usa defaults PERO puede haber sido cambiado")
print("      por el parámetro reparto_mode del frontend")
print()
print("3. VOTOS_REDISTRIBUIDOS:")
print("   - Script CSV: None")
print("   - API: puede tener datos si se aplicó redistribución")
print()
print("4. UMBRAL:")
print("   - Script CSV: None → usa 0.03 default")
print("   - API: explícito 0.03")
print("   (probablemente igual, pero verificar)")
print()
print("5. MAX_SEATS_PER_PARTY:")
print("   - Script CSV: None")
print("   - API: puede tener un valor si el frontend lo envía")
print()
print("6. SOBRERREPRESENTACION:")
print("   - Script CSV: None")
print("   - API: puede ser 8.0 si aplicar_topes=True")
print("   ⚠️ IMPORTANTE: en las pruebas API, aplicar_topes=False")
print("      pero sobrerrepresentacion aún puede estar seteado!")
print()

print("=" * 80)
print("🎯 DIAGNÓSTICO FINAL")
print("=" * 80)
print()
print("El motor produce resultados CORRECTOS cuando se llama directamente.")
print("La API tiene +1 RP en MORENA (249 vs 248 CON coal; 257 vs 256 SIN coal).")
print()
print("Hipótesis más probable:")
print("  La API está pasando parámetros adicionales que alteran ligeramente")
print("  la asignación RP, probablemente relacionados con:")
print("  - Desempates (seed diferente o ausente)")
print("  - Método de reparto (quota_method o divisor_method)")
print("  - Votos redistribuidos (si hay datos)")
print()
print("SIGUIENTE PASO:")
print("  Inspeccionar los logs del servidor cuando se llama a la API")
print("  para ver exactamente qué parámetros está recibiendo")
print("  procesar_diputados_v2")
print()
print("=" * 80)
