"""
DIAGNÓSTICO SIMPLIFICADO: ¿Dónde están los 10 escaños faltantes de MORENA?

Datos conocidos:
- Oficial 2024: MORENA = 257 escaños
- Motor actual: MORENA = 247 escaños (160 MR + 87 RP)
- Diferencia: 10 escaños

Hipótesis a verificar:
1. ¿El conteo de 160 MR es correcto?
2. ¿Los 87 RP son correctos?
3. ¿Hay algún tope aplicándose incorrectamente?
"""

import pandas as pd

print("="*80)
print("DIAGNÓSTICO: Comparación con datos oficiales 2024")
print("="*80)

# Leer datos oficiales
df_oficial = pd.read_csv('data/escaños_resumen_camaras_2018_2021_2024_oficial_gallagher_ratio_promedio(2).csv')
df_2024 = df_oficial[(df_oficial['Año'] == 2024) & (df_oficial['Cámara'] == 'Diputados')]

print("\n📊 DATOS OFICIALES 2024:")
print("-" * 50)
print(f"{'Partido':<10} {'Escaños':<10} {'% Escaños':<10}")
print("-" * 50)

total_oficial = 0
for _, row in df_2024.iterrows():
    partido = row['Partido']
    escanos = int(row['Total'])
    pct = row['% Escaños']
    total_oficial += escanos
    print(f"{partido:<10} {escanos:<10} {pct:<10.2f}%")

print("-" * 50)
print(f"{'TOTAL':<10} {total_oficial:<10}")

# Datos del motor (del test anterior)
motor_data = {
    'PAN': {'MR': 33, 'RP': 36, 'TOTAL': 69},
    'PRI': {'MR': 9, 'RP': 24, 'TOTAL': 33},
    'PRD': {'MR': 1, 'RP': 0, 'TOTAL': 1},
    'PVEM': {'MR': 58, 'RP': 18, 'TOTAL': 76},
    'PT': {'MR': 38, 'RP': 12, 'TOTAL': 50},
    'MC': {'MR': 1, 'RP': 23, 'TOTAL': 24},
    'MORENA': {'MR': 160, 'RP': 87, 'TOTAL': 247}
}

print("\n📊 RESULTADO DEL MOTOR:")
print("-" * 50)
print(f"{'Partido':<10} {'MR':<6} {'RP':<6} {'Total':<10}")
print("-" * 50)

total_motor = 0
for partido, datos in motor_data.items():
    mr = datos['MR']
    rp = datos['RP']
    total = datos['TOTAL']
    total_motor += total
    print(f"{partido:<10} {mr:<6} {rp:<6} {total:<10}")

print("-" * 50)
print(f"{'TOTAL':<10} {'':<6} {'':<6} {total_motor:<10}")

# Comparación detallada
print("\n" + "="*80)
print("COMPARACIÓN PARTIDO POR PARTIDO:")
print("="*80)
print(f"{'Partido':<10} {'Oficial':<10} {'Motor':<10} {'Diferencia':<12}")
print("-" * 50)

diferencias = {}
for _, row in df_2024.iterrows():
    partido = row['Partido']
    oficial = int(row['Total'])
    motor = motor_data.get(partido, {}).get('TOTAL', 0)
    dif = oficial - motor
    diferencias[partido] = dif
    
    marca = "✅" if dif == 0 else "❌"
    print(f"{partido:<10} {oficial:<10} {motor:<10} {dif:+d} {marca}")

print("-" * 50)
total_dif = sum(abs(d) for d in diferencias.values())
print(f"\nTotal diferencias (suma abs): {total_dif}")

print("\n" + "="*80)
print("ANÁLISIS DE MORENA:")
print("="*80)

morena_oficial = df_2024[df_2024['Partido'] == 'MORENA']['Total'].values[0]
morena_motor = motor_data['MORENA']['TOTAL']
morena_mr = motor_data['MORENA']['MR']
morena_rp = motor_data['MORENA']['RP']

print(f"\nMORENA Oficial:  {morena_oficial} escaños")
print(f"MORENA Motor:    {morena_motor} escaños ({morena_mr} MR + {morena_rp} RP)")
print(f"Diferencia:      {morena_oficial - morena_motor} escaños")

# Análisis: ¿De dónde vienen esos 10 escaños?
print(f"\n🔍 Hipótesis sobre los 10 escaños faltantes:")
print(f"\n1. Si MR es correcto (160):")
print(f"   Entonces MORENA debería tener: 160 MR + {257-160} RP = 257 total")
print(f"   Actualmente tiene: 160 MR + 87 RP = 247 total")
print(f"   📍 Faltan {(257-160) - 87} escaños de RP")

print(f"\n2. Si RP es correcto (87):")
print(f"   Entonces MORENA debería tener: {257-87} MR + 87 RP = 257 total")
print(f"   Actualmente tiene: 160 MR + 87 RP = 247 total")
print(f"   📍 Sobran {160 - (257-87)} escaños de MR")

print(f"\n3. Si ambos MR y RP son independientemente correctos:")
print(f"   Entonces hay un problema de topes o distribución global")

print("\n" + "="*80)
print("SIGUIENTES PASOS:")
print("="*80)
print("1. Verificar si 160 MR es el conteo correcto de distritos ganados")
print("2. Verificar si 87 RP es la asignación correcta proporcional")
print("3. Revisar si hay algún tope aplicándose que no debería")
print("4. Comparar con otros partidos para ver un patrón")
