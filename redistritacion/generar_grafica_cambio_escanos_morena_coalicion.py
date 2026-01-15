import pandas as pd
import matplotlib.pyplot as plt
import os

# Definir coalición
COALICION = ['MORENA', 'PT', 'PVEM']

# Leer datos oficiales
df = pd.read_csv('data/escaños_resumen_camaras_2018_2021_2024_oficial_gallagher_ratio_promedio(2).csv')

# Solo años 2021 y 2024
anios = [2021, 2024]
camara = 'Diputados'  # Cambia a 'Senado' si quieres ambas, o haz un loop

resultados = []
for anio in anios:
    df_c = df[(df['Año'] == anio) & (df['Cámara'] == camara)]
    morena = df_c[df_c['Partido'] == 'MORENA']['Total'].sum()
    coalicion = df_c[df_c['Partido'].isin(COALICION)]['Total'].sum()
    resultados.append({'Escenario': f'{anio}', 'Grupo': 'MORENA', 'Escaños': morena})
    resultados.append({'Escenario': f'{anio}', 'Grupo': 'Coalición', 'Escaños': coalicion})

# Calcular cambio 2024-2021
cambios = []
for grupo in ['MORENA', 'Coalición']:
    esc_2021 = next(r for r in resultados if r['Escenario']=='2021' and r['Grupo']==grupo)['Escaños']
    esc_2024 = next(r for r in resultados if r['Escenario']=='2024' and r['Grupo']==grupo)['Escaños']
    cambios.append({'Grupo': grupo, 'Cambio': esc_2024 - esc_2021, 'Escaños_2024': esc_2024})

# Gráfica
fig, ax = plt.subplots(figsize=(7,3))
y_labels = [f'2021-2024 {g}' for g in ['MORENA','Coalición']]
bar = ax.barh(y_labels, [c['Cambio'] for c in cambios], color=['#B8860B','#5D4037'])

# Etiquetas encima: total escaños 2024
for i, c in enumerate(cambios):
    ax.text(c['Cambio'], i, f"{c['Escaños_2024']} escaños", va='center', ha='left' if c['Cambio']>=0 else 'right', fontweight='bold', color='#424242', fontsize=11)

ax.set_xlabel('Cambio de escaños (2024 - 2021)')
ax.set_ylabel('Escenario - Grupo')
ax.set_title('Cambio de escaños 2021→2024 (Diputados)\nTotal actual encima de la barra')
plt.tight_layout()
os.makedirs('redistritacion/outputs/graficas_extra', exist_ok=True)
plt.savefig('redistritacion/outputs/graficas_extra/cambio_escanos_morena_coalicion.png', dpi=300)
plt.savefig('redistritacion/outputs/graficas_extra/cambio_escanos_morena_coalicion.svg')
plt.close()
print('Gráfica generada en redistritacion/outputs/graficas_extra/')
