#!/usr/bin/env python3
"""
Test rápido para verificar si sobrerrepresentacion llega al motor de procesamiento
"""

import sys
sys.path.append('.')

from engine.procesar_diputados_v2 import procesar_diputados_v2

def test_debug_sobrerrepresentacion():
    """Test debug para ver si el parámetro sobrerrepresentacion tiene efecto"""
    
    print("🔍 DEBUG: Verificando efecto del parámetro sobrerrepresentacion")
    print("=" * 60)
    
    # Configuración base que simula lo que envía el frontend
    params_base = {
        "path_parquet": "data/computos_diputados_2018.parquet",
        "anio": 2018,
        "path_siglado": "data/siglado-diputados-2018.csv",
        "sistema": "mixto",
        "mr_seats": 64,
        "rp_seats": 64,
        "max_seats": 128,
        "umbral": 0.0  # Como en el frontend
    }
    
    tests = [
        {
            "nombre": "SIN sobrerrepresentacion (default)",
            "params": params_base.copy()
        },
        {
            "nombre": "CON sobrerrepresentacion=11.2 (frontend)",
            "params": {**params_base, "sobrerrepresentacion": 11.2}
        },
        {
            "nombre": "CON sobrerrepresentacion=8.0 (constitucional)",
            "params": {**params_base, "sobrerrepresentacion": 8.0}
        }
    ]
    
    resultados = []
    
    for test in tests:
        print(f"\n📊 {test['nombre']}")
        print(f"Parámetros: sobrerrepresentacion = {test['params'].get('sobrerrepresentacion', 'No definido')}")
        print("-" * 50)
        
        try:
            resultado = procesar_diputados_v2(**test['params'])
            
            if resultado and "seat_chart" in resultado:
                # Extraer escaños
                escanos = {}
                for item in resultado["seat_chart"]:
                    if isinstance(item, dict) and 'party' in item and 'seats' in item:
                        escanos[item['party']] = item['seats']
                
                morena = escanos.get("MORENA", 0)
                pan = escanos.get("PAN", 0)
                pri = escanos.get("PRI", 0)
                total = sum(escanos.values())
                
                print(f"✅ MORENA: {morena} escaños ({(morena/total)*100:.1f}%)")
                print(f"   PAN: {pan} escaños ({(pan/total)*100:.1f}%)")
                print(f"   PRI: {pri} escaños ({(pri/total)*100:.1f}%)")
                print(f"   Total: {total}")
                
                # Calcular sobrerrepresentación de MORENA
                if "seat_chart" in resultado:
                    for partido in resultado["seat_chart"]:
                        if partido.get("party") == "MORENA":
                            votos_pct = partido.get("percent", 0)
                            escanos_pct = (morena / total) * 100
                            sobrerep = escanos_pct - votos_pct
                            print(f"   Votos: {votos_pct:.1f}% | Escaños: {escanos_pct:.1f}% | Sobrerrepresentación: {sobrerep:.1f}%")
                            break
                
                resultados.append({
                    "test": test['nombre'],
                    "sobrerrepresentacion_param": test['params'].get('sobrerrepresentacion'),
                    "morena": morena,
                    "pan": pan,
                    "pri": pri,
                    "total": total
                })
                
            else:
                print("❌ Error: No se obtuvo seat_chart")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Comparación
    if len(resultados) >= 2:
        print("\n" + "="*60)
        print("📋 COMPARACIÓN DE RESULTADOS")
        print("="*60)
        print(f"{'TEST':<35} | {'PARAM':<6} | {'MORENA':<6} | {'PAN':<6} | {'PRI':<6}")
        print("-" * 70)
        
        for r in resultados:
            param_str = str(r['sobrerrepresentacion_param']) if r['sobrerrepresentacion_param'] is not None else "None"
            print(f"{r['test']:<35} | {param_str:<6} | {r['morena']:<6} | {r['pan']:<6} | {r['pri']:<6}")
        
        # Verificar si hay diferencias
        morena_values = [r['morena'] for r in resultados]
        if len(set(morena_values)) > 1:
            print(f"\n✅ HAY DIFERENCIAS: MORENA varía entre {min(morena_values)} y {max(morena_values)} escaños")
            print("   El parámetro sobrerrepresentacion SÍ tiene efecto")
        else:
            print(f"\n❌ NO HAY DIFERENCIAS: MORENA siempre {morena_values[0]} escaños")
            print("   El parámetro sobrerrepresentacion NO tiene efecto (posibles problemas:)")
            print("   - No se está procesando el parámetro")
            print("   - Los límites no se alcanzan con estos datos")
            print("   - La implementación tiene un bug")
    
    return resultados

if __name__ == "__main__":
    test_debug_sobrerrepresentacion()
