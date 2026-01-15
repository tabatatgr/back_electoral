"""
Genera tabla comparativa de escenarios electorales con redistritación

Escenarios:
1. 300 MR / 100 RP (con topes - sistema actual, sin redistritar)
2. 200 MR / 200 RP (sin topes - con redistritación)
3. 240 MR / 160 RP (sin topes - con redistritación)

Años: 2021 y 2024
Outputs: % de escaños por partido, total por regla, total por partido/coalición
"""

import sys
import pandas as pd
from pathlib import Path

# Agregar path del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

from redistritacion.config import ESCENARIOS
from redistritacion.modulos.reparto_distritos import repartir_distritos_hare
from redistritacion.modulos.distritacion import cargar_secciones_ine, distritar_estado
from redistritacion.modulos.tabla_puente import pipeline_tabla_puente
from engine.procesar_diputados_v2 import procesar_diputados_v2


def ejecutar_escenario(
    nombre: str,
    anio: int,
    mr_seats: int,
    rp_seats: int,
    usar_redistritacion: bool,
    aplicar_topes: bool,
    print_debug: bool = False
):
    """
    Ejecuta un escenario electoral específico.
    
    Args:
        nombre: Nombre del escenario
        anio: Año electoral (2021 o 2024)
        mr_seats: Número de distritos MR
        rp_seats: Número de diputados RP
        usar_redistritacion: Si True, redistrita; si False, usa cartografía actual
        aplicar_topes: Si True, aplica topes de sobrerrepresentación
        print_debug: Mostrar logs
    
    Returns:
        Dict con resultados
    """
    print(f"\n{'─'*80}")
    print(f"Ejecutando: {nombre} - {anio}")
    print(f"  MR: {mr_seats}, RP: {rp_seats}, Topes: {aplicar_topes}, Redistritar: {usar_redistritacion}")
    print(f"{'─'*80}")
    
    votos_parquet = f'data/computos_diputados_{anio}.parquet'
    siglado_original = f'data/siglado-diputados-{anio}.csv'
    
    # Si requiere redistritación, ejecutar pipeline
    if usar_redistritacion:
        print(f"  [1/3] Redistritando a {mr_seats} distritos...")
        
        # Cargar secciones
        secciones = cargar_secciones_ine()
        
        # Repartir distritos
        poblacion_por_estado = secciones.groupby('ENTIDAD')['POBTOT'].sum().to_dict()
        asignacion_distritos = repartir_distritos_hare(
            poblacion_estados=poblacion_por_estado,
            n_distritos=mr_seats,
            piso_constitucional=2
        )
        
        # Distritar cada estado
        distritacion_resultado = {}
        for entidad_id, n_distritos in asignacion_distritos.items():
            secciones_estado = secciones[secciones['ENTIDAD'] == entidad_id].copy()
            if len(secciones_estado) == 0:
                continue
            
            asignacion, _ = distritar_estado(
                secciones_estado=secciones_estado,
                n_distritos=n_distritos,
                metodo_semillas='municipios',
                print_debug=False
            )
            
            # Asignar DISTRITO_NEW
            secciones_estado['DISTRITO_NEW'] = 0
            for distrito_id, seccion_ids in asignacion.items():
                mask = secciones_estado['ID'].isin(seccion_ids)
                secciones_estado.loc[mask, 'DISTRITO_NEW'] = distrito_id
            
            distritacion_resultado[entidad_id] = secciones_estado
        
        print(f"  ✓ Redistritación completada")
        
        # Pipeline tabla puente
        print(f"  [2/3] Reagregando votos...")
        escenario_nombre = f"{mr_seats}_{rp_seats}_{anio}"
        _, votos_reagregados, siglado_new = pipeline_tabla_puente(
            distritacion_resultado=distritacion_resultado,
            votos_parquet_path=votos_parquet,
            output_dir='redistritacion/outputs',
            escenario_nombre=escenario_nombre,
            print_debug=False
        )
        
        # Usar votos y siglado redistritados
        votos_path = f'redistritacion/outputs/votos_reagregados_{escenario_nombre}.parquet'
        siglado_path = f'redistritacion/outputs/siglado_{escenario_nombre}.csv'
        print(f"  ✓ Votos reagregados")
    else:
        # Usar cartografía actual
        votos_path = votos_parquet
        siglado_path = siglado_original
        print(f"  Usando cartografía actual (sin redistritar)")
    
    # Calcular resultados
    print(f"  [3/3] Calculando asignación electoral...")
    
    resultado = procesar_diputados_v2(
        path_parquet=votos_path,
        anio=anio,
        path_siglado=siglado_path,
        max_seats=mr_seats + rp_seats,
        sistema='mixto',
        mr_seats=mr_seats,
        rp_seats=rp_seats,
        usar_coaliciones=True,
        sobrerrepresentacion=8.0 if aplicar_topes else None,  # Sin topes = None
        umbral=0.03,
        print_debug=False
    )
    
    print(f"  ✓ Cálculo completado")
    
    return {
        'nombre': nombre,
        'anio': anio,
        'mr_seats': mr_seats,
        'rp_seats': rp_seats,
        'total_seats': mr_seats + rp_seats,
        'topes': aplicar_topes,
        'redistritado': usar_redistritacion,
        'resultado': resultado
    }


def generar_tabla_comparativa(escenarios_resultados):
    """
    Genera tabla comparativa con todos los escenarios.
    """
    print("\n" + "="*100)
    print("GENERANDO TABLA COMPARATIVA")
    print("="*100)
    
    # Recolectar datos
    filas = []
    
    for esc in escenarios_resultados:
        nombre = esc['nombre']
        anio = esc['anio']
        mr_seats = esc['mr_seats']
        rp_seats = esc['rp_seats']
        total = esc['total_seats']
        resultado = esc['resultado']
        
        mr_dict = resultado['mr']
        rp_dict = resultado['rp']
        tot_dict = resultado['tot']
        
        # Por cada partido
        for partido in tot_dict.keys():
            mr = mr_dict.get(partido, 0)
            rp = rp_dict.get(partido, 0)
            tot = tot_dict.get(partido, 0)
            pct = (tot / total * 100) if total > 0 else 0
            
            filas.append({
                'ESCENARIO': nombre,
                'AÑO': anio,
                'MR': mr_seats,
                'RP': rp_seats,
                'TOTAL_ESCAÑOS': total,
                'PARTIDO': partido,
                'ESCAÑOS_MR': mr,
                'ESCAÑOS_RP': rp,
                'ESCAÑOS_TOTAL': tot,
                'PCT_ESCAÑOS': round(pct, 2)
            })
    
    df = pd.DataFrame(filas)
    
    # Guardar tabla completa
    output_path = 'redistritacion/outputs/comparacion_escenarios_completa.csv'
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n✓ Tabla completa guardada en: {output_path}")
    
    return df


def imprimir_resumen_por_escenario(df):
    """
    Imprime resumen agrupado por escenario y año.
    """
    print("\n" + "="*100)
    print("RESUMEN POR ESCENARIO Y AÑO")
    print("="*100)
    
    for (escenario, anio), grupo in df.groupby(['ESCENARIO', 'AÑO']):
        print(f"\n{'─'*100}")
        print(f"{escenario} - {anio}")
        mr = grupo['MR'].iloc[0]
        rp = grupo['RP'].iloc[0]
        total = grupo['TOTAL_ESCAÑOS'].iloc[0]
        print(f"Configuración: {mr} MR + {rp} RP = {total} escaños")
        print(f"{'─'*100}")
        
        # Tabla por partido
        resumen = grupo[['PARTIDO', 'ESCAÑOS_MR', 'ESCAÑOS_RP', 'ESCAÑOS_TOTAL', 'PCT_ESCAÑOS']].copy()
        resumen = resumen.sort_values('ESCAÑOS_TOTAL', ascending=False)
        
        print(resumen.to_string(index=False))
        
        # Totales
        print(f"\nTOTAL MR: {resumen['ESCAÑOS_MR'].sum()}")
        print(f"TOTAL RP: {resumen['ESCAÑOS_RP'].sum()}")
        print(f"TOTAL: {resumen['ESCAÑOS_TOTAL'].sum()}")


def generar_tabla_pivote(df):
    """
    Genera tabla pivote comparativa entre escenarios.
    """
    print("\n" + "="*100)
    print("TABLA PIVOTE: COMPARACIÓN ENTRE ESCENARIOS")
    print("="*100)
    
    for anio in df['AÑO'].unique():
        print(f"\n{'─'*100}")
        print(f"AÑO {anio}")
        print(f"{'─'*100}")
        
        df_anio = df[df['AÑO'] == anio].copy()
        
        # Pivote: Partidos en filas, Escenarios en columnas
        pivot = df_anio.pivot_table(
            index='PARTIDO',
            columns='ESCENARIO',
            values='ESCAÑOS_TOTAL',
            aggfunc='sum',
            fill_value=0
        )
        
        # Ordenar por total del primer escenario
        pivot = pivot.sort_values(by=pivot.columns[0], ascending=False)
        
        print(pivot.to_string())
        
        # Guardar pivote
        output_path = f'redistritacion/outputs/pivote_escenarios_{anio}.csv'
        pivot.to_csv(output_path, encoding='utf-8-sig')
        print(f"\n✓ Pivote {anio} guardado en: {output_path}")


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    print("="*100)
    print("COMPARACIÓN DE ESCENARIOS ELECTORALES CON REDISTRITACIÓN")
    print("="*100)
    
    # Definir escenarios
    escenarios_config = [
        # ESCENARIO 1: 300-100 CON TOPES (BASELINE - SIN REDISTRITAR)
        {
            'nombre': '300-100 CON TOPES',
            'mr': 300,
            'rp': 100,
            'redistritar': False,
            'topes': True,
            'años': [2021, 2024]
        },
        # ESCENARIO 2: 200-200 SIN TOPES (CON REDISTRITACIÓN)
        {
            'nombre': '200-200 SIN TOPES',
            'mr': 200,
            'rp': 200,
            'redistritar': True,
            'topes': False,
            'años': [2021, 2024]
        },
        # ESCENARIO 3: 240-160 SIN TOPES (CON REDISTRITACIÓN)
        {
            'nombre': '240-160 SIN TOPES',
            'mr': 240,
            'rp': 160,
            'redistritar': True,
            'topes': False,
            'años': [2021, 2024]
        },
        # ESCENARIO 4: 240-160 CON TOPES (CON REDISTRITACIÓN)
        {
            'nombre': '240-160 CON TOPES',
            'mr': 240,
            'rp': 160,
            'redistritar': True,
            'topes': True,
            'años': [2021, 2024]
        }
    ]
    
    # Ejecutar todos los escenarios
    todos_resultados = []
    
    for config in escenarios_config:
        for anio in config['años']:
            resultado = ejecutar_escenario(
                nombre=config['nombre'],
                anio=anio,
                mr_seats=config['mr'],
                rp_seats=config['rp'],
                usar_redistritacion=config['redistritar'],
                aplicar_topes=config['topes'],
                print_debug=False
            )
            todos_resultados.append(resultado)
    
    # Generar tabla comparativa
    df = generar_tabla_comparativa(todos_resultados)
    
    # Imprimir resúmenes
    imprimir_resumen_por_escenario(df)
    generar_tabla_pivote(df)
    
    print("\n" + "="*100)
    print("✅ PROCESO COMPLETADO")
    print("="*100)
    print("\nArchivos generados:")
    print("  - redistritacion/outputs/comparacion_escenarios_completa.csv")
    print("  - redistritacion/outputs/pivote_escenarios_2021.csv")
    print("  - redistritacion/outputs/pivote_escenarios_2024.csv")
    print("\n")


if __name__ == '__main__':
    main()
