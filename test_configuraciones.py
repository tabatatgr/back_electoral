#!/usr/bin/env python3
"""
Script de prueba para verificar los parámetros específicos de cada plan
"""

import sys
import os
sys.path.append(os.path.abspath('.'))

from engine.procesar_diputados_v3 import configurar_plan_diputados

def test_configuraciones():
    """Prueba las configuraciones de cada plan"""
    
    planes = ["vigente", "plan_a", "plan_c"]
    anio = 2024
    
    print("=" * 60)
    print("CONFIGURACIONES DE PLANES DE DIPUTADOS")
    print("=" * 60)
    
    for plan in planes:
        print(f"\n🔸 PLAN: {plan.upper()}")
        print("-" * 30)
        
        config = configurar_plan_diputados(plan, anio)
        
        for key, value in config.items():
            print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("RESUMEN DE DIFERENCIAS CLAVE:")
    print("=" * 60)
    
    vigente = configurar_plan_diputados("vigente", anio)
    plan_a = configurar_plan_diputados("plan_a", anio)
    plan_c = configurar_plan_diputados("plan_c", anio)
    
    print(f" VIGENTE: {vigente['max_seats']} escaños ({vigente['mr_seats']} MR + {vigente['rp_seats']} RP)")
    print(f"   └─ Territorial: {vigente['territorial_scope']}")
    print(f"   └─ Umbral: {vigente['umbral']}")
    print(f"   └─ Tope: {vigente['max_seats_per_party']}")
    print(f"   └─ Sobrerrepresentación: {vigente['apply_overrep_cap']}")
    
    print(f"\n PLAN A: {plan_a['max_seats']} escaños ({plan_a['mr_seats']} MR + {plan_a['rp_seats']} RP)")
    print(f"   └─ Territorial: {plan_a['territorial_scope']}")
    print(f"   └─ Umbral: {plan_a['umbral']}")
    print(f"   └─ Tope: {plan_a['max_seats_per_party']}")
    print(f"   └─ Sobrerrepresentación: {plan_a['apply_overrep_cap']}")
    
    print(f"\n PLAN C: {plan_c['max_seats']} escaños ({plan_c['mr_seats']} MR + {plan_c['rp_seats']} RP)")
    print(f"   └─ Territorial: {plan_c['territorial_scope']}")
    print(f"   └─ Umbral: {plan_c['umbral']}")
    print(f"   └─ Tope: {plan_c['max_seats_per_party']}")
    print(f"   └─ Sobrerrepresentación: {plan_c['apply_overrep_cap']}")

if __name__ == "__main__":
    test_configuraciones()
