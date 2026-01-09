"""
Diagnosticar: ¿Por qué PRD tiene RP en 2024 en los escenarios?
"""
import requests
import pandas as pd

print("=" * 80)
print("🔍 DIAGNÓSTICO: PRD recibiendo RP en 2024")
print("=" * 80)

# Leer el CSV generado
csv_file = sorted([f for f in pd.io.common.get_filepath_or_buffer('outputs/comparativa_escenarios_*.csv')[0] if 'comparativa' in str(f)])
if csv_file:
    import glob
    files = glob.glob('outputs/comparativa_escenarios_*.csv')
    if files:
        latest = max(files)
        df = pd.read_csv(latest)
        
        print(f"\n📄 Archivo: {latest}")
        print("\n🔍 PRD en 2024 - Todos los escenarios:")
        print("-" * 80)
        
        prd_2024 = df[df['Partido'] == 'PRD'][['Escenario', 'Votos_%_2024', 'MR_2024', 'PM_2024', 'RP_2024', 'Total_2024']]
        print(prd_2024.to_string(index=False))
        
        # Verificar si tiene RP cuando no debería
        problemas = df[(df['Partido'] == 'PRD') & (df['RP_2024'] > 0)]
        
        if len(problemas) > 0:
            print(f"\n⚠️  PROBLEMA DETECTADO: PRD tiene RP en {len(problemas)} escenario(s)")
            print(f"   PRD 2024: {prd_2024.iloc[0]['Votos_%_2024']:.2f}% de votos (< 3% umbral)")
            print(f"   NO debería recibir escaños de Representación Proporcional")

# Ahora consultar API directamente para verificar
print("\n\n" + "=" * 80)
print("🔄 VERIFICACIÓN DIRECTA AL API")
print("=" * 80)

escenarios = [
    {"nombre": "MR 200 - RP 200", "mr": 200, "rp": 200, "pm": 0, "sistema": "mixto"},
    {"nombre": "MR 300 - RP 100", "mr": 300, "rp": 100, "pm": 0, "sistema": "mixto"},
]

for esc in escenarios:
    print(f"\n📊 {esc['nombre']}")
    print("-" * 80)
    
    url = f"http://localhost:8000/procesar/diputados?anio=2024&plan=personalizado&escanos_totales=400&sistema={esc['sistema']}&mr_seats={esc['mr']}&rp_seats={esc['rp']}&pm_seats={esc['pm']}&umbral=0.03&aplicar_topes=true&sobrerrepresentacion=8.0&max_seats_per_party=300"
    
    try:
        r = requests.post(url, timeout=10)
        data = r.json()
        
        # Buscar PRD
        prd = [p for p in data['resultados'] if p['partido'] == 'PRD']
        if prd:
            prd = prd[0]
            print(f"PRD: {prd['porcentaje_votos']:.2f}% votos → MR:{prd['mr']} PM:{prd['pm']} RP:{prd['rp']} Total:{prd['total']}")
            
            if prd['rp'] > 0:
                print(f"⚠️  PROBLEMA: PRD tiene {prd['rp']} RP pero solo {prd['porcentaje_votos']:.2f}% (< 3%)")
        else:
            print("PRD no aparece en resultados")
            
    except Exception as e:
        print(f"Error: {e}")

print("\n\n" + "=" * 80)
print("🔧 SOLUCIÓN")
print("=" * 80)
print("Si PRD está recibiendo RP, el problema puede ser:")
print("1. El parámetro umbral=0.03 no se está enviando correctamente")
print("2. El motor no está aplicando el umbral antes del reparto RP")
print("3. Hay un override o lógica especial que ignora el umbral")
print("\nVoy a verificar el endpoint...")
