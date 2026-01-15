"""
Test de detección de mayorías para SENADO
"""

print("="*100)
print("TEST: Detección de Mayorías - SENADO")
print("="*100)

# Simular resultados del Senado
def detectar_mayorias_senado(resultado_tot):
    """
    Detecta mayorías simple y calificada en Senado
    """
    total_escanos = sum(resultado_tot.values())
    mayoria_simple_umbral = total_escanos / 2
    mayoria_calificada_umbral = (total_escanos * 2) / 3
    
    mayorias_info = {
        "mayoria_simple": {"partido": None, "escanos": 0, "coalicion": False},
        "mayoria_calificada": {"partido": None, "escanos": 0, "coalicion": False}
    }
    
    # Revisar partidos individuales
    partidos_ordenados = sorted(resultado_tot.items(), key=lambda x: x[1], reverse=True)
    
    for partido, escanos in partidos_ordenados:
        if escanos >= mayoria_calificada_umbral and mayorias_info["mayoria_calificada"]["partido"] is None:
            mayorias_info["mayoria_calificada"]["partido"] = partido
            mayorias_info["mayoria_calificada"]["escanos"] = escanos
            mayorias_info["mayoria_calificada"]["coalicion"] = False
        
        if escanos > mayoria_simple_umbral and mayorias_info["mayoria_simple"]["partido"] is None:
            mayorias_info["mayoria_simple"]["partido"] = partido
            mayorias_info["mayoria_simple"]["escanos"] = escanos
            mayorias_info["mayoria_simple"]["coalicion"] = False
    
    # Coaliciones
    coaliciones_posibles = [
        {"nombre": "MORENA+PT+PVEM", "partidos": ["MORENA", "PT", "PVEM"]},
        {"nombre": "PAN+PRI+PRD", "partidos": ["PAN", "PRI", "PRD"]},
    ]
    
    for coalicion in coaliciones_posibles:
        escanos_coalicion = sum(resultado_tot.get(p, 0) for p in coalicion["partidos"])
        
        if (escanos_coalicion >= mayoria_calificada_umbral and 
            mayorias_info["mayoria_calificada"]["partido"] is None):
            mayorias_info["mayoria_calificada"]["partido"] = coalicion["nombre"]
            mayorias_info["mayoria_calificada"]["escanos"] = escanos_coalicion
            mayorias_info["mayoria_calificada"]["coalicion"] = True
        
        if (escanos_coalicion > mayoria_simple_umbral and 
            mayorias_info["mayoria_simple"]["partido"] is None):
            mayorias_info["mayoria_simple"]["partido"] = coalicion["nombre"]
            mayorias_info["mayoria_simple"]["escanos"] = escanos_coalicion
            mayorias_info["mayoria_simple"]["coalicion"] = True
    
    return {
        "total_escanos": total_escanos,
        "mayoria_simple": {
            "umbral": int(mayoria_simple_umbral) + 1,
            "alcanzada": mayorias_info["mayoria_simple"]["partido"] is not None,
            "partido": mayorias_info["mayoria_simple"]["partido"],
            "escanos": mayorias_info["mayoria_simple"]["escanos"],
            "es_coalicion": mayorias_info["mayoria_simple"]["coalicion"]
        },
        "mayoria_calificada": {
            "umbral": int(mayoria_calificada_umbral) + 1,
            "alcanzada": mayorias_info["mayoria_calificada"]["partido"] is not None,
            "partido": mayorias_info["mayoria_calificada"]["partido"],
            "escanos": mayorias_info["mayoria_calificada"]["escanos"],
            "es_coalicion": mayorias_info["mayoria_calificada"]["coalicion"]
        }
    }

# ============================================================================
# TEST 1: Sistema Vigente (128 escaños) - Mayoría Simple Individual
# ============================================================================
print("\n" + "="*100)
print("TEST 1: Sistema Vigente (128 escaños) - Mayoría Simple Individual")
print("="*100)

resultado_test1 = {
    "MORENA": 70,  # Mayoría simple (>64)
    "PAN": 25,
    "PRI": 20,
    "MC": 8,
    "PVEM": 3,
    "PT": 2
}

mayorias1 = detectar_mayorias_senado(resultado_test1)
print(f"\n📊 Composición:")
for partido, escanos in sorted(resultado_test1.items(), key=lambda x: x[1], reverse=True):
    print(f"  {partido}: {escanos} senadores")

print(f"\n🏛️  Total escaños: {mayorias1['total_escanos']}")
print(f"\n✓ Mayoría Simple:")
print(f"  Umbral: >{mayorias1['mayoria_simple']['umbral']-1} (necesita {mayorias1['mayoria_simple']['umbral']} para mayoría)")
print(f"  Alcanzada: {mayorias1['mayoria_simple']['alcanzada']}")
print(f"  Partido: {mayorias1['mayoria_simple']['partido']}")
print(f"  Escaños: {mayorias1['mayoria_simple']['escanos']}")
print(f"  Es coalición: {mayorias1['mayoria_simple']['es_coalicion']}")

print(f"\n✓ Mayoría Calificada:")
print(f"  Umbral: ≥{mayorias1['mayoria_calificada']['umbral']} (2/3)")
print(f"  Alcanzada: {mayorias1['mayoria_calificada']['alcanzada']}")

assert mayorias1['total_escanos'] == 128, "Total debe ser 128"
assert mayorias1['mayoria_simple']['umbral'] == 65, "Umbral simple debe ser 65"
assert mayorias1['mayoria_calificada']['umbral'] == 86, "Umbral calificado debe ser 86"
assert mayorias1['mayoria_simple']['alcanzada'] == True, "MORENA debe tener mayoría simple"
assert mayorias1['mayoria_calificada']['alcanzada'] == False, "No debe haber mayoría calificada"
print("\n✅ TEST 1 PASADO: MORENA tiene mayoría simple (70 > 64) pero NO calificada (70 < 86)")

# ============================================================================
# TEST 2: Sistema Vigente - Mayoría Calificada Individual
# ============================================================================
print("\n" + "="*100)
print("TEST 2: Sistema Vigente - Mayoría Calificada Individual")
print("="*100)

resultado_test2 = {
    "MORENA": 90,  # Mayoría calificada (≥86)
    "PAN": 20,
    "PRI": 10,
    "MC": 5,
    "PVEM": 2,
    "PT": 1
}

mayorias2 = detectar_mayorias_senado(resultado_test2)
print(f"\n📊 Composición:")
for partido, escanos in sorted(resultado_test2.items(), key=lambda x: x[1], reverse=True):
    print(f"  {partido}: {escanos} senadores")

print(f"\n✓ Mayoría Calificada:")
print(f"  Umbral: ≥{mayorias2['mayoria_calificada']['umbral']}")
print(f"  Alcanzada: {mayorias2['mayoria_calificada']['alcanzada']}")
print(f"  Partido: {mayorias2['mayoria_calificada']['partido']}")
print(f"  Escaños: {mayorias2['mayoria_calificada']['escanos']}")

assert mayorias2['mayoria_calificada']['alcanzada'] == True, "MORENA debe tener mayoría calificada"
assert mayorias2['mayoria_calificada']['partido'] == "MORENA", "Partido debe ser MORENA"
assert mayorias2['mayoria_calificada']['escanos'] == 90, "Escaños deben ser 90"
print("\n✅ TEST 2 PASADO: MORENA tiene mayoría calificada (90 ≥ 86)")

# ============================================================================
# TEST 3: Plan A (96 escaños RP puro) - Mayoría Simple con Coalición
# ============================================================================
print("\n" + "="*100)
print("TEST 3: Plan A (96 escaños RP puro) - Mayoría Simple con Coalición")
print("="*100)

resultado_test3 = {
    "MORENA": 40,
    "PT": 5,
    "PVEM": 8,  # Coalición: 40+5+8 = 53 > 48
    "PAN": 22,
    "PRI": 15,
    "MC": 6
}

mayorias3 = detectar_mayorias_senado(resultado_test3)
print(f"\n📊 Composición (Plan A - 96 escaños):")
for partido, escanos in sorted(resultado_test3.items(), key=lambda x: x[1], reverse=True):
    print(f"  {partido}: {escanos} senadores")

print(f"\nCoalición MORENA+PT+PVEM: {resultado_test3['MORENA'] + resultado_test3['PT'] + resultado_test3['PVEM']} senadores")

print(f"\n✓ Mayoría Simple:")
print(f"  Umbral: >{mayorias3['mayoria_simple']['umbral']-1}")
print(f"  Alcanzada: {mayorias3['mayoria_simple']['alcanzada']}")
print(f"  Partido/Coalición: {mayorias3['mayoria_simple']['partido']}")
print(f"  Escaños: {mayorias3['mayoria_simple']['escanos']}")
print(f"  Es coalición: {mayorias3['mayoria_simple']['es_coalicion']}")

assert mayorias3['total_escanos'] == 96, "Total debe ser 96 (Plan A)"
assert mayorias3['mayoria_simple']['umbral'] == 49, "Umbral simple debe ser 49"
assert mayorias3['mayoria_simple']['alcanzada'] == True, "Debe haber mayoría con coalición"
assert mayorias3['mayoria_simple']['es_coalicion'] == True, "Debe ser coalición"
assert mayorias3['mayoria_simple']['partido'] == "MORENA+PT+PVEM", "Debe ser MORENA+PT+PVEM"
print("\n✅ TEST 3 PASADO: Mayoría simple SOLO con coalición MORENA+PT+PVEM (53 > 48)")

# ============================================================================
# TEST 4: Plan C (64 escaños MR+PM) - Mayoría Calificada con Coalición
# ============================================================================
print("\n" + "="*100)
print("TEST 4: Plan C (64 escaños MR+PM) - Mayoría Calificada con Coalición")
print("="*100)

resultado_test4 = {
    "MORENA": 35,
    "PT": 5,
    "PVEM": 8,  # Coalición: 35+5+8 = 48 ≥ 43
    "PAN": 10,
    "PRI": 4,
    "MC": 2
}

mayorias4 = detectar_mayorias_senado(resultado_test4)
print(f"\n📊 Composición (Plan C - 64 escaños):")
for partido, escanos in sorted(resultado_test4.items(), key=lambda x: x[1], reverse=True):
    print(f"  {partido}: {escanos} senadores")

coalicion_escanos = resultado_test4['MORENA'] + resultado_test4['PT'] + resultado_test4['PVEM']
print(f"\nCoalición MORENA+PT+PVEM: {coalicion_escanos} senadores")

print(f"\n✓ Mayoría Calificada:")
print(f"  Umbral: ≥{mayorias4['mayoria_calificada']['umbral']}")
print(f"  Alcanzada: {mayorias4['mayoria_calificada']['alcanzada']}")
print(f"  Partido/Coalición: {mayorias4['mayoria_calificada']['partido']}")
print(f"  Escaños: {mayorias4['mayoria_calificada']['escanos']}")
print(f"  Es coalición: {mayorias4['mayoria_calificada']['es_coalicion']}")

assert mayorias4['total_escanos'] == 64, "Total debe ser 64 (Plan C)"
assert mayorias4['mayoria_calificada']['umbral'] == 43, "Umbral calificado debe ser 43"
assert mayorias4['mayoria_calificada']['alcanzada'] == True, "Debe haber mayoría calificada con coalición"
assert mayorias4['mayoria_calificada']['es_coalicion'] == True, "Debe ser coalición"
print("\n✅ TEST 4 PASADO: Mayoría calificada con coalición (48 ≥ 43)")

# ============================================================================
# TEST 5: Senado Dividido - Sin Mayorías
# ============================================================================
print("\n" + "="*100)
print("TEST 5: Senado Dividido - Sin Mayorías")
print("="*100)

resultado_test5 = {
    "MORENA": 40,
    "PAN": 35,
    "PRI": 25,
    "MC": 15,
    "PVEM": 8,
    "PT": 5
}

mayorias5 = detectar_mayorias_senado(resultado_test5)
print(f"\n📊 Composición:")
for partido, escanos in sorted(resultado_test5.items(), key=lambda x: x[1], reverse=True):
    print(f"  {partido}: {escanos} senadores")

print(f"\n✓ Mayoría Simple:")
print(f"  Alcanzada: {mayorias5['mayoria_simple']['alcanzada']}")
print(f"  Partido: {mayorias5['mayoria_simple']['partido']}")

print(f"\n✓ Mayoría Calificada:")
print(f"  Alcanzada: {mayorias5['mayoria_calificada']['alcanzada']}")
print(f"  Partido: {mayorias5['mayoria_calificada']['partido']}")

assert mayorias5['mayoria_simple']['alcanzada'] == False, "No debe haber mayoría simple"
assert mayorias5['mayoria_calificada']['alcanzada'] == False, "No debe haber mayoría calificada"
print("\n✅ TEST 5 PASADO: Senado dividido - No hay mayorías")

# ============================================================================
# RESUMEN
# ============================================================================
print("\n" + "="*100)
print("RESUMEN FINAL - SENADO")
print("="*100)

tests = [
    ("TEST 1: Mayoría simple individual (128 escaños)", True),
    ("TEST 2: Mayoría calificada individual (128 escaños)", True),
    ("TEST 3: Mayoría simple coalición (96 escaños Plan A)", True),
    ("TEST 4: Mayoría calificada coalición (64 escaños Plan C)", True),
    ("TEST 5: Sin mayorías", True)
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
    print("\n✅ Detección de mayorías funciona para SENADO")
    print("\n📊 Umbrales según tamaño de Senado:")
    print("  • Sistema Vigente (128 escaños):")
    print("    - Mayoría simple: >64 (50%)")
    print("    - Mayoría calificada: ≥86 (66.67%, 2/3)")
    print("\n  • Plan A - RP puro (96 escaños):")
    print("    - Mayoría simple: >48")
    print("    - Mayoría calificada: ≥64")
    print("\n  • Plan C - MR+PM (64 escaños):")
    print("    - Mayoría simple: >32")
    print("    - Mayoría calificada: ≥43")
    print("\n🎨 Frontend puede usar:")
    print("  - 🔵 Mayoría Calificada (2/3)")
    print("  - 🟢 Mayoría Simple (>50%)")
    print("  - ⚠️  Solo con coalición")
    print("  - ⚪ Senado dividido")
    print("="*100)
