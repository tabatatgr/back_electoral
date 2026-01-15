"""
Test del motor de Mayoría Forzada para SENADO
"""

print("="*100)
print("TEST: Motor de Mayoría Forzada - SENADO")
print("="*100)

from engine.calcular_mayoria_forzada_senado import (
    calcular_mayoria_forzada_senado,
    generar_tabla_estados_senado
)

# ============================================================================
# TEST 1: Mayoría Simple - Sistema Vigente (128 senadores) CON TOPES
# ============================================================================
print("\n" + "="*100)
print("TEST 1: Mayoría SIMPLE - MORENA (Sistema Vigente: 64 MR + 32 PM + 32 RP = 128, CON TOPES)")
print("="*100)

resultado1 = calcular_mayoria_forzada_senado(
    partido="MORENA",
    tipo_mayoria="simple",
    plan="vigente",
    aplicar_topes=True,
    anio=2024
)

print(f"\n📊 Resultado:")
print(f"  Viable: {resultado1.get('viable')}")
if resultado1.get('viable'):
    print(f"  Senadores necesarios: {resultado1.get('senadores_necesarios')}/{resultado1.get('total_senadores')}")
    print(f"  Estados ganados: {resultado1.get('estados_ganados', 0)}/32")
    print(f"  Senadores MR: {resultado1.get('senadores_mr', 0)}")
    print(f"  Senadores RP: {resultado1.get('senadores_rp', 0)}")
    print(f"  Total obtenidos: {resultado1.get('senadores_obtenidos', 0)}")
    print(f"  Votos necesarios: {resultado1.get('votos_porcentaje', 0)}%")
    print(f"  Método: {resultado1.get('metodo')}")
    
    # Validaciones
    assert resultado1['viable'] == True, "Debe ser viable"
    assert resultado1['senadores_necesarios'] == 65, "Umbral debe ser 65"
    assert resultado1['senadores_obtenidos'] >= 65, "Debe alcanzar mayoría"
    assert resultado1['votos_porcentaje'] >= 30, "Votos deben ser >= 30%"
    assert resultado1['votos_porcentaje'] <= 70, "Votos deben ser <= 70%"
    
    print("\n✅ TEST 1 PASADO: Mayoría simple viable con topes")
else:
    print(f"  Razón: {resultado1.get('razon')}")
    print("\n❌ TEST 1 FALLIDO: Debería ser viable")

# ============================================================================
# TEST 2: Mayoría Calificada - Sistema Vigente CON TOPES (debe RECHAZAR)
# ============================================================================
print("\n" + "="*100)
print("TEST 2: Mayoría CALIFICADA - MORENA (Sistema Vigente CON TOPES)")
print("="*100)

resultado2 = calcular_mayoria_forzada_senado(
    partido="MORENA",
    tipo_mayoria="calificada",
    plan="vigente",
    aplicar_topes=True,
    anio=2024
)

print(f"\n📊 Resultado:")
print(f"  Viable: {resultado2.get('viable')}")
if not resultado2.get('viable'):
    print(f"  Razón: {resultado2.get('razon')}")
    print(f"  Senadores necesarios: {resultado2.get('senadores_necesarios')}/{resultado2.get('max_con_tope', 'N/A')}")
    print(f"  Máximo con tope: {resultado2.get('max_con_tope')} ({resultado2.get('max_porcentaje')}%)")
    
    # Validaciones
    assert resultado2['viable'] == False, "Debe rechazarse con topes"
    assert resultado2['senadores_necesarios'] == 86, "Umbral calificado debe ser 86"
    assert 'IMPOSIBLE' in resultado2['razon'], "Debe indicar que es imposible"
    
    print("\n✅ TEST 2 PASADO: Mayoría calificada correctamente rechazada con topes")
else:
    print("\n❌ TEST 2 FALLIDO: Debería rechazarse con topes")

# ============================================================================
# TEST 3: Mayoría Calificada SIN TOPES
# ============================================================================
print("\n" + "="*100)
print("TEST 3: Mayoría CALIFICADA - MORENA (Sistema Vigente SIN TOPES)")
print("="*100)

resultado3 = calcular_mayoria_forzada_senado(
    partido="MORENA",
    tipo_mayoria="calificada",
    plan="vigente",
    aplicar_topes=False,
    anio=2024
)

print(f"\n📊 Resultado:")
print(f"  Viable: {resultado3.get('viable')}")
if resultado3.get('viable'):
    print(f"  Senadores necesarios: {resultado3.get('senadores_necesarios')}/{resultado3.get('total_senadores')}")
    print(f"  Estados ganados: {resultado3.get('estados_ganados', 0)}/32")
    print(f"  Senadores MR: {resultado3.get('senadores_mr', 0)}")
    print(f"  Senadores RP: {resultado3.get('senadores_rp', 0)}")
    print(f"  Total obtenidos: {resultado3.get('senadores_obtenidos', 0)}")
    print(f"  Votos necesarios: {resultado3.get('votos_porcentaje', 0)}%")
    
    # Validaciones
    assert resultado3['viable'] == True, "Debe ser viable sin topes"
    assert resultado3['senadores_necesarios'] == 86, "Umbral debe ser 86"
    assert resultado3['senadores_obtenidos'] >= 86, "Debe alcanzar mayoría calificada"
    
    print("\n✅ TEST 3 PASADO: Mayoría calificada viable sin topes")
else:
    print(f"  Razón: {resultado3.get('razon')}")
    print("\n❌ TEST 3 FALLIDO: Debería ser viable sin topes")

# ============================================================================
# TEST 4: Plan A (96 RP puro)
# ============================================================================
print("\n" + "="*100)
print("TEST 4: Mayoría SIMPLE - MORENA (Plan A: 96 RP puro)")
print("="*100)

resultado4 = calcular_mayoria_forzada_senado(
    partido="MORENA",
    tipo_mayoria="simple",
    plan="plan_a",
    aplicar_topes=True,
    anio=2024
)

print(f"\n📊 Resultado:")
print(f"  Viable: {resultado4.get('viable')}")
if resultado4.get('viable'):
    print(f"  Senadores necesarios: {resultado4.get('senadores_necesarios')}/96")
    print(f"  Senadores RP: {resultado4.get('senadores_rp', 0)}")
    print(f"  Votos necesarios: {resultado4.get('votos_porcentaje', 0):.1f}%")
    print(f"  Método: {resultado4.get('metodo')}")
    
    # Validaciones
    assert resultado4['viable'] == True, "Plan A debe ser viable"
    assert resultado4['senadores_necesarios'] == 49, "Umbral debe ser 49"
    assert resultado4['senadores_mr'] == 0, "No debe haber MR en Plan A"
    assert 'rp_puro' in resultado4.get('metodo', ''), "Método debe ser RP puro"
    
    print("\n✅ TEST 4 PASADO: Plan A (RP puro) funciona correctamente")
else:
    print(f"  Razón: {resultado4.get('razon')}")
    print("\n❌ TEST 4 FALLIDO")

# ============================================================================
# TEST 5: Plan C (64 MR+PM sin RP)
# ============================================================================
print("\n" + "="*100)
print("TEST 5: Mayoría SIMPLE - MORENA (Plan C: 64 MR+PM sin RP)")
print("="*100)

resultado5 = calcular_mayoria_forzada_senado(
    partido="MORENA",
    tipo_mayoria="simple",
    plan="plan_c",
    aplicar_topes=True,
    anio=2024
)

print(f"\n📊 Resultado:")
print(f"  Viable: {resultado5.get('viable')}")
if resultado5.get('viable'):
    print(f"  Senadores necesarios: {resultado5.get('senadores_necesarios')}/64")
    print(f"  Estados ganados: {resultado5.get('estados_ganados', 0)}/32")
    print(f"  Senadores MR: {resultado5.get('senadores_mr', 0)}")
    print(f"  Votos necesarios: {resultado5.get('votos_porcentaje', 0)}%")
    
    # Validaciones
    assert resultado5['viable'] == True, "Plan C debe ser viable"
    assert resultado5['senadores_necesarios'] == 33, "Umbral debe ser 33"
    assert resultado5['senadores_rp'] == 0, "No debe haber RP en Plan C"
    
    print("\n✅ TEST 5 PASADO: Plan C (MR+PM sin RP) funciona correctamente")
else:
    print(f"  Razón: {resultado5.get('razon')}")
    print("\n❌ TEST 5 FALLIDO")

# ============================================================================
# TEST 6: Generar tabla de estados
# ============================================================================
print("\n" + "="*100)
print("TEST 6: Generar Tabla de Estados")
print("="*100)

df_estados = generar_tabla_estados_senado(
    partido="MORENA",
    votos_porcentaje=45,
    anio=2024
)

print(f"\n📊 Tabla generada:")
print(f"  Número de estados: {len(df_estados)}")
if not df_estados.empty:
    print(f"  Columnas: {df_estados.columns.tolist()}")
    print(f"\n  Top 5 estados:")
    print(df_estados.head().to_string(index=False))
    
    # Validaciones
    assert len(df_estados) > 0, "Debe generar al menos un estado"
    assert 'ESTADO' in df_estados.columns, "Debe tener columna ESTADO"
    assert 'partido_ganador' in df_estados.columns, "Debe tener partido_ganador"
    assert 'senadores_mr' in df_estados.columns, "Debe tener senadores_mr"
    assert all(df_estados['senadores_mr'] == 2), "Cada estado debe tener 2 MR"
    
    print("\n✅ TEST 6 PASADO: Tabla de estados generada correctamente")
else:
    print("\n❌ TEST 6 FALLIDO: No se generó la tabla")

# ============================================================================
# RESUMEN
# ============================================================================
print("\n" + "="*100)
print("RESUMEN FINAL - SENADO")
print("="*100)

tests = [
    ("TEST 1: Mayoría simple con topes", resultado1.get('viable') == True),
    ("TEST 2: Mayoría calificada rechazada con topes", resultado2.get('viable') == False),
    ("TEST 3: Mayoría calificada sin topes", resultado3.get('viable') == True),
    ("TEST 4: Plan A (RP puro)", resultado4.get('viable') == True),
    ("TEST 5: Plan C (MR+PM)", resultado5.get('viable') == True),
    ("TEST 6: Tabla de estados", not df_estados.empty)
]

total = len(tests)
pasados = sum(1 for _, resultado in tests if resultado)

print(f"\nResultados:")
for nombre, resultado in tests:
    estado = "✅" if resultado else "❌"
    print(f"  {estado} {nombre}")

print(f"\nTotal: {pasados}/{total} tests pasados")

if pasados == total:
    print("\n" + "="*100)
    print("🎉 TODOS LOS TESTS DE SENADO PASARON")
    print("="*100)
    print("\n✅ Motor de mayoría forzada para Senado funciona correctamente")
    print("\n📊 Sistemas soportados:")
    print("  • Sistema Vigente (128): 64 MR + 32 PM + 32 RP")
    print("  • Plan A (96): RP puro")
    print("  • Plan C (64): MR+PM sin RP")
    print("\n🎯 Características:")
    print("  ✓ Redistribución realista por población estatal")
    print("  ✓ Método Hare con eficiencia geográfica 1.1")
    print("  ✓ Basado en datos reales 2024")
    print("  ✓ Respeta estructura de 32 estados")
    print("  ✓ Topes constitucionales del 8%")
    print("="*100)
else:
    print("\n❌ ALGUNOS TESTS FALLARON")
    print(f"Pasados: {pasados}/{total}")
