import importlib, asyncio, json, pandas as pd, os

m = importlib.import_module('main')

class MockRequest:
    async def form(self):
        return {}

# Escenarios que pediste (adaptados a diputados)
SCENARIOS = [
    { 'label': '500_total_300mr_200rp', 'params': {'plan':'personalizado', 'escanos_totales':500, 'sistema':'mixto', 'mr_seats':300, 'rp_seats':200}},
    { 'label': '500_total_250mr_250rp', 'params': {'plan':'personalizado', 'escanos_totales':500, 'sistema':'mixto', 'mr_seats':250, 'rp_seats':250}},
    { 'label': '300mr_200pm_500_total', 'params': {'plan':'personalizado', 'escanos_totales':500, 'sistema':'mixto', 'mr_seats':300, 'rp_seats':0, 'pm_seats':200}},
    { 'label': '500_rp', 'params': {'plan':'personalizado', 'escanos_totales':500, 'sistema':'rp'}},
    { 'label': '300mr_100rp_100pm', 'params': {'plan':'personalizado', 'escanos_totales':500, 'sistema':'mixto', 'mr_seats':300, 'rp_seats':100, 'pm_seats':100}},
]

async def run():
    req = MockRequest()
    rows = []
    for sc in SCENARIOS:
        label = sc['label']
        params = sc['params'].copy()
        print(f"Procesando escenario: {label} -> {params}")
        # preparar argumentos para el endpoint de diputados
        kwargs = {'anio':2024}
        # Mapear pm_seats: no existe PM para diputados en engine, lo sumamos a MR
        pm = params.pop('pm_seats', 0)
        kwargs.update(params)
        if pm and 'mr_seats' in kwargs:
            kwargs['mr_seats'] = kwargs.get('mr_seats', 0) + pm
        # asegurarnos pasar sobrerrepresentacion=8 y umbral 0.03 y siglado activo (por defecto lo usa)
        kwargs['sobrerrepresentacion'] = 8.0
        kwargs['umbral'] = 0.03
        # llamar
        resp = await m.procesar_diputados(MockRequest(), **kwargs)
        # extraer body si es JSONResponse
        data = {}
        try:
            from fastapi.responses import JSONResponse
            if isinstance(resp, JSONResponse):
                body = resp.body.decode() if hasattr(resp, 'body') else None
                if body:
                    data = json.loads(body)
            elif isinstance(resp, dict):
                data = resp
            else:
                data = getattr(resp, '__dict__', {})
        except Exception:
            data = resp if isinstance(resp, dict) else getattr(resp, '__dict__', {})

        resultados = data.get('resultados', [])
        for r in resultados:
            row = {
                'scenario': label,
                'partido': r.get('partido'),
                'mr': r.get('mr', 0),
                'rp': r.get('rp', 0),
                'total': r.get('total', 0),
                'porcentaje_votos': r.get('porcentaje_votos'),
                'porcentaje_escanos': r.get('porcentaje_escanos')
            }
            # marcar pm si el partido obtuvo alguno en MR y pm fue solicitado (indicativo)
            row['pm_requested'] = pm
            rows.append(row)

    df = pd.DataFrame(rows)
    os.makedirs('outputs', exist_ok=True)
    out_path = os.path.join('outputs', 'diputados_scenarios.xlsx')
    with pd.ExcelWriter(out_path) as writer:
        for label in df['scenario'].unique():
            df[df['scenario']==label].to_excel(writer, sheet_name=label[:31], index=False)
    print('Escrito', out_path)

asyncio.run(run())
