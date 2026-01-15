"""
Parámetros globales del sistema de redistritación electoral

PRINCIPIO: Ningún módulo debe hardcodear valores.
Todo se parametriza aquí.
"""

# ==============================================================================
# PARÁMETROS CONSTITUCIONALES (fijos)
# ==============================================================================

TOTAL_CURULES = 400  # Tamaño de la Cámara de Diputados (Art. 52 CPEUM)
UMBRAL_RP = 0.03  # 3% para acceder a RP (Art. 54 CPEUM)
TOPE_SOBRERREPRESENTACION = 0.08  # +8% máximo (Art. 54 CPEUM)
MAX_SEATS_PER_PARTY = 300  # Límite por partido (Art. 54 CPEUM)

# Pisos constitucionales
MIN_DISTRITOS_POR_ESTADO = 2  # Mínimo 2 distritos por entidad

# Criterios de distritación (Art. 53 CPEUM)
DESVIACION_POBLACIONAL_MAX = 0.15  # ±15% respecto a promedio estatal

# ==============================================================================
# ESCENARIOS PARAMÉTRICOS (variables)
# ==============================================================================

# Diccionario de escenarios predefinidos
ESCENARIOS = {
    'baseline': {
        'id': 0,
        'nombre': 'Baseline 300-100',
        'descripcion': 'Configuración actual (2024)',
        'n_mr': 300,
        'n_rp': 100,
        'metodo_mr': 'get_max',  # Ganador por distrito
        'metodo_distritacion': 'oficial',  # Cartografía INE 2017
    },
    'reforma_200_200': {
        'id': 1,
        'nombre': 'Reforma 200-200',
        'descripcion': '200 MR + 200 RP (paridad)',
        'n_mr': 200,
        'n_rp': 200,
        'metodo_mr': 'scale_siglado',  # Muestreo estratificado
        'metodo_distritacion': 'poblacional',  # Rediseño por población
    },
    'reforma_400_0': {
        'id': 2,
        'nombre': 'Solo MR 400-0',
        'descripcion': '400 MR + 0 RP (puro mayoritario)',
        'n_mr': 400,
        'n_rp': 0,
        'metodo_mr': 'get_max',
        'metodo_distritacion': 'poblacional',
    },
    'reforma_200_pm_200': {
        'id': 3,
        'nombre': 'MR 200 + PM 200',
        'descripcion': '200 MR + 200 Primera Minoría',
        'n_mr': 200,
        'n_pm': 200,
        'n_rp': 0,
        'metodo_mr': 'scale_siglado',
        'metodo_distritacion': 'poblacional',
    },
}

# Escenario activo por default
ESCENARIO_DEFAULT = 'baseline'

# ==============================================================================
# PARÁMETROS DE DISTRITACIÓN
# ==============================================================================

# Métodos disponibles de distritación intraestatal
METODOS_DISTRITACION = {
    'oficial': 'Cartografía oficial INE 2017',
    'poblacional': 'Minimizar desviación poblacional',
    'compacidad': 'Maximizar compacidad geométrica',
    'municipal': 'Respetar integridad municipal',
    'mixto': 'Balance entre población, compacidad e integridad municipal',
}

# Pesos para método mixto
PESOS_MIXTO = {
    'poblacion': 0.5,
    'compacidad': 0.3,
    'integridad_municipal': 0.2,
}

# ==============================================================================
# PARÁMETROS DE MÉTODOS MR
# ==============================================================================

# Métodos disponibles para selección de distritos MR
METODOS_MR = {
    'get_max': 'Ganador simple por distrito',
    'scale_siglado': 'Muestreo estratificado PPS',
}

# Parámetros para scale_siglado
SCALE_SIGLADO_PARAMS = {
    'estratificacion': 'entidad',  # Estratificar por estado
    'seed': 42,  # Semilla para reproducibilidad
    'metodo_cuota': 'hare',  # Hare o Droop
}

# ==============================================================================
# PARÁMETROS DE DATOS
# ==============================================================================

# Rutas relativas desde la raíz del proyecto
PATH_POBLACION = 'redistritacion/data/poblacion_estados.csv'
PATH_BASELINE = 'redistritacion/data/baseline_300.csv'
PATH_SECCIONES = 'data/computos_diputados_{anio}.parquet'
PATH_SIGLADO = 'data/siglado-diputados-{anio}.csv'

# Tabla puente (mapeo de escenarios)
PATH_TABLA_PUENTE = 'redistritacion/escenarios/tabla_puente.csv'

# Columnas requeridas en tabla puente
COLUMNAS_TABLA_PUENTE = [
    'id_seccion',
    'entidad',
    'municipio',
    'distrito_baseline',  # Escenario 0 (300 distritos)
    # Columnas adicionales se agregan dinámicamente:
    # distrito_200, distrito_400, etc.
]

# ==============================================================================
# PARÁMETROS DE OUTPUT
# ==============================================================================

# Directorio de salida
PATH_OUTPUT = 'redistritacion/escenarios/'

# Formato de nombres de archivo
FORMATO_ESCENARIO = '{escenario}_MR{n_mr}_RP{n_rp}_{anio}.csv'
FORMATO_SIGLADO = 'siglado_{escenario}_MR{n_mr}_{anio}.csv'

# ==============================================================================
# VALIDACIONES
# ==============================================================================

def validar_escenario(n_mr: int, n_rp: int, n_pm: int = 0) -> bool:
    """
    Valida que los parámetros de un escenario sean constitucionales.
    
    Args:
        n_mr: Número de distritos MR
        n_rp: Número de escaños RP
        n_pm: Número de escaños PM
    
    Returns:
        True si es válido, False si no
    
    Raises:
        ValueError: Si la configuración viola restricciones constitucionales
    """
    total = n_mr + n_rp + n_pm
    
    if total != TOTAL_CURULES:
        raise ValueError(
            f"Total de curules ({total}) debe ser {TOTAL_CURULES}. "
            f"n_mr={n_mr}, n_rp={n_rp}, n_pm={n_pm}"
        )
    
    if n_mr < 0 or n_rp < 0 or n_pm < 0:
        raise ValueError("Número de escaños no puede ser negativo")
    
    # PM y RP son mutuamente excluyentes
    if n_pm > 0 and n_rp > 0:
        raise ValueError("PM y RP son mutuamente excluyentes (uno debe ser 0)")
    
    # Validar pisos mínimos por estado (32 estados × 2 = 64 mínimo)
    if n_mr < 64:
        raise ValueError(
            f"n_mr={n_mr} violaría piso constitucional de 2 distritos por estado "
            f"(mínimo 32 estados × 2 = 64)"
        )
    
    return True


def get_escenario(nombre: str) -> dict:
    """
    Obtiene configuración de un escenario por nombre.
    
    Args:
        nombre: Nombre del escenario ('baseline', 'reforma_200_200', etc.)
    
    Returns:
        Dict con configuración del escenario
    
    Raises:
        KeyError: Si el escenario no existe
    """
    if nombre not in ESCENARIOS:
        raise KeyError(
            f"Escenario '{nombre}' no existe. "
            f"Disponibles: {list(ESCENARIOS.keys())}"
        )
    
    config = ESCENARIOS[nombre].copy()
    
    # Validar antes de retornar
    n_mr = config.get('n_mr', 0)
    n_rp = config.get('n_rp', 0)
    n_pm = config.get('n_pm', 0)
    
    validar_escenario(n_mr, n_rp, n_pm)
    
    return config


def crear_escenario_custom(
    nombre: str,
    n_mr: int,
    n_rp: int = 0,
    n_pm: int = 0,
    metodo_mr: str = 'get_max',
    metodo_distritacion: str = 'poblacional',
    descripcion: str = ''
) -> dict:
    """
    Crea un escenario personalizado con validación.
    
    Args:
        nombre: Nombre identificador del escenario
        n_mr: Número de distritos MR
        n_rp: Número de escaños RP (default 0)
        n_pm: Número de escaños PM (default 0)
        metodo_mr: Método de selección MR
        metodo_distritacion: Método de distritación
        descripcion: Descripción del escenario
    
    Returns:
        Dict con configuración del escenario validado
    """
    # Validar parámetros
    validar_escenario(n_mr, n_rp, n_pm)
    
    if metodo_mr not in METODOS_MR:
        raise ValueError(
            f"metodo_mr '{metodo_mr}' no válido. "
            f"Opciones: {list(METODOS_MR.keys())}"
        )
    
    if metodo_distritacion not in METODOS_DISTRITACION:
        raise ValueError(
            f"metodo_distritacion '{metodo_distritacion}' no válido. "
            f"Opciones: {list(METODOS_DISTRITACION.keys())}"
        )
    
    escenario = {
        'nombre': nombre,
        'descripcion': descripcion,
        'n_mr': n_mr,
        'n_rp': n_rp,
        'n_pm': n_pm,
        'metodo_mr': metodo_mr,
        'metodo_distritacion': metodo_distritacion,
    }
    
    return escenario


# ==============================================================================
# EJEMPLO DE USO
# ==============================================================================

if __name__ == '__main__':
    print("="*80)
    print("CONFIGURACIÓN DEL SISTEMA DE REDISTRITACIÓN")
    print("="*80)
    
    print(f"\nTotal curules: {TOTAL_CURULES}")
    print(f"Umbral RP: {UMBRAL_RP:.0%}")
    print(f"Tope sobrerrepresentación: +{TOPE_SOBRERREPRESENTACION:.0%}")
    
    print(f"\n{'='*80}")
    print("ESCENARIOS DISPONIBLES")
    print(f"{'='*80}")
    
    for key, esc in ESCENARIOS.items():
        print(f"\n{key}:")
        print(f"  Nombre: {esc['nombre']}")
        print(f"  MR: {esc['n_mr']}, RP: {esc['n_rp']}")
        print(f"  Método MR: {esc['metodo_mr']}")
        print(f"  Método distritación: {esc['metodo_distritacion']}")
    
    print(f"\n{'='*80}")
    print("VALIDACIÓN")
    print(f"{'='*80}")
    
    try:
        validar_escenario(200, 200, 0)
        print("✓ Escenario 200-200 VÁLIDO")
    except ValueError as e:
        print(f"✗ Error: {e}")
    
    try:
        validar_escenario(100, 100, 100)
        print("✓ Escenario 100-100-100 VÁLIDO")
    except ValueError as e:
        print(f"✗ Error: {e}")
