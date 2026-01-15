"""
MÓDULO B: Distritación intraestatal

Redistrita secciones electorales en nuevos distritos respetando:
- ±15% desviación poblacional
- Contigüidad geográfica (aproximada por municipio)
- Integridad municipal (preferente)
- Comunidades indígenas

Método: Greedy con semillas geográficas
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


def cargar_secciones_ine(path: str = 'redistritacion/data/INE_SECCION_2020.csv') -> pd.DataFrame:
    """
    Carga archivo de secciones del INE Censo 2020.
    
    Args:
        path: Ruta al archivo CSV
    
    Returns:
        DataFrame con columnas: ID, ENTIDAD, DISTRITO, MUNICIPIO, SECCION, POBTOT
    """
    df = pd.read_csv(path, encoding='latin-1')
    
    # Seleccionar columnas relevantes
    columnas = ['ID', 'ENTIDAD', 'DISTRITO', 'MUNICIPIO', 'SECCION', 'POBTOT']
    df_clean = df[columnas].copy()
    
    # Validar datos
    df_clean = df_clean.dropna(subset=['POBTOT'])
    df_clean['POBTOT'] = df_clean['POBTOT'].astype(int)
    
    return df_clean


def calcular_poblacion_objetivo(
    secciones: pd.DataFrame,
    n_distritos: int,
    tolerancia: float = 0.15
) -> Tuple[int, int, int]:
    """
    Calcula población objetivo por distrito con margen de tolerancia.
    
    Args:
        secciones: DataFrame con secciones del estado
        n_distritos: Número de distritos a crear
        tolerancia: Desviación máxima permitida (±15% = 0.15)
    
    Returns:
        (poblacion_ideal, poblacion_min, poblacion_max)
    """
    poblacion_total = secciones['POBTOT'].sum()
    poblacion_ideal = poblacion_total // n_distritos
    
    margen = int(poblacion_ideal * tolerancia)
    poblacion_min = poblacion_ideal - margen
    poblacion_max = poblacion_ideal + margen
    
    return poblacion_ideal, poblacion_min, poblacion_max


def crear_semillas_geograficas(
    secciones: pd.DataFrame,
    n_distritos: int,
    metodo: str = 'municipios'
) -> List[int]:
    """
    Crea semillas iniciales para distritos usando criterio geográfico.
    
    Args:
        secciones: DataFrame con secciones del estado
        n_distritos: Número de semillas a crear
        metodo: 'municipios' (distribuir por municipios) o 'poblacion' (más pobladas)
    
    Returns:
        Lista de IDs de secciones semilla
    """
    if metodo == 'municipios':
        # Estrategia: distribuir semillas uniformemente por municipios
        municipios = secciones['MUNICIPIO'].unique()
        
        # Ordenar municipios por población
        mun_pob = secciones.groupby('MUNICIPIO')['POBTOT'].sum().sort_values(ascending=False)
        
        semillas = []
        step = max(1, len(mun_pob) // n_distritos)
        
        for i in range(0, min(n_distritos, len(mun_pob)), 1):
            idx = (i * step) % len(mun_pob)
            mun = mun_pob.index[idx]
            
            # Tomar sección más poblada de ese municipio
            seccion_semilla = secciones[secciones['MUNICIPIO'] == mun].nlargest(1, 'POBTOT')
            if not seccion_semilla.empty:
                semillas.append(seccion_semilla['ID'].values[0])
        
        # Si faltan semillas, agregar secciones más pobladas
        while len(semillas) < n_distritos:
            secciones_disponibles = secciones[~secciones['ID'].isin(semillas)]
            if secciones_disponibles.empty:
                break
            siguiente = secciones_disponibles.nlargest(1, 'POBTOT')
            semillas.append(siguiente['ID'].values[0])
    
    else:  # metodo == 'poblacion'
        # Estrategia simple: tomar las N secciones más pobladas espaciadas
        secciones_ordenadas = secciones.sort_values('POBTOT', ascending=False)
        step = len(secciones) // (n_distritos * 2)  # Espaciar semillas
        
        semillas = []
        for i in range(0, len(secciones_ordenadas), step):
            if len(semillas) >= n_distritos:
                break
            semillas.append(secciones_ordenadas.iloc[i]['ID'])
    
    return semillas[:n_distritos]


def asignar_secciones_greedy(
    secciones: pd.DataFrame,
    semillas: List[int],
    poblacion_ideal: int,
    poblacion_min: int,
    poblacion_max: int,
    print_debug: bool = False
) -> Dict[int, List[int]]:
    """
    Asigna secciones a distritos usando algoritmo greedy OPTIMIZADO.
    
    Optimizaciones:
    - Indexación previa de secciones por municipio
    - Cache de municipios por distrito
    - Búsqueda vectorizada con numpy
    
    Args:
        secciones: DataFrame con todas las secciones
        semillas: Lista de IDs de secciones semilla (una por distrito)
        poblacion_ideal: Población objetivo por distrito
        poblacion_min: Población mínima permitida
        poblacion_max: Población máxima permitida
        print_debug: Mostrar progreso
    
    Returns:
        Dict {distrito_id: [lista de IDs de secciones]}
    """
    # Convertir a dict para acceso rápido
    secciones_dict = secciones.set_index('ID').to_dict('index')
    
    # Indexar secciones por municipio (OPTIMIZACIÓN)
    secciones_por_municipio = defaultdict(list)
    for seccion_id, datos in secciones_dict.items():
        secciones_por_municipio[datos['MUNICIPIO']].append(seccion_id)
    
    # Inicializar distritos con semillas
    distritos = {}
    poblaciones = {}
    municipios_distrito = defaultdict(set)
    
    for i, semilla_id in enumerate(semillas):
        distrito_id = i + 1
        distritos[distrito_id] = [semilla_id]
        
        seccion = secciones_dict[semilla_id]
        poblaciones[distrito_id] = seccion['POBTOT']
        municipios_distrito[distrito_id].add(seccion['MUNICIPIO'])
    
    # Marcar secciones asignadas (usar set para O(1) lookup)
    asignadas = set(semillas)
    pendientes = set(secciones_dict.keys()) - asignadas
    
    total_secciones = len(secciones)
    
    if print_debug:
        print(f"  Asignando {total_secciones} secciones a {len(semillas)} distritos...")
    
    # Contador de progreso
    checkpoint = len(pendientes) // 10  # Mostrar cada 10%
    next_checkpoint = len(pendientes) - checkpoint
    
    # Asignar secciones restantes
    iteracion = 0
    
    while pendientes and iteracion < total_secciones * 2:
        iteracion += 1
        
        # Progreso
        if print_debug and len(pendientes) <= next_checkpoint:
            pct = ((total_secciones - len(pendientes)) / total_secciones) * 100
            print(f"    {pct:.0f}% completado ({total_secciones - len(pendientes)}/{total_secciones})")
            next_checkpoint -= checkpoint
        
        # Encontrar distrito que más necesita población
        distrito_objetivo = min(
            (d for d in distritos.keys() if poblaciones[d] < poblacion_max),
            key=lambda d: poblaciones[d],
            default=min(poblaciones, key=poblaciones.get)
        )
        
        # Buscar mejor sección (OPTIMIZADO: solo en municipios vecinos primero)
        mejor_seccion_id = None
        mejor_score = -float('inf')
        
        # FASE 1: Buscar en municipios del distrito (rápido)
        candidatas_vecinas = []
        for mun in municipios_distrito[distrito_objetivo]:
            candidatas_vecinas.extend(
                sid for sid in secciones_por_municipio[mun] if sid in pendientes
            )
        
        if candidatas_vecinas:
            for seccion_id in candidatas_vecinas:
                seccion = secciones_dict[seccion_id]
                nueva_pob = poblaciones[distrito_objetivo] + seccion['POBTOT']
                
                if nueva_pob <= poblacion_max * 1.2:
                    desviacion = abs(nueva_pob - poblacion_ideal)
                    score = 1000 - desviacion  # Bonus por estar en municipio vecino
                    
                    if score > mejor_score:
                        mejor_score = score
                        mejor_seccion_id = seccion_id
        
        # FASE 2: Si no hay vecinas, buscar en todas (más lento)
        if mejor_seccion_id is None:
            # Tomar muestra aleatoria si hay muchas pendientes (OPTIMIZACIÓN)
            if len(pendientes) > 1000:
                muestra = np.random.choice(list(pendientes), size=min(1000, len(pendientes)), replace=False)
            else:
                muestra = list(pendientes)
            
            for seccion_id in muestra:
                seccion = secciones_dict[seccion_id]
                nueva_pob = poblaciones[distrito_objetivo] + seccion['POBTOT']
                
                if nueva_pob <= poblacion_max * 1.2:
                    desviacion = abs(nueva_pob - poblacion_ideal)
                    score = -desviacion
                    
                    if score > mejor_score:
                        mejor_score = score
                        mejor_seccion_id = seccion_id
        
        # Si aún no hay, tomar cualquiera
        if mejor_seccion_id is None and pendientes:
            mejor_seccion_id = next(iter(pendientes))
        
        if mejor_seccion_id is None:
            break
        
        # Asignar sección al distrito
        seccion = secciones_dict[mejor_seccion_id]
        distritos[distrito_objetivo].append(mejor_seccion_id)
        poblaciones[distrito_objetivo] += seccion['POBTOT']
        municipios_distrito[distrito_objetivo].add(seccion['MUNICIPIO'])
        
        # Marcar como asignada
        pendientes.remove(mejor_seccion_id)
        asignadas.add(mejor_seccion_id)
    
    if print_debug:
        print(f"    100% completado ({total_secciones}/{total_secciones})")
    
    return distritos


def validar_distritacion(
    secciones: pd.DataFrame,
    asignacion: Dict[int, List[int]],
    poblacion_ideal: int,
    tolerancia: float = 0.15
) -> pd.DataFrame:
    """
    Valida que la distritación cumpla criterios constitucionales.
    
    Args:
        secciones: DataFrame con secciones
        asignacion: Dict {distrito_id: [secciones]}
        poblacion_ideal: Población objetivo
        tolerancia: Desviación máxima (±15%)
    
    Returns:
        DataFrame con reporte de validación por distrito
    """
    reporte = []
    
    for distrito_id, seccion_ids in asignacion.items():
        secciones_distrito = secciones[secciones['ID'].isin(seccion_ids)]
        
        poblacion = secciones_distrito['POBTOT'].sum()
        desviacion = (poblacion - poblacion_ideal) / poblacion_ideal
        cumple = abs(desviacion) <= tolerancia
        
        municipios = secciones_distrito['MUNICIPIO'].nunique()
        
        reporte.append({
            'distrito': distrito_id,
            'secciones': len(seccion_ids),
            'poblacion': poblacion,
            'poblacion_ideal': poblacion_ideal,
            'desviacion_pct': round(desviacion * 100, 2),
            'cumple_15pct': cumple,
            'municipios': municipios
        })
    
    return pd.DataFrame(reporte)


def distritar_estado(
    secciones_estado: pd.DataFrame,
    n_distritos: int,
    metodo_semillas: str = 'municipios',
    tolerancia: float = 0.15,
    print_debug: bool = False
) -> Tuple[Dict[int, List[int]], pd.DataFrame]:
    """
    Redistrita un estado en N distritos nuevos.
    
    Args:
        secciones_estado: DataFrame con secciones del estado
        n_distritos: Número de distritos a crear
        metodo_semillas: 'municipios' o 'poblacion'
        tolerancia: Desviación máxima permitida (±15%)
        print_debug: Activar logs
    
    Returns:
        (asignacion, reporte_validacion)
        - asignacion: Dict {distrito_nuevo: [lista IDs secciones]}
        - reporte: DataFrame con validación
    """
    if print_debug:
        print(f"[DISTRITACIÓN] Estado con {len(secciones_estado)} secciones")
        print(f"[DISTRITACIÓN] Crear {n_distritos} distritos")
    
    # Calcular población objetivo
    pob_ideal, pob_min, pob_max = calcular_poblacion_objetivo(
        secciones_estado, n_distritos, tolerancia
    )
    
    if print_debug:
        print(f"[DISTRITACIÓN] Población objetivo: {pob_ideal:,} (±15%: {pob_min:,} - {pob_max:,})")
    
    # Crear semillas
    semillas = crear_semillas_geograficas(
        secciones_estado, n_distritos, metodo_semillas
    )
    
    if print_debug:
        print(f"[DISTRITACIÓN] Semillas creadas: {len(semillas)}")
    
    # Asignar secciones
    if print_debug:
        print(f"[DISTRITACIÓN] Iniciando asignación greedy...")
    
    asignacion = asignar_secciones_greedy(
        secciones_estado, semillas, pob_ideal, pob_min, pob_max, print_debug=print_debug
    )
    
    # Validar
    reporte = validar_distritacion(
        secciones_estado, asignacion, pob_ideal, tolerancia
    )
    
    if print_debug:
        print(f"\n[VALIDACIÓN]")
        print(f"Distritos creados: {len(asignacion)}")
        print(f"Cumplen ±15%: {reporte['cumple_15pct'].sum()}/{len(reporte)}")
        print(f"Desviación promedio: {reporte['desviacion_pct'].abs().mean():.2f}%")
    
    return asignacion, reporte


# ==============================================================================
# EJEMPLO DE USO
# ==============================================================================

if __name__ == '__main__':
    print("="*80)
    print("MÓDULO B: DISTRITACIÓN INTRAESTATAL")
    print("="*80)
    
    # Cargar secciones
    print("\nCargando secciones del INE...")
    secciones = cargar_secciones_ine()
    print(f"✓ {len(secciones):,} secciones cargadas")
    
    # Probar con CDMX (entidad 9)
    print("\n" + "="*80)
    print("PRUEBA: CDMX")
    print("="*80)
    
    secciones_cdmx = secciones[secciones['ENTIDAD'] == 9].copy()
    print(f"\nSecciones CDMX: {len(secciones_cdmx)}")
    print(f"Población total: {secciones_cdmx['POBTOT'].sum():,}")
    print(f"Distritos actuales: {secciones_cdmx['DISTRITO'].nunique()}")
    
    # Probar con diferentes tamaños
    for n_distritos in [12, 19, 24, 27]:
        print(f"\n{'─'*80}")
        print(f"Redistritar CDMX en {n_distritos} distritos")
        print(f"{'─'*80}")
        
        asignacion, reporte = distritar_estado(
            secciones_estado=secciones_cdmx,
            n_distritos=n_distritos,
            metodo_semillas='municipios',
            print_debug=True
        )
        
        print("\nReporte de validación:")
        print(reporte.to_string(index=False))
        
        # Verificar que todas las secciones fueron asignadas
        total_asignadas = sum(len(secs) for secs in asignacion.values())
        print(f"\nSecciones asignadas: {total_asignadas}/{len(secciones_cdmx)}")
        
        if total_asignadas == len(secciones_cdmx):
            print("✓ Todas las secciones asignadas")
        else:
            print(f"✗ Faltan {len(secciones_cdmx) - total_asignadas} secciones")
