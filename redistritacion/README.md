# Sistema de Redistritación Electoral

## Objetivo

Modelar cambios en el número de distritos de mayoría relativa (MR) manteniendo la coherencia cartográfica y funcional del simulador electoral.

## Principio de diseño

> "La modificación en el número de distritos de mayoría relativa se modela como un cambio paramétrico que induce una nueva cartografía electoral, manteniendo separada la asignación de la representación proporcional nacional."

## Estructura del sistema

```
redistritacion/
├── README.md                    # Este archivo
├── config.py                    # Parámetros globales del sistema
├── data/                        # Datos de entrada
│   ├── baseline_300.csv         # Escenario 0 (actual)
│   ├── poblacion_estados.csv   # Censo 2020
│   └── secciones_votos.parquet  # Votos por sección
├── escenarios/                  # Escenarios de redistritación
│   ├── escenario_200.csv
│   ├── escenario_400.csv
│   └── tabla_puente.csv         # Mapeo sección → distrito_old → distrito_new
├── modulos/                     # Módulos funcionales
│   ├── __init__.py
│   ├── reparto_distritos.py    # MÓDULO A: Reparto por entidad
│   ├── distritacion.py         # MÓDULO B: Cartografía intraestatal
│   ├── tabla_puente.py         # MÓDULO C: Traducción siglado
│   ├── calcular_mr.py          # MÓDULO D: Asignación MR
│   ├── calcular_rp.py          # MÓDULO E: Asignación RP
│   └── ensamblar_camara.py     # MÓDULO F: Composición final
└── main.py                      # Script principal
```

## Flujo de trabajo

### 0️⃣ Baseline (Escenario 0)
- **Cartografía actual**: 300 distritos
- **Siglado actual**: Resultados oficiales
- **Resultados MR + RP**: Estado actual del sistema

### 1️⃣ Parametrización
```python
N_MR = 200  # o 300, o 400
N_RP = 200  # o 100, o 0
TOTAL_CURULES = N_MR + N_RP  # Siempre 400
```

### 2️⃣ Reparto de distritos por entidad
- **Insumo**: Población estatal (Censo 2020)
- **Restricción**: Mínimo 2 distritos por estado
- **Método**: Algoritmo INE (Hare con piso constitucional)
- **Output**: `distritos_por_estado.csv`

### 3️⃣ Distritación intraestatal
- **Unidad mínima**: Sección electoral
- **Criterios**:
  - ±15% desviación poblacional
  - Contigüidad geográfica
  - Integridad municipal (preferente)
  - Comunidades indígenas/afromexicanas
  - Compacidad
- **Output**: `seccion_distrito_mapping.csv`

### 4️⃣ Tabla puente (clave para compatibilidad)
```csv
id_seccion,entidad,municipio,distrito_baseline,distrito_200,distrito_400,escenario_activo
001234,CDMX,Cuauhtémoc,5,3,7,200
001235,CDMX,Cuauhtémoc,5,3,7,200
...
```
**Nunca eliminar columnas viejas**, solo agregar nuevas.

### 5️⃣ Cálculo MR
1. Reasignar votos: `sección → distrito_new`
2. Sumar votos por partido en cada distrito
3. Aplicar scale_siglado o get.max()
4. Ganador se lleva el escaño

### 6️⃣ Cálculo RP (separada)
- **RP Nacional**: No usa distritos, solo votos nacionales
- **RP Distrital**: Usa magnitudes variables (experimental)
- **Parámetro**: `N_RP`

---

## Errores a evitar

❌ **NO hardcodear 300** en ningún módulo  
❌ **NO reescribir IDs** de distrito sin guardar versión antigua  
❌ **NO mezclar RP con cartografía** (son independientes)  
❌ **NO perder escenarios** (siempre versionar)  

---

## Uso

```python
from redistritacion import main

# Generar escenario con 200 distritos MR
resultado = main.generar_escenario(
    n_mr=200,
    n_rp=200,
    anio=2024,
    metodo_distritacion='poblacional',  # o 'compacidad', 'municipal'
    metodo_mr='scale_siglado',  # o 'get_max'
    aplicar_topes=True,
    seed=42
)

# Exportar resultados
resultado.to_csv('escenarios/resultado_200_200.csv')
```

---

## Tecnología

- **Lenguaje**: Python 3.12
- **Datos**: pandas, numpy, geopandas (opcional)
- **Motor electoral**: engine/procesar_diputados_v2.py (ya existente)

---

## Próximos pasos

1. ✅ Crear estructura de carpetas
2. ⏳ Definir config.py con parámetros
3. ⏳ Implementar MÓDULO A (reparto distritos)
4. ⏳ Implementar MÓDULO B (distritación)
5. ⏳ Implementar MÓDULO C (tabla puente)
6. ⏳ Integrar con motor electoral existente

---

## Referencias

- INE: "Manual de distritación electoral 2017"
- COFIPE/LGIPE: Criterios constitucionales
- Tu simulador actual: `engine/procesar_diputados_v2.py`
