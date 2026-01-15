import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from utils_pct_escanos import get_pct_escanos_2024
def grafica_morena_coalicion_todos_escenarios(df, output_dir):
    """
    Genera una sola gráfica tipo flechitas para todos los escenarios, solo MORENA y COALICIÓN TOTAL.
    El eje Y es 'Escenario - Grupo'.
    """
    escenarios = df['ESCENARIO'].unique()
    filas = []
    for escenario in escenarios:
        df_esc = df[df['ESCENARIO'] == escenario]
        # Pivot para partidos aliados
        pivot = df_esc.pivot_table(index='PARTIDO', columns='AÑO', values='PCT_ESCAÑOS', aggfunc='first')
        # MORENA
        if 'MORENA' in pivot.index:
            x1 = pivot.loc['MORENA', 2021] if 2021 in pivot.columns else None
            x2 = pivot.loc['MORENA', 2024] if 2024 in pivot.columns else None
            if x1 is not None and x2 is not None:
                filas.append({
                    'grupo': 'MORENA',
                    'escenario': escenario,
                    'x1': x1,
                    'x2': x2
                })
        # COALICIÓN TOTAL
        aliados = ['MORENA', 'PVEM', 'PT']
        if all(a in pivot.index for a in aliados):
            x1 = pivot.loc[aliados, 2021].sum() if 2021 in pivot.columns else None
            x2 = pivot.loc[aliados, 2024].sum() if 2024 in pivot.columns else None
            if x1 is not None and x2 is not None:
                filas.append({
                    'grupo': 'COALICIÓN TOTAL',
                    'escenario': escenario,
                    'x1': x1,
                    'x2': x2
                })
    # Ordenar: primero todos los escenarios MORENA, luego COALICIÓN TOTAL
    filas = sorted(filas, key=lambda d: (d['grupo'] != 'MORENA', d['escenario']))
    labels = [f"{f['escenario']} - {f['grupo']}" for f in filas]
    y_pos = range(len(filas))
    x1_vals = [f['x1'] for f in filas]
    x2_vals = [f['x2'] for f in filas]
    grupos = [f['grupo'] for f in filas]
    # Colores
    color_map = {'MORENA': MORENA_COLOR, 'COALICIÓN TOTAL': COALICION_COLOR}
    # Gráfica
    fig, ax = plt.subplots(figsize=(12, max(6, len(filas)*0.6)))
    for i, (x1, x2, grupo, fila) in enumerate(zip(x1_vals, x2_vals, grupos, filas)):
        color = color_map.get(grupo, LABEL_COLOR)
        dif = x2 - x1
        # Línea
        ax.hlines(y=i, xmin=x1, xmax=x2, color=AUMENTO_COLOR if dif>=0 else DISMINUCION_COLOR, alpha=0.5, linewidth=2.5)
        # Flecha
        if abs(dif) >= 0.01:
            ax.annotate("",
                        xy=(x2, i),
                        xytext=(x1, i),
                        arrowprops=dict(arrowstyle="->",
                                        color=AUMENTO_COLOR if dif>=0 else DISMINUCION_COLOR,
                                        linewidth=2.5,
                                        alpha=0.9))
        # Bolitas si no hay cambio
        if abs(dif) < 0.01:
            ax.scatter(x1, i, color=color, s=100, zorder=3, alpha=0.8, edgecolors='white', linewidths=1.5)
            ax.scatter(x2, i, color=color, s=100, zorder=3, alpha=0.8, edgecolors='white', linewidths=1.5)
        
        # Mostrar los valores según si crece o decrece
        from utils_pct_escanos import get_pct_escanos_2021
        camara = 'Diputados' if 'DIP' in fila['escenario'].upper() or 'DIPUT' in fila['escenario'].upper() else 'Senado'
        pct_oficial_2024 = get_pct_escanos_2024(grupo, camara)
        pct_oficial_2021 = get_pct_escanos_2021(grupo, camara)
        y_base = i + 0.05
        sep_h = 2.8  # separación horizontal mayor
        sep_v = 0.14 # separación vertical mayor
        if dif < 0:  # Decrece: 2024 a la izquierda, 2021 a la derecha
            # Izquierda: 2024 real arriba, 2024 simulado abajo
            if pct_oficial_2024 is not None:
                ax.text(x2 - sep_h, y_base + sep_v, f"{pct_oficial_2024:.1f}%", va='center', ha='right', color=LABEL_COLOR, fontweight='bold', fontsize=8)
            ax.text(x2 - sep_h, y_base - sep_v, f"{x2:.1f}%", va='center', ha='right', color=LABEL_COLOR, fontweight='bold', fontsize=8)
            # Derecha: 2021 real arriba, 2021 simulado abajo
            if pct_oficial_2021 is not None:
                ax.text(x1 + sep_h, y_base + sep_v, f"{pct_oficial_2021:.1f}%", va='center', ha='left', color=LABEL_COLOR, fontweight='bold', fontsize=8)
            ax.text(x1 + sep_h, y_base - sep_v, f"{x1:.1f}%", va='center', ha='left', color=LABEL_COLOR, fontweight='bold', fontsize=8)
        else:  # Crece o igual: 2021 a la izquierda, 2024 a la derecha
            # Izquierda: 2021 real arriba, 2021 simulado abajo
            if pct_oficial_2021 is not None:
                ax.text(x1 - sep_h, y_base + sep_v, f"{pct_oficial_2021:.1f}%", va='center', ha='right', color=LABEL_COLOR, fontweight='bold', fontsize=8)
            ax.text(x1 - sep_h, y_base - sep_v, f"{x1:.1f}%", va='center', ha='right', color=LABEL_COLOR, fontweight='bold', fontsize=8)
            # Derecha: 2024 real arriba, 2024 simulado abajo
            if pct_oficial_2024 is not None:
                ax.text(x2 + sep_h, y_base + sep_v, f"{pct_oficial_2024:.1f}%", va='center', ha='left', color=LABEL_COLOR, fontweight='bold', fontsize=8)
            ax.text(x2 + sep_h, y_base - sep_v, f"{x2:.1f}%", va='center', ha='left', color=LABEL_COLOR, fontweight='bold', fontsize=8)
    # Ejes y estilo
    ax.set_yticks(list(y_pos))
    ax.set_yticklabels(labels, color=LABEL_COLOR, fontweight='bold', fontsize=11)
    for lab in ax.get_xticklabels():
        lab.set_weight('bold')
        lab.set_color(LABEL_COLOR)
        lab.set_fontsize(10)
    ax.grid(True, axis='x', linestyle='--', linewidth=0.5, color=GRID_COLOR, alpha=0.6)
    ax.set_axisbelow(True)
    ax.set_title('Cambio % Escaños 2021 → 2024\n(MORENA y COALICIÓN TOTAL, todos los escenarios)', fontsize=13, fontweight='bold', color=LABEL_COLOR, pad=20)
    ax.set_xlabel('% de Escaños', fontweight='bold', fontsize=11, color=LABEL_COLOR, labelpad=10)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    plt.tight_layout()
    # Guardar
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    png_path = output_dir / 'morena_coalicion_todos_escenarios.png'
    svg_path = output_dir / 'morena_coalicion_todos_escenarios.svg'
    fig.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    fig.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='white')
    optimizar_svg_con_scour(svg_path)
    plt.close(fig)
"""
Genera gráficas de cambio de % escaños 2021→2024 por escenario

Para cada escenario:
1. Gráfica MORENA + Aliados (MORENA, PVEM, PT, + TOTAL COALICIÓN)
2. Gráfica TODOS los partidos

Formato: SVG (optimizado con scour) + PNG
Output: redistritacion/outputs/graficas/{escenario}/
"""

import sys
import subprocess
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Backend sin GUI

# Colores
AUMENTO_COLOR = '#1B5E20'   # Verde bosque (menos oscuro que #022F2A)
DISMINUCION_COLOR = '#671435'  # Rojo oscuro para disminuciones
GRID_COLOR = '#E0E0E0'      # Grid más suave
LABEL_COLOR = '#424242'
YEAR_COLOR = '#9E9E9E'      # Gris para los años
MORENA_COLOR = '#B8860B'    # Guinda/dorado
PVEM_COLOR = '#4CAF50'      # Verde
PT_COLOR = '#E53935'        # Rojo
COALICION_COLOR = '#5D4037' # Café oscuro

# Definir aliados de MORENA
MORENA_ALIADOS = ['MORENA', 'PVEM', 'PT']


def optimizar_svg_con_scour(svg_path):
    """
    Optimiza SVG usando scour si está disponible.
    """
    try:
        result = subprocess.run(
            ['scour', '--enable-id-stripping', '--enable-comment-stripping',
             '--shorten-ids', '--indent=none', '-i', str(svg_path), '-o', str(svg_path)],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(f"    ✓ SVG optimizado con scour: {svg_path.name}")
        else:
            print(f"    ⚠ Scour warning: {result.stderr[:100]}")
    except FileNotFoundError:
        print(f"    ⚠ scour no encontrado, SVG sin optimizar")
    except Exception as e:
        print(f"    ⚠ Error en scour: {e}")


def grafica_cambio_escenario(
    df_completo,
    escenario,
    partidos_filtro=None,
    titulo_sufijo="",
    output_dir=None,
    color_especial=None
):
    """
    Genera gráfica de cambio % escaños 2021→2024 para un escenario.
    
    Args:
        df_completo: DataFrame con todos los datos
        escenario: Nombre del escenario ('300-100 CON TOPES', etc.)
        partidos_filtro: Lista de partidos a incluir (None = todos)
        titulo_sufijo: Sufijo para el título y nombre de archivo
        output_dir: Directorio de salida
        color_especial: Dict {partido: color} para personalizar
    """
    
    # Filtrar por escenario
    df_esc = df_completo[df_completo['ESCENARIO'] == escenario].copy()
    
    if df_esc.empty:
        print(f"  ⚠ No hay datos para {escenario}")
        return
    
    # Crear pivot: Partido vs Año
    pivot = df_esc.pivot_table(
        index='PARTIDO',
        columns='AÑO',
        values='PCT_ESCAÑOS',
        aggfunc='first'
    )
    
    # Filtrar partidos si se especifica
    if partidos_filtro:
        pivot = pivot[pivot.index.isin(partidos_filtro)]
    
    # Verificar que existan ambos años
    if 2021 not in pivot.columns or 2024 not in pivot.columns:
        print(f"  ⚠ Faltan datos de 2021 o 2024 para {escenario}")
        return
    
    # Calcular diferencia
    pivot['DIF'] = pivot[2024] - pivot[2021]
    
    # Si estamos en modo MORENA+ALIADOS, agregar fila de TOTAL COALICIÓN
    coalicion_total_presente = False
    if partidos_filtro and set(partidos_filtro) == set(MORENA_ALIADOS):
        # Calcular total coalición
        total_2021 = pivot.loc[MORENA_ALIADOS, 2021].sum()
        total_2024 = pivot.loc[MORENA_ALIADOS, 2024].sum()
        total_dif = total_2024 - total_2021
        
        # Agregar fila
        nueva_fila = pd.DataFrame({
            2021: [total_2021],
            2024: [total_2024],
            'DIF': [total_dif]
        }, index=['COALICIÓN TOTAL'])
        
        pivot = pd.concat([pivot, nueva_fila])
        coalicion_total_presente = True
    
    # Ordenar: COALICIÓN TOTAL primero, otros por diferencia, MORENA al final
    if coalicion_total_presente and 'COALICIÓN TOTAL' in pivot.index:
        # Separar COALICIÓN TOTAL
        coalicion_row = pivot.loc[['COALICIÓN TOTAL']]
        otros = pivot.drop('COALICIÓN TOTAL')
        
        # Si hay MORENA, separar también
        if 'MORENA' in otros.index:
            morena_row = otros.loc[['MORENA']]
            otros = otros.drop('MORENA')
            # Ordenar otros por diferencia absoluta
            otros = otros.sort_values('DIF', key=abs, ascending=False)
            # Reordenar: COALICIÓN TOTAL, otros, MORENA
            pivot = pd.concat([coalicion_row, otros, morena_row])
        else:
            # Ordenar otros por diferencia absoluta
            otros = otros.sort_values('DIF', key=abs, ascending=False)
            # Reordenar: COALICIÓN TOTAL, otros
            pivot = pd.concat([coalicion_row, otros])
    elif 'MORENA' in pivot.index:
        # Si no hay coalición pero sí MORENA, ponerla al final
        morena_row = pivot.loc[['MORENA']]
        otros = pivot.drop('MORENA')
        otros = otros.sort_values('DIF', key=abs, ascending=False)
        pivot = pd.concat([otros, morena_row])
    else:
        # Si no hay ni coalición ni MORENA, ordenar por diferencia absoluta normal
        pivot = pivot.sort_values('DIF', key=abs, ascending=False)
    
    # Si está vacío después del filtro
    if pivot.empty:
        print(f"  ⚠ No hay datos después de filtrar para {escenario}")
        return
    
    # Preparar datos para graficar
    labels = [str(idx).upper() for idx in pivot.index]
    y_pos = range(len(pivot))
    x1_vals = pivot[2021].values
    x2_vals = pivot[2024].values
    dif_vals = pivot['DIF'].values
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(10, max(6, len(pivot) * 0.6)))
    
    # Estilo de ejes - MOSTRAR SOLO LÍNEAS DE EJES X e Y
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(GRID_COLOR)
    ax.spines['left'].set_linewidth(1)
    ax.spines['bottom'].set_color(GRID_COLOR)
    ax.spines['bottom'].set_linewidth(1)
    ax.tick_params(axis='x', colors=LABEL_COLOR, length=0)
    ax.tick_params(axis='y', colors=LABEL_COLOR, length=0)
    
    # Líneas y flechas
    for i, (x1, x2, partido, dif) in enumerate(zip(x1_vals, x2_vals, pivot.index, dif_vals)):
        # Determinar color base según partido
        if color_especial and partido in color_especial:
            color_base = color_especial[partido]
        elif partido == 'COALICIÓN TOTAL':
            color_base = COALICION_COLOR
        elif partido == 'MORENA':
            color_base = MORENA_COLOR
        elif partido == 'PVEM':
            color_base = PVEM_COLOR
        elif partido == 'PT':
            color_base = PT_COLOR
        else:
            color_base = None
        
        # Determinar color según aumento o disminución
        if dif >= 0:
            color_cambio = AUMENTO_COLOR  # Verde bosque
        else:
            color_cambio = DISMINUCION_COLOR  # Rojo oscuro
        
        # Usar color base si existe, sino usar color de cambio
        color_linea = color_base if color_base else color_cambio
        
        # SOLO MOSTRAR BOLITAS SI NO HUBO CAMBIO (dif == 0)
        if abs(dif) < 0.01:  # Prácticamente sin cambio
            # Punto inicial (2021)
            ax.scatter(x1, i, color=color_linea, s=100, zorder=3, alpha=0.8, edgecolors='white', linewidths=1.5)
            # Punto final (2024)
            ax.scatter(x2, i, color=color_linea, s=100, zorder=3, alpha=0.8, edgecolors='white', linewidths=1.5)
        
        # Línea conectora
        ax.hlines(y=i, xmin=x1, xmax=x2, color=color_cambio, alpha=0.5, linewidth=2.5)
        
        # Flecha (solo si hay cambio)
        if abs(dif) >= 0.01:
            ax.annotate("",
                        xy=(x2, i),
                        xytext=(x1, i),
                        arrowprops=dict(arrowstyle="->",
                                        color=color_cambio,
                                        linewidth=2.5,
                                        alpha=0.9))
        
        # Calcular distancia para detectar encimamiento
        distancia = abs(x2 - x1)

        # Mostrar los valores según si crece o decrece
        camara = 'Diputados' if 'DIP' in escenario.upper() or 'DIPUT' in escenario.upper() else 'Senado'
        grupo = partido if partido != 'COALICIÓN TOTAL' else 'COALICIÓN TOTAL'
        from utils_pct_escanos import get_pct_escanos_2021
        pct_oficial_2024 = get_pct_escanos_2024(grupo, camara)
        pct_oficial_2021 = get_pct_escanos_2021(grupo, camara)
        y_base = i + 0.05
        sep_h = 2.8  # separación horizontal mayor
        sep_v = 0.14 # separación vertical mayor
        if dif < 0:  # Decrece: 2024 a la izquierda, 2021 a la derecha
            # Izquierda: 2024 real arriba, 2024 simulado abajo
            if pct_oficial_2024 is not None:
                ax.text(x2 - sep_h, y_base + sep_v, f"{pct_oficial_2024:.1f}%", va='center', ha='right', color=LABEL_COLOR, fontweight='bold', fontsize=8)
            ax.text(x2 - sep_h, y_base - sep_v, f"{x2:.1f}%", va='center', ha='right', color=LABEL_COLOR, fontweight='bold', fontsize=8)
            # Derecha: 2021 real arriba, 2021 simulado abajo
            if pct_oficial_2021 is not None:
                ax.text(x1 + sep_h, y_base + sep_v, f"{pct_oficial_2021:.1f}%", va='center', ha='left', color=LABEL_COLOR, fontweight='bold', fontsize=8)
            ax.text(x1 + sep_h, y_base - sep_v, f"{x1:.1f}%", va='center', ha='left', color=LABEL_COLOR, fontweight='bold', fontsize=8)
        else:  # Crece o igual: 2021 a la izquierda, 2024 a la derecha
            # Izquierda: 2021 real arriba, 2021 simulado abajo
            if pct_oficial_2021 is not None:
                ax.text(x1 - sep_h, y_base + sep_v, f"{pct_oficial_2021:.1f}%", va='center', ha='right', color=LABEL_COLOR, fontweight='bold', fontsize=8)
            ax.text(x1 - sep_h, y_base - sep_v, f"{x1:.1f}%", va='center', ha='right', color=LABEL_COLOR, fontweight='bold', fontsize=8)
            # Derecha: 2024 real arriba, 2024 simulado abajo
            if pct_oficial_2024 is not None:
                ax.text(x2 + sep_h, y_base + sep_v, f"{pct_oficial_2024:.1f}%", va='center', ha='left', color=LABEL_COLOR, fontweight='bold', fontsize=8)
            ax.text(x2 + sep_h, y_base - sep_v, f"{x2:.1f}%", va='center', ha='left', color=LABEL_COLOR, fontweight='bold', fontsize=8)
    
    # Etiquetas del eje Y
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, color=LABEL_COLOR, fontweight='bold', fontsize=11)
    
    # Etiquetas del eje X
    for lab in ax.get_xticklabels():
        lab.set_weight('bold')
        lab.set_color(LABEL_COLOR)
        lab.set_fontsize(10)
    
    # Grid suave solo en X
    ax.grid(True, axis='x', linestyle='--', linewidth=0.5, color=GRID_COLOR, alpha=0.6)
    ax.set_axisbelow(True)
    
    # Título
    escenario_corto = escenario.replace('300-100 CON TOPES', '300 MR + 100 RP (con topes)')
    escenario_corto = escenario_corto.replace('200-200 SIN TOPES', '200 MR + 200 RP (sin topes)')
    escenario_corto = escenario_corto.replace('240-160 SIN TOPES', '240 MR + 160 RP (sin topes)')
    
    titulo = f"Cambio % Escaños 2021 → 2024{titulo_sufijo}\n{escenario_corto}"
    ax.set_title(titulo, fontsize=13, fontweight='bold', color=LABEL_COLOR, pad=20)
    ax.set_xlabel("% de Escaños", fontweight='bold', fontsize=11, color=LABEL_COLOR, labelpad=10)
    
    # Fondo blanco limpio
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    plt.tight_layout()
    
    # Guardar archivos
    nombre_archivo = escenario.replace(' ', '_').replace('/', '-')
    if titulo_sufijo:
        sufijo_archivo = titulo_sufijo.replace(' ', '_').replace(':', '').replace('\n', '')
        nombre_archivo = f"{nombre_archivo}_{sufijo_archivo}"
    
    # PNG
    png_path = output_dir / f"{nombre_archivo}.png"
    fig.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"    ✓ PNG guardado: {png_path.name}")
    
    # SVG
    svg_path = output_dir / f"{nombre_archivo}.svg"
    fig.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='white')
    print(f"    ✓ SVG guardado: {svg_path.name}")
    
    # Optimizar SVG con scour
    optimizar_svg_con_scour(svg_path)
    
    plt.close(fig)


def main():
    # Cargar datos
    csv_path = Path('redistritacion/outputs/comparacion_escenarios_completa.csv')
    if not csv_path.exists():
        print(f"❌ ERROR: No se encuentra {csv_path}")
        return
    df = pd.read_csv(csv_path)
    print(f"✓ Datos cargados: {len(df)} filas\n")

    # Gráfica extra: todos los escenarios, solo MORENA y COALICIÓN TOTAL
    print('\n' + '='*100)
    print('GRÁFICA EXTRA: TODOS LOS ESCENARIOS (MORENA y COALICIÓN TOTAL)')
    print('='*100)
    grafica_morena_coalicion_todos_escenarios(df, 'redistritacion/outputs/graficas/MORENA_COALICION_TODOS_ESCENARIOS')
    print('  ✓ Gráfica generada en redistritacion/outputs/graficas/MORENA_COALICION_TODOS_ESCENARIOS/')
    print("="*100)
    print("GENERACIÓN DE GRÁFICAS: CAMBIO % ESCAÑOS 2021→2024")
    print("="*100)
    
    # Escenarios
    escenarios = df['ESCENARIO'].unique()
    
    for escenario in escenarios:
        print(f"\n{'─'*100}")
        print(f"ESCENARIO: {escenario}")
        print(f"{'─'*100}")
        
        # Crear directorio de salida
        escenario_dir_name = escenario.replace(' ', '_').replace('/', '-')
        output_base = Path('redistritacion/outputs/graficas') / escenario_dir_name
        
        # 1. MORENA + ALIADOS
        print(f"\n  [1/2] Generando gráfica: MORENA + Aliados...")
        output_dir_morena = output_base / 'MORENA_y_Aliados'
        output_dir_morena.mkdir(parents=True, exist_ok=True)
        
        grafica_cambio_escenario(
            df_completo=df,
            escenario=escenario,
            partidos_filtro=MORENA_ALIADOS,
            titulo_sufijo=" - MORENA y Aliados",
            output_dir=output_dir_morena,
            color_especial={
                'MORENA': MORENA_COLOR,
                'PVEM': PVEM_COLOR,
                'PT': PT_COLOR,
                'COALICIÓN TOTAL': COALICION_COLOR
            }
        )
        
        # 2. TODOS LOS PARTIDOS
        print(f"\n  [2/2] Generando gráfica: Todos los Partidos...")
        output_dir_todos = output_base / 'Todos_los_Partidos'
        output_dir_todos.mkdir(parents=True, exist_ok=True)
        
        grafica_cambio_escenario(
            df_completo=df,
            escenario=escenario,
            partidos_filtro=None,  # Todos
            titulo_sufijo=" - Todos los Partidos",
            output_dir=output_dir_todos,
            color_especial={
                'MORENA': MORENA_COLOR,
                'PVEM': PVEM_COLOR,
                'PT': PT_COLOR
            }
        )
        
        print(f"\n  ✅ Gráficas completadas para {escenario}")
    
    print("\n" + "="*100)
    print("✅ PROCESO COMPLETADO")
    print("="*100)
    print("\nEstructura de salida:")
    print("redistritacion/outputs/graficas/")
    for escenario in escenarios:
        esc_dir = escenario.replace(' ', '_').replace('/', '-')
        print(f"  ├── {esc_dir}/")
        print(f"  │   ├── MORENA_y_Aliados/")
        print(f"  │   │   ├── {esc_dir}_-_MORENA_y_Aliados.png")
        print(f"  │   │   └── {esc_dir}_-_MORENA_y_Aliados.svg")
        print(f"  │   └── Todos_los_Partidos/")
        print(f"  │       ├── {esc_dir}_-_Todos_los_Partidos.png")
        print(f"  │       └── {esc_dir}_-_Todos_los_Partidos.svg")
    print()


if __name__ == '__main__':
    main()
