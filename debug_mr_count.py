import pandas as pd
from engine.procesar_diputados_v2 import procesar_diputados_v2

def debug_mr_processing():
    """Debug cuántos distritos MR se procesan en cada año"""
    
    años = [2018, 2021, 2024]
    
    for año in años:
        print(f"\n{'='*50}")
        print(f"🔍 ANÁLISIS DETALLADO AÑO {año}")
        print(f"{'='*50}")
        
        # Cargar datos
        parquet_file = f"data/computos_diputados_{año}.parquet"
        df = pd.read_parquet(parquet_file)
        
        # Procesar con debug activado
        print(f"\n📊 Procesando {año} con DEBUG activado...")
        
        try:
            resultado = procesar_diputados_v2(
                anio=año,
                max_seats=500,
                mr_seats=None,  # Permitir cálculo automático
                rp_seats=200,
                print_debug=True  # ACTIVAR DEBUG
            )
            
            print(f"\n📈 RESUMEN {año}:")
            print(f"   - Total escaños: {sum(resultado['escanos'].values())}")
            print(f"   - Total MR: {sum(resultado['mr'].values())}")
            print(f"   - Total RP: {sum(resultado['rp'].values())}")
            
        except Exception as e:
            print(f"❌ Error procesando {año}: {e}")

if __name__ == "__main__":
    debug_mr_processing()
