"""
Script de integración: Redistritación → Motor Electoral

Pipeline completo:
1. MÓDULO A: Repartir distritos por estado (Hare)
2. MÓDULO B: Distritar cada estado (Greedy)
3. MÓDULO C: Crear tabla puente y reagregar votos
4. Motor Electoral: Calcular resultados con nueva cartografía

Compara resultados:
- Baseline: 300-100 (cartografía actual)
- Reforma: 200-200 (nueva cartografía)
"""

import sys
import time
from pathlib import Path
import pandas as pd

# Agregar path del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

from redistritacion.config import ESCENARIOS
from redistritacion.modulos.reparto_distritos import repartir_distritos_hare
from redistritacion.modulos.distritacion import cargar_secciones_ine, distritar_estado
from redistritacion.modulos.tabla_puente import pipeline_tabla_puente

# Importar motor electoral
from engine.procesar_diputados_v2 import procesar_diputados_v2


def ejecutar_redistritacion_completa(
    escenario: str = 'reforma_200_200',
    anio: int = 2024,
    print_debug: bool = True
):
    """
    Ejecuta redistritación completa y calcula resultados electorales.
    
    Args:
        escenario: Nombre del escenario a ejecutar
        anio: Año electoral
        print_debug: Mostrar logs detallados
    
    Returns:
        Dict con resultados comparativos
    """
    config = ESCENARIOS[escenario]
    n_mr = config['n_mr']
    n_rp = config['n_rp']
    
    print("="*80)
    print(f"REDISTRITACIÓN Y SIMULACIÓN ELECTORAL")
    print("="*80)
    print(f"\nEscenario: {config['nombre']}")
    print(f"Descripción: {config['descripcion']}")
    print(f"Configuración: {n_mr} MR + {n_rp} RP = {n_mr + n_rp} total")
    print("="*80)
    
    # =========================================================================
    # PASO 1: REDISTRITACIÓN (MÓDULOS A + B)
    # =========================================================================
    
    print("\n" + "─"*80)
    print("FASE 1: REDISTRITACIÓN")
    print("─"*80)
    
    # Cargar secciones
    print("\n[1.1] Cargando secciones del INE...")
    inicio_carga = time.time()
    secciones = cargar_secciones_ine()
    print(f"✓ {len(secciones):,} secciones cargadas en {time.time()-inicio_carga:.2f}s")
    
    # Repartir distritos por estado
    print("\n[1.2] Repartiendo distritos por estado (Hare)...")
    poblacion_por_estado = secciones.groupby('ENTIDAD')['POBTOT'].sum().to_dict()
    
    asignacion_distritos = repartir_distritos_hare(
        poblacion_estados=poblacion_por_estado,
        n_distritos=n_mr,
        piso_constitucional=2
    )
    print(f"✓ {sum(asignacion_distritos.values())} distritos asignados a {len(asignacion_distritos)} estados")
    
    # Distritar cada estado
    print("\n[1.3] Distritando cada estado...")
    distritacion_resultado = {}
    tiempo_total_distritacion = 0
    
    for entidad_id, n_distritos in asignacion_distritos.items():
        secciones_estado = secciones[secciones['ENTIDAD'] == entidad_id].copy()
        
        if len(secciones_estado) == 0:
            continue
        
        print(f"  Estado {entidad_id}: {len(secciones_estado):,} secciones → {n_distritos} distritos", end=" ")
        
        inicio = time.time()
        asignacion, reporte = distritar_estado(
            secciones_estado=secciones_estado,
            n_distritos=n_distritos,
            metodo_semillas='municipios',
            print_debug=False  # Silencioso para no saturar output
        )
        tiempo = time.time() - inicio
        tiempo_total_distritacion += tiempo
        
        # Crear DataFrame con DISTRITO_NEW
        secciones_estado['DISTRITO_NEW'] = 0
        for distrito_id, seccion_ids in asignacion.items():
            mask = secciones_estado['ID'].isin(seccion_ids)
            secciones_estado.loc[mask, 'DISTRITO_NEW'] = distrito_id
        
        distritacion_resultado[entidad_id] = secciones_estado
        
        cumplen = reporte['cumple_15pct'].sum()
        print(f"({cumplen}/{n_distritos} cumplen ±15%, {tiempo:.2f}s)")
    
    print(f"\n✓ Distritación completada en {tiempo_total_distritacion:.2f}s")
    
    # =========================================================================
    # PASO 2: TABLA PUENTE Y REAGREGACIÓN (MÓDULO C)
    # =========================================================================
    
    print("\n" + "─"*80)
    print("FASE 2: REAGREGACIÓN DE VOTOS")
    print("─"*80)
    
    votos_parquet = f'data/computos_diputados_{anio}.parquet'
    
    tabla_puente, votos_reagregados, siglado_new = pipeline_tabla_puente(
        distritacion_resultado=distritacion_resultado,
        votos_parquet_path=votos_parquet,
        output_dir='redistritacion/outputs',
        escenario_nombre=escenario,
        print_debug=print_debug
    )
    
    # =========================================================================
    # PASO 3: CALCULAR RESULTADOS CON MOTOR ELECTORAL
    # =========================================================================
    
    print("\n" + "─"*80)
    print("FASE 3: CÁLCULO ELECTORAL")
    print("─"*80)
    
    # A) Resultado BASELINE (300-200 con cartografía actual)
    print("\n[3.1] Calculando BASELINE (300-200 cartografía actual)...")
    
    resultado_baseline = procesar_diputados_v2(
        path_parquet=votos_parquet,
        anio=anio,
        path_siglado=f'data/siglado-diputados-{anio}.csv',
        max_seats=500,
        sistema='mixto',
        mr_seats=300,
        rp_seats=200,
        usar_coaliciones=True,
        sobrerrepresentacion=8.0,
        umbral=0.03,
        print_debug=False
    )
    
    print("✓ Baseline calculado")
    
    # B) Resultado REFORMA (200-200 con nueva cartografía)
    print(f"\n[3.2] Calculando REFORMA ({n_mr}-{n_rp} nueva cartografía)...")
    
    # Usar votos reagregados y siglado nuevo
    votos_reagregados_path = f'redistritacion/outputs/votos_reagregados_{escenario}.parquet'
    siglado_new_path = f'redistritacion/outputs/siglado_{escenario}.csv'
    
    resultado_reforma = procesar_diputados_v2(
        path_parquet=votos_reagregados_path,
        anio=anio,
        path_siglado=siglado_new_path,
        max_seats=400,
        sistema='mixto',
        mr_seats=n_mr,
        rp_seats=n_rp,
        usar_coaliciones=True,
        sobrerrepresentacion=8.0,
        umbral=0.03,
        print_debug=False
    )
    
    print("✓ Reforma calculada")
    
    # =========================================================================
    # PASO 4: COMPARAR RESULTADOS
    # =========================================================================
    
    print("\n" + "="*80)
    print("COMPARACIÓN DE RESULTADOS")
    print("="*80)
    
    # Extraer partidos principales
    partidos = list(resultado_baseline['tot'].keys())
    
    # Crear tabla comparativa
    comparacion = []
    
    for partido in partidos:
        baseline_mr = resultado_baseline['mr'].get(partido, 0)
        baseline_rp = resultado_baseline['rp'].get(partido, 0)
        baseline_tot = resultado_baseline['tot'].get(partido, 0)
        
        reforma_mr = resultado_reforma['mr'].get(partido, 0)
        reforma_rp = resultado_reforma['rp'].get(partido, 0)
        reforma_tot = resultado_reforma['tot'].get(partido, 0)
        
        comparacion.append({
            'PARTIDO': partido,
            'BASELINE_MR': baseline_mr,
            'BASELINE_RP': baseline_rp,
            'BASELINE_TOT': baseline_tot,
            'REFORMA_MR': reforma_mr,
            'REFORMA_RP': reforma_rp,
            'REFORMA_TOT': reforma_tot,
            'DIFF_MR': reforma_mr - baseline_mr,
            'DIFF_RP': reforma_rp - baseline_rp,
            'DIFF_TOT': reforma_tot - baseline_tot
        })
    
    df_comparacion = pd.DataFrame(comparacion)
    df_comparacion = df_comparacion.sort_values('BASELINE_TOT', ascending=False)
    
    print("\n📊 Tabla Comparativa:")
    print(df_comparacion.to_string(index=False))
    
    # Guardar resultados
    output_path = f'redistritacion/outputs/comparacion_{escenario}_vs_baseline.csv'
    df_comparacion.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n✓ Resultados guardados en: {output_path}")
    
    # Resumen
    print("\n" + "─"*80)
    print("RESUMEN")
    print("─"*80)
    print(f"\nBASELINE (300-200 = 500 escaños):")
    print(f"  Total asignado: {sum(resultado_baseline['tot'].values())}")
    gallagher_baseline = resultado_baseline['meta'].get('gallagher_rp', 'N/A')
    if isinstance(gallagher_baseline, (int, float)):
        print(f"  Gallagher: {gallagher_baseline:.3f}")
    else:
        print(f"  Gallagher: {gallagher_baseline}")
    
    print(f"\nREFORMA ({n_mr}-{n_rp} = {n_mr + n_rp} escaños):")
    print(f"  Total asignado: {sum(resultado_reforma['tot'].values())}")
    gallagher_reforma = resultado_reforma['meta'].get('gallagher_rp', 'N/A')
    if isinstance(gallagher_reforma, (int, float)):
        print(f"  Gallagher: {gallagher_reforma:.3f}")
    else:
        print(f"  Gallagher: {gallagher_reforma}")
    
    # Cambios netos
    print(f"\nCAMBIOS NETOS (Reforma - Baseline):")
    for _, row in df_comparacion.iterrows():
        if row['DIFF_TOT'] != 0:
            signo = '+' if row['DIFF_TOT'] > 0 else ''
            print(f"  {row['PARTIDO']}: {signo}{row['DIFF_TOT']} (MR: {signo}{row['DIFF_MR']}, RP: {signo}{row['DIFF_RP']})")
    
    print("\n" + "="*80)
    
    return {
        'baseline': resultado_baseline,
        'reforma': resultado_reforma,
        'comparacion': df_comparacion,
        'tabla_puente': tabla_puente,
        'votos_reagregados': votos_reagregados,
        'siglado_new': siglado_new
    }


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Redistritación y simulación electoral')
    parser.add_argument('--escenario', default='reforma_200_200', 
                        help='Escenario a ejecutar (reforma_200_200, reforma_400_0, etc.)')
    parser.add_argument('--anio', type=int, default=2024,
                        help='Año electoral')
    parser.add_argument('--debug', action='store_true',
                        help='Mostrar logs detallados')
    
    args = parser.parse_args()
    
    resultado = ejecutar_redistritacion_completa(
        escenario=args.escenario,
        anio=args.anio,
        print_debug=args.debug
    )
    
    print("\n✅ Proceso completado exitosamente")
