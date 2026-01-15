"""
Test directo del código de distribución por estados (sin servidor HTTP)

Este test verifica:
1. Cálculo de distribución estado por estado
2. Validación de suma por estado
3. Conversión de distribución por estado a totales

Autor: Sistema Electoral v2.0
Fecha: 2024
"""

import json
import sys
from redistritacion.modulos.reparto_distritos import repartir_distritos_hare
from redistritacion.modulos.distritacion import cargar_secciones_ine
from engine.calcular_eficiencia_real import calcular_eficiencia_partidos

def test_calcular_distribucion_estados():
    """Test 1: Calcular distribución geográfica por estado"""
    print("\n" + "="*80)
    print("TEST 1: Calcular distribución geográfica por estado")
    print("="*80)
    
    try:
        anio = 2024
        n_distritos = 300
        
        # 1. Calcular distribución de distritos por estado (método Hare)
        print(f"\n1. Cargando secciones del INE...")
        secciones_df = cargar_secciones_ine()
        poblacion_estados = secciones_df.groupby("ENTIDAD")["POBTOT"].sum().to_dict()
        
        print(f"2. Repartiendo {n_distritos} distritos entre {len(poblacion_estados)} estados...")
        distribucion_hare = repartir_distritos_hare(poblacion_estados, n_distritos, piso_constitucional=2)
        
        # Verificar suma
        suma_distritos = sum(distribucion_hare.values())
        print(f"   Total distritos repartidos: {suma_distritos} (esperado: {n_distritos})")
        
        if suma_distritos == n_distritos:
            print("   ✓ Suma correcta")
        else:
            print(f"   ✗ ERROR: Suma incorrecta ({suma_distritos} != {n_distritos})")
            return False
        
        # 2. Calcular eficiencias históricas
        print(f"\n3. Calculando eficiencias históricas para {anio}...")
        eficiencias = calcular_eficiencia_partidos(anio, usar_coaliciones=True)
        print(f"   Eficiencias: {eficiencias}")
        
        # 3. Simular votos redistribuidos
        votos_dict = {
            "MORENA": 38.0,
            "PAN": 22.0,
            "PRI": 18.0,
            "MC": 12.0,
            "PVEM": 6.0,
            "PT": 4.0
        }
        
        print(f"\n4. Calculando votos efectivos (votos × eficiencia)...")
        votos_efectivos = {}
        total_efectivo = 0
        for partido, pct in votos_dict.items():
            if partido in eficiencias:
                efectivo = pct * eficiencias[partido]
                votos_efectivos[partido] = efectivo
                total_efectivo += efectivo
        
        # Normalizar a porcentajes
        votos_efectivos_pct = {p: (v / total_efectivo * 100) for p, v in votos_efectivos.items()}
        print(f"   Votos efectivos (%):")
        for p, v in sorted(votos_efectivos_pct.items(), key=lambda x: x[1], reverse=True):
            print(f"      {p}: {v:.2f}%")
        
        # 4. Distribuir distritos MR por estado usando votos efectivos
        print(f"\n5. Distribuyendo MR por estado según votos efectivos...")
        distribucion_estados = []
        totales_partidos = {p: 0 for p in votos_efectivos_pct.keys()}
        
        nombres_estados = {
            1: "Aguascalientes", 2: "Baja California", 3: "Baja California Sur",
            4: "Campeche", 5: "Coahuila", 6: "Colima", 7: "Chiapas", 8: "Chihuahua",
            9: "Ciudad de México", 10: "Durango", 11: "Guanajuato", 12: "Guerrero",
            13: "Hidalgo", 14: "Jalisco", 15: "México", 16: "Michoacán",
            17: "Morelos", 18: "Nayarit", 19: "Nuevo León", 20: "Oaxaca",
            21: "Puebla", 22: "Querétaro", 23: "Quintana Roo", 24: "San Luis Potosí",
            25: "Sinaloa", 26: "Sonora", 27: "Tabasco", 28: "Tamaulipas",
            29: "Tlaxcala", 30: "Veracruz", 31: "Yucatán", 32: "Zacatecas"
        }
        
        for estado_id in sorted(distribucion_hare.keys()):
            distritos_estado = distribucion_hare[estado_id]
            
            # Distribuir distritos del estado proporcionalmente a votos efectivos
            distribucion_partidos = {}
            asignados = 0
            
            # Primera vuelta: asignación proporcional
            for partido, pct in sorted(votos_efectivos_pct.items(), key=lambda x: x[1], reverse=True):
                cuota = (pct / 100) * distritos_estado
                asignacion = int(cuota)
                distribucion_partidos[partido] = asignacion
                asignados += asignacion
            
            # Segunda vuelta: residuos
            restantes = distritos_estado - asignados
            if restantes > 0:
                residuos = []
                for partido, pct in votos_efectivos_pct.items():
                    cuota = (pct / 100) * distritos_estado
                    residuo = cuota - distribucion_partidos[partido]
                    residuos.append((partido, residuo))
                
                residuos.sort(key=lambda x: x[1], reverse=True)
                
                for i in range(restantes):
                    partido = residuos[i][0]
                    distribucion_partidos[partido] += 1
            
            # Actualizar totales
            for partido, distritos in distribucion_partidos.items():
                totales_partidos[partido] += distritos
            
            distribucion_estados.append({
                "estado_id": estado_id,
                "estado_nombre": nombres_estados.get(estado_id, f"Estado {estado_id}"),
                "distritos_totales": distritos_estado,
                "distribucion_partidos": distribucion_partidos
            })
        
        # Mostrar primeros 5 estados
        print(f"\n   Primeros 5 estados:")
        for estado in distribucion_estados[:5]:
            print(f"      {estado['estado_nombre']} ({estado['estado_id']}): {estado['distritos_totales']} distritos")
            print(f"         {estado['distribucion_partidos']}")
        
        # Mostrar totales
        print(f"\n6. Totales por partido:")
        suma_total = 0
        for partido, total in sorted(totales_partidos.items(), key=lambda x: x[1], reverse=True):
            print(f"      {partido}: {total} MR")
            suma_total += total
        
        print(f"\n   Suma total: {suma_total} (esperado: {n_distritos})")
        
        if suma_total == n_distritos:
            print("   ✓ Suma total correcta")
        else:
            print(f"   ✗ ERROR: Suma total incorrecta ({suma_total} != {n_distritos})")
            return False
        
        print("\n✓ TEST 1 PASADO")
        return distribucion_estados
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_validacion_estado(distribucion_estados):
    """Test 2: Validación de suma por estado"""
    print("\n" + "="*80)
    print("TEST 2: Validación de suma por estado")
    print("="*80)
    
    if not distribucion_estados:
        print("✗ Skipped: no hay distribución")
        return False
    
    try:
        # Cargar distribución Hare real
        secciones_df = cargar_secciones_ine()
        poblacion_estados = secciones_df.groupby("ENTIDAD")["POBTOT"].sum().to_dict()
        distribucion_hare = repartir_distritos_hare(poblacion_estados, 300, piso_constitucional=2)
        
        print(f"\nValidando {len(distribucion_estados)} estados...")
        errores = 0
        
        for estado in distribucion_estados:
            estado_id = estado['estado_id']
            distritos_esperados = distribucion_hare[estado_id]
            distritos_asignados = sum(estado['distribucion_partidos'].values())
            
            if distritos_asignados != distritos_esperados:
                print(f"   ✗ {estado['estado_nombre']}: {distritos_asignados} != {distritos_esperados}")
                errores += 1
        
        if errores == 0:
            print(f"   ✓ Todos los estados suman correctamente")
            print("\n✓ TEST 2 PASADO")
            return True
        else:
            print(f"\n✗ {errores} estados con suma incorrecta")
            return False
            
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_edicion_manual(distribucion_estados):
    """Test 3: Edición manual de distribución por estado"""
    print("\n" + "="*80)
    print("TEST 3: Edición manual de distribución por estado")
    print("="*80)
    
    if not distribucion_estados:
        print("✗ Skipped: no hay distribución")
        return False
    
    try:
        # Crear distribución editada
        distribucion_editada = {}
        
        # Cargar distribución Hare para validación
        secciones_df = cargar_secciones_ine()
        poblacion_estados = secciones_df.groupby("ENTIDAD")["POBTOT"].sum().to_dict()
        distribucion_hare = repartir_distritos_hare(poblacion_estados, 300, piso_constitucional=2)
        
        print(f"\nEditando manualmente CDMX (estado 9) y EdoMex (estado 15)...")
        
        for estado in distribucion_estados:
            estado_id = str(estado['estado_id'])
            
            if estado['estado_id'] == 9:  # CDMX: 19 distritos
                distribucion_editada[estado_id] = {
                    "MORENA": 12,
                    "PAN": 4,
                    "PRI": 2,
                    "MC": 1
                }
                print(f"   CDMX editado:")
                print(f"      Original: {estado['distribucion_partidos']}")
                print(f"      Editado:  {distribucion_editada[estado_id]}")
                print(f"      Suma: {sum(distribucion_editada[estado_id].values())} (esperado: 19)")
                
            elif estado['estado_id'] == 15:  # EdoMex: 34 distritos
                distribucion_editada[estado_id] = {
                    "MORENA": 20,
                    "PAN": 8,
                    "PRI": 4,
                    "MC": 2
                }
                print(f"   EdoMex editado:")
                print(f"      Original: {estado['distribucion_partidos']}")
                print(f"      Editado:  {distribucion_editada[estado_id]}")
                print(f"      Suma: {sum(distribucion_editada[estado_id].values())} (esperado: 34)")
            else:
                # Mantener original
                distribucion_editada[estado_id] = estado['distribucion_partidos']
        
        # Validar y sumar
        print(f"\nValidando distribución editada...")
        totales_por_partido = {}
        errores = 0
        
        for estado_id_str, partidos_dict in distribucion_editada.items():
            estado_id = int(estado_id_str)
            
            # Validar suma
            distritos_esperados = distribucion_hare[estado_id]
            distritos_asignados = sum(partidos_dict.values())
            
            if distritos_asignados != distritos_esperados:
                print(f"   ✗ Estado {estado_id}: suma incorrecta ({distritos_asignados} != {distritos_esperados})")
                errores += 1
            
            # Sumar a totales
            for partido, distritos in partidos_dict.items():
                totales_por_partido[partido] = totales_por_partido.get(partido, 0) + distritos
        
        if errores > 0:
            print(f"\n✗ {errores} errores de validación")
            return False
        
        print(f"   ✓ Validación exitosa")
        
        # Mostrar totales
        print(f"\nTotales MR después de edición:")
        suma_total = 0
        for partido, total in sorted(totales_por_partido.items(), key=lambda x: x[1], reverse=True):
            print(f"   {partido}: {total} MR")
            suma_total += total
        
        print(f"\nSuma total: {suma_total} (esperado: 300)")
        
        if suma_total == 300:
            print("✓ Suma total correcta")
            print("\n✓ TEST 3 PASADO")
            return True
        else:
            print(f"✗ ERROR: Suma incorrecta ({suma_total} != 300)")
            return False
            
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecutar todos los tests"""
    print("\n" + "="*80)
    print("TESTS DIRECTOS DE DISTRIBUCIÓN POR ESTADO (SIN SERVIDOR)")
    print("="*80)
    print("\nEstos tests verifican:")
    print("1. Cálculo de distribución estado por estado")
    print("2. Validación de suma por estado")
    print("3. Edición manual y conversión a totales")
    
    resultados = []
    
    # Test 1: Calcular distribución
    distribucion = test_calcular_distribucion_estados()
    resultados.append(("Cálculo de distribución", distribucion is not None))
    
    # Test 2: Validación
    if distribucion:
        validacion_ok = test_validacion_estado(distribucion)
        resultados.append(("Validación suma por estado", validacion_ok))
        
        # Test 3: Edición manual
        edicion_ok = test_edicion_manual(distribucion)
        resultados.append(("Edición manual", edicion_ok))
    
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
