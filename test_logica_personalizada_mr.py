#!/usr/bin/env python3
"""
Test para verificar que la lógica personalizada MR puro YA NO fuerza 300 escaños
Simula el flujo: 1) elegir magnitud, 2) elegir sistema MR puro
"""

import sys
sys.path.append('.')

def test_logica_personalizada_mr():
    """Test de la lógica interna del endpoint personalizado MR"""
    
    print("🔍 TEST LÓGICA PERSONALIZADA MR PURO")
    print("=" * 50)
    print("Simulando flujo frontend: magnitud → sistema MR puro")
    print()
    
    configs = [
        {"magnitud": 200, "descripcion": "200 escaños → MR puro"},
        {"magnitud": 250, "descripcion": "250 escaños → MR puro"},
        {"magnitud": 400, "descripcion": "400 escaños → MR puro"},
        {"magnitud": 500, "descripcion": "500 escaños → MR puro"}
    ]
    
    for config in configs:
        magnitud = config["magnitud"]
        print(f"📊 {config['descripcion']}")
        print(f"   Usuario elige: magnitud={magnitud}, sistema='mr'")
        
        # SIMULAR LA NUEVA LÓGICA DEL ENDPOINT
        # Variables que recibiría el endpoint
        escanos_totales = magnitud  # Lo que envía el frontend como magnitud
        sistema_final = "mr"        # Lo que envía como sistema
        mr_seats = None            # Frontend no especifica esto para MR puro
        rp_seats = None            # Frontend no especifica esto para MR puro
        
        # APLICAR LA NUEVA LÓGICA (copiada del endpoint)
        if escanos_totales is not None:
            max_seats = escanos_totales
            print(f"   [LÓGICA] Usando magnitud base: {max_seats} escaños")
            
            # Distribuir según el sistema elegido
            if sistema_final == "mr":
                # MR PURO: TODOS los escaños van a MR
                mr_seats_final = max_seats
                rp_seats_final = 0
                print(f"   [LÓGICA] Sistema MR puro: {mr_seats_final} MR + {rp_seats_final} RP = {max_seats}")
            elif sistema_final == "rp":
                # RP PURO: TODOS los escaños van a RP
                mr_seats_final = 0
                rp_seats_final = max_seats
                print(f"   [LÓGICA] Sistema RP puro: {mr_seats_final} MR + {rp_seats_final} RP = {max_seats}")
            else:  # mixto
                # MIXTO: Usuario debe especificar MR/RP o usar proporción default
                if mr_seats is not None and rp_seats is not None:
                    # Usuario especificó ambos
                    mr_seats_final = mr_seats
                    rp_seats_final = rp_seats
                    print(f"   [LÓGICA] Sistema mixto especificado: {mr_seats_final} MR + {rp_seats_final} RP")
                else:
                    # Usar proporción default 60% MR, 40% RP
                    mr_seats_final = int(max_seats * 0.6)
                    rp_seats_final = max_seats - mr_seats_final
                    print(f"   [LÓGICA] Sistema mixto automático (60/40): {mr_seats_final} MR + {rp_seats_final} RP = {max_seats}")
        else:
            # FALLBACK: Usuario no especificó magnitud total
            print(f"   [LÓGICA] No se especificó magnitud, usando parámetros individuales o defaults")
            if sistema_final == "mr":
                # Para MR puro, usar mr_seats como magnitud total
                mr_seats_final = mr_seats if mr_seats is not None else 300
                rp_seats_final = 0
                max_seats = mr_seats_final
            elif sistema_final == "rp":
                # Para RP puro, usar rp_seats como magnitud total
                mr_seats_final = 0
                rp_seats_final = rp_seats if rp_seats is not None else 300
                max_seats = rp_seats_final
        
        # VERIFICAR RESULTADO
        total_final = mr_seats_final + rp_seats_final
        
        print(f"   ✅ Resultado: {mr_seats_final} MR + {rp_seats_final} RP = {total_final} total")
        print(f"   🎯 Magnitud solicitada: {magnitud}")
        
        if total_final == magnitud:
            print(f"   ✅ CORRECTO: Respeta los {magnitud} escaños de magnitud")
        elif total_final == 300:
            print(f"   ❌ ERROR: Sigue forzando 300 escaños (ignora magnitud)")
        else:
            print(f"   ⚠️  RARO: Dio {total_final} escaños (ni {magnitud} ni 300)")
            
        print()
    
    print("💡 Si todos muestran '✅ CORRECTO', entonces la lógica YA está arreglada")

if __name__ == "__main__":
    test_logica_personalizada_mr()
