"""
Diagnóstico: ¿Por qué 300-100 SIN TOPES no genera datos?
"""

import sys
sys.path.append('.')

from engine.procesar_diputados_v2 import procesar_diputados_v2
import json

print("\n" + "="*80)
print("DIAGNÓSTICO: 300 MR + 100 RP SIN TOPES")
print("="*80)

# Probar con 2024
anio = 2024

print(f"\n[PRUEBA] Probando escenario para anio {anio}...")
print(f"   - 300 MR + 100 RP")
print(f"   - SIN TOPES (aplicar_topes=False)")
print(f"   - Umbral: 3%")

resultado = procesar_diputados_v2(
    path_parquet=f"data/computos_diputados_{anio}.parquet",
    anio=anio,
    max_seats=400,
    sistema='mixto',
    mr_seats=300,
    rp_seats=100,
    umbral=0.03,
    aplicar_topes=False,  # SIN TOPES
    usar_coaliciones=True,
    votos_redistribuidos=None,
    mr_ganados_geograficos=None,
    print_debug=True  # Activar debug
)

print("\n" + "="*80)
print("ESTRUCTURA DEL RESULTADO")
print("="*80)

print(f"\nClaves en resultado: {list(resultado.keys())}")

print("\n[CHART] seat_chart:")
seat_chart = resultado.get('seat_chart', [])
if seat_chart:
    print(f"   - Tipo: {type(seat_chart)}")
    print(f"   - Longitud: {len(seat_chart)}")
    print(f"   - Primeros 3 elementos:")
    for i, item in enumerate(seat_chart[:3]):
        print(f"      [{i}] {item}")
else:
    print("   [X] VACIO O NO EXISTE")

print("\n[PARTIDO] resultados_por_partido:")
resultados_partido = resultado.get('resultados_por_partido', [])
if resultados_partido:
    print(f"   - Tipo: {type(resultados_partido)}")
    print(f"   - Longitud: {len(resultados_partido)}")
    print(f"   - Primeros 3 elementos:")
    for i, item in enumerate(resultados_partido[:3]):
        print(f"      [{i}] {item}")
else:
    print("   [X] VACIO O NO EXISTE")

print("\n[OTRAS] Otras claves importantes:")
for key in ['total_seats', 'kpis', 'metadata']:
    if key in resultado:
        val = resultado[key]
        if isinstance(val, (dict, list)):
            print(f"   - {key}: {type(val).__name__} con {len(val)} elementos")
        else:
            print(f"   - {key}: {val}")
    else:
        print(f"   - {key}: NO EXISTE")

# Buscar MORENA, PT, PVEM en todos los lugares
print("\n" + "="*80)
print("BÚSQUEDA DE MORENA, PT, PVEM")
print("="*80)

partidos_4t = ['MORENA', 'PT', 'PVEM']

# En seat_chart
print("\n[BUSQUEDA] En seat_chart:")
if seat_chart:
    for partido in partidos_4t:
        encontrado = [item for item in seat_chart if item.get('partido') == partido]
        if encontrado:
            print(f"   [OK] {partido}: {encontrado[0]}")
        else:
            print(f"   [X] {partido}: NO ENCONTRADO")
else:
    print("   [!] seat_chart esta vacio")

# En resultados_por_partido
print("\n[BUSQUEDA] En resultados_por_partido:")
if resultados_partido:
    for partido in partidos_4t:
        encontrado = [item for item in resultados_partido if item.get('partido') == partido]
        if encontrado:
            print(f"   [OK] {partido}: {encontrado[0]}")
        else:
            print(f"   [X] {partido}: NO ENCONTRADO")
else:
    print("   [!] resultados_por_partido esta vacio")

# Imprimir TODO el resultado en formato JSON para análisis
print("\n" + "="*80)
print("DUMP COMPLETO DEL RESULTADO (JSON)")
print("="*80)

# Función para convertir a JSON-serializable
def make_serializable(obj):
    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable(item) for item in obj]
    elif isinstance(obj, (int, float, str, bool, type(None))):
        return obj
    else:
        return str(obj)

resultado_serializable = make_serializable(resultado)

# Guardar a archivo
output_file = "diagnostico_300_sin_topes_resultado.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(resultado_serializable, f, indent=2, ensure_ascii=False)

print(f"\n[OK] Resultado completo guardado en: {output_file}")

# Mostrar primeras líneas
print(f"\n[ARCHIVO] Primeras 100 lineas del JSON:")
print("-" * 80)
json_str = json.dumps(resultado_serializable, indent=2, ensure_ascii=False)
lines = json_str.split('\n')[:100]
print('\n'.join(lines))
if len(json_str.split('\n')) > 100:
    print(f"\n... ({len(json_str.split('\n')) - 100} lineas mas en el archivo)")

print("\n" + "="*80)
print("[OK] DIAGNOSTICO COMPLETADO")
print("="*80)
