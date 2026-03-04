"""
Simulación de Escenario Electoral: 300 MR + 100 PM + 100 RP

Este script simula un escenario electoral con:
- 300 escaños de Mayoría Relativa pura (ganador por coalición)
- 100 escaños de Primera Minoría (segundo lugar por coalición)
- 100 escaños de Representación Proporcional

La primera minoría se calcula POR COALICIÓN, no por partido individual.

Años: 2021 y 2024
Coaliciones:
- SHH (Sigamos Haciendo Historia): MORENA + PT + PVEM
- FCM (Fuerza y Corazón por México): PAN + PRI + PRD
- MC (Movimiento Ciudadano): va solo
"""

import pandas as pd
from collections import Counter
from datetime import datetime

# Definir coaliciones
SHH = ['MORENA', 'PT', 'PVEM']  # Sigamos Haciendo Historia
FCM = ['PAN', 'PRI', 'PRD']     # Fuerza y Corazón por México
MC_PARTIDOS = ['MC']             # Movimiento Ciudadano

def calcular_votos_coalicion(row, partidos):
    """Calcula la suma de votos de una coalición"""
    return sum(row.get(p, 0) for p in partidos)

def asignar_mayorias_y_minorias(df, num_mr=300, num_pm=100):
    """
    Asigna escaños de mayoría relativa y primera minoría por coalición.
    
    Args:
        df: DataFrame con datos de votación por distrito
        num_mr: Número de escaños de mayoría relativa (300)
        num_pm: Número de escaños de primera minoría (100)
    
    Returns:
        dict con conteos de escaños por coalición para MR y PM
    """
    resultados_mr = Counter()  # Escaños de mayoría relativa
    candidatos_pm = []  # Lista de (coalicion, margen, distrito_idx) para PM
    
    total_distritos = len(df)
    
    for idx, row in df.iterrows():
        # Calcular votos por coalición
        votos_shh = calcular_votos_coalicion(row, SHH)
        votos_fcm = calcular_votos_coalicion(row, FCM)
        votos_mc = calcular_votos_coalicion(row, MC_PARTIDOS)
        
        # Crear ranking de coaliciones
        coaliciones = [
            ('SHH', votos_shh),
            ('FCM', votos_fcm),
            ('MC', votos_mc)
        ]
        
        # Ordenar por votos (de mayor a menor)
        coaliciones_ordenadas = sorted(coaliciones, key=lambda x: x[1], reverse=True)
        
        # Primer lugar = Mayoría Relativa (siempre asignado)
        ganador = coaliciones_ordenadas[0][0]
        resultados_mr[ganador] += 1
        
        # Segundo lugar = Candidato a Primera Minoría
        if len(coaliciones_ordenadas) > 1:
            segundo_lugar = coaliciones_ordenadas[1][0]
            votos_segundo = coaliciones_ordenadas[1][1]
            votos_primero = coaliciones_ordenadas[0][1]
            
            # El margen indica qué tan competitivo fue
            # Cuanto menor el margen, más competitivo
            margen = votos_primero - votos_segundo
            
            # Guardar como candidato a PM
            candidatos_pm.append((segundo_lugar, margen, idx))
    
    # Ordenar candidatos PM por margen (menor margen = más competitivo = prioridad)
    # Esto asigna PM a los distritos más competitivos
    candidatos_pm.sort(key=lambda x: x[1])
    
    # Asignar los primeros num_pm (100) escaños de PM
    resultados_pm = Counter()
    for i in range(min(num_pm, len(candidatos_pm))):
        coalicion, margen, distrito_idx = candidatos_pm[i]
        resultados_pm[coalicion] += 1
    
    return {
        'mr': dict(resultados_mr),
        'pm': dict(resultados_pm),
        'total_distritos': total_distritos,
        'distritos_pm': len(resultados_pm)
    }

def calcular_rp_proporcional(df, num_rp=100):
    """
    Calcula escaños de representación proporcional usando método Hare.
    
    Args:
        df: DataFrame con datos de votación
        num_rp: Número de escaños de RP a distribuir (100)
    
    Returns:
        dict con escaños de RP por coalición
    """
    # Calcular votos totales por coalición a nivel nacional
    votos_shh = df[SHH].sum().sum()
    votos_fcm = df[FCM].sum().sum()
    votos_mc = df[MC_PARTIDOS].sum().sum()
    
    total_votos = votos_shh + votos_fcm + votos_mc
    
    # Calcular cociente (votos / escaños)
    cociente = total_votos / num_rp
    
    # Distribución inicial por cociente
    escanos_iniciales = {
        'SHH': int(votos_shh / cociente),
        'FCM': int(votos_fcm / cociente),
        'MC': int(votos_mc / cociente)
    }
    
    escanos_asignados = sum(escanos_iniciales.values())
    escanos_restantes = num_rp - escanos_asignados
    
    # Calcular residuos para distribuir escaños restantes
    residuos = {
        'SHH': (votos_shh / cociente) - escanos_iniciales['SHH'],
        'FCM': (votos_fcm / cociente) - escanos_iniciales['FCM'],
        'MC': (votos_mc / cociente) - escanos_iniciales['MC']
    }
    
    # Asignar escaños restantes a los mayores residuos
    escanos_finales = escanos_iniciales.copy()
    for _ in range(escanos_restantes):
        coalicion_max_residuo = max(residuos, key=residuos.get)
        escanos_finales[coalicion_max_residuo] += 1
        residuos[coalicion_max_residuo] = 0  # Ya asignado, quitar del pool
    
    return {
        'rp': escanos_finales,
        'votos_totales': {
            'SHH': votos_shh,
            'FCM': votos_fcm,
            'MC': votos_mc
        }
    }

def simular_escenario(anio, num_mr=300, num_pm=100, num_rp=100):
    """
    Simula el escenario completo para un año dado.
    
    Args:
        anio: Año electoral (2021 o 2024)
        num_mr: Escaños de mayoría relativa (300)
        num_pm: Escaños de primera minoría (100)
        num_rp: Escaños de representación proporcional (100)
    
    Returns:
        dict con resultados detallados
    """
    print(f"\n{'='*80}")
    print(f"SIMULACIÓN ESCENARIO {anio}")
    print(f"{'='*80}")
    print(f"Configuración:")
    print(f"  • Mayoría Relativa (MR): {num_mr} escaños")
    print(f"  • Primera Minoría (PM): {num_pm} escaños")
    print(f"  • Representación Proporcional (RP): {num_rp} escaños")
    print(f"  • TOTAL: {num_mr + num_pm + num_rp} escaños")
    print(f"{'='*80}")
    
    # Cargar datos
    path_parquet = f'data/computos_diputados_{anio}.parquet'
    df = pd.read_parquet(path_parquet)
    
    print(f"\nDatos cargados: {len(df)} distritos")
    
    # Asignar MR y PM
    print(f"\n📊 Calculando Mayoría Relativa y Primera Minoría por coalición...")
    resultados_mr_pm = asignar_mayorias_y_minorias(df, num_mr, num_pm)
    
    # Calcular RP
    print(f"\n📊 Calculando Representación Proporcional...")
    resultados_rp = calcular_rp_proporcional(df, num_rp)
    
    # Consolidar resultados
    resultados_totales = {}
    
    for coalicion in ['SHH', 'FCM', 'MC']:
        mr = resultados_mr_pm['mr'].get(coalicion, 0)
        pm = resultados_mr_pm['pm'].get(coalicion, 0)
        rp = resultados_rp['rp'].get(coalicion, 0)
        total = mr + pm + rp
        
        resultados_totales[coalicion] = {
            'MR': mr,
            'PM': pm,
            'RP': rp,
            'Total': total
        }
    
    # Mostrar resultados
    print(f"\n{'='*80}")
    print(f"RESULTADOS - AÑO {anio}")
    print(f"{'='*80}")
    
    total_escanos = num_mr + num_pm + num_rp
    
    tabla = []
    for coalicion in ['SHH', 'FCM', 'MC']:
        r = resultados_totales[coalicion]
        pct = (r['Total'] / total_escanos) * 100
        
        tabla.append([
            coalicion,
            r['MR'],
            r['PM'],
            r['RP'],
            r['Total'],
            f"{pct:.2f}%"
        ])
        
        print(f"\n{coalicion}:")
        print(f"  MR: {r['MR']:3d} escaños")
        print(f"  PM: {r['PM']:3d} escaños")
        print(f"  RP: {r['RP']:3d} escaños")
        print(f"  ───────────────")
        print(f"  TOTAL: {r['Total']:3d} escaños ({pct:.2f}%)")
    
    # Verificación
    total_mr_asignado = sum(r['MR'] for r in resultados_totales.values())
    total_pm_asignado = sum(r['PM'] for r in resultados_totales.values())
    total_rp_asignado = sum(r['RP'] for r in resultados_totales.values())
    total_asignado = sum(r['Total'] for r in resultados_totales.values())
    
    print(f"\n{'='*80}")
    print(f"VERIFICACIÓN:")
    print(f"{'='*80}")
    print(f"  MR asignados: {total_mr_asignado}/{num_mr}")
    print(f"  PM asignados: {total_pm_asignado}/{num_pm}")
    print(f"  RP asignados: {total_rp_asignado}/{num_rp}")
    print(f"  TOTAL: {total_asignado}/{total_escanos}")
    
    if total_asignado == total_escanos:
        print(f"  ✅ Todos los escaños asignados correctamente")
    else:
        print(f"  ⚠️  ADVERTENCIA: Discrepancia en asignación de escaños")
    
    return {
        'anio': anio,
        'resultados': resultados_totales,
        'config': {
            'MR': num_mr,
            'PM': num_pm,
            'RP': num_rp,
            'Total': total_escanos
        }
    }

def generar_csv_comparativo(resultados_2021, resultados_2024):
    """
    Genera CSV comparativo con resultados de ambos años.
    """
    print(f"\n{'='*80}")
    print(f"GENERANDO CSV COMPARATIVO")
    print(f"{'='*80}")
    
    # Preparar datos para CSV
    datos = []
    
    for anio, resultados in [(2021, resultados_2021), (2024, resultados_2024)]:
        total_escanos = resultados['config']['Total']
        
        for coalicion in ['SHH', 'FCM', 'MC']:
            r = resultados['resultados'][coalicion]
            pct = (r['Total'] / total_escanos) * 100
            
            datos.append({
                'Año': anio,
                'Coalición': coalicion,
                'MR_Escaños': r['MR'],
                'PM_Escaños': r['PM'],
                'RP_Escaños': r['RP'],
                'Total_Escaños': r['Total'],
                'Porcentaje': round(pct, 2)
            })
    
    # Crear DataFrame
    df = pd.DataFrame(datos)
    
    # Guardar CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"simulacion_300mr_100pm_100rp_{timestamp}.csv"
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ CSV guardado: {filename}")
    
    # Mostrar preview
    print(f"\nPreview del CSV:")
    print(df.to_string(index=False))
    
    return filename

def main():
    """
    Ejecuta la simulación para ambos años y genera el CSV.
    """
    print("="*80)
    print("SIMULACIÓN: 300 MR + 100 PM + 100 RP")
    print("Primera Minoría por COALICIÓN")
    print("="*80)
    
    # Simular para 2021
    resultados_2021 = simular_escenario(2021, num_mr=300, num_pm=100, num_rp=100)
    
    # Simular para 2024
    resultados_2024 = simular_escenario(2024, num_mr=300, num_pm=100, num_rp=100)
    
    # Generar CSV comparativo
    filename = generar_csv_comparativo(resultados_2021, resultados_2024)
    
    # Resumen final
    print(f"\n{'='*80}")
    print(f"RESUMEN COMPARATIVO 2021 vs 2024")
    print(f"{'='*80}")
    
    for coalicion in ['SHH', 'FCM', 'MC']:
        r2021 = resultados_2021['resultados'][coalicion]
        r2024 = resultados_2024['resultados'][coalicion]
        
        diff_total = r2024['Total'] - r2021['Total']
        diff_mr = r2024['MR'] - r2021['MR']
        diff_pm = r2024['PM'] - r2021['PM']
        diff_rp = r2024['RP'] - r2021['RP']
        
        print(f"\n{coalicion}:")
        print(f"  2021: {r2021['Total']} escaños (MR:{r2021['MR']} PM:{r2021['PM']} RP:{r2021['RP']})")
        print(f"  2024: {r2024['Total']} escaños (MR:{r2024['MR']} PM:{r2024['PM']} RP:{r2024['RP']})")
        print(f"  Diferencia: {diff_total:+d} escaños (MR:{diff_mr:+d} PM:{diff_pm:+d} RP:{diff_rp:+d})")
    
    print(f"\n{'='*80}")
    print(f"✅ Simulación completada")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
