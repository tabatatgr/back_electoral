#!/usr/bin/env python3
"""
Test del Slider de Primera Minoría usando la API HTTP
Verifica que el slider de PM realmente afecte la distribución de escaños
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_api_primera_minoria():
    """
    Testa el slider de primera minoría usando la API HTTP
    """
    
    print("🧪 TEST SLIDER PRIMERA MINORÍA - VÍA API")
    print("=" * 50)
    
    # Configuraciones a probar - simulando diferentes ajustes del slider PM
    configs = [
        {
            "nombre": "Plan C - Solo MR (64 escaños)",
            "plan": "plan_c",
            "anio": 2018,
            "descripcion": "Sistema mayoría relativa puro"
        },
        {
            "nombre": "Sistema Vigente (96MR+32RP)", 
            "plan": "vigente",
            "anio": 2018,
            "descripcion": "Incluye primera minoría automática"
        },
        {
            "nombre": "Plan A - Solo RP (96 escaños)",
            "plan": "plan_a", 
            "anio": 2018,
            "descripcion": "Sistema representación proporcional puro"
        },
        {
            "nombre": "Personalizado 80MR+48RP",
            "plan": "personalizado",
            "anio": 2018,
            "sistema": "mixto",
            "mr_seats": 80,
            "rp_seats": 48,
            "descripcion": "Sistema mixto personalizado"
        },
        {
            "nombre": "Personalizado 100MR+28RP", 
            "plan": "personalizado",
            "anio": 2018,
            "sistema": "mixto",
            "mr_seats": 100,
            "rp_seats": 28,
            "descripcion": "Más MR, menos RP"
        }
    ]
    
    resultados = []
    
    for config in configs:
        print(f"\n📊 {config['nombre']}")
        print(f"   {config['descripcion']}")
        print("-" * 40)
        
        try:
            # Preparar payload para API
            payload = {
                "anio": config["anio"],
                "plan": config["plan"]
            }
            
            # Agregar parámetros específicos si es personalizado
            if config["plan"] == "personalizado":
                payload.update({
                    "sistema": config.get("sistema", "mixto"),
                    "mr_seats": config.get("mr_seats"),
                    "rp_seats": config.get("rp_seats"),
                    "umbral": 0.0
                })
            
            # Llamada a la API
            response = requests.post(f"{BASE_URL}/procesar/senado", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                if "seat_chart" in data:
                    escanos = data["seat_chart"]
                    total = sum(escanos.values())
                    
                    print(f"   ✅ Total escaños: {total}")
                    
                    # Mostrar top partidos
                    partidos_ordenados = sorted(escanos.items(), key=lambda x: x[1], reverse=True)
                    for i, (partido, seats) in enumerate(partidos_ordenados[:4]):
                        if seats > 0:
                            porcentaje = (seats/total)*100
                            print(f"   {i+1}. {partido}: {seats} ({porcentaje:.1f}%)")
                    
                    # Obtener datos del sistema
                    sistema_info = data.get("configuracion", {})
                    mr_seats = sistema_info.get("mr_seats", "N/A")
                    rp_seats = sistema_info.get("rp_seats", "N/A") 
                    
                    print(f"   Sistema: {mr_seats} MR + {rp_seats} RP")
                    
                    resultados.append({
                        "config": config["nombre"],
                        "plan": config["plan"],
                        "total": total,
                        "mr_seats": mr_seats,
                        "rp_seats": rp_seats,
                        "morena": escanos.get('MORENA', 0),
                        "pan": escanos.get('PAN', 0),
                        "pri": escanos.get('PRI', 0),
                        "success": True
                    })
                    
                else:
                    print("   ❌ No se encontró seat_chart en respuesta")
                    resultados.append({
                        "config": config["nombre"],
                        "plan": config["plan"], 
                        "success": False,
                        "error": "No seat_chart"
                    })
                    
            else:
                print(f"   ❌ Error HTTP {response.status_code}: {response.text}")
                resultados.append({
                    "config": config["nombre"],
                    "plan": config["plan"],
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            resultados.append({
                "config": config["nombre"],
                "plan": config["plan"],
                "success": False,
                "error": str(e)
            })
    
    # Tabla de resultados exitosos
    exitosos = [r for r in resultados if r.get("success", False)]
    
    if exitosos:
        print("\n" + "=" * 80)
        print("📋 TABLA COMPARATIVA - DIFERENTES PLANES ELECTORALES")
        print("=" * 80)
        print(f"{'PLAN':<25} | {'MR':<6} | {'RP':<6} | {'MORENA':<6} | {'PAN':<6} | {'PRI':<6} | {'TOTAL':<6}")
        print("-" * 80)
        
        for r in exitosos:
            print(f"{r['plan']:<25} | {str(r['mr_seats']):<6} | {str(r['rp_seats']):<6} | {r['morena']:<6} | {r['pan']:<6} | {r['pri']:<6} | {r['total']:<6}")
        
        # Análisis de variaciones
        print("\n🔍 ANÁLISIS DE VARIACIONES:")
        print("-" * 40)
        
        morena_values = [r['morena'] for r in exitosos]
        pan_values = [r['pan'] for r in exitosos]
        
        if len(morena_values) > 1:
            morena_min, morena_max = min(morena_values), max(morena_values)
            pan_min, pan_max = min(pan_values), max(pan_values)
            
            print(f"MORENA: rango {morena_min}-{morena_max} escaños (variación: {morena_max-morena_min})")
            print(f"PAN: rango {pan_min}-{pan_max} escaños (variación: {pan_max-pan_min})")
            
            if morena_max - morena_min > 0 or pan_max - pan_min > 0:
                print("✅ Los diferentes planes SÍ producen variaciones en escaños")
            else:
                print("❌ Los planes no muestran variaciones significativas")
        
        # Comparación específica Plan C vs Vigente vs Plan A
        plan_c = next((r for r in exitosos if r['plan'] == 'plan_c'), None)
        vigente = next((r for r in exitosos if r['plan'] == 'vigente'), None)
        plan_a = next((r for r in exitosos if r['plan'] == 'plan_a'), None)
        
        if plan_c and vigente and plan_a:
            print(f"\n🔄 COMPARACIÓN CLAVE:")
            print(f"Plan C (MR puro):    MORENA {plan_c['morena']}, PAN {plan_c['pan']}, PRI {plan_c['pri']}")
            print(f"Vigente (MR+PM+RP):  MORENA {vigente['morena']}, PAN {vigente['pan']}, PRI {vigente['pri']}")
            print(f"Plan A (RP puro):    MORENA {plan_a['morena']}, PAN {plan_a['pan']}, PRI {plan_a['pri']}")
            
            # Calcular diferencias
            diff_c_vigente = vigente['morena'] - plan_c['morena']
            diff_vigente_a = plan_a['morena'] - vigente['morena']
            
            print(f"\nImpacto de Primera Minoría:")
            print(f"- MR puro → MR+PM+RP: MORENA {diff_c_vigente:+d} escaños")
            print(f"- MR+PM+RP → RP puro: MORENA {diff_vigente_a:+d} escaños")
    
    else:
        print("\n❌ No se obtuvieron resultados exitosos")
    
    # Resumen de errores
    errores = [r for r in resultados if not r.get("success", False)]
    if errores:
        print(f"\n⚠️  Se encontraron {len(errores)} errores:")
        for r in errores:
            print(f"   - {r['config']}: {r.get('error', 'Error desconocido')}")
    
    print(f"\n✅ TEST COMPLETADO: {len(exitosos)}/{len(resultados)} configuraciones exitosas")
    
    return exitosos

if __name__ == "__main__":
    print("🚀 Iniciando test del slider de Primera Minoría...")
    print("📡 Asegúrate de que el servidor esté corriendo en http://localhost:8001")
    print()
    
    try:
        # Verificar que el servidor esté disponible
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Servidor conectado correctamente")
            test_api_primera_minoria()
        else:
            print(f"❌ Servidor no responde correctamente: {response.status_code}")
    except Exception as e:
        print(f"❌ No se puede conectar al servidor: {e}")
        print("💡 Ejecuta 'python main.py' en otra terminal primero")
