"""
Investigar: ¿PRD recibe escaños RP en 2024 cuando no debería?
PRD perdió registro en 2024 por no alcanzar 3% umbral nacional
"""
import requests
import pandas as pd

print("=" * 80)
print("🔍 INVESTIGACIÓN: PRD recibiendo escaños RP en 2024")
print("=" * 80)

# Primero verificar votos de PRD en 2024
print("\n1️⃣  Verificando votos de PRD en datos originales")
print("-" * 80)

df = pd.read_parquet('data/computos_diputados_2024.parquet')
# En 2024 cada partido es una columna
prd_votos = df['PRD'].sum()
# Total es suma de todos los partidos
partidos_cols = ['FXM', 'MC', 'MORENA', 'NA', 'PAN', 'PES', 'PRD', 'PRI', 'PT', 'PVEM', 'RSP']
total_votos = df[partidos_cols].sum().sum()
prd_porcentaje = (prd_votos / total_votos) * 100

print(f"PRD votos totales: {prd_votos:,}")
print(f"Total votos: {total_votos:,}")
print(f"PRD porcentaje: {prd_porcentaje:.4f}%")
print(f"Umbral 3%: {total_votos * 0.03:,.0f} votos")
print(f"¿Alcanzó 3%?: {'❌ NO' if prd_porcentaje < 3.0 else '✅ SÍ'}")

# Probar con diferentes configuraciones del API
configs = [
    {
        "nombre": "Plan vigente (default)",
        "params": "anio=2024&plan=vigente"
    },
    {
        "nombre": "Personalizado CON umbral 3%",
        "params": "anio=2024&plan=personalizado&escanos_totales=500&sistema=mixto&mr_seats=300&rp_seats=200&umbral=0.03"
    },
    {
        "nombre": "Personalizado SIN umbral (0%)",
        "params": "anio=2024&plan=personalizado&escanos_totales=500&sistema=mixto&mr_seats=300&rp_seats=200&umbral=0"
    },
    {
        "nombre": "Personalizado umbral DEFAULT (debería ser 3%)",
        "params": "anio=2024&plan=personalizado&escanos_totales=500&sistema=mixto&mr_seats=300&rp_seats=200"
    }
]

print("\n\n2️⃣  Probando diferentes configuraciones del API")
print("=" * 80)

for i, config in enumerate(configs, 1):
    print(f"\n{i}. {config['nombre']}")
    print("-" * 80)
    
    try:
        r = requests.post(f"http://localhost:8000/procesar/diputados?{config['params']}", timeout=10)
        data = r.json()
        
        # Buscar PRD en resultados
        prd_result = None
        for partido in data.get('resultados', []):
            if partido.get('partido') == 'PRD':
                prd_result = partido
                break
        
        if prd_result:
            total_escanos = prd_result.get('escanos_totales', prd_result.get('total', 0))
            mr_escanos = prd_result.get('escanos_mr', prd_result.get('mayoría relativa', 0))
            rp_escanos = prd_result.get('escanos_rp', prd_result.get('representación proporcional', 0))
            
            print(f"  PRD encontrado:")
            print(f"    Votos: {prd_result.get('votos', 'N/A'):,} ({prd_result.get('porcentaje_votos', 0):.2f}%)")
            print(f"    Escaños totales: {total_escanos}")
            print(f"    MR: {mr_escanos}")
            print(f"    RP: {rp_escanos}")
            
            if rp_escanos > 0 and prd_porcentaje < 3.0:
                print(f"  ⚠️  PROBLEMA: PRD tiene {rp_escanos} escaños RP pero NO alcanzó 3% umbral")
            elif total_escanos == 0 and prd_porcentaje < 3.0:
                print(f"  ✅ CORRECTO: PRD sin escaños (no alcanzó umbral)")
            elif rp_escanos == 0 and mr_escanos > 0:
                print(f"  ✅ CORRECTO: PRD solo tiene MR (ganó distritos pero no umbral)")
        else:
            print(f"  PRD no aparece en resultados")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n\n" + "=" * 80)
print("📋 RESUMEN")
print("=" * 80)
print(f"• PRD obtuvo {prd_porcentaje:.4f}% de votos en 2024")
print(f"• Umbral requerido: 3.00%")
print(f"• Estado: {'NO alcanzó umbral - perdió registro' if prd_porcentaje < 3.0 else 'SÍ alcanzó umbral'}")
print(f"\n✅ Regla correcta:")
print(f"  - Si PRD ganó distritos por MR → SÍ puede tener esos escaños MR")
print(f"  - Si PRD NO alcanzó 3% → NO debe recibir escaños RP")
print(f"  - Si PRD perdió registro → NO debe aparecer en resultados")
