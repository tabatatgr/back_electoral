#!/usr/bin/env python3
"""
Script de diagnóstico para verificar qué pasa en el PASO 1 del tope
"""
import numpy as np
from pathlib import Path
import pandas as pd
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from engine.procesar_diputados_v2 import procesar_diputados_v2

def test_paso1_debug():
    """
    Prueba con 75MR/25RP (375 MR + 125 RP = 500)
    MORENA debería recibir 311 MR + 0 RP = 311
    Pero el tope del +8% es 252
    """
    print("=" * 70)
    print("TEST: PASO 1 - Recorte de MR cuando excede tope")
    print("=" * 70)
    print()
    
    # Cargar datos
    parquet_path = Path(__file__).parent / "data" / "computos_diputados_2024.parquet"
    df = pd.read_parquet(parquet_path)
    
    # Procesar con 75MR/25RP
    resultado = procesar_diputados_v2(
        path_parquet=str(parquet_path),
        anio=2024,
        usar_coaliciones=True,
        max_seats=500,
        mr_seats=375,
        rp_seats=125,
        seed=42,
        print_debug=False
    )
    
    # Buscar MORENA en el resultado
    for idx, partido in enumerate(resultado['partidos']):
        if partido == 'MORENA':
            mr = int(resultado['s_mr'][idx])
            rp = int(resultado['s_rp'][idx])
            tot = int(resultado['s_tot'][idx])
            
            print(f"MORENA RESULTADOS:")
            print(f"  MR: {mr}")
            print(f"  RP: {rp}")
            print(f"  TOTAL: {tot}")
            print()
            
            # Cálculo del tope
            vote_share = float(resultado['v_nacional'][idx])
            max_pp = 0.08
            cap_teorico = np.floor((vote_share + max_pp) * 500)
            
            print(f"ANÁLISIS DEL TOPE:")
            print(f"  Vote share MORENA: {vote_share*100:.2f}%")
            print(f"  Tope teórico (+8%): {cap_teorico:.0f} escaños")
            print(f"  Total obtenido: {tot} escaños")
            print(f"  Diferencia: {tot - cap_teorico:.0f}")
            print()
            
            if tot > cap_teorico:
                print(f"⚠️ MORENA EXCEDE el tope por {int(tot - cap_teorico)} escaños")
            elif tot == cap_teorico:
                print(f"✓ MORENA está EXACTAMENTE en el tope")
            else:
                print(f"✓ MORENA está DENTRO del tope")
            
            break

if __name__ == "__main__":
    test_paso1_debug()
