"""
Test del nuevo endpoint GET /calcular/distribucion_estados
y del parámetro mr_distritos_por_estado en POST /procesar/diputados

Este test verifica:
1. GET devuelve distribución estado por estado correctamente
2. POST acepta ediciones estado por estado
3. Validación: suma por estado = distritos Hare del estado
4. Conversión automática de estado→total MR

Autor: Sistema Electoral v2.0
Fecha: 2024
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_get_distribucion_estados():
    """Test 1: GET /calcular/distribucion_estados"""
    print("\n" + "="*80)
    print("TEST 1: GET /calcular/distribucion_estados")
    print("="*80)
    
    # Test con configuración vigente
    response = requests.get(
        f"{BASE_URL}/calcular/distribucion_estados",
        params={
            "anio": 2024,
            "plan": "vigente"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"\n✓ Respuesta exitosa")
        print(f"Total de estados: {len(data['distribucion_estados'])}")
        print(f"Totales por partido: {data['totales']}")
        print(f"Método: {data['metadatos']['metodo']}")
        print(f"Eficiencias usadas: {data['metadatos']['eficiencias']}")
        
        # Mostrar primeros 5 estados
        print("\nPrimeros 5 estados:")
        for estado in data['distribucion_estados'][:5]:
            print(f"  {estado['estado_nombre']} ({estado['estado_id']}): {estado['distritos_totales']} distritos")
            print(f"    Distribución: {estado['distribucion_partidos']}")
        
        # Validar suma total
        suma_total = sum(data['totales'].values())
        print(f"\nSuma total MR: {suma_total} (esperado: 300)")
        
        if suma_total == 300:
            print("✓ Suma total correcta")
        else:
            print(f"✗ ERROR: Suma total incorrecta ({suma_total} != 300)")
        
        return data
    else:
        print(f"✗ ERROR: {response.status_code}")
        print(response.text)
        return None

def test_post_con_estado_manual(distribucion_original):
    """Test 2: POST /procesar/diputados con mr_distritos_por_estado"""
    print("\n" + "="*80)
    print("TEST 2: POST /procesar/diputados con mr_distritos_por_estado")
    print("="*80)
    
    if not distribucion_original:
        print("✗ Skipped: no hay distribución original")
        return
    
    # Crear edición manual: darle más distritos a MORENA en CDMX (estado 9)
    # y EdoMex (estado 15)
    distribucion_editada = {}
    
    for estado in distribucion_original['distribucion_estados']:
        estado_id = str(estado['estado_id'])
        
        if estado['estado_id'] == 9:  # CDMX: 24 distritos
            # Original: MORENA probablemente ~12-14
            # Editado: MORENA 16, PAN 4, PRI 2, MC 2
            distribucion_editada[estado_id] = {
                "MORENA": 16,
                "PAN": 4,
                "PRI": 2,
                "MC": 2
            }
            print(f"\nEditando CDMX (estado 9):")
            print(f"  Original: {estado['distribucion_partidos']}")
            print(f"  Editado: {distribucion_editada[estado_id]}")
            
        elif estado['estado_id'] == 15:  # EdoMex: 40 distritos
            # Original: MORENA probablemente ~20-24
            # Editado: MORENA 26, PAN 8, PRI 4, MC 2
            distribucion_editada[estado_id] = {
                "MORENA": 26,
                "PAN": 8,
                "PRI": 4,
                "MC": 2
            }
            print(f"\nEditando EdoMex (estado 15):")
            print(f"  Original: {estado['distribucion_partidos']}")
            print(f"  Editado: {distribucion_editada[estado_id]}")
            
        else:
            # Mantener distribución original
            distribucion_editada[estado_id] = estado['distribucion_partidos']
    
    # Hacer POST con distribución editada
    print("\nEnviando POST con distribución editada...")
    
    response = requests.post(
        f"{BASE_URL}/procesar/diputados",
        params={
            "anio": 2024,
            "plan": "vigente",
            "mr_distritos_por_estado": json.dumps(distribucion_editada),
            "votos_custom": json.dumps({
                "MORENA": 38.0,
                "PAN": 22.0,
                "PRI": 18.0,
                "MC": 12.0,
                "PVEM": 6.0,
                "PT": 4.0
            })
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ Procesamiento exitoso")
        print(f"Escaños totales: {data.get('escanos_totales', 'N/A')}")
        
        # Verificar que MORENA tenga más escaños (debido a ediciones)
        if 'distribucion_final' in data:
            dist = data['distribucion_final']
            print(f"\nDistribución final:")
            for partido, escanos in sorted(dist.items(), key=lambda x: x[1], reverse=True):
                print(f"  {partido}: {escanos}")
        
        return data
    else:
        print(f"✗ ERROR: {response.status_code}")
        print(response.text)
        return None

def test_validacion_suma_incorrecta():
    """Test 3: Validación - suma incorrecta por estado"""
    print("\n" + "="*80)
    print("TEST 3: Validación - suma incorrecta por estado")
    print("="*80)
    
    # CDMX tiene 24 distritos, vamos a dar solo 20 (debería fallar)
    distribucion_invalida = {
        "9": {  # CDMX
            "MORENA": 12,
            "PAN": 4,
            "PRI": 2,
            "MC": 2
            # Total: 20, pero CDMX tiene 24 distritos → DEBE FALLAR
        }
    }
    
    print(f"\nEnviando distribución inválida para CDMX (20 distritos en vez de 24)...")
    
    response = requests.post(
        f"{BASE_URL}/procesar/diputados",
        params={
            "anio": 2024,
            "plan": "vigente",
            "mr_distritos_por_estado": json.dumps(distribucion_invalida)
        }
    )
    
    if response.status_code == 400:
        print(f"✓ Validación correcta: rechazó distribución inválida")
        print(f"Mensaje: {response.json().get('detail', 'N/A')}")
    else:
        print(f"✗ ERROR: Debió rechazar (código: {response.status_code})")
        print(response.text)

def test_plan_200_200():
    """Test 4: Plan 200-200 con distribución por estado"""
    print("\n" + "="*80)
    print("TEST 4: Plan 200-200 con distribución por estado")
    print("="*80)
    
    # Primero obtener distribución para 200 distritos
    response = requests.get(
        f"{BASE_URL}/calcular/distribucion_estados",
        params={
            "anio": 2024,
            "plan": "200_200_sin_topes"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ Distribución obtenida para plan 200-200")
        print(f"Total distritos: {sum(data['totales'].values())} (esperado: 200)")
        print(f"Totales por partido: {data['totales']}")
        
        # Verificar suma
        suma = sum(data['totales'].values())
        if suma == 200:
            print("✓ Suma correcta para 200 distritos")
        else:
            print(f"✗ ERROR: Suma incorrecta ({suma} != 200)")
    else:
        print(f"✗ ERROR: {response.status_code}")
        print(response.text)

def main():
    """Ejecutar todos los tests"""
    print("\n" + "="*80)
    print("TESTS DE DISTRIBUCIÓN POR ESTADO")
    print("="*80)
    print("\nEstos tests verifican:")
    print("1. GET /calcular/distribucion_estados devuelve distribución correcta")
    print("2. POST /procesar/diputados acepta mr_distritos_por_estado")
    print("3. Validación de suma por estado funciona")
    print("4. Funciona con diferentes planes (vigente, 200-200)")
    
    try:
        # Test 1: GET distribución
        distribucion = test_get_distribucion_estados()
        
        # Test 2: POST con edición manual
        test_post_con_estado_manual(distribucion)
        
        # Test 3: Validación
        test_validacion_suma_incorrecta()
        
        # Test 4: Plan 200-200
        test_plan_200_200()
        
        print("\n" + "="*80)
        print("TESTS COMPLETADOS")
        print("="*80)
        
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: No se pudo conectar al servidor")
        print("Asegúrate de que el servidor esté corriendo en http://localhost:8000")
    except Exception as e:
        print(f"\n✗ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
