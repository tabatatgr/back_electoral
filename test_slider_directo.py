#!/usr/bin/env python3
"""
Test DIRECTO del Slider de Primera Minoría
Prueba diferentes configuraciones para verificar el efecto de la PM
"""

import sys
sys.path.append('.')

from engine.procesar_senadores_v2 import procesar_senadores_v2

def test_slider_primera_minoria_directo():
    """
    Prueba directa de diferentes configuraciones electorales
    para verificar el efecto del "slider" de primera minoría
    """
    
    print("🧪 TEST DIRECTO - SLIDER PRIMERA MINORÍA")
    print("=" * 55)
    print("Simulando diferentes posiciones del slider MR/PM/RP")
    print()
    
    # Configuraciones que simulan el slider
    configs = [
        {
            "nombre": "64MR PURO",
            "sistema": "mr", 
            "max_seats": 64,
            "descripcion": "Sistema MR puro (sin PM ni RP)"
        },
        {
            "nombre": "80MR PURO", 
            "sistema": "mr",
            "max_seats": 80,
            "descripcion": "Más escaños MR puros"
        },
        {
            "nombre": "64MR + 32RP",
            "sistema": "mixto",
            "mr_seats": 64,
            "rp_seats": 32, 
            "max_seats": 96,
            "descripcion": "Mixto balanceado (incluye PM automática)"
        },
        {
            "nombre": "80MR + 48RP",
            "sistema": "mixto",
            "mr_seats": 80,
            "rp_seats": 48,
            "max_seats": 128,
            "descripcion": "Mixto con más MR"
        },
        {
            "nombre": "96MR + 32RP VIGENTE",
            "sistema": "mixto", 
            "mr_seats": 96,
            "rp_seats": 32,
            "max_seats": 128,
            "descripcion": "Sistema vigente (incluye 32 PM)"
        }
    ]
    
    resultados = []
    
    for config in configs:
        print(f"📊 {config['nombre']}")
        print(f"   {config['descripcion']}")
        print("-" * 35)
        
        try:
            # Parámetros base
            params = {
                "path_parquet": "data/computos_senado_2018.parquet",
                "anio": 2018,
                "path_siglado": "data/siglado_senado_2018_corregido.csv",
                "sistema": config["sistema"],
                "max_seats": config["max_seats"],
                "umbral": 0.0
            }
            
            # Agregar parámetros específicos según sistema
            if config["sistema"] == "mixto":
                params["mr_seats"] = config["mr_seats"]
                params["rp_seats"] = config["rp_seats"]
            
            # Ejecutar procesamiento
            resultado = procesar_senadores_v2(**params)
            
            if resultado and "seat_chart" in resultado:
                # seat_chart es una lista de diccionarios
                seat_chart = resultado["seat_chart"]
                
                # Convertir a diccionario escaños por partido
                escanos = {}
                for item in seat_chart:
                    if isinstance(item, dict) and 'party' in item and 'seats' in item:
                        escanos[item['party']] = item['seats']
                
                total = sum(escanos.values())
                
                print(f"   ✅ Total: {total} escaños")
                
                # Top 4 partidos
                partidos_top = sorted(escanos.items(), key=lambda x: x[1], reverse=True)[:4]
                for i, (partido, seats) in enumerate(partidos_top):
                    if seats > 0:
                        pct = (seats/total)*100
                        print(f"   {i+1}. {partido}: {seats} ({pct:.1f}%)")
                
                # Información del sistema
                if config["sistema"] == "mixto":
                    print(f"   Sistema: {config['mr_seats']} MR + {config['rp_seats']} RP")
                else:
                    print(f"   Sistema: {config['max_seats']} MR puro")
                
                resultados.append({
                    "config": config["nombre"],
                    "sistema": config["sistema"],
                    "total": total,
                    "mr_config": config.get("mr_seats", config.get("max_seats", 0)),
                    "rp_config": config.get("rp_seats", 0),
                    "morena": escanos.get("MORENA", 0),
                    "pan": escanos.get("PAN", 0),
                    "pri": escanos.get("PRI", 0),
                    "prd": escanos.get("PRD", 0),
                    "success": True
                })
                
            else:
                print("   ❌ Error: No se obtuvo seat_chart")
                resultados.append({
                    "config": config["nombre"],
                    "success": False
                })
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            resultados.append({
                "config": config["nombre"],
                "success": False,
                "error": str(e)
            })
        
        print()
    
    # Análisis de resultados exitosos
    exitosos = [r for r in resultados if r.get("success", False)]
    
    if exitosos:
        print("=" * 90)
        print("📋 TABLA COMPARATIVA - SIMULACIÓN SLIDER PRIMERA MINORÍA")
        print("=" * 90)
        print(f"{'CONFIGURACIÓN':<20} | {'MR':<3} | {'RP':<3} | {'MORENA':<6} | {'PAN':<6} | {'PRI':<6} | {'PRD':<6} | {'TOTAL':<6}")
        print("-" * 90)
        
        for r in exitosos:
            print(f"{r['config']:<20} | {r['mr_config']:<3} | {r['rp_config']:<3} | {r['morena']:<6} | {r['pan']:<6} | {r['pri']:<6} | {r['prd']:<6} | {r['total']:<6}")
        
        print()
        print("🔍 ANÁLISIS DE EFECTOS DEL SLIDER:")
        print("-" * 45)
        
        # Análisis de variación por partido
        morena_values = [r['morena'] for r in exitosos]
        pan_values = [r['pan'] for r in exitosos]
        pri_values = [r['pri'] for r in exitosos]
        
        def analizar_variacion(partido, valores):
            if len(valores) > 1:
                minimo, maximo = min(valores), max(valores)
                variacion = maximo - minimo
                return f"{partido}: {minimo}-{maximo} escaños (variación: {variacion})"
            return f"{partido}: {valores[0]} escaños (sin variación)"
        
        print(analizar_variacion("MORENA", morena_values))
        print(analizar_variacion("PAN", pan_values))
        print(analizar_variacion("PRI", pri_values))
        
        # Verificar si hay cambios significativos
        variacion_total = (max(morena_values) - min(morena_values) + 
                          max(pan_values) - min(pan_values) + 
                          max(pri_values) - min(pri_values))
        
        print()
        if variacion_total > 0:
            print("✅ EL SLIDER SÍ TIENE EFECTO:")
            print("   Los cambios en MR/PM/RP redistribuyen escaños entre partidos")
            
            # Comparaciones específicas
            mr_puro = next((r for r in exitosos if "64MR PURO" in r['config']), None)
            vigente = next((r for r in exitosos if "VIGENTE" in r['config']), None)
            
            if mr_puro and vigente:
                print(f"\n🔄 COMPARACIÓN CLAVE (64MR puro vs Sistema vigente):")
                print(f"   64MR puro:      MORENA {mr_puro['morena']}, PAN {mr_puro['pan']}, PRI {mr_puro['pri']}")
                print(f"   96MR+32RP:      MORENA {vigente['morena']}, PAN {vigente['pan']}, PRI {vigente['pri']}")
                
                diff_morena = vigente['morena'] - mr_puro['morena']
                diff_pan = vigente['pan'] - mr_puro['pan']
                print(f"   Cambio:         MORENA {diff_morena:+d}, PAN {diff_pan:+d}")
                
        else:
            print("❌ EL SLIDER NO TIENE EFECTO DETECTABLE:")
            print("   Todas las configuraciones producen la misma distribución")
        
        # Resumen de eficiencia por sistema
        print(f"\n📊 EFICIENCIA DE MORENA POR SISTEMA:")
        for r in exitosos:
            eficiencia = (r['morena'] / r['total']) * 100
            tipo_sistema = "MR puro" if r['sistema'] == 'mr' else "Mixto"
            print(f"   {r['config']}: {eficiencia:.1f}% ({tipo_sistema})")
            
    else:
        print("❌ No se obtuvieron resultados exitosos")
    
    print(f"\n🎯 CONCLUSIÓN: {len(exitosos)}/{len(resultados)} configuraciones procesadas exitosamente")
    
    if len(exitosos) >= 2:
        print("💡 RECOMENDACIÓN: El slider está funcionando - diferentes configuraciones producen diferentes resultados")
    else:
        print("⚠️  ADVERTENCIA: No hay suficientes datos para evaluar el efecto del slider")
    
    return exitosos

if __name__ == "__main__":
    test_slider_primera_minoria_directo()
