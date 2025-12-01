"""
Test rápido para ver la estructura de salida de procesar_diputados_v2
"""
from engine.procesar_diputados_v2 import procesar_diputados_v2
import json

resultado = procesar_diputados_v2(
    anio=2018,
    max_seats=400,
    mr_seats=200,
    rp_seats=200,
    usar_coaliciones=True,
    aplicar_topes=False
)

print("Claves del resultado:")
print(resultado.keys())

print("\nPartidos en 'tot':")
if 'tot' in resultado:
    print(resultado['tot'].keys())
    print(f"\nTotal partidos: {len(resultado['tot'])}")
    
    # Buscar MORENA en alguna variante
    for partido in resultado['tot'].keys():
        if 'MORENA' in partido.upper() or 'PT' in partido.upper():
            print(f"  {partido}: {resultado['tot'][partido]} escaños")
