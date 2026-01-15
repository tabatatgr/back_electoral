"""
Test simple de la lógica de detección de mayorías
"""

print("="*100)
print("TEST: Lógica de Detección de Mayorías")
print("="*100)

# Simular resultados
def detectar_mayorias(resultado_tot):
    """
    Detecta mayorías simple y calificada
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
# TEST 1: Mayoría Simple Individual
# ============================================================================
print("\n" + "="*100)
print("TEST 1: Mayoría Simple Individual (MORENA)")
print("="*100)

resultado_test1 = {
    "MORENA": 210,
    "PAN": 80,
    "PRI": 60,
    "MC": 30,
    "PVEM": 15,
    "PT": 5
}

mayorias1 = detectar_mayorias(resultado_test1)
print(f"\nTotal escaños: {mayorias1['total_escanos']}")
print(f"\n📊 Mayoría Simple:")
print(f"  Umbral: {mayorias1['mayoria_simple']['umbral']}")
print(f"  Alcanzada: {mayorias1['mayoria_simple']['alcanzada']}")
print(f"  Partido: {mayorias1['mayoria_simple']['partido']}")
print(f"  Escaños: {mayorias1['mayoria_simple']['escanos']}")
print(f"  Es coalición: {mayorias1['mayoria_simple']['es_coalicion']}")

print(f"\n🏛️  Mayoría Calificada:")
print(f"  Umbral: {mayorias1['mayoria_calificada']['umbral']}")
print(f"  Alcanzada: {mayorias1['mayoria_calificada']['alcanzada']}")
print(f"  Partido: {mayorias1['mayoria_calificada']['partido']}")

print("\n✅ TEST 1: MORENA tiene mayoría simple (210 > 201) pero NO calificada (210 < 267)")

# ============================================================================
# TEST 2: Mayoría Calificada Individual
# ============================================================================
print("\n" + "="*100)
print("TEST 2: Mayoría Calificada Individual (MORENA)")
print("="*100)

resultado_test2 = {
    "MORENA": 270,
    "PAN": 60,
    "PRI": 40,
    "MC": 20,
    "PVEM": 7,
    "PT": 3
}

mayorias2 = detectar_mayorias(resultado_test2)
print(f"\nTotal escaños: {mayorias2['total_escanos']}")
print(f"\n📊 Mayoría Simple:")
print(f"  Alcanzada: {mayorias2['mayoria_simple']['alcanzada']}")
print(f"  Partido: {mayorias2['mayoria_simple']['partido']}")
print(f"  Escaños: {mayorias2['mayoria_simple']['escanos']}")

print(f"\n🏛️  Mayoría Calificada:")
print(f"  Umbral: {mayorias2['mayoria_calificada']['umbral']}")
print(f"  Alcanzada: {mayorias2['mayoria_calificada']['alcanzada']}")
print(f"  Partido: {mayorias2['mayoria_calificada']['partido']}")
print(f"  Escaños: {mayorias2['mayoria_calificada']['escanos']}")

print("\n✅ TEST 2: MORENA tiene mayoría calificada (270 ≥ 267)")

# ============================================================================
# TEST 3: Mayoría Simple SOLO con Coalición
# ============================================================================
print("\n" + "="*100)
print("TEST 3: Mayoría Simple SOLO con Coalición")
print("="*100)

resultado_test3 = {
    "MORENA": 165,
    "PT": 20,
    "PVEM": 25,
    "PAN": 90,
    "PRI": 60,
    "MC": 30,
    "PRD": 10
}

mayorias3 = detectar_mayorias(resultado_test3)
print(f"\nPartidos individuales:")
print(f"  MORENA: {resultado_test3['MORENA']} (mayoría: {resultado_test3['MORENA']} > 200)")
print(f"  PAN: {resultado_test3['PAN']}")
print(f"  Coalición MORENA+PT+PVEM: {resultado_test3['MORENA'] + resultado_test3['PT'] + resultado_test3['PVEM']}")

print(f"\n📊 Mayoría Simple:")
print(f"  Alcanzada: {mayorias3['mayoria_simple']['alcanzada']}")
print(f"  Partido/Coalición: {mayorias3['mayoria_simple']['partido']}")
print(f"  Escaños: {mayorias3['mayoria_simple']['escanos']}")
print(f"  Es coalición: {mayorias3['mayoria_simple']['es_coalicion']}")

print("\n✅ TEST 3: Solo con coalición hay mayoría simple (MORENA+PT+PVEM = 210 > 201)")

# ============================================================================
# TEST 4: Mayoría Calificada SOLO con Coalición  
# ============================================================================
print("\n" + "="*100)
print("TEST 4: Mayoría Calificada SOLO con Coalición")
print("="*100)

resultado_test4 = {
    "MORENA": 190,
    "PT": 30,
    "PVEM": 50,
    "PAN": 65,
    "PRI": 40,
    "MC": 20,
    "PRD": 5
}

mayorias4 = detectar_mayorias(resultado_test4)
print(f"\nPartidos individuales:")
print(f"  MORENA: {resultado_test4['MORENA']} (calificada: {resultado_test4['MORENA']} ≥ 267?)")
print(f"  Coalición MORENA+PT+PVEM: {resultado_test4['MORENA'] + resultado_test4['PT'] + resultado_test4['PVEM']}")

print(f"\n🏛️  Mayoría Calificada:")
print(f"  Umbral: {mayorias4['mayoria_calificada']['umbral']}")
print(f"  Alcanzada: {mayorias4['mayoria_calificada']['alcanzada']}")
print(f"  Partido/Coalición: {mayorias4['mayoria_calificada']['partido']}")
print(f"  Escaños: {mayorias4['mayoria_calificada']['escanos']}")
print(f"  Es coalición: {mayorias4['mayoria_calificada']['es_coalicion']}")

print("\n✅ TEST 4: Solo con coalición hay mayoría calificada (MORENA+PT+PVEM = 270 ≥ 267)")

# ============================================================================
# TEST 5: Sin Mayorías
# ============================================================================
print("\n" + "="*100)
print("TEST 5: Sin Mayorías (Congreso dividido)")
print("="*100)

resultado_test5 = {
    "MORENA": 150,
    "PAN": 100,
    "PRI": 80,
    "MC": 40,
    "PVEM": 20,
    "PT": 10
}

mayorias5 = detectar_mayorias(resultado_test5)
print(f"\nPartidos:")
for partido, escanos in sorted(resultado_test5.items(), key=lambda x: x[1], reverse=True):
    print(f"  {partido}: {escanos}")

print(f"\n📊 Mayoría Simple:")
print(f"  Alcanzada: {mayorias5['mayoria_simple']['alcanzada']}")
print(f"  Partido: {mayorias5['mayoria_simple']['partido']}")

print(f"\n🏛️  Mayoría Calificada:")
print(f"  Alcanzada: {mayorias5['mayoria_calificada']['alcanzada']}")
print(f"  Partido: {mayorias5['mayoria_calificada']['partido']}")

print("\n✅ TEST 5: Congreso dividido - No hay mayoría simple ni calificada")

# ============================================================================
# RESUMEN
# ============================================================================
print("\n" + "="*100)
print("RESUMEN FINAL")
print("="*100)

tests = [
    ("TEST 1: Mayoría simple individual", mayorias1['mayoria_simple']['alcanzada'] and not mayorias1['mayoria_simple']['es_coalicion']),
    ("TEST 2: Mayoría calificada individual", mayorias2['mayoria_calificada']['alcanzada'] and not mayorias2['mayoria_calificada']['es_coalicion']),
    ("TEST 3: Mayoría simple solo coalición", mayorias3['mayoria_simple']['alcanzada'] and mayorias3['mayoria_simple']['es_coalicion']),
    ("TEST 4: Mayoría calificada solo coalición", mayorias4['mayoria_calificada']['alcanzada'] and mayorias4['mayoria_calificada']['es_coalicion']),
    ("TEST 5: Sin mayorías", not mayorias5['mayoria_simple']['alcanzada'] and not mayorias5['mayoria_calificada']['alcanzada'])
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
    print("🎉 TODOS LOS TESTS PASARON")
    print("="*100)
    print("\n✅ La lógica de detección de mayorías funciona correctamente")
    print("✅ Detecta mayoría simple (>50%)")
    print("✅ Detecta mayoría calificada (≥66.67%)")
    print("✅ Distingue entre partido individual y coalición")
    print("✅ Identifica cuando NO hay mayoría")
    print("\n📝 Formato de respuesta del endpoint:")
    print("""
{
  "mayorias": {
    "total_escanos": 400,
    "mayoria_simple": {
      "umbral": 201,
      "alcanzada": true,
      "partido": "MORENA" o "MORENA+PT+PVEM",
      "escanos": 210,
      "es_coalicion": false o true
    },
    "mayoria_calificada": {
      "umbral": 267,
      "alcanzada": false,
      "partido": null,
      "escanos": 0,
      "es_coalicion": false
    }
  }
}
    """)
    print("🎨 El frontend puede usar esto para:")
    print("  - Colorear resultados según mayoría alcanzada")
    print("  - Mostrar badges/indicadores (🟢 Mayoría Simple, 🔵 Mayoría Calificada)")
    print("  - Alertar cuando solo hay mayoría con coalición (⚠️)")
    print("  - Indicar congreso dividido cuando no hay mayoría (⚪)")
    print("="*100)
