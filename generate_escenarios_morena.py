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

# Agregar el directorio actual al path
sys.path.append('.')

from engine.procesar_diputados_v2 import procesar_diputados_v2

def calcular_escenarios_morena():
    """
    Genera todos los escenarios para MORENA y exporta a CSV
    """
    
    # Configuración de escenarios
    años = [2018, 2021, 2024]
    magnitudes = [400, 500]
    configuraciones = [
        {"nombre": "50MR_50RP", "mr_pct": 0.50, "rp_pct": 0.50},
        {"nombre": "75MR_25RP", "mr_pct": 0.75, "rp_pct": 0.25}
    ]
    
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
                    
                    print(f"      [✓] CON coalición: MORENA={escaños_morena_solo} ({pct_morena_solo:.1f}%), "
                          f"Coalición={escaños_coalicion} ({pct_coalicion:.1f}%)")
                    
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
                    
                    print(f"      [✓] SIN coalición: MORENA={escaños_morena} ({pct_morena:.1f}%)")
                    
                except Exception as e:
                    print(f"      [ERROR] SIN coalición: {e}")
    
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
    print(f"[✓] Escenarios generados exitosamente: {output_path}")
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
        print("\n[MAYORÍA CALIFICADA - SOLO MORENA (≥66.67%)]")
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
        print("\n[MAYORÍA CALIFICADA - CON COALICIÓN (≥66.67%)]")
        for _, row in mayoria_calif_coal.iterrows():
            print(f"  • {row['año']} | {row['magnitud']} escaños | {row['configuracion']} | "
                  f"{row['escenario']} | Coalición: {row['coalicion_escaños']} ({row['coalicion_porcentaje']}%)")
    
    print("\n" + "=" * 80)
    
    return output_path, df

if __name__ == "__main__":
    try:
        output_path, df = calcular_escenarios_morena()
        print(f"\n[✓] Proceso completado. Archivo generado: {output_path}")
        
        # Mostrar preview del CSV
        print("\n[PREVIEW - Primeras 10 filas]")
        print(df.head(10).to_string(index=False))
        
    except Exception as e:
        print(f"\n[ERROR] Error en el proceso: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
