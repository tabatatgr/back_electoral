import pandas as pd
import sys
sys.path.append('.')
from engine.recomposicion import _is_candidate_col, _is_coalition_col, _tokens_from_col

def analizar_coaliciones_por_año(year, chamber):
    """Analiza las coaliciones detectadas para un año y cámara específicos"""
    print(f"\n=== ANÁLISIS {year} - {chamber.upper()} ===")
    
    # Cargar datos
    if chamber == "diputados":
        file_path = f'data/computos_diputados_{year}.parquet'
    else:
        file_path = f'data/computos_senado_{year}.parquet'
    
    try:
        df = pd.read_parquet(file_path)
        print(f"Dataset encontrado: {file_path}")
        print(f"Shape: {df.shape}")
        print(f"Columnas: {df.columns.tolist()}")
        
        # Detectar coaliciones
        cand_cols = [c for c in df.columns if _is_candidate_col(c, year)]
        coal_cols = [c for c in cand_cols if _is_coalition_col(c, year)]
        
        print(f"Columnas candidatas: {len(cand_cols)} -> {cand_cols}")
        print(f"Columnas coalición: {len(coal_cols)} -> {coal_cols}")
        
        if coal_cols:
            print("✅ COALICIONES DETECTADAS:")
            for coal in coal_cols:
                try:
                    tokens = _tokens_from_col(coal)
                    total_votos = df[coal].sum()
                    print(f"  {coal}: {tokens} -> {total_votos:,} votos")
                    
                    # Verificar si MC está en alguna coalición
                    if 'MC' in tokens:
                        print(f"    🎯 MC ESTÁ EN ESTA COALICIÓN!")
                except Exception as e:
                    print(f"  {coal}: Error -> {e}")
        else:
            print("❌ NO HAY COALICIONES DETECTADAS")
            # Buscar MC individual
            if 'MC' in df.columns:
                mc_votos = df['MC'].sum()
                print(f"  MC individual: {mc_votos:,} votos")
            else:
                print("  MC no está en el dataset")
                
        return len(coal_cols) > 0
        
    except FileNotFoundError:
        print(f"❌ Dataset no encontrado: {file_path}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

# Analizar todos los años disponibles
años = [2018, 2021, 2024]
camaras = ["diputados", "senado"]

resumen = {}

for año in años:
    resumen[año] = {}
    for camara in camaras:
        tiene_coaliciones = analizar_coaliciones_por_año(año, camara)
        resumen[año][camara] = tiene_coaliciones

print("\n" + "="*60)
print("RESUMEN GENERAL")
print("="*60)

for año in años:
    print(f"\n{año}:")
    for camara in camaras:
        status = "✅ CON COALICIONES" if resumen[año][camara] else "❌ SIN COALICIONES"
        print(f"  {camara.capitalize()}: {status}")

print("\n🔍 CONCLUSIÓN:")
problemas = []
for año in años:
    for camara in camaras:
        if not resumen[año][camara]:
            problemas.append(f"{año}-{camara}")

if problemas:
    print(f"❌ Problemas de coaliciones detectados en: {', '.join(problemas)}")
    print("   MC no recibirá escaños de coalición en estos casos.")
else:
    print("✅ Todos los años tienen coaliciones correctamente detectadas.")
