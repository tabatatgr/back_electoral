"""
Calculador de Mayoría Forzada para SENADO - Versión Realista V2
Basado en redistribución geográfica por ESTADOS (no distritos)

Características:
- Usa datos reales de votación por ESTADO (2024)
- Aplica método Hare para redistribución por población
- Factor de eficiencia geográfica: 1.1 (10% extra)
- Respeta la estructura: 32 estados × 2 MR = 64 senadores MR
- 32 senadores PM (primera minoría por estado)
- 32 senadores RP (reparto proporcional nacional)
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional

# Población por estado (Censo 2020 - INEGI)
POBLACION_ESTADOS = {
    'AGUASCALIENTES': 1425607,
    'BAJA CALIFORNIA': 3769020,
    'BAJA CALIFORNIA SUR': 798447,
    'CAMPECHE': 928363,
    'CHIAPAS': 5543828,
    'CHIHUAHUA': 3741869,
    'CIUDAD DE MEXICO': 9209944,
    'COAHUILA': 3146771,
    'COLIMA': 731391,
    'DURANGO': 1832650,
    'GUANAJUATO': 6166934,
    'GUERRERO': 3540685,
    'HIDALGO': 3082841,
    'JALISCO': 8348151,
    'MEXICO': 16992418,
    'MICHOACAN': 4748846,
    'MORELOS': 1971520,
    'NAYARIT': 1235456,
    'NUEVO LEON': 5784442,
    'OAXACA': 4132148,
    'PUEBLA': 6583278,
    'QUERETARO': 2368467,
    'QUINTANA ROO': 1857985,
    'SAN LUIS POTOSI': 2822255,
    'SINALOA': 3026943,
    'SONORA': 2944840,
    'TABASCO': 2402598,
    'TAMAULIPAS': 3527735,
    'TLAXCALA': 1342977,
    'VERACRUZ': 8062579,
    'YUCATAN': 2320898,
    'ZACATECAS': 1622138
}


def calcular_estados_mr_realistas(
    partido: str,
    votos_objetivo: float,
    anio: int = 2024
) -> Dict:
    """
    Calcula distribución realista de estados MR usando redistribución Hare
    
    Args:
        partido: Partido objetivo (MORENA, PAN, etc.)
        votos_objetivo: Porcentaje de votos que el partido obtendrá (0.0-1.0)
        anio: Año electoral (2024, 2018)
        
    Returns:
        dict con estados_ganados, votos_necesarios, es_viable, etc.
    """
    try:
        # Intentar usar módulos de redistritacion
        import sys
        import os
        # Agregar path de redistritacion si existe
        redistritacion_path = os.path.join(os.path.dirname(__file__), '..', 'redistritacion')
        if os.path.exists(redistritacion_path) and redistritacion_path not in sys.path:
            sys.path.insert(0, redistritacion_path)
        
        from modulos.reparto_distritos import asignar_votos_por_poblacion_hare
        
        # Cargar datos reales de votación por estado
        path_parquet = f"data/computos_senado_{anio}.parquet"
        df_votos = pd.read_parquet(path_parquet)
        
        # Normalizar nombres de estados
        df_votos['ENTIDAD'] = df_votos['ENTIDAD'].str.strip().str.upper()
        
        # Calcular participación por estado
        participacion_por_estado = {}
        for estado in POBLACION_ESTADOS.keys():
            df_estado = df_votos[df_votos['ENTIDAD'] == estado]
            if not df_estado.empty:
                total_votos = df_estado['TOTAL_PARTIDOS_SUM'].iloc[0]
                participacion_por_estado[estado] = total_votos
            else:
                # Si no hay datos, usar promedio nacional
                participacion_por_estado[estado] = df_votos['TOTAL_PARTIDOS_SUM'].mean()
        
        # Total de votos nacionales
        total_votos_nacional = sum(participacion_por_estado.values())
        
        # Votos que necesita el partido a nivel nacional
        votos_partido_nacional = int(total_votos_nacional * votos_objetivo)
        
        # Usar Hare para redistribuir votos del partido por población estatal
        # con factor de eficiencia geográfica 1.1 (10% extra por dispersión)
        votos_por_estado = asignar_votos_por_poblacion_hare(
            votos_totales=votos_partido_nacional,
            poblacion_por_estado=POBLACION_ESTADOS,
            eficiencia_geografica=1.1  # 10% extra por dispersión
        )
        
        # Calcular qué estados ganaría el partido
        estados_ganados = []
        for estado, votos_partido in votos_por_estado.items():
            # El partido gana si tiene más del 35% en ese estado
            # (asumiendo competencia de ~3 partidos principales)
            votos_estado_total = participacion_por_estado[estado]
            porcentaje_estado = votos_partido / votos_estado_total if votos_estado_total > 0 else 0
            
            # Umbral realista: >35% para ganar MR en competencia tripartita
            if porcentaje_estado > 0.35:
                estados_ganados.append({
                    'estado': estado,
                    'votos_partido': votos_partido,
                    'votos_total': votos_estado_total,
                    'porcentaje': porcentaje_estado
                })
        
        # Ordenar por porcentaje
        estados_ganados = sorted(estados_ganados, key=lambda x: x['porcentaje'], reverse=True)
        
        # Cada estado da 2 MR + 1 PM = 3 senadores
        # Pero solo contamos los 2 MR para el ganador
        num_estados = len(estados_ganados)
        senadores_mr = num_estados * 2  # 2 por estado ganado
        
        return {
            'viable': True,
            'metodo': 'hare_redistribucion',
            'estados_ganados': num_estados,
            'senadores_mr': senadores_mr,
            'votos_necesarios': votos_objetivo,
            'votos_absolutos': votos_partido_nacional,
            'total_votos_nacional': total_votos_nacional,
            'distribucion_por_estado': estados_ganados[:10],  # Top 10 estados
            'eficiencia_geografica': 1.1
        }
        
    except (ImportError, FileNotFoundError) as e:
        # Si no están disponibles los módulos de redistritacion, usar método simplificado
        print(f"[INFO] Usando método simplificado: {e}")
        return calcular_estados_mr_simplificado(partido, votos_objetivo, anio)


def calcular_estados_mr_simplificado(
    partido: str,
    votos_objetivo: float,
    anio: int = 2024
) -> Dict:
    """
    Método simplificado si no están disponibles los módulos de redistritacion
    Asume distribución proporcional simple con ajuste realista
    """
    # Cargar datos reales
    path_parquet = f"data/computos_senado_{anio}.parquet"
    df_votos = pd.read_parquet(path_parquet)
    
    # Calcular votos totales
    total_votos = df_votos['TOTAL_PARTIDOS_SUM'].sum()
    votos_partido = int(total_votos * votos_objetivo)
    
    # Aproximación REALISTA: 
    # - Con 40% de votos → ~12-15 estados (no 40% de estados)
    # - Con 50% de votos → ~20-24 estados
    # - Con 60% de votos → ~26-30 estados
    
    # Usar curva sigmoidea para modelar victoria por estados
    if votos_objetivo < 0.35:
        # Menos del 35%: muy pocos estados
        num_estados_ganados = int(32 * votos_objetivo * 0.5)
    elif votos_objetivo < 0.45:
        # 35-45%: crecimiento moderado
        num_estados_ganados = int(32 * votos_objetivo * 0.8)
    elif votos_objetivo < 0.55:
        # 45-55%: crecimiento fuerte (zona competitiva)
        num_estados_ganados = int(32 * votos_objetivo * 1.1)
    else:
        # >55%: saturación (ya se ganaron casi todos)
        num_estados_ganados = int(32 * votos_objetivo * 1.15)
    
    num_estados_ganados = min(num_estados_ganados, 32)
    num_estados_ganados = max(num_estados_ganados, 0)
    
    senadores_mr = num_estados_ganados * 2
    
    return {
        'viable': True,
        'metodo': 'simplificado',
        'estados_ganados': num_estados_ganados,
        'senadores_mr': senadores_mr,
        'votos_necesarios': votos_objetivo,
        'votos_absolutos': votos_partido,
        'total_votos_nacional': total_votos,
        'distribucion_por_estado': [],
        'advertencia': 'Método simplificado - Instalar módulos de redistritacion para cálculo preciso'
    }


def calcular_mayoria_forzada_senado(
    partido: str,
    tipo_mayoria: str = "simple",
    plan: str = "vigente",
    aplicar_topes: bool = True,
    anio: int = 2024
) -> Dict:
    """
    Calcula la configuración necesaria para que un partido alcance mayoría en el Senado
    
    Args:
        partido: Partido objetivo (MORENA, PAN, PRI, etc.)
        tipo_mayoria: "simple" (>64) o "calificada" (>=86)
        plan: Plan electoral ("vigente", "plan_a", "plan_c")
        aplicar_topes: Si aplica el tope del 8% de sobrerrepresentación
        anio: Año electoral
        
    Returns:
        dict con la configuración necesaria y si es viable
    """
    
    # Configurar según el plan
    if plan == "vigente":
        # Sistema vigente: 64 MR (32 estados × 2) + 32 PM + 32 RP = 128 total
        total_senadores = 128
        mr_disponibles = 64  # 32 estados × 2 senadores
        pm_disponibles = 32  # 32 estados × 1 senador
        rp_disponibles = 32
        
    elif plan == "plan_a":
        # Plan A: 96 RP puro
        total_senadores = 96
        mr_disponibles = 0
        pm_disponibles = 0
        rp_disponibles = 96
        
    elif plan == "plan_c":
        # Plan C: 64 MR+PM (32 estados × 2) sin RP
        total_senadores = 64
        mr_disponibles = 32  # 32 estados × 1 senador (solo primera fórmula)
        pm_disponibles = 32  # 32 estados × 1 senador (primera minoría)
        rp_disponibles = 0
        
    else:
        return {
            'viable': False,
            'razon': f'Plan "{plan}" no reconocido. Use: vigente, plan_a, plan_c'
        }
    
    # Calcular umbrales
    if tipo_mayoria == "simple":
        senadores_necesarios = (total_senadores // 2) + 1  # >50%
    elif tipo_mayoria == "calificada":
        senadores_necesarios = int((total_senadores * 2) / 3) + 1  # >=66.67%
    else:
        return {
            'viable': False,
            'razon': f'Tipo de mayoría "{tipo_mayoria}" no válido. Use: simple o calificada'
        }
    
    # Si hay tope del 8%, calcular máximo de senadores permitidos
    if aplicar_topes:
        max_senadores_con_tope = int(total_senadores * 0.58)  # 50% + 8% = 58%
        
        if tipo_mayoria == "calificada":
            return {
                'viable': False,
                'razon': f'Mayoría calificada ({senadores_necesarios}/{total_senadores} = {senadores_necesarios/total_senadores*100:.1f}%) es IMPOSIBLE con topes del 8%',
                'max_con_tope': max_senadores_con_tope,
                'max_porcentaje': 58.0,
                'senadores_necesarios': senadores_necesarios,
                'tipo_mayoria': tipo_mayoria,
                'plan': plan
            }
    
    # Para Plan A (RP puro), no hay MR que forzar
    if plan == "plan_a":
        # Solo calcular votos necesarios para RP
        votos_necesarios = senadores_necesarios / total_senadores
        
        return {
            'viable': True,
            'partido': partido,
            'tipo_mayoria': tipo_mayoria,
            'plan': plan,
            'senadores_necesarios': senadores_necesarios,
            'total_senadores': total_senadores,
            'senadores_rp': senadores_necesarios,  # Todos por RP
            'senadores_mr': 0,
            'votos_porcentaje': votos_necesarios * 100,
            'metodo': 'rp_puro',
            'advertencia': 'Plan A es RP puro - no hay MR ni PM'
        }
    
    # Para sistemas con MR (vigente o plan_c)
    # Estrategia: Maximizar MR ganados, minimizar votos necesarios
    
    # Iterar porcentajes de votos de 30% a 75%
    mejor_configuracion = None
    
    for votos_pct in range(30, 76):
        votos_decimal = votos_pct / 100.0
        
        # Calcular estados que ganaría con este porcentaje
        resultado = calcular_estados_mr_realistas(partido, votos_decimal, anio)
        
        if not resultado['viable']:
            continue
        
        estados_ganados = resultado['estados_ganados']
        
        # En plan_c, solo 1 MR por estado (el sistema es diferente)
        if plan == "plan_c":
            senadores_mr = estados_ganados  # Solo 1 por estado
            # En plan C también hay PM, pero eso se maneja aparte
            senadores_pm = min(estados_ganados, 32 - estados_ganados)  # PM en estados que no ganó
        else:
            # Sistema vigente: 2 MR por estado ganado
            senadores_mr = estados_ganados * 2
        
        # Calcular RP proporcional
        senadores_rp = int(rp_disponibles * votos_decimal)
        
        # Total de senadores
        if plan == "plan_c":
            # En plan C: MR del ganador + PM en otros estados
            # Simplificación: el partido gana MR donde es primero
            total_obtenidos = senadores_mr
        else:
            total_obtenidos = senadores_mr + senadores_rp
        
        # Verificar tope si aplica
        if aplicar_topes:
            max_permitidos = int(total_senadores * 0.58)
            if total_obtenidos > max_permitidos:
                total_obtenidos = max_permitidos
        
        # ¿Alcanza la mayoría?
        if total_obtenidos >= senadores_necesarios:
            mejor_configuracion = {
                'viable': True,
                'partido': partido,
                'tipo_mayoria': tipo_mayoria,
                'plan': plan,
                'senadores_necesarios': senadores_necesarios,
                'total_senadores': total_senadores,
                'senadores_obtenidos': total_obtenidos,
                'senadores_mr': senadores_mr,
                'senadores_rp': senadores_rp,
                'estados_ganados': estados_ganados,
                'total_estados': 32,
                'votos_porcentaje': votos_pct,
                'votos_absolutos': resultado['votos_absolutos'],
                'metodo': resultado['metodo'],
                'distribucion_estados': resultado.get('distribucion_por_estado', []),
                'topes_aplicados': aplicar_topes
            }
            break  # Encontramos el mínimo
    
    if mejor_configuracion:
        return mejor_configuracion
    else:
        return {
            'viable': False,
            'razon': f'No se encontró configuración viable para mayoría {tipo_mayoria}',
            'senadores_necesarios': senadores_necesarios,
            'total_senadores': total_senadores,
            'plan': plan
        }


def generar_tabla_estados_senado(
    partido: str,
    votos_porcentaje: float,
    anio: int = 2024
) -> pd.DataFrame:
    """
    Genera tabla de estados con el partido ganador y votos
    
    Args:
        partido: Partido objetivo
        votos_porcentaje: Porcentaje de votos (0-100)
        anio: Año electoral
        
    Returns:
        DataFrame con: estado, partido_ganador, votos_partido, votos_total, porcentaje
    """
    votos_decimal = votos_porcentaje / 100.0
    resultado = calcular_estados_mr_realistas(partido, votos_decimal, anio)
    
    if not resultado['viable']:
        return pd.DataFrame()
    
    # Convertir a DataFrame
    df = pd.DataFrame(resultado.get('distribucion_por_estado', []))
    
    if df.empty:
        return pd.DataFrame()
    
    # Agregar columna de ganador
    df['partido_ganador'] = partido
    df['senadores_mr'] = 2  # 2 por estado
    
    # Renombrar columnas
    df = df.rename(columns={
        'estado': 'ESTADO',
        'votos_partido': 'VOTOS_PARTIDO',
        'votos_total': 'VOTOS_TOTAL',
        'porcentaje': 'PORCENTAJE'
    })
    
    return df[['ESTADO', 'partido_ganador', 'senadores_mr', 'VOTOS_PARTIDO', 'VOTOS_TOTAL', 'PORCENTAJE']]
