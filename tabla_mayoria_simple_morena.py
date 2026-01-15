"""
Genera tabla de MAYORÍA SIMPLE con distritos MORENA por estado.
"""
import pandas as pd

# Leer CSV
df = pd.read_csv('redistritacion/outputs/distritos_morena_comparativa.csv')

# Filtrar solo mayoría simple
df_simple = df[df['TIPO_MAYORIA'] == 'SIMPLE'].copy()

print("="*100)
print("📊 MAYORÍA SIMPLE - DISTRITOS GANADOS POR MORENA")
print("="*100)

# Agrupar por escenario
escenarios = df_simple['ESCENARIO'].unique()

for escenario in escenarios:
    df_esc = df_simple[df_simple['ESCENARIO'] == escenario]
    
    print(f"\n{'='*100}")
    print(f"🏛️  ESCENARIO: {escenario}")
    print(f"{'='*100}")
    print(f"MR necesarios para mayoría simple: {df_esc['MR_NECESARIOS'].iloc[0]}")
    print(f"% Votos necesario: {df_esc['PCT_VOTOS_NECESARIO'].iloc[0]}%")
    print(f"{'='*100}\n")
    
    # Tabla por estado
    tabla = df_esc[['ESTADO', 'DISTRITOS_TOTALES', 'DISTRITOS_MORENA', 'PCT_DISTRITOS']].copy()
    tabla['PCT_DISTRITOS'] = tabla['PCT_DISTRITOS'].round(1)
    tabla = tabla.rename(columns={
        'ESTADO': 'Estado',
        'DISTRITOS_TOTALES': 'Total Distritos',
        'DISTRITOS_MORENA': 'Distritos MORENA',
        'PCT_DISTRITOS': '% MORENA'
    })
    
    print(tabla.to_string(index=False))
    
    # Resumen
    total_distritos = df_esc['DISTRITOS_TOTALES'].sum()
    total_morena = df_esc['DISTRITOS_MORENA'].sum()
    pct_morena = (total_morena / total_distritos * 100)
    
    print(f"\n{'─'*100}")
    print(f"TOTAL: {total_morena} de {total_distritos} distritos ({pct_morena:.1f}%)")
    print(f"{'─'*100}")
    
    # Guardar CSV individual
    csv_file = f"outputs/mayoria_simple_{escenario.replace(' ', '_').replace('-', '_')}.csv"
    tabla.to_csv(csv_file, index=False, encoding='utf-8-sig')
    print(f"✅ Guardado en: {csv_file}")

# Crear tabla comparativa final
print("\n\n" + "="*100)
print("📊 COMPARATIVA ENTRE ESCENARIOS - MAYORÍA SIMPLE")
print("="*100)

comparativa = []
for escenario in escenarios:
    df_esc = df_simple[df_simple['ESCENARIO'] == escenario]
    total_distritos = df_esc['DISTRITOS_TOTALES'].sum()
    total_morena = df_esc['DISTRITOS_MORENA'].sum()
    pct_morena = (total_morena / total_distritos * 100)
    mr_necesarios = df_esc['MR_NECESARIOS'].iloc[0]
    pct_votos = df_esc['PCT_VOTOS_NECESARIO'].iloc[0]
    
    comparativa.append({
        'Escenario': escenario,
        'Total MR': total_distritos,
        'MR MORENA': total_morena,
        '% Distritos': f"{pct_morena:.1f}%",
        'MR Necesarios': mr_necesarios,
        '¿Alcanza?': '✅ Sí' if total_morena >= mr_necesarios else '❌ No',
        '% Votos Necesario': f"{pct_votos}%"
    })

df_comp = pd.DataFrame(comparativa)
print(df_comp.to_string(index=False))

# Guardar comparativa
df_comp.to_csv('outputs/comparativa_mayoria_simple_final.csv', index=False, encoding='utf-8-sig')
print(f"\n✅ Comparativa guardada en: outputs/comparativa_mayoria_simple_final.csv")

print("\n" + "="*100)
print("✅ PROCESO COMPLETADO")
print("="*100)
