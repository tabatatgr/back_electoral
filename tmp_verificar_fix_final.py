"""
VERIFICACIÓN FINAL: API debe dar MORENA = 256 (sin topes, sin coaliciones)
"""

import requests
import json

API_URL = "http://127.0.0.1:8000/procesar/diputados"

print("\n" + "="*80)
print("🧪 VERIFICACIÓN FINAL DEL FIX")
print("="*80)

print("\n📋 Probando: 400 escaños, SIN topes, SIN coaliciones")
print("   Resultado esperado: MORENA = 256 (MR=163, RP=93)")

# Hacer request a la API
response = requests.post(
    f"{API_URL}?anio=2024",
    json={
        "plan": "personalizado",
        "escanos_totales": 400,
        "sistema": "mixto",
        "mr_seats": 200,
        "rp_seats": 200,
        "aplicar_topes": False,
        "usar_coaliciones": False
    },
    timeout=30
)

print(f"\nStatus: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    resultados = data.get('resultados', [])
    
    # Buscar MORENA
    morena = [r for r in resultados if r['partido'] == 'MORENA'][0]
    
    mr = morena['mr']
    rp = morena['rp']
    total = morena['total']
    
    print("\n" + "="*80)
    print("RESULTADO:")
    print("="*80)
    print(f"\nMORENA:")
    print(f"  MR:    {mr}")
    print(f"  RP:    {rp}")
    print(f"  TOTAL: {total}")
    
    print("\n" + "="*80)
    print("VERIFICACIÓN:")
    print("="*80)
    
    # Verificar cada componente
    checks = []
    
    if mr == 163:
        print(f"✅ MR correcto: {mr} (esperado 163)")
        checks.append(True)
    else:
        print(f"❌ MR incorrecto: {mr} (esperado 163)")
        checks.append(False)
    
    if rp == 93:
        print(f"✅ RP correcto: {rp} (esperado 93)")
        checks.append(True)
    else:
        print(f"❌ RP incorrecto: {rp} (esperado 93)")
        checks.append(False)
    
    if total == 256:
        print(f"✅ TOTAL correcto: {total} (esperado 256)")
        checks.append(True)
    else:
        print(f"❌ TOTAL incorrecto: {total} (esperado 256)")
        checks.append(False)
    
    # Resultado final
    print("\n" + "="*80)
    if all(checks):
        print("✅✅✅ ÉXITO! La API ahora devuelve los valores correctos")
        print("El fix funcionó: método Hare por default resolvió el problema")
    else:
        print("❌ El problema persiste")
        print("\n💡 SIGUIENTE PASO:")
        print("   1. Verifica que el servidor se haya reiniciado")
        print("   2. Revisa los logs del servidor para ver qué método está usando")
        print("   3. El servidor debería mostrar: '[DEBUG] Modo cuota seleccionado: hare'")
    print("="*80)
    
else:
    print(f"❌ Error en la API: {response.status_code}")
    print(response.text[:500])

print("\n⚠️  Recuerda: Si acabas de hacer el cambio, necesitas REINICIAR el servidor")
print("   El servidor no recarga cambios automáticamente en main.py")
