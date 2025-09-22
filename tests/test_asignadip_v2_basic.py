import numpy as np

from engine.procesar_diputados_v2 import asignadip_v2


def test_asignadip_v2_sum_matches_S():
    # Escenario simple con 3 partidos y MR ya asignados
    x = np.array([1000.0, 800.0, 200.0])
    ssd = np.array([2, 1, 0])

    # Queremos que el total S sea 10
    S = 10
    m = S - int(np.sum(ssd))

    resultado = asignadip_v2(
        x=x,
        ssd=ssd,
        m=m,
        S=S,
        threshold=0.0,
        max_seats=300,
        apply_caps=False,
        seed=42,
        print_debug=False,
    )

    seats = resultado['seats']

    total = int(np.sum(seats[2]))
    assert total == S, f"Total seats {total} != expected {S}"
