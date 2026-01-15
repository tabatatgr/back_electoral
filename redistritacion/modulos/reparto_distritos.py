"""
MÓDULO A: Reparto de distritos por entidad federativa

Implementa el algoritmo del INE para distribuir N_MR distritos entre 32 estados,
respetando el piso constitucional de 2 distritos por estado.

Método: Hare con piso constitucional (igual que el INE)
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple


def calcular_cuota_hare(poblacion_total: int, n_distritos: int) -> float:
    """
    Calcula la cuota Hare para reparto de distritos.
    
    Args:
        poblacion_total: Población total del país
        n_distritos: Número total de distritos a repartir
    
    Returns:
        Cuota Hare (población por distrito)
    """
    return poblacion_total / n_distritos


def aplicar_piso_constitucional(
    estados: List[str],
    piso: int = 2
) -> Dict[str, int]:
    """
    Asigna el piso constitucional de distritos a cada estado.
    
    Args:
        estados: Lista de nombres de estados
        piso: Número mínimo de distritos por estado (default 2)
    
    Returns:
        Dict {estado: distritos_piso}
    """
    return {estado: piso for estado in estados}


def repartir_distritos_hare(
    poblacion_estados: Dict[str, int],
    n_distritos: int,
    piso_constitucional: int = 2
) -> Dict[str, int]:
    """
    Reparte distritos MR entre estados usando el método Hare con piso constitucional.
    
    Este es el método oficial del INE para distritación federal.
    
    Algoritmo:
    1. Asignar piso constitucional (2 distritos) a cada estado
    2. Calcular cuota Hare con población y distritos restantes
    3. Asignar parte entera (cocientes)
    4. Distribuir residuos por restos mayores
    
    Args:
        poblacion_estados: Dict {estado: poblacion}
        n_distritos: Número total de distritos a repartir
        piso_constitucional: Mínimo de distritos por estado (default 2)
    
    Returns:
        Dict {estado: distritos_asignados}
    
    Raises:
        ValueError: Si n_distritos < (32 estados × piso_constitucional)
    """
    n_estados = len(poblacion_estados)
    
    # Validar que hay suficientes distritos para el piso
    minimo_distritos = n_estados * piso_constitucional
    if n_distritos < minimo_distritos:
        raise ValueError(
            f"n_distritos={n_distritos} es menor que el mínimo constitucional "
            f"({n_estados} estados × {piso_constitucional} = {minimo_distritos})"
        )
    
    # PASO 1: Asignar piso constitucional
    distritos = {estado: piso_constitucional for estado in poblacion_estados.keys()}
    distritos_asignados = n_estados * piso_constitucional
    distritos_restantes = n_distritos - distritos_asignados
    
    if distritos_restantes == 0:
        # Si ya se agotaron los distritos, retornar
        return distritos
    
    # PASO 2: Calcular cuota Hare con población total
    poblacion_total = sum(poblacion_estados.values())
    cuota = poblacion_total / distritos_restantes
    
    # PASO 3: Calcular cocientes y residuos
    cocientes = {}
    residuos = {}
    
    for estado, poblacion in poblacion_estados.items():
        cociente_exacto = poblacion / cuota
        cociente_entero = int(np.floor(cociente_exacto))
        residuo = cociente_exacto - cociente_entero
        
        cocientes[estado] = cociente_entero
        residuos[estado] = residuo
    
    # PASO 4: Asignar parte entera (cocientes)
    for estado, cociente in cocientes.items():
        distritos[estado] += cociente
        distritos_asignados += cociente
    
    # PASO 5: Distribuir residuos (restos mayores)
    distritos_faltantes = n_distritos - distritos_asignados
    
    if distritos_faltantes > 0:
        # Ordenar estados por residuo descendente
        estados_ordenados = sorted(
            residuos.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Asignar un distrito extra a los primeros N estados
        for i in range(distritos_faltantes):
            estado = estados_ordenados[i][0]
            distritos[estado] += 1
    
    return distritos


def generar_reporte_reparto(
    poblacion_estados: Dict[str, int],
    distritos_estados: Dict[str, int],
    n_distritos: int
) -> pd.DataFrame:
    """
    Genera un DataFrame con el reporte detallado del reparto.
    
    Args:
        poblacion_estados: Dict {estado: poblacion}
        distritos_estados: Dict {estado: distritos}
        n_distritos: Número total de distritos
    
    Returns:
        DataFrame con columnas:
        - estado
        - poblacion
        - distritos
        - pct_poblacion
        - pct_distritos
        - desviacion (diferencia en puntos porcentuales)
        - poblacion_por_distrito
    """
    poblacion_total = sum(poblacion_estados.values())
    
    datos = []
    for estado in poblacion_estados.keys():
        poblacion = poblacion_estados[estado]
        distritos = distritos_estados[estado]
        
        pct_poblacion = (poblacion / poblacion_total) * 100
        pct_distritos = (distritos / n_distritos) * 100
        desviacion = pct_distritos - pct_poblacion
        poblacion_por_distrito = poblacion / distritos if distritos > 0 else 0
        
        datos.append({
            'estado': estado,
            'poblacion': poblacion,
            'distritos': distritos,
            'pct_poblacion': round(pct_poblacion, 2),
            'pct_distritos': round(pct_distritos, 2),
            'desviacion_pp': round(desviacion, 2),
            'poblacion_por_distrito': int(poblacion_por_distrito)
        })
    
    df = pd.DataFrame(datos)
    
    # Ordenar por población descendente
    df = df.sort_values('poblacion', ascending=False).reset_index(drop=True)
    
    return df


def asignar_votos_por_poblacion_hare(
    votos_totales: int,
    poblacion_por_estado: Dict[str, int],
    eficiencia_geografica: float = 1.0
) -> Dict[str, int]:
    """
    Asigna votos de un partido por estado usando método Hare con eficiencia geográfica.
    
    Similar al reparto de distritos, pero para distribuir votos del partido
    proporcionalmente a la población de cada estado, ajustado por eficiencia.
    
    Args:
        votos_totales: Total de votos del partido a nivel nacional
        poblacion_por_estado: Dict {estado: poblacion}
        eficiencia_geografica: Factor de ajuste (default 1.0)
            - 1.0 = distribución puramente proporcional
            - >1.0 = bonificación por dispersión geográfica
            - <1.0 = penalización
    
    Returns:
        Dict {estado: votos_asignados}
    
    Ejemplo:
        >>> votos = asignar_votos_por_poblacion_hare(
        ...     votos_totales=50_000_000,
        ...     poblacion_por_estado={'MEXICO': 16_992_418, 'CDMX': 9_209_944},
        ...     eficiencia_geografica=1.1
        ... )
    """
    # PASO 1: Ajustar población por eficiencia geográfica
    poblacion_ajustada_dict = {
        estado: poblacion * eficiencia_geografica
        for estado, poblacion in poblacion_por_estado.items()
    }
    poblacion_total_ajustada = sum(poblacion_ajustada_dict.values())
    
    # Calcular cuota con la población ajustada total
    cuota = poblacion_total_ajustada / votos_totales
    
    # PASO 2: Calcular cocientes y residuos
    cocientes = {}
    residuos = {}
    votos_asignados = {}
    
    for estado, poblacion_ajustada in poblacion_ajustada_dict.items():
        cociente_exacto = poblacion_ajustada / cuota
        cociente_entero = int(np.floor(cociente_exacto))
        residuo = cociente_exacto - cociente_entero
        
        cocientes[estado] = cociente_entero
        residuos[estado] = residuo
        votos_asignados[estado] = cociente_entero
    
    # PASO 3: Contar votos ya asignados
    votos_ya_asignados = sum(votos_asignados.values())
    votos_faltantes = votos_totales - votos_ya_asignados
    
    # PASO 4: Distribuir votos faltantes por restos mayores
    if votos_faltantes > 0:
        estados_ordenados = sorted(
            residuos.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for i in range(min(votos_faltantes, len(estados_ordenados))):
            estado = estados_ordenados[i][0]
            votos_asignados[estado] += 1
    
    # PASO 5: Ajuste final para garantizar exactitud (por si acaso)
    votos_ya_asignados = sum(votos_asignados.values())
    if votos_ya_asignados != votos_totales:
        diferencia = votos_totales - votos_ya_asignados
        if diferencia > 0:
            # Faltan votos: asignar a estados con mayor población
            estados_grandes = sorted(
                poblacion_por_estado.items(),
                key=lambda x: x[1],
                reverse=True
            )
            for i in range(diferencia):
                estado = estados_grandes[i % len(estados_grandes)][0]
                votos_asignados[estado] += 1
        else:
            # Sobran votos: quitar de estados con menor población
            estados_pequenos = sorted(
                poblacion_por_estado.items(),
                key=lambda x: x[1],
                reverse=False
            )
            for i in range(abs(diferencia)):
                estado = estados_pequenos[i % len(estados_pequenos)][0]
                if votos_asignados[estado] > 0:
                    votos_asignados[estado] -= 1
    
    return votos_asignados


# ==============================================================================
# EJEMPLO DE USO
# ==============================================================================

if __name__ == '__main__':
    # Población por estado (Censo 2020 - simplificado para ejemplo)
    poblacion_ejemplo = {
        'MEXICO': 16992418,
        'CDMX': 9209944,
        'JALISCO': 8348151,
        'VERACRUZ': 8062579,
        'PUEBLA': 6583278,
        'GUANAJUATO': 6166884,
        'CHIAPAS': 5543828,
        'NUEVO LEON': 5784442,
        'MICHOACAN': 4748846,
        'OAXACA': 4132148,
        'CHIHUAHUA': 3741869,
        'GUERRERO': 3540685,
        'TAMAULIPAS': 3527735,
        'BAJA CALIFORNIA': 3769020,
        'SINALOA': 3026943,
        'COAHUILA': 3146771,
        'HIDALGO': 3082841,
        'SONORA': 2944840,
        'SAN LUIS POTOSI': 2822255,
        'TABASCO': 2402598,
        'YUCATAN': 2320898,
        'QUERETARO': 2368467,
        'MORELOS': 1971520,
        'DURANGO': 1832650,
        'ZACATECAS': 1622138,
        'QUINTANA ROO': 1857985,
        'AGUASCALIENTES': 1425607,
        'TLAXCALA': 1342977,
        'NAYARIT': 1235456,
        'CAMPECHE': 928363,
        'BAJA CALIFORNIA SUR': 798447,
        'COLIMA': 731391,
    }
    
    print("="*80)
    print("MÓDULO A: REPARTO DE DISTRITOS POR ENTIDAD")
    print("="*80)
    
    # Probar con diferentes valores de N_MR
    for n_mr in [200, 300, 400]:
        print(f"\n{'='*80}")
        print(f"ESCENARIO: {n_mr} DISTRITOS MR")
        print(f"{'='*80}")
        
        distritos = repartir_distritos_hare(
            poblacion_estados=poblacion_ejemplo,
            n_distritos=n_mr,
            piso_constitucional=2
        )
        
        reporte = generar_reporte_reparto(
            poblacion_estados=poblacion_ejemplo,
            distritos_estados=distritos,
            n_distritos=n_mr
        )
        
        print(f"\nTotal distritos: {reporte['distritos'].sum()}")
        print(f"Mínimo por estado: {reporte['distritos'].min()}")
        print(f"Máximo por estado: {reporte['distritos'].max()}")
        
        print("\nTop 10 estados:")
        print(reporte.head(10).to_string(index=False))
        
        print("\nEstados con mínimo:")
        min_estados = reporte[reporte['distritos'] == reporte['distritos'].min()]
        print(min_estados[['estado', 'poblacion', 'distritos']].to_string(index=False))

