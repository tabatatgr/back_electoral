"""
Test para verificar el slider y botón de primera minoría en el frontend
"""

from engine.procesar_senadores_v2 import procesar_senadores_v2
import json

def test_slider_primera_minoria_frontend():
    """
    Verificar si el slider de primera minoría funciona y cómo se debe implementar en el frontend
    """
    print("🔍 TEST: Verificando slider y botón de primera minoría")
    print("=" * 70)
    
    # Datos base para las pruebas
    base_params = {
        "path_parquet": "data/computos_senado_2018.parquet",
        "anio": 2018,
        "path_siglado": "data/siglado_senado_2018_corregido.csv"
    }
    
    # 1. Test del botón ON/OFF de primera minoría
    print("\n📊 CASO 1: BOTÓN ON/OFF DE PRIMERA MINORÍA")
    print("-" * 50)
    
    print("🔘 Caso 1A: Sistema MR SIN primera minoría (solo MR puro)")
    resultado_mr_puro = procesar_senadores_v2(
        **base_params,
        sistema="mr",
        max_seats=64,
        umbral=0.0
    )
    
    if resultado_mr_puro and 'seat_chart' in resultado_mr_puro:
        escanos_mr_puro = {}
        for item in resultado_mr_puro['seat_chart']:
            escanos_mr_puro[item['party']] = item['seats']
        
        morena_mr = escanos_mr_puro.get('MORENA', 0)
        pan_mr = escanos_mr_puro.get('PAN', 0)
        total_mr = sum(escanos_mr_puro.values())
        
        print(f"   ✅ MR puro (64 escaños): MORENA {morena_mr}, PAN {pan_mr}, Total {total_mr}")
    else:
        print("   ❌ Error en MR puro")
        return
    
    print("\n🔘 Caso 1B: Sistema MIXTO CON primera minoría (MR+PM+RP)")
    resultado_mixto = procesar_senadores_v2(
        **base_params,
        sistema="mixto",
        max_seats=128,
        mr_seats=96,  # Incluye PM automáticamente
        rp_seats=32,
        umbral=0.0
    )
    
    if resultado_mixto and 'seat_chart' in resultado_mixto:
        escanos_mixto = {}
        for item in resultado_mixto['seat_chart']:
            escanos_mixto[item['party']] = item['seats']
        
        morena_mixto = escanos_mixto.get('MORENA', 0)
        pan_mixto = escanos_mixto.get('PAN', 0)
        total_mixto = sum(escanos_mixto.values())
        
        print(f"   ✅ Mixto con PM (128 escaños): MORENA {morena_mixto}, PAN {pan_mixto}, Total {total_mixto}")
    else:
        print("   ❌ Error en sistema mixto")
        return
    
    # Análisis del efecto ON/OFF
    print(f"\n📈 EFECTO DEL BOTÓN ON/OFF:")
    print(f"   • MORENA: {morena_mr} → {morena_mixto} ({morena_mixto - morena_mr:+d} escaños)")
    print(f"   • PAN: {pan_mr} → {pan_mixto} ({pan_mixto - pan_mr:+d} escaños)")
    
    if morena_mixto != morena_mr or pan_mixto != pan_mr:
        print("   ✅ EL BOTÓN ON/OFF SÍ TIENE EFECTO")
    else:
        print("   ❌ EL BOTÓN ON/OFF NO TIENE EFECTO")
    
    # 2. Test del slider de proporción MR/PM/RP
    print("\n📊 CASO 2: SLIDER DE PROPORCIÓN MR/PM/RP")
    print("-" * 50)
    
    configuraciones_slider = [
        {"mr": 64, "pm_incluida": True, "rp": 32, "total": 96, "nombre": "Menos MR+PM"},
        {"mr": 80, "pm_incluida": True, "rp": 48, "total": 128, "nombre": "Balanceado"},
        {"mr": 96, "pm_incluida": True, "rp": 32, "total": 128, "nombre": "Vigente"},
        {"mr": 112, "pm_incluida": True, "rp": 16, "total": 128, "nombre": "Más MR+PM"}
    ]
    
    resultados_slider = []
    
    for config in configuraciones_slider:
        print(f"\n🎚️ {config['nombre']}: {config['mr']} MR+PM + {config['rp']} RP = {config['total']} total")
        
        resultado = procesar_senadores_v2(
            **base_params,
            sistema="mixto",
            max_seats=config['total'],
            mr_seats=config['mr'],
            rp_seats=config['rp'],
            umbral=0.0
        )
        
        if resultado and 'seat_chart' in resultado:
            escanos = {}
            for item in resultado['seat_chart']:
                escanos[item['party']] = item['seats']
            
            morena = escanos.get('MORENA', 0)
            pan = escanos.get('PAN', 0)
            pri = escanos.get('PRI', 0)
            total = sum(escanos.values())
            
            print(f"   ✅ MORENA: {morena}, PAN: {pan}, PRI: {pri}, Total: {total}")
            
            resultados_slider.append({
                'config': config['nombre'],
                'mr_seats': config['mr'],
                'rp_seats': config['rp'],
                'morena': morena,
                'pan': pan,
                'pri': pri,
                'total': total
            })
        else:
            print(f"   ❌ Error en configuración {config['nombre']}")
    
    # Análisis del slider
    if len(resultados_slider) >= 2:
        print(f"\n📈 ANÁLISIS DEL SLIDER:")
        
        morena_values = [r['morena'] for r in resultados_slider]
        pan_values = [r['pan'] for r in resultados_slider]
        
        morena_min, morena_max = min(morena_values), max(morena_values)
        pan_min, pan_max = min(pan_values), max(pan_values)
        
        print(f"   • MORENA varía: {morena_min} - {morena_max} escaños (diferencia: {morena_max - morena_min})")
        print(f"   • PAN varía: {pan_min} - {pan_max} escaños (diferencia: {pan_max - pan_min})")
        
        if morena_max - morena_min > 0 or pan_max - pan_min > 0:
            print("   ✅ EL SLIDER SÍ TIENE EFECTO")
        else:
            print("   ❌ EL SLIDER NO TIENE EFECTO")
    
    # 3. Verificar estructura de API actual
    print("\n📊 CASO 3: VERIFICANDO API ACTUAL")
    print("-" * 40)
    
    verificar_api_senado()
    
    return {
        'boton_efectivo': morena_mixto != morena_mr or pan_mixto != pan_mr,
        'slider_efectivo': len(resultados_slider) >= 2 and (max([r['morena'] for r in resultados_slider]) - min([r['morena'] for r in resultados_slider]) > 0),
        'resultados_slider': resultados_slider
    }

def verificar_api_senado():
    """
    Verificar qué parámetros acepta la API de senado
    """
    try:
        with open("main.py", "r", encoding="utf-8") as f:
            contenido = f.read()
        
        # Buscar la función procesar_senado
        import re
        
        match = re.search(r'async def procesar_senado\((.*?)\):', contenido, re.DOTALL)
        if match:
            parametros = match.group(1)
            print("📋 Parámetros actuales de /procesar/senado:")
            
            lineas = parametros.split('\n')
            for linea in lineas:
                linea = linea.strip()
                if linea and not linea.startswith('"""') and ':' in linea:
                    print(f"   • {linea}")
            
            # Verificar parámetros específicos de primera minoría
            tiene_pm_seats = 'pm_seats' in parametros.lower()
            tiene_sistema = 'sistema' in parametros.lower()
            tiene_mr_seats = 'mr_seats' in parametros.lower()
            tiene_rp_seats = 'rp_seats' in parametros.lower()
            
            print(f"\n📋 Parámetros de primera minoría:")
            print(f"   • pm_seats: {'✅ SÍ' if tiene_pm_seats else '❌ NO'}")
            print(f"   • sistema: {'✅ SÍ' if tiene_sistema else '❌ NO'}")
            print(f"   • mr_seats: {'✅ SÍ' if tiene_mr_seats else '❌ NO'}")
            print(f"   • rp_seats: {'✅ SÍ' if tiene_rp_seats else '❌ NO'}")
            
        else:
            print("❌ No se pudo extraer los parámetros de procesar_senado")
            
    except Exception as e:
        print(f"❌ Error leyendo main.py: {e}")

def generar_codigo_frontend_pm():
    """
    Generar código sugerido para el frontend de primera minoría
    """
    print("\n💻 CÓDIGO SUGERIDO PARA EL FRONTEND - PRIMERA MINORÍA")
    print("=" * 70)
    
    js_code = '''
// 1. COMPONENTE TOGGLE PRIMERA MINORÍA
const TogglePrimeraMinoria = ({ habilitada, onChange, disabled = false }) => {
    return (
        <div className="toggle-primera-minoria">
            <label>
                <input 
                    type="checkbox" 
                    checked={habilitada}
                    onChange={(e) => onChange(e.target.checked)}
                    disabled={disabled}
                />
                <span className="toggle-slider"></span>
                Primera Minoría {habilitada ? 'ACTIVADA' : 'DESACTIVADA'}
            </label>
            <div className="help-text">
                {habilitada 
                    ? "Se asignarán escaños de primera minoría en cada estado"
                    : "Solo se asignarán escaños de mayoría relativa pura"
                }
            </div>
        </div>
    );
};

// 2. SLIDER DE PROPORCIÓN MR/PM vs RP
const SliderProporcionMRRP = ({ 
    mrSeats, 
    rpSeats, 
    totalSeats = 128, 
    onChange,
    primeraMinoriaHabilitada = true 
}) => {
    const handleMRChange = (newMR) => {
        const newRP = totalSeats - newMR;
        onChange({ mr: newMR, rp: newRP });
    };
    
    return (
        <div className="slider-proporcion">
            <h4>Distribución de Escaños</h4>
            
            <div className="slider-container">
                <label>
                    Escaños MR{primeraMinoriaHabilitada ? '+PM' : ''}: {mrSeats}
                </label>
                <input 
                    type="range"
                    min={64}
                    max={totalSeats - 16}  // Mínimo 16 RP
                    step={16}
                    value={mrSeats}
                    onChange={(e) => handleMRChange(parseInt(e.target.value))}
                />
                
                <label>
                    Escaños RP: {rpSeats}
                </label>
                
                <div className="proporcion-visual">
                    <div 
                        className="barra-mr" 
                        style={{ width: `${(mrSeats/totalSeats)*100}%` }}
                    >
                        MR{primeraMinoriaHabilitada ? '+PM' : ''}: {mrSeats}
                    </div>
                    <div 
                        className="barra-rp" 
                        style={{ width: `${(rpSeats/totalSeats)*100}%` }}
                    >
                        RP: {rpSeats}
                    </div>
                </div>
            </div>
            
            <div className="explicacion">
                {primeraMinoriaHabilitada 
                    ? `${mrSeats} escaños se asignan por MR (64) + PM (32) por estado`
                    : `${mrSeats} escaños se asignan por MR pura por estado`
                }
                <br />
                {rpSeats} escaños se asignan por RP nacional
            </div>
        </div>
    );
};

// 3. COMPONENTE INTEGRADO
const ConfiguradorPrimeraMinoria = ({ 
    configuracion, 
    onChange 
}) => {
    const { 
        primeraMinoriaHabilitada = true,
        mrSeats = 96,
        rpSeats = 32,
        sistema = "mixto"
    } = configuracion;
    
    const handleTogglePM = (habilitada) => {
        if (habilitada) {
            // Activar sistema mixto
            onChange({
                ...configuracion,
                primeraMinoriaHabilitada: true,
                sistema: "mixto"
            });
        } else {
            // Cambiar a sistema MR puro
            onChange({
                ...configuracion,
                primeraMinoriaHabilitada: false,
                sistema: "mr",
                rpSeats: 0,
                mrSeats: configuracion.mrSeats + configuracion.rpSeats
            });
        }
    };
    
    const handleProporcionChange = ({ mr, rp }) => {
        onChange({
            ...configuracion,
            mrSeats: mr,
            rpSeats: rp
        });
    };
    
    return (
        <div className="configurador-primera-minoria">
            <TogglePrimeraMinoria 
                habilitada={primeraMinoriaHabilitada}
                onChange={handleTogglePM}
            />
            
            {primeraMinoriaHabilitada && (
                <SliderProporcionMRRP 
                    mrSeats={mrSeats}
                    rpSeats={rpSeats}
                    onChange={handleProporcionChange}
                    primeraMinoriaHabilitada={true}
                />
            )}
            
            {!primeraMinoriaHabilitada && (
                <div className="info-mr-puro">
                    <h4>Sistema MR Puro</h4>
                    <p>Todos los escaños se asignan por mayoría relativa en cada estado.</p>
                    <p>No hay asignación de primera minoría ni representación proporcional.</p>
                </div>
            )}
        </div>
    );
};

// 4. FUNCIÓN PARA ENVIAR A LA API
const enviarConfiguracion = async (configuracion) => {
    const payload = {
        anio: configuracion.anio,
        plan: "personalizado",
        sistema: configuracion.primeraMinoriaHabilitada ? "mixto" : "mr",
        mr_seats: configuracion.mrSeats,
        rp_seats: configuracion.primeraMinoriaHabilitada ? configuracion.rpSeats : 0,
        umbral: 0.0
    };
    
    const response = await fetch('/procesar/senado', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    
    return response.json();
};
'''
    
    print("📄 JAVASCRIPT/REACT:")
    print(js_code)
    
    print("\n📄 CSS SUGERIDO:")
    css_code = '''
.toggle-primera-minoria {
    margin: 20px 0;
    padding: 15px;
    border: 1px solid #ddd;
    border-radius: 8px;
    background: #f9f9f9;
}

.toggle-slider {
    position: relative;
    display: inline-block;
    width: 60px;
    height: 34px;
    background-color: #ccc;
    border-radius: 34px;
    transition: 0.4s;
}

.toggle-slider:before {
    position: absolute;
    content: "";
    height: 26px;
    width: 26px;
    left: 4px;
    bottom: 4px;
    background-color: white;
    border-radius: 50%;
    transition: 0.4s;
}

input:checked + .toggle-slider {
    background-color: #2196F3;
}

input:checked + .toggle-slider:before {
    transform: translateX(26px);
}

.slider-proporcion {
    margin: 20px 0;
    padding: 15px;
    border: 1px solid #ddd;
    border-radius: 8px;
}

.proporcion-visual {
    display: flex;
    height: 30px;
    border-radius: 5px;
    overflow: hidden;
    margin: 10px 0;
}

.barra-mr {
    background: #ff6b6b;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
}

.barra-rp {
    background: #4ecdc4;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
}
'''
    print(css_code)

if __name__ == "__main__":
    resultado = test_slider_primera_minoria_frontend()
    generar_codigo_frontend_pm()
    
    if resultado:
        print(f"\n🎯 RESUMEN EJECUTIVO:")
        print(f"   • Botón ON/OFF primera minoría: {'✅ FUNCIONA' if resultado['boton_efectivo'] else '❌ NO FUNCIONA'}")
        print(f"   • Slider proporción MR/RP: {'✅ FUNCIONA' if resultado['slider_efectivo'] else '❌ NO FUNCIONA'}")
        
        if resultado['boton_efectivo'] and resultado['slider_efectivo']:
            print("   🎉 AMBOS CONTROLES ESTÁN FUNCIONANDO CORRECTAMENTE")
        else:
            print("   ⚠️  ALGUNOS CONTROLES NECESITAN VERIFICACIÓN")
