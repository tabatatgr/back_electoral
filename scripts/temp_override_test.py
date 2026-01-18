import requests, json
BASE='http://127.0.0.1:8000'

# 1) obtener senado actual
r = requests.post(f"{BASE}/procesar/senado?anio=2024", json={'plan':'vigente'}, timeout=60)
print('SENADO HTTP', r.status_code)
s=r.json()
mr_por_estado = s.get('meta',{}).get('mr_por_estado',{})
# buscar JALISCO
j_name = None
for k in mr_por_estado:
    if 'JALIS' in k.upper():
        j_name=k
        break
print('Jalisco name in senado meta:', j_name)
print('Jalisco entry senado:', mr_por_estado.get(j_name))

# 2) obtener diputados actual
r2 = requests.post(f"{BASE}/procesar/diputados?anio=2024", json={'plan':'vigente','escanos_totales':300}, timeout=60)
print('DIPUTADOS HTTP', r2.status_code)
d = r2.json()
distritos = d.get('meta',{}).get('distritos_por_estado',{})
mr_est = d.get('meta',{}).get('mr_por_estado',{})
print('Jalisco distritos_por_estado (id 14):', distritos.get('14') or distritos.get(14) or distritos.get('Jalisco'))
# buscar JALISCO en mr_por_estado diputados
j_dip=None
for k in mr_est:
    if 'JALIS' in k.upper():
        j_dip=k; break
print('Jalisco key diputados:', j_dip)
print('Jalisco entry diputados mr_por_estado:', mr_est.get(j_dip))

# 3) construir override para senado: aumentar MORENA +1 en Jalisco
if j_name:
    entry = mr_por_estado.get(j_name).copy()
    dec_party = None
    maxv=-1
    for p,v in entry.items():
        try:
            vi = int(v)
        except Exception:
            vi = 0
        if p!='MORENA' and vi>maxv:
            maxv=vi; dec_party=p
    if dec_party is None:
        print('No candidate to decrement in senado Jalisco, aborting')
    else:
        new_entry = entry.copy()
        new_entry['MORENA'] = int(new_entry.get('MORENA',0))+1
        new_entry[dec_party] = int(new_entry.get(dec_party,0))-1
        payload = {'plan':'vigente','mr_distritos_por_estado': { '14': new_entry }}
        print('Sending senado override payload for JALISCO:', payload)
        rr = requests.post(f"{BASE}/procesar/senado?anio=2024", json=payload, timeout=60)
        print('SENADO OVERRIDE HTTP', rr.status_code)
        try:
            rrj = rr.json()
            mj = rrj.get('meta',{}).get('mr_por_estado',{})
            print('Jalisco after override (senado):', mj.get(j_name) or mj.get('14'))
        except Exception as e:
            print('No JSON or error', e, rr.text[:1000])

# 4) construir override para diputados: change MORENA +1 in Jalisco, decrement largest other party
if j_dip:
    entry = mr_est.get(j_dip)
    dec=None; mv=-1
    for p,v in entry.items():
        try:
            vi=int(v)
        except Exception:
            vi=0
        if p!='MORENA' and vi>mv:
            mv=vi; dec=p
    if dec is None:
        print('No candidate to decrement in diputados Jalisco')
    else:
        new_entry = entry.copy()
        new_entry['MORENA']=int(new_entry.get('MORENA',0))+1
        new_entry[dec]=int(new_entry.get(dec,0))-1
        payload2={'plan':'vigente','mr_distritos_por_estado': {'14': new_entry}}
        print('Sending diputados override payload for JALISCO:', payload2)
        rr2 = requests.post(f"{BASE}/procesar/diputados?anio=2024", json=payload2, timeout=60)
        print('DIPUTADOS OVERRIDE HTTP', rr2.status_code)
        try:
            js=rr2.json(); md=js.get('meta',{}).get('mr_por_estado',{})
            print('Jalisco after override (diputados):', md.get(j_dip) or md.get('14'))
        except Exception as e:
            print('No JSON or error', e, rr2.text[:1000])

print('Done')
