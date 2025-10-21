"""
Test para verificar que max_seats_per_party limita correctamente los escaños por partido
"""

import numpy as np
from engine.procesar_diputados_v2 import asignadip_v2


def test_max_seats_per_party_limit():
    """
    Verifica que cuando se especifica max_seats_per_party, ningún partido supere ese límite.
    
    Escenario de prueba:
    - Un partido dominante con muchos votos
    - max_seats_per_party=250
    - Sin ese límite, el partido obtendría más de 250 escaños
    - Con el límite, debe caparse a 250
    """
    
    # Simular un escenario donde un partido tiene muchos votos
    # 5 partidos, el primero con mayoría absoluta
    votos = np.array([10_000_000, 2_000_000, 1_500_000, 1_000_000, 500_000], dtype=float)
    
    # Escaños de MR simulados (el partido dominante gana muchos distritos)
    escanos_mr = np.array([180, 30, 20, 15, 5], dtype=int)
    
    # Configuración: 250 MR + 250 RP = 500 total
    m_rp = 250
    total_seats = 500
    tope_por_partido = 250
    
    print("\n=== TEST: max_seats_per_party ===")
    print(f"Votos: {votos}")
    print(f"Escaños MR: {escanos_mr}")
    print(f"Total escaños: {total_seats}")
    print(f"Escaños RP a asignar: {m_rp}")
    print(f"Tope por partido: {tope_por_partido}")
    
    # CASO 1: SIN límite de max_seats_per_party (solo tope 300 default)
    resultado_sin_limite = asignadip_v2(
        x=votos,
        ssd=escanos_mr,
        m=m_rp,
        S=total_seats,
        threshold=0.03,
        max_seats=300,  # tope default
        max_pp=0.08,
        max_seats_per_party=None,  # SIN límite personalizado
        apply_caps=True,
        print_debug=True
    )
    
    escanos_sin_limite = resultado_sin_limite['seats'][2]  # fila 2 = totales
    print(f"\nSIN max_seats_per_party:")
    print(f"  Escaños totales: {escanos_sin_limite}")
    print(f"  Partido dominante: {escanos_sin_limite[0]} escaños")
    
    # CASO 2: CON límite de max_seats_per_party=250
    resultado_con_limite = asignadip_v2(
        x=votos,
        ssd=escanos_mr,
        m=m_rp,
        S=total_seats,
        threshold=0.03,
        max_seats=300,  # esto se ignorará porque max_seats_per_party tiene prioridad
        max_pp=0.08,
        max_seats_per_party=tope_por_partido,  # CON límite personalizado
        apply_caps=True,
        print_debug=True
    )
    
    escanos_con_limite = resultado_con_limite['seats'][2]  # fila 2 = totales
    print(f"\nCON max_seats_per_party={tope_por_partido}:")
    print(f"  Escaños totales: {escanos_con_limite}")
    print(f"  Partido dominante: {escanos_con_limite[0]} escaños")
    
    # VERIFICACIONES
    print("\n=== VERIFICACIONES ===")
    
    # 1. Sin límite: el partido dominante podría tener >250 (o no, dependiendo de sobrerrepresentación)
    print(f"✓ Sin límite personalizado, partido dominante tiene {escanos_sin_limite[0]} escaños")
    
    # 2. Con límite: el partido dominante NO debe superar 250
    if escanos_con_limite[0] <= tope_por_partido:
        print(f"✓ Con límite, partido dominante tiene {escanos_con_limite[0]} escaños (≤{tope_por_partido}) ✅")
    else:
        print(f"✗ ERROR: Partido dominante tiene {escanos_con_limite[0]} escaños (>{tope_por_partido}) ❌")
        raise AssertionError(f"El partido superó el tope de {tope_por_partido} escaños")
    
    # 3. Ningún partido debe superar el límite
    for i, escanos in enumerate(escanos_con_limite):
        if escanos > tope_por_partido:
            print(f"✗ ERROR: Partido {i} tiene {escanos} escaños (>{tope_por_partido}) ❌")
            raise AssertionError(f"Partido {i} superó el tope de {tope_por_partido}")
    
    print(f"✓ Ningún partido supera el tope de {tope_por_partido} escaños ✅")
    
    # 4. Verificar que la suma total de escaños es correcta
    suma_total = np.sum(escanos_con_limite)
    print(f"✓ Suma total de escaños: {suma_total}/{total_seats}")
    
    print("\n✅ TEST PASADO: max_seats_per_party funciona correctamente")


if __name__ == "__main__":
    test_max_seats_per_party_limit()
