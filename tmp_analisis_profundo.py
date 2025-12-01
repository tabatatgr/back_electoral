"""
Análisis detallado: ¿Por qué MORENA tiene los mismos escaños totales?
Verificar si el problema está en la distribución de votos o en el cálculo RP
"""
from engine.procesar_diputados_v2 import procesar_diputados_v2
import pandas as pd

print("="*80)
print("ANÁLISIS PROFUNDO: Votos y Distribución RP")
print("="*80)

# Cargar datos originales
df = pd.read_parquet('data/computos_diputados_2024.parquet')

# Ver votos nacionales totales
print("\n1. VOTOS NACIONALES ORIGINALES (de parquet):")
print("-" * 60)
votos_totales = {}
for partido in ['MORENA', 'PT', 'PVEM', 'PAN', 'PRI', 'PRD', 'MC']:
    if partido in df.columns:
        votos = df[partido].sum()
        votos_totales[partido] = votos
        print(f"  {partido:10} {votos:>12,} votos")

total_votos = sum(votos_totales.values())
print(f"  {'TOTAL':10} {total_votos:>12,} votos")

print("\n2. PORCENTAJES NACIONALES:")
print("-" * 60)
for partido in ['MORENA', 'PT', 'PVEM', 'PAN', 'PRI', 'PRD', 'MC']:
    if partido in votos_totales:
        pct = (votos_totales[partido] / total_votos) * 100
        print(f"  {partido:10} {pct:>6.2f}%")

# Procesar CON coalición
print("\n" + "="*80)
print("3. PROCESAMIENTO CON COALICIÓN")
print("="*80)
resultado_con = procesar_diputados_v2(
    path_parquet='data/computos_diputados_2024.parquet',
    anio=2024,
    path_siglado='data/siglado-diputados-2024.csv',
    max_seats=500,
    sistema='mixto',
    mr_seats=250,
    rp_seats=250,
    umbral=0.03,
    quota_method='hare',
    usar_coaliciones=True,
    print_debug=False
)

print("\nResultados CON coalición:")
print(f"  MORENA: {resultado_con['mr']['MORENA']} MR + {resultado_con['rp']['MORENA']} RP = {resultado_con['tot']['MORENA']} TOTAL")
print(f"  PT:     {resultado_con['mr']['PT']} MR + {resultado_con['rp']['PT']} RP = {resultado_con['tot']['PT']} TOTAL")
print(f"  PVEM:   {resultado_con['mr']['PVEM']} MR + {resultado_con['rp']['PVEM']} RP = {resultado_con['tot']['PVEM']} TOTAL")
bloque_con = resultado_con['tot']['MORENA'] + resultado_con['tot']['PT'] + resultado_con['tot']['PVEM']
print(f"  BLOQUE: {bloque_con} escaños")

# Procesar SIN coalición
print("\n" + "="*80)
print("4. PROCESAMIENTO SIN COALICIÓN")
print("="*80)
resultado_sin = procesar_diputados_v2(
    path_parquet='data/computos_diputados_2024.parquet',
    anio=2024,
    path_siglado='data/siglado-diputados-2024.csv',
    max_seats=500,
    sistema='mixto',
    mr_seats=250,
    rp_seats=250,
    umbral=0.03,
    quota_method='hare',
    usar_coaliciones=False,
    print_debug=False
)

print("\nResultados SIN coalición:")
print(f"  MORENA: {resultado_sin['mr']['MORENA']} MR + {resultado_sin['rp']['MORENA']} RP = {resultado_sin['tot']['MORENA']} TOTAL")
print(f"  PT:     {resultado_sin['mr']['PT']} MR + {resultado_sin['rp']['PT']} RP = {resultado_sin['tot']['PT']} TOTAL")
print(f"  PVEM:   {resultado_sin['mr']['PVEM']} MR + {resultado_sin['rp']['PVEM']} RP = {resultado_sin['tot']['PVEM']} TOTAL")
bloque_sin = resultado_sin['tot']['MORENA'] + resultado_sin['tot']['PT'] + resultado_sin['tot']['PVEM']
print(f"  BLOQUE: {bloque_sin} escaños")

# ANÁLISIS
print("\n" + "="*80)
print("5. ANÁLISIS DEL PROBLEMA")
print("="*80)

print("\nMR (Mayoría Relativa):")
print(f"  MORENA: {resultado_sin['mr']['MORENA']} SIN → {resultado_con['mr']['MORENA']} CON (Δ={resultado_con['mr']['MORENA']-resultado_sin['mr']['MORENA']:+d})")
print(f"  PT:     {resultado_sin['mr']['PT']} SIN → {resultado_con['mr']['PT']} CON (Δ={resultado_con['mr']['PT']-resultado_sin['mr']['PT']:+d})")
print(f"  PVEM:   {resultado_sin['mr']['PVEM']} SIN → {resultado_con['mr']['PVEM']} CON (Δ={resultado_con['mr']['PVEM']-resultado_sin['mr']['PVEM']:+d})")

print("\nRP (Representación Proporcional):")
print(f"  MORENA: {resultado_sin['rp']['MORENA']} SIN → {resultado_con['rp']['MORENA']} CON (Δ={resultado_con['rp']['MORENA']-resultado_sin['rp']['MORENA']:+d})")
print(f"  PT:     {resultado_sin['rp']['PT']} SIN → {resultado_con['rp']['PT']} CON (Δ={resultado_con['rp']['PT']-resultado_sin['rp']['PT']:+d})")
print(f"  PVEM:   {resultado_sin['rp']['PVEM']} SIN → {resultado_con['rp']['PVEM']} CON (Δ={resultado_con['rp']['PVEM']-resultado_sin['rp']['PVEM']:+d})")

print("\nTOTAL:")
print(f"  MORENA: {resultado_sin['tot']['MORENA']} SIN → {resultado_con['tot']['MORENA']} CON (Δ={resultado_con['tot']['MORENA']-resultado_sin['tot']['MORENA']:+d})")
print(f"  PT:     {resultado_sin['tot']['PT']} SIN → {resultado_con['tot']['PT']} CON (Δ={resultado_con['tot']['PT']-resultado_sin['tot']['PT']:+d})")
print(f"  PVEM:   {resultado_sin['tot']['PVEM']} SIN → {resultado_con['tot']['PVEM']} CON (Δ={resultado_con['tot']['PVEM']-resultado_sin['tot']['PVEM']:+d})")

print("\n" + "="*80)
print("6. DIAGNÓSTICO")
print("="*80)

if resultado_sin['tot']['MORENA'] == resultado_con['tot']['MORENA']:
    print("❌ PROBLEMA CONFIRMADO: MORENA tiene exactamente los mismos escaños totales")
    print("")
    print("Posibles causas:")
    print("  1. Los VOTOS no cambian entre escenarios (usar misma base de votos)")
    print("  2. El tope 8% está compensando exactamente la pérdida MR con RP")
    print("  3. La distribución RP se calcula por BLOQUE en lugar de por PARTIDO")
    print("")
    
    # Verificar si es compensación perfecta
    delta_mr_morena = resultado_con['mr']['MORENA'] - resultado_sin['mr']['MORENA']
    delta_rp_morena = resultado_con['rp']['MORENA'] - resultado_sin['rp']['MORENA']
    
    if abs(delta_mr_morena + delta_rp_morena) < 2:
        print("  → CAUSA IDENTIFICADA: Compensación RP perfecta")
        print(f"     MORENA pierde {abs(delta_mr_morena)} MR pero gana {delta_rp_morena} RP")
        print(f"     Diferencia neta: {delta_mr_morena + delta_rp_morena}")
        print("")
        print("  EXPLICACIÓN: El sistema RP está compensando automáticamente")
        print("  porque MORENA tiene menos MR, entonces el tope 8% le da más RP.")
        print("")
        print("  ESTO ES CORRECTO si:")
        print("    - Los votos de MORENA son LOS MISMOS en ambos escenarios")
        print("    - El tope 8% se calcula POR PARTIDO")
        print("")
        print("  PREGUNTA CLAVE: ¿Los votos de MORENA deberían REDUCIRSE")
        print("  cuando se rompe la coalición?")
else:
    print("✅ OK: MORENA tiene diferentes escaños totales")
    print(f"   Diferencia: {resultado_con['tot']['MORENA'] - resultado_sin['tot']['MORENA']:+d} escaños")
