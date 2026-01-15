"""
Script para probar MÓDULO B: Distritación completa del país
Prueba con escenario 200-200 (200 MR)
"""

import sys
import os
import time
from pathlib import Path

# Agregar path del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

from redistritacion.config import ESCENARIOS
from redistritacion.modulos.reparto_distritos import repartir_distritos_hare
from redistritacion.modulos.distritacion import cargar_secciones_ine, distritar_estado

def main():
    print("="*80)
    print("DISTRITACIÓN COMPLETA DE MÉXICO")
    print("="*80)
    
    # Configurar escenario
    escenario = 'reforma_200_200'
    config = ESCENARIOS[escenario]
    n_mr = config['n_mr']
    
    print(f"\nEscenario: {config['nombre']}")
    print(f"Distritos MR totales: {n_mr}")
    
    # 1. Cargar secciones
    print("\n" + "─"*80)
    print("PASO 1: Cargando secciones del INE...")
    print("─"*80)
    
    inicio_carga = time.time()
    secciones = cargar_secciones_ine()
    tiempo_carga = time.time() - inicio_carga
    
    print(f"✓ {len(secciones):,} secciones cargadas en {tiempo_carga:.2f}s")
    print(f"  Población total: {secciones['POBTOT'].sum():,}")
    print(f"  Estados: {secciones['ENTIDAD'].nunique()}")
    
    # 2. Repartir distritos por estado
    print("\n" + "─"*80)
    print("PASO 2: Repartiendo distritos por estado (Hare)...")
    print("─"*80)
    
    # Calcular población por estado
    poblacion_por_estado = secciones.groupby('ENTIDAD')['POBTOT'].sum().to_dict()
    
    inicio_reparto = time.time()
    asignacion_distritos = repartir_distritos_hare(
        poblacion_estados=poblacion_por_estado,
        n_distritos=n_mr,
        piso_constitucional=2
    )
    tiempo_reparto = time.time() - inicio_reparto
    
    print(f"✓ Reparto completado en {tiempo_reparto:.2f}s")
    
    # Crear DataFrame de reparto para iterar
    import pandas as pd
    reparto_data = []
    for entidad_id, n_dist in asignacion_distritos.items():
        pob = poblacion_por_estado.get(entidad_id, 0)
        reparto_data.append({
            'entidad_id': entidad_id,
            'entidad_nombre': f'Estado_{entidad_id}',  # Placeholder
            'distritos_asignados': n_dist,
            'poblacion': pob
        })
    reparto = pd.DataFrame(reparto_data)
    
    print(f"\nResumen reparto:")
    print(f"  Total distritos: {reparto['distritos_asignados'].sum()}")
    print(f"  Mínimo por estado: {reparto['distritos_asignados'].min()}")
    print(f"  Máximo por estado: {reparto['distritos_asignados'].max()}")
    
    # 3. Distritar cada estado
    print("\n" + "="*80)
    print("PASO 3: DISTRITACIÓN POR ESTADO")
    print("="*80)
    
    todos_resultados = []
    tiempo_total_distritacion = 0
    
    for idx, row in reparto.iterrows():
        entidad_id = row['entidad_id']
        entidad_nombre = row['entidad_nombre']
        n_distritos = row['distritos_asignados']
        
        # Filtrar secciones del estado
        secciones_estado = secciones[secciones['ENTIDAD'] == entidad_id].copy()
        
        if len(secciones_estado) == 0:
            print(f"\n⚠ {entidad_nombre}: Sin secciones, omitiendo...")
            continue
        
        print(f"\n{'─'*80}")
        print(f"Estado {idx+1}/32: {entidad_nombre}")
        print(f"{'─'*80}")
        print(f"  Secciones: {len(secciones_estado):,}")
        print(f"  Población: {secciones_estado['POBTOT'].sum():,}")
        print(f"  Distritos a crear: {n_distritos}")
        
        # Distritar estado
        inicio_estado = time.time()
        
        try:
            asignacion, reporte = distritar_estado(
                secciones_estado=secciones_estado,
                n_distritos=n_distritos,
                metodo_semillas='municipios',
                print_debug=True  # Mostrar progreso
            )
            
            tiempo_estado = time.time() - inicio_estado
            tiempo_total_distritacion += tiempo_estado
            
            # Validación
            total_asignadas = sum(len(secs) for secs in asignacion.values())
            cumplen = reporte['cumple_15pct'].sum()
            desv_prom = reporte['desviacion_pct'].abs().mean()
            
            print(f"\n  ✓ Completado en {tiempo_estado:.2f}s")
            print(f"    Secciones asignadas: {total_asignadas}/{len(secciones_estado)}")
            print(f"    Distritos que cumplen ±15%: {cumplen}/{n_distritos}")
            print(f"    Desviación promedio: {desv_prom:.2f}%")
            
            # Guardar resultado
            reporte['entidad_id'] = entidad_id
            reporte['entidad_nombre'] = entidad_nombre
            todos_resultados.append(reporte)
            
            if total_asignadas != len(secciones_estado):
                print(f"    ⚠ Advertencia: Faltan {len(secciones_estado) - total_asignadas} secciones")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            continue
    
    # 4. Resumen final
    print("\n" + "="*80)
    print("RESUMEN FINAL")
    print("="*80)
    
    import pandas as pd
    if todos_resultados:
        df_final = pd.concat(todos_resultados, ignore_index=True)
        
        print(f"\nEstados procesados: {df_final['entidad_nombre'].nunique()}")
        print(f"Distritos creados: {len(df_final)}")
        print(f"Distritos que cumplen ±15%: {df_final['cumple_15pct'].sum()}")
        print(f"Tasa de cumplimiento: {df_final['cumple_15pct'].mean()*100:.1f}%")
        print(f"\nDesviación poblacional:")
        print(f"  Promedio: {df_final['desviacion_pct'].abs().mean():.2f}%")
        print(f"  Mínima: {df_final['desviacion_pct'].abs().min():.2f}%")
        print(f"  Máxima: {df_final['desviacion_pct'].abs().max():.2f}%")
        
        print(f"\nTiempos de ejecución:")
        print(f"  Carga datos: {tiempo_carga:.2f}s")
        print(f"  Reparto Hare: {tiempo_reparto:.2f}s")
        print(f"  Distritación total: {tiempo_total_distritacion:.2f}s")
        print(f"  TIEMPO TOTAL: {tiempo_carga + tiempo_reparto + tiempo_total_distritacion:.2f}s")
        
        # Guardar resultados
        output_path = Path(__file__).parent / 'outputs' / f'distritacion_{config["nombre"].replace(" ", "_")}_validacion.csv'
        output_path.parent.mkdir(exist_ok=True)
        df_final.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\n✓ Resultados guardados en: {output_path}")
    else:
        print("\n✗ No se procesó ningún estado")
    
    print("\n" + "="*80)

if __name__ == '__main__':
    main()
