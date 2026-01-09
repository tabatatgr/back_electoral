"""
Generar tabla comparativa de escenarios 2021 vs 2024
Con 4 configuraciones diferentes y análisis por partido
"""
import requests
import pandas as pd
import json
from datetime import datetime

print("=" * 80)
print("📊 GENERANDO TABLA COMPARATIVA DE ESCENARIOS 2021 vs 2024")
print("=" * 80)

# Definición de escenarios
escenarios = [
    {
        "id": 1,
        "nombre": "MR 200 - RP 200",
        "descripcion": "Mayoría Relativa 200 - Representación Proporcional 200",
        "params": {
            "plan": "personalizado",
            "escanos_totales": 400,
            "sistema": "mixto",
            "mr_seats": 200,
            "rp_seats": 200,
            "pm_seats": 0,
            "umbral": 0.03,
            "aplicar_topes": True,
            "sobrerrepresentacion": 8.0,
            "max_seats_per_party": 300
        }
    },
    {
        "id": 2,
        "nombre": "MR 300 - RP 100",
        "descripcion": "Mayoría Relativa 300 - Representación Proporcional 100",
        "params": {
            "plan": "personalizado",
            "escanos_totales": 400,
            "sistema": "mixto",
            "mr_seats": 300,
            "rp_seats": 100,
            "pm_seats": 0,
            "umbral": 0.03,
            "aplicar_topes": True,
            "sobrerrepresentacion": 8.0,
            "max_seats_per_party": 300
        }
    },
    {
        "id": 3,
        "nombre": "MR 200 - PM 200",
        "descripcion": "Mayoría Relativa 200 - Primera Minoría 200",
        "params": {
            "plan": "personalizado",
            "escanos_totales": 400,
            "sistema": "mr",  # Solo MR+PM, sin RP
            "mr_seats": 200,
            "rp_seats": 0,
            "pm_seats": 200,
            "umbral": 0.03,
            "aplicar_topes": True,
            "sobrerrepresentacion": 8.0,
            "max_seats_per_party": 300
        }
    },
    {
        "id": 4,
        "nombre": "MR 300 - PM 100",
        "descripcion": "Mayoría Relativa 300 - Primera Minoría 100",
        "params": {
            "plan": "personalizado",
            "escanos_totales": 400,
            "sistema": "mr",  # Solo MR+PM, sin RP
            "mr_seats": 300,
            "rp_seats": 0,
            "pm_seats": 100,
            "umbral": 0.03,
            "aplicar_topes": True,
            "sobrerrepresentacion": 8.0,
            "max_seats_per_party": 300
        }
    }
]

# Función para consultar API
def obtener_resultados(anio, escenario):
    """Consulta el API y devuelve resultados por partido"""
    url = f"http://localhost:8000/procesar/diputados"
    
    params = escenario["params"].copy()
    params["anio"] = anio
    
    try:
        # Construir query string
        query_parts = [f"{k}={v}" for k, v in params.items()]
        full_url = url + "?" + "&".join(query_parts)
        
        print(f"  Consultando: {anio} - {escenario['nombre']}...", end=" ")
        
        response = requests.post(full_url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✓")
            return data.get("resultados", [])
        else:
            print(f"✗ (Error {response.status_code})")
            return []
    except Exception as e:
        print(f"✗ (Error: {e})")
        return []

# Recolectar todos los datos
print("\n🔄 Consultando API para todos los escenarios...")
print("-" * 80)

todos_los_datos = []

for escenario in escenarios:
    print(f"\n📋 Escenario {escenario['id']}: {escenario['nombre']}")
    
    # Obtener datos 2021
    resultados_2021 = obtener_resultados(2021, escenario)
    
    # Obtener datos 2024
    resultados_2024 = obtener_resultados(2024, escenario)
    
    # Procesar resultados por partido
    if resultados_2021 and resultados_2024:
        # Crear diccionario de partidos 2021
        partidos_2021 = {r['partido']: r for r in resultados_2021}
        partidos_2024 = {r['partido']: r for r in resultados_2024}
        
        # Combinar todos los partidos únicos
        todos_partidos = set(partidos_2021.keys()) | set(partidos_2024.keys())
        
        for partido in sorted(todos_partidos):
            datos_2021 = partidos_2021.get(partido, {})
            datos_2024 = partidos_2024.get(partido, {})
            
            # Extraer escaños
            mr_2021 = datos_2021.get('mr', 0)
            pm_2021 = datos_2021.get('pm', 0)
            rp_2021 = datos_2021.get('rp', 0)
            total_2021 = datos_2021.get('total', 0)
            
            mr_2024 = datos_2024.get('mr', 0)
            pm_2024 = datos_2024.get('pm', 0)
            rp_2024 = datos_2024.get('rp', 0)
            total_2024 = datos_2024.get('total', 0)
            
            # Calcular diferencias (2024 - 2021)
            diff_mr = mr_2024 - mr_2021
            diff_pm = pm_2024 - pm_2021
            diff_rp = rp_2024 - rp_2021
            diff_total = total_2024 - total_2021
            
            # Agregar fila
            todos_los_datos.append({
                'Escenario_ID': escenario['id'],
                'Escenario': escenario['nombre'],
                'Partido': partido,
                
                # 2021
                'MR_2021': mr_2021,
                'PM_2021': pm_2021,
                'RP_2021': rp_2021,
                'Total_2021': total_2021,
                
                # 2024
                'MR_2024': mr_2024,
                'PM_2024': pm_2024,
                'RP_2024': rp_2024,
                'Total_2024': total_2024,
                
                # Diferencias (2024 - 2021)
                'Diff_MR': diff_mr,
                'Diff_PM': diff_pm,
                'Diff_RP': diff_rp,
                'Diff_Total': diff_total,
                
                # Votos
                'Votos_%_2021': datos_2021.get('porcentaje_votos', 0),
                'Votos_%_2024': datos_2024.get('porcentaje_votos', 0),
            })

# Crear DataFrame
print("\n\n📊 Creando tabla...")
df = pd.DataFrame(todos_los_datos)

# Reordenar columnas para mejor lectura
columnas_ordenadas = [
    'Escenario_ID', 'Escenario', 'Partido',
    'Votos_%_2021', 'MR_2021', 'PM_2021', 'RP_2021', 'Total_2021',
    'Votos_%_2024', 'MR_2024', 'PM_2024', 'RP_2024', 'Total_2024',
    'Diff_MR', 'Diff_PM', 'Diff_RP', 'Diff_Total'
]

df = df[columnas_ordenadas]

# Guardar CSV
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"outputs/comparativa_escenarios_2021_vs_2024_{timestamp}.csv"

df.to_csv(filename, index=False, encoding='utf-8-sig')

print(f"✅ Tabla guardada en: {filename}")
print(f"   Filas totales: {len(df)}")
print(f"   Escenarios: {df['Escenario'].nunique()}")
print(f"   Partidos únicos: {df['Partido'].nunique()}")

# Mostrar resumen de MORENA
print("\n" + "=" * 80)
print("📊 RESUMEN MORENA - Diferencias 2024 vs 2021")
print("=" * 80)

morena_df = df[df['Partido'] == 'MORENA']

if not morena_df.empty:
    print(f"\n{'Escenario':<25} {'Total 2021':>12} {'Total 2024':>12} {'Diferencia':>12}")
    print("-" * 80)
    
    for _, row in morena_df.iterrows():
        print(f"{row['Escenario']:<25} {row['Total_2021']:>12} {row['Total_2024']:>12} {row['Diff_Total']:>+12}")
    
    print("\nDesglose por tipo de escaño:")
    print(f"\n{'Escenario':<25} {'MR':>8} {'PM':>8} {'RP':>8} {'Total':>8}")
    print("-" * 80)
    
    for _, row in morena_df.iterrows():
        print(f"{row['Escenario']:<25} {row['Diff_MR']:>+8} {row['Diff_PM']:>+8} {row['Diff_RP']:>+8} {row['Diff_Total']:>+8}")

print("\n\n✅ Proceso completado!")
print(f"📄 Archivo CSV: {filename}")
