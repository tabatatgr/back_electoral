"""
Módulo para calcular la eficiencia geográfica REAL de cada partido
basada en datos históricos de elecciones.

La eficiencia mide qué tan bien un partido convierte sus votos en victorias distritales.
"""

import pandas as pd
import os
from typing import Dict


def calcular_eficiencia_partidos(anio: int, usar_coaliciones: bool = False) -> Dict[str, float]:
    """
    Calcula la eficiencia real de cada partido en una elección histórica.
    
    Eficiencia = (% de distritos ganados) / (% de votos nacionales)
    
    - Eficiencia = 1.0: Proporcional exacto
    - Eficiencia > 1.0: El partido gana más distritos de lo proporcional (votos bien distribuidos)
    - Eficiencia < 1.0: El partido gana menos distritos de lo proporcional (votos mal distribuidos)
    
    Args:
        anio: Año de la elección (2018, 2021, 2024)
        usar_coaliciones: Si True, considera coaliciones; si False, solo partidos individuales
    
    Returns:
        Dict con eficiencia por partido: {'MORENA': 1.15, 'PAN': 0.95, ...}
    """
    
    # Cargar datos de votos
    path_votos = f"data/computos_diputados_{anio}.parquet"
    if not os.path.exists(path_votos):
        print(f"[WARN] No existe archivo {path_votos}, usando eficiencia 1.0 para todos")
        return {}
    
    df_votos = pd.read_parquet(path_votos)
    
    # Normalizar nombres de columnas
    df_votos.columns = [str(c).strip().upper() for c in df_votos.columns]
    
    # Cargar siglado para saber quién ganó cada distrito
    path_siglado = f"data/siglado-diputados-{anio}.csv"
    if not os.path.exists(path_siglado):
        print(f"[WARN] No existe archivo {path_siglado}, usando eficiencia 1.0 para todos")
        return {}
    
    df_siglado = pd.read_csv(path_siglado, dtype=str, keep_default_na=False)
    df_siglado.columns = [str(c).strip().lower() for c in df_siglado.columns]
    
    # Identificar columna de partido ganador
    # Puede ser: 'grupo_parlamentario', 'partido_origen', 'partido', 'postulador'
    columna_partido = None
    for opcion in ['grupo_parlamentario', 'partido_origen', 'partido', 'postulador']:
        if opcion in df_siglado.columns:
            columna_partido = opcion
            break
    
    if not columna_partido:
        print(f"[WARN] No se encontró columna de partido en siglado, usando eficiencia 1.0")
        return {}
    
    # Normalizar nombres de partidos en siglado
    df_siglado['partido_norm'] = df_siglado[columna_partido].str.strip().str.upper()
    
    # Contar distritos ganados por cada partido
    distritos_ganados = df_siglado['partido_norm'].value_counts().to_dict()
    total_distritos = len(df_siglado)
    
    print(f"\n[DEBUG] Eficiencias año {anio}:")
    print(f"Total distritos: {total_distritos}")
    
    # Calcular votos totales por partido
    columnas_excluir = ['ENTIDAD', 'DISTRITO', 'TOTAL_BOLETAS', 'CI', 'ENTIDAD_NOMBRE']
    partidos = [col for col in df_votos.columns if col not in columnas_excluir and not col.startswith('COAL')]
    
    eficiencias = {}
    total_votos_validos = df_votos['TOTAL_BOLETAS'].sum() if 'TOTAL_BOLETAS' in df_votos.columns else df_votos[partidos].sum().sum()
    
    for partido in partidos:
        if partido not in df_votos.columns:
            continue
        
        # Votos nacionales del partido
        votos_partido = df_votos[partido].sum()
        pct_votos = (votos_partido / total_votos_validos * 100) if total_votos_validos > 0 else 0
        
        # Distritos ganados
        distritos_partido = distritos_ganados.get(partido, 0)
        pct_distritos = (distritos_partido / total_distritos * 100) if total_distritos > 0 else 0
        
        # Calcular eficiencia
        if pct_votos > 0:
            eficiencia = pct_distritos / pct_votos
        else:
            eficiencia = 0.0
        
        # Solo guardar si el partido tiene votos significativos (>1%)
        if pct_votos >= 1.0:
            eficiencias[partido] = eficiencia
            print(f"  {partido:12s}: {pct_votos:5.2f}% votos → {pct_distritos:5.2f}% distritos → eficiencia {eficiencia:.3f}")
    
    # Si usar_coaliciones, calcular eficiencia para coaliciones
    if usar_coaliciones:
        # Identificar coaliciones del año
        coaliciones_por_anio = {
            2018: {'JUNTOS_HAREMOS_HISTORIA': ['MORENA', 'PT', 'PES']},
            2021: {'JUNTOS_HACEMOS_HISTORIA': ['MORENA', 'PT', 'PVEM']},
            2024: {'SIGAMOS_HACIENDO_HISTORIA': ['MORENA', 'PT', 'PVEM']}
        }
        
        coaliciones = coaliciones_por_anio.get(anio, {})
        
        for coal_nombre, miembros in coaliciones.items():
            # Sumar votos de miembros
            votos_coal = sum(df_votos[m].sum() for m in miembros if m in df_votos.columns)
            pct_votos_coal = (votos_coal / total_votos_validos * 100) if total_votos_validos > 0 else 0
            
            # Sumar distritos ganados por miembros
            distritos_coal = sum(distritos_ganados.get(m, 0) for m in miembros)
            pct_distritos_coal = (distritos_coal / total_distritos * 100) if total_distritos > 0 else 0
            
            # Calcular eficiencia
            if pct_votos_coal > 0:
                eficiencia_coal = pct_distritos_coal / pct_votos_coal
                eficiencias[coal_nombre] = eficiencia_coal
                print(f"  {coal_nombre}: {pct_votos_coal:5.2f}% votos → {pct_distritos_coal:5.2f}% distritos → eficiencia {eficiencia_coal:.3f}")
    
    return eficiencias


def obtener_eficiencia_partido(partido: str, anio: int, eficiencias_calculadas: Dict[str, float]) -> float:
    """
    Obtiene la eficiencia de un partido específico.
    Si no existe, devuelve 1.0 (proporcional).
    
    Args:
        partido: Nombre del partido
        anio: Año de la elección
        eficiencias_calculadas: Dict de eficiencias ya calculadas
    
    Returns:
        Factor de eficiencia (típicamente entre 0.5 y 1.5)
    """
    
    if partido in eficiencias_calculadas:
        return eficiencias_calculadas[partido]
    
    # Si no existe, usar 1.0 (proporcional)
    return 1.0


if __name__ == "__main__":
    """Prueba del módulo"""
    
    for anio in [2018, 2021, 2024]:
        print(f"\n{'='*60}")
        print(f"EFICIENCIAS {anio}")
        print(f"{'='*60}")
        
        eficiencias = calcular_eficiencia_partidos(anio, usar_coaliciones=False)
        
        # Mostrar estadísticas
        if eficiencias:
            eficiencias_valores = list(eficiencias.values())
            print(f"\nEstadísticas:")
            print(f"  Promedio: {sum(eficiencias_valores) / len(eficiencias_valores):.3f}")
            print(f"  Máxima: {max(eficiencias_valores):.3f} ({max(eficiencias, key=eficiencias.get)})")
            print(f"  Mínima: {min(eficiencias_valores):.3f} ({min(eficiencias, key=eficiencias.get)})")
