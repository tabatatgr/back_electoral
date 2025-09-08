import asyncio, json
from pprint import pprint
import main

class DummyRequest:
    async def form(self):
        return {}

async def run():
    req = DummyRequest()
    resp = await main.procesar_diputados(req, 2018, 'vigente')
    if hasattr(resp,'body'):
        print('Is JSONResponse')
        print('status', getattr(resp,'status_code',None))
        print(json.dumps(json.loads(resp.body.decode()), indent=2, ensure_ascii=False))
    else:
        pprint(resp)

asyncio.run(run())
