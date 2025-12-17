"""
DIAGNÓSTICO PROFUNDO: ¿Por qué PVEM tiene 16 escaños de más?

PVEM:
- Oficial: 60 escaños
- Motor: 76 escaños (58 MR + 18 RP)
- Diferencia: +16 escaños DE MÁS

Esto es RARO porque PVEM tiene demasiados. Si PVEM está inflado,
esos escaños tienen que venir de otros partidos.
"""

import pandas as pd

print("="*80)
print("DIAGNÓSTICO: ¿Por qué PVEM tiene 76 en vez de 60?")
print("="*80)

# Datos del motor
motor_data = {
    'MORENA': {'MR': 160, 'RP': 87, 'TOTAL': 247},
    'PAN': {'MR': 33, 'RP': 36, 'TOTAL': 69},
    'PVEM': {'MR': 58, 'RP': 18, 'TOTAL': 76},  # ← PROBLEMA
    'PT': {'MR': 38, 'RP': 12, 'TOTAL': 50},
    'PRI': {'MR': 9, 'RP': 24, 'TOTAL': 33},
    'MC': {'MR': 1, 'RP': 23, 'TOTAL': 24},
    'PRD': {'MR': 1, 'RP': 0, 'TOTAL': 1}
}

# Datos oficiales
oficial_data = {
    'MORENA': 257,
    'PAN': 71,
    'PVEM': 60,  # ← OFICIAL
    'PT': 47,
    'PRI': 36,
    'MC': 27,
    'PRD': 1,
    'IND': 1
}

print("\n🔍 Análisis de PVEM:")
print("-" * 60)
print(f"PVEM Oficial:  {oficial_data['PVEM']} escaños")
print(f"PVEM Motor:    {motor_data['PVEM']['TOTAL']} escaños ({motor_data['PVEM']['MR']} MR + {motor_data['PVEM']['RP']} RP)")
print(f"Diferencia:    {motor_data['PVEM']['TOTAL'] - oficial_data['PVEM']:+d} escaños (PVEM tiene DE MÁS)")

print(f"\n📊 PVEM ganó {motor_data['PVEM']['MR']} distritos de MR")
print(f"   ¿Esto es correcto? (necesitamos verificar)")

print(f"\n📊 PVEM recibió {motor_data['PVEM']['RP']} escaños de RP")
print(f"   ¿Esto es correcto según su % de votos?")

print("\n" + "="*80)
print("HIPÓTESIS:")
print("="*80)

print("\nSi PVEM tiene 58 MR (distritos ganados), entonces:")
print(f"  - Para tener 60 total oficial: necesita {60-58} RP")
print(f"  - Motor le da: {motor_data['PVEM']['RP']} RP")
print(f"  - Diferencia en RP: {motor_data['PVEM']['RP'] - (60-58):+d} escaños de más")

print("\n💡 CONCLUSIÓN PRELIMINAR:")
print("Si el motor está dando a PVEM 16 RP cuando debería dar 2 RP,")
print("entonces esos 14 escaños 'extra' de RP están mal distribuidos.")
print("")
print("Los 14 escaños extra de PVEM podrían explicar:")
print("  - 10 escaños faltantes de MORENA")
print("  - 2 escaños faltantes de PAN")
print("  - 3 escaños faltantes de MC")
print("  - Menos los 3 extra de PRI y 3 extra de PT")

print("\n" + "="*80)
print("¿QUÉ VERIFICAR?")
print("="*80)
print("1. ¿PVEM realmente ganó 58 distritos de MR?")
print("2. ¿El % de votos de PVEM justifica 18 RP o solo 2 RP?")
print("3. ¿Hay algún problema en la asignación proporcional (Hare, D'Hondt)?")
print("4. ¿El motor está confundiendo votos de coalición con votos propios de PVEM?")
