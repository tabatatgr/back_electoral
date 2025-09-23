#!/usr/bin/env python3
"""
Módulo para redistribución inteligente de votos por partido
Permite simular escenarios electorales alternativos manteniendo la estructura geográfica
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

def redistribuir_votos_mixto(votos_originales: Dict[str, float], 
                           nuevos_porcentajes: Dict[str, float],
                           overrides_manuales: Optional[Dict[str, float]] = None) -> Dict[str, float]:
    """
    Redistribución mixta de votos con overrides manuales
    
    Args:
        votos_originales: {partido: % original}
        nuevos_porcentajes: {partido: % fijo deseado}
        overrides_manuales: {partido: puntos_adicionales_del_pool}
    
    Returns:
        {partido: % final} - siempre suma 100%
    
    Example:
        >>> redistribuir_votos_mixto(
        ...     {"MORENA": 50, "PAN": 25, "PRI": 15, "MC": 10},
        ...     {"MORENA": 2},  # Fijar MORENA en 2%
        ...     {"PAN": 30, "MC": 10}  # Dar +30 a PAN, +10 a MC del pool
        ... )
        {"MORENA": 2.0, "PAN": 55.0, "PRI": 23.0, "MC": 20.0}
    """
    if overrides_manuales is None:
        overrides_manuales = {}
    
    # PASO 1: Inicializar con valores originales
    resultado = votos_originales.copy()
    
    # PASO 2: Aplicar valores fijos y calcular pool liberado
    pool_liberado = 0
    for partido, valor_fijo in nuevos_porcentajes.items():
        if partido in resultado:
            pool_liberado += resultado[partido] - valor_fijo
            resultado[partido] = valor_fijo
    
    # PASO 3: Aplicar overrides del pool
    pool_usado_overrides = 0
    for partido, override in overrides_manuales.items():
        if partido in resultado:
            resultado[partido] += override
            pool_usado_overrides += override
    
    # PASO 4: Calcular pool restante
    pool_restante = pool_liberado - pool_usado_overrides
    
    # PASO 5: Distribuir pool restante proporcionalmente
    partidos_elegibles = [
        p for p in votos_originales.keys() 
        if p not in nuevos_porcentajes and p not in overrides_manuales
    ]
    
    if pool_restante != 0 and partidos_elegibles:
        # Peso basado en valores ORIGINALES de partidos elegibles
        peso_total = sum(votos_originales[p] for p in partidos_elegibles)
        
        if peso_total > 0:
            for partido in partidos_elegibles:
                proporcion = votos_originales[partido] / peso_total
                ajuste = pool_restante * proporcion
                resultado[partido] += ajuste
        else:
            # Distribución igualitaria si no hay peso
            distribucion_igual = pool_restante / len(partidos_elegibles)
            for partido in partidos_elegibles:
                resultado[partido] += distribucion_igual
    
    # PASO 6: Redondear y ajustar para suma exacta de 100%
    resultado_redondeado = {p: round(v, 2) for p, v in resultado.items()}
    diferencia = 100.0 - sum(resultado_redondeado.values())
    
    if abs(diferencia) > 0.01:
        # Ajustar en el partido con mayor porcentaje
        partido_mayor = max(resultado_redondeado.keys(), key=lambda x: resultado_redondeado[x])
        resultado_redondeado[partido_mayor] += round(diferencia, 2)
    
    return resultado_redondeado
    
    return resultado_redondeado


def aplicar_redistribucion_geografica(df_votos: pd.DataFrame, 
                                     porcentajes_objetivo: Dict[str, float],
                                     columna_partido: str = 'PARTIDO',
                                     columna_votos: str = 'VOTOS_CALCULADOS',
                                     mantener_estructura: bool = True) -> pd.DataFrame:
    """
    Aplica redistribución de votos manteniendo estructura geográfica
    
    Args:
        df_votos: DataFrame con votos por distrito/casilla
        porcentajes_objetivo: {partido: % objetivo}
        columna_partido: nombre de columna con partidos
        columna_votos: nombre de columna con votos
        mantener_estructura: si mantener distribución geográfica relativa
    
    Returns:
        DataFrame con votos redistribuidos
    """
    df_resultado = df_votos.copy()
    
    # Calcular totales actuales por partido
    totales_actuales = df_votos.groupby(columna_partido)[columna_votos].sum()
    total_general = totales_actuales.sum()
    
    # Calcular porcentajes actuales
    porcentajes_actuales = (totales_actuales / total_general * 100).to_dict()
    
    print(f"[DEBUG] Redistribución geográfica:")
    print(f"[DEBUG] Porcentajes actuales: {porcentajes_actuales}")
    print(f"[DEBUG] Porcentajes objetivo: {porcentajes_objetivo}")
    
    # Calcular factores de ajuste por partido
    factores_ajuste = {}
    for partido in totales_actuales.index:
        if partido in porcentajes_objetivo:
            objetivo_abs = (porcentajes_objetivo[partido] / 100) * total_general
            actual_abs = totales_actuales[partido]
            factores_ajuste[partido] = objetivo_abs / actual_abs if actual_abs > 0 else 0
        else:
            factores_ajuste[partido] = 1.0  # Mantener sin cambios
    
    print(f"[DEBUG] Factores de ajuste: {factores_ajuste}")
    
    # Aplicar factores de ajuste
    if mantener_estructura:
        # Mantener distribución geográfica relativa
        for partido, factor in factores_ajuste.items():
            mask = df_resultado[columna_partido] == partido
            df_resultado.loc[mask, columna_votos] *= factor
    else:
        # Redistribución uniforme (menos realista)
        for partido in porcentajes_objetivo:
            objetivo_abs = (porcentajes_objetivo[partido] / 100) * total_general
            mask = df_resultado[columna_partido] == partido
            registros_partido = mask.sum()
            if registros_partido > 0:
                votos_por_registro = objetivo_abs / registros_partido
                df_resultado.loc[mask, columna_votos] = votos_por_registro
    
    # Verificar resultado
    totales_finales = df_resultado.groupby(columna_partido)[columna_votos].sum()
    porcentajes_finales = (totales_finales / totales_finales.sum() * 100).to_dict()
    
    print(f"[DEBUG] Porcentajes finales: {porcentajes_finales}")
    
    return df_resultado


def extraer_porcentajes_actuales(df_votos: pd.DataFrame,
                                columna_partido: str = 'PARTIDO',
                                columna_votos: str = 'VOTOS_CALCULADOS') -> Dict[str, float]:
    """
    Extrae porcentajes actuales de votos por partido
    
    Returns:
        {partido: % actual}
    """
    totales = df_votos.groupby(columna_partido)[columna_votos].sum()
    total_general = totales.sum()
    
    porcentajes = {}
    for partido, votos in totales.items():
        porcentajes[partido] = round((votos / total_general) * 100, 2)
    
    return porcentajes


def simular_escenario_electoral(path_parquet: str,
                              porcentajes_objetivo: Dict[str, float],
                              partidos_fijos: Optional[Dict[str, float]] = None,
                              overrides_pool: Optional[Dict[str, float]] = None,
                              mantener_geografia: bool = True) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """
    Simula un escenario electoral completo con redistribución de votos
    
    Args:
        path_parquet: ruta al archivo de datos electorales
        porcentajes_objetivo: porcentajes objetivo finales {partido: %}
        partidos_fijos: partidos con % fijo {partido: %}
        overrides_pool: overrides manuales del pool {partido: puntos}
        mantener_geografia: si mantener distribución geográfica
    
    Returns:
        (DataFrame redistribuido, porcentajes finales)
    """
    # Cargar datos
    df = pd.read_parquet(path_parquet)
    # Normalizar formato de input: la función espera un DataFrame en formato "largo"
    # con columnas 'PARTIDO' y 'VOTOS_CALCULADOS'. Algunos parquets (como los
    # de computos_*.parquet) vienen en formato "ancho" donde cada partido es
    # una columna. Detectamos ese caso y convertimos automáticamente a formato
    # largo para mantener compatibilidad.
    try:
        if 'PARTIDO' not in df.columns or 'VOTOS_CALCULADOS' not in df.columns:
            # Detectar columnas de id/estructura (si existen)
            id_cols = [c for c in ['ENTIDAD', 'DISTRITO', 'TOTAL_BOLETAS', 'CI'] if c in df.columns]
            # Las columnas restantes se consideran partidos (valores numéricos)
            party_cols = [c for c in df.columns if c not in id_cols]
            # Evitar convertir si ya parece estar en largo (por ejemplo, tiene PARTIDO)
            if party_cols:
                df = df.melt(id_vars=id_cols, value_vars=party_cols, var_name='PARTIDO', value_name='VOTOS_CALCULADOS')
                # Convertir tipos y rellenar nulos en votos
                df['VOTOS_CALCULADOS'] = df['VOTOS_CALCULADOS'].fillna(0)
                print(f"[DEBUG] Converted wide-format parquet to long-format: id_cols={id_cols}, parties={len(party_cols)}")
    except Exception as _e:
        print(f"[WARN] No se pudo normalizar formato de parquet a largo: {_e}")
    
    # Extraer porcentajes actuales
    porcentajes_actuales = extraer_porcentajes_actuales(df)
    
    print(f"[DEBUG] Iniciando simulación electoral:")
    print(f"[DEBUG] Partidos encontrados: {list(porcentajes_actuales.keys())}")
    print(f"[DEBUG] Porcentajes actuales: {porcentajes_actuales}")
    
    # Si no se proporcionan porcentajes objetivo, usar redistribución mixta
    if not porcentajes_objetivo:
        if partidos_fijos or overrides_pool:
            porcentajes_objetivo = redistribuir_votos_mixto(
                porcentajes_actuales, 
                partidos_fijos or {}, 
                overrides_pool or {}
            )
        else:
            porcentajes_objetivo = porcentajes_actuales
    
    print(f"[DEBUG] Porcentajes objetivo calculados: {porcentajes_objetivo}")
    
    # Aplicar redistribución geográfica
    df_redistribuido = aplicar_redistribucion_geografica(
        df, 
        porcentajes_objetivo,
        mantener_estructura=mantener_geografia
    )
    
    # Calcular porcentajes finales
    porcentajes_finales = extraer_porcentajes_actuales(df_redistribuido)
    
    return df_redistribuido, porcentajes_finales


def test_redistribucion():
    """Test básico del sistema de redistribución"""
    print("🧪 TEST SISTEMA DE REDISTRIBUCIÓN")
    print("=" * 50)
    
    # Test 1: Redistribución básica
    print("\n📊 Test 1: Redistribución mixta básica")
    votos_orig = {"MORENA": 50, "PAN": 25, "PRI": 15, "MC": 10}
    resultado = redistribuir_votos_mixto(
        votos_orig,
        {"MORENA": 2},  # Fijar MORENA en 2%
        {"PAN": 30, "MC": 10}  # +30 a PAN, +10 a MC del pool
    )
    
    print(f"Original: {votos_orig}")
    print(f"Resultado: {resultado}")
    print(f"Suma: {sum(resultado.values())}")
    
    # Test 2: Solo sliders
    print("\n📊 Test 2: Solo valores fijos")
    resultado2 = redistribuir_votos_mixto(
        votos_orig,
        {"MORENA": 30, "PAN": 40}  # Fijar dos partidos
    )
    
    print(f"Original: {votos_orig}")
    print(f"Resultado: {resultado2}")
    print(f"Suma: {sum(resultado2.values())}")
    
    # Test 3: Solo pool
    print("\n📊 Test 3: Solo redistribución de pool")
    resultado3 = redistribuir_votos_mixto(
        votos_orig,
        {},  # No fijar nada
        {"PAN": 20, "PRI": -5}  # +20 a PAN, -5 a PRI del pool
    )
    
    print(f"Original: {votos_orig}")
    print(f"Resultado: {resultado3}")
    print(f"Suma: {sum(resultado3.values())}")


if __name__ == "__main__":
    test_redistribucion()
