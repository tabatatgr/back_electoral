"""
Script para simular escenarios específicos directamente usando las funciones del backend:
1. 200-200 sin topes (para 2021 y 2024)
2. 250-250 con topes (para 2021 y 2024)

Para: Morena, PT, PVEM y Coalición total
"""

import sys
sys.path.append('.')

from engine.procesar_diputados_v2 import procesar_diputados_v2
from tabulate import tabulate
import pandas as pd
from datetime import datetime

def simular_escenario(mr_seats, rp_seats, aplicar_topes, anio, nombre_escenario):
    """
    Simula un escenario electoral usando la función del backend directamente
    """
    print(f"\n{'='*80}")
    print(f"ESCENARIO: {nombre_escenario} - Año {anio}")
    print(f"{'='*80}")
    
    # Total de escaños
    max_seats = mr_seats + rp_seats
    
    # Path al archivo de votos reagregados según el escenario y año
    if mr_seats == 200 and rp_seats == 200:
        path_parquet = f"redistritacion/outputs/votos_reagregados_200_200_{anio}.parquet"
    elif mr_seats == 250 and rp_seats == 250:
        # Para 250-250, usar 200-200 como base
        path_parquet = f"redistritacion/outputs/votos_reagregados_200_200_{anio}.parquet"
    else:
        # Fallback a los datos originales
        path_parquet = f"data/computos_diputados_{anio}.parquet"
    
    siglado_path = f"data/siglado-diputados-{anio}.csv"
    
    # Calcular tope proporcional: 300/500 = 60% -> para 400 sería 240
    max_seats_per_party = None
    if aplicar_topes and max_seats == 400:
        # Tope proporcional ajustado para cámara de 400
        max_seats_per_party = 240  # 60% de 400
        print(f"  ** Tope ajustado a {max_seats_per_party} escaños (60% de {max_seats})")
    
    try:
        # Llamar a la función del backend
        resultado = procesar_diputados_v2(
            path_parquet=path_parquet,
            anio=anio,
            path_siglado=siglado_path,
            max_seats=max_seats,
            mr_seats=mr_seats,
            rp_seats=rp_seats,
            aplicar_topes=aplicar_topes,
            max_seats_per_party=max_seats_per_party,
            usar_coaliciones=True,
            sobrerrepresentacion=8.0 if aplicar_topes else None,
            umbral=0.03,
            print_debug=False
        )
        
        # Debug: ver qué retorna
        if resultado is None:
            print("ERROR: La función retornó None")
            return None
        
        if isinstance(resultado, dict):
            # La función retorna 'tot' en lugar de 'seat_chart'
            if 'tot' in resultado:
                seat_chart = resultado['tot']
            elif 'seat_chart' in resultado:
                seat_chart = resultado['seat_chart']
            else:
                print(f"ERROR: No se encontró 'tot' ni 'seat_chart'. Claves: {list(resultado.keys())}")
                return None
        else:
            print(f"ERROR: Resultado no es un diccionario, es {type(resultado)}")
            return None
        
        # Partidos de interés
        partidos_interes = ["MORENA", "PT", "PVEM"]
        
        # Preparar tabla de resultados
        tabla_datos = []
        
        # Total de escaños
        total_escanos = max_seats
        
        # Procesar cada partido
        for partido in partidos_interes:
            if partido in seat_chart:
                escanos = seat_chart[partido]
                porcentaje = (escanos / total_escanos) * 100
                tabla_datos.append([partido, escanos, f"{porcentaje:.2f}%"])
            else:
                tabla_datos.append([partido, 0, "0.00%"])
        
        # Calcular coalición
        escanos_coalicion = sum(seat_chart.get(p, 0) for p in partidos_interes)
        porcentaje_coalicion = (escanos_coalicion / total_escanos) * 100
        tabla_datos.append(["-"*20, "-"*10, "-"*10])
        tabla_datos.append(["COALICIÓN TOTAL", escanos_coalicion, f"{porcentaje_coalicion:.2f}%"])
        
        # Mostrar tabla
        headers = ["Partido/Coalición", "Escaños", "% del Total"]
        print("\n" + tabulate(tabla_datos, headers=headers, tablefmt="grid"))
        
        # Información adicional
        print(f"\nTotal de escaños en juego: {total_escanos}")
        print(f"  - MR (mayoría relativa): {mr_seats}")
        print(f"  - RP (representación proporcional): {rp_seats}")
        print(f"Topes aplicados: {'SÍ' if aplicar_topes else 'NO'}")
        
        # Mostrar todos los partidos
        print("\n--- Distribución completa de escaños ---")
        todos_partidos = []
        for partido, escanos in sorted(seat_chart.items(), key=lambda x: x[1], reverse=True):
            if escanos > 0:
                porcentaje = (escanos / total_escanos) * 100
                todos_partidos.append([partido, escanos, f"{porcentaje:.2f}%"])
        
        print(tabulate(todos_partidos, headers=["Partido", "Escaños", "% del Total"], tablefmt="simple"))
        
        return {
            "nombre": nombre_escenario,
            "anio": anio,
            "morena": seat_chart.get("MORENA", 0),
            "pt": seat_chart.get("PT", 0),
            "pvem": seat_chart.get("PVEM", 0),
            "coalicion": escanos_coalicion,
            "total": total_escanos,
            "porcentaje_coalicion": porcentaje_coalicion,
            "mr_seats": mr_seats,
            "rp_seats": rp_seats,
            "pct_morena": (seat_chart.get("MORENA", 0) / total_escanos * 100),
            "pct_pt": (seat_chart.get("PT", 0) / total_escanos * 100),
            "pct_pvem": (seat_chart.get("PVEM", 0) / total_escanos * 100)
        }
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("SIMULACIÓN DE ESCENARIOS ELECTORALES")
    print("="*80)
    
    resultados = []
    
    # Escenarios para 2021 y 2024
    años = [2021, 2024]
    
    for anio in años:
        print(f"\n\n{'='*80}")
        print(f"AÑO {anio}")
        print(f"{'='*80}")
        
        # Escenario 1: 200-200 sin topes
        print("\n\n🔹 Ejecutando Escenario 1...")
        resultado1 = simular_escenario(
            mr_seats=200,
            rp_seats=200,
            aplicar_topes=False,
            anio=anio,
            nombre_escenario="200 MR + 200 RP (SIN TOPES)"
        )
        if resultado1:
            resultados.append(resultado1)
        
        # Escenario 2: 200-200 CON topes
        print("\n\n🔹 Ejecutando Escenario 2...")
        resultado2 = simular_escenario(
            mr_seats=200,
            rp_seats=200,
            aplicar_topes=True,
            anio=anio,
            nombre_escenario="200 MR + 200 RP (CON TOPES)"
        )
        if resultado2:
            resultados.append(resultado2)
        
        # Escenario 3: 250-250 SIN topes
        print("\n\n🔹 Ejecutando Escenario 3...")
        resultado3 = simular_escenario(
            mr_seats=250,
            rp_seats=250,
            aplicar_topes=False,
            anio=anio,
            nombre_escenario="250 MR + 250 RP (SIN TOPES)"
        )
        if resultado3:
            resultados.append(resultado3)
        
        # Escenario 4: 250-250 CON topes
        print("\n\n🔹 Ejecutando Escenario 4...")
        resultado4 = simular_escenario(
            mr_seats=250,
            rp_seats=250,
            aplicar_topes=True,
            anio=anio,
            nombre_escenario="250 MR + 250 RP (CON TOPES)"
        )
        if resultado4:
            resultados.append(resultado4)
    
    # Resumen comparativo
    if len(resultados) > 0:
        print("\n\n" + "="*80)
        print("RESUMEN COMPARATIVO - TODOS LOS ESCENARIOS")
        print("="*80)
        
        tabla_comparativa = []
        for r in resultados:
            tabla_comparativa.append([
                r["anio"],
                r["nombre"],
                r["morena"],
                r["pt"],
                r["pvem"],
                r["coalicion"],
                f"{r['porcentaje_coalicion']:.2f}%",
                r["total"]
            ])
        
        headers = ["Año", "Escenario", "MORENA", "PT", "PVEM", "Coalición", "% Coalición", "Total"]
        print("\n" + tabulate(tabla_comparativa, headers=headers, tablefmt="grid"))
        
        # Análisis por año
        for anio in años:
            resultados_anio = [r for r in resultados if r["anio"] == anio]
            if len(resultados_anio) == 2:
                print(f"\n\n📊 ANÁLISIS {anio}:")
                print("-" * 80)
                r1 = resultados_anio[0]  # 200-200 sin topes
                r2 = resultados_anio[1]  # 250-250 con topes
                
                diff_escanos = r2["coalicion"] - r1["coalicion"]
                diff_porcentaje = r2["porcentaje_coalicion"] - r1["porcentaje_coalicion"]
                
                print(f"\nDiferencia entre escenarios:")
                print(f"  • Escaños de coalición: {diff_escanos:+d} escaños")
                print(f"  • Porcentaje: {diff_porcentaje:+.2f} puntos porcentuales")
                
                if diff_escanos > 0:
                    print(f"\n⬆️  La coalición gana {abs(diff_escanos)} escaños más con 250-250 CON TOPES")
                elif diff_escanos < 0:
                    print(f"\n⬇️  La coalición pierde {abs(diff_escanos)} escaños con 250-250 CON TOPES")
                else:
                    print(f"\n➡️  Sin cambios en escaños de coalición entre escenarios")
        
        # Comparación entre años
        print(f"\n\n📊 COMPARACIÓN ENTRE 2021 Y 2024:")
        print("-" * 80)
        
        for nombre_esc in ["200 MR + 200 RP (SIN TOPES)", "250 MR + 250 RP (CON TOPES)"]:
            r_2021 = [r for r in resultados if r["anio"] == 2021 and r["nombre"] == nombre_esc]
            r_2024 = [r for r in resultados if r["anio"] == 2024 and r["nombre"] == nombre_esc]
            
            if r_2021 and r_2024:
                diff = r_2024[0]["coalicion"] - r_2021[0]["coalicion"]
                print(f"\n{nombre_esc}:")
                print(f"  2021: {r_2021[0]['coalicion']} escaños ({r_2021[0]['porcentaje_coalicion']:.2f}%)")
                print(f"  2024: {r_2024[0]['coalicion']} escaños ({r_2024[0]['porcentaje_coalicion']:.2f}%)")
                print(f"  Diferencia: {diff:+d} escaños")
        
        # Guardar resultados en CSV
        print(f"\n\n{'='*80}")
        print("GUARDANDO RESULTADOS EN CSV")
        print(f"{'='*80}")
        
        # Crear DataFrame
        df_resultados = pd.DataFrame(resultados)
        
        # Reordenar columnas
        df_resultados = df_resultados[['anio', 'nombre', 'mr_seats', 'rp_seats', 'total', 
                                        'morena', 'pct_morena', 'pt', 'pct_pt', 'pvem', 'pct_pvem',
                                        'coalicion', 'porcentaje_coalicion']]
        
        # Renombrar columnas
        df_resultados.columns = ['Año', 'Escenario', 'MR', 'RP', 'Total_Escaños', 
                                 'MORENA_Escaños', 'MORENA_%', 'PT_Escaños', 'PT_%', 
                                 'PVEM_Escaños', 'PVEM_%', 'Coalición_Escaños', 'Coalición_%']
        
        # Redondear porcentajes
        df_resultados['MORENA_%'] = df_resultados['MORENA_%'].round(2)
        df_resultados['PT_%'] = df_resultados['PT_%'].round(2)
        df_resultados['PVEM_%'] = df_resultados['PVEM_%'].round(2)
        df_resultados['Coalición_%'] = df_resultados['Coalición_%'].round(2)
        
        # Guardar
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"simulacion_escenarios_{timestamp}.csv"
        df_resultados.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        print(f"\n✅ Resultados guardados en: {output_file}")
        print(f"   {len(resultados)} escenarios procesados")

if __name__ == "__main__":
    main()
