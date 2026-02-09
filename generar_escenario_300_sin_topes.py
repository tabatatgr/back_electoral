"""
Generar escenario 300-100 SIN TOPES para 2021 y 2024
Solo MORENA y aliados (PT, PVEM)
"""

import sys
sys.path.append('.')

from engine.procesar_diputados_v2 import procesar_diputados_v2
import pandas as pd

def generar_escenario_300_sin_topes(anio):
    """
    Genera el escenario 300 MR + 100 RP SIN TOPES para un año específico
    """
    print(f"\n{'='*80}")
    print(f"ESCENARIO: 300-100 SIN TOPES - AÑO {anio}")
    print(f"{'='*80}")
    
    resultado = procesar_diputados_v2(
        path_parquet=f"data/computos_diputados_{anio}.parquet",
        anio=anio,
        max_seats=400,
        sistema='mixto',
        mr_seats=300,
        rp_seats=100,
        umbral=0.03,
        aplicar_topes=False,  # SIN TOPES
        usar_coaliciones=True,
        votos_redistribuidos=None,
        mr_ganados_geograficos=None,
        print_debug=False
    )
    
    # Extraer datos del resultado
    # El motor SIN TOPES devuelve estructura diferente: mr, rp, tot
    mr_dict = resultado.get('mr', {})
    rp_dict = resultado.get('rp', {})
    tot_dict = resultado.get('tot', {})
    
    # Filtrar solo MORENA y aliados
    partidos_4t = ['MORENA', 'PT', 'PVEM']
    
    datos = []
    
    for partido in partidos_4t:
        if partido in tot_dict:  # Solo si el partido tiene datos
            datos.append({
                'ESCENARIO': '300-100 SIN TOPES',
                'AÑO': anio,
                'MR': 300,
                'RP': 100,
                'TOTAL_ESCAÑOS': 400,
                'PARTIDO': partido,
                'ESCAÑOS_MR': mr_dict.get(partido, 0),
                'ESCAÑOS_RP': rp_dict.get(partido, 0),
                'ESCAÑOS_TOTAL': tot_dict.get(partido, 0),
                'PCT_ESCAÑOS': round(tot_dict.get(partido, 0) / 400 * 100, 2)
            })
    
    return datos

# Procesar ambos años
print("\n🔄 Procesando escenarios 300-100 SIN TOPES...")

datos_2021 = generar_escenario_300_sin_topes(2021)
datos_2024 = generar_escenario_300_sin_topes(2024)

# Combinar datos
todos_datos = datos_2021 + datos_2024

# Crear DataFrame
df_nuevo = pd.DataFrame(todos_datos)

print("\n📊 RESULTADOS GENERADOS:")
print("="*80)
print(df_nuevo.to_string(index=False))
print("="*80)

# Cargar CSV existente
csv_path = 'redistritacion/outputs/comparacion_escenarios_completa.csv'
df_existente = pd.read_csv(csv_path)

print(f"\n📂 CSV existente tiene {len(df_existente)} filas")

# Filtrar CSV existente: eliminar 300-100 SIN TOPES si existe, y dejar solo 4T
print("\n🔄 Filtrando datos existentes...")

# Eliminar escenario 300-100 SIN TOPES del CSV existente (si existe)
df_existente = df_existente[df_existente['ESCENARIO'] != '300-100 SIN TOPES']

# Filtrar solo partidos de la 4T en TODOS los escenarios
partidos_4t = ['MORENA', 'PT', 'PVEM']
df_existente = df_existente[df_existente['PARTIDO'].isin(partidos_4t)]

print(f"📂 Después de filtrar solo 4T: {len(df_existente)} filas")

# Combinar con nuevo escenario
df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)

# Ordenar por ESCENARIO, AÑO, PARTIDO
df_final = df_final.sort_values(['ESCENARIO', 'AÑO', 'PARTIDO']).reset_index(drop=True)

print(f"\n📊 CSV final tiene {len(df_final)} filas")

# Guardar
df_final.to_csv(csv_path, index=False)

print(f"\n✅ CSV actualizado guardado en: {csv_path}")

# Mostrar resumen
print("\n" + "="*80)
print("RESUMEN FINAL")
print("="*80)

print("\n📊 Escenarios incluidos:")
for escenario in df_final['ESCENARIO'].unique():
    count = len(df_final[df_final['ESCENARIO'] == escenario])
    print(f"  • {escenario}: {count} filas")

print("\n🎯 Partidos incluidos (solo 4T):")
for partido in sorted(df_final['PARTIDO'].unique()):
    count = len(df_final[df_final['PARTIDO'] == partido])
    print(f"  • {partido}: {count} filas")

print("\n📅 Años incluidos:")
for anio in sorted(df_final['AÑO'].unique()):
    count = len(df_final[df_final['AÑO'] == anio])
    print(f"  • {anio}: {count} filas")

print("\n" + "="*80)
print("✅ PROCESO COMPLETADO")
print("="*80)

# Mostrar tabla final completa
print("\n📊 TABLA FINAL COMPLETA:")
print("="*80)
print(df_final.to_string(index=False))
print("="*80)
