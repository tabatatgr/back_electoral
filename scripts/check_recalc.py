from fastapi.testclient import TestClient
import main
import json

client = TestClient(main.app)

def pretty(obj):
    print(json.dumps(obj, indent=2, ensure_ascii=False))

def run_test():
    query = '/procesar/diputados?anio=2024&plan=personalizado&escanos_totales=128&sistema=mixto&mr_seats=64&rp_seats=64&reparto_mode=cuota&reparto_method=hare&usar_coaliciones=true'

    # 1) Enviar como form-urlencoded (simula frontend mal-encoded)
    form = 'PRD=90&PAN=5'
    print('\n=== POST application/x-www-form-urlencoded ===')
    resp1 = client.post(query, data=form, headers={'Content-Type': 'application/x-www-form-urlencoded'}, timeout=120)
    print('status', resp1.status_code)
    try:
        j1 = resp1.json()
        print('meta.trace:')
        pretty(j1.get('meta', {}).get('trace'))
        print('\nseat_chart:')
        pretty(j1.get('seat_chart'))
        print('\nkpis:')
        pretty(j1.get('kpis'))
    except Exception as e:
        print('No JSON response or parse error:', e)

    # 2) Enviar como text/plain con JSON body
    import pathlib
    body_raw = pathlib.Path('scripts/test_prd_90.json').read_text(encoding='utf-8')
    print('\n=== POST text/plain (raw JSON body) ===')
    resp2 = client.post(query, data=body_raw, headers={'Content-Type': 'text/plain'}, timeout=120)
    print('status', resp2.status_code)
    try:
        j2 = resp2.json()
        print('meta.trace:')
        pretty(j2.get('meta', {}).get('trace'))
        print('\nseat_chart:')
        pretty(j2.get('seat_chart'))
        print('\nkpis:')
        pretty(j2.get('kpis'))
    except Exception as e:
        print('No JSON response or parse error:', e)

if __name__ == '__main__':
    run_test()
