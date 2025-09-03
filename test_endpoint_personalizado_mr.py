#!/usr/bin/env python3
"""
Test para simular exactamente lo que hace el frontend con personalizado + MR
"""

import requests
import json

def test_frontend_personalizado_mr():
    """Test que simula el frontend enviando personalizado + MR"""
    
    print("🔍 TEST ENDPOINT PERSONALIZADO MR - SIMULANDO FRONTEND")
    print("=" * 60)
    
    base_url = "http://localhost:8001"  # Asumiendo que el servidor está corriendo
    
    configs = [
        {"escanos": 200, "descripcion": "200 escaños MR personalizado"},
        {"escanos": 250, "descripcion": "250 escaños MR personalizado"},
        {"escanos": 400, "descripcion": "400 escaños MR personalizado"},
        {"escanos": 500, "descripcion": "500 escaños MR personalizado"}
    ]
    
    for config in configs:
        escanos_totales = config["escanos"]
        print(f"📊 {config['descripcion']}")
        
        # Parámetros exactos que enviaría el frontend
        params = {
            "anio": 2018,
            "plan": "personalizado",
            "sistema": "mr",  # MR puro
            "escanos_totales": escanos_totales,
            "mr_seats": None,  # No especificado, debería calcularse automáticamente
            "rp_seats": None,  # No especificado, debería ser 0 para MR
            "umbral": 0.03,
            "max_seats_per_party": None,
            "sobrerrepresentacion": True,
            "quota_method": "hare",
            "divisor_method": "dhondt"
        }
        
        print(f"   Enviando: {escanos_totales} escaños totales, sistema='mr'")
        
        try:
            response = requests.post(f"{base_url}/procesar/diputados", params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Contar escaños totales
                total_calculado = 0
                if 'partidos' in data:
                    for partido in data['partidos']:
                        total_calculado += partido.get('escanos', 0)
                
                print(f"   ✅ Status: {response.status_code}")
                print(f"   📊 Total calculado: {total_calculado}")
                print(f"   🎯 Total solicitado: {escanos_totales}")
                
                if total_calculado == escanos_totales:
                    print(f"   ✅ CORRECTO: Respeta los {escanos_totales} escaños configurados")
                elif total_calculado == 300:
                    print(f"   ❌ ERROR: Sigue forzando 300 escaños (ignoró configuración)")
                else:
                    print(f"   ⚠️  RARO: Dio {total_calculado} escaños (ni 300 ni {escanos_totales})")
                    
            else:
                print(f"   ❌ Error HTTP: {response.status_code}")
                print(f"   ❌ Detalle: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error de conexión: {e}")
            print(f"   💡 ¿Está corriendo el servidor en {base_url}?")
            
        print()
    
    print("💡 Si todos muestran '✅ CORRECTO', entonces el endpoint YA NO fuerza 300 escaños")

if __name__ == "__main__":
    test_frontend_personalizado_mr()
