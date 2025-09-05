import requests
import json

def test_partidos_endpoint():
    """Test para verificar que el endpoint /partidos/por-anio regresa el JSON correcto"""
    
    base_url = "https://back-electoral.onrender.com"  # Tu URL de producción
    
    # Test para diferentes años
    años = [2018, 2021, 2024]
    
    for año in años:
        print(f"\n🔍 Probando año {año}...")
        
        try:
            # Llamada al endpoint
            url = f"{base_url}/partidos/por-anio?anio={año}&camara=diputados"
            response = requests.get(url, timeout=30)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verificar estructura
                print(f"✅ Respuesta exitosa para {año}")
                print(f"Keys en respuesta: {list(data.keys())}")
                
                if 'partidos' in data:
                    partidos = data['partidos']
                    print(f"📊 Encontrados {len(partidos)} partidos")
                    
                    # Mostrar estructura de los primeros partidos
                    for i, partido in enumerate(partidos[:3]):
                        print(f"  Partido {i+1}: {list(partido.keys())}")
                        print(f"    {partido}")
                    
                    # Verificar que tengan los campos necesarios
                    campos_requeridos = ['partido', 'porcentaje_vigente']
                    todos_ok = True
                    for partido in partidos:
                        for campo in campos_requeridos:
                            if campo not in partido:
                                print(f"❌ FALTA CAMPO '{campo}' en partido {partido.get('partido', 'UNKNOWN')}")
                                todos_ok = False
                    
                    if todos_ok:
                        print(f"✅ Todos los partidos tienen campos requeridos")
                    
                    # Verificar suma de porcentajes
                    total_porcentaje = sum(p.get('porcentaje_vigente', 0) for p in partidos)
                    print(f"📈 Suma total porcentajes: {total_porcentaje:.2f}%")
                    
                    if abs(total_porcentaje - 100) < 1:
                        print("✅ Suma de porcentajes OK (~100%)")
                    else:
                        print(f"⚠️ Suma de porcentajes extraña: {total_porcentaje}%")
                
                else:
                    print(f"❌ No se encontró key 'partidos' en respuesta")
                    print(f"Respuesta completa: {data}")
            
            else:
                print(f"❌ Error HTTP {response.status_code}")
                print(f"Respuesta: {response.text[:500]}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def test_formato_para_frontend():
    """Test específico para el formato que necesita el frontend"""
    
    print("\n🎯 Test formato para frontend...")
    
    try:
        url = "https://back-electoral.onrender.com/partidos/por-anio?anio=2024&camara=diputados"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Convertir al formato que necesita el frontend
            if 'partidos' in data:
                porcentajes_iniciales = {}
                
                for partido in data['partidos']:
                    nombre = partido.get('partido')
                    porcentaje = partido.get('porcentaje_vigente', 0)
                    
                    if nombre:
                        porcentajes_iniciales[nombre] = porcentaje
                
                print("📋 Formato para frontend:")
                print(json.dumps(porcentajes_iniciales, indent=2, ensure_ascii=False))
                
                # Verificar suma
                total = sum(porcentajes_iniciales.values())
                print(f"\n📊 Total: {total:.2f}%")
                
                # Código JavaScript equivalente
                print("\n🔧 Código para el frontend:")
                print("```javascript")
                print("const obtenerPartidos = async (anio) => {")
                print("  const response = await fetch(`${API_BASE}/partidos/por-anio?anio=${anio}&camara=diputados`);")
                print("  const data = await response.json();")
                print("  ")
                print("  const partidosIniciales = {};")
                print("  data.partidos.forEach(p => {")
                print("    partidosIniciales[p.partido] = p.porcentaje_vigente;")
                print("  });")
                print("  ")
                print("  return partidosIniciales;")
                print("};")
                print("```")
                
                # Test de ejemplo para el brief
                print("\n🎯 Ejemplo para el brief del frontend:")
                print("```javascript")
                print("// Estado inicial desde el backend:")
                print(f"const [porcentajes, setPorcentajes] = useState({json.dumps(porcentajes_iniciales, ensure_ascii=False)});")
                print("```")
                
            else:
                print("❌ No hay key 'partidos'")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_request_real():
    """Test con un request real completo para verificar respuesta"""
    
    print("\n🚀 Test request completo...")
    
    try:
        # Simular request del frontend
        params = {
            'anio': 2024,
            'plan': 'personalizado',
            'mr_seats': 64,
            'rp_seats': 64,
            'escanos_totales': 128,
            'umbral': 0,
            'sobrerrepresentacion': 8,
            'reparto_mode': 'cuota',
            'reparto_method': 'hare',
            'usar_coaliciones': True,
            'porcentajes_partidos': json.dumps({
                "MORENA": 35.0,
                "PAN": 25.0,
                "PRI": 15.0,
                "MC": 12.0,
                "PVEM": 8.0,
                "PT": 3.0,
                "PRD": 2.0
            }),
            'partidos_fijos': json.dumps({}),
            'overrides_pool': json.dumps({})
        }
        
        print("📤 Enviando request con porcentajes personalizados...")
        
        response = requests.post(
            "https://back-electoral.onrender.com/procesar/diputados",
            data=params,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=60
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ Respuesta del backend:")
            print(f"Keys disponibles: {list(data.keys())}")
            
            # Verificar campos que necesita el frontend
            campos_esperados = ['seat_chart', 'kpis', 'resultados_detalle', 'meta']
            
            for campo in campos_esperados:
                if campo in data:
                    print(f"✅ Campo '{campo}': presente")
                    if campo == 'seat_chart' and data[campo]:
                        print(f"   - {len(data[campo])} partidos en seat_chart")
                        primer_partido = data[campo][0]
                        print(f"   - Estructura: {list(primer_partido.keys())}")
                    elif campo == 'kpis':
                        print(f"   - KPIs: {list(data[campo].keys())}")
                else:
                    print(f"❌ Campo '{campo}': FALTANTE")
                    
        else:
            print(f"❌ Error {response.status_code}: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Test completo del backend electoral")
    print("=" * 60)
    
    # Test 1: Endpoint de partidos
    test_partidos_endpoint()
    
    # Test 2: Formato para frontend
    test_formato_para_frontend()
    
    # Test 3: Request completo
    test_request_real()
    
    print("\n" + "=" * 60)
    print("✅ Tests completados")
    print("💡 Si todo sale bien, tu backend está listo para el frontend")
