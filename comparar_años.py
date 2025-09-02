#!/usr/bin/env python3
"""
Comparar el procesamiento de diputados entre 2018, 2021 y 2024
"""

import sys
import os
sys.path.append(os.path.abspath('.'))

from engine.procesar_diputados_v2 import procesar_diputados_v2
import pandas as pd

def comparar_años():
    """Compara el procesamiento de los tres años"""
    
    años = [2018, 2021, 2024]
    
    print("=" * 80)
    print("COMPARACIÓN ENTRE AÑOS - DIPUTADOS PLAN VIGENTE")
    print("=" * 80)
    
    for anio in años:
        print(f"\n{'='*20} AÑO {anio} {'='*20}")
        
        # Verificar archivos
        path_parquet = f"data/computos_diputados_{anio}.parquet"
        path_siglado = f"data/siglado-diputados-{anio}.csv"
        
        if not os.path.exists(path_parquet):
            print(f"❌ No existe: {path_parquet}")
            continue
        if not os.path.exists(path_siglado):
            print(f"❌ No existe: {path_siglado}")
            continue
        
        print(f"✅ Archivos encontrados")
        
        # Inspeccionar datos
        try:
            df = pd.read_parquet(path_parquet)
            siglado = pd.read_csv(path_siglado)
            
            print(f"📊 Datos básicos:")
            print(f"   - Parquet shape: {df.shape}")
            print(f"   - Siglado shape: {siglado.shape}")
            print(f"   - Columnas parquet: {list(df.columns)[:10]}...")
            print(f"   - Columnas siglado: {list(siglado.columns)}")
            
            # Verificar distritos únicos
            if 'ENTIDAD' in df.columns and 'DISTRITO' in df.columns:
                distritos_unicos = df.groupby(['ENTIDAD', 'DISTRITO']).size().shape[0]
                print(f"   - Distritos únicos en parquet: {distritos_unicos}")
            
            if 'entidad' in siglado.columns and 'distrito' in siglado.columns:
                distritos_siglado = siglado.groupby(['entidad', 'distrito']).size().shape[0]
                print(f"   - Distritos únicos en siglado: {distritos_siglado}")
            elif 'entidad_ascii' in siglado.columns:
                distritos_siglado = siglado.groupby(['entidad_ascii', 'distrito']).size().shape[0]
                print(f"   - Distritos únicos en siglado: {distritos_siglado}")
        
        except Exception as e:
            print(f"❌ Error inspeccionando datos: {e}")
            continue
        
        # Procesar
        try:
            print(f"\n🔄 Procesando año {anio}...")
            resultado = procesar_diputados_v2(
                path_parquet=path_parquet,
                anio=anio,
                path_siglado=path_siglado,
                max_seats=500,
                sistema="mixto",
                mr_seats=None,
                rp_seats=200,
                umbral=0.03,
                max_seats_per_party=300,
                quota_method="hare",
                divisor_method=None,
                print_debug=False  # Sin debug para comparación limpia
            )
            
            # Analizar resultados
            total_dict = resultado.get('tot', {})
            mr_dict = resultado.get('mr', {})
            rp_dict = resultado.get('rp', {})
            votos_dict = resultado.get('votos', {})
            
            total_escanos = sum(total_dict.values())
            total_mr = sum(mr_dict.values())
            total_rp = sum(rp_dict.values())
            total_votos = sum(votos_dict.values())
            
            print(f"📈 Resultados {anio}:")
            print(f"   - Total escaños: {total_escanos}")
            print(f"   - Total MR: {total_mr}")
            print(f"   - Total RP: {total_rp}")
            print(f"   - Total votos: {total_votos:,}")
            
            # Top 5 partidos
            partidos_top = sorted(total_dict.items(), key=lambda x: x[1], reverse=True)[:5]
            print(f"   - Top 5 partidos:")
            for partido, escanos in partidos_top:
                mr = mr_dict.get(partido, 0)
                rp = rp_dict.get(partido, 0)
                votos = votos_dict.get(partido, 0)
                pct = (escanos/total_escanos)*100 if total_escanos > 0 else 0
                print(f"     {partido}: {escanos} esc ({mr}MR+{rp}RP) = {pct:.1f}% | {votos:,} votos")
            
            # Verificar MC específicamente
            mc_total = total_dict.get('MC', 0)
            mc_mr = mr_dict.get('MC', 0)
            mc_rp = rp_dict.get('MC', 0)
            mc_votos = votos_dict.get('MC', 0)
            
            print(f"🔍 MC en {anio}:")
            print(f"   - Escaños: {mc_total} ({mc_mr}MR + {mc_rp}RP)")
            print(f"   - Votos: {mc_votos:,}")
            if total_votos > 0:
                print(f"   - % votos: {(mc_votos/total_votos)*100:.2f}%")
            if total_escanos > 0:
                print(f"   - % escaños: {(mc_total/total_escanos)*100:.2f}%")
                
        except Exception as e:
            print(f"❌ Error procesando {anio}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    comparar_años()
