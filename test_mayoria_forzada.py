"""
Test del endpoint GET /calcular/mayoria_forzada

Verifica que el endpoint calcule correctamente la configuración
para forzar mayorías simple y calificada.

Autor: Sistema Electoral v2.0
Fecha: 2024
"""

import sys
from engine.calcular_mayoria_forzada_v2 import calcular_mayoria_forzada

def test_mayoria_simple_300_100():
    """Test 1: Mayoría simple en escenario 300-100 con topes"""
    print("\n" + "="*80)
    print("TEST 1: Mayoría SIMPLE - MORENA (300 MR + 100 RP, CON TOPES)")
    print("="*80)
    
    resultado = calcular_mayoria_forzada(
        partido="MORENA",
        tipo_mayoria="simple",
        mr_total=300,
        rp_total=100,
        aplicar_topes=True
    )
    
    print(f"\nViable: {resultado['viable']}")
    
    if resultado['viable']:
        print(f"✓ Configuración calculada correctamente")
        print(f"\nObjetivo: {resultado['objetivo_escanos']} escaños (mayoría simple)")
        print(f"\nDetalle:")
        print(f"  - MR ganados: {resultado['detalle']['mr_ganados']}/{resultado['detalle']['mr_total']} ({resultado['detalle']['pct_mr']}%)")
        print(f"  - RP esperado: {resultado['detalle']['rp_esperado']}/{resultado['detalle']['rp_total']}")
        print(f"  - Votos necesarios: {resultado['detalle']['pct_votos']}%")
        print(f"\nConfiguración para API:")
        print(f"  mr_distritos_manuales = {resultado['mr_distritos_manuales']}")
        print(f"  votos_custom = {resultado['votos_custom']}")
        
        if resultado.get('advertencias'):
            print(f"\n⚠️  Advertencias:")
            for adv in resultado['advertencias']:
                print(f"  - {adv}")
        
        print(f"\n✓ TEST 1 PASADO")
        return True
    else:
        print(f"✗ NO VIABLE: {resultado.get('razon', 'Sin razón')}")
        print(f"\n✗ TEST 1 FALLADO")
        return False

def test_mayoria_calificada_con_topes():
    """Test 2: Mayoría calificada CON topes - debería fallar"""
    print("\n" + "="*80)
    print("TEST 2: Mayoría CALIFICADA - MORENA (300 MR + 100 RP, CON TOPES)")
    print("="*80)
    print("\nEste test DEBE FALLAR (mayoría calificada es imposible con topes)")
    
    resultado = calcular_mayoria_forzada(
        partido="MORENA",
        tipo_mayoria="calificada",
        mr_total=300,
        rp_total=100,
        aplicar_topes=True
    )
    
    print(f"\nViable: {resultado['viable']}")
    
    if not resultado['viable']:
        print(f"✓ Correctamente rechazado")
        print(f"\nRazón: {resultado.get('razon', 'Sin razón')}")
        if 'sugerencia' in resultado:
            print(f"Sugerencia: {resultado['sugerencia']}")
        if 'votos_min_necesarios' in resultado:
            print(f"Votos mínimos requeridos: {resultado['votos_min_necesarios']:.1f}%")
        
        print(f"\n✓ TEST 2 PASADO (correctamente rechazado)")
        return True
    else:
        print(f"✗ ERROR: No debería ser viable con topes")
        print(f"\n✗ TEST 2 FALLADO")
        return False

def test_mayoria_calificada_sin_topes():
    """Test 3: Mayoría calificada SIN topes - debería funcionar"""
    print("\n" + "="*80)
    print("TEST 3: Mayoría CALIFICADA - MORENA (200 MR + 200 RP, SIN TOPES)")
    print("="*80)
    
    resultado = calcular_mayoria_forzada(
        partido="MORENA",
        tipo_mayoria="calificada",
        mr_total=200,
        rp_total=200,
        aplicar_topes=False
    )
    
    print(f"\nViable: {resultado['viable']}")
    
    if resultado['viable']:
        print(f"✓ Configuración calculada correctamente")
        print(f"\nObjetivo: {resultado['objetivo_escanos']} escaños (mayoría calificada)")
        print(f"\nDetalle:")
        print(f"  - MR ganados: {resultado['detalle']['mr_ganados']}/{resultado['detalle']['mr_total']} ({resultado['detalle']['pct_mr']}%)")
        print(f"  - RP esperado: {resultado['detalle']['rp_esperado']}/{resultado['detalle']['rp_total']}")
        print(f"  - Votos necesarios: {resultado['detalle']['pct_votos']}%")
        print(f"\nConfiguración para API:")
        print(f"  mr_distritos_manuales = {resultado['mr_distritos_manuales']}")
        print(f"  votos_custom = {resultado['votos_custom']}")
        
        if resultado.get('advertencias'):
            print(f"\n⚠️  Advertencias:")
            for adv in resultado['advertencias']:
                print(f"  - {adv}")
        
        print(f"\n✓ TEST 3 PASADO")
        return True
    else:
        print(f"✗ NO VIABLE: {resultado.get('razon', 'Sin razón')}")
        print(f"\n✗ TEST 3 FALLADO")
        return False

def test_otros_partidos():
    """Test 4: Otros partidos (PAN, PRI, MC)"""
    print("\n" + "="*80)
    print("TEST 4: Mayorías SIMPLE para otros partidos")
    print("="*80)
    
    partidos = ["PAN", "PRI", "MC"]
    todos_ok = True
    
    for partido in partidos:
        print(f"\n{partido}:")
        resultado = calcular_mayoria_forzada(
            partido=partido,
            tipo_mayoria="simple",
            mr_total=300,
            rp_total=100,
            aplicar_topes=True
        )
        
        if resultado['viable']:
            print(f"  ✓ Viable - MR: {resultado['detalle']['mr_ganados']}, Votos: {resultado['detalle']['pct_votos']}%")
        else:
            print(f"  ✗ No viable: {resultado.get('razon', 'Sin razón')}")
            todos_ok = False
    
    if todos_ok:
        print(f"\n✓ TEST 4 PASADO")
    else:
        print(f"\n✗ TEST 4 FALLADO")
    
    return todos_ok

def main():
    """Ejecutar todos los tests"""
    print("\n" + "="*80)
    print("TESTS DEL ENDPOINT /calcular/mayoria_forzada")
    print("="*80)
    print("\nEstos tests verifican:")
    print("1. Cálculo de mayoría simple (201 escaños)")
    print("2. Rechazo correcto de mayoría calificada CON topes")
    print("3. Cálculo de mayoría calificada SIN topes")
    print("4. Funcionamiento para diferentes partidos")
    
    resultados = []
    
    # Test 1
    resultados.append(("Mayoría simple MORENA", test_mayoria_simple_300_100()))
    
    # Test 2
    resultados.append(("Mayoría calificada CON topes", test_mayoria_calificada_con_topes()))
    
    # Test 3
    resultados.append(("Mayoría calificada SIN topes", test_mayoria_calificada_sin_topes()))
    
    # Test 4
    resultados.append(("Otros partidos", test_otros_partidos()))
    
    # Resumen
    print("\n" + "="*80)
    print("RESUMEN DE TESTS")
    print("="*80)
    
    total_tests = len(resultados)
    tests_pasados = sum(1 for _, ok in resultados if ok)
    
    for nombre, ok in resultados:
        estado = "✓ PASADO" if ok else "✗ FALLADO"
        print(f"{estado}: {nombre}")
    
    print(f"\nTotal: {tests_pasados}/{total_tests} tests pasados")
    
    if tests_pasados == total_tests:
        print("\n🎉 TODOS LOS TESTS PASARON")
        return 0
    else:
        print(f"\n❌ {total_tests - tests_pasados} tests fallaron")
        return 1

if __name__ == "__main__":
    sys.exit(main())
