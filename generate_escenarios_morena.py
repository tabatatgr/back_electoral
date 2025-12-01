"""
Script para generar escenarios de MORENA (con y sin coalición)
en distintas configuraciones de la Cámara de Diputados.

Evalúa:
- Años: 2018, 2021, 2024
- Magnitudes: 400 y 500 diputados
- Configuraciones MR/RP:
  - 50% MR / 50% RP
  - 75% MR / 25% RP
- Con coalición y sin coalición
- Identifica cuándo MORENA alcanza mayoría simple (>50%) y mayoría calificada (≥66.67%)
"""

import pandas as pd
import sys
import os
from datetime import datetime
import numpy as np

# Agregar el directorio actual al path
sys.path.append('.')

from engine.procesar_diputados_v2 import procesar_diputados_v2
from usar_swing import SwingElectoral

def calcular_escenarios_morena():
    """
    Genera todos los escenarios para MORENA y exporta a CSV
    Incluye escenarios con swing electoral para 2021
    """
    
    # Configuración de escenarios
    años = [2018, 2021, 2024]
    magnitudes = [400, 500]
    configuraciones = [
        {"nombre": "50MR_50RP", "mr_pct": 0.50, "rp_pct": 0.50},
        {"nombre": "75MR_25RP", "mr_pct": 0.75, "rp_pct": 0.25}
    ]
    
    # Inicializar swing electoral (solo para 2021)
    try:
        swing = SwingElectoral()
        usar_swing = True
        print("[INFO] Swing electoral cargado correctamente")
    except Exception as e:
        print(f"[WARN] No se pudo cargar swing electoral: {e}")
        print("[INFO] Los escenarios con swing no se generarán")
        usar_swing = False
    
    # Partidos en coalición con MORENA por año
    coaliciones_morena = {
        2018: ["MORENA", "PT", "PES"],  # Juntos Haremos Historia
        2021: ["MORENA", "PT", "PVEM"],  # Juntos Hacemos Historia
        2024: ["MORENA", "PT", "PVEM"]   # Sigamos Haciendo Historia
    }
    
    resultados = []
    
    print("[INFO] Generando escenarios para MORENA...")
    print("=" * 80)
    
    for año in años:
        print(f"\n[INFO] Procesando año {año}...")
        
        # Paths de datos
        path_parquet = f"data/computos_diputados_{año}.parquet"
        path_siglado = f"data/siglado-diputados-{año}.csv"
        
        # Verificar que existen los archivos
        if not os.path.exists(path_parquet):
            print(f"[WARN] No se encontró {path_parquet}, saltando año {año}")
            continue
        if not os.path.exists(path_siglado):
            print(f"[WARN] No se encontró {path_siglado}, saltando año {año}")
            continue
        
        for magnitud in magnitudes:
            print(f"  [INFO] Magnitud: {magnitud} escaños")
            
            for config in configuraciones:
                mr_seats = int(magnitud * config["mr_pct"])
                rp_seats = magnitud - mr_seats
                
                print(f"    [INFO] Config: {config['nombre']} (MR={mr_seats}, RP={rp_seats})")
                
                # Procesar CON coalición
                try:
                    resultado_con_coal = procesar_diputados_v2(
                        path_parquet=path_parquet,
                        anio=año,
                        path_siglado=path_siglado,
                        max_seats=magnitud,
                        sistema="mixto",
                        mr_seats=mr_seats,
                        rp_seats=rp_seats,
                        umbral=0.03,
                        quota_method="hare",
                        usar_coaliciones=True,
                        print_debug=False
                    )
                    
                    # Sumar escaños de MORENA y coalición
                    partidos_coalicion = coaliciones_morena.get(año, ["MORENA"])
                    escaños_morena_solo = resultado_con_coal['tot'].get('MORENA', 0)
                    escaños_coalicion = sum(resultado_con_coal['tot'].get(p, 0) for p in partidos_coalicion)
                    
                    pct_morena_solo = (escaños_morena_solo / magnitud) * 100
                    pct_coalicion = (escaños_coalicion / magnitud) * 100
                    
                    # Determinar mayorías
                    mayoria_simple_morena = escaños_morena_solo > (magnitud / 2)
                    mayoria_calif_morena = escaños_morena_solo >= (magnitud * 2 / 3)
                    mayoria_simple_coal = escaños_coalicion > (magnitud / 2)
                    mayoria_calif_coal = escaños_coalicion >= (magnitud * 2 / 3)
                    
                    resultados.append({
                        "año": año,
                        "magnitud": magnitud,
                        "configuracion": config['nombre'],
                        "mr_seats": mr_seats,
                        "rp_seats": rp_seats,
                        "escenario": "CON_COALICION",
                        "partidos_coalicion": ", ".join(partidos_coalicion),
                        "morena_escaños": escaños_morena_solo,
                        "morena_porcentaje": round(pct_morena_solo, 2),
                        "coalicion_escaños": escaños_coalicion,
                        "coalicion_porcentaje": round(pct_coalicion, 2),
                        "mayoría_simple_morena": "SÍ" if mayoria_simple_morena else "NO",
                        "mayoría_calificada_morena": "SÍ" if mayoria_calif_morena else "NO",
                        "mayoría_simple_coalición": "SÍ" if mayoria_simple_coal else "NO",
                        "mayoría_calificada_coalición": "SÍ" if mayoria_calif_coal else "NO",
                        "umbral_mayoría_simple": int(magnitud / 2) + 1,
                        "umbral_mayoría_calificada": int((magnitud * 2 / 3) + 0.5)
                    })
                    
                    print(f"      [OK] CON coalicion: MORENA={escaños_morena_solo} ({pct_morena_solo:.1f}%), "
                          f"Coalicion={escaños_coalicion} ({pct_coalicion:.1f}%)")
                except Exception as e:
                    print(f"      [ERROR] CON coalición: {e}")
                
                # Procesar SIN coalición
                try:
                    resultado_sin_coal = procesar_diputados_v2(
                        path_parquet=path_parquet,
                        anio=año,
                        path_siglado=path_siglado,
                        max_seats=magnitud,
                        sistema="mixto",
                        mr_seats=mr_seats,
                        rp_seats=rp_seats,
                        umbral=0.03,
                        quota_method="hare",
                        usar_coaliciones=False,
                        print_debug=False
                    )
                    
                    escaños_morena = resultado_sin_coal['tot'].get('MORENA', 0)
                    pct_morena = (escaños_morena / magnitud) * 100
                    
                    mayoria_simple = escaños_morena > (magnitud / 2)
                    mayoria_calif = escaños_morena >= (magnitud * 2 / 3)
                    
                    resultados.append({
                        "año": año,
                        "magnitud": magnitud,
                        "configuracion": config['nombre'],
                        "mr_seats": mr_seats,
                        "rp_seats": rp_seats,
                        "escenario": "SIN_COALICION",
                        "partidos_coalicion": "Solo MORENA",
                        "morena_escaños": escaños_morena,
                        "morena_porcentaje": round(pct_morena, 2),
                        "coalicion_escaños": escaños_morena,
                        "coalicion_porcentaje": round(pct_morena, 2),
                        "mayoría_simple_morena": "SÍ" if mayoria_simple else "NO",
                        "mayoría_calificada_morena": "SÍ" if mayoria_calif else "NO",
                        "mayoría_simple_coalición": "SÍ" if mayoria_simple else "NO",
                        "mayoría_calificada_coalición": "SÍ" if mayoria_calif else "NO",
                        "umbral_mayoría_simple": int(magnitud / 2) + 1,
                        "umbral_mayoría_calificada": int((magnitud * 2 / 3) + 0.5)
                    })
                    
                    print(f"      [OK] SIN coalicion: MORENA={escaños_morena} ({pct_morena:.1f}%)")
                    
                except Exception as e:
                    print(f"      [ERROR] SIN coalición: {e}")
        
        # NUEVO: Procesar 2021 CON SWING (solo para año 2021)
        if año == 2021 and usar_swing:
            print(f"\n  [INFO] Procesando 2021 CON SWING ELECTORAL...")
            
            # Mapeo de nombres de estados a códigos
            ESTADOS_A_CODIGO = {
                'AGUASCALIENTES': '01', 'BAJA CALIFORNIA': '02', 'BAJA CALIFORNIA SUR': '03',
                'CAMPECHE': '04', 'COAHUILA': '05', 'COLIMA': '06', 'CHIAPAS': '07',
                'CHIHUAHUA': '08', 'CIUDAD DE MEXICO': '09', 'DURANGO': '10',
                'GUANAJUATO': '11', 'GUERRERO': '12', 'HIDALGO': '13', 'JALISCO': '14',
                'MEXICO': '15', 'MICHOACAN': '16', 'MORELOS': '17', 'NAYARIT': '18',
                'NUEVO LEON': '19', 'OAXACA': '20', 'PUEBLA': '21', 'QUERETARO': '22',
                'QUINTANA ROO': '23', 'SAN LUIS POTOSI': '24', 'SINALOA': '25',
                'SONORA': '26', 'TABASCO': '27', 'TAMAULIPAS': '28', 'TLAXCALA': '29',
                'VERACRUZ': '30', 'YUCATAN': '31', 'ZACATECAS': '32'
            }
            
            try:
                # Cargar votos federales 2021
                df_votos_2021 = pd.read_parquet(path_parquet)
                
                # Aplicar swing por distrito
                df_votos_ajustados = df_votos_2021.copy()
                distritos_ajustados = 0
                distritos_sin_swing = 0
                
                for idx, row in df_votos_2021.iterrows():
                    entidad_nombre = str(row['ENTIDAD']).upper() if 'ENTIDAD' in row else None
                    entidad = ESTADOS_A_CODIGO.get(entidad_nombre)
                    distrito = row['DISTRITO'] if 'DISTRITO' in row else None
                    
                    if entidad and distrito:
                        # Preparar votos originales
                        votos_originales = {
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
                            votos_originales, 
                            entidad=entidad, 
                            distrito=distrito,
                            usar_coaliciones=True,
                            factor_confianza=0.7
                        )
                        
                        # Verificar si hubo cambio (si hay swing disponible)
                        tiene_cambio = any(
                            abs(votos_ajustados.get(p, 0) - votos_originales.get(p, 0)) > 0.1
                            for p in votos_originales
                        )
                        
                        if tiene_cambio:
                            distritos_ajustados += 1
                        else:
                            distritos_sin_swing += 1
                        
                        # Actualizar DataFrame
                        for partido, votos in votos_ajustados.items():
                            if partido in df_votos_ajustados.columns:
                                df_votos_ajustados.at[idx, partido] = max(0, int(votos))
                
                # Guardar temporalmente
                temp_parquet_path = f"data/temp_computos_diputados_2021_con_swing.parquet"
                df_votos_ajustados.to_parquet(temp_parquet_path, index=False)
                
                print(f"    [INFO] Votos ajustados con swing guardados temporalmente")
                print(f"    [INFO] Distritos con swing aplicado: {distritos_ajustados} de {len(df_votos_2021)}")
                print(f"    [INFO] Distritos sin swing (mantienen votos originales): {distritos_sin_swing}")
                
                # Procesar escenarios con votos ajustados
                for magnitud in magnitudes:
                    print(f"    [INFO] Magnitud: {magnitud} escaños (CON SWING)")
                    
                    for config in configuraciones:
                        mr_seats = int(magnitud * config["mr_pct"])
                        rp_seats = magnitud - mr_seats
                        
                        print(f"      [INFO] Config: {config['nombre']} (MR={mr_seats}, RP={rp_seats})")
                        
                        # CON coalición y CON swing
                        try:
                            resultado_swing_coal = procesar_diputados_v2(
                                path_parquet=temp_parquet_path,
                                anio=2021,
                                path_siglado=path_siglado,
                                max_seats=magnitud,
                                sistema="mixto",
                                mr_seats=mr_seats,
                                rp_seats=rp_seats,
                                umbral=0.03,
                                quota_method="hare",
                                usar_coaliciones=True,
                                print_debug=False
                            )
                            
                            partidos_coalicion = coaliciones_morena.get(2021, ["MORENA"])
                            escaños_morena_solo = resultado_swing_coal['tot'].get('MORENA', 0)
                            escaños_coalicion = sum(resultado_swing_coal['tot'].get(p, 0) for p in partidos_coalicion)
                            
                            pct_morena_solo = (escaños_morena_solo / magnitud) * 100
                            pct_coalicion = (escaños_coalicion / magnitud) * 100
                            
                            mayoria_simple_morena = escaños_morena_solo > (magnitud / 2)
                            mayoria_calif_morena = escaños_morena_solo >= (magnitud * 2 / 3)
                            mayoria_simple_coal = escaños_coalicion > (magnitud / 2)
                            mayoria_calif_coal = escaños_coalicion >= (magnitud * 2 / 3)
                            
                            resultados.append({
                                "año": "2021_CON_SWING",
                                "magnitud": magnitud,
                                "configuracion": config['nombre'],
                                "mr_seats": mr_seats,
                                "rp_seats": rp_seats,
                                "escenario": "CON_COALICION_Y_SWING",
                                "partidos_coalicion": ", ".join(partidos_coalicion),
                                "morena_escaños": escaños_morena_solo,
                                "morena_porcentaje": round(pct_morena_solo, 2),
                                "coalicion_escaños": escaños_coalicion,
                                "coalicion_porcentaje": round(pct_coalicion, 2),
                                "mayoría_simple_morena": "SÍ" if mayoria_simple_morena else "NO",
                                "mayoría_calificada_morena": "SÍ" if mayoria_calif_morena else "NO",
                                "mayoría_simple_coalición": "SÍ" if mayoria_simple_coal else "NO",
                                "mayoría_calificada_coalición": "SÍ" if mayoria_calif_coal else "NO",
                                "umbral_mayoría_simple": int(magnitud / 2) + 1,
                                "umbral_mayoría_calificada": int((magnitud * 2 / 3) + 0.5),
                                "nota": "Votos 2021 ajustados con swing electoral de elecciones locales 2022-2023"
                            })
                            
                            print(f"        [OK] CON swing: Coalición={escaños_coalicion} ({pct_coalicion:.1f}%)")
                            
                        except Exception as e:
                            print(f"        [ERROR] CON swing: {e}")
                        
                        # SIN coalición pero CON swing
                        try:
                            resultado_swing_sin_coal = procesar_diputados_v2(
                                path_parquet=temp_parquet_path,
                                anio=2021,
                                path_siglado=path_siglado,
                                max_seats=magnitud,
                                sistema="mixto",
                                mr_seats=mr_seats,
                                rp_seats=rp_seats,
                                umbral=0.03,
                                quota_method="hare",
                                usar_coaliciones=False,
                                print_debug=False
                            )
                            
                            escaños_morena = resultado_swing_sin_coal['tot'].get('MORENA', 0)
                            pct_morena = (escaños_morena / magnitud) * 100
                            
                            mayoria_simple = escaños_morena > (magnitud / 2)
                            mayoria_calif = escaños_morena >= (magnitud * 2 / 3)
                            
                            resultados.append({
                                "año": "2021_CON_SWING",
                                "magnitud": magnitud,
                                "configuracion": config['nombre'],
                                "mr_seats": mr_seats,
                                "rp_seats": rp_seats,
                                "escenario": "SIN_COALICION_CON_SWING",
                                "partidos_coalicion": "Solo MORENA",
                                "morena_escaños": escaños_morena,
                                "morena_porcentaje": round(pct_morena, 2),
                                "coalicion_escaños": escaños_morena,
                                "coalicion_porcentaje": round(pct_morena, 2),
                                "mayoría_simple_morena": "SÍ" if mayoria_simple else "NO",
                                "mayoría_calificada_morena": "SÍ" if mayoria_calif else "NO",
                                "mayoría_simple_coalición": "SÍ" if mayoria_simple else "NO",
                                "mayoría_calificada_coalición": "SÍ" if mayoria_calif else "NO",
                                "umbral_mayoría_simple": int(magnitud / 2) + 1,
                                "umbral_mayoría_calificada": int((magnitud * 2 / 3) + 0.5),
                                "nota": "Votos 2021 ajustados con swing electoral de elecciones locales 2022-2023"
                            })
                            
                            print(f"        [OK] SIN coalición + swing: MORENA={escaños_morena} ({pct_morena:.1f}%)")
                            
                        except Exception as e:
                            print(f"        [ERROR] SIN coalición + swing: {e}")
                
                # Limpiar archivo temporal
                if os.path.exists(temp_parquet_path):
                    os.remove(temp_parquet_path)
                    print(f"    [INFO] Archivo temporal eliminado")
                
            except Exception as e:
                print(f"  [ERROR] Error al procesar 2021 con swing: {e}")
                import traceback
                traceback.print_exc()
    
    # Convertir a DataFrame
    df = pd.DataFrame(resultados)
    
    # Ordenar por año, magnitud y configuración
    df = df.sort_values(['año', 'magnitud', 'configuracion', 'escenario'])
    
    # Exportar a CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"outputs/escenarios_morena_{timestamp}.csv"
    
    os.makedirs("outputs", exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print("\n" + "=" * 80)
    print(f"[OK] Escenarios generados exitosamente: {output_path}")
    print(f"[INFO] Total de escenarios: {len(df)}")
    
    # Generar reporte de mayorías
    print("\n" + "=" * 80)
    print("RESUMEN: ESCENARIOS DONDE MORENA ALCANZA MAYORÍAS")
    print("=" * 80)
    
    # Mayoría simple solo MORENA
    mayoria_simple_morena = df[df['mayoría_simple_morena'] == 'SÍ']
    if not mayoria_simple_morena.empty:
        print("\n[MAYORÍA SIMPLE - SOLO MORENA (>50%)]")
        for _, row in mayoria_simple_morena.iterrows():
            print(f"  • {row['año']} | {row['magnitud']} escaños | {row['configuracion']} | "
                  f"{row['escenario']} | MORENA: {row['morena_escaños']} ({row['morena_porcentaje']}%)")
    else:
        print("\n[MAYORÍA SIMPLE - SOLO MORENA]: Ningún escenario")
    
    # Mayoría calificada solo MORENA
    mayoria_calif_morena = df[df['mayoría_calificada_morena'] == 'SÍ']
    if not mayoria_calif_morena.empty:
        print("\n[MAYORÍA CALIFICADA - SOLO MORENA (>=66.67%)]")
        for _, row in mayoria_calif_morena.iterrows():
            print(f"  • {row['año']} | {row['magnitud']} escaños | {row['configuracion']} | "
                  f"{row['escenario']} | MORENA: {row['morena_escaños']} ({row['morena_porcentaje']}%)")
    else:
        print("\n[MAYORÍA CALIFICADA - SOLO MORENA]: Ningún escenario")
    
    # Mayoría simple con coalición
    mayoria_simple_coal = df[df['mayoría_simple_coalición'] == 'SÍ']
    if not mayoria_simple_coal.empty:
        print("\n[MAYORÍA SIMPLE - CON COALICIÓN (>50%)]")
        for _, row in mayoria_simple_coal.iterrows():
            print(f"  • {row['año']} | {row['magnitud']} escaños | {row['configuracion']} | "
                  f"{row['escenario']} | Coalición: {row['coalicion_escaños']} ({row['coalicion_porcentaje']}%)")
    
    # Mayoría calificada con coalición
    mayoria_calif_coal = df[df['mayoría_calificada_coalición'] == 'SÍ']
    if not mayoria_calif_coal.empty:
        print("\n[MAYORÍA CALIFICADA - CON COALICIÓN (>=66.67%)]")
        for _, row in mayoria_calif_coal.iterrows():
            print(f"  • {row['año']} | {row['magnitud']} escaños | {row['configuracion']} | "
                  f"{row['escenario']} | Coalición: {row['coalicion_escaños']} ({row['coalicion_porcentaje']}%)")
    
    print("\n" + "=" * 80)
    
    # Agregar explicación sobre swing electoral
    print("\nNOTA METODOLÓGICA: SWING ELECTORAL 2021")
    print("=" * 80)
    print("""
Los escenarios "2021_CON_SWING" ajustan los votos federales 2021 con el swing 
electoral calculado a partir de elecciones locales 2022-2023 en 8 estados:
- Aguascalientes, Durango, Hidalgo, Oaxaca, Quintana Roo, Tamaulipas (2022)
- Coahuila, México (2023)

HALLAZGOS CLAVE:
1. COAHUILA - Rotación PT/MORENA:
   Se detectó que PT tuvo un swing individual de +3,797% en algunos distritos,
   mientras MORENA bajó -43%. Esto NO refleja crecimiento real, sino ROTACIÓN
   de candidatos entre partidos de la misma coalición.
   
   Solución: Se usa swing de COALICIÓN PT+MORENA (-11%) en lugar de individual.
   
2. MÉXICO - Coaliciones completas:
   En las elecciones locales 2023, PVEM, PT, MC y MORENA fueron EXCLUSIVAMENTE
   en coalición (columna PVEM_PT_MORENA en los datos). Por tanto, no se aplica
   swing individual a estos partidos en México.
   
3. QUINTANA ROO - Crecimiento PVEM/MC:
   PVEM creció +198% y MC +183%. Es crecimiento REAL pero se aplica factor de
   confianza de 0.70 para evitar sobreestimación.

COBERTURA: 83 de 300 distritos federales (27.7%)
Los distritos sin datos de swing mantienen sus votos originales 2021.

Para más detalles, ver: INVESTIGACION_OUTLIERS_SWING.md
""")
    print("=" * 80)
    
    return output_path, df

if __name__ == "__main__":
    try:
        output_path, df = calcular_escenarios_morena()
        print(f"\n[OK] Proceso completado. Archivo generado: {output_path}")
        
        # Mostrar preview del CSV
        print("\n[PREVIEW - Primeras 10 filas]")
        print(df.head(10).to_string(index=False))
        
    except Exception as e:
        print(f"\n[ERROR] Error en el proceso: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
