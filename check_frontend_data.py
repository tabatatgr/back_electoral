import sys
import os
import pandas as pd
import json

# Agregar path
sys.path.append('.')

from engine.procesar_diputados_v2 import procesar_diputados_v2
from engine.procesar_senadores_v2 import procesar_senadores_v2

def check_diputados():
    print("\n=== VERIFICANDO DIPUTADOS ===")
    path_data = "data/computos_diputados_2024.parquet"
    path_siglado = "data/siglado_diputados_2024.csv" # Usar mock o None si no es crítico, pero mejor None si la función lo permite o un path dummy
    # En el código real se usa un csv. Verificar argumento. 
    # Usaremos None para siglado si es opcional, o el path real si existe.
    if not os.path.exists(path_siglado):
        path_siglado = None 

    # CASO 1: 300 Distritos
    print("--- Caso 1: 300 Distritos ---")
    res_300 = procesar_diputados_v2(
        path_parquet=path_data,
        anio=2024,
        path_siglado=path_siglado,
        mr_seats=300,
        rp_seats=200,
        max_seats=500
    )
    
    meta_300 = res_300.get('meta', {})
    dist_300 = meta_300.get('distritos_por_estado', {})
    
    if dist_300:
        print(f"✅ Meta contiene distritos_por_estado ({len(dist_300)} estados)")
        # Imprimir todas las keys para depuración
        print(f"   Keys encontradas (primeras 5): {list(dist_300.keys())[:5]}")
        # Intentar buscar por nombre si las keys son strings
        val_jalisco = dist_300.get('Jalisco') or dist_300.get('JALISCO') or dist_300.get(14)
        val_cdmx = dist_300.get('Ciudad de Mexico') or dist_300.get('CIUDAD DE MEXICO') or dist_300.get(9)
        
        print(f"   Jalisco (Busqueda flexible): {val_jalisco}")
        print(f"   CDMX (Busqueda flexible): {val_cdmx}")
        
        total = sum(dist_300.values())
        print(f"   Total Distritos reportados en meta: {total}")
        
        if total != 300:
            print(f"⚠️  ALERTA: Se pidieron 300 distritos pero meta reporta {total}. Posible escalado activo o dataset incompleto.")
    else:
        print("❌ Meta NO contiene distritos_por_estado o está vacío")

    # CASO 2: 150 Distritos
    print("\n--- Caso 2: 150 Distritos ---")
    res_150 = procesar_diputados_v2(
        path_parquet=path_data,
        anio=2024,
        path_siglado=path_siglado,
        mr_seats=150,
        rp_seats=150,
        max_seats=300
    )
    
    meta_150 = res_150.get('meta', {})
    dist_150 = meta_150.get('distritos_por_estado', {})
    
    if dist_150:
        print(f"✅ Meta contiene distritos_por_estado ({len(dist_150)} estados)")
        print(f"   Jalisco (14): {dist_150.get(14, 'No encontrado')}")
        print(f"   CDMX (9): {dist_150.get(9, 'No encontrado')}")
        total = sum(dist_150.values())
        print(f"   Total Distritos reportados en meta: {total}")
        
        # Tolerancia +-1 por redondeo
        if abs(total - 150) <= 2:
             print("✅ El total coincide con input (150 approx)")
        else:
             print(f"⚠️ El total NO coincide (esperado 150, real {total})")
    else:
        print("❌ Meta NO contiene distritos_por_estado")

    # CASO 3: 50 Distritos (Test de estrés)
    print("\n--- Caso 3: 50 Distritos (Mini Cámara) ---")
    res_50 = procesar_diputados_v2(
        path_parquet=path_data,
        anio=2024,
        path_siglado=path_siglado,
        mr_seats=50,
        rp_seats=50,
        max_seats=100
    )
    
    meta_50 = res_50.get('meta', {})
    dist_50 = meta_50.get('distritos_por_estado', {})
    
    if dist_50:
        print(f"✅ Meta contiene distritos_por_estado ({len(dist_50)} estados)")
        total = sum(dist_50.values())
        print(f"   Total Distritos reportados en meta: {total}")
        # Tolerancia +-1
        if abs(total - 50) <= 2:
            print("✅ El total coincide con input (50 approx)")
        else:
            print(f"⚠️ El total NO coincide (esperado 50, real {total})")
    else:
        print("❌ Meta NO contiene distritos_por_estado")

def check_senado():
    print("\n=== VERIFICANDO SENADO ===")
    path_data = "data/computos_senado_2024.parquet"
    path_siglado = None # Senado usualmente calcula siglado interno o no usa

    # CASO 1: 96 Senadores (64 MR + 32 PM) - Plan A
    
    print("--- Caso 1: 64 MR (Plan 96 Directos? o Plan A) ---")
    # Si mr_seats=64, debería repartir 2 por estado.
    res_64 = procesar_senadores_v2(
        path_parquet=path_data,
        anio=2024,
        path_siglado=path_siglado,
        mr_seats=64,
        rp_seats=32,
        max_seats=96
    )
    
    meta_64 = res_64.get('meta', {})
    # En senado puede llamarse 'senadores_por_estado' o 'mr_por_estado'
    sen_est_64 = meta_64.get('senadores_por_estado', meta_64.get('mr_por_estado', {}))
    # OJO: mr_por_estado es un dict de {estado: {partido: votos}}? 
    # No, en meta suele ser {estado: total}.
    # Revisemos el código de senadores.
    # El código dice: 
    # mr_por_estado[estado][partido] = asignado
    # Pero no veo un 'limites_por_estado'. 
    # El usuario necesita saber el LÍMITE.
    
    # Veamos qué hay en meta.
    print(f"Keys en meta: {list(meta_64.keys())}")
    print(f"   senadores_por_estado en meta: {meta_64.get('senadores_por_estado')}")
    
    # Analizar estructura de mr_por_estado
    mr_dict = meta_64.get('mr_por_estado', {})
    if mr_dict:
        ejemplo_edo = list(mr_dict.keys())[0]
        print(f"Ejemplo estructura mr_por_estado[{ejemplo_edo}]: {mr_dict[ejemplo_edo]}")
        
        # Calcular totales por estado
        totales_por_estado = {k: sum(v.values()) for k, v in mr_dict.items()}
        print(f"Total por estado (Jalisco=14): {totales_por_estado.get(14, 'N/A')}")
        print(f"Total nacional MR: {sum(totales_por_estado.values())}")
    
    # CASO 2: 96 MR (3 por estado)
    print("\n--- Caso 2: 96 MR ---")
    res_96 = procesar_senadores_v2(
        path_parquet=path_data,
        anio=2024,
        path_siglado=path_siglado,
        mr_seats=96,
        rp_seats=32,
        max_seats=128
    )
    meta_96 = res_96.get('meta', {})
    mr_dict_96 = meta_96.get('mr_por_estado', {})
    if mr_dict_96:
        totales_por_estado = {k: sum(v.values()) for k, v in mr_dict_96.items()}
        print(f"Total por estado (Jalisco=14): {totales_por_estado.get(14, 'N/A')}")
        print(f"Total nacional MR: {sum(totales_por_estado.values())}")

    # CASO 3: 50 MR en Senado (Inusual)
    print("\n--- Caso 3: 50 MR en Senado (Test de estrés) ---")
    res_sen_50 = procesar_senadores_v2(
        path_parquet=path_data,
        anio=2024,
        path_siglado=path_siglado,
        mr_seats=50,
        rp_seats=14, # Total 64 solo por jugar
        max_seats=64
    )
    meta_sen_50 = res_sen_50.get('meta', {})
    mr_dict_50 = meta_sen_50.get('mr_por_estado', {})
    
    if mr_dict_50:
        totales_por_estado = {k: sum(v.values()) for k, v in mr_dict_50.items()}
        print(f"Total nacional MR: {sum(totales_por_estado.values())}")
        print(f"Distribucion de escaños (ejemplo 5 estados): {list(totales_por_estado.items())[:5]}")
    else:
        print("❌ No se generó distribución MR")

if __name__ == "__main__":
    try:
        check_diputados()
        check_senado()
    except Exception as e:
        print(f"CRASH: {e}")
        import traceback
        traceback.print_exc()
