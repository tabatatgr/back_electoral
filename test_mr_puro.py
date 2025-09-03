#!/usr/bin/env python3
"""
Test de Mayoría Relativa PURA
Verificar qué pasa cuando se elige solo MR (sin RP ni PM)
"""

import sys
sys.path.append('.')

from engine.procesar_senadores_v2 import procesar_senadores_v2

def test_mayoria_relativa_pura():
    """Test para verificar el comportamiento con MR puro"""
    
    print("🔍 TEST MAYORÍA RELATIVA PURA")
    print("=" * 50)
    print("Verificando comportamiento con solo MR (sin RP ni PM)")
    print()
    
    configs = [
        {
            "nombre": "64 MR puro (Plan C estilo)",
            "sistema": "mr",
            "mr_seats": 64,
            "rp_seats": 0,
            "pm_seats": 0,
            "max_seats": 64,
            "esperado_total": 64
        },
        {
            "nombre": "96 MR puro (más escaños)",
            "sistema": "mr", 
            "mr_seats": 96,
            "rp_seats": 0,
            "pm_seats": 0,
            "max_seats": 96,
            "esperado_total": 96
        },
        {
            "nombre": "128 MR puro (todos MR)",
            "sistema": "mr",
            "mr_seats": 128,
            "rp_seats": 0,
            "pm_seats": 0,
            "max_seats": 128,
            "esperado_total": 128
        },
        {
            "nombre": "32 MR puro (mínimo)",
            "sistema": "mr",
            "mr_seats": 32,
            "rp_seats": 0,
            "pm_seats": 0,
            "max_seats": 32,
            "esperado_total": 32
        }
    ]
    
    resultados = []
    
    for config in configs:
        print(f"📊 {config['nombre']}")
        print(f"   Configuración: {config['mr_seats']} MR, {config['rp_seats']} RP, {config['pm_seats']} PM")
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
                    print(f"   ✅ CORRECTO: Total coincide")
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
                print(f"   - PRD: {prd} ({(prd/total_real)*100:.1f}%)")
                print(f"   - PVEM: {pvem} ({(pvem/total_real)*100:.1f}%)")
                print(f"   - PT: {pt} ({(pt/total_real)*100:.1f}%)")
                print(f"   - MC: {mc} ({(mc/total_real)*100:.1f}%)")
                
                # Calcular concentración (¿es muy desigual?)
                total_top_3 = morena + pan + pri
                concentracion = (total_top_3 / total_real) * 100
                print(f"   - Top 3 partidos: {concentracion:.1f}% de escaños")
                
                resultados.append({
                    "config": config['nombre'],
                    "mr_seats": config['mr_seats'],
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
                    "concentracion": concentracion
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
        print("📋 ANÁLISIS DE MAYORÍA RELATIVA PURA")
        print("=" * 90)
        print(f"{'CONFIGURACIÓN':<25} | {'MR':<4} | {'TOTAL':<6} | {'MORENA':<6} | {'PAN':<6} | {'PRI':<6} | {'CONC%':<6}")
        print("-" * 90)
        
        for r in exitosos:
            print(f"{r['config']:<25} | {r['mr_seats']:<4} | {r['total_real']:<6} | {r['morena']:<6} | {r['pan']:<6} | {r['pri']:<6} | {r['concentracion']:<6.1f}")
        
        print()
        print("🔍 ANÁLISIS DE PATRONES:")
        print("-" * 35)
        
        # Verificar si hay escalamiento proporcional
        morena_values = [r['morena'] for r in exitosos]
        pan_values = [r['pan'] for r in exitosos]
        pri_values = [r['pri'] for r in exitosos]
        mr_sizes = [r['mr_seats'] for r in exitosos]
        
        print(f"MORENA por tamaño MR: {dict(zip(mr_sizes, morena_values))}")
        print(f"PAN por tamaño MR: {dict(zip(mr_sizes, pan_values))}")
        print(f"PRI por tamaño MR: {dict(zip(mr_sizes, pri_values))}")
        
        # Verificar concentración
        concentraciones = [r['concentracion'] for r in exitosos]
        print(f"Concentración Top 3: {min(concentraciones):.1f}% - {max(concentraciones):.1f}%")
        
        if max(concentraciones) - min(concentraciones) < 5:
            print("✅ CONCENTRACIÓN ESTABLE: La distribución es proporcional al tamaño")
        else:
            print("⚠️  CONCENTRACIÓN VARIABLE: El tamaño afecta la distribución")
        
        # Verificar eficiencia de MORENA
        print(f"\n📊 EFICIENCIA DE MORENA EN MR PURO:")
        for r in exitosos:
            eficiencia = (r['morena'] / r['total_real']) * 100
            print(f"   {r['mr_seats']} MR: {r['morena']} escaños = {eficiencia:.1f}%")
        
        # Comparar con sistema mixto vigente (referencia)
        print(f"\n🔄 COMPARACIÓN CON SISTEMA VIGENTE:")
        print(f"   Sistema vigente (96MR+32RP): MORENA ~65/128 = 50.8%")
        
        mr_96 = next((r for r in exitosos if r['mr_seats'] == 96), None)
        if mr_96:
            eficiencia_96_puro = (mr_96['morena'] / mr_96['total_real']) * 100
            print(f"   96 MR puro: MORENA {mr_96['morena']}/{mr_96['total_real']} = {eficiencia_96_puro:.1f}%")
            print(f"   Diferencia: {eficiencia_96_puro - 50.8:.1f} puntos porcentuales")
        
        # Verificar diversidad partidista
        print(f"\n🎭 DIVERSIDAD PARTIDISTA:")
        for r in exitosos:
            partidos_con_escanos = sum(1 for partido in ['morena', 'pan', 'pri', 'prd', 'pvem', 'pt', 'mc'] 
                                     if r.get(partido, 0) > 0)
            print(f"   {r['mr_seats']} MR: {partidos_con_escanos} partidos con escaños")
            
    else:
        print("❌ No se obtuvieron resultados exitosos")
    
    print(f"\n🎯 RESUMEN: {len(exitosos)}/{len(resultados)} configuraciones exitosas")
    
    # Conclusiones
    if len(exitosos) >= 2:
        print("\n💡 CONCLUSIONES SOBRE MAYORÍA RELATIVA PURA:")
        print("1. El sistema MR puro asigna escaños por entidad ganadora")
        print("2. MORENA probablemente domine por su fuerza territorial")
        print("3. Los partidos pequeños pueden quedar sin representación") 
        print("4. La concentración depende de la geografía electoral")
        print("5. Diferente al sistema mixto que balancea con RP")
    
    return exitosos

if __name__ == "__main__":
    test_mayoria_relativa_pura()
