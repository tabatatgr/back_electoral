"""
TABLA FINAL - DESGLOSE POR ESTADO PARA MAYORÍA SIMPLE
TODOS LOS ESCENARIOS INCLUIDOS
"""
import pandas as pd

# Leer CSV
df = pd.read_csv('redistritacion/outputs/distritos_morena_comparativa.csv')

# Filtrar SOLO mayoría simple
df_simple = df[df['TIPO_MAYORIA'] == 'SIMPLE'].copy()

print("="*120)
print("📊 TABLA COMPLETA - MAYORÍA SIMPLE - DISTRITOS MORENA POR ESTADO")
print("="*120)

# Crear tabla pivoteada
tabla = df_simple.pivot_table(
    index='ESTADO',
    columns='ESCENARIO',
    values='DISTRITOS_MORENA',
    aggfunc='first'
).fillna(0).astype(int)

# Agregar columna de distritos totales por escenario
totales_por_escenario = df_simple.groupby('ESCENARIO')['DISTRITOS_TOTALES'].first()

print("\nDISTRITOS GANADOS POR MORENA POR ESTADO EN CADA ESCENARIO:\n")
print(tabla.to_string())

print("\n" + "="*120)
print("TOTALES POR ESCENARIO:")
print("="*120)

for escenario in tabla.columns:
    df_esc = df_simple[df_simple['ESCENARIO'] == escenario]
    total_distritos = df_esc['DISTRITOS_TOTALES'].sum()
    total_morena = tabla[escenario].sum()
    mr_necesarios = df_esc['MR_NECESARIOS'].iloc[0]
    pct_votos = df_esc['PCT_VOTOS_NECESARIO'].iloc[0]
    pct_distritos = (total_morena / total_distritos * 100)
    
    print(f"\n{escenario}:")
    print(f"  Total MR: {total_distritos}")
    print(f"  MORENA gana: {total_morena} distritos ({pct_distritos:.1f}%)")
    print(f"  Necesita para mayoría simple: {mr_necesarios} distritos")
    print(f"  % Votos necesario: {pct_votos}%")
    print(f"  ¿Alcanza? {'✅ SÍ' if total_morena >= mr_necesarios else f'❌ NO (faltan {mr_necesarios - total_morena})'}")

# Exportar tabla completa
tabla.to_csv('outputs/TABLA_MAYORIA_SIMPLE_TODOS_ESCENARIOS.csv', encoding='utf-8-sig')
print(f"\n✅ Tabla guardada en: outputs/TABLA_MAYORIA_SIMPLE_TODOS_ESCENARIOS.csv")

# Crear tabla resumen
print("\n\n" + "="*120)
print("📋 RESUMEN COMPARATIVO")
print("="*120)

resumen = []
for escenario in tabla.columns:
    df_esc = df_simple[df_simple['ESCENARIO'] == escenario]
    total_distritos = df_esc['DISTRITOS_TOTALES'].sum()
    total_morena = tabla[escenario].sum()
    mr_necesarios = df_esc['MR_NECESARIOS'].iloc[0]
    
    resumen.append({
        'ESCENARIO': escenario,
        'TOTAL_MR': total_distritos,
        'MORENA_GANA': total_morena,
        'PCT_MORENA': f"{(total_morena/total_distritos*100):.1f}%",
        'NECESITA': mr_necesarios,
        'FALTAN': max(0, mr_necesarios - total_morena),
        'ALCANZA': 'SÍ' if total_morena >= mr_necesarios else 'NO'
    })

df_resumen = pd.DataFrame(resumen)
print(df_resumen.to_string(index=False))

df_resumen.to_csv('outputs/RESUMEN_MAYORIA_SIMPLE.csv', index=False, encoding='utf-8-sig')
print(f"\n✅ Resumen guardado en: outputs/RESUMEN_MAYORIA_SIMPLE.csv")

print("\n" + "="*120)
print("✅ PROCESO COMPLETADO")
print("="*120)
