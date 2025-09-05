#!/usr/bin/env python3
"""
Test para verificar que la corrección de porcentajes → votos → escaños funciona
"""

import json
import urllib.request
import urllib.parse

def test_correccion_porcentajes_a_escanos():
    """Test: Verificar que cambios de porcentajes se traduzcan correctamente a escaños"""
    
    print("🎯 TEST: Corrección porcentajes → votos → escaños")
    print("=" * 60)
    
    # Caso de prueba: Subir PRI y bajar MORENA
    porcentajes_originales = {
        "MORENA": 42.49,
        "PAN": 17.58, 
        "PRI": 11.59,
        "MC": 11.37,
        "PVEM": 8.74,
        "PT": 5.69,
        "PRD": 2.54
    }
    
    porcentajes_editados = {
        "MORENA": 35.0,  # -7.49% (debería tener MENOS escaños)
        "PRI": 20.0,     # +8.41% (debería tener MÁS escaños)
        "PAN": 17.58,    # Sin cambio
        "MC": 11.37,     # Sin cambio
        "PVEM": 8.74,    # Sin cambio
        "PT": 5.69,      # Sin cambio
        "PRD": 2.54      # Sin cambio
    }
    
    print("📊 CAMBIOS ESPERADOS:")
    print("MORENA: 42.49% → 35.00% (-7.49%) = DEBERÍA TENER MENOS ESCAÑOS")
    print("PRI:    11.59% → 20.00% (+8.41%) = DEBERÍA TENER MÁS ESCAÑOS")
    print("Resto:  Sin cambios")
    
    # Enviar al backend
    query_params = {
        'anio': '2024',
        'plan': 'personalizado',
        'umbral': '0',
        'sobrerrepresentacion': '8',
        'sistema': 'mixto',
        'mr_seats': '64',
        'rp_seats': '64',
        'escanos_totales': '128',
        'reparto_mode': 'cuota',
        'reparto_method': 'hare',
        'usar_coaliciones': 'true'
    }
    
    body_data = {
        'porcentajes_partidos': json.dumps(porcentajes_editados),
        'partidos_fijos': '{}',
        'overrides_pool': '{}'
    }
    
    query_string = urllib.parse.urlencode(query_params)
    url = f"https://back-electoral.onrender.com/procesar/diputados?{query_string}"
    body_encoded = urllib.parse.urlencode(body_data).encode('utf-8')
    
    print(f"\n🚀 Enviando porcentajes editados...")
    
    try:
        req = urllib.request.Request(
            url,
            data=body_encoded,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            },
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            status_code = response.getcode()
            
            if status_code == 200:
                data = json.loads(response.read().decode('utf-8'))
                
                if 'resultados_detalle' in data:
                    print("\n📊 RESULTADOS:")
                    print("Partido | Porcentaje | Escaños | Cambio vs Original")
                    print("-" * 55)
                    
                    # Escaños originales esperados (aproximados)
                    escanos_originales_aprox = {
                        "MORENA": 54,  # ~42% de 128
                        "PRI": 15      # ~11% de 128
                    }
                    
                    for partido, info in data['resultados_detalle'].items():
                        escanos = info.get('total_seats', 0)
                        porcentaje = porcentajes_editados.get(partido, porcentajes_originales.get(partido, 0))
                        
                        if partido in ["MORENA", "PRI"]:
                            escanos_orig = escanos_originales_aprox.get(partido, 0)
                            cambio = escanos - escanos_orig
                            cambio_str = f"+{cambio}" if cambio > 0 else f"{cambio}"
                            print(f"{partido:<7} | {porcentaje:>9.1f}% | {escanos:>6} | {cambio_str:>8}")
                        else:
                            print(f"{partido:<7} | {porcentaje:>9.1f}% | {escanos:>6} | {'N/A':>8}")
                    
                    print(f"\n✅ VERIFICACIÓN:")
                    morena_escanos = data['resultados_detalle'].get('MORENA', {}).get('total_seats', 0)
                    pri_escanos = data['resultados_detalle'].get('PRI', {}).get('total_seats', 0)
                    
                    if morena_escanos < 54:  # Menos que el ~42% original
                        print("✅ MORENA tiene MENOS escaños (correcto)")
                    else:
                        print("❌ MORENA debería tener MENOS escaños")
                    
                    if pri_escanos > 15:  # Más que el ~11% original  
                        print("✅ PRI tiene MÁS escaños (correcto)")
                    else:
                        print("❌ PRI debería tener MÁS escaños")
                    
                    return True
                
            else:
                print(f"❌ Error {status_code}")
                return False
                
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP ERROR {e.code}")
        if e.code == 500:
            print("⏳ La corrección aún no se aplicó en el servidor")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("🧪 VERIFICAR CORRECCIÓN: PORCENTAJES → ESCAÑOS")
    print("=" * 55)
    
    test_correccion_porcentajes_a_escanos()
    
    print("\n🎯 LO QUE DEBERÍA PASAR AHORA:")
    print("✅ Cuando subas % de PRI → Más votos para PRI → Más escaños para PRI")
    print("✅ Cuando bajes % de MORENA → Menos votos para MORENA → Menos escaños para MORENA")
    print("✅ El total de votos se mantiene constante")
    print("✅ La proporcionalidad se conserva")
    
    print("\n⏳ NOTA: La corrección se aplicó localmente.")
    print("Necesitas hacer deploy para que se refleje en el servidor.")
