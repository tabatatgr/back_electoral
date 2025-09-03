import pandas as pd
from engine.procesar_diputados_v2 import extraer_coaliciones_de_siglado, cols_candidaturas_anio_con_coaliciones, partidos_de_col

def debug_primer_distrito():
    """Debug específico del primer distrito para ver por qué no entra a la lógica de coaliciones"""
    
    print("="*60)
    print("🔍 DEBUG ESPECÍFICO PRIMER DISTRITO")
    print("="*60)
    
    # Cargar datos
    df = pd.read_parquet("data/computos_diputados_2018.parquet")
    
    # Extraer coaliciones
    coaliciones_detectadas = extraer_coaliciones_de_siglado("data/siglado-diputados-2018.csv", 2018)
    print(f"🤝 COALICIONES DETECTADAS:")
    for nombre, partidos in coaliciones_detectadas.items():
        print(f"   - {nombre}: {partidos}")
    
    # Crear dataset con coaliciones
    recomposed = df.copy()
    for nombre_coalicion, partidos_coalicion in coaliciones_detectadas.items():
        votos_coalicion = sum(recomposed[p] for p in partidos_coalicion if p in recomposed.columns)
        recomposed[nombre_coalicion] = votos_coalicion
    
    # Obtener candidaturas
    candidaturas_cols = cols_candidaturas_anio_con_coaliciones(recomposed, 2018)
    print(f"\n🎯 CANDIDATURAS: {candidaturas_cols}")
    
    # Analizar primer distrito
    distrito = recomposed.iloc[0]
    entidad = distrito['ENTIDAD']
    num_distrito = distrito['DISTRITO']
    
    print(f"\n🗳️  DISTRITO: {entidad}-{num_distrito}")
    
    # Encontrar ganador (exactamente como en el código)
    max_votos = -1
    coalicion_ganadora = None
    
    print(f"\n📊 EVALUANDO CANDIDATURAS:")
    for col in candidaturas_cols:
        if col in distrito:
            votos = distrito[col]
            print(f"   - {col}: {votos:,.0f} votos")
            if votos > max_votos:
                max_votos = votos
                coalicion_ganadora = col
    
    print(f"\n🏆 GANADOR: {coalicion_ganadora} con {max_votos:,.0f} votos")
    print(f"¿Es coalición detectada?: {coalicion_ganadora in coaliciones_detectadas}")
    
    # Simular la lógica condicional
    print(f"\n🔄 SIMULANDO LÓGICA:")
    print(f"   - coalicion_ganadora: {coalicion_ganadora}")
    print(f"   - bool(coalicion_ganadora): {bool(coalicion_ganadora)}")
    print(f"   - coalicion_ganadora in coaliciones_detectadas: {coalicion_ganadora in coaliciones_detectadas}")
    
    if coalicion_ganadora:
        print("   ✅ Entra al if coalicion_ganadora")
        if coalicion_ganadora in coaliciones_detectadas:
            print("   ✅ Entra al if coalicion_ganadora in coaliciones_detectadas")
            print("   → Debería buscar en siglado")
        else:
            print("   ❌ NO entra al if coalicion_ganadora in coaliciones_detectadas")
            print("   → Va al else (partido individual)")
    else:
        print("   ❌ NO entra al if coalicion_ganadora")
        print("   → Va directo al fallback [GARANTÍA]")

if __name__ == "__main__":
    debug_primer_distrito()
