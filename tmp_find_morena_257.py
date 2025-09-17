import importlib, asyncio, json, copy

m = importlib.import_module('main')

class MockRequest:
    def __init__(self, form_dict=None):
        self._form = form_dict or {}
    async def form(self):
        return self._form

# Leemos votos actuales desde el procesador (usar los porcentajes reales como base)
async def get_base_porcentajes():
    resp = await m.procesar_diputados(MockRequest(), anio=2024, plan='vigente')
    try:
        from fastapi.responses import JSONResponse
        if isinstance(resp, JSONResponse):
            body = resp.body.decode() if hasattr(resp, 'body') else None
            data = json.loads(body)
        else:
            data = resp if isinstance(resp, dict) else getattr(resp, '__dict__', {})
    except Exception:
        data = resp if isinstance(resp, dict) else getattr(resp, '__dict__', {})

    resultados = data.get('resultados', [])
    porcentajes = {r['partido']: r['porcentaje_votos'] for r in resultados if r.get('porcentaje_votos') is not None}
    return porcentajes

async def test_with_morena_share(morena_share, base_porcentajes):
    # Ajustar porcentajes manteniendo proporciones de los otros partidos
    other_total = sum(v for k,v in base_porcentajes.items() if k != 'MORENA')
    if other_total == 0:
        return None
    factor = (100.0 - morena_share) / other_total
    new_porcentajes = {k: (v * factor) if k != 'MORENA' else morena_share for k,v in base_porcentajes.items()}
    # llamar al endpoint con porcentajes_partidos
    porcentajes_json = json.dumps(new_porcentajes)
    form_req = MockRequest({'porcentajes_partidos': porcentajes_json})
    resp = await m.procesar_diputados(form_req, anio=2024, plan='personalizado', escanos_totales=500, sistema='mixto', mr_seats=300, rp_seats=200)
    try:
        from fastapi.responses import JSONResponse
        if isinstance(resp, JSONResponse):
            body = resp.body.decode() if hasattr(resp, 'body') else None
            data = json.loads(body)
        else:
            data = resp if isinstance(resp, dict) else getattr(resp, '__dict__', {})
    except Exception:
        data = resp if isinstance(resp, dict) else getattr(resp, '__dict__', {})
    total_morena = 0
    for r in data.get('resultados', []):
        if r.get('partido') == 'MORENA':
            total_morena = r.get('total', 0)
    return total_morena, data

async def find_target():
    base = await get_base_porcentajes()
    if 'MORENA' not in base:
        print('No se pudo extraer base de porcentajes')
        return
    low, high = base['MORENA'], 95.0
    target = 257
    found = None
    for _ in range(25):
        mid = (low + high) / 2.0
        total, data = await test_with_morena_share(mid, base)
        print(f"probando {mid:.4f}% -> MORENA escaños = {total}")
        if total is None:
            print('Error en llamada')
            return
        if total >= target:
            found = (mid, total)
            high = mid
        else:
            low = mid
    print('Resultado aproximado:', found)

asyncio.run(find_target())
