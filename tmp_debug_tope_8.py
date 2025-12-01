#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug profundo: ¿Por qué el tope del 8% no está funcionando correctamente?
"""

from engine.procesar_diputados_v2 import procesar_diputados_v2
import pandas as pd

def test_tope_8_porciento():
    """
    Ver el tope del 8% en acción
    """
    
    print("="*80)
    print("ANÁLISIS DEL TOPE DEL 8% - 2024")
    print("="*80)
    
    # Primero, cargar los votos para ver el vote share real de MORENA
    df = pd.read_parquet("data/computos_diputados_2024.parquet")
    
    partidos = ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA']
    votos = {p: df[p].sum() for p in partidos if p in df.columns}
    total_votos = sum(votos.values())
    
    print(f"\nVOTOS NACIONALES 2024:")
    for p in sorted(votos.keys(), key=lambda x: votos[x], reverse=True):
        pct = (votos[p] / total_votos) * 100
        print(f"  {p:10s}: {votos[p]:>12,} votos ({pct:>5.2f}%)")
    
    print(f"\n  {'TOTAL':10s}: {total_votos:>12,} votos")
    
    morena_vote_share = votos['MORENA'] / total_votos
    print(f"\nMORENA vote share: {morena_vote_share:.4f} ({morena_vote_share*100:.2f}%)")
    
    # Calcular límite teórico del 8%
    for total_escanos in [400, 500]:
        limite_teorico = (morena_vote_share + 0.08) * total_escanos
        print(f"\nLímite teórico 8% con {total_escanos} escaños:")
        print(f"  ({morena_vote_share:.4f} + 0.08) × {total_escanos} = {limite_teorico:.2f} escaños")
        print(f"  Redondeado: {int(limite_teorico)} escaños")
    
    # Ahora probar las configuraciones
    configs = [
        {"nombre": "50MR_50RP", "total": 500, "mr": 250, "rp": 250},
        {"nombre": "75MR_25RP", "total": 500, "mr": 375, "rp": 125},
    ]
    
    for config in configs:
        print("\n" + "="*80)
        print(f"CONFIGURACIÓN: {config['nombre']} ({config['mr']} MR + {config['rp']} RP = {config['total']})")
        print("="*80)
        
        resultado = procesar_diputados_v2(
            path_parquet="data/computos_diputados_2024.parquet",
            anio=2024,
            path_siglado="data/siglado-diputados-2024.csv",
            max_seats=config['total'],
            sistema="mixto",
            mr_seats=config['mr'],
            rp_seats=config['rp'],
            umbral=0.03,
            quota_method="hare",
            usar_coaliciones=True,
            print_debug=False  # Sin debug para output limpio
        )
        
        morena_mr = resultado['mr'].get('MORENA', 0)
        morena_rp = resultado['rp'].get('MORENA', 0)
        morena_tot = resultado['tot'].get('MORENA', 0)
        
        morena_pct = (morena_tot / config['total']) * 100
        sobrerrepresentacion = morena_pct - (morena_vote_share * 100)
        
        limite_esperado = int((morena_vote_share + 0.08) * config['total'])
        
        print(f"\nRESULTADOS MORENA:")
        print(f"  MR solicitado: {config['mr']}")
        print(f"  MR obtenido:   {morena_mr}")
        print(f"  RP solicitado: {config['rp']}")
        print(f"  RP obtenido:   {morena_rp}")
        print(f"  TOTAL:         {morena_tot} ({morena_pct:.2f}%)")
        
        print(f"\nANÁLISIS DE SOBRERREPRESENTACIÓN:")
        print(f"  Vote share:          {morena_vote_share*100:.2f}%")
        print(f"  Seat share:          {morena_pct:.2f}%")
        print(f"  Sobrerrepresentación: {sobrerrepresentacion:+.2f} pp")
        print(f"  Límite constitucional (+8pp): {(morena_vote_share + 0.08)*100:.2f}% = {limite_esperado} escaños")
        
        if morena_tot > limite_esperado:
            print(f"  ⚠️  MORENA EXCEDE el límite por {morena_tot - limite_esperado} escaños")
        elif morena_tot < limite_esperado:
            print(f"  ✓ MORENA está DENTRO del límite por {limite_esperado - morena_tot} escaños de margen")
        else:
            print(f"  ✓ MORENA está EXACTAMENTE en el límite")

if __name__ == "__main__":
    test_tope_8_porciento()
