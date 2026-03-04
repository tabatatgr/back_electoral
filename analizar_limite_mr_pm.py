"""
Análisis: Límite Superior de Distritos MR para Recibir Escaños PM

Este script analiza la relación entre los distritos ganados en Mayoría Relativa (MR)
y la elegibilidad para recibir escaños de Primera Minoría (PM).

Pregunta clave: ¿Cuál es el máximo de distritos MR que una coalición puede ganar
y aún así recibir escaños de Primera Minoría?

Sistema: 300 MR + 100 PM + 100 RP = 500 escaños totales
"""

import pandas as pd
import numpy as np
from datetime import datetime

def analizar_limite_mr_pm():
    """
    Analiza el límite superior de distritos MR para recibir PM.
    """
    print("=" * 80)
    print("ANÁLISIS: LÍMITE SUPERIOR DE DISTRITOS MR PARA RECIBIR PM")
    print("=" * 80)
    print()
    
    total_distritos = 300
    pm_disponibles = 100
    
    # Teoría básica
    print("📚 TEORÍA BÁSICA")
    print("-" * 80)
    print(f"Total de distritos: {total_distritos}")
    print(f"Escaños PM disponibles: {pm_disponibles}")
    print()
    print("Regla fundamental:")
    print("  • Los escaños PM se asignan a quien queda en SEGUNDO LUGAR")
    print("  • Si ganas un distrito en MR, NO puedes recibir PM de ese distrito")
    print("  • Los PM se asignan a los 100 distritos más competitivos")
    print()
    
    # Límite teórico
    print("🔢 LÍMITE TEÓRICO")
    print("-" * 80)
    limite_teorico = total_distritos - 1
    print(f"Límite teórico máximo: {limite_teorico} distritos MR")
    print(f"Explicación:")
    print(f"  • Si ganas {limite_teorico} distritos, pierdes {total_distritos - limite_teorico}")
    print(f"  • En ese {total_distritos - limite_teorico} distrito perdido, puedes quedar 2°")
    print(f"  • Recibirías solo {total_distritos - limite_teorico} escaño PM (no los {pm_disponibles})")
    print()
    
    # Límite práctico
    print("💡 LÍMITE PRÁCTICO")
    print("-" * 80)
    limite_practico = total_distritos - pm_disponibles
    print(f"Límite práctico para recibir {pm_disponibles} escaños PM: {limite_practico} distritos MR")
    print(f"Explicación:")
    print(f"  • Si ganas {limite_practico} distritos en MR")
    print(f"  • Pierdes {total_distritos - limite_practico} distritos")
    print(f"  • Si quedas 2° en esos {total_distritos - limite_practico} distritos más competitivos")
    print(f"  • Recibes {pm_disponibles} escaños PM completos")
    print()
    
    # Tabla de escenarios
    print("📊 TABLA DE ESCENARIOS")
    print("-" * 80)
    print()
    
    escenarios = []
    
    # Analizar diferentes niveles de MR ganados
    for mr_ganados in [0, 50, 100, 150, 200, 210, 220, 230, 240, 250, 260, 270, 280, 290, 295, 299, 300]:
        distritos_perdidos = total_distritos - mr_ganados
        
        # PM máximo que podría recibir
        pm_potencial = min(distritos_perdidos, pm_disponibles)
        
        # ¿Recibe PM completo?
        pm_completo = "SÍ" if pm_potencial == pm_disponibles else "NO"
        
        escenarios.append({
            'MR_ganados': mr_ganados,
            'Distritos_perdidos': distritos_perdidos,
            'PM_potencial': pm_potencial,
            'PM_completo': pm_completo,
            'Total_potencial': mr_ganados + pm_potencial
        })
    
    df = pd.DataFrame(escenarios)
    
    print(df.to_string(index=False))
    print()
    
    # Punto de inflexión
    print("🎯 PUNTO DE INFLEXIÓN")
    print("-" * 80)
    print(f"A partir de {limite_practico + 1} distritos MR ganados,")
    print(f"ya no se pueden obtener los {pm_disponibles} escaños PM completos")
    print()
    
    # Ejemplos con datos reales
    print("📈 EJEMPLOS CON DATOS REALES 2024")
    print("-" * 80)
    
    # Cargar datos de la simulación anterior
    try:
        df_sim = pd.read_csv('simulacion_300mr_100pm_100rp.csv')
        df_2024 = df_sim[df_sim['Año'] == 2024]
        
        print("\nResultados de la simulación 300 MR + 100 PM + 100 RP:")
        print()
        
        for _, row in df_2024.iterrows():
            coalicion = row['Coalición']
            mr = row['MR_Escaños']
            pm = row['PM_Escaños']
            
            distritos_perdidos = total_distritos - mr
            
            print(f"{coalicion}:")
            print(f"  • MR ganados: {mr} distritos")
            print(f"  • Distritos perdidos: {distritos_perdidos}")
            print(f"  • PM recibidos: {pm} escaños")
            
            if mr <= limite_practico:
                print(f"  ✓ Por debajo del límite ({limite_practico}) - Puede recibir PM completo")
            else:
                print(f"  ⚠ Por encima del límite ({limite_practico}) - PM limitado")
            
            print()
    except FileNotFoundError:
        print("No se encontró el archivo de simulación")
        print()
    
    # Resumen final
    print("=" * 80)
    print("📌 RESUMEN")
    print("=" * 80)
    print()
    print(f"1. LÍMITE TEÓRICO ABSOLUTO: {limite_teorico} distritos MR")
    print(f"   (Puedes ganar hasta 299 y aún recibir 1 PM)")
    print()
    print(f"2. LÍMITE PRÁCTICO PARA PM COMPLETO: {limite_practico} distritos MR")
    print(f"   (Para recibir los {pm_disponibles} escaños PM)")
    print()
    print(f"3. REGLA GENERAL:")
    print(f"   PM posibles = min(300 - MR_ganados, 100)")
    print()
    print(f"4. FÓRMULA:")
    print(f"   Si ganas X distritos MR → Máximo PM = min(300 - X, 100)")
    print()
    
    # Guardar análisis
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"analisis_limite_mr_pm_{timestamp}.csv"
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"✅ Análisis guardado en: {output_file}")
    print()
    
    return df

def crear_grafica_visual():
    """
    Crea una representación visual del límite.
    """
    print("=" * 80)
    print("VISUALIZACIÓN: RELACIÓN MR vs PM")
    print("=" * 80)
    print()
    
    print("MR Ganados │ PM Potencial │ Visualización")
    print("───────────┼──────────────┼" + "─" * 50)
    
    for mr in range(0, 301, 20):
        pm = min(300 - mr, 100)
        
        # Crear barra visual
        bar_mr = "█" * (mr // 10)
        bar_pm = "░" * (pm // 5)
        
        marker = " ←" if mr == 200 else ""
        
        print(f"{mr:3d}        │  {pm:3d}         │ MR:{bar_mr} PM:{bar_pm}{marker}")
    
    print()
    print("Leyenda:")
    print("  █ = Escaños MR (cada símbolo = 10 escaños)")
    print("  ░ = Escaños PM potenciales (cada símbolo = 5 escaños)")
    print("  ← = Límite práctico (200 MR) para recibir 100 PM completos")
    print()

def main():
    """
    Ejecuta el análisis completo.
    """
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  ANÁLISIS: LÍMITE SUPERIOR DE DISTRITOS MR PARA RECIBIR PM".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    # Análisis principal
    df_analisis = analizar_limite_mr_pm()
    
    # Visualización
    crear_grafica_visual()
    
    # Respuesta directa
    print("=" * 80)
    print("🎯 RESPUESTA DIRECTA A LA PREGUNTA")
    print("=" * 80)
    print()
    print("¿Cuál es el límite superior de distritos MR para recibir PM?")
    print()
    print("RESPUESTA:")
    print()
    print("  • LÍMITE TEÓRICO: 299 distritos")
    print("    (Puedes ganar 299 y aún recibir 1 PM)")
    print()
    print("  • LÍMITE PRÁCTICO: 200 distritos")
    print("    (Para recibir los 100 escaños PM completos)")
    print()
    print("REGLA:")
    print()
    print("  Si ganas X distritos en MR:")
    print("  → Puedes recibir máximo min(300-X, 100) escaños PM")
    print()
    print("EJEMPLOS:")
    print()
    print("  • Ganas 200 MR → Máximo 100 PM ✓ (PM completo)")
    print("  • Ganas 210 MR → Máximo 90 PM  (pierdes 10 PM)")
    print("  • Ganas 250 MR → Máximo 50 PM  (pierdes 50 PM)")
    print("  • Ganas 290 MR → Máximo 10 PM  (pierdes 90 PM)")
    print("  • Ganas 300 MR → Máximo 0 PM   (sin PM)")
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()
