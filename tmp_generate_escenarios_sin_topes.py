"""
Script para generar escenarios de MORENA SIN aplicar topes constitucionales
(sin cláusula del 8% ni límite de 300 escaños)

Esto permite ver la distribución "pura" basada solo en los votos
"""
from engine.procesar_diputados_v2 import procesar_diputados_v2
from usar_swing import SwingElectoral
import pandas as pd
from datetime import datetime
import os
import math

# Configuraciones a probar
AÑOS = [2018, 2021, 2024]

# Cargar swing para 2021
try:
    swing = SwingElectoral()
    USAR_SWING_2021 = True
    print("[OK] Swing electoral 2021 cargado\n")
except Exception as e:
    print(f"[!] No se pudo cargar swing: {e}")
    print("[!] Los escenarios 2021_SWING no se generaran\n")
    USAR_SWING_2021 = False

ESCAÑOS_TOTALES = [400, 500, 600]
CONFIGURACIONES_MR_RP = [
    {'tipo': 'porcentaje', 'mr_pct': 0.50, 'nombre': '50MR_50RP'},
    {'tipo': 'porcentaje', 'mr_pct': 0.60, 'nombre': '60MR_40RP'},
    {'tipo': 'porcentaje', 'mr_pct': 0.75, 'nombre': '75MR_25RP'},
]
COALICIONES = [
    {'usar': True, 'nombre': 'CON'},
    {'usar': False, 'nombre': 'SIN'}
]

resultados = []

print("="*80)
print("GENERANDO ESCENARIOS SIN TOPES CONSTITUCIONALES")
print("="*80)
print("[!] ADVERTENCIA: Los resultados NO respetan el limite del 8% ni los 300 escaños")
print("   Esto es solo para analisis contrafactual\n")

total_escenarios = (len(AÑOS) + (1 if USAR_SWING_2021 else 0)) * len(ESCAÑOS_TOTALES) * len(CONFIGURACIONES_MR_RP) * len(COALICIONES)
contador = 0

# Procesar años normales
for anio in AÑOS:
    for escanos_totales in ESCAÑOS_TOTALES:
        for config_mr_rp in CONFIGURACIONES_MR_RP:
            for coalicion in COALICIONES:
                contador += 1
                
                print(f"\n[{contador}/{total_escenarios}] Procesando: {anio} | {escanos_totales} escaños | "
                      f"{config_mr_rp['nombre']} | {coalicion['nombre']} coalición")
                
                try:
                    # Calcular escaños MR y RP según porcentaje
                    mr_escanos = int(escanos_totales * config_mr_rp['mr_pct'])
                    rp_escanos = escanos_totales - mr_escanos
                    
                    # Paths a datos
                    path_parquet = f'data/computos_diputados_{anio}.parquet'
                    path_siglado = f'data/siglado-diputados-{anio}.csv'
                    
                    # Ejecutar procesamiento SIN topes
                    resultado = procesar_diputados_v2(
                        path_parquet=path_parquet,
                        path_siglado=path_siglado,  # Agregar siglado
                        anio=anio,
                        max_seats=escanos_totales,
                        mr_seats=mr_escanos,
                        rp_seats=rp_escanos,
                        usar_coaliciones=coalicion['usar'],
                        aplicar_topes=False  # ⚠️ DESACTIVAR TOPES
                    )
                    
                    # Extraer datos de MORENA
                    # procesar_diputados_v2 devuelve: {mr: {partido: escaños}, rp: {...}, tot: {...}}
                    if 'tot' not in resultado or 'mr' not in resultado or 'rp' not in resultado:
                        raise KeyError("Estructura de resultado inesperada")
                    
                    # Buscar MORENA en los diccionarios
                    if 'MORENA' not in resultado['tot']:
                        raise KeyError("MORENA no encontrado")
                    
                    morena_mr = resultado['mr'].get('MORENA', 0)
                    morena_rp = resultado['rp'].get('MORENA', 0)
                    morena_total = resultado['tot'].get('MORENA', 0)
                    
                    morena = {
                        'mr': morena_mr,
                        'rp': morena_rp,
                        'total': morena_total,
                        'partido': 'MORENA'
                    }
                    
                    # También extraer PT y PVEM para coalición
                    pt_total = resultado['tot'].get('PT', 0)
                    pvem_total = resultado['tot'].get('PVEM', 0)
                    
                    if morena:
                        # Calcular coalición total (MORENA + PT + PVEM)
                        total_coalicion = morena_total + pt_total + pvem_total
                        
                        # Calcular mayorías (4 columnas separadas)
                        # MORENA solo
                        mayoria_simple_morena = morena_total > (escanos_totales / 2)
                        umbral_calificada = math.ceil(escanos_totales * 2 / 3)
                        mayoria_calificada_morena = morena_total >= umbral_calificada
                        
                        # Coalición
                        mayoria_simple_coalicion = total_coalicion > (escanos_totales / 2)
                        mayoria_calificada_coalicion = total_coalicion >= umbral_calificada
                        
                        # Guardar resultado
                        resultados.append({
                            'anio': anio,
                            'escanos_totales': escanos_totales,
                            'config_mr_rp': config_mr_rp['nombre'],
                            'coalicion': coalicion['nombre'],
                            'morena_mr': morena['mr'],
                            'morena_rp': morena['rp'],
                            'morena_total': morena['total'],
                            'morena_pct': round(morena['total'] / escanos_totales * 100, 2),
                            'coalicion_total': total_coalicion,
                            'coalicion_pct': round(total_coalicion / escanos_totales * 100, 2),
                            'mayoria_simple_morena': mayoria_simple_morena,
                            'mayoria_calificada_morena': mayoria_calificada_morena,
                            'mayoria_simple_coalicion': mayoria_simple_coalicion,
                            'mayoria_calificada_coalicion': mayoria_calificada_coalicion
                        })
                        
                        print(f"   (+) MORENA: {morena['total']} escaños ({morena['total']/escanos_totales*100:.1f}%)")
                        print(f"   (+) Coalición: {total_coalicion} escaños ({total_coalicion/escanos_totales*100:.1f}%)")
                    else:
                        print(f"   (X) MORENA no encontrado en resultados")
                        
                except Exception as e:
                    print(f"   (X) Error: {e}")
                    import traceback
                    traceback.print_exc()

# Procesar 2021 CON SWING
if USAR_SWING_2021:
    print("\n" + "="*80)
    print("PROCESANDO 2021 CON SWING ELECTORAL (SIN TOPES)")
    print("="*80)
    
    df_votos_2021 = pd.read_parquet('data/computos_diputados_2021.parquet')
    
    for escanos_totales in ESCAÑOS_TOTALES:
        for config_mr_rp in CONFIGURACIONES_MR_RP:
            for coalicion in COALICIONES:
                contador += 1
                
                print(f"\n[{contador}/{total_escenarios}] Procesando: 2021_SWING | {escanos_totales} escaños | {config_mr_rp['nombre']} | {coalicion['nombre']} coalición")
                
                try:
                    mr_escanos = int(escanos_totales * config_mr_rp['mr_pct'])
                    rp_escanos = escanos_totales - mr_escanos
                    
                    # Aplicar swing
                    df_ajustado = df_votos_2021.copy()
                    distritos_ajustados = 0
                    
                    for idx, row in df_ajustado.iterrows():
                        # usar_swing.py acepta nombres de entidad directamente
                        entidad = row['ENTIDAD']  # Ya viene como nombre completo del estado
                        distrito = int(row['DISTRITO'])
                        
                        # Preparar votos 2021 originales
                        votos_2021 = {
                            'PAN': row.get('PAN', 0),
                            'PRI': row.get('PRI', 0),
                            'PRD': row.get('PRD', 0),
                            'PVEM': row.get('PVEM', 0),
                            'PT': row.get('PT', 0),
                            'MC': row.get('MC', 0),
                            'MORENA': row.get('MORENA', 0)
                        }
                        
                        # Aplicar swing
                        votos_ajustados = swing.ajustar_votos(
                            votos_2021=votos_2021,
                            entidad=entidad,
                            distrito=distrito,
                            usar_coaliciones=coalicion['usar']
                        )
                        
                        # Actualizar solo si hubo cambio
                        cambio = False
                        for partido, nuevo_voto in votos_ajustados.items():
                            if partido in df_ajustado.columns:
                                if abs(nuevo_voto - row.get(partido, 0)) > 0.01:
                                    cambio = True
                                df_ajustado.at[idx, partido] = nuevo_voto
                        
                        if cambio:
                            distritos_ajustados += 1
                    
                    temp_parquet = 'data/temp_2021_swing_sin_topes.parquet'
                    df_ajustado.to_parquet(temp_parquet)
                    
                    print(f"   (+) Swing aplicado a {distritos_ajustados} distritos")
                    
                    # Procesar SIN topes
                    resultado = procesar_diputados_v2(
                        path_parquet=temp_parquet,
                        path_siglado='data/siglado-diputados-2021.csv',
                        anio=2021,
                        max_seats=escanos_totales,
                        mr_seats=mr_escanos,
                        rp_seats=rp_escanos,
                        usar_coaliciones=coalicion['usar'],
                        aplicar_topes=False  # SIN TOPES
                    )
                    
                    if os.path.exists(temp_parquet):
                        os.remove(temp_parquet)
                    
                    if 'tot' in resultado and 'MORENA' in resultado['tot']:
                        morena = {
                            'mr': resultado['mr'].get('MORENA', 0),
                            'rp': resultado['rp'].get('MORENA', 0),
                            'total': resultado['tot'].get('MORENA', 0)
                        }
                        
                        coal_partidos = ['MORENA', 'PT', 'PVEM']
                        total_coalicion = sum(resultado['tot'].get(p, 0) for p in coal_partidos)
                        
                        # Calcular mayorías (4 columnas separadas)
                        # MORENA solo
                        mayoria_simple_morena = morena['total'] > (escanos_totales / 2)
                        umbral_calificada = math.ceil(escanos_totales * 2 / 3)
                        mayoria_calificada_morena = morena['total'] >= umbral_calificada
                        
                        # Coalición
                        mayoria_simple_coalicion = total_coalicion > (escanos_totales / 2)
                        mayoria_calificada_coalicion = total_coalicion >= umbral_calificada
                        
                        resultados.append({
                            'anio': '2021_SWING',
                            'escanos_totales': escanos_totales,
                            'config_mr_rp': config_mr_rp['nombre'],
                            'coalicion': coalicion['nombre'],
                            'morena_mr': morena['mr'],
                            'morena_rp': morena['rp'],
                            'morena_total': morena['total'],
                            'morena_pct': round(morena['total'] / escanos_totales * 100, 2),
                            'coalicion_total': total_coalicion,
                            'coalicion_pct': round(total_coalicion / escanos_totales * 100, 2),
                            'mayoria_simple_morena': mayoria_simple_morena,
                            'mayoria_calificada_morena': mayoria_calificada_morena,
                            'mayoria_simple_coalicion': mayoria_simple_coalicion,
                            'mayoria_calificada_coalicion': mayoria_calificada_coalicion
                        })
                        
                        print(f"   (+) MORENA: {morena['total']} escaños ({morena['total']/escanos_totales*100:.1f}%)")
                        print(f"   (+) Coalición: {total_coalicion} escaños ({total_coalicion/escanos_totales*100:.1f}%)")
                    
                except Exception as e:
                    print(f"   (X) Error: {e}")
                    import traceback
                    traceback.print_exc()

# Crear DataFrame
df = pd.DataFrame(resultados)

# Guardar CSV
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_file = f'outputs/escenarios_morena_SIN_TOPES_{timestamp}.csv'
os.makedirs('outputs', exist_ok=True)
df.to_csv(output_file, index=False, encoding='utf-8-sig')

print("\n" + "="*80)
print(f"(+) Escenarios generados: {len(resultados)}")
print(f"(+) Archivo guardado: {output_file}")
print("="*80)

# Mostrar resumen
print("\n📊 RESUMEN DE RESULTADOS SIN TOPES:\n")

# Agrupar por año y configuración
for anio in AÑOS:
    print(f"\n{'='*60}")
    print(f"AÑO {anio}")
    print(f"{'='*60}")
    
    df_anio = df[df['anio'] == anio]
    
    for escanos in ESCAÑOS_TOTALES:
        df_escanos = df_anio[df_anio['escanos_totales'] == escanos]
        
        if not df_escanos.empty:
            print(f"\n{escanos} ESCAÑOS:")
            for _, row in df_escanos.iterrows():
                mayorias = ""
                if row['mayoria_calificada_coalicion']:
                    mayorias = " [(!!) MAYORIA CALIFICADA COALICIÓN]"
                elif row['mayoria_simple_coalicion']:
                    mayorias = " [Mayoría simple coalición]"
                elif row['mayoria_calificada_morena']:
                    mayorias = " [(!!) MAYORIA CALIFICADA MORENA SOLO]"
                elif row['mayoria_simple_morena']:
                    mayorias = " [Mayoría simple MORENA solo]"
                    
                print(f"  {row['config_mr_rp']} | {row['coalicion']} coalición: "
                      f"MORENA {row['morena_total']} ({row['morena_pct']}%) | "
                      f"Coalición {row['coalicion_total']} ({row['coalicion_pct']}%){mayorias}")

print("\n" + "="*80)
print("[!] RECORDATORIO: Estos resultados NO respetan los topes constitucionales")
print("   Son solo para analisis contrafactual")
print("="*80)
