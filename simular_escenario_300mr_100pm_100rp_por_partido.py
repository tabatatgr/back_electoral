"""
Simulación con Desglose por Partido: 300 MR + 100 PM + 100 RP

Este script desglosa la simulación anterior a nivel PARTIDO INDIVIDUAL,
pero manteniendo los mismos totales por coalición.

La diferencia clave:
- MR: Se asigna al partido específico que ganó cada distrito
- PM: Se asigna al partido específico que quedó segundo en distritos competitivos  
- RP: Se distribuye proporcionalmente dentro de cada coalición según votos del partido

Coaliciones:
- SHH (Sigamos Haciendo Historia): MORENA + PT + PVEM
- FCM (Fuerza y Corazón por México): PAN + PRI + PRD
- MC (Movimiento Ciudadano): va solo

Los totales por coalición deben coincidir con la simulación original.
"""

import pandas as pd
from collections import Counter, defaultdict
from datetime import datetime

# Definir coaliciones y partidos
SHH = ['MORENA', 'PT', 'PVEM']
FCM = ['PAN', 'PRI', 'PRD']
MC_PARTIDOS = ['MC']

TODOS_PARTIDOS = SHH + FCM + MC_PARTIDOS

# Mapeo de partido a coalición
PARTIDO_A_COALICION = {}
for p in SHH:
    PARTIDO_A_COALICION[p] = 'SHH'
for p in FCM:
    PARTIDO_A_COALICION[p] = 'FCM'
for p in MC_PARTIDOS:
    PARTIDO_A_COALICION[p] = 'MC'

def calcular_votos_coalicion(row, partidos):
    """Calcula la suma de votos de una coalición"""
    return sum(row.get(p, 0) for p in partidos)

def asignar_mayorias_y_minorias_por_partido(df, num_mr=300, num_pm=100):
    """
    Asigna escaños de MR y PM por PARTIDO INDIVIDUAL.
    
    Returns:
        dict con resultados por partido y por coalición para validación
    """
    resultados_mr_partido = Counter()  # MR por partido
    resultados_mr_coalicion = Counter()  # MR por coalición (para validar)
    
    candidatos_pm = []  # Lista de (partido, coalicion, margen, distrito_idx)
    
    for idx, row in df.iterrows():
        # Calcular votos por coalición
        votos_shh = calcular_votos_coalicion(row, SHH)
        votos_fcm = calcular_votos_coalicion(row, FCM)
        votos_mc = calcular_votos_coalicion(row, MC_PARTIDOS)
        
        # Ranking de coaliciones para determinar ganador
        coaliciones = [
            ('SHH', votos_shh),
            ('FCM', votos_fcm),
            ('MC', votos_mc)
        ]
        coaliciones_ordenadas = sorted(coaliciones, key=lambda x: x[1], reverse=True)
        coalicion_ganadora = coaliciones_ordenadas[0][0]
        coalicion_segunda = coaliciones_ordenadas[1][0] if len(coaliciones_ordenadas) > 1 else None
        
        # Determinar el PARTIDO ganador dentro de la coalición ganadora
        if coalicion_ganadora == 'SHH':
            partidos_ganadores = SHH
        elif coalicion_ganadora == 'FCM':
            partidos_ganadores = FCM
        else:
            partidos_ganadores = MC_PARTIDOS
        
        # Encontrar el partido con más votos en la coalición ganadora
        max_votos = -1
        partido_ganador = None
        for partido in partidos_ganadores:
            votos = row.get(partido, 0)
            if votos > max_votos:
                max_votos = votos
                partido_ganador = partido
        
        # Asignar MR al partido ganador
        resultados_mr_partido[partido_ganador] += 1
        resultados_mr_coalicion[coalicion_ganadora] += 1
        
        # Para PM: encontrar el partido con más votos en la coalición que quedó segunda
        if coalicion_segunda:
            if coalicion_segunda == 'SHH':
                partidos_segunda = SHH
            elif coalicion_segunda == 'FCM':
                partidos_segunda = FCM
            else:
                partidos_segunda = MC_PARTIDOS
            
            # Encontrar el partido con más votos en la coalición segunda
            max_votos_segunda = -1
            partido_segundo = None
            for partido in partidos_segunda:
                votos = row.get(partido, 0)
                if votos > max_votos_segunda:
                    max_votos_segunda = votos
                    partido_segundo = partido
            
            # Calcular margen para competitividad
            votos_primero = coaliciones_ordenadas[0][1]
            votos_segundo = coaliciones_ordenadas[1][1]
            margen = votos_primero - votos_segundo
            
            # Guardar candidato a PM
            candidatos_pm.append((partido_segundo, coalicion_segunda, margen, idx))
    
    # Ordenar candidatos PM por margen (menor = más competitivo)
    candidatos_pm.sort(key=lambda x: x[2])
    
    # Asignar PM a los primeros num_pm distritos más competitivos
    resultados_pm_partido = Counter()
    resultados_pm_coalicion = Counter()
    
    for i in range(min(num_pm, len(candidatos_pm))):
        partido, coalicion, margen, distrito_idx = candidatos_pm[i]
        resultados_pm_partido[partido] += 1
        resultados_pm_coalicion[coalicion] += 1
    
    return {
        'mr_partido': dict(resultados_mr_partido),
        'mr_coalicion': dict(resultados_mr_coalicion),
        'pm_partido': dict(resultados_pm_partido),
        'pm_coalicion': dict(resultados_pm_coalicion)
    }

def calcular_rp_por_partido(df, num_rp=100):
    """
    Distribuye RP por partido dentro de cada coalición, proporcionalmente.
    
    Returns:
        dict con RP por partido y por coalición
    """
    # Calcular votos totales por partido
    votos_partido = {}
    for partido in TODOS_PARTIDOS:
        votos_partido[partido] = df[partido].sum()
    
    # Calcular votos totales por coalición
    votos_shh = sum(votos_partido[p] for p in SHH)
    votos_fcm = sum(votos_partido[p] for p in FCM)
    votos_mc = sum(votos_partido[p] for p in MC_PARTIDOS)
    
    total_votos = votos_shh + votos_fcm + votos_mc
    
    # Calcular cociente
    cociente = total_votos / num_rp
    
    # Distribución inicial por coalición
    rp_shh_inicial = int(votos_shh / cociente)
    rp_fcm_inicial = int(votos_fcm / cociente)
    rp_mc_inicial = int(votos_mc / cociente)
    
    # Calcular residuos
    residuos = {
        'SHH': (votos_shh / cociente) - rp_shh_inicial,
        'FCM': (votos_fcm / cociente) - rp_fcm_inicial,
        'MC': (votos_mc / cociente) - rp_mc_inicial
    }
    
    # Asignar escaños restantes a los mayores residuos
    rp_por_coalicion = {
        'SHH': rp_shh_inicial,
        'FCM': rp_fcm_inicial,
        'MC': rp_mc_inicial
    }
    
    escanos_asignados = sum(rp_por_coalicion.values())
    escanos_restantes = num_rp - escanos_asignados
    
    residuos_ordenados = sorted(residuos.items(), key=lambda x: x[1], reverse=True)
    for i in range(escanos_restantes):
        coalicion = residuos_ordenados[i][0]
        rp_por_coalicion[coalicion] += 1
    
    # Ahora distribuir RP de cada coalición entre sus partidos proporcionalmente
    rp_por_partido = {}
    
    # SHH
    rp_shh_total = rp_por_coalicion['SHH']
    if rp_shh_total > 0:
        cociente_shh = votos_shh / rp_shh_total
        rp_shh_partido = {}
        for partido in SHH:
            rp_shh_partido[partido] = int(votos_partido[partido] / cociente_shh)
        
        # Asignar residuos
        asignados = sum(rp_shh_partido.values())
        residuos_shh = {}
        for partido in SHH:
            residuos_shh[partido] = (votos_partido[partido] / cociente_shh) - rp_shh_partido[partido]
        
        residuos_shh_ordenados = sorted(residuos_shh.items(), key=lambda x: x[1], reverse=True)
        for i in range(rp_shh_total - asignados):
            partido = residuos_shh_ordenados[i][0]
            rp_shh_partido[partido] += 1
        
        rp_por_partido.update(rp_shh_partido)
    else:
        for partido in SHH:
            rp_por_partido[partido] = 0
    
    # FCM
    rp_fcm_total = rp_por_coalicion['FCM']
    if rp_fcm_total > 0:
        cociente_fcm = votos_fcm / rp_fcm_total
        rp_fcm_partido = {}
        for partido in FCM:
            rp_fcm_partido[partido] = int(votos_partido[partido] / cociente_fcm)
        
        # Asignar residuos
        asignados = sum(rp_fcm_partido.values())
        residuos_fcm = {}
        for partido in FCM:
            residuos_fcm[partido] = (votos_partido[partido] / cociente_fcm) - rp_fcm_partido[partido]
        
        residuos_fcm_ordenados = sorted(residuos_fcm.items(), key=lambda x: x[1], reverse=True)
        for i in range(rp_fcm_total - asignados):
            partido = residuos_fcm_ordenados[i][0]
            rp_fcm_partido[partido] += 1
        
        rp_por_partido.update(rp_fcm_partido)
    else:
        for partido in FCM:
            rp_por_partido[partido] = 0
    
    # MC
    rp_por_partido['MC'] = rp_por_coalicion['MC']
    
    return {
        'rp_partido': rp_por_partido,
        'rp_coalicion': rp_por_coalicion
    }

def simular_con_desglose_partido(anio, num_mr=300, num_pm=100, num_rp=100):
    """
    Simula el escenario completo con desglose por partido.
    """
    print(f"\n{'='*80}")
    print(f"SIMULACIÓN CON DESGLOSE POR PARTIDO - AÑO {anio}")
    print(f"{'='*80}")
    
    # Cargar datos
    path_parquet = f'data/computos_diputados_{anio}.parquet'
    df = pd.read_parquet(path_parquet)
    
    print(f"\nDatos cargados: {len(df)} distritos")
    
    # Calcular MR y PM por partido
    print(f"\n📊 Calculando MR y PM por partido...")
    resultados_mr_pm = asignar_mayorias_y_minorias_por_partido(df, num_mr, num_pm)
    
    # Calcular RP por partido
    print(f"📊 Calculando RP por partido...")
    resultados_rp = calcular_rp_por_partido(df, num_rp)
    
    # Consolidar resultados
    resultados_partido = {}
    resultados_coalicion = {}
    
    for partido in TODOS_PARTIDOS:
        mr = resultados_mr_pm['mr_partido'].get(partido, 0)
        pm = resultados_mr_pm['pm_partido'].get(partido, 0)
        rp = resultados_rp['rp_partido'].get(partido, 0)
        total = mr + pm + rp
        
        coalicion = PARTIDO_A_COALICION[partido]
        
        resultados_partido[partido] = {
            'MR': mr,
            'PM': pm,
            'RP': rp,
            'Total': total,
            'Coalicion': coalicion
        }
    
    # Consolidar por coalición
    for coalicion in ['SHH', 'FCM', 'MC']:
        mr = resultados_mr_pm['mr_coalicion'].get(coalicion, 0)
        pm = resultados_mr_pm['pm_coalicion'].get(coalicion, 0)
        rp = resultados_rp['rp_coalicion'].get(coalicion, 0)
        total = mr + pm + rp
        
        resultados_coalicion[coalicion] = {
            'MR': mr,
            'PM': pm,
            'RP': rp,
            'Total': total
        }
    
    # Mostrar resultados
    total_escanos = num_mr + num_pm + num_rp
    
    print(f"\n{'='*80}")
    print(f"RESULTADOS POR PARTIDO - AÑO {anio}")
    print(f"{'='*80}")
    
    for coalicion in ['SHH', 'FCM', 'MC']:
        print(f"\n{coalicion}:")
        if coalicion == 'SHH':
            partidos = SHH
        elif coalicion == 'FCM':
            partidos = FCM
        else:
            partidos = MC_PARTIDOS
        
        for partido in partidos:
            r = resultados_partido[partido]
            pct = (r['Total'] / total_escanos) * 100
            print(f"  {partido:6s}: MR={r['MR']:3d}  PM={r['PM']:3d}  RP={r['RP']:3d}  →  Total={r['Total']:3d} ({pct:5.2f}%)")
        
        # Subtotal de coalición
        rc = resultados_coalicion[coalicion]
        pct_coal = (rc['Total'] / total_escanos) * 100
        print(f"  {'─'*70}")
        print(f"  TOTAL {coalicion}: MR={rc['MR']:3d}  PM={rc['PM']:3d}  RP={rc['RP']:3d}  →  {rc['Total']:3d} ({pct_coal:5.2f}%)")
    
    # Verificación
    print(f"\n{'='*80}")
    print(f"VERIFICACIÓN:")
    print(f"{'='*80}")
    
    total_mr_partido = sum(r['MR'] for r in resultados_partido.values())
    total_pm_partido = sum(r['PM'] for r in resultados_partido.values())
    total_rp_partido = sum(r['RP'] for r in resultados_partido.values())
    total_general = sum(r['Total'] for r in resultados_partido.values())
    
    print(f"  MR asignados: {total_mr_partido}/{num_mr}")
    print(f"  PM asignados: {total_pm_partido}/{num_pm}")
    print(f"  RP asignados: {total_rp_partido}/{num_rp}")
    print(f"  TOTAL: {total_general}/{total_escanos}")
    
    if total_general == total_escanos:
        print(f"  ✅ Todos los escaños asignados correctamente")
    else:
        print(f"  ⚠️  ADVERTENCIA: Discrepancia en asignación")
    
    # Verificar que los totales por coalición coinciden
    print(f"\n{'='*80}")
    print(f"VALIDACIÓN DE TOTALES POR COALICIÓN:")
    print(f"{'='*80}")
    
    for coalicion in ['SHH', 'FCM', 'MC']:
        rc = resultados_coalicion[coalicion]
        print(f"  {coalicion}: {rc['Total']} escaños (MR:{rc['MR']} PM:{rc['PM']} RP:{rc['RP']})")
    
    return {
        'anio': anio,
        'resultados_partido': resultados_partido,
        'resultados_coalicion': resultados_coalicion,
        'config': {
            'MR': num_mr,
            'PM': num_pm,
            'RP': num_rp,
            'Total': total_escanos
        }
    }

def generar_csv_desglosado(resultados_2021, resultados_2024):
    """
    Genera CSV con desglose por partido para ambos años.
    """
    print(f"\n{'='*80}")
    print(f"GENERANDO CSV CON DESGLOSE POR PARTIDO")
    print(f"{'='*80}")
    
    datos = []
    
    for anio, resultados in [(2021, resultados_2021), (2024, resultados_2024)]:
        for partido in TODOS_PARTIDOS:
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
                'Porcentaje': round((r['Total'] / 500) * 100, 2)
            })
    
    df = pd.DataFrame(datos)
    
    # Guardar CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"simulacion_300mr_100pm_100rp_por_partido_{timestamp}.csv"
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ CSV guardado: {filename}")
    
    # Mostrar preview
    print(f"\nPreview del CSV:")
    print(df.to_string(index=False))
    
    return filename

def main():
    """
    Ejecuta la simulación con desglose por partido para ambos años.
    """
    print("="*80)
    print("SIMULACIÓN: 300 MR + 100 PM + 100 RP")
    print("DESGLOSE POR PARTIDO INDIVIDUAL")
    print("="*80)
    
    # Simular para 2021
    resultados_2021 = simular_con_desglose_partido(2021, num_mr=300, num_pm=100, num_rp=100)
    
    # Simular para 2024
    resultados_2024 = simular_con_desglose_partido(2024, num_mr=300, num_pm=100, num_rp=100)
    
    # Generar CSV
    filename = generar_csv_desglosado(resultados_2021, resultados_2024)
    
    # Resumen comparativo
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
    print(f"✅ Simulación con desglose por partido completada")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
