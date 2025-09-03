#!/usr/bin/env python3
"""
Test del Slider con Validaciones Lógicas
Prueba configuraciones electorales con diferentes números de escaños
incluyendo validaciones de coherencia lógica
"""

import sys
sys.path.append('.')

from engine.procesar_senadores_v2 import procesar_senadores_v2
from validador_configuraciones import validar_configuracion_electoral, mostrar_validacion

def test_configuraciones_personalizadas():
    """
    Prueba configuraciones electorales personalizadas
    con validaciones lógicas completas
    """
    
    print("🎯 TEST DE CONFIGURACIONES PERSONALIZADAS")
    print("=" * 60)
    print("Probando diferentes números de escaños con validaciones")
    print()
    
    # Configuraciones de prueba
    configuraciones = [
        # ✅ CONFIGURACIONES VÁLIDAS
        {
            "nombre": "📊 200 ESCAÑOS BALANCEADO",
            "sistema": "mixto",
            "max_seats": 200,
            "mr_seats": 120,
            "rp_seats": 80,
            "pm_seats": 40,
            "descripcion": "200 escaños: 120 MR (40 PM) + 80 RP"
        },
        {
            "nombre": "📊 200 ESCAÑOS CON MÁS MR",
            "sistema": "mixto", 
            "max_seats": 200,
            "mr_seats": 150,
            "rp_seats": 50,
            "pm_seats": 50,
            "descripcion": "200 escaños: 150 MR (50 PM) + 50 RP"
        },
        {
            "nombre": "📊 300 ESCAÑOS GRANDE",
            "sistema": "mixto",
            "max_seats": 300,
            "mr_seats": 200,
            "rp_seats": 100,
            "pm_seats": 80,
            "descripcion": "300 escaños: 200 MR (80 PM) + 100 RP"
        },
        {
            "nombre": "📊 150 MR PURO",
            "sistema": "mr",
            "max_seats": 150,
            "pm_seats": 50,
            "descripcion": "150 escaños MR puro con 50 PM"
        },
        
        # ❌ CONFIGURACIONES INVÁLIDAS (para probar validaciones)
        {
            "nombre": "❌ PM MAYOR QUE MR",
            "sistema": "mixto",
            "max_seats": 200,
            "mr_seats": 120,
            "rp_seats": 80,
            "pm_seats": 130,
            "descripcion": "PM (130) > MR (120) - INVÁLIDO"
        },
        {
            "nombre": "❌ MR + RP ≠ TOTAL",
            "sistema": "mixto",
            "max_seats": 200,
            "mr_seats": 120,
            "rp_seats": 90,  # 120 + 90 = 210 ≠ 200
            "pm_seats": 40,
            "descripcion": "MR + RP ≠ Total - INVÁLIDO"
        },
        {
            "nombre": "❌ PM MAYOR QUE TOTAL MR",
            "sistema": "mr",
            "max_seats": 100,
            "pm_seats": 120,
            "descripcion": "PM > Total MR - INVÁLIDO"
        }
    ]
    
    resultados_validos = []
    
    for config in configuraciones:
        print(f"🔬 {config['nombre']}")
        print(f"   {config['descripcion']}")
        print("-" * 50)
        
        # 1️⃣ VALIDAR CONFIGURACIÓN
        validacion = validar_configuracion_electoral(
            sistema=config["sistema"],
            max_seats=config["max_seats"],
            mr_seats=config.get("mr_seats"),
            rp_seats=config.get("rp_seats"),
            pm_seats=config.get("pm_seats")
        )
        
        es_valida = mostrar_validacion(validacion)
        
        # 2️⃣ SI ES VÁLIDA, EJECUTAR PROCESAMIENTO
        if es_valida:
            print("🚀 EJECUTANDO PROCESAMIENTO...")
            try:
                # Parámetros base
                params = {
                    "path_parquet": "data/computos_senado_2018.parquet",
                    "anio": 2018,
                    "path_siglado": "data/siglado_senado_2018_corregido.csv",
                    "sistema": config["sistema"],
                    "max_seats": config["max_seats"],
                    "umbral": 0.03
                }
                
                # Agregar parámetros específicos
                if config["sistema"] == "mixto":
                    params["mr_seats"] = config["mr_seats"]
                    params["rp_seats"] = config["rp_seats"]
                
                if config.get("pm_seats") is not None:
                    params["pm_seats"] = config["pm_seats"]
                
                # Ejecutar
                resultado = procesar_senadores_v2(**params)
                
                if resultado and "tot" in resultado:
                    totales = resultado["tot"]
                    total_escanos = sum(totales.values())
                    morena = totales.get('MORENA', 0)
                    pan = totales.get('PAN', 0)
                    pri = totales.get('PRI', 0)
                    
                    print(f"✅ RESULTADO EXITOSO:")
                    print(f"   📊 Total: {total_escanos} escaños")
                    print(f"   🔴 MORENA: {morena} ({morena/total_escanos*100:.1f}%)")
                    print(f"   🔵 PAN: {pan} ({pan/total_escanos*100:.1f}%)")
                    print(f"   🟢 PRI: {pri} ({pri/total_escanos*100:.1f}%)")
                    
                    # Verificar coherencia
                    if total_escanos == config["max_seats"]:
                        print(f"   ✅ Total correcto: {total_escanos} = {config['max_seats']}")
                    else:
                        print(f"   ⚠️ Discrepancia: {total_escanos} ≠ {config['max_seats']}")
                    
                    resultados_validos.append({
                        "config": config,
                        "resultado": resultado,
                        "totales": totales,
                        "total_escanos": total_escanos
                    })
                
                else:
                    print("❌ Error en procesamiento: resultado vacío")
                    
            except Exception as e:
                print(f"❌ Error en procesamiento: {e}")
        
        else:
            print("❌ CONFIGURACIÓN INVÁLIDA - NO SE EJECUTA")
        
        print()
    
    # 3️⃣ RESUMEN DE RESULTADOS VÁLIDOS
    if resultados_validos:
        print("📈 RESUMEN DE CONFIGURACIONES EXITOSAS")
        print("=" * 60)
        
        for resultado in resultados_validos:
            config = resultado["config"]
            totales = resultado["totales"]
            total = resultado["total_escanos"]
            
            print(f"✅ {config['nombre']}")
            print(f"   Total: {total} | MORENA: {totales.get('MORENA', 0)} | PAN: {totales.get('PAN', 0)} | PRI: {totales.get('PRI', 0)}")
        
        print()
        print(f"🎉 {len(resultados_validos)} configuraciones exitosas de {len(configuraciones)} probadas")
    
    else:
        print("❌ No se encontraron configuraciones válidas")

def test_limites_primera_minoria():
    """
    Prueba específica de los límites de primera minoría
    """
    
    print("🔥 TEST DE LÍMITES DE PRIMERA MINORÍA")
    print("=" * 50)
    
    # Configuración base: 200 escaños mixto
    base_config = {
        "sistema": "mixto",
        "max_seats": 200,
        "mr_seats": 120,
        "rp_seats": 80
    }
    
    # Diferentes valores de PM para probar límites
    pm_valores = [0, 20, 40, 60, 80, 100, 120, 140]  # Último es inválido
    
    print(f"📊 Configuración base: {base_config['mr_seats']} MR + {base_config['rp_seats']} RP = {base_config['max_seats']} total")
    print(f"🔥 Probando PM desde 0 hasta {max(pm_valores)} (límite = {base_config['mr_seats']})")
    print()
    
    resultados_pm = []
    
    for pm in pm_valores:
        print(f"🧪 PM = {pm}")
        print("-" * 20)
        
        # Validar
        validacion = validar_configuracion_electoral(
            sistema=base_config["sistema"],
            max_seats=base_config["max_seats"],
            mr_seats=base_config["mr_seats"],
            rp_seats=base_config["rp_seats"],
            pm_seats=pm
        )
        
        if validacion["valid"]:
            try:
                params = {
                    "path_parquet": "data/computos_senado_2018.parquet",
                    "anio": 2018,
                    "path_siglado": "data/siglado_senado_2018_corregido.csv",
                    **base_config,
                    "pm_seats": pm,
                    "umbral": 0.03
                }
                
                resultado = procesar_senadores_v2(**params)
                totales = resultado["tot"]
                morena = totales.get('MORENA', 0)
                
                print(f"   ✅ MORENA: {morena} escaños")
                resultados_pm.append({"pm": pm, "morena": morena})
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
        else:
            print(f"   ❌ Configuración inválida:")
            for error in validacion["errors"]:
                print(f"      {error}")
        
        print()
    
    # Mostrar tendencia
    if len(resultados_pm) > 1:
        print("📈 TENDENCIA DE PRIMERA MINORÍA:")
        print("-" * 40)
        for resultado in resultados_pm:
            pm = resultado["pm"]
            morena = resultado["morena"]
            print(f"   PM={pm:3d} → MORENA={morena:3d} escaños")
        
        # Calcular efecto
        base = resultados_pm[0]["morena"]  # PM = 0
        print()
        print("🔄 EFECTO DE LA PM:")
        for resultado in resultados_pm[1:]:
            pm = resultado["pm"]
            morena = resultado["morena"]
            diferencia = morena - base
            print(f"   PM={pm:3d} → {diferencia:+3d} escaños vs PM=0")

if __name__ == "__main__":
    test_configuraciones_personalizadas()
    print()
    test_limites_primera_minoria()
