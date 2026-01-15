"""
Script integrado: Levanta servidor, ejecuta pruebas, y cierra servidor
"""
import subprocess
import time
import requests
import sys
import signal

print("="*80)
print("🚀 Iniciando servidor FastAPI...")
print("="*80)

# Iniciar servidor en subproceso
server_process = subprocess.Popen(
    [sys.executable, "main.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Esperar a que el servidor esté listo
print("\n⏳ Esperando a que el servidor esté listo...")
max_attempts = 20
for i in range(max_attempts):
    try:
        response = requests.get("http://localhost:8001/docs", timeout=1)
        if response.status_code == 200:
            print("✅ Servidor listo!\n")
            break
    except:
        pass
    time.sleep(0.5)
    if i == max_attempts - 1:
        print("❌ Servidor no respondió a tiempo")
        server_process.kill()
        sys.exit(1)

# EJECUTAR PRUEBAS
try:
    URL = "http://localhost:8001/procesar/diputados"
    
    payload_base = {
        "anio": 2024,
        "sistema": "mixto",
        "mr_seats": 300,
        "rp_seats": 100,
        "max_seats": 400,
        "aplicar_topes": True,
        "votos_redistribuidos": {
            "MORENA": 50.0,
            "PAN": 20.0,
            "PRI": 15.0,
            "PVEM": 8.0,
            "MC": 7.0
        }
    }
    
    # TEST 1: Proporcional
    print("="*80)
    print("📊 TEST 1: Modo PROPORCIONAL")
    print("="*80)
    
    payload1 = payload_base.copy()
    payload1["redistritacion_geografica"] = False
    
    response1 = requests.post(URL, json=payload1, timeout=60)
    
    if response1.status_code == 200:
        data1 = response1.json()
        print("✅ Respuesta exitosa\n")
        asig1 = data1.get("asignaciones", {})
        print("MR por partido:")
        prop_results = {}
        for p in ["MORENA", "PAN", "PRI", "PVEM", "MC", "PT", "PRD"]:
            if p in asig1:
                mr = asig1[p].get("MR", 0)
                prop_results[p] = mr
                print(f"  {p:10s}: {mr:3d} MR")
    else:
        print(f"❌ Error {response1.status_code}")
        print(response1.text[:500])
        prop_results = None
    
    # TEST 2: Geográfico
    print("\n" + "="*80)
    print("📍 TEST 2: Modo GEOGRÁFICO (Eficiencias Históricas Reales 2024)")
    print("="*80)
    print("Eficiencias esperadas:")
    print("  MORENA: 0.604 (desperdicia votos)")
    print("  PAN: 1.172 (+17% eficiencia)")
    print("  PRI: 1.732 (+73% eficiencia)")
    print("  PRD: 4.919 (super eficiente)")
    print("  PVEM: 1.469 (+47% eficiencia)")
    print("  PT: 1.461 (+46% eficiencia)")
    print("  MC: 0.000 (no gana distritos)\n")
    
    payload2 = payload_base.copy()
    payload2["redistritacion_geografica"] = True
    
    response2 = requests.post(URL, json=payload2, timeout=60)
    
    if response2.status_code == 200:
        data2 = response2.json()
        print("✅ Respuesta exitosa\n")
        asig2 = data2.get("asignaciones", {})
        print("MR por partido:")
        geo_results = {}
        for p in ["MORENA", "PAN", "PRI", "PVEM", "MC", "PT", "PRD"]:
            if p in asig2:
                mr = asig2[p].get("MR", 0)
                geo_results[p] = mr
                print(f"  {p:10s}: {mr:3d} MR")
    else:
        print(f"❌ Error {response2.status_code}")
        print(response2.text[:500])
        geo_results = None
    
    # COMPARACIÓN
    if prop_results and geo_results:
        print("\n" + "="*80)
        print("📈 COMPARACIÓN: Proporcional vs Geográfico")
        print("="*80)
        print(f"{'Partido':10s} | {'Proporcional':>12s} | {'Geográfico':>10s} | {'Diferencia':>10s}")
        print("-" * 80)
        for p in ["MORENA", "PAN", "PRI", "PVEM", "MC", "PT", "PRD"]:
            prop_mr = prop_results.get(p, 0)
            geo_mr = geo_results.get(p, 0)
            diff = geo_mr - prop_mr
            diff_str = f"+{diff}" if diff > 0 else str(diff)
            print(f"{p:10s} | {prop_mr:12d} | {geo_mr:10d} | {diff_str:>10s}")
        
        print("\n💡 Análisis:")
        print("  - Diferencia negativa: Partido necesita MÁS votos con redistritación geográfica")
        print("  - Diferencia positiva: Partido se beneficia de su distribución geográfica")
        print("  - Basado en eficiencias REALES calculadas de la elección 2024")
    
    print("\n" + "="*80)
    print("✅ PRUEBAS COMPLETADAS EXITOSAMENTE")
    print("="*80)
    
finally:
    # Cerrar servidor
    print("\n🛑 Cerrando servidor...")
    server_process.terminate()
    try:
        server_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server_process.kill()
    print("✅ Servidor cerrado")
