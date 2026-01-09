"""
Verificación específica: ¿PRD recibe escaños RP cuando no debería?
"""
import requests
import json

print("=" * 80)
print("🔍 VERIFICACIÓN: PRD y escaños de Representación Proporcional en 2024")
print("=" * 80)

# PRD: 2.54% de votos (NO alcanza 3% umbral)
# Regla: Puede tener MR (ganó distritos), pero NO debe tener RP

configs = [
    {
        "nombre": "Plan vigente (500 escaños, 300 MR, 200 RP)",
        "url": "http://localhost:8000/procesar/diputados?anio=2024&plan=vigente"
    },
    {
        "nombre": "Personalizado 400 escaños CON umbral 3%",
        "url": "http://localhost:8000/procesar/diputados?anio=2024&plan=personalizado&escanos_totales=400&sistema=mixto&mr_seats=200&rp_seats=200&umbral=0.03"
    },
    {
        "nombre": "Personalizado 400 escaños SIN umbral",
        "url": "http://localhost:8000/procesar/diputados?anio=2024&plan=personalizado&escanos_totales=400&sistema=mixto&mr_seats=200&rp_seats=200&umbral=0"
    },
    {
        "nombre": "Personalizado 500 escaños CON umbral 3%",
        "url": "http://localhost:8000/procesar/diputados?anio=2024&plan=personalizado&escanos_totales=500&sistema=mixto&mr_seats=300&rp_seats=200&umbral=0.03"
    },
]

resultados_verificacion = []

for config in configs:
    print(f"\n{'=' * 80}")
    print(f"📊 {config['nombre']}")
    print("-" * 80)
    
    try:
        r = requests.post(config['url'], timeout=10)
        data = r.json()
        
        # Buscar PRD
        prd = None
        for p in data['resultados']:
            if p.get('partido') == 'PRD':
                prd = p
                break
        
        if prd:
            mr = prd.get('mr', prd.get('escanos_mr', 0))
            rp = prd.get('rp', prd.get('escanos_rp', 0))
            total = prd.get('total', prd.get('escanos_totales', 0))
            
            print(f"✓ PRD encontrado:")
            print(f"  Votos: {prd.get('votos', 0):,} ({prd.get('porcentaje_votos', 0):.2f}%)")
            print(f"  Mayoría Relativa (MR): {mr}")
            print(f"  Representación Proporcional (RP): {rp}")
            print(f"  Total escaños: {total}")
            
            # Verificación
            if rp > 0:
                print(f"\n  ⚠️  PROBLEMA DETECTADO:")
                print(f"      PRD tiene {rp} escaños de RP pero solo alcanzó 2.54%")
                print(f"      NO debería tener escaños RP (umbral mínimo = 3%)")
                resultados_verificacion.append({
                    "config": config['nombre'],
                    "problema": True,
                    "rp": rp
                })
            else:
                print(f"\n  ✅ CORRECTO: PRD NO recibe escaños RP (no alcanzó umbral)")
                resultados_verificacion.append({
                    "config": config['nombre'],
                    "problema": False,
                    "rp": 0
                })
        else:
            print(f"  PRD no aparece en resultados")
            resultados_verificacion.append({
                "config": config['nombre'],
                "problema": False,
                "rp": 0
            })
            
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n\n" + "=" * 80)
print("📋 RESUMEN DE VERIFICACIÓN")
print("=" * 80)

problemas = [r for r in resultados_verificacion if r['problema']]

if problemas:
    print(f"\n⚠️  SE ENCONTRARON {len(problemas)} PROBLEMA(S):")
    for p in problemas:
        print(f"   • {p['config']}: PRD recibe {p['rp']} escaños RP")
    print(f"\n🔧 ACCIÓN REQUERIDA:")
    print(f"   El motor debe verificar umbral ANTES de asignar RP")
    print(f"   PRD (2.54%) < Umbral (3.00%) → RP = 0")
else:
    print(f"\n✅ TODO CORRECTO:")
    print(f"   PRD NO recibe escaños RP en ninguna configuración")
    print(f"   El umbral del 3% se está aplicando correctamente")

print(f"\n📝 Nota: PRD puede tener escaños MR (mayoría relativa)")
print(f"   si ganó distritos directamente, incluso sin alcanzar umbral")
