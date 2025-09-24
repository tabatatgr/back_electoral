import pathlib
from fastapi.testclient import TestClient
import main

client = TestClient(main.app)


def test_text_plain_sets_raw_body_parsed_flag():
    # Use same test body as existing test to simulate malformed Content-Type
    body_raw = pathlib.Path("scripts/test_prd_90.json").read_text(encoding='utf-8')
    resp = client.post(
        '/procesar/diputados?anio=2024&plan=personalizado&escanos_totales=128&sistema=mixto&mr_seats=64&rp_seats=64&reparto_mode=cuota&reparto_method=hare&usar_coaliciones=true',
        data=body_raw,
        headers={'Content-Type': 'text/plain'},
        timeout=120
    )
    assert resp.status_code == 200, f"Status not OK: {resp.status_code} - {resp.text}"
    j = resp.json()
    trace = j.get('meta', {}).get('trace', {})
    # When heuristics are used, raw_body_parsed should be True
    assert isinstance(trace, dict), f"trace not a dict: {trace}"
    assert trace.get('raw_body_parsed') is True, f"expected raw_body_parsed True, got: {trace.get('raw_body_parsed')}"


def test_form_urlencoded_sets_raw_body_parsed_flag():
    # Simulate a frontend that sends form-encoded party percentages like PRD=90&PAN=5
    form = 'PRD=90&PAN=5'
    resp = client.post(
        '/procesar/diputados?anio=2024&plan=personalizado&escanos_totales=128&sistema=mixto&mr_seats=64&rp_seats=64&reparto_mode=cuota&reparto_method=hare&usar_coaliciones=true',
        data=form,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        timeout=120
    )
    assert resp.status_code == 200, f"Status not OK: {resp.status_code} - {resp.text}"
    j = resp.json()
    trace = j.get('meta', {}).get('trace', {})
    assert isinstance(trace, dict), f"trace not a dict: {trace}"
    assert trace.get('raw_body_parsed') is True, f"expected raw_body_parsed True for form body, got: {trace.get('raw_body_parsed')}"
    # Also expect that porcentajes_partidos was detected and included in trace or meta
    # It may be embedded in other keys; accept if any key mentions 'porcent' or 'porcentaje'
    joined = ' '.join(trace.keys()).lower()
    assert ('porcent' in joined) or ('porcentaje' in joined) or ('tmp_parquet' in joined) or ('votos_redistribuidos' in joined), \
        f"expected trace to include info about detected porcentajes_partidos, got keys: {list(trace.keys())}"
