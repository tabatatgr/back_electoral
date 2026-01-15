import pandas as pd
import matplotlib.pyplot as plt
import os

# Configuración de partidos por coalición
COALICION_DIP = ['MORENA', 'PT', 'PVEM']
COALICION_SEN = ['MORENA', 'PT', 'PVEM']

# Leer datos
archivo = 'data/escaños_resumen_camaras_2018_2021_2024_oficial_gallagher_ratio_promedio(2).csv'
df = pd.read_csv(archivo)

# Filtrar solo cámaras relevantes
camaras = ['Diputados', 'Senado']
resultados = []

for camara in camaras:
    for anio in sorted(df['Año'].unique()):
        df_c = df[(df['Cámara'] == camara) & (df['Año'] == anio)]
        if df_c.empty:
            continue
        # MORENA
        morena = df_c[df_c['Partido'] == 'MORENA']['Total'].sum()
        # Coalición
        if camara == 'Diputados':
            coalicion = df_c[df_c['Partido'].isin(COALICION_DIP)]['Total'].sum()
        else:
            coalicion = df_c[df_c['Partido'].isin(COALICION_SEN)]['Total'].sum()
        resultados.append({'Escenario': f'{anio} {camara}', 'Grupo': 'MORENA', 'Escaños': morena})
        resultados.append({'Escenario': f'{anio} {camara}', 'Grupo': 'Coalición', 'Escaños': coalicion})

# Crear DataFrame para graficar
df_plot = pd.DataFrame(resultados)

# Ordenar para que el eje Y sea Escenario - Grupo
labels = [f"{row['Escenario']} - {row['Grupo']}" for _, row in df_plot.iterrows()]
valores = df_plot['Escaños']

# Crear gráfica
plt.figure(figsize=(10, 6))
plt.barh(labels, valores, color=['#1B5E20' if g=='MORENA' else '#FFC107' for g in df_plot['Grupo']])
plt.xlabel('Número de escaños')
plt.title('Escaños actuales de MORENA y Coalición por escenario')
plt.tight_layout()

# Crear carpeta de salida
os.makedirs('outputs/graficas_resumen', exist_ok=True)
plt.savefig('outputs/graficas_resumen/escanos_morena_coalicion.png', dpi=300)
plt.savefig('outputs/graficas_resumen/escanos_morena_coalicion.svg')
plt.close()

print('Gráfica generada en outputs/graficas_resumen/')
