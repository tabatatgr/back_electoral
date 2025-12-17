"""
Verificar el resultado OFICIAL de MORENA en 2024
Procesando correctamente con el motor
"""

from engine.procesar_diputados_v2 import procesar_diputados_v2
import pandas as pd

print("="*80)
print("VERIFICACIÓN: ¿Cuántos escaños obtiene MORENA con sistema vigente 2024?")
print("="*80)

# Sistema vigente EXACTO como está configurado en main.py
resultado = procesar_diputados_v2(
    path_parquet="data/computos_diputados_2024.parquet",
    anio=2024,
    path_siglado="data/siglado-diputados-2024.csv",
    max_seats=500,
    sistema="mixto",
    mr_seats=None,  # Calcula del siglado (ganadores por distrito)
    rp_seats=200,   # 200 RP fijos
    pm_seats=0,     # Sin PM
    umbral=0.03,
    max_seats_per_party=300,  # Límite constitucional
    sobrerrepresentacion=None,  # SIN límite % (solo el tope de 300)
    aplicar_topes=True,
    quota_method="hare",
    divisor_method=None,
    usar_coaliciones=True,  # Usar coaliciones como en la realidad
    votos_redistribuidos=None,
    print_debug=False
)

print("\n" + "="*80)
print("RESULTADO DEL MOTOR:")
print("="*80)

# El motor devuelve diccionario con resultados directamente, no con 'status'
if resultado and 'tot' in resultado:
    # Convertir formato antiguo a nuevo
    partidos_dict = resultado['tot']
    partidos = []
    for partido, total in partidos_dict.items():
        partidos.append({
            'PARTIDO': partido,
            'MR': resultado['mr'].get(partido, 0),
            'RP': resultado['rp'].get(partido, 0),
            'TOTAL': total
        })
    
    print("\nTodos los partidos:")
    print(f"{'Partido':<10} {'MR':<6} {'RP':<6} {'TOTAL':<6}")
    print("-" * 35)
    
    total_escanos = 0
    for p in partidos:
        partido = p['PARTIDO']
        mr = p.get('MR', 0)
        rp = p.get('RP', 0)
        total = p.get('TOTAL', 0)
        total_escanos += total
        print(f"{partido:<10} {mr:<6} {rp:<6} {total:<6}")
    
    print("-" * 35)
    print(f"{'TOTAL':<10} {'':<6} {'':<6} {total_escanos:<6}")
    
    # Verificar MORENA
    morena = next((p for p in partidos if p['PARTIDO'] == 'MORENA'), None)
    
    print("\n" + "="*80)
    print("COMPARACIÓN CON DATO OFICIAL:")
    print("="*80)
    
    if morena:
        morena_motor = morena.get('TOTAL', 0)
        
        # Leer dato oficial
        df_oficial = pd.read_csv('data/escaños_resumen_camaras_2018_2021_2024_oficial_gallagher_ratio_promedio(2).csv')
        morena_oficial = df_oficial[(df_oficial['Año'] == 2024) & 
                                     (df_oficial['Cámara'] == 'Diputados') & 
                                     (df_oficial['Partido'] == 'MORENA')]['Total'].values[0]
        
        print(f"\nMORENA:")
        print(f"  Dato oficial 2024:    {morena_oficial} escaños")
        print(f"  Resultado del motor:  {morena_motor} escaños")
        print(f"  Diferencia:           {morena_oficial - morena_motor} escaños")
        
        if morena_motor == morena_oficial:
            print(f"\n✅ ¡PERFECTO! El motor reproduce exactamente el resultado oficial")
        elif abs(morena_motor - morena_oficial) <= 5:
            print(f"\n⚠️ Diferencia pequeña ({abs(morena_motor - morena_oficial)} escaños)")
        else:
            print(f"\n❌ ERROR: Diferencia significativa de {abs(morena_motor - morena_oficial)} escaños")
            print(f"\n🔍 Posibles causas:")
            print(f"   - Problema en conteo de MR (ganadores por distrito)")
            print(f"   - Problema en asignación de RP")
            print(f"   - Problema en aplicación de topes")
    else:
        print("❌ ERROR: No se encontró MORENA en los resultados")
        
else:
    print("❌ ERROR en el procesamiento")
    print("Resultado devuelto:")
    print(resultado)
