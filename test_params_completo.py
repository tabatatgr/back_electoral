#!/usr/bin/env python3
"""
Test completo de parámetros personalizados
"""

def test_todos_los_parametros():
    print(" TEST COMPLETO DE PARÁMETROS PERSONALIZADOS")
    print("=" * 60)
    
    # Test cases problemáticos
    test_cases = [
        {
            "nombre": "Usuario quiere 10 escaños total (mixto)",
            "sistema": "mixto",
            "escanos_totales": 10,
            "mr_seats": None,
            "rp_seats": None,
            "umbral": 0.0
        },
        {
            "nombre": "Usuario quiere 10 escaños total con MR/RP específicos",
            "sistema": "mixto", 
            "escanos_totales": 10,
            "mr_seats": 3,
            "rp_seats": 7,
            "umbral": 0.0
        },
        {
            "nombre": "Usuario quiere solo RP (100 total)",
            "sistema": "rp",
            "escanos_totales": 100,
            "mr_seats": None,
            "rp_seats": None,
            "umbral": 0.05
        },
        {
            "nombre": "Usuario especifica MR/RP sin total",
            "sistema": "mixto",
            "escanos_totales": None,
            "mr_seats": 50,
            "rp_seats": 25,
            "umbral": 0.01
        }
    ]
    
    for test in test_cases:
        print(f"\n📋 {test['nombre']}:")
        
        # Simular nueva lógica
        sistema_final = test["sistema"]
        escanos_totales = test["escanos_totales"]
        mr_seats = test["mr_seats"]
        rp_seats = test["rp_seats"]
        umbral = test["umbral"]
        
        # Aplicar nueva lógica inteligente
        if escanos_totales is not None:
            max_seats = escanos_totales
            if mr_seats is None and rp_seats is None:
                if sistema_final == "mr":
                    mr_seats_final = max_seats
                    rp_seats_final = 0
                elif sistema_final == "rp":
                    mr_seats_final = 0
                    rp_seats_final = max_seats
                else:  # mixto
                    proportion_mr = 300 / 500
                    mr_seats_final = int(max_seats * proportion_mr)
                    rp_seats_final = max_seats - mr_seats_final
            else:
                mr_seats_final = mr_seats if mr_seats is not None else 0
                rp_seats_final = rp_seats if rp_seats is not None else 0
        else:
            mr_seats_final = mr_seats if mr_seats is not None else 300
            rp_seats_final = rp_seats if rp_seats is not None else 200
            max_seats = mr_seats_final + rp_seats_final
        
        umbral_final = umbral if umbral is not None else 0.03
        
        print(f"   📥 Input:")
        print(f"      sistema={sistema_final}, escanos_totales={escanos_totales}")
        print(f"      mr_seats={mr_seats}, rp_seats={rp_seats}, umbral={umbral}")
        print(f"   📤 Output:")
        print(f"      max_seats={max_seats}, mr_seats={mr_seats_final}")
        print(f"      rp_seats={rp_seats_final}, umbral={umbral_final}")
        
        # Verificar coherencia
        suma = mr_seats_final + rp_seats_final
        if suma != max_seats:
            print(f"    ADVERTENCIA: MR+RP ({suma}) ≠ total ({max_seats})")
        else:
            print(f"   ✅ Configuración coherente")

if __name__ == "__main__":
    test_todos_los_parametros()
