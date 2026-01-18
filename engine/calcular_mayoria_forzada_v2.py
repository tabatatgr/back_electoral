"""
Calcula configuración REALISTA para forzar mayoría simple o calificada.

MÉTODO REALISTA (basado en redistritacion/calcular_votos_minimos_morena.py):
1. Usa redistritación geográfica REAL por población (método Hare)
2. Distribuye MR por estado según votación histórica 2024
3. Aplica factor de eficiencia geográfica (+10% realista)
4. Calcula votos mínimos necesarios para alcanzar mayoría
5. Genera configuración viable basada en datos reales

VENTAJAS sobre método simplificado:
- No asume proporcionalidad directa votos→MR
- Considera geografía real de México
- Usa votación histórica 2024 como base
- Resultados más creíbles y alcanzables

Autor: Sistema Electoral v2.0
Fecha: 2024
"""

from typing import Dict, Optional, Literal
import pandas as pd
import sys
from pathlib import Path

# Importar módulos de redistritación realista
try:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from redistritacion.modulos.reparto_distritos import repartir_distritos_hare
    from redistritacion.modulos.distritacion import cargar_secciones_ine
    REDISTRITACION_DISPONIBLE = True
except ImportError:
    REDISTRITACION_DISPONIBLE = False
    print("[WARN] Módulos de redistritación no disponibles, usando método simplificado")


# Mapeo de nombres de estados (mismo que en redistritacion)
ESTADO_NOMBRES = {
    1: 'AGUASCALIENTES', 2: 'BAJA CALIFORNIA', 3: 'BAJA CALIFORNIA SUR',
    4: 'CAMPECHE', 5: 'CHIAPAS', 6: 'CHIHUAHUA', 7: 'COAHUILA',
    8: 'COLIMA', 9: 'CIUDAD DE MEXICO', 10: 'DURANGO', 11: 'GUANAJUATO',
    12: 'GUERRERO', 13: 'HIDALGO', 14: 'JALISCO', 15: 'MEXICO',
    16: 'MICHOACAN', 17: 'MORELOS', 18: 'NAYARIT', 19: 'NUEVO LEON',
    20: 'OAXACA', 21: 'PUEBLA', 22: 'QUERETARO', 23: 'QUINTANA ROO',
    24: 'SAN LUIS POTOSI', 25: 'SINALOA', 26: 'SONORA', 27: 'TABASCO',
    28: 'TAMAULIPAS', 29: 'TLAXCALA', 30: 'VERACRUZ', 31: 'YUCATAN',
    32: 'ZACATECAS'
}


def calcular_distritos_mr_realistas(
    partido: str,
    mr_total: int,
    pct_votos_objetivo: float,
    eficiencia: float = 1.1,
    anio_base: int = 2024
) -> Dict[str, int]:
    """
    Calcula distribución realista de distritos MR por partido usando método geográfico.
    
    Args:
        partido: Partido objetivo
        mr_total: Total de distritos MR
        pct_votos_objetivo: % de votos del partido objetivo
        eficiencia: Factor de conversión votos→distritos (1.1 = +10% por geografía)
        anio_base: Año base para datos históricos
    
    Returns:
        Dict con distribución MR por partido
    """
    if not REDISTRITACION_DISPONIBLE:
        # Fallback al método simplificado
        return calcular_distritos_mr_simplificado(partido, mr_total, pct_votos_objetivo)
    
    try:
        # Cargar población por estado
        secciones = cargar_secciones_ine()
        poblacion_por_estado = secciones.groupby('ENTIDAD')['POBTOT'].sum().to_dict()
        
        # Repartir distritos usando método Hare
        asignacion_distritos = repartir_distritos_hare(
            poblacion_estados=poblacion_por_estado,
            n_distritos=mr_total,
            piso_constitucional=2
        )
        
        # Cargar votos reales 2024
        df_votos = pd.read_parquet(f'data/computos_diputados_{anio_base}.parquet')
        df_votos['ENTIDAD_NOMBRE'] = df_votos['ENTIDAD'].str.strip().str.upper()
        
        # Calcular factor de escalamiento: de votación real a objetivo
        # MORENA 2024: 42.49%
        votacion_real_2024 = 42.49
        factor_escala = pct_votos_objetivo / votacion_real_2024
        
        # Distribuir MR por estado
        mr_por_estado_partido = {}
        total_mr_partido = 0
        
        for entidad_id, nombre in ESTADO_NOMBRES.items():
            # Buscar votos del estado
            df_estado = df_votos[df_votos['ENTIDAD_NOMBRE'] == nombre]
            
            if len(df_estado) == 0:
                df_estado = df_votos[df_votos['ENTIDAD_NOMBRE'].str.contains(nombre.split()[0], na=False)]
            
            if len(df_estado) > 0:
                votos_morena = df_estado['MORENA'].sum()
                votos_totales = df_estado['TOTAL_BOLETAS'].sum()
                pct_morena_estado_real = (votos_morena / votos_totales * 100) if votos_totales > 0 else 0
                
                # Escalar proporcionalmente
                pct_partido_estado = pct_morena_estado_real * factor_escala
            else:
                pct_partido_estado = pct_votos_objetivo  # Default
            
            distritos_totales = asignacion_distritos.get(entidad_id, 0)
            
            # Calcular distritos ganados con eficiencia
            distritos_ganados = int(distritos_totales * (pct_partido_estado / 100) * eficiencia)
            distritos_ganados = min(distritos_ganados, distritos_totales)
            
            mr_por_estado_partido[nombre] = distritos_ganados
            total_mr_partido += distritos_ganados
        
        # Ajustar para alcanzar el MR objetivo si hay diferencia
        if total_mr_partido < mr_total:
            # Distribuir los faltantes en estados grandes
            diferencia = mr_total - total_mr_partido
            estados_grandes = ['MEXICO', 'JALISCO', 'VERACRUZ', 'CIUDAD DE MEXICO', 'GUANAJUATO']
            for estado in estados_grandes:
                if diferencia <= 0:
                    break
                mr_por_estado_partido[estado] = mr_por_estado_partido.get(estado, 0) + 1
                diferencia -= 1
        
        # Distribuir el resto entre otros partidos
        mr_restantes = mr_total - sum(mr_por_estado_partido.values())
        
        # Otros partidos (distribución proporcional histórica)
        otros_partidos = ['PAN', 'PRI', 'MC', 'PVEM', 'PT']
        dist_otros = {
            'PAN': 0.35,
            'PRI': 0.28,
            'MC': 0.19,
            'PVEM': 0.10,
            'PT': 0.08
        }
        
        mr_distritos = {partido: sum(mr_por_estado_partido.values())}
        
        for p, prop in dist_otros.items():
            if p == partido:
                continue
            mr_distritos[p] = int(mr_restantes * prop)
        
        # Ajustar para que sume exacto
        total_asignado = sum(mr_distritos.values())
        if total_asignado < mr_total:
            mr_distritos['PAN'] += (mr_total - total_asignado)
        
        return mr_distritos
        
    except Exception as e:
        print(f"[WARN] Error en cálculo realista: {e}, usando método simplificado")
        return calcular_distritos_mr_simplificado(partido, mr_total, pct_votos_objetivo)


def calcular_distritos_mr_simplificado(
    partido: str,
    mr_total: int,
    pct_votos: float
) -> Dict[str, int]:
    """
    Método simplificado cuando no está disponible la redistritación.
    """
    # Calcular MR para el partido objetivo (proporcional + boost)
    mr_partido = int(mr_total * (pct_votos / 100) * 1.1)  # +10% eficiencia
    mr_partido = min(mr_partido, mr_total)
    
    # Distribuir el resto
    mr_restantes = mr_total - mr_partido
    
    dist_otros = {
        'PAN': 0.35,
        'PRI': 0.28,
        'MC': 0.19,
        'PVEM': 0.10,
        'PT': 0.08
    }
    
    mr_distritos = {partido: mr_partido}
    
    for p, prop in dist_otros.items():
        if p == partido:
            continue
        mr_distritos[p] = int(mr_restantes * prop)
    
    # Ajustar para que sume exacto
    total_asignado = sum(mr_distritos.values())
    if total_asignado < mr_total:
        mr_distritos['PAN'] += (mr_total - total_asignado)
    
    return mr_distritos


def calcular_mayoria_forzada(
    partido: str,
    tipo_mayoria: Literal["simple", "calificada"],
    mr_total: int = 300,
    rp_total: int = 100,
    aplicar_topes: bool = True,
    votos_base: Optional[Dict[str, float]] = None,
    solo_partido: bool = True,  # 🆕 NUEVO: Si true, fuerza solo el partido; si false, fuerza la coalición
    anio: int = 2024  # 🆕 NUEVO: Año electoral
) -> Dict:
    """
    Calcula configuración REALISTA para forzar mayoría.
    
    Usa método geográfico basado en redistritacion/calcular_votos_minimos_morena.py
    
    Args:
        partido: Partido objetivo (MORENA, PAN, PRI, etc.)
        tipo_mayoria: "simple" (201) o "calificada" (267)
        mr_total: Total de distritos MR
        rp_total: Total de escaños RP
        aplicar_topes: Si aplicar topes del 8%
        votos_base: Distribución actual de votos (opcional)
        solo_partido: Si True, fuerza mayoría SOLO del partido; Si False, fuerza coalición completa
        anio: Año electoral (2018, 2021, 2024)
    
    Returns:
        Dict con configuración y viabilidad
    """
    total_escanos = mr_total + rp_total
    objetivo = 201 if tipo_mayoria == "simple" else 267
    
    # 1. VALIDAR si es posible
    if tipo_mayoria == "calificada" and aplicar_topes:
        # Con topes, mayoría calificada es matemáticamente imposible
        votos_necesarios = (objetivo / total_escanos - 0.08) * 100
        
        return {
            "viable": False,
            "razon": f"Mayoría calificada ({objetivo} escaños) es IMPOSIBLE con topes del 8%. "
                     f"Requeriría {votos_necesarios:.1f}% de votos (históricamente inalcanzable). "
                     f"Para usar mayoría calificada, DESACTIVE los topes (aplicar_topes=False)",
            "sugerencia": "Desactivar topes de sobrerrepresentación",
            "votos_min_necesarios": votos_necesarios
        }
    
    # 2. CALCULAR votos mínimos necesarios (basado en análisis realista)
    if tipo_mayoria == "simple":
        # Mayoría simple con eficiencia geográfica +10%
        if mr_total == 300 and rp_total == 100 and aplicar_topes:
            # Caso analizado: requiere ~47% votos
            pct_votos_necesario = 47.0
            mr_objetivo = 155  # De análisis
            rp_esperado = 47   # Aproximado
        elif mr_total == 300 and rp_total == 100 and not aplicar_topes:
            pct_votos_necesario = 40.0
            mr_objetivo = 130
            rp_esperado = 72
        else:
            # BÚSQUEDA ITERATIVA para encontrar % exacto
            # Para configuraciones personalizadas, usar búsqueda binaria
            umbral_mayorias = (total_escanos // 2) + 1  # Mayoría simple = 50% + 1
            
            print(f"[DEBUG] Mayoría forzada genérica: total={total_escanos}, umbral={umbral_mayorias}")
            print(f"[DEBUG] Usando búsqueda iterativa para encontrar % exacto...")
            
            # Búsqueda binaria: empezar entre 40% y 70%
            pct_min = 40.0
            pct_max = 70.0
            pct_votos_necesario = 50.0  # Valor inicial
            
            # Iteraciones de búsqueda
            for _ in range(20):  # Máximo 20 iteraciones
                pct_actual = (pct_min + pct_max) / 2
                
                # Estimar escaños con este porcentaje
                # MR: usar eficiencia conservadora (0.9 para configs pequeñas)
                eficiencia_mr = 0.9 if mr_total < 100 else 1.1
                mr_estimado = int(mr_total * (pct_actual / 100) * eficiencia_mr)
                mr_estimado = min(mr_estimado, mr_total)
                
                # RP: proporcional directo
                rp_estimado = int(rp_total * (pct_actual / 100))
                
                total_estimado = mr_estimado + rp_estimado
                
                # Ajustar rango de búsqueda
                if total_estimado < umbral_mayorias:
                    pct_min = pct_actual  # Necesita más %
                elif total_estimado >= umbral_mayorias + 5:
                    pct_max = pct_actual  # Demasiado %
                else:
                    # Encontrado rango aceptable
                    pct_votos_necesario = pct_actual
                    mr_objetivo = mr_estimado
                    rp_esperado = rp_estimado
                    break
            else:
                # Si no converge, usar valor medio
                pct_votos_necesario = (pct_min + pct_max) / 2
                eficiencia_mr = 0.9 if mr_total < 100 else 1.1
                mr_objetivo = int(mr_total * (pct_votos_necesario / 100) * eficiencia_mr)
                mr_objetivo = min(mr_objetivo, mr_total)
                rp_esperado = umbral_mayorias - mr_objetivo
            
            print(f"[DEBUG] Resultado búsqueda: {pct_votos_necesario:.1f}% votos → {mr_objetivo} MR + {rp_esperado} RP = {mr_objetivo + rp_esperado} escaños")
            
    else:
        # Mayoría calificada (solo sin topes, ya validado arriba)
        umbral_calificada = int(total_escanos * 2 / 3) + 1  # 66.67% + 1
        
        if mr_total == 300 and rp_total == 100:
            pct_votos_necesario = 62.5
            mr_objetivo = 206
            rp_esperado = 62
        elif mr_total == 200 and rp_total == 200:
            pct_votos_necesario = 64.0
            mr_objetivo = 140
            rp_esperado = 128
        else:
            # Estimación genérica para mayoría calificada
            # Requiere ~66.67% de escaños
            # Con eficiencia 1.1 en MR:
            # pct = umbral / (mr_total * 1.1 + rp_total)
            
            pct_votos_necesario = (umbral_calificada / (mr_total * 1.1 + rp_total)) * 100
            mr_objetivo = int(mr_total * (pct_votos_necesario / 100) * 1.1)
            mr_objetivo = min(mr_objetivo, mr_total)
            rp_esperado = umbral_calificada - mr_objetivo
            
            print(f"[DEBUG] Mayoría calificada genérica: total={total_escanos}, umbral={umbral_calificada}")
            print(f"[DEBUG] Estimación: {pct_votos_necesario:.1f}% votos → {mr_objetivo} MR + {rp_esperado} RP = {mr_objetivo + rp_esperado} escaños")
    
    # 3. GENERAR distribución realista de MR
    mr_distritos = calcular_distritos_mr_realistas(
        partido=partido,
        mr_total=mr_total,
        pct_votos_objetivo=pct_votos_necesario,
        eficiencia=1.1  # +10% eficiencia geográfica realista
    )
    
    # 🆕 PASO 3.5: Si solo_partido=True, redistribuir distritos MR de coalición
    coalicion_4t = ['MORENA', 'PT', 'PVEM']
    coalicion_xm = ['PAN', 'PRI', 'PRD']
    
    if solo_partido:
        print(f"[DEBUG MR] solo_partido=True: Redistribuyendo distritos de coalición partners")
        
        # Identificar partidos de coalición
        if partido in coalicion_4t:
            partidos_coalicion = [p for p in coalicion_4t if p != partido]
            todos_partidos = list(mr_distritos.keys())
            print(f"[DEBUG MR] {partido} en 4T, partners: {partidos_coalicion}")
        elif partido in coalicion_xm:
            partidos_coalicion = [p for p in coalicion_xm if p != partido]
            todos_partidos = list(mr_distritos.keys())
            print(f"[DEBUG MR] {partido} en Fuerza y Corazón, partners: {partidos_coalicion}")
        else:
            partidos_coalicion = []
            todos_partidos = list(mr_distritos.keys())
            print(f"[DEBUG MR] {partido} sin coalición conocida")
        
        # Calcular cuántos distritos hay que redistribuir (de PT y PVEM)
        mr_coalicion_total = 0
        for p_coal in partidos_coalicion:
            if p_coal in mr_distritos:
                mr_previo = mr_distritos[p_coal]
                mr_coalicion_total += mr_previo
                print(f"[DEBUG MR]   {p_coal}: {mr_previo} distritos (se anularán)")
        
        if mr_coalicion_total > 0:
            # Calcular total ANTES de anular coalición partners
            total_mr_antes = sum(mr_distritos.values())
            
            # Anular coalición partners
            for p_coal in partidos_coalicion:
                mr_distritos[p_coal] = 0
            
            # Calcular proporción de cada partido (SIN coalición partners)
            partidos_activos = [p for p in todos_partidos if p not in partidos_coalicion]
            total_mr_activos = sum(mr_distritos.get(p, 0) for p in partidos_activos)
            
            print(f"[DEBUG MR] Redistribuyendo {mr_coalicion_total} distritos proporcionalmente:")
            
            # Redistribuir proporcionalmente entre TODOS (incluyendo partido objetivo)
            distritos_redistribuidos = {}
            for p in partidos_activos:
                if p in mr_distritos and total_mr_activos > 0:
                    proporcion = mr_distritos[p] / total_mr_activos
                    distritos_extra = round(mr_coalicion_total * proporcion)
                    distritos_redistribuidos[p] = distritos_extra
            
            # Ajustar para que sume exactamente mr_coalicion_total
            suma_redistribuida = sum(distritos_redistribuidos.values())
            diferencia = mr_coalicion_total - suma_redistribuida
            
            # Dar la diferencia al partido con más distritos
            if diferencia != 0 and partidos_activos:
                partido_mayor = max(partidos_activos, key=lambda p: mr_distritos.get(p, 0))
                distritos_redistribuidos[partido_mayor] = distritos_redistribuidos.get(partido_mayor, 0) + diferencia
            
            # Aplicar redistribución
            for p, extra in distritos_redistribuidos.items():
                if extra > 0:
                    mr_previo = mr_distritos[p]
                    mr_distritos[p] = mr_previo + extra
                    print(f"[DEBUG MR]   {p}: {mr_previo} → {mr_distritos[p]} (+{extra} redistribuidos)")
            
            # Verificar que el partido objetivo puede alcanzar mayoría
            mr_partido_actual = mr_distritos.get(partido, 0)
            print(f"[DEBUG MR] {partido} tiene ahora {mr_partido_actual} distritos MR")
            
            # Si el partido objetivo no alcanza suficientes MR para la mayoría, 
            # necesitamos incrementar su porcentaje de votos
            # Estimación: con mr_partido_actual MR y el RP proporcional, ¿alcanza?
            escanos_estimados = mr_partido_actual + rp_esperado
            
            if escanos_estimados < objetivo:
                # Necesita más votos - incrementar porcentaje
                deficit = objetivo - escanos_estimados
                pct_adicional = (deficit / rp_total) * 100  # Porcentaje extra en RP
                pct_votos_necesario_nuevo = pct_votos_necesario + pct_adicional
                
                print(f"[DEBUG MR] ⚠️  Déficit: {deficit} escaños, incrementando votos de {pct_votos_necesario:.1f}% a {pct_votos_necesario_nuevo:.1f}%")
                
                # Recalcular RP esperado con nuevo porcentaje
                rp_esperado = int(rp_total * (pct_votos_necesario_nuevo / 100))
                
                # Actualizar el porcentaje para usarlo en votos_custom más adelante
                pct_votos_necesario = pct_votos_necesario_nuevo
    
    # 4. CALCULAR distribución de votos
    if votos_base is None:
        # Distribución histórica 2024
        votos_base_dist = {
            'MORENA': 42.49,
            'PAN': 21.09,
            'PRI': 17.24,
            'MC': 11.50,
            'PVEM': 5.75,
            'PT': 3.83
        }
    else:
        votos_base_dist = votos_base.copy()
    
    # Ajustar para que el partido objetivo tenga los votos necesarios
    votos_custom = votos_base_dist.copy()
    votos_custom[partido] = pct_votos_necesario
    
    # 🆕 LÓGICA DE solo_partido
    if solo_partido:
        # Si solo_partido=True, los aliados del partido deben quedar en 0
        # y sus votos se redistribuyen a la oposición
        print(f"[DEBUG] solo_partido=True: Redistribuyendo votos de coalición a oposición")
        
        # Identificar partidos de la coalición del partido objetivo
        if partido in coalicion_4t:
            partidos_coalicion = [p for p in coalicion_4t if p != partido and p in votos_custom]
            partidos_oposicion = [p for p in votos_custom.keys() if p not in coalicion_4t]
        elif partido in coalicion_xm:
            partidos_coalicion = [p for p in coalicion_xm if p != partido and p in votos_custom]
            partidos_oposicion = [p for p in votos_custom.keys() if p not in coalicion_xm]
        else:
            # Partido sin coalición conocida, redistribuir entre todos los demás
            partidos_coalicion = []
            partidos_oposicion = [p for p in votos_custom.keys() if p != partido]
        
        # Sumar votos de los partidos de la coalición (que vamos a poner en 0)
        votos_coalicion_total = sum(votos_base_dist.get(p, 0) for p in partidos_coalicion)
        
        # Poner partidos de la coalición en 0
        for p in partidos_coalicion:
            votos_custom[p] = 0.0
        
        # Calcular votos disponibles para redistribuir
        # Total disponible = 100 - votos del partido objetivo
        otros_total = 100 - pct_votos_necesario
        
        # Redistribuir SOLO entre la oposición (no incluye coalición)
        suma_oposicion = sum(votos_base_dist.get(p, 0) for p in partidos_oposicion)
        
        if suma_oposicion > 0:
            for p in partidos_oposicion:
                proporcion = votos_base_dist.get(p, 0) / suma_oposicion
                votos_custom[p] = otros_total * proporcion
        
        print(f"[DEBUG] Partidos coalición (0%): {partidos_coalicion}")
        print(f"[DEBUG] Votos redistribuidos ({votos_coalicion_total:.2f}%) a oposición: {partidos_oposicion}")
    else:
        # Comportamiento original: redistribuir entre TODOS los demás partidos
        print(f"[DEBUG] solo_partido=False: Redistribuyendo entre todos los partidos")
        otros_total = 100 - pct_votos_necesario
        otros_partidos = [p for p in votos_custom.keys() if p != partido]
        suma_otros = sum(votos_base_dist.get(p, 0) for p in otros_partidos)
        
        for p in otros_partidos:
            proporcion = votos_base_dist.get(p, 0) / suma_otros if suma_otros > 0 else 1.0 / len(otros_partidos)
            votos_custom[p] = otros_total * proporcion
    
    # 5. ADVERTENCIAS
    advertencias = []
    
    if pct_votos_necesario > 55:
        advertencias.append(f"Requiere votación muy alta ({pct_votos_necesario:.1f}%) - históricamente difícil de alcanzar")
    
    if tipo_mayoria == "calificada":
        pct_mr = (mr_objetivo / mr_total) * 100
        if pct_mr > 70:
            advertencias.append(f"Mayoría calificada requiere dominio extremo: {pct_mr:.0f}% de distritos MR")
            advertencias.append(f"Requiere ganar {mr_objetivo}/{mr_total} distritos MR ({pct_mr:.0f}%) - dominio extremo, históricamente improbable")
    
    if not aplicar_topes and tipo_mayoria == "simple":
        advertencias.append("Sin topes, el partido podría obtener MÁS del objetivo de mayoría simple")
    
    # 6. RETORNAR configuración
    return {
        "viable": True,
        "objetivo_escanos": objetivo,
        "mr_distritos_manuales": mr_distritos,
        "votos_custom": votos_custom,
        "detalle": {
            "mr_ganados": mr_distritos[partido],
            "mr_total": mr_total,
            "pct_mr": (mr_distritos[partido] / mr_total) * 100,
            "rp_esperado": rp_esperado,
            "rp_total": rp_total,
            "pct_votos": pct_votos_necesario
        },
        "advertencias": advertencias,
        "metodo": "Redistritación geográfica realista (Hare + eficiencia 1.1)" if REDISTRITACION_DISPONIBLE else "Método simplificado"
    }


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("TEST: Cálculo REALISTA de Mayoría Forzada")
    print("="*80)
    
    # Test 1: Mayoría simple CON TOPES (300-100)
    print("\n1. Mayoría SIMPLE para MORENA (300 MR + 100 RP, CON TOPES)")
    print("-"*80)
    resultado = calcular_mayoria_forzada(
        partido="MORENA",
        tipo_mayoria="simple",
        mr_total=300,
        rp_total=100,
        aplicar_topes=True
    )
    
    if resultado['viable']:
        print(f"✓ VIABLE")
        print(f"\nObjetivo: {resultado['objetivo_escanos']} escaños")
        print(f"Método: {resultado['metodo']}")
        print(f"\nDistribución:")
        print(f"  MR ganados: {resultado['detalle']['mr_ganados']}/{resultado['detalle']['mr_total']} ({resultado['detalle']['pct_mr']:.1f}%)")
        print(f"  RP esperado: {resultado['detalle']['rp_esperado']}/{resultado['detalle']['rp_total']}")
        print(f"  Votos necesarios: {resultado['detalle']['pct_votos']:.1f}%")
        print(f"\nConfiguración:")
        print(f"  mr_distritos_manuales: {resultado['mr_distritos_manuales']}")
        print(f"  votos_custom: {resultado['votos_custom']}")
        if resultado['advertencias']:
            print(f"\n⚠️  Advertencias:")
            for adv in resultado['advertencias']:
                print(f"  - {adv}")
    else:
        print(f"✗ NO VIABLE")
        print(f"Razón: {resultado['razon']}")
    
    # Test 2: Mayoría calificada CON TOPES (debe fallar)
    print("\n" + "="*80)
    print("2. Mayoría CALIFICADA para MORENA (300 MR + 100 RP, CON TOPES)")
    print("-"*80)
    resultado = calcular_mayoria_forzada(
        partido="MORENA",
        tipo_mayoria="calificada",
        mr_total=300,
        rp_total=100,
        aplicar_topes=True
    )
    
    if not resultado['viable']:
        print(f"✓ Correctamente rechazado")
        print(f"Razón: {resultado['razon']}")
        print(f"Votos mínimos requeridos: {resultado['votos_min_necesarios']:.1f}%")
    else:
        print(f"✗ ERROR: No debería ser viable")
    
    # Test 3: Mayoría calificada SIN TOPES (200-200)
    print("\n" + "="*80)
    print("3. Mayoría CALIFICADA para MORENA (200 MR + 200 RP, SIN TOPES)")
    print("-"*80)
    resultado = calcular_mayoria_forzada(
        partido="MORENA",
        tipo_mayoria="calificada",
        mr_total=200,
        rp_total=200,
        aplicar_topes=False
    )
    
    if resultado['viable']:
        print(f"✓ VIABLE")
        print(f"\nObjetivo: {resultado['objetivo_escanos']} escaños")
        print(f"Método: {resultado['metodo']}")
        print(f"\nDistribución:")
        print(f"  MR ganados: {resultado['detalle']['mr_ganados']}/{resultado['detalle']['mr_total']} ({resultado['detalle']['pct_mr']:.1f}%)")
        print(f"  RP esperado: {resultado['detalle']['rp_esperado']}/{resultado['detalle']['rp_total']}")
        print(f"  Votos necesarios: {resultado['detalle']['pct_votos']:.1f}%")
        if resultado['advertencias']:
            print(f"\n⚠️  Advertencias:")
            for adv in resultado['advertencias']:
                print(f"  - {adv}")
    else:
        print(f"✗ NO VIABLE")
        print(f"Razón: {resultado['razon']}")
    
    print("\n" + "="*80)
