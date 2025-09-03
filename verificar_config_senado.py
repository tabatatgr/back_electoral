#!/usr/bin/env python3
"""
Test rápido de configuraciones de Senado
"""

def mostrar_configuraciones_senado():
    print("🏛️ CONFIGURACIONES DE SENADO")
    print("=" * 50)
    
    configs = {
        "vigente": {
            "descripcion": "Sistema vigente: 64 MR + 32 PM + 32 RP = 128 total",
            "sistema": "mixto",
            "mr_seats": 96,  # 64 MR + 32 PM
            "rp_seats": 32,  # 32 RP
            "max_seats": 128,
            "umbral": 0.03,
            "usar_siglado_mr": True
        },
        "plan_a": {
            "descripcion": "Plan A: solo RP = 128 total",
            "sistema": "rp", 
            "mr_seats": 0,
            "rp_seats": 128,
            "max_seats": 128,
            "umbral": 0.03,
            "usar_siglado_mr": False
        },
        "plan_c": {
            "descripcion": "Plan C: solo MR+PM = 128 total",
            "sistema": "mr",
            "mr_seats": 128,  # Todos como MR+PM
            "rp_seats": 0,
            "max_seats": 128,
            "umbral": 0.0,
            "usar_siglado_mr": True
        }
    }
    
    for plan, config in configs.items():
        print(f"\n📋 {plan.upper()}:")
        print(f"   {config['descripcion']}")
        print(f"   Sistema: {config['sistema']}")
        print(f"   MR+PM: {config['mr_seats']}")
        print(f"   RP: {config['rp_seats']}")
        print(f"   Total: {config['max_seats']}")
        print(f"   Umbral: {config['umbral']}")
        print(f"   Usar siglado MR: {config['usar_siglado_mr']}")
        
        # Verificar que las sumas sean correctas
        total_calculado = config['mr_seats'] + config['rp_seats']
        if total_calculado != config['max_seats']:
            print(f"   ⚠️  ERROR: suma {total_calculado} ≠ max_seats {config['max_seats']}")
        else:
            print(f"   ✅ Suma correcta: {total_calculado}")

if __name__ == "__main__":
    mostrar_configuraciones_senado()
