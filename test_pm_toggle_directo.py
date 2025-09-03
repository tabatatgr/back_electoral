"""
Test directo: Primera Minoría Toggle sin servidor
Probar prender/apagar PM directamente con el engine
"""

from engine.procesar_senadores_v2 import procesar_senadores_v2

def test_pm_toggle_directo():
    """Test directo del toggle de primera minoría"""
    
    print("🔄 TESTING PRIMERA MINORÍA TOGGLE (DIRECTO)")
    print("=" * 60)
    
    base_config = {
        "anio": 2018,
        "max_seats": 96,
        "mr_seats": 64,
        "rp_seats": 32,
        "sistema": "mixto",
        "umbral": 0.03,
        "path_parquet": "data/computos_senado_2018.parquet",
        "path_siglado": "data/siglado_senado_2018_corregido.csv"
    }
    
    tests = [
        {"pm_seats": 0, "name": "PM APAGADA"},
        {"pm_seats": 16, "name": "PM MEDIA"},
        {"pm_seats": 32, "name": "PM MÁXIMA"}
    ]
    
    results = []
    
    for test_case in tests:
        config = base_config.copy()
        config["pm_seats"] = test_case["pm_seats"]
        
        print(f"\n📊 {test_case['name']} (PM={test_case['pm_seats']})")
        print("-" * 50)
        
        try:
            result = procesar_senadores_v2(**config)
            
            print(f"[DEBUG] Estructura result: {type(result)}")
            print(f"[DEBUG] Keys: {result.keys() if hasattr(result, 'keys') else 'No keys'}")
            
            # Buscar donde están los totales
            if 'tot' in result:
                totales = result['tot']
            elif 'totales' in result:
                totales = result['totales']
            elif 'seat_chart' in result:
                # Calcular totales desde seat_chart
                totales = {}
                for item in result['seat_chart']:
                    partido = item.get('party', '')
                    seats = item.get('seats', 0)
                    if partido:
                        totales[partido] = seats
            else:
                print(f"[ERROR] No se encontraron totales en: {result.keys()}")
                continue
            
            total = sum(totales.values())
            morena = totales.get('MORENA', 0)
            pan = totales.get('PAN', 0)
            pri = totales.get('PRI', 0)
            
            results.append({
                'name': test_case['name'],
                'pm': test_case['pm_seats'],
                'total': total,
                'morena': morena,
                'pan': pan,
                'pri': pri,
                'result': result
            })
            
            print(f"✅ Total: {total} escaños")
            print(f"✅ MORENA: {morena} ({morena/total*100:.1f}%)")
            print(f"✅ PAN: {pan} ({pan/total*100:.1f}%)")
            print(f"✅ PRI: {pri} ({pri/total*100:.1f}%)")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    # Análisis comparativo
    print(f"\n📈 ANÁLISIS COMPARATIVO")
    print("=" * 60)
    
    pm_off = results[0]
    pm_med = results[1] 
    pm_max = results[2]
    
    print(f"{'CONFIG':<12} {'TOTAL':<6} {'MORENA':<8} {'PAN':<6} {'PRI':<6}")
    print("-" * 40)
    print(f"{pm_off['name']:<12} {pm_off['total']:<6} {pm_off['morena']:<8} {pm_off['pan']:<6} {pm_off['pri']:<6}")
    print(f"{pm_med['name']:<12} {pm_med['total']:<6} {pm_med['morena']:<8} {pm_med['pan']:<6} {pm_med['pri']:<6}")
    print(f"{pm_max['name']:<12} {pm_max['total']:<6} {pm_max['morena']:<8} {pm_max['pan']:<6} {pm_max['pri']:<6}")
    
    # Calcular diferencias
    morena_diff_med = pm_med['morena'] - pm_off['morena']
    morena_diff_max = pm_max['morena'] - pm_off['morena']
    pan_diff_med = pm_med['pan'] - pm_off['pan']
    pan_diff_max = pm_max['pan'] - pm_off['pan']
    
    print(f"\n🔄 EFECTOS DEL TOGGLE:")
    print(f"   MORENA: {pm_off['morena']} → {pm_med['morena']} → {pm_max['morena']}")
    print(f"           ({morena_diff_med:+d}) → ({morena_diff_max:+d})")
    print(f"   PAN:    {pm_off['pan']} → {pm_med['pan']} → {pm_max['pan']}")
    print(f"           ({pan_diff_med:+d}) → ({pan_diff_max:+d})")
    
    # Validaciones
    print(f"\n✅ VALIDACIONES:")
    
    # 1. Totales iguales
    if pm_off['total'] == pm_med['total'] == pm_max['total'] == 96:
        print("✅ Totales constantes: 96 escaños en todos los casos")
    else:
        print("❌ Totales variables")
        return False
    
    # 2. MORENA disminuye con más PM
    if pm_max['morena'] < pm_med['morena'] < pm_off['morena']:
        print("✅ MORENA disminuye: Más PM = Menos escaños MORENA")
    else:
        print("❌ MORENA no disminuye consistentemente")
        return False
    
    # 3. PAN aumenta con más PM
    if pm_max['pan'] > pm_med['pan'] > pm_off['pan']:
        print("✅ PAN aumenta: Más PM = Más escaños PAN")
    else:
        print("❌ PAN no aumenta consistentemente")
        return False
    
    # 4. Efecto gradual
    if abs(morena_diff_max) > abs(morena_diff_med):
        print("✅ Efecto gradual: PM32 > PM16 > PM0")
    else:
        print("❌ Efecto no gradual")
        return False
    
    print(f"\n🎉 CONCLUSIÓN: ¡PRIMERA MINORÍA TOGGLE FUNCIONA!")
    print(f"   📴 Se puede APAGAR (PM=0)")
    print(f"   🔄 Se puede ajustar (PM=16)")
    print(f"   🔥 Se puede maximizar (PM=32)")
    print(f"   📊 Redistribuye escaños progresivamente")
    print(f"   ⚖️ Mantiene total constante")
    
    return True

def test_mr_puro_toggle():
    """Test toggle en MR puro"""
    
    print(f"\n\n🔄 TESTING PM TOGGLE EN MR PURO")
    print("=" * 60)
    
    base_config = {
        "anio": 2018,
        "max_seats": 64,
        "sistema": "mr",
        "umbral": 0.03,
        "path_parquet": "data/computos_senado_2018.parquet",
        "path_siglado": "data/siglado_senado_2018_corregido.csv"
    }
    
    tests = [
        {"pm_seats": 0, "name": "MR PURO"},
        {"pm_seats": 32, "name": "MR+PM"}
    ]
    
    results = []
    
    for test_case in tests:
        config = base_config.copy()
        config["pm_seats"] = test_case["pm_seats"]
        
        print(f"\n📊 {test_case['name']} (PM={test_case['pm_seats']})")
        print("-" * 40)
        
        try:
            result = procesar_senadores_v2(**config)
            
            total = sum(result['tot'].values())
            morena = result['tot'].get('MORENA', 0)
            pan = result['tot'].get('PAN', 0)
            
            results.append({
                'name': test_case['name'],
                'pm': test_case['pm_seats'],
                'total': total,
                'morena': morena,
                'pan': pan,
                'result': result
            })
            
            print(f"✅ Total: {total}, MORENA: {morena}, PAN: {pan}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    # Comparar resultados
    puro = results[0]
    con_pm = results[1]
    
    print(f"\n📊 COMPARACIÓN MR PURO:")
    print(f"   Sin PM: MORENA {puro['morena']}, PAN {puro['pan']}")
    print(f"   Con PM: MORENA {con_pm['morena']}, PAN {con_pm['pan']}")
    print(f"   Efecto: MORENA {con_pm['morena'] - puro['morena']:+d}, PAN {con_pm['pan'] - puro['pan']:+d}")
    
    if con_pm['morena'] < puro['morena'] and con_pm['pan'] > puro['pan']:
        print("✅ PM funciona en MR puro: Redistribuye correctamente")
        return True
    else:
        print("❌ PM no funciona en MR puro")
        return False

if __name__ == "__main__":
    print("🧪 TESTING PRIMERA MINORÍA TOGGLE - VERSIÓN DIRECTA")
    
    success_mixto = test_pm_toggle_directo()
    success_mr = test_mr_puro_toggle()
    
    print(f"\n📋 RESUMEN FINAL:")
    print(f"   Sistema Mixto: {'✅ PASS' if success_mixto else '❌ FAIL'}")
    print(f"   Sistema MR Puro: {'✅ PASS' if success_mr else '❌ FAIL'}")
    
    if success_mixto and success_mr:
        print(f"\n🎉 ¡TODOS LOS TESTS EXITOSOS!")
        print(f"   ✅ Primera minoría se puede prender y apagar")
        print(f"   ✅ Funciona en ambos sistemas (mixto y MR puro)")
        print(f"   ✅ Efecto gradual y progresivo")
        print(f"   ✅ Mantiene totales constantes")
    else:
        print(f"\n❌ ALGUNOS TESTS FALLARON")
