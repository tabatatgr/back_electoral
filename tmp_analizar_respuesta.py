import json

with open('tmp_respuesta_endpoint.json') as f:
    data = json.load(f)

resultados = data['resultados']

# Buscar cada partido
morena = next(p for p in resultados if p['partido'] == 'MORENA')
pt = next(p for p in resultados if p['partido'] == 'PT')
pvem = next(p for p in resultados if p['partido'] == 'PVEM')

print("="*80)
print("RESULTADO DEL ENDPOINT (plan=personalizado)")
print("="*80)
print(f"\nMORENA:")
print(f"  MR: {morena['mr']}")
print(f"  RP: {morena['rp']}")
print(f"  TOTAL: {morena['total']} ({morena['porcentaje_escanos']}%)")

print(f"\nPT: {pt['total']}")
print(f"PVEM: {pvem['total']}")

coalicion = morena['total'] + pt['total'] + pvem['total']
print(f"\nCOALICIÓN (MORENA+PT+PVEM): {coalicion} ({coalicion/400*100:.1f}%)")

print("\n" + "="*80)
print("COMPARACIÓN CON SCRIPT DIRECTO")
print("="*80)
print("\nScript directo dio:")
print("  MORENA MR: 161")
print("  MORENA RP: 87")
print("  MORENA TOTAL: 248 (62%)")
print("  COALICIÓN: 282 (70.5%)")

print(f"\nDIFERENCIA:")
print(f"  MORENA: {morena['total']} - 248 = {morena['total'] - 248}")
print(f"  COALICIÓN: {coalicion} - 282 = {coalicion - 282}")

if morena['total'] == 248 and coalicion == 282:
    print("\n✅✅✅ ¡COINCIDEN PERFECTAMENTE!")
else:
    print("\n⚠️⚠️⚠️ HAY DIFERENCIAS")
