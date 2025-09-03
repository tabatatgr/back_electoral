"""
Test para verificar si la sobrerrepresentación ELIMINA o REDISTRIBUYE escaños
"""

import numpy as np
from engine.core import apply_overrep_cap

def test_sobrerrepresentacion_redistribucion():
    """
    Verificar si la sobrerrepresentación elimina escaños o los redistribuye
    """
    print("🔍 TEST: ¿La sobrerrepresentación elimina o redistribuye escaños?")
    print("=" * 70)
    
    # Configurar un caso de prueba realista
    # Simulamos un partido dominante con sobrerrepresentación
    S = 128  # Total de escaños
    
    # Caso 1: Sin sobrerrepresentación (baseline)
    print("\n📊 CASO 1: SIN SOBRERREPRESENTACIÓN")
    print("-" * 40)
    
    # Votos simulados
    vote_share = np.array([0.43, 0.20, 0.18, 0.12, 0.07])  # MORENA dominante
    partidos = ['MORENA', 'PAN', 'PRI', 'PRD', 'OTROS']
    
    # Escaños iniciales (sin limitación)
    seats_inicial = np.array([62, 24, 22, 14, 6])  # Total = 128
    
    print("Escaños iniciales:")
    for i, partido in enumerate(partidos):
        pct_escanos = (seats_inicial[i] / S) * 100
        pct_votos = vote_share[i] * 100
        sobrer = pct_escanos - pct_votos
        print(f"  {partido}: {seats_inicial[i]} escaños ({pct_escanos:.1f}%) | {pct_votos:.1f}% votos | Sobrer: {sobrer:+.1f}%")
    
    print(f"\nTOTAL ESCAÑOS: {seats_inicial.sum()}")
    
    # Caso 2: Con sobrerrepresentación del 8%
    print("\n📊 CASO 2: CON SOBRERREPRESENTACIÓN 8%")
    print("-" * 40)
    
    over_cap = 0.08  # 8% de sobrerrepresentación máxima
    seats_con_cap = apply_overrep_cap(seats_inicial, vote_share, S, over_cap)
    
    print("Escaños con limitación:")
    escanos_removidos = 0
    escanos_añadidos = 0
    
    for i, partido in enumerate(partidos):
        antes = seats_inicial[i]
        despues = seats_con_cap[i]
        cambio = despues - antes
        pct_escanos = (despues / S) * 100
        pct_votos = vote_share[i] * 100
        sobrer = pct_escanos - pct_votos
        
        if cambio != 0:
            if cambio > 0:
                escanos_añadidos += cambio
                print(f"  {partido}: {despues} escaños ({pct_escanos:.1f}%) | {pct_votos:.1f}% votos | Sobrer: {sobrer:+.1f}% | GANÓ {cambio:+d}")
            else:
                escanos_removidos += abs(cambio)
                print(f"  {partido}: {despues} escaños ({pct_escanos:.1f}%) | {pct_votos:.1f}% votos | Sobrer: {sobrer:+.1f}% | PERDIÓ {cambio}")
        else:
            print(f"  {partido}: {despues} escaños ({pct_escanos:.1f}%) | {pct_votos:.1f}% votos | Sobrer: {sobrer:+.1f}% | Sin cambio")
    
    print(f"\nTOTAL ESCAÑOS: {seats_con_cap.sum()}")
    print(f"Escaños removidos: {escanos_removidos}")
    print(f"Escaños añadidos: {escanos_añadidos}")
    
    # Caso 3: Sobrerrepresentación más estricta (4%)
    print("\n📊 CASO 3: CON SOBRERREPRESENTACIÓN 4% (MÁS ESTRICTA)")
    print("-" * 50)
    
    over_cap_estricto = 0.04  # 4% de sobrerrepresentación máxima
    seats_estricto = apply_overrep_cap(seats_inicial, vote_share, S, over_cap_estricto)
    
    print("Escaños con limitación estricta:")
    escanos_removidos_est = 0
    escanos_añadidos_est = 0
    
    for i, partido in enumerate(partidos):
        antes = seats_inicial[i]
        despues = seats_estricto[i]
        cambio = despues - antes
        pct_escanos = (despues / S) * 100
        pct_votos = vote_share[i] * 100
        sobrer = pct_escanos - pct_votos
        
        if cambio != 0:
            if cambio > 0:
                escanos_añadidos_est += cambio
                print(f"  {partido}: {despues} escaños ({pct_escanos:.1f}%) | {pct_votos:.1f}% votos | Sobrer: {sobrer:+.1f}% | GANÓ {cambio:+d}")
            else:
                escanos_removidos_est += abs(cambio)
                print(f"  {partido}: {despues} escaños ({pct_escanos:.1f}%) | {pct_votos:.1f}% votos | Sobrer: {sobrer:+.1f}% | PERDIÓ {cambio}")
        else:
            print(f"  {partido}: {despues} escaños ({pct_escanos:.1f}%) | {pct_votos:.1f}% votos | Sobrer: {sobrer:+.1f}% | Sin cambio")
    
    print(f"\nTOTAL ESCAÑOS: {seats_estricto.sum()}")
    print(f"Escaños removidos: {escanos_removidos_est}")
    print(f"Escaños añadidos: {escanos_añadidos_est}")
    
    # Análisis final
    print("\n🎯 ANÁLISIS Y CONCLUSIONES")
    print("=" * 50)
    
    if seats_inicial.sum() == seats_con_cap.sum() == seats_estricto.sum():
        print("✅ CONFIRMADO: La sobrerrepresentación REDISTRIBUYE escaños")
        print("   • El total de escaños se mantiene constante")
        print("   • Los escaños quitados a partidos sobrerrepresentados")
        print("   • Se redistribuyen a partidos que están por debajo del límite")
        print("   • Utiliza el método de resto mayor (largest remainder) para la redistribución")
    else:
        print("❌ ERROR: Parece que se eliminan escaños")
        print(f"   • Inicial: {seats_inicial.sum()}")
        print(f"   • Con cap 8%: {seats_con_cap.sum()}")
        print(f"   • Con cap 4%: {seats_estricto.sum()}")
    
    # Verificar el mecanismo específico
    print("\n🔧 MECANISMO TÉCNICO:")
    print("1. Se calcula el límite: cap = floor((porcentaje_votos + sobrerrepresentacion) * total_escaños)")
    print("2. Se aplica el tope: escaños = min(escaños_actuales, límite)")
    print("3. Se calcula el déficit: delta = total_escaños - suma_escaños_después_del_tope")
    print("4. Se redistribuye el déficit usando resto mayor entre partidos con margen disponible")
    
    # Ejemplo específico con MORENA
    morena_votos = vote_share[0] * 100
    morena_escanos_inicial = (seats_inicial[0] / S) * 100
    morena_escanos_con_cap = (seats_con_cap[0] / S) * 100
    
    print(f"\n📈 EJEMPLO MORENA:")
    print(f"   • Votos: {morena_votos:.1f}%")
    print(f"   • Escaños inicial: {morena_escanos_inicial:.1f}% (sobrerr: {morena_escanos_inicial-morena_votos:+.1f}%)")
    print(f"   • Escaños con cap 8%: {morena_escanos_con_cap:.1f}% (sobrerr: {morena_escanos_con_cap-morena_votos:+.1f}%)")
    print(f"   • Límite teórico: {morena_votos + 8:.1f}%")
    
    return {
        'redistribuye': seats_inicial.sum() == seats_con_cap.sum() == seats_estricto.sum(),
        'escaños_inicial': seats_inicial.sum(),
        'escaños_con_cap_8': seats_con_cap.sum(),
        'escaños_con_cap_4': seats_estricto.sum(),
        'cambios_8': dict(zip(partidos, seats_con_cap - seats_inicial)),
        'cambios_4': dict(zip(partidos, seats_estricto - seats_inicial))
    }

if __name__ == "__main__":
    resultado = test_sobrerrepresentacion_redistribucion()
    
    if resultado['redistribuye']:
        print("\n🏆 RESPUESTA A TU PREGUNTA:")
        print("La sobrerrepresentación NO elimina escaños, los REDISTRIBUYE")
        print("Mantiene el total constante pero limita la sobrerrepresentación individual")
    else:
        print("\n⚠️  Necesitamos investigar más el comportamiento")
