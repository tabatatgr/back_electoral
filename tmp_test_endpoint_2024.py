"""
Script para probar el endpoint de diputados con parámetros específicos
y comparar con los resultados de los CSV generados
"""
import requests
import json
import pandas as pd

# Parámetros de prueba
PARAMS = {
    "anio": 2024,
    "max_seats": 400,
    "mr_seats": 200,
    "rp_seats": 200,
    "usar_coaliciones": True,
    "aplicar_topes": True
}

print("="*80)
print("PROBANDO ENDPOINT: /api/procesar_diputados")
print("="*80)
print(f"\nParámetros:")
for k, v in PARAMS.items():
    print(f"  {k}: {v}")

try:
    response = requests.post(
        "http://127.0.0.1:8000/api/procesar_diputados",
        json=PARAMS,
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        
        print("\n" + "="*80)
        print("RESPUESTA DEL ENDPOINT")
        print("="*80)
        
        # Extraer totales
        if 'tot' in data:
            print("\n📊 ESCAÑOS TOTALES (MR + RP):")
            totales = data['tot']
            for partido in ['MORENA', 'PAN', 'PRI', 'PT', 'PVEM', 'MC', 'PRD']:
                if partido in totales:
                    print(f"  {partido}: {totales[partido]}")
            
            # Calcular coalición
            coal_total = totales.get('MORENA', 0) + totales.get('PT', 0) + totales.get('PVEM', 0)
            print(f"\n  COALICIÓN (MORENA+PT+PVEM): {coal_total}")
            print(f"  MORENA %: {totales.get('MORENA', 0)/400*100:.2f}%")
            print(f"  COALICIÓN %: {coal_total/400*100:.2f}%")
        
        if 'mr' in data:
            print("\n🏛️ ESCAÑOS MR:")
            mr = data['mr']
            for partido in ['MORENA', 'PAN', 'PRI', 'PT', 'PVEM', 'MC', 'PRD']:
                if partido in mr:
                    print(f"  {partido}: {mr[partido]}")
        
        if 'rp' in data:
            print("\n📋 ESCAÑOS RP:")
            rp = data['rp']
            for partido in ['MORENA', 'PAN', 'PRI', 'PT', 'PVEM', 'MC', 'PRD']:
                if partido in rp:
                    print(f"  {partido}: {rp[partido]}")
        
        # Comparar con CSV
        print("\n" + "="*80)
        print("COMPARACIÓN CON CSV GENERADO")
        print("="*80)
        
        try:
            df = pd.read_csv('outputs/escenarios_morena_CON_TOPES_20251217_172516.csv')
            # Buscar fila con los mismos parámetros
            fila = df[
                (df['anio'] == 2024) &
                (df['total_escanos'] == 400) &
                (df['configuracion'] == '50MR_50RP') &
                (df['usar_coaliciones'] == 'CON') &
                (df['topes_aplicados'] == 'SI')
            ]
            
            if not fila.empty:
                fila = fila.iloc[0]
                
                print("\n📄 Datos del CSV:")
                print(f"  MORENA MR: {fila['morena_mr']}")
                print(f"  MORENA RP: {fila['morena_rp']}")
                print(f"  MORENA TOTAL: {fila['morena_total']}")
                print(f"  MORENA %: {fila['morena_pct_escanos']:.2f}%")
                print(f"  COALICIÓN TOTAL: {fila['coalicion_total']}")
                print(f"  COALICIÓN %: {fila['coalicion_pct_escanos']:.2f}%")
                
                print("\n🔍 COMPARACIÓN:")
                morena_endpoint = totales.get('MORENA', 0)
                morena_csv = int(fila['morena_total'])
                
                coal_endpoint = coal_total
                coal_csv = int(fila['coalicion_total'])
                
                print(f"  MORENA: Endpoint={morena_endpoint}, CSV={morena_csv}, Diff={morena_endpoint - morena_csv}")
                print(f"  COALICIÓN: Endpoint={coal_endpoint}, CSV={coal_csv}, Diff={coal_endpoint - coal_csv}")
                
                if morena_endpoint == morena_csv and coal_endpoint == coal_csv:
                    print("\n  ✅ ¡COINCIDEN PERFECTAMENTE!")
                else:
                    print("\n  ⚠️ HAY DIFERENCIAS")
            else:
                print("\n  ⚠️ No se encontró la fila en el CSV")
        
        except Exception as e:
            print(f"\n  ⚠️ Error al leer CSV: {e}")
    
    else:
        print(f"\n❌ Error {response.status_code}:")
        print(response.text)

except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: No se pudo conectar al servidor.")
    print("   Asegúrate de que el servidor esté corriendo en http://127.0.0.1:8000")
except Exception as e:
    print(f"\n❌ ERROR: {e}")

print("\n" + "="*80)
