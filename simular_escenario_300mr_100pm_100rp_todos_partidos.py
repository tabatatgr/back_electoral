"""
Simulación COMPLETA con Desglose por Partido: 300 MR + 100 PM + 100 RP

Este script incluye TODOS los partidos que tuvieron votos, no solo las coaliciones.

IMPORTANTE: Incluye partidos menores como PES, RSP, FXM, y CI (independientes)
que en 2021 tuvieron votos significativos y en algunos casos quedaron en segundo lugar.

Partidos incluidos:
- Coaliciones principales: MORENA, PT, PVEM (SHH), PAN, PRI, PRD (FCM), MC
- Partidos menores: PES, RSP, FXM, CI (Candidatos Independientes)

Metodología:
- MR: Partido que ganó cada distrito (cualquier partido)
- PM: Partido que quedó segundo en los 100 distritos más competitivos (cualquier partido)
- RP: Distribuido solo entre partidos que cumplan umbral nacional (normalmente 3%)

Los totales por coalición deben seguir coincidiendo con la simulación original.
"""

import pandas as pd
from collections import Counter, defaultdict
from datetime import datetime

# Definir coaliciones principales
SHH = ['MORENA', 'PT', 'PVEM']
FCM = ['PAN', 'PRI', 'PRD']
MC_PARTIDOS = ['MC']

# Partidos menores que pueden aparecer
PARTIDOS_MENORES = ['PES', 'RSP', 'FXM', 'CI', 'NA']

# Todos los partidos posibles
TODOS_PARTIDOS_POSIBLES = SHH + FCM + MC_PARTIDOS + PARTIDOS_MENORES

# Mapeo de partido a coalición (solo para coaliciones)
PARTIDO_A_COALICION = {}
for p in SHH:
    PARTIDO_A_COALICION[p] = 'SHH'
for p in FCM:
    PARTIDO_A_COALICION[p] = 'FCM'
for p in MC_PARTIDOS:
    PARTIDO_A_COALICION[p] = 'MC'
# Partidos menores no tienen coalición
for p in PARTIDOS_MENORES:
    PARTIDO_A_COALICION[p] = 'Independiente'

def detectar_partidos_con_votos(df):
    """
    Detecta qué partidos tienen votos en el DataFrame.
    """
    partidos_con_votos = []
    for partido in TODOS_PARTIDOS_POSIBLES:
        if partido in df.columns:
            total_votos = df[partido].sum()
            if total_votos > 0:
                partidos_con_votos.append(partido)
    return partidos_con_votos

def calcular_votos_coalicion(row, partidos):
    """Calcula la suma de votos de una coalición"""
    return sum(row.get(p, 0) for p in partidos)

def asignar_mayorias_y_minorias_todos_partidos(df, num_mr=300, num_pm=100):
    """
    Asigna escaños de MR y PM considerando TODOS los partidos.
    
    Returns:
        dict con resultados por partido y por coalición
    """
    # Detectar partidos activos
    partidos_activos = detectar_partidos_con_votos(df)
    
    resultados_mr_partido = Counter()
    resultados_mr_coalicion = Counter()
    
    candidatos_pm = []  # (partido, coalicion, margen, distrito_idx)
    
    for idx, row in df.iterrows():
        # Ranking de TODOS los partidos por votos
        votos_por_partido = []
        for partido in partidos_activos:
            votos = row.get(partido, 0)
            coalicion = PARTIDO_A_COALICION.get(partido, 'Independiente')
            votos_por_partido.append((partido, votos, coalicion))
        
        # Ordenar por votos
        votos_por_partido.sort(key=lambda x: x[1], reverse=True)
        
        if len(votos_por_partido) == 0:
            continue
        
        # Primer lugar = MR
        partido_ganador, votos_ganador, coalicion_ganador = votos_por_partido[0]
        resultados_mr_partido[partido_ganador] += 1
        if coalicion_ganador != 'Independiente':
            resultados_mr_coalicion[coalicion_ganador] += 1
        
        # Segundo lugar = candidato a PM
        if len(votos_por_partido) > 1:
            partido_segundo, votos_segundo, coalicion_segundo = votos_por_partido[1]
            
            # Margen para competitividad
            margen = votos_ganador - votos_segundo
            
            # Guardar candidato a PM (cualquier partido puede ser segunda)
            candidatos_pm.append((partido_segundo, coalicion_segundo, margen, idx))
    
    # Ordenar por margen (menor = más competitivo)
    candidatos_pm.sort(key=lambda x: x[2])
    
    # Asignar PM a los primeros num_pm más competitivos
    resultados_pm_partido = Counter()
    resultados_pm_coalicion = Counter()
    
    for i in range(min(num_pm, len(candidatos_pm))):
        partido, coalicion, margen, distrito_idx = candidatos_pm[i]
        resultados_pm_partido[partido] += 1
        if coalicion != 'Independiente':
            resultados_pm_coalicion[coalicion] += 1
    
    return {
        'partidos_activos': partidos_activos,
        'mr_partido': dict(resultados_mr_partido),
        'mr_coalicion': dict(resultados_mr_coalicion),
        'pm_partido': dict(resultados_pm_partido),
        'pm_coalicion': dict(resultados_pm_coalicion)
    }

def calcular_rp_todos_partidos(df, num_rp=100, umbral_porcentaje=3.0):
    """
    Distribuye RP entre partidos que superan umbral nacional.
    
    En la realidad, solo partidos con 3%+ de votos nacionales reciben RP.
    """
    partidos_activos = detectar_partidos_con_votos(df)
    
    # Calcular votos totales por partido
    votos_partido = {}
    for partido in partidos_activos:
        votos_partido[partido] = df[partido].sum()
    
    total_votos_validos = sum(votos_partido.values())
    
    # Determinar partidos que superan umbral
    partidos_con_umbral = {}
    for partido, votos in votos_partido.items():
        porcentaje = (votos / total_votos_validos) * 100
        if porcentaje >= umbral_porcentaje:
            partidos_con_umbral[partido] = votos
    
    if not partidos_con_umbral:
        # Caso extremo: ningún partido supera umbral
        return {
            'rp_partido': {p: 0 for p in partidos_activos},
            'rp_coalicion': {'SHH': 0, 'FCM': 0, 'MC': 0},
            'partidos_con_umbral': []
        }
    
    # Calcular RP con método Hare solo para partidos con umbral
    total_votos_umbral = sum(partidos_con_umbral.values())
    cociente = total_votos_umbral / num_rp
    
    # Distribución inicial
    rp_partido = {}
    for partido in partidos_activos:
        if partido in partidos_con_umbral:
            rp_partido[partido] = int(partidos_con_umbral[partido] / cociente)
        else:
            rp_partido[partido] = 0
    
    # Calcular residuos
    residuos = {}
    for partido, votos in partidos_con_umbral.items():
        residuos[partido] = (votos / cociente) - rp_partido[partido]
    
    # Asignar escaños restantes
    escanos_asignados = sum(rp_partido.values())
    escanos_restantes = num_rp - escanos_asignados
    
    residuos_ordenados = sorted(residuos.items(), key=lambda x: x[1], reverse=True)
    for i in range(min(escanos_restantes, len(residuos_ordenados))):
        partido = residuos_ordenados[i][0]
        rp_partido[partido] += 1
    
    # Calcular RP por coalición
    rp_coalicion = {'SHH': 0, 'FCM': 0, 'MC': 0}
    for partido, escanos in rp_partido.items():
        coalicion = PARTIDO_A_COALICION.get(partido, 'Independiente')
        if coalicion in rp_coalicion:
            rp_coalicion[coalicion] += escanos
    
    return {
        'rp_partido': rp_partido,
        'rp_coalicion': rp_coalicion,
        'partidos_con_umbral': list(partidos_con_umbral.keys())
    }

def simular_completo_todos_partidos(anio, num_mr=300, num_pm=100, num_rp=100):
    """
    Simula el escenario completo incluyendo TODOS los partidos.
    """
    print(f"\n{'='*80}")
    print(f"SIMULACIÓN COMPLETA CON TODOS LOS PARTIDOS - AÑO {anio}")
    print(f"{'='*80}")
    
    # Cargar datos
    path_parquet = f'data/computos_diputados_{anio}.parquet'
    df = pd.read_parquet(path_parquet)
    
    # Detectar partidos activos
    partidos_activos = detectar_partidos_con_votos(df)
    
    print(f"\nPartidos con votos en {anio}: {', '.join(partidos_activos)}")
    print(f"Total de distritos: {len(df)}")
    
    # Calcular MR y PM
    print(f"\n📊 Calculando MR y PM para todos los partidos...")
    resultados_mr_pm = asignar_mayorias_y_minorias_todos_partidos(df, num_mr, num_pm)
    
    # Calcular RP
    print(f"📊 Calculando RP (umbral 3%)...")
    resultados_rp = calcular_rp_todos_partidos(df, num_rp, umbral_porcentaje=3.0)
    
    print(f"   Partidos que superan umbral 3%: {', '.join(resultados_rp['partidos_con_umbral'])}")
    
    # Consolidar resultados por partido
    resultados_partido = {}
    total_escanos = num_mr + num_pm + num_rp
    
    for partido in partidos_activos:
        mr = resultados_mr_pm['mr_partido'].get(partido, 0)
        pm = resultados_mr_pm['pm_partido'].get(partido, 0)
        rp = resultados_rp['rp_partido'].get(partido, 0)
        total = mr + pm + rp
        
        coalicion = PARTIDO_A_COALICION.get(partido, 'Independiente')
        
        resultados_partido[partido] = {
            'MR': mr,
            'PM': pm,
            'RP': rp,
            'Total': total,
            'Coalicion': coalicion,
            'Porcentaje': (total / total_escanos) * 100
        }
    
    # Consolidar por coalición
    resultados_coalicion = {}
    for coalicion_nombre in ['SHH', 'FCM', 'MC']:
        mr = resultados_mr_pm['mr_coalicion'].get(coalicion_nombre, 0)
        pm = resultados_mr_pm['pm_coalicion'].get(coalicion_nombre, 0)
        rp = resultados_rp['rp_coalicion'].get(coalicion_nombre, 0)
        total = mr + pm + rp
        
        resultados_coalicion[coalicion_nombre] = {
            'MR': mr,
            'PM': pm,
            'RP': rp,
            'Total': total
        }
    
    # Mostrar resultados
    print(f"\n{'='*80}")
    print(f"RESULTADOS POR PARTIDO - AÑO {anio}")
    print(f"{'='*80}")
    
    # Agrupar por coalición
    for coalicion in ['SHH', 'FCM', 'MC', 'Independiente']:
        partidos_en_coalicion = [p for p in partidos_activos 
                                 if PARTIDO_A_COALICION.get(p, 'Independiente') == coalicion]
        
        if not partidos_en_coalicion:
            continue
        
        print(f"\n{coalicion}:")
        
        for partido in partidos_en_coalicion:
            r = resultados_partido[partido]
            if r['Total'] > 0 or r['MR'] > 0 or r['PM'] > 0:  # Solo mostrar si tiene algo
                pct = r['Porcentaje']
                print(f"  {partido:6s}: MR={r['MR']:3d}  PM={r['PM']:3d}  RP={r['RP']:3d}  →  Total={r['Total']:3d} ({pct:5.2f}%)")
        
        # Subtotal de coalición (solo para SHH, FCM, MC)
        if coalicion in resultados_coalicion:
            rc = resultados_coalicion[coalicion]
            pct_coal = (rc['Total'] / total_escanos) * 100
            print(f"  {'─'*70}")
            print(f"  TOTAL {coalicion}: MR={rc['MR']:3d}  PM={rc['PM']:3d}  RP={rc['RP']:3d}  →  {rc['Total']:3d} ({pct_coal:5.2f}%)")
    
    # Verificación
    print(f"\n{'='*80}")
    print(f"VERIFICACIÓN:")
    print(f"{'='*80}")
    
    total_mr_partido = sum(resultados_partido[p]['MR'] for p in partidos_activos)
    total_pm_partido = sum(resultados_partido[p]['PM'] for p in partidos_activos)
    total_rp_partido = sum(resultados_partido[p]['RP'] for p in partidos_activos)
    total_general = sum(resultados_partido[p]['Total'] for p in partidos_activos)
    
    print(f"  MR asignados: {total_mr_partido}/{num_mr}")
    print(f"  PM asignados: {total_pm_partido}/{num_pm}")
    print(f"  RP asignados: {total_rp_partido}/{num_rp}")
    print(f"  TOTAL: {total_general}/{total_escanos}")
    
    if total_general == total_escanos:
        print(f"  ✅ Todos los escaños asignados correctamente")
    else:
        print(f"  ⚠️  ADVERTENCIA: Discrepancia en asignación")
    
    # Validar coaliciones
    print(f"\n{'='*80}")
    print(f"VALIDACIÓN DE TOTALES POR COALICIÓN:")
    print(f"{'='*80}")
    
    for coalicion in ['SHH', 'FCM', 'MC']:
        rc = resultados_coalicion[coalicion]
        print(f"  {coalicion}: {rc['Total']} escaños (MR:{rc['MR']} PM:{rc['PM']} RP:{rc['RP']})")
    
    return {
        'anio': anio,
        'partidos_activos': partidos_activos,
        'resultados_partido': resultados_partido,
        'resultados_coalicion': resultados_coalicion,
        'config': {
            'MR': num_mr,
            'PM': num_pm,
            'RP': num_rp,
            'Total': total_escanos
        }
    }

def generar_csv_completo(resultados_2021, resultados_2024):
    """
    Genera CSV con TODOS los partidos.
    """
    print(f"\n{'='*80}")
    print(f"GENERANDO CSV CON TODOS LOS PARTIDOS")
    print(f"{'='*80}")
    
    datos = []
    
    # Combinar partidos de ambos años
    todos_partidos_ambos_anos = set(resultados_2021['partidos_activos'] + resultados_2024['partidos_activos'])
    
    for anio, resultados in [(2021, resultados_2021), (2024, resultados_2024)]:
        for partido in sorted(todos_partidos_ambos_anos):
            if partido in resultados['resultados_partido']:
                r = resultados['resultados_partido'][partido]
                coalicion = r['Coalicion']
                
                datos.append({
                    'Año': anio,
                    'Coalición': coalicion,
                    'Partido': partido,
                    'MR_Escaños': r['MR'],
                    'PM_Escaños': r['PM'],
                    'RP_Escaños': r['RP'],
                    'Total_Escaños': r['Total'],
                    'Porcentaje': round(r['Porcentaje'], 2)
                })
            else:
                # Partido no existía en este año
                coalicion = PARTIDO_A_COALICION.get(partido, 'Independiente')
                datos.append({
                    'Año': anio,
                    'Coalición': coalicion,
                    'Partido': partido,
                    'MR_Escaños': 0,
                    'PM_Escaños': 0,
                    'RP_Escaños': 0,
                    'Total_Escaños': 0,
                    'Porcentaje': 0.0
                })
    
    df = pd.DataFrame(datos)
    
    # Ordenar por año, coalición, y total (descendente)
    df = df.sort_values(['Año', 'Coalición', 'Total_Escaños'], ascending=[True, True, False])
    
    # Guardar CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"simulacion_300mr_100pm_100rp_todos_partidos_{timestamp}.csv"
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ CSV guardado: {filename}")
    
    # Mostrar preview
    print(f"\nPreview del CSV:")
    print(df.to_string(index=False))
    
    return filename

def main():
    """
    Ejecuta la simulación completa para ambos años.
    """
    print("="*80)
    print("SIMULACIÓN COMPLETA: 300 MR + 100 PM + 100 RP")
    print("INCLUYE TODOS LOS PARTIDOS (PES, RSP, FXM, CI, etc.)")
    print("="*80)
    
    # Simular para 2021
    resultados_2021 = simular_completo_todos_partidos(2021, num_mr=300, num_pm=100, num_rp=100)
    
    # Simular para 2024
    resultados_2024 = simular_completo_todos_partidos(2024, num_mr=300, num_pm=100, num_rp=100)
    
    # Generar CSV
    filename = generar_csv_completo(resultados_2021, resultados_2024)
    
    # Resumen
    print(f"\n{'='*80}")
    print(f"RESUMEN COMPARATIVO 2021 vs 2024 (POR COALICIÓN)")
    print(f"{'='*80}")
    
    for coalicion in ['SHH', 'FCM', 'MC']:
        r2021 = resultados_2021['resultados_coalicion'][coalicion]
        r2024 = resultados_2024['resultados_coalicion'][coalicion]
        
        diff = r2024['Total'] - r2021['Total']
        
        print(f"\n{coalicion}:")
        print(f"  2021: {r2021['Total']} escaños")
        print(f"  2024: {r2024['Total']} escaños")
        print(f"  Diferencia: {diff:+d} escaños")
    
    print(f"\n{'='*80}")
    print(f"✅ Simulación completa con todos los partidos finalizada")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
