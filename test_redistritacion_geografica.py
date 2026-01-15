"""
Script para probar la redistritación geográfica en el endpoint /procesar/diputados

Compara:
1. Redistritación proporcional (actual, default)
2. Redistritación geográfica con eficiencia 1.1 (nuevo)

Para un escenario de ejemplo con MORENA al 50%
"""

import requests
import json

# URL del endpoint
BASE_URL = "http://localhost:8001"
ENDPOINT = f"{BASE_URL}/procesar/diputados"

# Escenario de prueba: MORENA con 50% de votos
# Según cálculos en votos_minimos_morena.csv:
# - Proporcional: ~47-48% → 155 MR aproximadamente  
# - Geográfico (eficiencia 1.1): 50.0% → 153 MR
VOTOS_TEST = {
    "MORENA": 50.0,
    "PAN": 20.0,
    "PRI": 15.0,
    "PVEM": 8.0,
    "MC": 7.0
}

def test_proporcional():
    """Prueba con redistritación proporcional (modo actual)"""
    print("\n" + "="*80)
    print("TEST 1: REDISTRITACIÓN PROPORCIONAL (modo actual)")
    print("="*80)
    
    payload = {
        "anio": 2024,
        "sistema": "mixto",
        "mr_seats": 300,
        "rp_seats": 100,
        "max_seats": 400,
        "aplicar_topes": True,
        "votos_redistribuidos": VOTOS_TEST,
        "redistritacion_geografica": False  # Modo proporcional
    }
    
    print(f"\nPayload enviado:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(ENDPOINT, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        print(f"\nResultados:")
        print(f"Status: {response.status_code}")
        
        # Extraer info relevante
        if "asignaciones" in data:
            asignaciones = data["asignaciones"]
            print(f"\nAsignaciones por partido:")
            for partido, valores in asignaciones.items():
                mr = valores.get("MR", 0)
                rp = valores.get("RP", 0)
                total = valores.get("Total", 0)
                print(f"  {partido:10s}: MR={mr:3d}, RP={rp:3d}, Total={total:3d}")
            
            # Calcular totales
            total_mr = sum(v.get("MR", 0) for v in asignaciones.values())
            total_rp = sum(v.get("RP", 0) for v in asignaciones.values())
            total_seats = sum(v.get("Total", 0) for v in asignaciones.values())
            
            print(f"\nTOTALES: MR={total_mr}, RP={total_rp}, Total={total_seats}")
            
        return data
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return None


def test_geografico():
    """Prueba con redistritación geográfica (modo nuevo)"""
    print("\n" + "="*80)
    print("TEST 2: REDISTRITACIÓN GEOGRÁFICA (con eficiencias históricas reales)")
    print("="*80)
    
    payload = {
        "anio": 2024,
        "sistema": "mixto",
        "mr_seats": 300,
        "rp_seats": 100,
        "max_seats": 400,
        "aplicar_topes": True,
        "votos_redistribuidos": VOTOS_TEST,
        "redistritacion_geografica": True  # Modo geográfico (calcula eficiencias automáticamente)
    }
    
    print(f"\nPayload enviado:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(ENDPOINT, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        print(f"\nResultados:")
        print(f"Status: {response.status_code}")
        
        # Extraer info relevante
        if "asignaciones" in data:
            asignaciones = data["asignaciones"]
            print(f"\nAsignaciones por partido:")
            for partido, valores in asignaciones.items():
                mr = valores.get("MR", 0)
                rp = valores.get("RP", 0)
                total = valores.get("Total", 0)
                print(f"  {partido:10s}: MR={mr:3d}, RP={rp:3d}, Total={total:3d}")
            
            # Calcular totales
            total_mr = sum(v.get("MR", 0) for v in asignaciones.values())
            total_rp = sum(v.get("RP", 0) for v in asignaciones.values())
            total_seats = sum(v.get("Total", 0) for v in asignaciones.values())
            
            print(f"\nTOTALES: MR={total_mr}, RP={total_rp}, Total={total_seats}")
            
        return data
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return None


def comparar_resultados(prop_data, geo_data):
    """Compara los resultados de ambos métodos"""
    print("\n" + "="*80)
    print("COMPARACIÓN DE RESULTADOS")
    print("="*80)
    
    if not prop_data or not geo_data:
        print("❌ No se pudieron obtener ambos resultados para comparar")
        return
    
    prop_asig = prop_data.get("asignaciones", {})
    geo_asig = geo_data.get("asignaciones", {})
    
    print(f"\n{'Partido':<12} | {'Proporcional':<15} | {'Geográfico':<15} | {'Diferencia':<10}")
    print("-" * 75)
    
    for partido in sorted(set(list(prop_asig.keys()) + list(geo_asig.keys()))):
        prop_mr = prop_asig.get(partido, {}).get("MR", 0)
        geo_mr = geo_asig.get(partido, {}).get("MR", 0)
        diff = geo_mr - prop_mr
        diff_str = f"+{diff}" if diff > 0 else str(diff)
        
        print(f"{partido:<12} | {prop_mr:3d} MR         | {geo_mr:3d} MR         | {diff_str:>10}")
    
    # Totales
    total_prop = sum(v.get("MR", 0) for v in prop_asig.values())
    total_geo = sum(v.get("MR", 0) for v in geo_asig.values())
    
    print("-" * 75)
    print(f"{'TOTAL':<12} | {total_prop:3d}            | {total_geo:3d}            | {total_geo - total_prop:+10d}")
    
    print("\nNOTA:")
    print("  - Proporcional: Distribución simple por porcentaje de votos")
    print("  - Geográfico: Método Hare con población real por estado")
    print("  - Geográfico usa eficiencias HISTÓRICAS de cada partido (2024)")
    print("  - Eficiencia = (% distritos ganados) / (% votos nacionales) en elección real")


if __name__ == "__main__":
    print("\n🧪 PRUEBA DE REDISTRITACIÓN GEOGRÁFICA")
    print("Escenario: MORENA 50%, PAN 20%, PRI 15%, PVEM 8%, MC 7%")
    print("Sistema: 300 MR + 100 RP = 400 total, CON TOPES")
    
    # Ejecutar pruebas
    prop_result = test_proporcional()
    geo_result = test_geografico()
    
    # Comparar
    comparar_resultados(prop_result, geo_result)
    
    print("\n" + "="*80)
    print("✅ Pruebas completadas")
    print("="*80)
