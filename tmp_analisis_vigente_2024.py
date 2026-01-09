"""
Revisar TODOS los partidos en plan vigente 2024
"""
import requests

r = requests.post('http://localhost:8000/procesar/diputados?anio=2024&plan=vigente')
data = r.json()

print("=" * 80)
print("📊 PLAN VIGENTE 2024 - TODOS LOS PARTIDOS CON ESCAÑOS")
print("=" * 80)
print(f"\n{'Partido':<10} {'Votos %':>9} {'MR':>5} {'PM':>5} {'RP':>5} {'Total':>7} {'Problema?':>12}")
print("-" * 80)

partidos_con_problema = []

for p in data['resultados']:
    if p['total'] > 0:
        tiene_problema = ""
        # Verificar si tiene RP pero menos de 3% de votos
        if p['rp'] > 0 and p['porcentaje_votos'] < 3.0:
            tiene_problema = "⚠️ RP < 3%"
            partidos_con_problema.append({
                'partido': p['partido'],
                'votos_pct': p['porcentaje_votos'],
                'rp': p['rp']
            })
        
        print(f"{p['partido']:<10} {p['porcentaje_votos']:>8.2f}% {p['mr']:>5} {p['pm']:>5} {p['rp']:>5} {p['total']:>7} {tiene_problema:>12}")

print("\n" + "=" * 80)
print("📋 ANÁLISIS")
print("=" * 80)

if partidos_con_problema:
    print(f"\n⚠️  PROBLEMAS DETECTADOS: {len(partidos_con_problema)} partido(s)")
    print("-" * 80)
    for p in partidos_con_problema:
        print(f"  • {p['partido']}: {p['votos_pct']:.2f}% de votos pero {p['rp']} escaños RP")
        print(f"    → NO alcanzó umbral 3% (mínimo: 3.00%)")
        print(f"    → NO debería recibir escaños de Representación Proporcional")
    
    print(f"\n🔧 ACCIÓN REQUERIDA:")
    print(f"   Verificar que el motor aplica correctamente el umbral del 3%")
    print(f"   en el reparto de escaños de Representación Proporcional")
else:
    print(f"\n✅ TODO CORRECTO:")
    print(f"   Todos los partidos con RP tienen ≥ 3% de votos")
    print(f"   El umbral se está aplicando correctamente")

print(f"\n📝 NOTAS:")
print(f"   • MR (Mayoría Relativa): Se ganan por distrito, sin umbral")
print(f"   • PM (Primera Minoría): Se ganan por distrito, sin umbral")
print(f"   • RP (Representación Proporcional): Requiere ≥ 3% de votación nacional")
