"""
Script de ejecución INMEDIATA de pruebas del motor electoral
Ejecutar: python EJECUTAR_PRUEBAS_AHORA.py
"""
import subprocess
import sys
import os

def main():
    print("=" * 80)
    print("EJECUTANDO PRUEBAS DEL MOTOR ELECTORAL")
    print("=" * 80)
    print()
    
    # Cambiar al directorio del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print(f"[INFO] Directorio de trabajo: {os.getcwd()}")
    print()
    
    # Ejecutar pruebas básicas
    print("[TEST 1] Ejecutando pruebas básicas del motor...")
    print("-" * 80)
    
    try:
        result = subprocess.run(
            [sys.executable, "tests/test_motor_electoral.py"],
            capture_output=False,
            text=True
        )
        
        if result.returncode != 0:
            print()
            print("=" * 80)
            print("[ERROR] LAS PRUEBAS FALLARON")
            print("=" * 80)
            sys.exit(1)
        
        print()
        print("=" * 80)
        print("[OK] TODAS LAS PRUEBAS PASARON")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n[ERROR] No se pudieron ejecutar las pruebas: {e}")
        print("\nIntentando ejecución directa...")
        
        # Fallback: importar y ejecutar directamente
        sys.path.insert(0, script_dir)
        try:
            from tests import test_motor_electoral
            test_motor_electoral.main()
        except Exception as e2:
            print(f"[ERROR] Falló también la ejecución directa: {e2}")
            sys.exit(1)

if __name__ == "__main__":
    main()
