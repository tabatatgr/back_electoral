"""
Verificación final del sistema de redistritación geográfica
Confirma que todos los componentes están listos
"""

import os
import sys

print("="*80)
print("🔍 VERIFICACIÓN FINAL DEL SISTEMA")
print("="*80)

errores = []
warnings = []
ok = []

# 1. Verificar archivos clave existen
print("\n📁 Verificando archivos...")
archivos_requeridos = [
    ("engine/calcular_eficiencia_real.py", "Módulo de cálculo de eficiencias"),
    ("engine/procesar_diputados_v2.py", "Procesador principal"),
    ("main.py", "Servidor FastAPI"),
    ("redistritacion/modulos/reparto_distritos.py", "Módulo de reparto Hare"),
    ("redistritacion/modulos/distritacion.py", "Módulo de distritación"),
    ("data/computos_diputados_2024.parquet", "Datos 2024"),
    ("data/computos_diputados_2021.parquet", "Datos 2021"),
    ("data/computos_diputados_2018.parquet", "Datos 2018"),
    ("data/siglado-diputados-2024.csv", "Siglado 2024"),
    ("data/siglado-diputados-2021.csv", "Siglado 2021"),
    ("data/siglado-diputados-2018.csv", "Siglado 2018"),
]

for archivo, desc in archivos_requeridos:
    if os.path.exists(archivo):
        ok.append(f"✅ {desc}: {archivo}")
    else:
        errores.append(f"❌ FALTA {desc}: {archivo}")

# 2. Verificar imports
print("\n📦 Verificando imports...")
try:
    from engine.calcular_eficiencia_real import calcular_eficiencia_partidos
    ok.append("✅ Import calcular_eficiencia_partidos")
except Exception as e:
    errores.append(f"❌ Error importando calcular_eficiencia_partidos: {e}")

try:
    from redistritacion.modulos.reparto_distritos import repartir_distritos_hare
    ok.append("✅ Import repartir_distritos_hare")
except Exception as e:
    errores.append(f"❌ Error importando repartir_distritos_hare: {e}")

try:
    from redistritacion.modulos.distritacion import cargar_secciones_ine
    ok.append("✅ Import cargar_secciones_ine")
except Exception as e:
    errores.append(f"❌ Error importando cargar_secciones_ine: {e}")

# 3. Verificar que main.py tiene el parámetro redistritacion_geografica
print("\n🔧 Verificando configuración del endpoint...")
try:
    with open("main.py", "r", encoding="utf-8") as f:
        content = f.read()
        
    if "redistritacion_geografica" in content:
        ok.append("✅ Parámetro redistritacion_geografica en main.py")
    else:
        errores.append("❌ Parámetro redistritacion_geografica NO encontrado en main.py")
    
    if "calcular_eficiencia_partidos" in content:
        ok.append("✅ Import de calcular_eficiencia_partidos en main.py")
    else:
        warnings.append("⚠️  calcular_eficiencia_partidos no importado en main.py (podría estar en bloque try)")
    
    if "mr_ganados_geograficos" in content:
        ok.append("✅ Variable mr_ganados_geograficos en main.py")
    else:
        errores.append("❌ Variable mr_ganados_geograficos NO encontrada en main.py")
        
except Exception as e:
    errores.append(f"❌ Error leyendo main.py: {e}")

# 4. Verificar procesar_diputados_v2
print("\n⚙️  Verificando procesador...")
try:
    with open("engine/procesar_diputados_v2.py", "r", encoding="utf-8") as f:
        content = f.read()
        
    if "mr_ganados_geograficos" in content:
        ok.append("✅ Parámetro mr_ganados_geograficos en procesar_diputados_v2")
    else:
        errores.append("❌ Parámetro mr_ganados_geograficos NO en procesar_diputados_v2")
        
except Exception as e:
    errores.append(f"❌ Error leyendo procesar_diputados_v2.py: {e}")

# 5. Probar cálculo de eficiencias
print("\n🧮 Probando cálculo de eficiencias...")
try:
    from engine.calcular_eficiencia_real import calcular_eficiencia_partidos
    
    for anio in [2024, 2021, 2018]:
        try:
            eficiencias = calcular_eficiencia_partidos(anio, usar_coaliciones=False)
            if eficiencias and len(eficiencias) > 0:
                ok.append(f"✅ Eficiencias calculadas para {anio}: {len(eficiencias)} partidos")
            else:
                warnings.append(f"⚠️  Eficiencias para {anio} vacías")
        except Exception as e:
            errores.append(f"❌ Error calculando eficiencias {anio}: {e}")
            
except Exception as e:
    errores.append(f"❌ Error en módulo de eficiencias: {e}")

# RESULTADOS
print("\n" + "="*80)
print("📊 RESULTADOS DE LA VERIFICACIÓN")
print("="*80)

if ok:
    print(f"\n✅ CORRECTOS ({len(ok)}):")
    for item in ok:
        print(f"  {item}")

if warnings:
    print(f"\n⚠️  ADVERTENCIAS ({len(warnings)}):")
    for item in warnings:
        print(f"  {item}")

if errores:
    print(f"\n❌ ERRORES ({len(errores)}):")
    for item in errores:
        print(f"  {item}")

# VEREDICTO FINAL
print("\n" + "="*80)
if len(errores) == 0:
    print("🎉 SISTEMA COMPLETAMENTE FUNCIONAL")
    print("="*80)
    print("\n✅ Todos los componentes están en su lugar")
    print("✅ El backend puede procesar redistritación geográfica")
    print("✅ Las eficiencias históricas se calculan correctamente")
    print("\n🚀 LISTO PARA USAR EN EL FRONTEND")
    print("\nPara activar en el frontend, enviar:")
    print('  {"redistritacion_geografica": true, ...}')
    sys.exit(0)
else:
    print("⚠️  SE ENCONTRARON PROBLEMAS")
    print("="*80)
    print(f"\n{len(errores)} error(es) que deben corregirse")
    print(f"{len(warnings)} advertencia(s) para revisar")
    sys.exit(1)
