"""
Genera tabla comparativa 2021 vs 2024 con 4 escenarios
SIN TOPES (sin límite 300, sin +8%) pero CON umbral 3%
"""
import pandas as pd
from datetime import datetime
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.procesar_diputados_v2 import procesar_diputados_v2

def generar_tabla_sin_topes():
    """
    Genera tabla con 4 escenarios comparando 2021 vs 2024
    SIN aplicar topes constitucionales
    """
    print("=" * 80)
    print("GENERANDO TABLA COMPARATIVA 2021 vs 2024 - SIN TOPES")
    print("=" * 80)
    print()
    
    # Definir escenarios
    escenarios = [
        {
            "nombre": "MR 200 - RP 200",
            "mr_seats": 200,
            "rp_seats": 200,
            "pm_seats": 0
        },
        {
            "nombre": "MR 300 - RP 100",
            "mr_seats": 300,
            "rp_seats": 100,
            "pm_seats": 0
        },
        {
            "nombre": "MR 200 - PM 200",
            "mr_seats": 200,
            "rp_seats": 0,
            "pm_seats": 200
        },
        {
            "nombre": "MR 300 - PM 100",
            "mr_seats": 300,
            "rp_seats": 0,
            "pm_seats": 100
        }
    ]
    
    # Supuestos fijos
    print("Supuestos aplicados:")
    print("  - Umbral de representacion: 3% (ACTIVADO)")
    print("  - Tope de sobrerrepresentacion: DESACTIVADO")
    print("  - Limite maximo de escaños: DESACTIVADO")
    print("  - Coaliciones: Activadas")
    print()
    
    resultados = []
    
    for escenario in escenarios:
        print(f"\n{'='*80}")
        print(f"Escenario: {escenario['nombre']}")
        print(f"{'='*80}")
        
        for anio in [2021, 2024]:
            print(f"\n  Procesando año {anio}...")
            
            # Paths según el año
            path_parquet = f'data/computos_diputados_{anio}.parquet'
            path_siglado = f'data/siglado-diputados-{anio}.csv'
            
            # Partidos que participaron según año
            if anio == 2021:
                partidos_base = ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA', 'PES', 'RSP', 'FXM']
            else:  # 2024
                partidos_base = ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA']
            
            try:
                # Llamar motor SIN TOPES
                resultado = procesar_diputados_v2(
                    path_parquet=path_parquet,
                    path_siglado=path_siglado,
                    partidos_base=partidos_base,
                    anio=anio,
                    max_seats=400,
                    mr_seats=escenario["mr_seats"],
                    pm_seats=escenario["pm_seats"],
                    rp_seats=escenario["rp_seats"],
                    aplicar_topes=False,  # ← SIN TOPES
                    umbral=0.03,  # ← 3% ACTIVO
                    sobrerrepresentacion=None,  # ← No aplicar +8%
                    max_seats_per_party=None,  # ← No aplicar límite 300
                    usar_coaliciones=True,
                    seed=42,
                    print_debug=False
                )
                
                # Extraer resultados
                mr_dict = resultado['mr']
                pm_dict = resultado.get('pm', {})
                rp_dict = resultado['rp']
                tot_dict = resultado['tot']
                votos_dict = resultado['votos']
                
                # Total votos para porcentajes
                total_votos = sum(votos_dict.values())
                
                # Procesar cada partido
                for partido in partidos_base:
                    votos = votos_dict.get(partido, 0)
                    votos_pct = (votos / total_votos * 100) if total_votos > 0 else 0
                    
                    mr = mr_dict.get(partido, 0)
                    pm = pm_dict.get(partido, 0)
                    rp = rp_dict.get(partido, 0)
                    total = tot_dict.get(partido, 0)
                    
                    # VERIFICACION PRD 2024
                    if partido == 'PRD' and anio == 2024:
                        if rp > 0 and votos_pct < 3.0:
                            print(f"    ⚠️  WARNING: PRD con {votos_pct:.2f}% tiene {rp} RP (deberia ser 0)")
                        else:
                            print(f"    ✓ PRD: {votos_pct:.2f}% votos, {rp} RP")
                    
                    resultados.append({
                        'Año': anio,
                        'Escenario': escenario['nombre'],
                        'Partido': partido,
                        'Votos_%': round(votos_pct, 2),
                        'MR': mr,
                        'PM': pm,
                        'RP': rp,
                        'Total': total
                    })
                
                print(f"    ✓ Completado")
                
            except Exception as e:
                print(f"    ✗ Error: {e}")
                import traceback
                traceback.print_exc()
    
    # Crear DataFrame
    df = pd.DataFrame(resultados)
    
    # Calcular diferencias MORENA (2024 - 2021)
    print(f"\n{'='*80}")
    print("Calculando diferencias MORENA (2024 - 2021)...")
    print(f"{'='*80}")
    
    diferencias = []
    
    for escenario in escenarios:
        escenario_nombre = escenario['nombre']
        
        morena_2021 = df[(df['Escenario'] == escenario_nombre) & 
                         (df['Año'] == 2021) & 
                         (df['Partido'] == 'MORENA')]
        
        morena_2024 = df[(df['Escenario'] == escenario_nombre) & 
                         (df['Año'] == 2024) & 
                         (df['Partido'] == 'MORENA')]
        
        if not morena_2021.empty and not morena_2024.empty:
            diff_mr = morena_2024['MR'].values[0] - morena_2021['MR'].values[0]
            diff_pm = morena_2024['PM'].values[0] - morena_2021['PM'].values[0]
            diff_rp = morena_2024['RP'].values[0] - morena_2021['RP'].values[0]
            diff_total = morena_2024['Total'].values[0] - morena_2021['Total'].values[0]
            
            diferencias.append({
                'Escenario': escenario_nombre,
                'Diff_MORENA_MR': diff_mr,
                'Diff_MORENA_PM': diff_pm,
                'Diff_MORENA_RP': diff_rp,
                'Diff_MORENA_Total': diff_total
            })
            
            print(f"\n{escenario_nombre}:")
            print(f"  MR: {diff_mr:+d}")
            print(f"  PM: {diff_pm:+d}")
            print(f"  RP: {diff_rp:+d}")
            print(f"  Total: {diff_total:+d}")
    
    # Agregar diferencias al DataFrame
    df_diff = pd.DataFrame(diferencias)
    df = df.merge(df_diff, on='Escenario', how='left')
    
    # =========================================================================
    # AGREGAR FILAS DE COALICIONES
    # =========================================================================
    print(f"\n{'='*80}")
    print("Agregando totales por coalición...")
    print(f"{'='*80}\n")
    
    coalicion_morena = ['MORENA', 'PT', 'PVEM']
    coalicion_pan = ['PAN', 'PRI', 'PRD']
    
    filas_coaliciones = []
    
    for escenario in escenarios:
        escenario_nombre = escenario['nombre']
        
        for anio in [2021, 2024]:
            df_filtrado = df[(df['Escenario'] == escenario_nombre) & (df['Año'] == anio)]
            
            # Coalición MORENA + PT + PVEM
            morena_coal = df_filtrado[df_filtrado['Partido'].isin(coalicion_morena)]
            if not morena_coal.empty:
                fila_morena = {
                    'Año': anio,
                    'Escenario': escenario_nombre,
                    'Partido': 'COALICIÓN MORENA+PT+PVEM',
                    'Votos_%': morena_coal['Votos_%'].sum(),
                    'MR': morena_coal['MR'].sum(),
                    'PM': morena_coal['PM'].sum(),
                    'RP': morena_coal['RP'].sum(),
                    'Total': morena_coal['Total'].sum()
                }
                # Agregar las columnas de diferencias si existen
                if 'Diff_MORENA_MR' in df_filtrado.columns:
                    fila_morena['Diff_MORENA_MR'] = df_filtrado['Diff_MORENA_MR'].iloc[0] if not df_filtrado.empty else None
                    fila_morena['Diff_MORENA_PM'] = df_filtrado['Diff_MORENA_PM'].iloc[0] if not df_filtrado.empty else None
                    fila_morena['Diff_MORENA_RP'] = df_filtrado['Diff_MORENA_RP'].iloc[0] if not df_filtrado.empty else None
                    fila_morena['Diff_MORENA_Total'] = df_filtrado['Diff_MORENA_Total'].iloc[0] if not df_filtrado.empty else None
                
                filas_coaliciones.append(fila_morena)
            
            # Coalición PAN + PRI + PRD
            pan_coal = df_filtrado[df_filtrado['Partido'].isin(coalicion_pan)]
            if not pan_coal.empty:
                fila_pan = {
                    'Año': anio,
                    'Escenario': escenario_nombre,
                    'Partido': 'COALICIÓN PAN+PRI+PRD',
                    'Votos_%': pan_coal['Votos_%'].sum(),
                    'MR': pan_coal['MR'].sum(),
                    'PM': pan_coal['PM'].sum(),
                    'RP': pan_coal['RP'].sum(),
                    'Total': pan_coal['Total'].sum()
                }
                # Agregar las columnas de diferencias si existen
                if 'Diff_MORENA_MR' in df_filtrado.columns:
                    fila_pan['Diff_MORENA_MR'] = df_filtrado['Diff_MORENA_MR'].iloc[0] if not df_filtrado.empty else None
                    fila_pan['Diff_MORENA_PM'] = df_filtrado['Diff_MORENA_PM'].iloc[0] if not df_filtrado.empty else None
                    fila_pan['Diff_MORENA_RP'] = df_filtrado['Diff_MORENA_RP'].iloc[0] if not df_filtrado.empty else None
                    fila_pan['Diff_MORENA_Total'] = df_filtrado['Diff_MORENA_Total'].iloc[0] if not df_filtrado.empty else None
                
                filas_coaliciones.append(fila_pan)
    
    # Agregar filas de coaliciones al DataFrame
    if filas_coaliciones:
        df_coaliciones = pd.DataFrame(filas_coaliciones)
        df = pd.concat([df, df_coaliciones], ignore_index=True)
        print(f"✓ Agregadas {len(filas_coaliciones)} filas de coaliciones")
    
    # =========================================================================
    # AGREGAR COLUMNA DE PORCENTAJE DE ESCAÑOS
    # =========================================================================
    print("\nCalculando porcentaje de escaños...")
    
    # Total de escaños siempre es 400
    total_escanos = 400
    df['Escaños_%'] = (df['Total'] / total_escanos * 100).round(2)
    
    print(f"✓ Columna 'Escaños_%' agregada")
    
    # Guardar CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = f'outputs/comparativa_2021_vs_2024_SIN_TOPES_{timestamp}.csv'
    
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"\n{'='*80}")
    print("✓ TABLA GENERADA EXITOSAMENTE (SIN TOPES)")
    print(f"{'='*80}")
    print(f"Archivo: {output_path}")
    print(f"Total filas: {len(df)}")
    print(f"Años: {sorted(df['Año'].unique())}")
    print(f"Escenarios: {len(escenarios)}")
    print()
    
    # Mostrar preview
    print("Vista previa (primeras 20 filas):")
    print(df.head(20).to_string())
    
    return output_path

if __name__ == '__main__':
    try:
        output = generar_tabla_sin_topes()
        print("\n✓ Generacion exitosa")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
