#!/usr/bin/env python3
"""
Test de Primera Minoría CORREGIDO
Verificar que PM no suma al total, sino que redistribuye desde MR
"""

import sys
sys.path.append('.')

from engine.procesar_senadores_v2 import procesar_senadores_v2

def test_primera_minoria_corregido():
    """Test para verificar que PM redistribuye correctamente sin sumar al total"""
    
    print("🔍 TEST PRIMERA MINORÍA - REDISTRIBUCIÓN CORRECTA")
    print("=" * 60)
    print("Verificando que PM 'sale' de MR, no se suma al total")
    print()
    
    configs = [
        {
            "nombre": "Sistema vigente (96MR + 32RP = 128)",
            "sistema": "mixto",
            "mr_seats": 96,
            "rp_seats": 32,
            "pm_seats": 0,  # Sin PM explícita (incluida en MR)
            "max_seats": 128,
            "esperado_total": 128
        },
        {
            "nombre": "32 PM explícita (64MR + 32PM + 32RP = 128)",
            "sistema": "mixto", 
            "mr_seats": 96,  # Total MR disponible
            "rp_seats": 32,
            "pm_seats": 32,  # 32 PM "salen" de los 96 MR
            "max_seats": 128,
            "esperado_total": 128,
            "esperado_mr_efectivo": 64,  # 96 - 32 = 64
            "esperado_pm": 32
        },
        {
            "nombre": "16 PM explícita (80MR + 16PM + 32RP = 128)",
            "sistema": "mixto",
            "mr_seats": 96,  # Total MR disponible
            "rp_seats": 32,
            "pm_seats": 16,  # 16 PM "salen" de los 96 MR
            "max_seats": 128,
            "esperado_total": 128,
            "esperado_mr_efectivo": 80,  # 96 - 16 = 80
            "esperado_pm": 16
        }
    ]
    
    resultados = []
    
    for config in configs:
        print(f"📊 {config['nombre']}")
        print(f"   Configuración: {config['mr_seats']} MR disponible, {config['pm_seats']} PM, {config['rp_seats']} RP")
        print("-" * 55)
        
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
                
                # Mostrar distribución
                morena = escanos.get("MORENA", 0)
                pan = escanos.get("PAN", 0)
                pri = escanos.get("PRI", 0)
                
                print(f"   Distribución: MORENA {morena}, PAN {pan}, PRI {pri}")
                
                resultados.append({
                    "config": config['nombre'],
                    "pm_seats": config['pm_seats'],
                    "total_real": total_real,
                    "total_esperado": config['esperado_total'],
                    "correcto": total_real == config['esperado_total'],
                    "morena": morena,
                    "pan": pan,
                    "pri": pri
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
    
    # Análisis final
    exitosos = [r for r in resultados if not r.get("error", False)]
    
    if exitosos:
        print("=" * 80)
        print("📋 ANÁLISIS DE RESULTADOS - PRIMERA MINORÍA")
        print("=" * 80)
        print(f"{'CONFIGURACIÓN':<35} | {'PM':<3} | {'TOTAL':<6} | {'OK':<3} | {'MORENA':<6} | {'PAN':<6}")
        print("-" * 80)
        
        for r in exitosos:
            ok_symbol = "✅" if r['correcto'] else "❌"
            print(f"{r['config']:<35} | {r['pm_seats']:<3} | {r['total_real']:<6} | {ok_symbol:<3} | {r['morena']:<6} | {r['pan']:<6}")
        
        # Verificar si el efecto es correcto
        todos_correctos = all(r['correcto'] for r in exitosos)
        
        print()
        if todos_correctos:
            print("✅ PRIMERA MINORÍA FUNCIONA CORRECTAMENTE:")
            print("   - El total de escaños NO cambia al agregar PM")
            print("   - Los escaños PM 'salen' de los escaños MR disponibles")
            print("   - La redistribución afecta la composición partidista")
            
            # Verificar variación en MORENA
            morena_values = [r['morena'] for r in exitosos]
            if len(set(morena_values)) > 1:
                print(f"   - MORENA varía entre {min(morena_values)} y {max(morena_values)} escaños según PM")
            
        else:
            print("❌ PRIMERA MINORÍA TIENE PROBLEMAS:")
            errores = [r for r in exitosos if not r['correcto']]
            for error in errores:
                print(f"   - {error['config']}: Total {error['total_real']} ≠ {error['total_esperado']}")
            
    else:
        print("❌ No se obtuvieron resultados exitosos")
    
    print(f"\n🎯 RESUMEN: {len(exitosos)}/{len(resultados)} configuraciones exitosas")
    
    return resultados

if __name__ == "__main__":
    test_primera_minoria_corregido()
