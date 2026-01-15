"""
Genera tabla comparativa de MAYORÍA SIMPLE para diferentes escenarios.

Compara:
- Senado (vigente, plan_a, plan_c)
- Diputados (300-100, 200-200, 240-160)

Para MORENA con mayoría simple.
"""

import requests
import pandas as pd
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000"
PARTIDO = "MORENA"
TIPO_MAYORIA = "simple"
ANIO_SENADO = 2024
ANIO_DIPUTADOS = 2024
APLICAR_TOPES = True

def calcular_mayoria_senado(plan):
    """Calcula mayoría simple para Senado en un plan."""
    url = f"{BASE_URL}/calcular/mayoria_forzada_senado"
    params = {
        "partido": PARTIDO,
        "tipo_mayoria": TIPO_MAYORIA,
        "plan": plan,
        "aplicar_topes": APLICAR_TOPES,
        "anio": ANIO_SENADO
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error en plan {plan}: {e}")
        return None

def calcular_mayoria_diputados(plan):
    """Calcula mayoría simple para Diputados en un plan."""
    url = f"{BASE_URL}/calcular/mayoria_forzada"
    params = {
        "partido": PARTIDO,
        "tipo_mayoria": TIPO_MAYORIA,
        "plan": plan,
        "aplicar_topes": APLICAR_TOPES
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error en plan {plan}: {e}")
        return None

def generar_tabla_comparativa():
    """Genera tabla comparativa de mayoría simple."""
    
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
        resultado = calcular_mayoria_senado(plan_id)
        
        if resultado and resultado.get('viable'):
            info = {
                'Plan': descripcion,
                'Total Senadores': resultado.get('total_senadores', 128),
                'Necesarios (>50%)': resultado.get('senadores_necesarios', 65),
                'Obtenidos': resultado.get('senadores_obtenidos', 0),
                '% Votos Necesario': f"{resultado.get('votos_porcentaje', 0)}%",
                'Estados Ganados': f"{resultado.get('estados_ganados', 0)}/32",
                'Viable': '✅' if resultado.get('viable') else '❌'
            }
            resultados_senado.append(info)
            
            print(f"  ✅ Viable: {resultado.get('votos_porcentaje')}% votos, {resultado.get('estados_ganados')} estados")
            print(f"     Obtendrías: {resultado.get('senadores_obtenidos')} senadores")
        else:
            print(f"  ❌ No viable o error")
    
    # Crear DataFrame Senado
    df_senado = pd.DataFrame(resultados_senado)
    
    print("\n" + "="*80)
    print("📋 TABLA RESUMEN - SENADO")
    print("="*80)
    print(df_senado.to_string(index=False))
    
    # ========================
    # DIPUTADOS
    # ========================
    print("\n\n📊 DIPUTADOS - Mayoría Simple (>200 diputados, 50%)")
    print("-"*80)
    
    planes_diputados = [
        ("300_100_con_topes", "Sistema Vigente (300 MR + 100 RP con topes)"),
        ("300_100_sin_topes", "300 MR + 100 RP sin topes"),
        ("200_200_sin_topes", "Plan 200-200 (200 MR + 200 RP)"),
        ("240_160_sin_topes", "Plan 240-160 (240 MR + 160 RP)")
    ]
    
    resultados_diputados = []
    
    for plan_id, descripcion in planes_diputados:
        print(f"\n🔍 Calculando: {descripcion}...")
        resultado = calcular_mayoria_diputados(plan_id)
        
        if resultado and resultado.get('viable'):
            info = {
                'Plan': descripcion,
                'Total Diputados': resultado.get('total_diputados', 400),
                'Necesarios (>50%)': resultado.get('diputados_necesarios', 201),
                'Obtenidos': resultado.get('diputados_obtenidos', 0),
                '% Votos Necesario': f"{resultado.get('votos_porcentaje', 0)}%",
                'Distritos MR': f"{resultado.get('distritos_ganados', 0)}/{resultado.get('total_distritos', 300)}",
                'Viable': '✅' if resultado.get('viable') else '❌'
            }
            resultados_diputados.append(info)
            
            print(f"  ✅ Viable: {resultado.get('votos_porcentaje')}% votos")
            print(f"     Obtendrías: {resultado.get('diputados_obtenidos')} diputados")
            print(f"     MR ganados: {resultado.get('distritos_ganados')} de {resultado.get('total_distritos', 300)}")
        else:
            print(f"  ❌ No viable o error")
    
    # Crear DataFrame Diputados
    df_diputados = pd.DataFrame(resultados_diputados)
    
    print("\n" + "="*80)
    print("📋 TABLA RESUMEN - DIPUTADOS")
    print("="*80)
    print(df_diputados.to_string(index=False))
    
    # ========================
    # EXPORTAR A CSV
    # ========================
    print("\n" + "="*80)
    print("💾 EXPORTANDO RESULTADOS...")
    print("="*80)
    
    # Crear timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Exportar Senado
    csv_senado = f"outputs/comparativa_mayoria_simple_senado_{timestamp}.csv"
    df_senado.to_csv(csv_senado, index=False, encoding='utf-8-sig')
    print(f"✅ Senado guardado en: {csv_senado}")
    
    # Exportar Diputados
    csv_diputados = f"outputs/comparativa_mayoria_simple_diputados_{timestamp}.csv"
    df_diputados.to_csv(csv_diputados, index=False, encoding='utf-8-sig')
    print(f"✅ Diputados guardado en: {csv_diputados}")
    
    # Exportar consolidado
    with open(f"outputs/comparativa_mayoria_simple_completa_{timestamp}.txt", 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("TABLA COMPARATIVA - MAYORÍA SIMPLE\n")
        f.write(f"Partido: {PARTIDO}\n")
        f.write(f"Tipo: Mayoría Simple (>50%)\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write("="*80 + "\n\n")
        
        f.write("SENADO\n")
        f.write("-"*80 + "\n")
        f.write(df_senado.to_string(index=False))
        f.write("\n\n")
        
        f.write("DIPUTADOS\n")
        f.write("-"*80 + "\n")
        f.write(df_diputados.to_string(index=False))
        f.write("\n")
    
    print(f"✅ Reporte completo en: outputs/comparativa_mayoria_simple_completa_{timestamp}.txt")
    
    print("\n" + "="*80)
    print("✅ PROCESO COMPLETADO")
    print("="*80)
    
    return df_senado, df_diputados

if __name__ == '__main__':
    print("\n🚀 Iniciando generación de tabla comparativa...")
    print("⚠️  IMPORTANTE: Asegúrate de que el servidor esté corriendo:")
    print("   uvicorn main:app --reload --port 8000\n")
    
    input("Presiona ENTER para continuar...")
    
    try:
        df_senado, df_diputados = generar_tabla_comparativa()
        print("\n🎉 ¡Tablas generadas exitosamente!")
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: No se pudo conectar al servidor")
        print("   Ejecuta primero: uvicorn main:app --reload --port 8000")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
