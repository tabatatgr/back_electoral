def get_pct_escanos_2021(partido, camara):
    df = pd.read_csv('data/escaños_resumen_camaras_2018_2021_2024_oficial_gallagher_ratio_promedio(2).csv')
    df_2021 = df[(df['Año'] == 2021) & (df['Cámara'] == camara)]
    if partido == 'COALICIÓN TOTAL':
        aliados = ['MORENA', 'PVEM', 'PT']
        pct = df_2021[df_2021['Partido'].isin(aliados)]['% Escaños'].sum()
        return pct
    else:
        row = df_2021[df_2021['Partido'] == partido]
        if not row.empty:
            return row.iloc[0]['% Escaños']
        else:
            return None
import pandas as pd

def get_pct_escanos_2024(partido, camara):
    df = pd.read_csv('data/escaños_resumen_camaras_2018_2021_2024_oficial_gallagher_ratio_promedio(2).csv')
    df_2024 = df[(df['Año'] == 2024) & (df['Cámara'] == camara)]
    if partido == 'COALICIÓN TOTAL':
        aliados = ['MORENA', 'PVEM', 'PT']
        pct = df_2024[df_2024['Partido'].isin(aliados)]['% Escaños'].sum()
        return pct
    else:
        row = df_2024[df_2024['Partido'] == partido]
        if not row.empty:
            return row.iloc[0]['% Escaños']
        else:
            return None
