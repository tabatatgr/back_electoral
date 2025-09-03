"""
Test: Primera Minoría - Toggle ON/OFF
Verificar que se puede prender y apagar la primera minoría correctamente
"""

import requests
import json

def test_pm_toggle():
    """Probar encender y apagar primera minoría"""
    
    base_config = {
        "anio": 2018,
        "sistema": "mixto",  # Sistema mixto personalizado
        "max_seats": 96,
        "mr_seats": 64,
        "rp_seats": 32,
        "sobrerrepresentacion": 11.2,
        "umbral": 0.03
    }
    
    print("🔄 TESTING PRIMERA MINORÍA TOGGLE")
    print("=" * 50)
    
    # Test 1: PM APAGADA (pm_seats = 0)
    config_off = base_config.copy()
    config_off["pm_seats"] = 0
    
    print("\n📴 TEST 1: PRIMERA MINORÍA APAGADA")
    print("-" * 40)
    print(f"Config: {config_off['mr_seats']} MR, {config_off['rp_seats']} RP, {config_off['pm_seats']} PM")
    
    try:
        response = requests.post("http://localhost:8001/senado", json=config_off, timeout=30)
        if response.status_code == 200:
            result_off = response.json()
            total_off = sum(result_off['totales'].values())
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Total escaños: {total_off}")
            print(f"✅ Distribución:")
            for partido, escanos in result_off['totales'].items():
                if escanos > 0:
                    pct = (escanos / total_off) * 100
                    print(f"   - {partido}: {escanos} ({pct:.1f}%)")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"❌ Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error en petición: {e}")
        return False
    
    # Test 2: PM PRENDIDA (pm_seats = 16)
    config_on = base_config.copy()
    config_on["pm_seats"] = 16
    
    print("\n🟢 TEST 2: PRIMERA MINORÍA PRENDIDA (16 PM)")
    print("-" * 40)
    print(f"Config: {config_on['mr_seats']} MR, {config_on['rp_seats']} RP, {config_on['pm_seats']} PM")
    
    try:
        response = requests.post("http://localhost:8001/senado", json=config_on, timeout=30)
        if response.status_code == 200:
            result_on = response.json()
            total_on = sum(result_on['totales'].values())
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Total escaños: {total_on}")
            print(f"✅ Distribución:")
            for partido, escanos in result_on['totales'].items():
                if escanos > 0:
                    pct = (escanos / total_on) * 100
                    print(f"   - {partido}: {escanos} ({pct:.1f}%)")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"❌ Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error en petición: {e}")
        return False
    
    # Test 3: PM MÁXIMA (pm_seats = 32)
    config_max = base_config.copy()
    config_max["pm_seats"] = 32
    
    print("\n🔥 TEST 3: PRIMERA MINORÍA MÁXIMA (32 PM)")
    print("-" * 40)
    print(f"Config: {config_max['mr_seats']} MR, {config_max['rp_seats']} RP, {config_max['pm_seats']} PM")
    
    try:
        response = requests.post("http://localhost:8001/senado", json=config_max, timeout=30)
        if response.status_code == 200:
            result_max = response.json()
            total_max = sum(result_max['totales'].values())
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Total escaños: {total_max}")
            print(f"✅ Distribución:")
            for partido, escanos in result_max['totales'].items():
                if escanos > 0:
                    pct = (escanos / total_max) * 100
                    print(f"   - {partido}: {escanos} ({pct:.1f}%)")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"❌ Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error en petición: {e}")
        return False
    
    # Análisis comparativo
    print("\n📊 ANÁLISIS COMPARATIVO")
    print("=" * 50)
    
    # Validar totales
    if total_off == total_on == total_max == 96:
        print("✅ TOTALES CORRECTOS: Todos los escenarios dan 96 escaños")
    else:
        print(f"❌ TOTALES INCORRECTOS: OFF={total_off}, ON={total_on}, MAX={total_max}")
        return False
    
    # Comparar MORENA (partido dominante)
    morena_off = result_off['totales'].get('MORENA', 0)
    morena_on = result_on['totales'].get('MORENA', 0)
    morena_max = result_max['totales'].get('MORENA', 0)
    
    print(f"\n🏛️ MORENA (partido dominante):")
    print(f"   PM OFF:  {morena_off} escaños")
    print(f"   PM 16:   {morena_on} escaños ({morena_on - morena_off:+d})")
    print(f"   PM 32:   {morena_max} escaños ({morena_max - morena_off:+d})")
    
    # Comparar PAN (principal oposición)
    pan_off = result_off['totales'].get('PAN', 0)
    pan_on = result_on['totales'].get('PAN', 0)
    pan_max = result_max['totales'].get('PAN', 0)
    
    print(f"\n🔵 PAN (principal oposición):")
    print(f"   PM OFF:  {pan_off} escaños")
    print(f"   PM 16:   {pan_on} escaños ({pan_on - pan_off:+d})")
    print(f"   PM 32:   {pan_max} escaños ({pan_max - pan_off:+d})")
    
    # Validar efectos esperados
    print(f"\n🎯 VALIDACIÓN DE EFECTOS:")
    
    # PM debe reducir al partido dominante
    if morena_on < morena_off and morena_max < morena_on:
        print("✅ PM reduce escaños del partido dominante (MORENA)")
    else:
        print("❌ PM NO reduce escaños del partido dominante")
        return False
    
    # PM debe beneficiar a la oposición
    if pan_on > pan_off and pan_max > pan_on:
        print("✅ PM aumenta escaños de la oposición (PAN)")
    else:
        print("❌ PM NO aumenta escaños de la oposición")
        return False
    
    # Efecto gradual
    diferencia_16 = abs(morena_on - morena_off)
    diferencia_32 = abs(morena_max - morena_off)
    
    if diferencia_32 > diferencia_16:
        print("✅ Efecto gradual: Más PM = Mayor redistribución")
    else:
        print("❌ Efecto NO gradual")
        return False
    
    print(f"\n🎉 CONCLUSIÓN: PRIMERA MINORÍA TOGGLE FUNCIONA CORRECTAMENTE")
    print(f"   - Se puede prender y apagar (0 ← → 16 ← → 32)")
    print(f"   - Redistribuye escaños del dominante a la oposición")
    print(f"   - Efecto gradual según cantidad de PM")
    print(f"   - Total de escaños se mantiene fijo")
    
    return True

def test_pm_mr_puro_toggle():
    """Probar toggle en sistema MR puro"""
    
    print("\n\n🔄 TESTING PM TOGGLE EN MR PURO")
    print("=" * 50)
    
    base_config = {
        "anio": 2018,
        "sistema": "mr",  # MR puro
        "max_seats": 64,
        "sobrerrepresentacion": 11.2,
        "umbral": 0.03
    }
    
    configs = [
        {"pm_seats": 0, "name": "PM OFF"},
        {"pm_seats": 16, "name": "PM 16"},
        {"pm_seats": 32, "name": "PM 32"}
    ]
    
    results = []
    
    for config_extra in configs:
        config = base_config.copy()
        config.update(config_extra)
        
        print(f"\n🧪 {config_extra['name']}: {config.get('pm_seats', 0)} PM")
        print(f"Config: Sistema={config['sistema']}, Total={config['max_seats']}, PM={config.get('pm_seats', 0)}")
        
        try:
            response = requests.post("http://localhost:8001/senado", json=config, timeout=30)
            if response.status_code == 200:
                result = response.json()
                total = sum(result['totales'].values())
                results.append({
                    'name': config_extra['name'],
                    'pm': config.get('pm_seats', 0),
                    'total': total,
                    'morena': result['totales'].get('MORENA', 0),
                    'pan': result['totales'].get('PAN', 0),
                    'result': result
                })
                print(f"✅ Total: {total}, MORENA: {result['totales'].get('MORENA', 0)}, PAN: {result['totales'].get('PAN', 0)}")
            else:
                print(f"❌ Error: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    # Análisis MR puro
    print(f"\n📊 ANÁLISIS MR PURO:")
    for r in results:
        print(f"   {r['name']}: MORENA {r['morena']}, PAN {r['pan']}, Total {r['total']}")
    
    # Validaciones
    morena_diff = results[2]['morena'] - results[0]['morena']  # PM32 - PM0
    pan_diff = results[2]['pan'] - results[0]['pan']
    
    print(f"\n🎯 EFECTOS EN MR PURO:")
    print(f"   MORENA: {morena_diff:+d} escaños (PM32 vs PM0)")
    print(f"   PAN: {pan_diff:+d} escaños (PM32 vs PM0)")
    
    if morena_diff < 0 and pan_diff > 0:
        print("✅ PM funciona en MR puro: Redistribuye de MORENA a PAN")
        return True
    else:
        print("❌ PM NO funciona en MR puro")
        return False

if __name__ == "__main__":
    print("🧪 INICIANDO TESTS DE PRIMERA MINORÍA TOGGLE")
    
    # Test sistema mixto
    success_mixto = test_pm_toggle()
    
    # Test sistema MR puro
    success_mr = test_pm_mr_puro_toggle()
    
    print(f"\n📋 RESUMEN FINAL:")
    print(f"   Sistema Mixto: {'✅ PASS' if success_mixto else '❌ FAIL'}")
    print(f"   Sistema MR Puro: {'✅ PASS' if success_mr else '❌ FAIL'}")
    
    if success_mixto and success_mr:
        print(f"\n🎉 TODOS LOS TESTS PASARON")
        print(f"   ✅ Primera minoría se puede prender y apagar")
        print(f"   ✅ Funciona en sistema mixto y MR puro")
        print(f"   ✅ Redistribuye escaños correctamente")
    else:
        print(f"\n❌ ALGUNOS TESTS FALLARON")
