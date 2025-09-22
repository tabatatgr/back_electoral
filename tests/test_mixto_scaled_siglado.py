import os
import tempfile
import pandas as pd
import numpy as np
from engine.procesar_diputados_v2 import procesar_diputados_v2


def make_dummy_parquet(path):
    # Crear DataFrame con columnas mínimas que el pipeline espera
    partidos = ['PAN','PRI','PRD','PVEM','PT','MC','MORENA']
    rows = []
    # crear 10 distritos por 3 entidades = 30 filas
    entidades = ['ENT1','ENT2','ENT3']
    for ent in entidades:
        for d in range(1,11):
            row = {p: np.random.randint(1000,100000) for p in partidos}
            row['ENTIDAD'] = ent
            row['DISTRITO'] = d
            # columna dominante para scale_siglado
            row['DOMINANTE'] = max(partidos, key=lambda p: row[p])
            rows.append(row)
    df = pd.DataFrame(rows)
    df.to_parquet(path)


def test_mixto_scale_siglado_smoke(tmp_path):
    parquet = tmp_path / "dummy.parquet"
    make_dummy_parquet(str(parquet))

    # pedir MR objetivo menor que el total de distritos (30) -> probar up/downscale
    mr_target = 20
    max_seats = 100

    res = procesar_diputados_v2(
        path_parquet=str(parquet),
        partidos_base=['PAN','PRI','PRD','PVEM','PT','MC','MORENA'],
        anio=2024,
        path_siglado=None,
        max_seats=max_seats,
        sistema='mixto',
        mr_seats=mr_target,
        rp_seats=None,
        seed=42,
        print_debug=False
    )

    assert isinstance(res, dict)
    # meta debe existir y ser un dict
    assert 'meta' in res and isinstance(res['meta'], dict)

    # extraer totales mr/rp/tot en varias claves posibles
    tot = res.get('tot') or res.get('totales') or res.get('tot_dict')
    mr = res.get('mr') or res.get('mr_dict')

    # Debe devolver diccionarios de asientos por partido
    assert isinstance(tot, dict) or tot is None
    assert isinstance(mr, dict) or mr is None

    # Si tot está presente, comprobar que cubre los partidos y que la suma está cerca de max_seats
    if isinstance(tot, dict):
        assert len(tot) == len(['PAN','PRI','PRD','PVEM','PT','MC','MORENA'])
        total_assigned = sum(int(v) for v in tot.values())
        # permitir pequeñas diferencias por ajustes internos (tolerancia 5 escaños)
        assert abs(total_assigned - max_seats) <= 5

    # Si MR está presente, asegurar que hay asignaciones no negativas
    if isinstance(mr, dict):
        assert all(int(v) >= 0 for v in mr.values())
