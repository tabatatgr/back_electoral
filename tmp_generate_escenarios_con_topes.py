"""
Generar escenarios MORENA CON TOPES CONSTITUCIONALES
- 8% de sobrerrepresentación
- Máximo 300 escaños por partido
"""
from engine.procesar_diputados_v2 import procesar_diputados_v2
from usar_swing import SwingElectoral
import pandas as pd
from datetime import datetime
import os
import math

print("="*80)
print("GENERANDO ESCENARIOS CON TOPES CONSTITUCIONALES")
print("="*80)
print("[OK] Tope 8% de sobrerrepresentacion: APLICADO")
print("[OK] Tope 300 escanos maximo: APLICADO")

# Cargar swing electoral para 2021
try:
    swing = SwingElectoral()
    usar_swing_2021 = True
    print("[OK] Swing electoral 2021 cargado")
except Exception as e:
    print(f"[!] No se pudo cargar swing: {e}")
    print("[!] Los escenarios 2021_SWING no se generaran")
    usar_swing_2021 = False

print()

# Configuraciones
anios = [2018, 2021, 2024]
anios_con_swing = ['2021_SWING'] if usar_swing_2021 else []  # Añadir 2021 con swing
total_escanos = [400, 500, 600]
configs_mr_rp = [
    (50, 50),  # 50% MR, 50% RP
    (60, 40),  # 60% MR, 40% RP
    (75, 25),  # 75% MR, 25% RP
]
usar_coaliciones_opts = [True, False]

# Paths de datos
data_paths = {
    2018: 'data/computos_diputados_2018.parquet',
    2021: 'data/computos_diputados_2021.parquet',
    2024: 'data/computos_diputados_2024.parquet',
}

# Paths de siglado
siglado_paths = {
    2018: 'data/siglado-diputados-2018.csv',
    2021: 'data/siglado-diputados-2021.csv',
    2024: 'data/siglado-diputados-2024.csv',
}

resultados = []
total_escenarios = (len(anios) + len(anios_con_swing)) * len(total_escanos) * len(configs_mr_rp) * len(usar_coaliciones_opts)
contador = 0

# Procesar años normales
for anio in anios:
    for escanos in total_escanos:
        for (pct_mr, pct_rp) in configs_mr_rp:
            mr_seats = int(escanos * pct_mr / 100)
            rp_seats = int(escanos * pct_rp / 100)
            
            for usar_coal in usar_coaliciones_opts:
                contador += 1
                coal_label = "CON" if usar_coal else "SIN"
                config_label = f"{pct_mr}MR_{pct_rp}RP"
                
                print(f"[{contador}/{total_escenarios}] Procesando: {anio} | {escanos} escaños | {config_label} | {coal_label} coalición")
                
                try:
                    resultado = procesar_diputados_v2(
                        path_parquet=data_paths[anio],
                        path_siglado=siglado_paths.get(anio),  # Agregar siglado
                        anio=anio,
                        max_seats=escanos,
                        mr_seats=mr_seats,
                        rp_seats=rp_seats,
                        usar_coaliciones=usar_coal,
                        aplicar_topes=True,  # 🔒 CON TOPES
                        print_debug=False
                    )
                    
                    # Calcular total de votos
                    total_votos = sum(resultado['votos'].values())
                    
                    # Extraer datos de MORENA
                    morena_mr = resultado['mr'].get('MORENA', 0)
                    morena_rp = resultado['rp'].get('MORENA', 0)
                    morena_tot = resultado['tot'].get('MORENA', 0)
                    morena_votos = resultado['votos'].get('MORENA', 0)
                    morena_pct_votos = (morena_votos / total_votos * 100) if total_votos > 0 else 0
                    morena_pct_escanos = (morena_tot / escanos * 100) if escanos > 0 else 0
                    
                    # Calcular escaños de la coalición (MORENA + aliados)
                    if anio == 2018:
                        # JHH (MORENA + PT + PES)
                        coal_partidos = ['MORENA', 'PT', 'PES']
                    elif anio == 2021:
                        # JHH (MORENA + PT + PVEM)
                        coal_partidos = ['MORENA', 'PT', 'PVEM']
                    else:  # 2024
                        # SSP (MORENA + PT + PVEM)
                        coal_partidos = ['MORENA', 'PT', 'PVEM']
                    
                    coal_tot = sum(resultado['tot'].get(p, 0) for p in coal_partidos)
                    coal_pct_escanos = (coal_tot / escanos * 100) if escanos > 0 else 0
                    
                    # Verificar mayorías (CORREGIDO - 4 columnas separadas)
                    # MORENA solo
                    mayoria_simple_morena = morena_tot > (escanos / 2)
                    umbral_calificada = math.ceil(escanos * 2 / 3)
                    mayoria_calificada_morena = morena_tot >= umbral_calificada
                    
                    # Coalición
                    mayoria_simple_coalicion = coal_tot > (escanos / 2)
                    mayoria_calificada_coalicion = coal_tot >= umbral_calificada
                    
                    print(f"    (+) MORENA: {morena_tot} escaños ({morena_pct_escanos:.1f}%)")
                    print(f"    (+) Coalición: {coal_tot} escaños ({coal_pct_escanos:.1f}%)")
                    
                    # Guardar resultado
                    resultados.append({
                        'anio': anio,
                        'total_escanos': escanos,
                        'configuracion': config_label,
                        'pct_mr': pct_mr,
                        'pct_rp': pct_rp,
                        'mr_seats': mr_seats,
                        'rp_seats': rp_seats,
                        'usar_coaliciones': coal_label,
                        'morena_votos_pct': round(morena_pct_votos, 2),
                        'morena_mr': morena_mr,
                        'morena_rp': morena_rp,
                        'morena_total': morena_tot,
                        'morena_pct_escanos': round(morena_pct_escanos, 2),
                        'coalicion_total': coal_tot,
                        'coalicion_pct_escanos': round(coal_pct_escanos, 2),
                        'mayoria_simple_morena': mayoria_simple_morena,
                        'mayoria_calificada_morena': mayoria_calificada_morena,
                        'mayoria_simple_coalicion': mayoria_simple_coalicion,
                        'mayoria_calificada_coalicion': mayoria_calificada_coalicion,
                        'topes_aplicados': 'SI'
                    })
                    
                except Exception as e:
                    print(f"    (✗) ERROR: {e}")
                    continue

# Procesar 2021 CON SWING
if usar_swing_2021:
    print("\n" + "="*80)
    print("PROCESANDO 2021 CON SWING ELECTORAL")
    print("="*80)
    
    # Cargar votos de 2021
    df_votos_2021 = pd.read_parquet('data/computos_diputados_2021.parquet')
    
    for escanos in total_escanos:
        for (pct_mr, pct_rp) in configs_mr_rp:
            mr_seats = int(escanos * pct_mr / 100)
            rp_seats = int(escanos * pct_rp / 100)
            
            for usar_coal in usar_coaliciones_opts:
                contador += 1
                coal_label = "CON" if usar_coal else "SIN"
                config_label = f"{pct_mr}MR_{pct_rp}RP"
                
                print(f"[{contador}/{total_escenarios}] Procesando: 2021_SWING | {escanos} escaños | {config_label} | {coal_label} coalición")
                
                try:
                    # Aplicar swing por distrito
                    df_ajustado = df_votos_2021.copy()
                    distritos_ajustados = 0
                    
                    for idx, row in df_ajustado.iterrows():
                        # usar_swing.py acepta nombres de entidad directamente
                        entidad = row['ENTIDAD']  # Ya viene como nombre completo del estado
                        distrito = int(row['DISTRITO'])
                        
                        # Preparar votos 2021 originales para este distrito
                        votos_2021 = {
                            'PAN': row.get('PAN', 0),
                            'PRI': row.get('PRI', 0),
                            'PRD': row.get('PRD', 0),
                            'PVEM': row.get('PVEM', 0),
                            'PT': row.get('PT', 0),
                            'MC': row.get('MC', 0),
                            'MORENA': row.get('MORENA', 0)
                        }
                        
                        # Aplicar swing (retorna votos originales si no hay swing para este distrito)
                        votos_ajustados = swing.ajustar_votos(
                            votos_2021=votos_2021,
                            entidad=entidad,
                            distrito=distrito,
                            usar_coaliciones=usar_coal
                        )
                        
                        # Actualizar DataFrame solo si hubo cambio
                        cambio = False
                        for partido, nuevo_voto in votos_ajustados.items():
                            if partido in df_ajustado.columns:
                                if abs(nuevo_voto - row.get(partido, 0)) > 0.01:
                                    cambio = True
                                df_ajustado.at[idx, partido] = nuevo_voto
                        
                        if cambio:
                            distritos_ajustados += 1
                    
                    # Guardar temporalmente
                    temp_parquet = 'data/temp_2021_con_swing.parquet'
                    df_ajustado.to_parquet(temp_parquet)
                    
                    print(f"    (+) Swing aplicado a {distritos_ajustados} distritos")
                    
                    # Procesar con topes
                    resultado = procesar_diputados_v2(
                        path_parquet=temp_parquet,
                        path_siglado='data/siglado-diputados-2021.csv',
                        anio=2021,
                        max_seats=escanos,
                        mr_seats=mr_seats,
                        rp_seats=rp_seats,
                        usar_coaliciones=usar_coal,
                        aplicar_topes=True,
                        print_debug=False
                    )
                    
                    # Limpiar temporal
                    if os.path.exists(temp_parquet):
                        os.remove(temp_parquet)
                    
                    # Calcular estadísticas
                    total_votos = sum(resultado['votos'].values())
                    morena_mr = resultado['mr'].get('MORENA', 0)
                    morena_rp = resultado['rp'].get('MORENA', 0)
                    morena_tot = resultado['tot'].get('MORENA', 0)
                    morena_votos = resultado['votos'].get('MORENA', 0)
                    morena_pct_votos = (morena_votos / total_votos * 100) if total_votos > 0 else 0
                    morena_pct_escanos = (morena_tot / escanos * 100) if escanos > 0 else 0
                    
                    # Coalición JHH 2021: MORENA + PT + PVEM
                    coal_partidos = ['MORENA', 'PT', 'PVEM']
                    coal_tot = sum(resultado['tot'].get(p, 0) for p in coal_partidos)
                    coal_pct_escanos = (coal_tot / escanos * 100) if escanos > 0 else 0
                    
                    # Verificar mayorías (CORREGIDO - 4 columnas separadas)
                    # MORENA solo
                    mayoria_simple_morena = morena_tot > (escanos / 2)
                    umbral_calificada = math.ceil(escanos * 2 / 3)
                    mayoria_calificada_morena = morena_tot >= umbral_calificada
                    
                    # Coalición
                    mayoria_simple_coalicion = coal_tot > (escanos / 2)
                    mayoria_calificada_coalicion = coal_tot >= umbral_calificada
                    
                    print(f"    (+) MORENA: {morena_tot} escaños ({morena_pct_escanos:.1f}%)")
                    print(f"    (+) Coalición: {coal_tot} escaños ({coal_pct_escanos:.1f}%)")
                    
                    # Guardar resultado
                    resultados.append({
                        'anio': '2021_SWING',
                        'total_escanos': escanos,
                        'configuracion': config_label,
                        'pct_mr': pct_mr,
                        'pct_rp': pct_rp,
                        'mr_seats': mr_seats,
                        'rp_seats': rp_seats,
                        'usar_coaliciones': coal_label,
                        'morena_votos_pct': round(morena_pct_votos, 2),
                        'morena_mr': morena_mr,
                        'morena_rp': morena_rp,
                        'morena_total': morena_tot,
                        'morena_pct_escanos': round(morena_pct_escanos, 2),
                        'coalicion_total': coal_tot,
                        'coalicion_pct_escanos': round(coal_pct_escanos, 2),
                        'mayoria_simple_morena': mayoria_simple_morena,
                        'mayoria_calificada_morena': mayoria_calificada_morena,
                        'mayoria_simple_coalicion': mayoria_simple_coalicion,
                        'mayoria_calificada_coalicion': mayoria_calificada_coalicion,
                        'topes_aplicados': 'SI'
                    })
                    
                except Exception as e:
                    print(f"    (✗) ERROR: {e}")
                    import traceback
                    traceback.print_exc()
                    continue

# Convertir a DataFrame
df = pd.DataFrame(resultados)

# Guardar CSV
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_path = f'outputs/escenarios_morena_CON_TOPES_{timestamp}.csv'
df.to_csv(output_path, index=False)

print()
print("="*80)
print(f"(+) Escenarios generados: {len(resultados)}")
print(f"(+) Archivo guardado: {output_path}")
print("="*80)

# Resumen por año
print()
print("📊 RESUMEN DE RESULTADOS CON TOPES:")
print()

for anio in anios:
    print("="*70)
    print(f"AÑO {anio}")
    print("="*70)
    
    df_anio = df[df['anio'] == anio]
    
    for escanos in total_escanos:
        df_escanos = df_anio[df_anio['total_escanos'] == escanos]
        if len(df_escanos) == 0:
            continue
            
        print(f"\n{escanos} ESCAÑOS:")
        for _, row in df_escanos.iterrows():
            config = row['configuracion']
            coal = row['usar_coaliciones']
            morena_tot = row['morena_total']
            morena_pct = row['morena_pct_escanos']
            coal_tot = row['coalicion_total']
            coal_pct = row['coalicion_pct_escanos']
            mayoria = row['mayoria_tipo']
            
            mayoria_label = {
                'MAYORIA_CALIFICADA': '[(!!) MAYORIA CALIFICADA]',
                'MAYORIA_SIMPLE': '[Mayoria simple]',
                'MINORIA': '[Minoría]'
            }.get(mayoria, '')
            
            print(f"  {config} | {coal} coalición: MORENA {morena_tot} ({morena_pct}%) | "
                  f"Coalición {coal_tot} ({coal_pct}%) {mayoria_label}")

print()
print("="*80)
print("[!] RECORDATORIO: Estos resultados RESPETAN los topes constitucionales")
print("    - 8% de sobrerrepresentación máxima")
print("    - 300 escaños máximo por partido")
print("="*80)
