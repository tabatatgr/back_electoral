# Sistema de Redistritación Electoral - Estado Actual

## ✅ Componentes implementados

### 1. Estructura de carpetas
```
redistritacion/
├── README.md                    # Documentación completa
├── config.py                    # Parámetros globales (PROBADO ✓)
├── data/                        # Datos de entrada
├── escenarios/                  # Escenarios de redistritación
└── modulos/                     # Módulos funcionales
    ├── __init__.py
    └── reparto_distritos.py     # MÓDULO A (PROBADO ✓)
```

### 2. Configuración global (`config.py`)

**Parámetros constitucionales:**
- Total curules: 400
- Umbral RP: 3%
- Tope sobrerrepresentación: +8%
- Máximo por partido: 300 escaños
- Piso mínimo: 2 distritos por estado

**Escenarios predefinidos:**
1. `baseline`: 300 MR + 100 RP (actual)
2. `reforma_200_200`: 200 MR + 200 RP
3. `reforma_400_0`: 400 MR + 0 RP
4. `reforma_200_pm_200`: 200 MR + 200 PM

**Funcionalidades:**
- Validación automática de escenarios
- Creación de escenarios personalizados
- Verificación de restricciones constitucionales

### 3. MÓDULO A: Reparto de distritos (`reparto_distritos.py`)

**Implementado:**
- Algoritmo Hare con piso constitucional (método oficial INE)
- Validación de restricciones constitucionales
- Generación de reportes detallados

**Resultados probados:**
- **200 distritos**: Min 3, Max 20 (México)
- **300 distritos**: Min 3, Max 34 (México)
- **400 distritos**: Min 4, Max 47 (México)

---

## ⏳ Próximos pasos

### MÓDULO B: Distritación intraestatal (`distritacion.py`)
**Objetivo:** Asignar secciones electorales a distritos dentro de cada estado

**Criterios a implementar:**
1. ±15% desviación poblacional
2. Contigüidad geográfica
3. Integridad municipal (preferente)
4. Comunidades indígenas/afromexicanas
5. Compacidad

**Métodos propuestos:**
- `poblacional`: Minimizar desviación poblacional
- `compacidad`: Maximizar compacidad geométrica
- `municipal`: Respetar límites municipales
- `mixto`: Balance ponderado

**Algoritmo sugerido:**
```python
def distritar_estado(
    secciones: pd.DataFrame,
    n_distritos_estado: int,
    metodo: str = 'poblacional'
) -> Dict[str, int]:
    """
    Asigna secciones a distritos dentro de un estado.
    
    Args:
        secciones: DataFrame con [id_seccion, poblacion, municipio, geometria]
        n_distritos_estado: Número de distritos a crear
        metodo: 'poblacional', 'compacidad', 'municipal', 'mixto'
    
    Returns:
        Dict {id_seccion: distrito_nuevo}
    """
    # 1. Calcular población objetivo por distrito
    poblacion_objetivo = secciones['poblacion'].sum() / n_distritos_estado
    
    # 2. Algoritmo greedy con restricciones
    #    - Empezar con semillas (municipios más poblados o geográficos)
    #    - Agregar secciones vecinas hasta alcanzar población objetivo
    #    - Verificar ±15% desviación
    
    # 3. Refinamiento iterativo
    #    - Intercambiar secciones en frontera para mejorar compacidad
    #    - Respetar límites municipales cuando sea posible
    
    return asignacion_secciones
```

### MÓDULO C: Tabla puente (`tabla_puente.py`)
**Objetivo:** Mantener compatibilidad entre escenarios

**Estructura:**
```csv
id_seccion,entidad,municipio,distrito_baseline,distrito_200,distrito_400
001234,CDMX,Cuauhtémoc,5,3,7
001235,CDMX,Cuauhtémoc,5,3,7
...
```

**Funcionalidades:**
```python
def agregar_escenario(escenario: str, mapping: Dict[str, int])
def obtener_distrito(id_seccion: str, escenario: str) -> int
def comparar_escenarios(escenario_a: str, escenario_b: str) -> pd.DataFrame
```

### MÓDULO D: Cálculo MR (`calcular_mr.py`)
**Objetivo:** Integrar con `engine/procesar_diputados_v2.py` existente

**Flujo:**
1. Leer tabla puente con escenario activo
2. Reagregar votos por sección → distrito_nuevo
3. Aplicar método MR (scale_siglado o get_max)
4. Retornar escaños por partido

### MÓDULO E: Cálculo RP (`calcular_rp.py`)
**Objetivo:** Asignación proporcional (independiente de cartografía)

**Implementar:**
- RP Nacional (Hare sobre votos totales)
- RP Distrital (Hare por distrito con magnitudes variables)

### MÓDULO F: Ensamblaje Cámara (`ensamblar_camara.py`)
**Objetivo:** Composición final con topes constitucionales

**Integrar con:**
- `aplicar_topes_nacionales()` (ya existe en procesar_diputados_v2.py)

---

## 🚀 Script principal (`main.py`)

```python
from redistritacion import config
from redistritacion.modulos import (
    reparto_distritos,
    distritacion,
    tabla_puente,
    calcular_mr,
    calcular_rp,
    ensamblar_camara
)

def generar_escenario(
    n_mr: int,
    n_rp: int,
    anio: int = 2024,
    metodo_distritacion: str = 'poblacional',
    metodo_mr: str = 'scale_siglado',
    aplicar_topes: bool = True,
    seed: int = 42
) -> pd.DataFrame:
    """
    Genera un escenario completo de redistritación.
    
    Returns:
        DataFrame con resultados por partido
    """
    # MÓDULO A: Reparto de distritos por estado
    distritos_por_estado = reparto_distritos.repartir_distritos_hare(
        poblacion_estados=cargar_poblacion(),
        n_distritos=n_mr
    )
    
    # MÓDULO B: Distritación intraestatal
    mapeo_secciones = distritacion.distritar_pais(
        distritos_por_estado=distritos_por_estado,
        metodo=metodo_distritacion
    )
    
    # MÓDULO C: Actualizar tabla puente
    tabla_puente.agregar_escenario(
        escenario=f"mr_{n_mr}",
        mapping=mapeo_secciones
    )
    
    # MÓDULO D: Calcular MR
    escanos_mr = calcular_mr.asignar_mr(
        votos_secciones=cargar_votos(anio),
        mapeo=mapeo_secciones,
        metodo=metodo_mr,
        seed=seed
    )
    
    # MÓDULO E: Calcular RP
    escanos_rp = calcular_rp.asignar_rp(
        votos_nacionales=sumar_votos_nacionales(anio),
        n_rp=n_rp
    )
    
    # MÓDULO F: Ensamblar Cámara
    resultado = ensamblar_camara.componer_camara(
        escanos_mr=escanos_mr,
        escanos_rp=escanos_rp,
        aplicar_topes=aplicar_topes
    )
    
    return resultado
```

---

## 📊 Datos requeridos

### Ya existentes en el proyecto:
- ✅ `data/computos_diputados_2024.parquet` (votos por distrito)
- ✅ `data/siglado-diputados-2024.csv` (ganadores)
- ✅ `engine/procesar_diputados_v2.py` (motor electoral)

### Por agregar:
- ⏳ `redistritacion/data/poblacion_estados.csv` (Censo 2020)
- ⏳ `redistritacion/data/poblacion_secciones.csv` (Lista nominal)
- ⏳ `redistritacion/data/secciones_geometria.shp` (opcional - para compacidad)

---

## 🎯 Resumen

**Estado actual:**
- ✅ Estructura de carpetas creada
- ✅ Configuración global implementada
- ✅ MÓDULO A funcionando y probado
- ⏳ MÓDULOS B-F por implementar

**Ventajas del diseño:**
1. **Modular**: Cada módulo es independiente
2. **Parametrizado**: Sin valores hardcodeados
3. **Compatible**: Se integra con motor existente
4. **Versionado**: Tabla puente preserva todos los escenarios
5. **Validado**: Restricciones constitucionales verificadas

**Siguiente paso inmediato:**
Implementar MÓDULO B (distritación intraestatal) con algoritmo greedy simple que respete ±15% desviación poblacional.

---

## 📝 Respuestas a tus preguntas

> ¿lo estás haciendo en **R** o **Python**?

**Python 3.12** - usando tu stack actual (pandas, numpy, engine existente)

> ¿tienes ya shapefiles por sección?

No necesarios para versión inicial. Algoritmo greedy puede funcionar sin geometría explícita usando proximidad por municipio/distrito actual. Si quieres compacidad geométrica precisa, podemos agregarlo después.

---

**¿Procedo con MÓDULO B?**
