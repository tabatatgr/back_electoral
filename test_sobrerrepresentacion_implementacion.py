"""
Test directo para verificar si se puede agregar sobrerrepresentación al sistema
"""

from engine.procesar_diputados_v2 import procesar_diputados_v2

def test_sobrerrepresentacion_directo():
    """
    Verificar directamente si el sistema puede manejar sobrerrepresentación
    """
    print("🔍 TEST DIRECTO: Verificando sobrerrepresentación en el sistema")
    print("=" * 70)
    
    # Probar procesamiento directo
    print("\n📊 PROCESAMIENTO DIRECTO SIN SOBRERREPRESENTACIÓN")
    print("-" * 50)
    
    try:
        resultado_sin = procesar_diputados_v2(
            path_parquet="data/computos_diputados_2018.parquet",
            anio=2018,
            path_siglado="data/siglado-diputados-2018.csv",
            partidos_base=None,
            max_seats=500,
            mr_seats=300,
            rp_seats=200,
            umbral=0.03,
            quota_method="hare"
        )
        
        if resultado_sin and 'seat_chart' in resultado_sin:
            print("✅ Procesamiento exitoso")
            
            # Buscar MORENA
            morena_data = None
            for item in resultado_sin['seat_chart']:
                if item.get('party') == 'MORENA':
                    morena_data = item
                    break
            
            if morena_data:
                total_escanos = sum(item['seats'] for item in resultado_sin['seat_chart'])
                total_votos = sum(item['votes'] for item in resultado_sin['seat_chart'])
                
                morena_escanos_pct = (morena_data['seats'] / total_escanos) * 100
                morena_votos_pct = (morena_data['votes'] / total_votos) * 100
                sobrer = morena_escanos_pct - morena_votos_pct
                
                print(f"   MORENA sin límite: {morena_votos_pct:.1f}% votos → {morena_escanos_pct:.1f}% escaños")
                print(f"   Sobrerrepresentación actual: {sobrer:+.1f}%")
                
                return {
                    'morena_escanos_pct': morena_escanos_pct,
                    'morena_votos_pct': morena_votos_pct,
                    'sobrerrepresentacion': sobrer,
                    'total_escanos': total_escanos
                }
        else:
            print("❌ No se obtuvo seat_chart")
            
    except Exception as e:
        print(f"❌ Error en procesamiento: {e}")
        
    return None

def verificar_estructura_api():
    """
    Verificar qué parámetros acepta la API actual
    """
    print("\n📊 CASO 3: ESTRUCTURA DE API ACTUAL")
    print("-" * 40)
    
    # Leer el código de main.py para ver los parámetros
    try:
        with open("main.py", "r", encoding="utf-8") as f:
            contenido = f.read()
        
        # Buscar la función procesar_diputados
        import re
        
        # Extraer parámetros de la función
        match = re.search(r'async def procesar_diputados\((.*?)\):', contenido, re.DOTALL)
        if match:
            parametros = match.group(1)
            print("📋 Parámetros actuales de /procesar/diputados:")
            
            # Limpiar y mostrar parámetros
            lineas = parametros.split('\n')
            for linea in lineas:
                linea = linea.strip()
                if linea and not linea.startswith('"""'):
                    print(f"   • {linea}")
            
            # Verificar si sobrerrepresentacion está incluida
            if 'sobrerrepresentacion' in parametros.lower():
                print("\n✅ 'sobrerrepresentacion' está en los parámetros")
            else:
                print("\n❌ 'sobrerrepresentacion' NO está en los parámetros")
                print("   → Necesita agregarse al endpoint")
        else:
            print("❌ No se pudo extraer los parámetros")
            
    except Exception as e:
        print(f"❌ Error leyendo main.py: {e}")

def generar_codigo_frontend():
    """
    Generar código sugerido para implementar en el frontend
    """
    print("\n💻 CÓDIGO SUGERIDO PARA EL FRONTEND")
    print("=" * 50)
    
    # JavaScript para validación
    js_code = '''
// 1. VALIDACIÓN DE SOBRERREPRESENTACIÓN EN FRONTEND
const validarSobrerrepresentacion = (resultados, limitePorcentaje = 8) => {
    return resultados.map(partido => {
        const sobrerrepresentacion = partido.porcentaje_escanos - partido.porcentaje_votos;
        const dentroDeLimite = sobrerrepresentacion <= limitePorcentaje;
        
        return {
            ...partido,
            sobrerrepresentacion: Math.round(sobrerrepresentacion * 10) / 10, // 1 decimal
            dentroDeLimite,
            alertaColor: dentroDeLimite ? 'green' : 'red'
        };
    });
};

// 2. COMPONENTE REACT PARA MOSTRAR SOBRERREPRESENTACIÓN
const TablaConSobrerrepresentacion = ({ resultados, limite = 8 }) => {
    const resultadosConValidacion = validarSobrerrepresentacion(resultados, limite);
    
    return (
        <table>
            <thead>
                <tr>
                    <th>Partido</th>
                    <th>% Votos</th>
                    <th>% Escaños</th>
                    <th>Sobrerrepresentación</th>
                    <th>Estado</th>
                </tr>
            </thead>
            <tbody>
                {resultadosConValidacion.map(partido => (
                    <tr key={partido.partido}>
                        <td>{partido.partido}</td>
                        <td>{partido.porcentaje_votos.toFixed(1)}%</td>
                        <td>{partido.porcentaje_escanos.toFixed(1)}%</td>
                        <td style={{ color: partido.alertaColor }}>
                            {partido.sobrerrepresentacion > 0 ? '+' : ''}{partido.sobrerrepresentacion}%
                        </td>
                        <td>
                            <span style={{ color: partido.alertaColor }}>
                                {partido.dentroDeLimite ? '✓ Dentro del límite' : '⚠ Excede límite'}
                            </span>
                        </td>
                    </tr>
                ))}
            </tbody>
        </table>
    );
};

// 3. SLIDER PARA CONFIGURAR LÍMITE
const SliderSobrerrepresentacion = ({ valor, onChange }) => {
    return (
        <div>
            <label>Límite de Sobrerrepresentación: {valor}%</label>
            <input 
                type="range" 
                min="0" 
                max="15" 
                step="0.5"
                value={valor}
                onChange={(e) => onChange(parseFloat(e.target.value))}
            />
            <div style={{ fontSize: '0.8em', color: '#666' }}>
                0% = Sin sobrerrepresentación | 8% = Límite típico | 15% = Muy permisivo
            </div>
        </div>
    );
};
'''
    
    print("📄 JAVASCRIPT/REACT:")
    print(js_code)
    
    # Python para backend
    python_code = '''
# CÓDIGO PARA AGREGAR AL BACKEND (main.py)

@app.post("/procesar/diputados")
async def procesar_diputados(
    anio: int,
    plan: str = "vigente",
    escanos_totales: Optional[int] = None,
    sistema: Optional[str] = None,
    umbral: Optional[float] = None,
    mr_seats: Optional[int] = None,
    rp_seats: Optional[int] = None,
    max_seats_per_party: Optional[int] = None,
    quota_method: str = "hare",
    divisor_method: str = "dhondt",
    sobrerrepresentacion: Optional[float] = None  # ← AGREGAR ESTE PARÁMETRO
):
    """
    Agregar en la documentación:
    - **sobrerrepresentacion**: Límite de sobrerrepresentación (0.08 = 8%)
    """
    
    # Dentro de la función, pasar el parámetro:
    resultado = procesar_diputados_v2(
        # ... otros parámetros ...
        overrep_cap=sobrerrepresentacion  # ← PASAR A LA FUNCIÓN
    )
'''
    
    print("\n📄 PYTHON (BACKEND):")
    print(python_code)

if __name__ == "__main__":
    resultado = test_sobrerrepresentacion_directo()
    verificar_estructura_api()
    generar_codigo_frontend()
    
    if resultado:
        print(f"\n🎯 RESUMEN:")
        print(f"   MORENA actual: {resultado['sobrerrepresentacion']:+.1f}% de sobrerrepresentación")
        if resultado['sobrerrepresentacion'] > 8:
            print("   → Necesita aplicar límite de sobrerrepresentación")
        else:
            print("   → Está dentro del límite típico del 8%")
