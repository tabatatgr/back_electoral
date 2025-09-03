#!/usr/bin/env python3
"""
Test local de la lógica de parámetros personalizados
"""

def test_parametros_logica():
    print("🧪 TEST LÓGICA DE PARÁMETROS PERSONALIZADOS")
    print("=" * 50)
    
    # Simular parámetros que podrían llegar del frontend
    test_cases = [
        {"nombre": "Con 0 explícito", "mr_seats": 0, "rp_seats": 300},
        {"nombre": "Con None", "mr_seats": None, "rp_seats": None},
        {"nombre": "Con valores normales", "mr_seats": 100, "rp_seats": 200},
        {"nombre": "Solo MR", "mr_seats": 400, "rp_seats": 0},
    ]
    
    for test in test_cases:
        print(f"\n📋 {test['nombre']}:")
        mr_seats = test["mr_seats"]
        rp_seats = test["rp_seats"]
        
        # Lógica INCORRECTA (or)
        mr_final_incorrecto = mr_seats or 300
        rp_final_incorrecto = rp_seats or 200
        
        # Lógica CORRECTA (is not None)
        mr_final_correcto = mr_seats if mr_seats is not None else 300
        rp_final_correcto = rp_seats if rp_seats is not None else 200
        
        print(f"   Input: mr_seats={mr_seats}, rp_seats={rp_seats}")
        print(f"   ❌ Lógica OR: mr={mr_final_incorrecto}, rp={rp_final_incorrecto}")
        print(f"   ✅ Lógica IS NOT NONE: mr={mr_final_correcto}, rp={rp_final_correcto}")
        
        if mr_final_incorrecto != mr_final_correcto or rp_final_incorrecto != rp_final_correcto:
            print(f"   🚨 DIFERENCIA DETECTADA!")

if __name__ == "__main__":
    test_parametros_logica()
