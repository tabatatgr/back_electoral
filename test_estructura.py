"""
Test simple para verificar estructura de datos
"""

from engine.procesar_senadores_v2 import procesar_senadores_v2

def test_estructura():
    """Test para ver qué devuelve procesar_senadores_v2"""
    
    config = {
        "anio": 2018,
        "max_seats": 96,
        "mr_seats": 64,
        "rp_seats": 32,
        "sistema": "mixto",
        "pm_seats": 0,
        "umbral": 0.03,
        "path_parquet": "data/computos_senado_2018.parquet",
        "path_siglado": "data/siglado_senado_2018_corregido.csv"
    }
    
    print("🔍 VERIFICANDO ESTRUCTURA DE DATOS")
    print("=" * 50)
    
    result = procesar_senadores_v2(**config)
    
    print(f"Tipo: {type(result)}")
    print(f"Keys: {list(result.keys())}")
    
    for key, value in result.items():
        if isinstance(value, dict):
            print(f"{key}: dict con {len(value)} elementos")
            if len(value) <= 10:  # Mostrar solo si no es muy grande
                print(f"   {value}")
        elif isinstance(value, list):
            print(f"{key}: list con {len(value)} elementos")
            if len(value) <= 3:
                print(f"   {value}")
            else:
                print(f"   Primeros 3: {value[:3]}")
        else:
            print(f"{key}: {type(value)} = {value}")

if __name__ == "__main__":
    test_estructura()
