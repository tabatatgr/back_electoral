#!/usr/bin/env python3
"""
Script para revisar el cálculo de MR en detalle
"""

import sys
import os
sys.path.append(os.path.abspath('.'))

import pandas as pd
import numpy as np
from engine.procesar_diputados_v2 import norm_ascii_up, normalize_entidad_ascii, extraer_coaliciones_de_siglado, agregar_columnas_coalicion, cols_candidaturas_anio_con_coaliciones

def debug_mr_calculation():
    """Debug del cálculo de MR paso a paso"""
    
    print("=" * 60)
    print("DEBUG CÁLCULO DE MAYORÍA RELATIVA 2021")
    print("=" * 60)
    
    # Cargar datos
    df = pd.read_parquet("data/computos_diputados_2021.parquet")
    print(f"✅ Datos cargados: {df.shape}")
    
    # Normalizar columnas
    df.columns = [norm_ascii_up(c) for c in df.columns]
    
    # Normalizar entidades y distritos
    if 'ENTIDAD' in df.columns:
        df['ENTIDAD'] = df['ENTIDAD'].apply(normalize_entidad_ascii)
    if 'DISTRITO' in df.columns:
        df['DISTRITO'] = pd.to_numeric(df['DISTRITO'], errors='coerce').fillna(0).astype(int)
    
    print(f"✅ Normalización completada")
    
    # Detectar coaliciones
    coaliciones_detectadas = extraer_coaliciones_de_siglado("data/siglado-diputados-2021.csv", 2021)
    if coaliciones_detectadas:
        df = agregar_columnas_coalicion(df, coaliciones_detectadas)
        print(f"✅ Coaliciones agregadas: {coaliciones_detectadas}")
    
    # Obtener candidaturas
    candidaturas_cols = cols_candidaturas_anio_con_coaliciones(df, 2021)
    print(f"✅ Candidaturas encontradas: {candidaturas_cols}")
    
    # Calcular ganadores por distrito
    partidos_base = ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA', 'PES', 'RSP', 'FXM']
    mr_raw = {}
    
    ganadores_detalle = []
    
    for idx, distrito in df.iterrows():
        entidad = distrito['ENTIDAD']
        num_distrito = distrito['DISTRITO']
        
        # Encontrar candidatura con más votos
        max_votos = -1
        ganador = None
        votos_por_candidatura = {}
        
        for col in candidaturas_cols:
            if col in distrito:
                votos = distrito[col]
                votos_por_candidatura[col] = votos
                if votos > max_votos:
                    max_votos = votos
                    ganador = col
        
        ganadores_detalle.append({
            'entidad': entidad,
            'distrito': num_distrito,
            'ganador': ganador,
            'votos': max_votos,
            'votos_detalle': votos_por_candidatura
        })
        
        # Contar para MR
        if ganador:
            if ganador in partidos_base:
                mr_raw[ganador] = mr_raw.get(ganador, 0) + 1
            else:
                # Es una coalición, usar siglado para resolver
                print(f"Coalición {ganador} ganó en {entidad}-{num_distrito}")
    
    print(f"\n📊 RESUMEN DE MR:")
    print("-" * 40)
    
    total_mr = sum(mr_raw.values())
    for partido, escanos in sorted(mr_raw.items(), key=lambda x: x[1], reverse=True):
        print(f"{partido:<8}: {escanos:>3} escaños")
    
    print(f"{'TOTAL':<8}: {total_mr:>3} escaños")
    
    # Mostrar algunos ejemplos de MC
    mc_distritos = [g for g in ganadores_detalle if g['ganador'] == 'MC']
    print(f"\n🔍 MC GANÓ {len(mc_distritos)} DISTRITOS:")
    for i, distrito in enumerate(mc_distritos[:5]):  # Solo primeros 5
        print(f"  {i+1}. {distrito['entidad']}-{distrito['distrito']}: {distrito['votos']:,} votos")
        # Mostrar competencia
        top_3 = sorted(distrito['votos_detalle'].items(), key=lambda x: x[1], reverse=True)[:3]
        for j, (cand, votos) in enumerate(top_3):
            if j == 0:
                print(f"      🥇 {cand}: {votos:,}")
            elif j == 1:
                print(f"      🥈 {cand}: {votos:,}")
            else:
                print(f"      🥉 {cand}: {votos:,}")
    
    if len(mc_distritos) > 5:
        print(f"  ... y {len(mc_distritos) - 5} más")

if __name__ == "__main__":
    debug_mr_calculation()
