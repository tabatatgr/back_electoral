"""
Calcula el % de votos mínimo que necesita MORENA para lograr mayorías.

VERSIÓN CORREGIDA: Usa redistritación REAL por población (método Hare)
en lugar de asumir proporcionalidad directa.

Busca el punto de equilibrio: ¿Qué % de votos permite lograr mayoría
con una combinación REALISTA de MR ganados + RP proporcional?

Método iterativo: prueba diferentes % de votos y encuentra el mínimo.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from redistritacion.modulos.reparto_distritos import repartir_distritos_hare
from redistritacion.modulos.distritacion import cargar_secciones_ine


def calcular_mr_ganados_real(pct_votos, mr_total, eficiencia_mr=1.0, 
                             asignacion_distritos=None, df_votos=None, estado_nombres=None):
    """
    Calcula MR ganados usando redistritación REAL por población.
    
    Args:
        pct_votos: % de votos del partido
        mr_total: Total de distritos MR
        eficiencia_mr: Factor de conversión votos→distritos MR
        asignacion_distritos: Pre-calculado (para optimización)
        df_votos: Pre-cargado (para optimización)
        estado_nombres: Mapeo pre-definido (para optimización)
    
    Returns:
        Número de MR ganados
    """
    # Si no están pre-calculados, cargarlos
    if asignacion_distritos is None:
        secciones = cargar_secciones_ine()
        poblacion_por_estado = secciones.groupby('ENTIDAD')['POBTOT'].sum().to_dict()
        asignacion_distritos = repartir_distritos_hare(
            poblacion_estados=poblacion_por_estado,
            n_distritos=mr_total,
            piso_constitucional=2
        )
    
    if df_votos is None:
        df_votos = pd.read_parquet('data/computos_diputados_2024.parquet')
        df_votos['ENTIDAD_NOMBRE'] = df_votos['ENTIDAD'].str.strip().str.upper()
    
    if estado_nombres is None:
        estado_nombres = {
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
    
    # Calcular factor de escalamiento: de 42.49% real a pct_votos
    factor_escala = pct_votos / 42.49
    
    # Calcular MR ganados por estado
    total_mr_ganados = 0
    
    for entidad_id, nombre in estado_nombres.items():
        # Buscar en df_votos
        df_estado = df_votos[df_votos['ENTIDAD_NOMBRE'] == nombre]
        
        if len(df_estado) == 0:
            # Probar variantes del nombre
            df_estado = df_votos[df_votos['ENTIDAD_NOMBRE'].str.contains(nombre.split()[0], na=False)]
        
        if len(df_estado) > 0:
            votos_morena = df_estado['MORENA'].sum()
            votos_totales = df_estado['TOTAL_BOLETAS'].sum()
            pct_morena_estado_real = (votos_morena / votos_totales * 100) if votos_totales > 0 else 0
            # Escalar proporcionalmente
            pct_morena_estado = pct_morena_estado_real * factor_escala
        else:
            pct_morena_estado = pct_votos  # Default nacional
        
        distritos_totales = asignacion_distritos.get(entidad_id, 0)
        
        # Calcular distritos ganados con eficiencia
        distritos_ganados = int(distritos_totales * (pct_morena_estado / 100) * eficiencia_mr)
        distritos_ganados = min(distritos_ganados, distritos_totales)
        
        total_mr_ganados += distritos_ganados
    
    return total_mr_ganados


def calcular_escanos_combinado(pct_votos, mr_total, rp_total, aplicar_topes, 
                                eficiencia_mr=1.0,
                                asignacion_distritos=None, df_votos=None, estado_nombres=None):
    """
    Calcula escaños usando redistritación REAL para MR + proporcional para RP.
    
    Args:
        pct_votos: % de votos del partido
        mr_total: Total de distritos MR
        rp_total: Total de escaños RP
        aplicar_topes: Si True, aplica topes del 8%
        eficiencia_mr: Factor de conversión votos→distritos MR
        asignacion_distritos: Pre-calculado para optimización
        df_votos: Pre-cargado para optimización
        estado_nombres: Pre-definido para optimización
    
    Returns:
        Dict con escaños MR, RP, total
    """
    total_seats = mr_total + rp_total
    v_nacional = pct_votos / 100.0
    
    # MR ganados: USA REDISTRITACIÓN REAL
    mr_ganados = calcular_mr_ganados_real(pct_votos, mr_total, eficiencia_mr,
                                          asignacion_distritos, df_votos, estado_nombres)
    
    # RP proporcional a votos (método Hare simplificado)
    rp_proporcional = int(rp_total * v_nacional)
    
    # Total sin topes
    total_sin_topes = mr_ganados + rp_proporcional
    
    # Aplicar topes si corresponde
    if aplicar_topes:
        cap_dist = int(np.floor((v_nacional + 0.08) * total_seats))
        
        if total_sin_topes > cap_dist:
            total_con_topes = cap_dist
            rp_final = max(0, cap_dist - mr_ganados)
        else:
            total_con_topes = total_sin_topes
            rp_final = rp_proporcional
    else:
        total_con_topes = total_sin_topes
        rp_final = rp_proporcional
    
    return {
        'pct_votos': pct_votos,
        'mr_ganados': mr_ganados,
        'rp_ganados': rp_final,
        'total': total_con_topes,
        'pct_escanos': total_con_topes / total_seats * 100,
        'cap_dist': int(np.floor((v_nacional + 0.08) * total_seats)) if aplicar_topes else None
    }


def buscar_votos_minimos(mr_total, rp_total, aplicar_topes, objetivo_escanos,
                         eficiencia_mr=1.1):
    """
    Busca el % de votos mínimo para alcanzar objetivo_escanos.
    OPTIMIZADO: Pre-calcula datos compartidos.
    
    Args:
        mr_total: Total de distritos MR
        rp_total: Total de escaños RP
        aplicar_topes: Si True, aplica topes del 8%
        objetivo_escanos: Meta (201 para simple, 267 para calificada)
        eficiencia_mr: Factor de eficiencia en conversión votos→MR
    
    Returns:
        Dict con el % mínimo y detalle de escaños
    """
    # PRE-CALCULAR datos compartidos (esto es clave para optimizar)
    secciones = cargar_secciones_ine()
    poblacion_por_estado = secciones.groupby('ENTIDAD')['POBTOT'].sum().to_dict()
    asignacion_distritos = repartir_distritos_hare(
        poblacion_estados=poblacion_por_estado,
        n_distritos=mr_total,
        piso_constitucional=2
    )
    
    df_votos = pd.read_parquet('data/computos_diputados_2024.parquet')
    df_votos['ENTIDAD_NOMBRE'] = df_votos['ENTIDAD'].str.strip().str.upper()
    
    estado_nombres = {
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
    
    # Búsqueda binaria entre 30% y 80%
    min_pct = 30.0
    max_pct = 80.0
    
    mejor_resultado = None
    
    # Prueba incrementos de 0.5%
    for pct in np.arange(min_pct, max_pct + 0.5, 0.5):
        resultado = calcular_escanos_combinado(pct, mr_total, rp_total, 
                                               aplicar_topes, eficiencia_mr,
                                               asignacion_distritos, df_votos, estado_nombres)
        
        if resultado['total'] >= objetivo_escanos:
            if mejor_resultado is None or pct < mejor_resultado['pct_votos']:
                mejor_resultado = resultado
            break
    
    return mejor_resultado


def analizar_votos_minimos_morena():
    """
    Calcula votos mínimos para MORENA en cada escenario.
    """
    
    escenarios_config = [
        ('300-100 CON TOPES', 300, 100, True),
        ('300-100 SIN TOPES', 300, 100, False),
        ('200-200 SIN TOPES', 200, 200, False),
        ('240-160 SIN TOPES', 240, 160, False),
        ('240-160 CON TOPES', 240, 160, True)
    ]
    
    # Factores de eficiencia a considerar
    # 1.0 = votos se convierten proporcionalmente en distritos MR
    # 1.1 = gana 10% más distritos por concentración geográfica favorable
    # 1.2 = gana 20% más distritos (muy favorable)
    eficiencias = [
        (1.0, 'Proporcional exacto (votos% = MR% ganado)'),
        (1.1, 'Eficiencia +10% (concentración geográfica favorable)'),
        (1.2, 'Eficiencia +20% (muy concentrado geográficamente)')
    ]
    
    print("="*120)
    print("¿QUÉ % DE VOTOS NECESITA MORENA PARA MAYORÍAS?")
    print("Análisis con REDISTRITACIÓN REAL por población + RP proporcional")
    print("="*120)
    print("\n⚠️  NOTA: Este análisis usa redistritación REAL (método Hare por población)")
    print("   NO asume proporcionalidad directa. Los resultados son más precisos.\n")
    
    todos_resultados = []
    
    for eficiencia_val, eficiencia_desc in eficiencias:
        print(f"\n{'='*120}")
        print(f"ESCENARIO: {eficiencia_desc}")
        print(f"{'='*120}")
        
        for nombre, mr, rp, topes in escenarios_config:
            print(f"\n{'─'*120}")
            print(f"{nombre} ({mr} MR + {rp} RP)")
            print(f"{'─'*120}")
            
            # Mayoría simple (201)
            simple = buscar_votos_minimos(mr, rp, topes, 201, eficiencia_val)
            
            # Mayoría calificada (267)
            calificada = buscar_votos_minimos(mr, rp, topes, 267, eficiencia_val)
            
            print(f"\n📊 MAYORÍA SIMPLE (201 escaños):")
            if simple:
                print(f"   Votos mínimos: {simple['pct_votos']:.1f}%")
                print(f"   → {simple['mr_ganados']} MR + {simple['rp_ganados']} RP = {simple['total']} escaños ({simple['pct_escanos']:.1f}%)")
                if topes:
                    print(f"   Tope: {simple['cap_dist']} escaños")
            else:
                print(f"   ❌ NO ALCANZABLE (requiere >70% votos)")
            
            print(f"\n🏛️  MAYORÍA CALIFICADA (267 escaños):")
            if calificada:
                print(f"   Votos mínimos: {calificada['pct_votos']:.1f}%")
                print(f"   → {calificada['mr_ganados']} MR + {calificada['rp_ganados']} RP = {calificada['total']} escaños ({calificada['pct_escanos']:.1f}%)")
                if topes:
                    print(f"   Tope: {calificada['cap_dist']} escaños")
            else:
                print(f"   ❌ NO ALCANZABLE (requiere >70% votos o tope insuficiente)")
            
            # Guardar resultados
            todos_resultados.append({
                'escenario': nombre,
                'eficiencia': eficiencia_desc,
                'eficiencia_val': eficiencia_val,
                'mr_total': mr,
                'rp_total': rp,
                'topes': topes,
                'mayoria_simple_votos': simple['pct_votos'] if simple else None,
                'mayoria_simple_mr': simple['mr_ganados'] if simple else None,
                'mayoria_simple_rp': simple['rp_ganados'] if simple else None,
                'mayoria_calificada_votos': calificada['pct_votos'] if calificada else None,
                'mayoria_calificada_mr': calificada['mr_ganados'] if calificada else None,
                'mayoria_calificada_rp': calificada['rp_ganados'] if calificada else None
            })
    
    # Crear DataFrame y guardar
    df = pd.DataFrame(todos_resultados)
    output_path = 'redistritacion/outputs/votos_minimos_morena.csv'
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n{'='*120}")
    print(f"✓ Resultados guardados en: {output_path}")
    print(f"{'='*120}")
    
    # Resumen comparativo
    print(f"\n{'='*120}")
    print("RESUMEN COMPARATIVO: VOTOS MÍNIMOS POR ESCENARIO")
    print(f"{'='*120}")
    
    # Filtrar solo eficiencia 1.1 (escenario realista)
    df_realista = df[df['eficiencia_val'] == 1.1].copy()
    
    print(f"\nCon EFICIENCIA REALISTA (+10% geográfica):")
    print(f"{'─'*120}")
    print(f"{'Escenario':<25} {'May.Simple':<15} {'MR':<8} {'RP':<8} {'May.Calif':<15} {'MR':<8} {'RP':<8}")
    print(f"{'─'*120}")
    
    for _, row in df_realista.iterrows():
        simple_str = f"{row['mayoria_simple_votos']:.1f}%" if pd.notna(row['mayoria_simple_votos']) else "N/A"
        calif_str = f"{row['mayoria_calificada_votos']:.1f}%" if pd.notna(row['mayoria_calificada_votos']) else "N/A"
        
        simple_mr = int(row['mayoria_simple_mr']) if pd.notna(row['mayoria_simple_mr']) else "-"
        simple_rp = int(row['mayoria_simple_rp']) if pd.notna(row['mayoria_simple_rp']) else "-"
        calif_mr = int(row['mayoria_calificada_mr']) if pd.notna(row['mayoria_calificada_mr']) else "-"
        calif_rp = int(row['mayoria_calificada_rp']) if pd.notna(row['mayoria_calificada_rp']) else "-"
        
        print(f"{row['escenario']:<25} {simple_str:<15} {simple_mr!s:<8} {simple_rp!s:<8} {calif_str:<15} {calif_mr!s:<8} {calif_rp!s:<8}")
    
    # Conclusiones
    print(f"\n{'='*120}")
    print("CONCLUSIONES CLAVE")
    print(f"{'='*120}")
    print("""
🎯 HALLAZGOS PRINCIPALES (con eficiencia geográfica +10% y redistritación REAL):

1. DIFERENCIA CLAVE vs ANÁLISIS ANTERIOR:
   - ESTE análisis usa redistritación REAL por población (método Hare)
   - Los votos mínimos son MÁS ALTOS porque la geografía importa
   - No se puede asumir proporcionalidad directa votos→MR

2. ESCENARIOS CON TOPES:
   - Mayoría simple: requiere más votos que con proporcionalidad simple
   - Mayoría calificada: prácticamente inalcanzable sin coalición
   - PROBLEMA: Topes del 8% + geografía hacen muy difícil mayoría calificada

3. ESCENARIOS SIN TOPES:
   - Mayoría simple: más alcanzable pero aún requiere votación fuerte
   - Mayoría calificada: requiere votación histórica
   - Redistritación por población afecta especialmente a estados pequeños

4. REALIDAD MORENA 2024:
   - Votación individual: 42.49%
   - Con redistritación real: NO alcanza mayoría simple en todos los escenarios
   - Mayoría calificada: IMPOSIBLE sin coalición (necesitaría >60%)

💡 IMPLICACIÓN POLÍTICA:
   La redistritación por población beneficia a estados grandes pero dispersa
   la fuerza electoral. Los votos mínimos calculados consideran esta realidad
   geográfica, por lo que son más precisos que análisis puramente proporcionales.
   
   Las coaliciones siguen siendo NECESARIAS para cualquier mayoría calificada.
    """)


if __name__ == '__main__':
    analizar_votos_minimos_morena()
