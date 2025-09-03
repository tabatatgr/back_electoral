import pandas as pd
from engine.procesar_diputados_v2 import cols_candidaturas_anio_con_coaliciones

def debug_candidaturas_2018():
    """Debug qué candidaturas se detectan en 2018"""
    
    print("="*60)
    print("🔍 DEBUG CANDIDATURAS 2018")
    print("="*60)
    
    # Cargar parquet
    df = pd.read_parquet("data/computos_diputados_2018.parquet")
    
    print(f"📋 COLUMNAS ORIGINALES PARQUET:")
    print(f"   {list(df.columns)}")
    
    # Simular el proceso de agregar coaliciones
    from engine.procesar_diputados_v2 import extraer_coaliciones_de_siglado
    
    coaliciones_detectadas = extraer_coaliciones_de_siglado("data/siglado-diputados-2018.csv", 2018)
    print(f"\n🤝 COALICIONES DETECTADAS:")
    for nombre, partidos in coaliciones_detectadas.items():
        print(f"   - {nombre}: {partidos}")
    
    # Agregar coaliciones al dataset (simulando el proceso)
    recomposed = df.copy()
    
    # Crear columnas de coaliciones
    for nombre_coalicion, partidos_coalicion in coaliciones_detectadas.items():
        votos_coalicion = sum(recomposed[p] for p in partidos_coalicion if p in recomposed.columns)
        recomposed[nombre_coalicion] = votos_coalicion
        print(f"   - Agregada columna: {nombre_coalicion}")
    
    print(f"\n📋 COLUMNAS DESPUÉS DE AGREGAR COALICIONES:")
    print(f"   {list(recomposed.columns)}")
    
    # Obtener candidaturas
    candidaturas_cols = cols_candidaturas_anio_con_coaliciones(recomposed, 2018)
    print(f"\n🎯 CANDIDATURAS DETECTADAS:")
    print(f"   {candidaturas_cols}")
    
    # Probar en algunos distritos
    print(f"\n🗳️  EJEMPLO DISTRITO 1:")
    distrito_ejemplo = recomposed.iloc[0]
    entidad = distrito_ejemplo['ENTIDAD']
    num_distrito = distrito_ejemplo['DISTRITO']
    
    print(f"   - {entidad}-{num_distrito}")
    
    for col in candidaturas_cols:
        if col in distrito_ejemplo:
            votos = distrito_ejemplo[col]
            print(f"     * {col}: {votos:,.0f} votos")
    
    # Encontrar ganador
    max_votos = -1
    ganador = None
    for col in candidaturas_cols:
        if col in distrito_ejemplo and distrito_ejemplo[col] > max_votos:
            max_votos = distrito_ejemplo[col]
            ganador = col
    
    print(f"   - GANADOR: {ganador} con {max_votos:,.0f} votos")
    print(f"   - ¿Es coalición?: {ganador in coaliciones_detectadas}")

if __name__ == "__main__":
    debug_candidaturas_2018()
