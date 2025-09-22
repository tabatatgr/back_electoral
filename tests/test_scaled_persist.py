import os
from engine.procesar_diputados_v2 import procesar_diputados_v2


def make_dummy_parquet(path):
    import pandas as pd
    df = pd.DataFrame({
        'ENTIDAD': ['A'] * 30,
        'DISTRITO': list(range(1, 31)),
        'PAN': [100] * 30,
        'PRI': [80] * 30,
        'PRD': [10] * 30,
        'PVEM': [5] * 30,
        'PT': [2] * 30,
        'MC': [3] * 30,
        'MORENA': [200] * 30,
    })
    df.to_parquet(path)


def test_scaled_persist_creates_file(tmp_path, monkeypatch):
    parquet = tmp_path / "dummy.parquet"
    make_dummy_parquet(str(parquet))

    # Forzar persistencia ON
    monkeypatch.setenv('SCALED_SIGLADO_PERSIST', '1')

    # Forzar MR-only para activar el escalado y generar scaled_info
    res = procesar_diputados_v2(
        path_parquet=str(parquet),
        partidos_base=['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA'],
        anio=2024,
        path_siglado=None,
        max_seats=20,
        sistema='mr',
        mr_seats=None,
        rp_seats=None,
        seed=42,
        print_debug=False
    )

    assert isinstance(res, dict)
    meta = res.get('meta', {})
    assert isinstance(meta, dict)
    si = meta.get('scaled_info')
    assert si is not None, "scaled_info must exist"

    path = si.get('scaled_csv_path')
    assert path is not None, "scaled_csv_path must be present when persistence is on"
    assert os.path.exists(path), f"scaled csv file not found at {path}"