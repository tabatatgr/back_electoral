"""
Probar votos_custom: editar porcentajes de votos por partido
"""
import requests
import json

print("=" * 80)
print("🧪 PRUEBA: Editando porcentajes de votos con votos_custom")
print("=" * 80)

# Escenario: Dar 5% de votos a PRD para que SÍ alcance el umbral del 3%
votos_personalizados = {
    "MORENA": 40.0,
    "PAN": 20.0,
    "PRI": 12.0,
    "PVEM": 8.0,
    "PT": 6.0,
    "MC": 9.0,
    "PRD": 5.0  # ← Dándole 5% en lugar del 2.54% real
}

print("\n📊 Votos personalizados:")
print("-" * 80)
for partido, pct in votos_personalizados.items():
    print(f"  {partido}: {pct}%")

print(f"\nTotal: {sum(votos_personalizados.values())}%")

# Probar con POST body (JSON)
url = "http://localhost:8000/procesar/diputados?anio=2024&plan=personalizado&escanos_totales=500&sistema=mixto&mr_seats=300&rp_seats=200&umbral=0.03"

payload = {
    "votos_custom": json.dumps(votos_personalizados)
}

print("\n" + "=" * 80)
print("🔄 Enviando request con votos_custom...")
print("=" * 80)

try:
    r = requests.post(url, json=payload, timeout=10)
    
    if r.status_code != 200:
        print(f"❌ Error {r.status_code}: {r.text[:500]}")
    else:
        data = r.json()
        
        print("\n📊 RESULTADOS CON VOTOS PERSONALIZADOS:")
        print("-" * 80)
        print(f"{'Partido':<10} {'Votos %':>9} {'MR':>5} {'RP':>5} {'Total':>7}")
        print("-" * 80)
        
        for p in data['resultados']:
            if p['total'] > 0:
                print(f"{p['partido']:<10} {p['porcentaje_votos']:>8.2f}% {p['mr']:>5} {p['rp']:>5} {p['total']:>7}")
        
        # Verificar PRD específicamente
        prd = [p for p in data['resultados'] if p['partido'] == 'PRD'][0]
        
        print("\n" + "=" * 80)
        print("🔍 VERIFICACIÓN PRD:")
        print("=" * 80)
        print(f"  Votos reales históricos: 2.54%")
        print(f"  Votos personalizados: {prd['porcentaje_votos']:.2f}%")
        print(f"  Escaños RP: {prd['rp']}")
        print(f"  Total escaños: {prd['total']}")
        
        if prd['rp'] > 0 and prd['porcentaje_votos'] >= 3.0:
            print(f"\n  ✅ CORRECTO: Con {prd['porcentaje_votos']:.2f}% SÍ recibe RP")
        elif prd['rp'] == 0 and prd['porcentaje_votos'] < 3.0:
            print(f"\n  ✅ CORRECTO: Con {prd['porcentaje_votos']:.2f}% NO recibe RP")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n\n" + "=" * 80)
print("💡 USO DE votos_custom:")
print("=" * 80)
print("Puedes enviar un JSON con los porcentajes de votos que quieras:")
print("")
print("Opción 1 - Query param (codificado):")
print('  votos_custom={"MORENA":40,"PAN":20,...}')
print("")
print("Opción 2 - POST body JSON:")
print('  {')
print('    "votos_custom": "{\\"MORENA\\":40,\\"PAN\\":20,...}"')
print('  }')
print("")
print("✅ Esto permite simular diferentes escenarios electorales")
