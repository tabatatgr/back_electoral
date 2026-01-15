"""
Genera tabla comparativa de MAYORÍA SIMPLE - DIRECTO (sin servidor)

Usa directamente las funciones del motor para generar comparativas rápidas.
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

# Agregar path del proyecto
sys.path.insert(0, str(Path(__file__).parent))

from engine.calcular_mayoria_forzada_senado import calcular_mayoria_forzada_senado
from engine.calcular_mayoria_forzada import calcular_mayoria_forzada

# Configuración
PARTIDO = "MORENA"
TIPO_MAYORIA = "simple"
ANIO_SENADO = 2024
ANIO_DIPUTADOS = 2024
APLICAR_TOPES = True

print("="*80)
print("🏛️  TABLA COMPARATIVA - MAYORÍA SIMPLE")
print(f"Partido: {PARTIDO}")
print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("="*80)

# ========================
# SENADO
# ========================
print("\n📊 SENADO - Mayoría Simple (>64 senadores, 50%)")
print("-"*80)

planes_senado = [
    ("vigente", "Sistema Vigente (64 MR + 32 PM + 32 RP = 128)"),
    ("plan_a", "Plan A (96 RP puro)"),
    ("plan_c", "Plan C (64 MR+PM sin RP)")
]

resultados_senado = []

for plan_id, descripcion in planes_senado:
    print(f"\n🔍 Calculando: {descripcion}...")
    
    try:
        resultado = calcular_mayoria_forzada_senado(
            partido=PARTIDO,
            tipo_mayoria=TIPO_MAYORIA,
            plan=plan_id,
            aplicar_topes=APLICAR_TOPES,
            anio=ANIO_SENADO
        )
        
        if resultado.get('viable'):
            info = {
                'Plan': descripcion,
                'Total Senadores': resultado.get('total_senadores', 128),
                'Necesarios (>50%)': resultado.get('senadores_necesarios', 65),
                'Obtenidos': resultado.get('senadores_obtenidos', 0),
                '% Votos Necesario': f"{resultado.get('votos_porcentaje', 0)}%",
                'Estados Ganados': f"{resultado.get('estados_ganados', 0)}/32",
                'Senadores MR': resultado.get('senadores_mr', 0),
                'Senadores RP': resultado.get('senadores_rp', 0),
                'Viable': '✅'
            }
            resultados_senado.append(info)
            
            print(f"  ✅ Viable con {resultado.get('votos_porcentaje')}% votos")
            print(f"     Estados: {resultado.get('estados_ganados')}/32")
            print(f"     Senadores: {resultado.get('senadores_obtenidos')} ({resultado.get('senadores_mr')} MR + {resultado.get('senadores_rp')} RP)")
        else:
            print(f"  ❌ No viable")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")

# Crear DataFrame Senado
df_senado = pd.DataFrame(resultados_senado)

print("\n" + "="*80)
print("📋 TABLA RESUMEN - SENADO")
print("="*80)
if not df_senado.empty:
    print(df_senado.to_string(index=False))
else:
    print("⚠️  No se pudieron calcular resultados para Senado")

# ========================
# DIPUTADOS
# ========================
print("\n\n📊 DIPUTADOS - Mayoría Simple (>200 diputados, 50%)")
print("-"*80)

planes_diputados = [
    (300, 100, True, "Sistema Vigente (300 MR + 100 RP con topes)"),
    (300, 100, False, "300 MR + 100 RP sin topes"),
    (200, 200, False, "Plan 200-200 (200 MR + 200 RP)"),
    (240, 160, False, "Plan 240-160 (240 MR + 160 RP)")
]

resultados_diputados = []

for mr, rp, topes, descripcion in planes_diputados:
    print(f"\n🔍 Calculando: {descripcion}...")
    
    try:
        resultado = calcular_mayoria_forzada(
            partido=PARTIDO,
            tipo_mayoria=TIPO_MAYORIA,
            mr_total=mr,
            rp_total=rp,
            aplicar_topes=topes
        )
        
        if resultado.get('viable'):
            total_dip = mr + rp
            info = {
                'Plan': descripcion,
                'MR Total': mr,
                'RP Total': rp,
                'Total Diputados': total_dip,
                'Necesarios (>50%)': 201,
                'Con Topes': 'Sí' if topes else 'No',
                'Viable': '✅ Sí' if resultado.get('viable') else '❌ No'
            }
            resultados_diputados.append(info)
            
            print(f"  ✅ Viable: {resultado.get('viable')}")
            if 'escanos_esperados' in resultado:
                print(f"     Escaños esperados: {resultado.get('escanos_esperados')}")
        else:
            info = {
                'Plan': descripcion,
                'MR Total': mr,
                'RP Total': rp,
                'Total Diputados': mr + rp,
                'Necesarios (>50%)': 201,
                'Con Topes': 'Sí' if topes else 'No',
                'Viable': '❌ No'
            }
            resultados_diputados.append(info)
            print(f"  ❌ No viable: {resultado.get('razon', 'Razón desconocida')}")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")

# Crear DataFrame Diputados
df_diputados = pd.DataFrame(resultados_diputados)

print("\n" + "="*80)
print("📋 TABLA RESUMEN - DIPUTADOS")
print("="*80)
if not df_diputados.empty:
    print(df_diputados.to_string(index=False))
else:
    print("⚠️  No se pudieron calcular resultados para Diputados")

# ========================
# EXPORTAR A CSV
# ========================
print("\n" + "="*80)
print("💾 EXPORTANDO RESULTADOS...")
print("="*80)

# Crear timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# Exportar Senado
if not df_senado.empty:
    csv_senado = f"outputs/mayoria_simple_senado_{timestamp}.csv"
    df_senado.to_csv(csv_senado, index=False, encoding='utf-8-sig')
    print(f"✅ Senado: {csv_senado}")

# Exportar Diputados
if not df_diputados.empty:
    csv_diputados = f"outputs/mayoria_simple_diputados_{timestamp}.csv"
    df_diputados.to_csv(csv_diputados, index=False, encoding='utf-8-sig')
    print(f"✅ Diputados: {csv_diputados}")

# Exportar reporte completo
txt_file = f"outputs/mayoria_simple_completa_{timestamp}.txt"
with open(txt_file, 'w', encoding='utf-8') as f:
    f.write("="*80 + "\n")
    f.write("COMPARATIVA DE MAYORÍA SIMPLE\n")
    f.write(f"Partido: {PARTIDO}\n")
    f.write(f"Tipo: Mayoría Simple (>50%)\n")
    f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    f.write("="*80 + "\n\n")
    
    f.write("SENADO (>64 senadores de 128)\n")
    f.write("-"*80 + "\n")
    if not df_senado.empty:
        f.write(df_senado.to_string(index=False))
    else:
        f.write("No hay resultados\n")
    f.write("\n\n")
    
    f.write("DIPUTADOS (>200 diputados de 400)\n")
    f.write("-"*80 + "\n")
    if not df_diputados.empty:
        f.write(df_diputados.to_string(index=False))
    else:
        f.write("No hay resultados\n")
    f.write("\n")

print(f"✅ Reporte: {txt_file}")

print("\n" + "="*80)
print("✅ PROCESO COMPLETADO")
print("="*80)

# Mostrar archivos generados
print("\n📁 Archivos generados en outputs/:")
import os
if os.path.exists('outputs'):
    archivos = [f for f in os.listdir('outputs') if f.startswith('mayoria_simple_')]
    archivos.sort(reverse=True)
    for archivo in archivos[:5]:  # Mostrar últimos 5
        print(f"   • {archivo}")
