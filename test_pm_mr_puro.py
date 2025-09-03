#!/usr/bin/env python3
"""
Test de Primera Minoría en MR PURO
Verificar si PM funciona cuando el sistema es pura mayoría relativa
"""

import sys
sys.path.append('.')

from engine.procesar_senadores_v2 import procesar_senadores_v2

def test_primera_minoria_mr_puro():
    """Test para verificar PM en sistema MR puro personalizado"""
    
    print("🔍 TEST PRIMERA MINORÍA EN MR PURO")
    print("=" * 55)
    print("Verificando si PM funciona con sistema de mayoría relativa pura")
    print()
    
    configs = [
        {
            "nombre": "64 MR puro (SIN PM)",
            "sistema": "mr",
            "mr_seats": 64,
            "rp_seats": 0,
            "pm_seats": 0,
            "max_seats": 64,
            "esperado_total": 64,
            "descripcion": "Línea base MR puro"
        },
        {
            "nombre": "64 MR con 16 PM",
            "sistema": "mr",
            "mr_seats": 64,
            "rp_seats": 0,
            "pm_seats": 16,  # 16 PM de los 64 MR
            "max_seats": 64,
            "esperado_total": 64,
            "descripcion": "64 MR total: 48 MR efectivo + 16 PM"
        },
        {
            "nombre": "64 MR con 32 PM",
            "sistema": "mr",
            "mr_seats": 64,
            "rp_seats": 0,
            "pm_seats": 32,  # 32 PM de los 64 MR
            "max_seats": 64,
            "esperado_total": 64,
            "descripcion": "64 MR total: 32 MR efectivo + 32 PM"
        },
        {
            "nombre": "96 MR puro (SIN PM)",
            "sistema": "mr", 
            "mr_seats": 96,
            "rp_seats": 0,
            "pm_seats": 0,
            "max_seats": 96,
            "esperado_total": 96,
            "descripcion": "Línea base MR puro más grande"
        },
        {
            "nombre": "96 MR con 32 PM",
            "sistema": "mr",
            "mr_seats": 96,
            "rp_seats": 0,
            "pm_seats": 32,  # 32 PM de los 96 MR
            "max_seats": 96,
            "esperado_total": 96,
            "descripcion": "96 MR total: 64 MR efectivo + 32 PM"
        }
    ]
    
    resultados = []
    
    for config in configs:
        print(f"📊 {config['nombre']}")
        print(f"   {config['descripcion']}")
        print(f"   Config: {config['mr_seats']} MR total, {config['pm_seats']} PM, {config['rp_seats']} RP")
        print("-" * 60)
        
        try:
            resultado = procesar_senadores_v2(
                path_parquet="data/computos_senado_2018.parquet",
                anio=2018,
                path_siglado="data/siglado_senado_2018_corregido.csv",
                sistema=config["sistema"],
                mr_seats=config["mr_seats"],
                rp_seats=config["rp_seats"],
                pm_seats=config["pm_seats"],
                max_seats=config["max_seats"],
                umbral=0.03
            )
            
            if resultado and "seat_chart" in resultado:
                seat_chart = resultado["seat_chart"]
                
                # Calcular totales
                escanos = {}
                for item in seat_chart:
                    if isinstance(item, dict) and 'party' in item and 'seats' in item:
                        escanos[item['party']] = item['seats']
                
                total_real = sum(escanos.values())
                
                # Verificaciones
                print(f"   ✅ Total real: {total_real}")
                print(f"   🎯 Total esperado: {config['esperado_total']}")
                
                if total_real == config['esperado_total']:
                    print(f"   ✅ CORRECTO: Total no cambió por PM")
                else:
                    print(f"   ❌ ERROR: Total debería ser {config['esperado_total']}, pero es {total_real}")
                
                # Mostrar distribución detallada
                morena = escanos.get("MORENA", 0)
                pan = escanos.get("PAN", 0)
                pri = escanos.get("PRI", 0)
                prd = escanos.get("PRD", 0)
                pvem = escanos.get("PVEM", 0)
                pt = escanos.get("PT", 0)
                mc = escanos.get("MC", 0)
                
                print(f"   Distribución:")
                print(f"   - MORENA: {morena} ({(morena/total_real)*100:.1f}%)")
                print(f"   - PAN: {pan} ({(pan/total_real)*100:.1f}%)")
                print(f"   - PRI: {pri} ({(pri/total_real)*100:.1f}%)")
                print(f"   - PRD: {prd}")
                print(f"   - PVEM: {pvem}")
                print(f"   - PT: {pt}")
                print(f"   - MC: {mc}")
                
                # Verificar efecto de PM
                if config['pm_seats'] > 0:
                    mr_efectivo = config['mr_seats'] - config['pm_seats']
                    print(f"   📊 PM Effect: {mr_efectivo} MR efectivo + {config['pm_seats']} PM = {config['mr_seats']} MR total")
                
                resultados.append({
                    "config": config['nombre'],
                    "mr_seats": config['mr_seats'],
                    "pm_seats": config['pm_seats'],
                    "total_real": total_real,
                    "total_esperado": config['esperado_total'],
                    "correcto": total_real == config['esperado_total'],
                    "morena": morena,
                    "pan": pan,
                    "pri": pri,
                    "prd": prd,
                    "pvem": pvem,
                    "pt": pt,
                    "mc": mc,
                    "descripcion": config['descripcion']
                })
                
            else:
                print("   ❌ Error: No se obtuvo seat_chart")
                resultados.append({
                    "config": config['nombre'],
                    "error": True
                })
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            resultados.append({
                "config": config['nombre'],
                "error": True,
                "mensaje": str(e)
            })
        
        print()
    
    # Análisis comparativo
    exitosos = [r for r in resultados if not r.get("error", False)]
    
    if exitosos:
        print("=" * 90)
        print("📋 ANÁLISIS PRIMERA MINORÍA EN MR PURO")
        print("=" * 90)
        print(f"{'CONFIGURACIÓN':<22} | {'MR':<3} | {'PM':<3} | {'TOTAL':<6} | {'MORENA':<6} | {'PAN':<6} | {'PRI':<6} | {'OK':<3}")
        print("-" * 90)
        
        for r in exitosos:
            ok_symbol = "✅" if r['correcto'] else "❌"
            print(f"{r['config']:<22} | {r['mr_seats']:<3} | {r['pm_seats']:<3} | {r['total_real']:<6} | {r['morena']:<6} | {r['pan']:<6} | {r['pri']:<6} | {ok_symbol:<3}")
        
        print()
        print("🔍 ANÁLISIS DE EFECTOS DE PM EN MR PURO:")
        print("-" * 45)
        
        # Comparar configuraciones con y sin PM del mismo tamaño
        comparaciones = [
            ("64 MR puro (SIN PM)", "64 MR con 16 PM", "64 MR con 32 PM"),
            ("96 MR puro (SIN PM)", "96 MR con 32 PM")
        ]
        
        for grupo in comparaciones:
            base_config = next((r for r in exitosos if r['config'] == grupo[0]), None)
            if base_config:
                print(f"\n📊 GRUPO {base_config['mr_seats']} MR:")
                print(f"   Base (sin PM): MORENA {base_config['morena']}, PAN {base_config['pan']}, PRI {base_config['pri']}")
                
                for config_name in grupo[1:]:
                    comp_config = next((r for r in exitosos if r['config'] == config_name), None)
                    if comp_config:
                        diff_morena = comp_config['morena'] - base_config['morena']
                        diff_pan = comp_config['pan'] - base_config['pan']
                        diff_pri = comp_config['pri'] - base_config['pri']
                        
                        print(f"   Con {comp_config['pm_seats']} PM: MORENA {comp_config['morena']} ({diff_morena:+d}), PAN {comp_config['pan']} ({diff_pan:+d}), PRI {comp_config['pri']} ({diff_pri:+d})")
        
        # Verificar si PM tiene efecto
        variaciones_morena = {}
        variaciones_pan = {}
        
        for size in [64, 96]:
            configs_size = [r for r in exitosos if r['mr_seats'] == size]
            if len(configs_size) > 1:
                morena_values = [r['morena'] for r in configs_size]
                pan_values = [r['pan'] for r in configs_size]
                
                variaciones_morena[size] = max(morena_values) - min(morena_values)
                variaciones_pan[size] = max(pan_values) - min(pan_values)
        
        print(f"\n📈 VARIACIONES POR TAMAÑO:")
        for size in variaciones_morena:
            print(f"   {size} MR: MORENA varía {variaciones_morena[size]} escaños, PAN varía {variaciones_pan[size]} escaños")
        
        # Conclusión
        hay_variaciones = any(v > 0 for v in variaciones_morena.values()) or any(v > 0 for v in variaciones_pan.values())
        
        print(f"\n💡 CONCLUSIÓN PRIMERA MINORÍA EN MR PURO:")
        if hay_variaciones:
            print("✅ LA PRIMERA MINORÍA SÍ FUNCIONA EN MR PURO:")
            print("   - Los escaños PM redistribuyen entre partidos")
            print("   - El total de escaños se mantiene fijo")
            print("   - PM 'sale' de los escaños MR disponibles")
        else:
            print("❌ LA PRIMERA MINORÍA NO TIENE EFECTO EN MR PURO:")
            print("   - Todas las configuraciones dan el mismo resultado")
            print("   - Posible problema en la implementación")
        
        # Validar totales
        todos_correctos = all(r['correcto'] for r in exitosos)
        if todos_correctos:
            print("✅ TODOS LOS TOTALES SON CORRECTOS: PM no inflr escaños")
        else:
            print("❌ HAY PROBLEMAS CON TOTALES: PM podría estar sumando")
            
    else:
        print("❌ No se obtuvieron resultados exitosos")
    
    print(f"\n🎯 RESUMEN: {len(exitosos)}/{len(resultados)} configuraciones exitosas")
    
    return exitosos

if __name__ == "__main__":
    test_primera_minoria_mr_puro()
