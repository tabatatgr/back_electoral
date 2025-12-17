"""
Script para comparar resultados del motor (como lo llama el endpoint)
vs los resultados del CSV generado

Simula exactamente lo que hace el endpoint
"""
import pandas as pd
from engine.procesar_diputados_v2 import procesar_diputados_v2

print("="*80)
print("COMPARACIÓN: MOTOR (como endpoint) vs CSV GENERADO")
print("="*80)

# Parámetros exactos
PARAMS = {
    "anio": 2024,
    "max_seats": 400,
    "mr_seats": 200,
    "rp_seats": 200,
    "usar_coaliciones": True,
    "aplicar_topes": True
}

print("\n📋 Parámetros:")
print(f"  Año: {PARAMS['anio']}")
print(f"  Total escaños: {PARAMS['max_seats']}")
print(f"  MR seats: {PARAMS['mr_seats']} (50%)")
print(f"  RP seats: {PARAMS['rp_seats']} (50%)")
print(f"  Usar coaliciones: {PARAMS['usar_coaliciones']}")
print(f"  Aplicar topes: {PARAMS['aplicar_topes']}")

# ==========================================
# 1. LLAMAR AL MOTOR (como lo hace el endpoint)
# ==========================================
print("\n" + "="*80)
print("1️⃣ EJECUTANDO MOTOR (simulando endpoint)...")
print("="*80)

resultado_motor = procesar_diputados_v2(
    path_parquet=f"data/computos_diputados_{PARAMS['anio']}.parquet",
    path_siglado=f"data/siglado-diputados-{PARAMS['anio']}.csv",
    anio=PARAMS['anio'],
    max_seats=PARAMS['max_seats'],
    mr_seats=PARAMS['mr_seats'],
    rp_seats=PARAMS['rp_seats'],
    usar_coaliciones=PARAMS['usar_coaliciones'],
    aplicar_topes=PARAMS['aplicar_topes'],
    print_debug=False
)

# Extraer datos del motor
morena_mr_motor = resultado_motor['mr'].get('MORENA', 0)
morena_rp_motor = resultado_motor['rp'].get('MORENA', 0)
morena_total_motor = resultado_motor['tot'].get('MORENA', 0)

pt_total_motor = resultado_motor['tot'].get('PT', 0)
pvem_total_motor = resultado_motor['tot'].get('PVEM', 0)
coalicion_total_motor = morena_total_motor + pt_total_motor + pvem_total_motor

print("\n✅ Resultados del MOTOR:")
print(f"  MORENA MR: {morena_mr_motor}")
print(f"  MORENA RP: {morena_rp_motor}")
print(f"  MORENA TOTAL: {morena_total_motor}")
print(f"  MORENA %: {morena_total_motor/PARAMS['max_seats']*100:.2f}%")
print(f"  COALICIÓN TOTAL: {coalicion_total_motor}")
print(f"  COALICIÓN %: {coalicion_total_motor/PARAMS['max_seats']*100:.2f}%")

print("\n  Todos los partidos:")
for partido in sorted(resultado_motor['tot'].keys()):
    total = resultado_motor['tot'][partido]
    mr = resultado_motor['mr'].get(partido, 0)
    rp = resultado_motor['rp'].get(partido, 0)
    print(f"    {partido:10s}: {total:3d} escaños (MR:{mr:3d} + RP:{rp:3d})")

# ==========================================
# 2. LEER DATOS DEL CSV
# ==========================================
print("\n" + "="*80)
print("2️⃣ LEYENDO CSV GENERADO...")
print("="*80)

try:
    df = pd.read_csv('outputs/escenarios_morena_CON_TOPES_20251217_172516.csv')
    
    # Buscar fila con los mismos parámetros
    fila = df[
        (df['anio'] == PARAMS['anio']) &
        (df['total_escanos'] == PARAMS['max_seats']) &
        (df['configuracion'] == '50MR_50RP') &
        (df['usar_coaliciones'] == 'CON') &
        (df['topes_aplicados'] == 'SI')
    ]
    
    if not fila.empty:
        fila = fila.iloc[0]
        
        morena_mr_csv = int(fila['morena_mr'])
        morena_rp_csv = int(fila['morena_rp'])
        morena_total_csv = int(fila['morena_total'])
        coalicion_total_csv = int(fila['coalicion_total'])
        
        print("\n✅ Resultados del CSV:")
        print(f"  MORENA MR: {morena_mr_csv}")
        print(f"  MORENA RP: {morena_rp_csv}")
        print(f"  MORENA TOTAL: {morena_total_csv}")
        print(f"  MORENA %: {fila['morena_pct_escanos']:.2f}%")
        print(f"  COALICIÓN TOTAL: {coalicion_total_csv}")
        print(f"  COALICIÓN %: {fila['coalicion_pct_escanos']:.2f}%")
        
        # ==========================================
        # 3. COMPARACIÓN
        # ==========================================
        print("\n" + "="*80)
        print("3️⃣ COMPARACIÓN DETALLADA")
        print("="*80)
        
        print("\n┌─────────────────┬────────┬────────┬──────────┐")
        print("│ Métrica         │ Motor  │ CSV    │ Diff     │")
        print("├─────────────────┼────────┼────────┼──────────┤")
        
        diff_mr = morena_mr_motor - morena_mr_csv
        diff_rp = morena_rp_motor - morena_rp_csv
        diff_total = morena_total_motor - morena_total_csv
        diff_coal = coalicion_total_motor - coalicion_total_csv
        
        print(f"│ MORENA MR       │ {morena_mr_motor:6d} │ {morena_mr_csv:6d} │ {diff_mr:+8d} │")
        print(f"│ MORENA RP       │ {morena_rp_motor:6d} │ {morena_rp_csv:6d} │ {diff_rp:+8d} │")
        print(f"│ MORENA TOTAL    │ {morena_total_motor:6d} │ {morena_total_csv:6d} │ {diff_total:+8d} │")
        print(f"│ COALICIÓN TOTAL │ {coalicion_total_motor:6d} │ {coalicion_total_csv:6d} │ {diff_coal:+8d} │")
        print("└─────────────────┴────────┴────────┴──────────┘")
        
        # Veredicto final
        print("\n" + "="*80)
        if diff_mr == 0 and diff_rp == 0 and diff_total == 0 and diff_coal == 0:
            print("✅✅✅ ¡PERFECTO! MOTOR Y CSV COINCIDEN EXACTAMENTE")
        else:
            print("⚠️⚠️⚠️ HAY DIFERENCIAS ENTRE MOTOR Y CSV")
            print("\nPosibles causas:")
            print("  1. El CSV se generó con parámetros diferentes")
            print("  2. El motor fue modificado después de generar el CSV")
            print("  3. Hay un problema en la lógica de procesamiento")
        print("="*80)
        
    else:
        print("\n❌ No se encontró la fila correspondiente en el CSV")
        print("\nFilas disponibles en el CSV:")
        print(df[df['anio'] == 2024][['anio', 'total_escanos', 'configuracion', 'usar_coaliciones', 'topes_aplicados']])

except FileNotFoundError:
    print("\n❌ No se encontró el archivo CSV")
    print("   Asegúrate de haber ejecutado tmp_generate_escenarios_con_topes.py primero")
except Exception as e:
    print(f"\n❌ Error al leer CSV: {e}")
    import traceback
    traceback.print_exc()
