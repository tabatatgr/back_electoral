"""
Script para simular escenarios específicos:
1. 200-200 sin topes
2. 250-250 con topes

Para: Morena, PT, PVEM y Coalición total
"""

import requests
import json
from tabulate import tabulate

BASE_URL = "http://localhost:5000"

def simular_escenario(mr_distritos, rp_nacional, aplicar_topes, nombre_escenario):
    """
    Simula un escenario electoral
    """
    print(f"\n{'='*80}")
    print(f"ESCENARIO: {nombre_escenario}")
    print(f"{'='*80}")
    
    # Preparar el payload
    payload = {
        "mr_distritos": mr_distritos,
        "rp_nacional": rp_nacional,
        "aplicar_topes": aplicar_topes
    }
    
    try:
        # Hacer la petición
        response = requests.post(f"{BASE_URL}/calcular_diputados", json=payload, timeout=30)
        
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
        
        data = response.json()
        
        # Extraer resultados
        if "seat_chart" not in data:
            print("Error: No se encontró seat_chart en la respuesta")
            return None
        
        seat_chart = data["seat_chart"]
        
        # Partidos de interés
        partidos_interes = ["MORENA", "PT", "PVEM"]
        
        # Preparar tabla de resultados
        tabla_datos = []
        
        # Total de escaños
        total_escanos = mr_distritos + rp_nacional
        
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
        print(f"  - MR (distritos): {mr_distritos}")
        print(f"  - RP (nacional): {rp_nacional}")
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
            "morena": seat_chart.get("MORENA", 0),
            "pt": seat_chart.get("PT", 0),
            "pvem": seat_chart.get("PVEM", 0),
            "coalicion": escanos_coalicion,
            "total": total_escanos,
            "porcentaje_coalicion": porcentaje_coalicion
        }
        
    except requests.exceptions.ConnectionError:
        print(f"ERROR: No se pudo conectar al servidor en {BASE_URL}")
        print("Asegúrate de que el servidor FastAPI esté corriendo (uvicorn main:app).")
        return None
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("SIMULACIÓN DE ESCENARIOS ELECTORALES")
    print("="*80)
    
    resultados = []
    
    # Escenario 1: 200-200 sin topes
    print("\n\n🔹 Ejecutando Escenario 1...")
    resultado1 = simular_escenario(
        mr_distritos=200,
        rp_nacional=200,
        aplicar_topes=False,
        nombre_escenario="200 MR + 200 RP (SIN TOPES)"
    )
    if resultado1:
        resultados.append(resultado1)
    
    # Escenario 2: 250-250 con topes
    print("\n\n🔹 Ejecutando Escenario 2...")
    resultado2 = simular_escenario(
        mr_distritos=250,
        rp_nacional=250,
        aplicar_topes=True,
        nombre_escenario="250 MR + 250 RP (CON TOPES)"
    )
    if resultado2:
        resultados.append(resultado2)
    
    # Resumen comparativo
    if len(resultados) == 2:
        print("\n\n" + "="*80)
        print("RESUMEN COMPARATIVO")
        print("="*80)
        
        tabla_comparativa = []
        for r in resultados:
            tabla_comparativa.append([
                r["nombre"],
                r["morena"],
                r["pt"],
                r["pvem"],
                r["coalicion"],
                f"{r['porcentaje_coalicion']:.2f}%",
                r["total"]
            ])
        
        headers = ["Escenario", "MORENA", "PT", "PVEM", "Coalición", "% Coalición", "Total"]
        print("\n" + tabulate(tabla_comparativa, headers=headers, tablefmt="grid"))

if __name__ == "__main__":
    main()
