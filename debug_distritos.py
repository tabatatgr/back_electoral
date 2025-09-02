import pandas as pd

def analizar_distritos():
    """Analizar cuántos distritos hay realmente en cada archivo"""
    
    años = [2018, 2021, 2024]
    
    for año in años:
        print(f"\n{'='*50}")
        print(f"📊 ANÁLISIS DISTRITOS {año}")
        print(f"{'='*50}")
        
        # Cargar parquet
        parquet_file = f"data/computos_diputados_{año}.parquet"
        df = pd.read_parquet(parquet_file)
        
        # Cargar siglado
        siglado_file = f"data/siglado-diputados-{año}.csv"
        try:
            siglado = pd.read_csv(siglado_file)
        except:
            print(f"❌ No se pudo cargar siglado: {siglado_file}")
            continue
        
        # Análisis parquet
        total_parquet = len(df)
        distritos_unicos_parquet = df.groupby(['ENTIDAD', 'DISTRITO']).size().shape[0]
        
        # Análisis siglado
        total_siglado = len(siglado)
        distritos_unicos_siglado = siglado.groupby(['entidad', 'distrito']).size().shape[0]
        
        print(f"📄 PARQUET:")
        print(f"   - Total filas: {total_parquet}")
        print(f"   - Distritos únicos: {distritos_unicos_parquet}")
        
        print(f"📄 SIGLADO:")
        print(f"   - Total filas: {total_siglado}")
        print(f"   - Distritos únicos: {distritos_unicos_siglado}")
        
        print(f"🔍 DIFERENCIA:")
        print(f"   - Distritos faltantes en siglado: {distritos_unicos_parquet - distritos_unicos_siglado}")
        
        # Verificar que todos los distritos del parquet están en siglado
        parquet_distritos = set(df.apply(lambda row: f"{row['ENTIDAD']}-{row['DISTRITO']}", axis=1))
        siglado_distritos = set(siglado.apply(lambda row: f"{row['entidad']}-{row['distrito']}", axis=1))
        
        faltantes = parquet_distritos - siglado_distritos
        print(f"   - Primeros 10 distritos faltantes: {list(faltantes)[:10]}")
        
        if año == 2018:
            print(f"✅ 2018 debería tener ~300 distritos y funciona bien")
        else:
            print(f"❌ {año} debería tener 300 distritos MR pero solo procesa {distritos_unicos_siglado}")

if __name__ == "__main__":
    analizar_distritos()
