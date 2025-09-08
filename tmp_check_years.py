import asyncio, importlib, json

m = importlib.import_module('main')


class MockRequest:
    """Objeto mínimo que expone async form() esperado por el endpoint."""
    async def form(self):
        return {}


async def run():
    req = MockRequest()
    r2018 = await m.procesar_diputados(req, anio=2018, plan='vigente')
    r2024 = await m.procesar_diputados(req, anio=2024, plan='vigente')
    def extract(resp):
        # Si es JSONResponse, extraer body
        try:
            from fastapi.responses import JSONResponse
            if isinstance(resp, JSONResponse):
                body = resp.body.decode() if hasattr(resp, 'body') else None
                if body:
                    return json.loads(body)
        except Exception:
            pass

        # Si ya es dict-like
        if isinstance(resp, dict):
            return resp
        # Intentar acceder a atributos comunes
        try:
            return resp.__dict__
        except Exception:
            return {}

    d2018 = extract(r2018)
    d2024 = extract(r2024)

    out2018 = {
        'anio': 2018,
    'total_escanos': d2018.get('kpis', {}).get('total_escanos'),
    'kpis': d2018.get('kpis', {}),
    'used_csv': d2018.get('meta', {}).get('used_csv_vigente'),
    'first5_partidos': [p.get('partido') for p in d2018.get('resultados', [])[:5]]
    }
    out2024 = {
        'anio': 2024,
    'total_escanos': d2024.get('kpis', {}).get('total_escanos'),
    'kpis': d2024.get('kpis', {}),
    'used_csv': d2024.get('meta', {}).get('used_csv_vigente'),
    'first5_partidos': [p.get('partido') for p in d2024.get('resultados', [])[:5]]
    }

    print(json.dumps({'2018': out2018, '2024': out2024}, indent=2, ensure_ascii=False))


asyncio.run(run())
