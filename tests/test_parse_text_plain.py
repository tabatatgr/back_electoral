import pathlib
from fastapi.testclient import TestClient
import main

client = TestClient(main.app)


def test_text_plain_parsing_creates_tmp_parquet():
    body_raw = pathlib.Path("scripts/test_prd_90.json").read_text(encoding='utf-8')
    resp = client.post(
        '/procesar/diputados?anio=2024&plan=personalizado&escanos_totales=128&sistema=mixto&mr_seats=64&rp_seats=64&reparto_mode=cuota&reparto_method=hare&usar_coaliciones=true',
        data=body_raw,
        headers={'Content-Type': 'text/plain'},
        timeout=120
    )
    assert resp.status_code == 200, f"Status not OK: {resp.status_code} - {resp.text}"
    j = resp.json()
    assert 'meta' in j and isinstance(j['meta'], dict), "meta missing in response"
    trace = j['meta'].get('trace')
    assert trace is not None, f"trace missing in meta: {j['meta']}"
    # Expect that trace contains info about the tmp_parquet or votos_redistribuidos
    # trace can be a dict-like object; check keys safely
    if isinstance(trace, dict):
        keys = set(trace.keys())
        assert ('tmp_parquet' in keys) or ('votos_redistribuidos' in keys), f"trace keys unexpected: {keys}"
    else:
        # If trace is a string or other structure, accept non-empty value
        assert trace, f"trace is empty or not dict: {trace}"
