import asyncio, importlib, json

m = importlib.import_module('main')

class MockRequest:
    async def form(self):
        return {}

async def run():
    req = MockRequest()
    resp = await m.procesar_diputados(req, anio=2024, plan='personalizado', sistema='mr', escanos_totales=97, req_id='test-97')
    # Extraer contenido si es JSONResponse
    try:
        from fastapi.responses import JSONResponse
        if isinstance(resp, JSONResponse):
            body = resp.body.decode() if hasattr(resp, 'body') else None
            if body:
                data = json.loads(body)
            else:
                data = {}
        else:
            data = resp if isinstance(resp, dict) else getattr(resp, '__dict__', {})
    except Exception:
        data = resp if isinstance(resp, dict) else getattr(resp, '__dict__', {})

    print(json.dumps({
        'meta': data.get('meta'),
        'kpis_total_escanos': data.get('kpis', {}).get('total_escanos'),
        'kpis': data.get('kpis')
    }, indent=2, ensure_ascii=False))

asyncio.run(run())
