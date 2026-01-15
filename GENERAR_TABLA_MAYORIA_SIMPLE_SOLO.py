"""
Genera tabla SOLO PARA MAYORÍA SIMPLE por estado.
Todos los escenarios configurados para alcanzar 201 escaños (mayoría simple).
"""

import sys
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from redistritacion.modulos.reparto_distritos import repartir_distritos_hare
from redistritacion.modulos.distritacion import cargar_secciones_ine


def calcular_distritos_morena(mr_total, mr_morena_total, eficiencia=1.1):
    """Calcula distritos ganados por MORENA por estado.
    
    Args:
        mr_total: Total de distritos MR del escenario
        mr_morena_total: Total de MR que MORENA debe ganar (del CSV)
    """
    secciones = cargar_secciones_ine()
    poblacion_por_estado = secciones.groupby('ENTIDAD')['POBTOT'].sum().to_dict()
    
    # Redistribuir distritos por población
    asignacion_distritos = repartir_distritos_hare(
        poblacion_estados=poblacion_por_estado,
        n_distritos=mr_total,
        piso_constitucional=2
    )
    
    # Calcular proporción real que MORENA debe ganar
    proporcion_morena = mr_morena_total / mr_total
    
    # Calcular distritos ganados por estado
    resultados = []
    distritos_asignados = 0
    
    for estado in sorted(poblacion_por_estado.keys()):
        distritos_totales = asignacion_distritos[estado]
        # Distritos base por proporción
        distritos_morena = distritos_totales * proporcion_morena
        
        resultados.append({
            'ESTADO': estado,
            'DISTRITOS_TOTALES': distritos_totales,
            'DISTRITOS_MORENA_REAL': distritos_morena,
            'DISTRITOS_MORENA': int(round(distritos_morena))
        })
        distritos_asignados += int(round(distritos_morena))
    
    # Ajuste por redondeo para que sume EXACTAMENTE mr_morena_total
    df_result = pd.DataFrame(resultados)
    diferencia = mr_morena_total - distritos_asignados
    
    if diferencia != 0:
        # Ajustar estados con mayor residuo
        df_result['RESIDUO'] = df_result['DISTRITOS_MORENA_REAL'] - df_result['DISTRITOS_MORENA']
        df_result = df_result.sort_values('RESIDUO', ascending=(diferencia < 0))
        
        for i in range(abs(diferencia)):
            idx = df_result.index[i]
            df_result.loc[idx, 'DISTRITOS_MORENA'] += (1 if diferencia > 0 else -1)
    
    return df_result[['ESTADO', 'DISTRITOS_TOTALES', 'DISTRITOS_MORENA']]


print("="*120)
print("📊 TABLA MAYORÍA SIMPLE - DISTRITOS MORENA POR ESTADO")
print("="*120)
print("\n⚠️  SOLO MAYORÍA SIMPLE (201 escaños) - TODOS LOS ESCENARIOS\n")

# Cargar votos mínimos del CSV
votos_csv = pd.read_csv('redistritacion/outputs/votos_minimos_morena.csv')
votos_ef11 = votos_csv[votos_csv['eficiencia_val'] == 1.1]

print("Escenarios calculados:")

# TODOS los escenarios con MAYORÍA SIMPLE
escenarios = []
for _, row in votos_ef11.iterrows():
    nombre = row['escenario']
    mr_total = int(row['mr_total'])
    mr_morena = int(row['mayoria_simple_mr'])  # MR exactos del CSV
    pct_votos = row['mayoria_simple_votos']
    
    escenarios.append({
        'nombre': nombre,
        'mr_total': mr_total,
        'mr_morena': mr_morena,
        'pct_votos': pct_votos,
        'rp_morena': int(row['mayoria_simple_rp']),
        'total_escanos': int(row['mayoria_simple_mr']) + int(row['mayoria_simple_rp'])
    })
    
    print(f"  • {nombre}: {pct_votos}% votos → {mr_morena} MR + {int(row['mayoria_simple_rp'])} RP = {int(row['mayoria_simple_mr']) + int(row['mayoria_simple_rp'])} escaños")

print("\nCalculando distribución por estado...\n")

# Calcular cada escenario
datos_escenarios = {}
for esc in escenarios:
    df = calcular_distritos_morena(esc['mr_total'], esc['mr_morena'])
    datos_escenarios[esc['nombre']] = df

# Crear tabla pivoteada
print("="*120)
print("DISTRITOS MR GANADOS POR MORENA EN CADA ESCENARIO (MAYORÍA SIMPLE)")
print("="*120)

# Crear tabla consolidada
df_base = datos_escenarios['300-100 CON TOPES'][['ESTADO']].copy()

for esc in escenarios:
    nombre = esc['nombre']
    df_esc = datos_escenarios[nombre]
    
    # Agregar columnas de total y morena
    df_base = df_base.merge(
        df_esc[['ESTADO', 'DISTRITOS_TOTALES', 'DISTRITOS_MORENA']].rename(
            columns={
                'DISTRITOS_TOTALES': f'{nombre}_TOTAL',
                'DISTRITOS_MORENA': f'{nombre}_MORENA'
            }
        ),
        on='ESTADO',
        how='left'
    )

# Imprimir tabla
print("\n" + df_base.to_string(index=False))

# Calcular totales
print("\n" + "="*120)
print("TOTALES POR ESCENARIO")
print("="*120)

resumen = []
for esc in escenarios:
    nombre = esc['nombre']
    df_esc = datos_escenarios[nombre]
    total_mr = df_esc['DISTRITOS_TOTALES'].sum()
    total_morena = df_esc['DISTRITOS_MORENA'].sum()
    
    print(f"\n{nombre}:")
    print(f"  % Votos necesario: {esc['pct_votos']}%")
    print(f"  Total MR: {total_mr}")
    print(f"  MORENA gana: {total_morena} MR")
    print(f"  + RP: {esc['rp_morena']}")
    print(f"  = TOTAL: {esc['total_escanos']} escaños ({'✅ Mayoría simple' if esc['total_escanos'] >= 201 else '❌ No alcanza'})")
    
    resumen.append({
        'ESCENARIO': nombre,
        'PCT_VOTOS': f"{esc['pct_votos']}%",
        'MR_TOTAL': total_mr,
        'MR_MORENA': total_morena,
        'RP_MORENA': esc['rp_morena'],
        'TOTAL_ESCANOS': esc['total_escanos'],
        'ALCANZA': '✅' if esc['total_escanos'] >= 201 else '❌'
    })

# Guardar CSV
csv_file = 'outputs/MAYORIA_SIMPLE_TODOS_ESCENARIOS.csv'
df_base.to_csv(csv_file, index=False, encoding='utf-8-sig')
print(f"\n✅ Tabla guardada en: {csv_file}")

# Guardar resumen
df_resumen = pd.DataFrame(resumen)
csv_resumen = 'outputs/RESUMEN_MAYORIA_SIMPLE.csv'
df_resumen.to_csv(csv_resumen, index=False, encoding='utf-8-sig')
print(f"✅ Resumen guardado en: {csv_resumen}")

print("\n" + "="*120)
print("📋 RESUMEN COMPARATIVO - MAYORÍA SIMPLE")
print("="*120)
print(df_resumen.to_string(index=False))

print("\n" + "="*120)
print("✅ PROCESO COMPLETADO - SOLO MAYORÍA SIMPLE")
print("="*120)
