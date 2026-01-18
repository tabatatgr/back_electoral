"""
Fuerza MORENA a 37 MR y recalcula el escenario para /procesar/senado.
Usa como base la respuesta guardada en scripts/test_outputs/response_nombres_normales_objeto_20260117_200041.json
"""
import json
import os
import requests

BASE_URL = 'http://127.0.0.1:8000'
RESPONSE_FILE = os.path.join(os.path.dirname(__file__), 'test_outputs', 'response_nombres_normales_objeto_20260117_200041.json')

with open(RESPONSE_FILE, 'r', encoding='utf-8') as fh:
    data = json.load(fh)

# Extraer MR actuales
mr_actual = {r['partido']: r['mr'] for r in data['resultados']}
print('MR actual:', mr_actual)
TOTAL_MR = sum(mr_actual.values())
print('Total MR actual:', TOTAL_MR)

# Queremos MORENA = 37
target_morena = 37
remaining = TOTAL_MR - target_morena
if remaining < 0:
    raise SystemExit('Target MORENA > total MR')

# Partidos excepto MORENA
others = {p: v for p, v in mr_actual.items() if p != 'MORENA'}
others_sum = sum(others.values())

# Escalar proporcionalmente
new_others = {}
for p, v in others.items():
    if others_sum == 0:
        new_others[p] = 0
    else:
        new_others[p] = int(round(v * (remaining / others_sum)))

# Ajustar por redondeo para igualar exactamente remaining
current_sum = sum(new_others.values())
# Ajuste fino: añadir o restar 1 a los partidos con mayor/v menor residuo
if current_sum != remaining:
    diff = remaining - current_sum
    # Ordenar partidos por original fractional remainder
    remainders = []
    for p, v in others.items():
        frac = (v * (remaining / others_sum)) - new_others[p]
        remainders.append((frac, p))
    remainders.sort(reverse=True)
    i = 0
    step = 1 if diff > 0 else -1
    diff = abs(diff)
    while diff > 0:
        _, p = remainders[i % len(remainders)]
        new_others[p] += step
        i += 1
        diff -= 1

# Construir mr_distritos_manuales nacional
mr_manuales = {p: new_others.get(p, 0) for p in others.keys()}
mr_manuales['MORENA'] = target_morena
print('MR manuales construidos:', mr_manuales, 'suma:', sum(mr_manuales.values()))

# Enviar POST a /procesar/senado?anio=2024 con mr_distritos_manuales como JSON-string
url = f"{BASE_URL}/procesar/senado?anio=2024"
body = {
    'plan': 'vigente',
    'mr_distritos_manuales': mr_manuales,
    'usar_coaliciones': True
}
print('POST', url)
r = requests.post(url, json=body, timeout=60)
print('HTTP', r.status_code)
try:
    resp = r.json()
except Exception:
    print('No JSON response, text:')
    print(r.text[:2000])
    raise SystemExit()

# Guardar respuesta y mostrar resumen
outf = os.path.join(os.path.dirname(__file__), 'test_outputs', 'response_force_morena_37.json')
with open(outf, 'w', encoding='utf-8') as fh:
    json.dump(resp, fh, ensure_ascii=False, indent=2)
print('Guardado respuesta en', outf)

# Resumen: MR nacional y meta.mr_por_estado keys
res_mr = {r['partido']: r['mr'] for r in resp.get('resultados', [])}
print('MR en nueva respuesta:', res_mr)
meta = resp.get('meta', {})
print('meta.mr_por_estado presente?', 'mr_por_estado' in meta)
if 'mr_por_estado' in meta:
    print('Ejemplo key sample:', list(meta['mr_por_estado'].keys())[:5])

print('Listo')
