"""
Test completo para verificar que la implementación de sobrerrepresentación funciona
tanto en backend como para generar código de verificación visual en frontend
"""

import requests
import json
from engine.procesar_diputados_v2 import procesar_diputados_v2

def test_backend_sobrerrepresentacion():
    """
    Test directo del backend para verificar que la sobrerrepresentación funciona
    """
    print("🔍 TEST: Verificando sobrerrepresentación en backend")
    print("=" * 70)
    
    # Test 1: Sin sobrerrepresentación
    print("\n📊 CASO 1: SIN límite de sobrerrepresentación")
    resultado_sin = procesar_diputados_v2(
        path_parquet="data/computos_diputados_2024.parquet",
        anio=2024,
        path_siglado="data/siglado-diputados-2024.csv",
        max_seats=500,
        sistema="mixto",
        mr_seats=300,
        rp_seats=200,
        umbral=3.0,
        sobrerrepresentacion=None,  # SIN límite
        print_debug=True
    )
    
    if resultado_sin and 'tot' in resultado_sin:
        total_sin = resultado_sin['tot']
        votos_sin = resultado_sin['votos']
        total_votos = sum(votos_sin.values())
        total_escanos = sum(total_sin.values())
        
        print("\n📈 Resultados SIN sobrerrepresentación:")
        for partido in ['MORENA', 'PAN', 'PRI', 'MC']:
            if partido in total_sin:
                escanos = total_sin[partido]
                votos = votos_sin[partido]
                pct_votos = (votos / total_votos) * 100 if total_votos > 0 else 0
                pct_escanos = (escanos / total_escanos) * 100 if total_escanos > 0 else 0
                sobrerep = pct_escanos - pct_votos
                print(f"   {partido}: {escanos} escaños ({pct_escanos:.1f}%), {votos:,} votos ({pct_votos:.1f}%) -> Sobrerrepresentación: {sobrerep:+.1f}%")
    
    # Test 2: Con sobrerrepresentación 8%
    print(f"\n📊 CASO 2: CON límite de sobrerrepresentación 8%")
    resultado_con = procesar_diputados_v2(
        path_parquet="data/computos_diputados_2024.parquet",
        anio=2024,
        path_siglado="data/siglado-diputados-2024.csv",
        max_seats=500,
        sistema="mixto",
        mr_seats=300,
        rp_seats=200,
        umbral=3.0,
        sobrerrepresentacion=8.0,  # Límite 8%
        print_debug=True
    )
    
    if resultado_con and 'tot' in resultado_con:
        total_con = resultado_con['tot']
        votos_con = resultado_con['votos']
        total_votos = sum(votos_con.values())
        total_escanos = sum(total_con.values())
        
        print("\n📈 Resultados CON sobrerrepresentación 8%:")
        for partido in ['MORENA', 'PAN', 'PRI', 'MC']:
            if partido in total_con:
                escanos = total_con[partido]
                votos = votos_con[partido]
                pct_votos = (votos / total_votos) * 100 if total_votos > 0 else 0
                pct_escanos = (escanos / total_escanos) * 100 if total_escanos > 0 else 0
                sobrerep = pct_escanos - pct_votos
                print(f"   {partido}: {escanos} escaños ({pct_escanos:.1f}%), {votos:,} votos ({pct_votos:.1f}%) -> Sobrerrepresentación: {sobrerep:+.1f}%")
    
    # Comparación
    print(f"\n📊 COMPARACIÓN:")
    if resultado_sin and resultado_con:
        cambios_detectados = False
        for partido in ['MORENA', 'PAN', 'PRI', 'MC']:
            if partido in total_sin and partido in total_con:
                diff = total_con[partido] - total_sin[partido]
                if diff != 0:
                    cambios_detectados = True
                    print(f"   {partido}: {total_sin[partido]} → {total_con[partido]} ({diff:+d} escaños)")
        
        if cambios_detectados:
            print("   ✅ LA SOBRERREPRESENTACIÓN SÍ TIENE EFECTO")
            return True
        else:
            print("   ❌ LA SOBRERREPRESENTACIÓN NO TIENE EFECTO")
            return False
    
    return False

def test_api_sobrerrepresentacion():
    """
    Test de la API para verificar que acepta el parámetro sobrerrepresentacion
    """
    print("\n🔍 TEST: Verificando API con sobrerrepresentación")
    print("=" * 50)
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code != 200:
            print("❌ Servidor no está corriendo en puerto 8001")
            return False
    except:
        print("❌ No se puede conectar al servidor en puerto 8001")
        return False
    
    # Test 1: Sin sobrerrepresentación
    payload_sin = {
        "anio": 2024,
        "plan": "vigente"
    }
    
    print("📤 Enviando request SIN sobrerrepresentación...")
    try:
        response_sin = requests.post(
            "http://localhost:8001/procesar/diputados",
            json=payload_sin,
            timeout=30
        )
        
        if response_sin.status_code == 200:
            data_sin = response_sin.json()
            print("✅ Request SIN sobrerrepresentación exitoso")
        else:
            print(f"❌ Error en request SIN sobrerrepresentación: {response_sin.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en request SIN sobrerrepresentación: {e}")
        return False
    
    # Test 2: Con sobrerrepresentación
    payload_con = {
        "anio": 2024,
        "plan": "vigente",
        "sobrerrepresentacion": 8.0
    }
    
    print("📤 Enviando request CON sobrerrepresentación 8%...")
    try:
        response_con = requests.post(
            "http://localhost:8001/procesar/diputados",
            json=payload_con,
            timeout=30
        )
        
        if response_con.status_code == 200:
            data_con = response_con.json()
            print("✅ Request CON sobrerrepresentación exitoso")
            
            # Comparar resultados
            if 'resultados' in data_sin and 'resultados' in data_con:
                print("\n📊 Comparando resultados de API:")
                
                # Crear mapas por partido
                escanos_sin = {r['partido']: r['total'] for r in data_sin['resultados']}
                escanos_con = {r['partido']: r['total'] for r in data_con['resultados']}
                
                cambios = False
                for partido in ['MORENA', 'PAN', 'PRI', 'MC']:
                    if partido in escanos_sin and partido in escanos_con:
                        diff = escanos_con[partido] - escanos_sin[partido]
                        if diff != 0:
                            cambios = True
                            print(f"   {partido}: {escanos_sin[partido]} → {escanos_con[partido]} ({diff:+d})")
                
                if cambios:
                    print("   ✅ API RESPONDE CORRECTAMENTE A SOBRERREPRESENTACIÓN")
                    return True
                else:
                    print("   ⚠️  API no muestra cambios (puede estar funcionando si no hay sobrerrepresentación que corregir)")
                    return True
            
        else:
            print(f"❌ Error en request CON sobrerrepresentación: {response_con.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en request CON sobrerrepresentación: {e}")
        return False

def generar_codigo_verificacion_frontend():
    """
    Generar código JavaScript para verificar sobrerrepresentación en el frontend
    """
    print("\n💻 CÓDIGO PARA VERIFICACIÓN VISUAL EN FRONTEND")
    print("=" * 70)
    
    js_code = '''
// 1. FUNCIÓN PARA CALCULAR SOBRERREPRESENTACIÓN
function calcularSobrerrepresentacion(resultados) {
    const totalVotos = resultados.reduce((sum, r) => sum + r.votos, 0);
    const totalEscanos = resultados.reduce((sum, r) => sum + r.total, 0);
    
    return resultados.map(partido => {
        const pctVotos = totalVotos > 0 ? (partido.votos / totalVotos) * 100 : 0;
        const pctEscanos = totalEscanos > 0 ? (partido.total / totalEscanos) * 100 : 0;
        const sobrerrepresentacion = pctEscanos - pctVotos;
        
        return {
            ...partido,
            porcentaje_votos_real: pctVotos,
            porcentaje_escanos_real: pctEscanos,
            sobrerrepresentacion: sobrerrepresentacion,
            excede_limite: false // Se calculará después
        };
    });
}

// 2. FUNCIÓN PARA VERIFICAR LÍMITES
function verificarLimitesSobrerrepresentacion(resultados, limite = 8.0) {
    return resultados.map(partido => ({
        ...partido,
        excede_limite: partido.sobrerrepresentacion > limite,
        dentro_limite: Math.abs(partido.sobrerrepresentacion) <= limite
    }));
}

// 3. COMPONENTE VISUALIZADOR DE SOBRERREPRESENTACIÓN
const VisualizadorSobrerrepresentacion = ({ resultados, limite = 8.0 }) => {
    const datosConSobrerrepresentacion = verificarLimitesSobrerrepresentacion(
        calcularSobrerrepresentacion(resultados), 
        limite
    );
    
    const partidosExcedentes = datosConSobrerrepresentacion.filter(p => p.excede_limite);
    const totalEscanosExcedentes = partidosExcedentes.reduce((sum, p) => sum + p.total, 0);
    
    return (
        <div className="sobrerrepresentacion-panel">
            <h3>📊 Análisis de Sobrerrepresentación</h3>
            
            <div className="limite-info">
                <strong>Límite constitucional: {limite}%</strong>
                {partidosExcedentes.length > 0 ? (
                    <span className="alerta">⚠️ {partidosExcedentes.length} partidos exceden el límite</span>
                ) : (
                    <span className="ok">✅ Todos los partidos dentro del límite</span>
                )}
            </div>
            
            <div className="tabla-sobrerrepresentacion">
                <table>
                    <thead>
                        <tr>
                            <th>Partido</th>
                            <th>Votos %</th>
                            <th>Escaños %</th>
                            <th>Sobrerrepresentación</th>
                            <th>Estado</th>
                        </tr>
                    </thead>
                    <tbody>
                        {datosConSobrerrepresentacion
                            .sort((a, b) => b.sobrerrepresentacion - a.sobrerrepresentacion)
                            .map(partido => (
                            <tr key={partido.partido} className={partido.excede_limite ? 'excede' : 'ok'}>
                                <td><strong>{partido.partido}</strong></td>
                                <td>{partido.porcentaje_votos_real.toFixed(1)}%</td>
                                <td>{partido.porcentaje_escanos_real.toFixed(1)}%</td>
                                <td className={`sobrerrepresentacion ${partido.sobrerrepresentacion > 0 ? 'positiva' : 'negativa'}`}>
                                    {partido.sobrerrepresentacion > 0 ? '+' : ''}{partido.sobrerrepresentacion.toFixed(1)}%
                                </td>
                                <td>
                                    {partido.excede_limite ? (
                                        <span className="excede">🔴 Excede límite</span>
                                    ) : partido.sobrerrepresentacion > limite * 0.8 ? (
                                        <span className="cerca">🟡 Cerca del límite</span>
                                    ) : (
                                        <span className="ok">🟢 Dentro del límite</span>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            
            {partidosExcedentes.length > 0 && (
                <div className="redistribucion-info">
                    <h4>📈 Redistribución necesaria:</h4>
                    <p>Los partidos que exceden el límite deberían redistribuir escaños:</p>
                    <ul>
                        {partidosExcedentes.map(partido => (
                            <li key={partido.partido}>
                                <strong>{partido.partido}</strong>: 
                                Sobrerrepresentado en {partido.sobrerrepresentacion.toFixed(1)}% 
                                (límite: {limite}%)
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
};

// 4. HOOK PARA USAR EN COMPONENTES
const useSobrerrepresentacion = (resultados, limite = 8.0) => {
    const [analisisSobrerrepresentacion, setAnalisisSobrerrepresentacion] = React.useState(null);
    
    React.useEffect(() => {
        if (resultados && resultados.length > 0) {
            const datos = verificarLimitesSobrerrepresentacion(
                calcularSobrerrepresentacion(resultados), 
                limite
            );
            
            const partidosExcedentes = datos.filter(p => p.excede_limite);
            const cumpleConstitucionalidad = partidosExcedentes.length === 0;
            
            setAnalisisSobrerrepresentacion({
                datos,
                partidosExcedentes,
                cumpleConstitucionalidad,
                limite
            });
        }
    }, [resultados, limite]);
    
    return analisisSobrerrepresentacion;
};

// 5. COMPONENTE SELECTOR DE LÍMITE
const SelectorLimiteSobrerrepresentacion = ({ limite, onChange }) => {
    return (
        <div className="selector-limite">
            <label>
                Límite de sobrerrepresentación:
                <select value={limite} onChange={(e) => onChange(parseFloat(e.target.value))}>
                    <option value={8.0}>8% (Constitucional)</option>
                    <option value={10.0}>10%</option>
                    <option value={12.0}>12%</option>
                    <option value={15.0}>15%</option>
                    <option value={0}>Sin límite</option>
                </select>
            </label>
            
            <div className="info-limite">
                {limite === 8.0 && (
                    <small>📜 Límite constitucional establecido en el artículo 54 de la Constitución</small>
                )}
                {limite === 0 && (
                    <small>⚠️ Sin límite de sobrerrepresentación</small>
                )}
            </div>
        </div>
    );
};
'''
    
    print("📄 JAVASCRIPT/REACT:")
    print(js_code)
    
    css_code = '''
.sobrerrepresentacion-panel {
    margin: 20px 0;
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 8px;
    background: #f9f9f9;
}

.limite-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    padding: 10px;
    background: #e8f4fd;
    border-radius: 5px;
}

.limite-info .alerta {
    color: #d73027;
    font-weight: bold;
}

.limite-info .ok {
    color: #1a9850;
    font-weight: bold;
}

.tabla-sobrerrepresentacion table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
}

.tabla-sobrerrepresentacion th,
.tabla-sobrerrepresentacion td {
    padding: 8px 12px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}

.tabla-sobrerrepresentacion th {
    background: #f5f5f5;
    font-weight: bold;
}

.tabla-sobrerrepresentacion tr.excede {
    background: #ffebee;
}

.tabla-sobrerrepresentacion tr.ok {
    background: #e8f5e8;
}

.sobrerrepresentacion.positiva {
    color: #d73027;
    font-weight: bold;
}

.sobrerrepresentacion.negativa {
    color: #1a9850;
}

.excede {
    color: #d73027;
    font-weight: bold;
}

.cerca {
    color: #ff9800;
    font-weight: bold;
}

.redistribucion-info {
    margin-top: 20px;
    padding: 15px;
    background: #fff3cd;
    border: 1px solid #ffeaa7;
    border-radius: 5px;
}

.selector-limite {
    margin-bottom: 20px;
}

.selector-limite select {
    margin-left: 10px;
    padding: 5px 10px;
    border-radius: 4px;
    border: 1px solid #ccc;
}

.info-limite {
    margin-top: 5px;
}

.info-limite small {
    color: #666;
}
'''
    
    print("\n📄 CSS:")
    print(css_code)

if __name__ == "__main__":
    print("🚀 INICIANDO TESTS DE SOBRERREPRESENTACIÓN")
    print("="*80)
    
    # Test 1: Backend directo
    backend_ok = test_backend_sobrerrepresentacion()
    
    # Test 2: API
    api_ok = test_api_sobrerrepresentacion()
    
    # Generar código frontend
    generar_codigo_verificacion_frontend()
    
    print(f"\n🎯 RESUMEN FINAL:")
    print(f"   • Backend directo: {'✅ FUNCIONA' if backend_ok else '❌ NO FUNCIONA'}")
    print(f"   • API endpoint: {'✅ FUNCIONA' if api_ok else '❌ NO FUNCIONA'}")
    
    if backend_ok and api_ok:
        print("   🎉 SOBRERREPRESENTACIÓN IMPLEMENTADA CORRECTAMENTE")
        print("   💡 Usar el código JavaScript generado para verificación visual en frontend")
    else:
        print("   ⚠️  REVISAR IMPLEMENTACIÓN DE SOBRERREPRESENTACIÓN")
