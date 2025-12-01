# METODOLOGÍA: Generación de Escenarios Electorales MORENA 2018-2024

## 📋 ÍNDICE
1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Metodología de Asignación de Diputados](#metodología-de-asignación-de-diputados)
3. [Cálculo del Swing Electoral 2021-2024](#cálculo-del-swing-electoral-2021-2024)
4. [Generación de Escenarios Contrafactuales](#generación-de-escenarios-contrafactuales)
5. [Archivos Generados](#archivos-generados)

---

## 1. RESUMEN EJECUTIVO

Este proyecto analiza escenarios electorales para la Cámara de Diputados mexicana bajo diferentes configuraciones institucionales, considerando:

- **3 años electorales**: 2018, 2021, 2024
- **3 tamaños de cámara**: 400, 500, 600 escaños
- **3 configuraciones MR/RP**: 50/50, 60/40, 75/25
- **2 modos de coalición**: CON y SIN coaliciones
- **2 regímenes de topes**: CON y SIN topes constitucionales
- **1 escenario adicional**: 2021_SWING (con ajuste por swing estatal)

**Total**: 72 escenarios por archivo (54 base + 18 con swing)

---

## 2. METODOLOGÍA DE ASIGNACIÓN DE DIPUTADOS

### 2.1 Sistema Electoral Mexicano

El sistema electoral mexicano para diputados es **mixto**:
- **Mayoría Relativa (MR)**: Diputados electos directamente en distritos uninominales
- **Representación Proporcional (RP)**: Diputados asignados por listas nacionales según proporción de votos

### 2.2 Algoritmo de Asignación (`asignadip_v2`)

**Ubicación**: `engine/asignadip_v2.py`

#### Paso 1: Asignación MR (Mayoría Relativa)
```
Para cada uno de los N distritos:
    1. Identificar partido ganador (más votos)
    2. Asignar 1 escaño MR al partido ganador
    3. Registrar votos del partido ganador como "no elegibles para RP"
```

#### Paso 2: Cálculo de Votos Elegibles para RP
```
Para cada partido:
    votos_rp = votos_totales_nacional - votos_en_distritos_ganados
```
**Lógica**: Solo los votos donde el partido NO ganó cuentan para RP.

#### Paso 3: Filtro de Umbral (3% nacional)
```
Para cada partido:
    Si (votos_totales / suma_votos_todos) < 0.03:
        partido_eliminado = True
```

#### Paso 4: Asignación RP (Método Huntington-Hill)
```
1. Calcular cocientes para cada partido:
   Q_i = votos_rp_i / sqrt(s_i * (s_i + 1))
   donde s_i = escaños ya asignados

2. Repetir hasta llenar escaños RP disponibles:
   - Identificar partido con mayor Q_i
   - Asignar 1 escaño RP
   - Actualizar s_i y recalcular Q_i
```

#### Paso 5: Aplicación de Topes Constitucionales (opcional)

**Tope 1: Sobrerrepresentación del 8%**
```
Para cada partido:
    proporcion_votos = votos_partido / votos_totales
    proporcion_escaños = escaños_partido / escaños_totales
    
    Si (proporcion_escaños - proporcion_votos) > 0.08:
        escaños_max = floor((proporcion_votos + 0.08) * escaños_totales)
        
        Si escaños_partido > escaños_max:
            escaños_recortados = escaños_partido - escaños_max
            Redistribuir escaños_recortados a otros partidos
```

**Tope 2: Máximo 300 escaños por partido** (solo para cámara de 500)
```
Si escaños_totales == 500:
    Para cada partido:
        Si escaños_partido > 300:
            escaños_recortados = escaños_partido - 300
            Redistribuir escaños_recortados a otros partidos
```

### 2.3 Manejo de Coaliciones

Cuando `usar_coaliciones=True`:
```
1. Votos se suman a nivel de coalición durante asignación
2. Escaños se distribuyen entre partidos de la coalición proporcionalmente
3. Coaliciones definidas por año:
   - 2018: JHH (MORENA + PT + PES)
   - 2021: JHH (MORENA + PT + PVEM)
   - 2024: SSP (MORENA + PT + PVEM)
```

---

## 3. CÁLCULO DEL SWING ELECTORAL 2021-2024

### 3.1 Concepto

**Swing electoral** = Cambio en el comportamiento del votante entre dos elecciones.

En México, **8 estados** tuvieron elecciones locales concurrentes en 2021 Y 2024:
- Aguascalientes
- Coahuila
- Durango
- Hidalgo
- México
- Oaxaca
- Quintana Roo
- Tamaulipas

El swing captura el cambio de preferencia electoral en estos estados entre ambas elecciones.

### 3.2 Fuentes de Datos

**Script**: `calcular_swing.py`

**Datos de entrada**:
1. `outputs/swing/tabla_equivalencia_seccion_df.csv` - Mapeo de secciones a distritos federales
2. Computos de elecciones locales 2021 y 2024 (por estado)

### 3.3 Algoritmo de Cálculo

#### Paso 1: Cargar Equivalencias Sección-Distrito
```python
# Mapeo de secciones electorales a distritos federales (DF)
# Solo para los 8 estados con elecciones concurrentes
equivalencias = pd.read_csv('tabla_equivalencia_seccion_df.csv')
```

#### Paso 2: Agregar Votos por Distrito Federal
```python
Para cada año (2021, 2024):
    Para cada estado en [8 estados]:
        # Leer computos locales
        votos_local = leer_computos_local(estado, año)
        
        # Agregar a nivel DF usando tabla de equivalencias
        votos_df = votos_local.merge(equivalencias, on='SECCION')
        votos_df = votos_df.groupby(['ENTIDAD', 'DF']).sum()
```

#### Paso 3: Calcular Swing por Partido
```python
Para cada (estado, distrito) en 8 estados:
    Para cada partido:
        votos_2021 = votos[estado][distrito][partido][2021]
        votos_2024 = votos[estado][distrito][partido][2024]
        
        Si votos_2021 > 0:
            swing_pct = ((votos_2024 - votos_2021) / votos_2021) * 100
        Sino:
            swing_pct = None  # No se puede calcular
```

#### Paso 4: Swing por Coalición
```python
# Calcular swing para coaliciones completas
coaliciones = {
    'VA_X_MEX': ['PAN', 'PRI', 'PRD'],
    'JUNTOS': ['PT', 'MORENA']
}

Para cada coalición:
    votos_coal_2021 = sum(votos[partido][2021] for partido in coalicion)
    votos_coal_2024 = sum(votos[partido][2024] for partido in coalicion)
    
    swing_coalicion = ((votos_coal_2024 - votos_coal_2021) / votos_coal_2021) * 100
```

#### Paso 5: Guardar Resultados
```python
# Archivo: outputs/swing/swing_con_coaliciones_YYYYMMDD_HHMMSS.csv
Columnas:
    - ENTIDAD (código)
    - NOMBRE_ESTADO
    - DF_2021 (distrito federal)
    - swing_PAN, swing_PRI, swing_PRD, swing_PVEM, swing_PT, swing_MC, swing_MORENA
    - swing_VA_X_MEX_PAN_PRI_PRD (coalición opositora)
    - swing_JUNTOS_PT_MORENA (coalición MORENA)
```

**Total registros**: 83 distritos en 8 estados

### 3.4 Aplicación del Swing a 2021

**Script**: `usar_swing.py` (clase `SwingElectoral`)

**Método**: `ajustar_votos(votos_2021, entidad, distrito, usar_coaliciones)`

```python
def ajustar_votos(votos_2021, entidad, distrito, usar_coaliciones):
    """
    Ajusta votos de 2021 aplicando swing 2021-2024
    
    Returns:
        dict con votos ajustados
    """
    # Obtener swing para este distrito
    swing_info = obtener_swing(entidad, distrito)
    
    Si swing_info es None:  # Estado sin elecciones locales
        return votos_2021.copy()  # Sin cambio
    
    votos_ajustados = {}
    
    # Partidos individuales (PAN, PRI, PRD) - 100% confianza
    Para partido in ['PAN', 'PRI', 'PRD']:
        swing_pct = swing_info['partidos'][partido]
        votos_ajustados[partido] = votos_2021[partido] * (1 + swing_pct/100)
    
    # PT + MORENA: usar swing de coalición si está disponible
    Si usar_coaliciones y swing_coalicion_disponible:
        swing_juntos = swing_info['coaliciones']['JUNTOS']
        votos_coalicion = votos_2021['PT'] + votos_2021['MORENA']
        votos_coalicion_ajustados = votos_coalicion * (1 + swing_juntos/100)
        
        # Distribuir proporcionalmente
        prop_pt = votos_2021['PT'] / votos_coalicion
        votos_ajustados['PT'] = votos_coalicion_ajustados * prop_pt
        votos_ajustados['MORENA'] = votos_coalicion_ajustados * (1 - prop_pt)
    Sino:
        # Swing individual con factor de confianza (70%)
        Para partido in ['PT', 'MORENA']:
            swing_pct = swing_info['partidos'][partido] * 0.7
            votos_ajustados[partido] = votos_2021[partido] * (1 + swing_pct/100)
    
    return votos_ajustados
```

**Cobertura**:
- **83 distritos** (de 300 totales) reciben ajuste de swing
- **217 distritos** mantienen votos 2021 originales

---

## 4. GENERACIÓN DE ESCENARIOS CONTRAFACTUALES

### 4.1 Escenarios Base (2018, 2021, 2024)

**Scripts**:
- `tmp_generate_escenarios_con_topes.py` (CON topes constitucionales)
- `tmp_generate_escenarios_sin_topes.py` (SIN topes constitucionales)

#### Configuración de Escenarios

```python
AÑOS = [2018, 2021, 2024]
TAMAÑOS_CAMARA = [400, 500, 600]  # escaños totales
CONFIGURACIONES_MR_RP = [
    (50, 50),  # 50% MR, 50% RP
    (60, 40),  # 60% MR, 40% RP
    (75, 25)   # 75% MR, 25% RP
]
MODOS_COALICION = ['CON', 'SIN']
```

#### Proceso de Generación

```python
Para cada año in [2018, 2021, 2024]:
    # Cargar votos reales
    votos = pd.read_parquet(f'data/computos_diputados_{año}.parquet')
    
    Para cada tamaño_camara in [400, 500, 600]:
        Para cada (pct_mr, pct_rp) in [(50,50), (60,40), (75,25)]:
            escanos_mr = int(tamaño_camara * pct_mr / 100)
            escanos_rp = int(tamaño_camara * pct_rp / 100)
            
            Para cada usar_coaliciones in [True, False]:
                # Ejecutar asignación
                resultado = procesar_diputados_v2(
                    path_parquet=votos,
                    path_siglado=f'data/siglado-diputados-{año}.csv',
                    anio=año,
                    max_seats=tamaño_camara,
                    mr_seats=escanos_mr,
                    rp_seats=escanos_rp,
                    usar_coaliciones=usar_coaliciones,
                    aplicar_topes=True/False  # según script
                )
                
                # Extraer resultados MORENA
                morena_mr = resultado['mr']['MORENA']
                morena_rp = resultado['rp']['MORENA']
                morena_total = resultado['tot']['MORENA']
                
                # Calcular mayorías
                mayoria_simple_morena = morena_total > (tamaño_camara / 2)
                mayoria_calificada_morena = morena_total >= ceil(tamaño_camara * 2/3)
                
                # Calcular coalición
                coal_partidos = ['MORENA', 'PT', 'PVEM']  # según año
                coalicion_total = sum(resultado['tot'][p] for p in coal_partidos)
                
                mayoria_simple_coalicion = coalicion_total > (tamaño_camara / 2)
                mayoria_calificada_coalicion = coalicion_total >= ceil(tamaño_camara * 2/3)
                
                # Guardar escenario
                guardar_resultado(...)
```

### 4.2 Escenarios con Swing (2021_SWING)

**Objetivo**: Simular qué habría pasado en 2021 si el electorado hubiera votado como en 2024.

#### Proceso

```python
# 1. Cargar votos 2021 originales
votos_2021 = pd.read_parquet('data/computos_diputados_2021.parquet')

# 2. Cargar swing electoral
swing = SwingElectoral()  # Lee outputs/swing/swing_con_coaliciones_*.csv

# 3. Aplicar swing distrito por distrito
ESTADOS_CON_SWING = {
    'AGUASCALIENTES': '01', 'COAHUILA': '05', 'DURANGO': '10',
    'HIDALGO': '13', 'MÉXICO': '15', 'OAXACA': '20',
    'QUINTANA ROO': '23', 'TAMAULIPAS': '28'
}

votos_ajustados = votos_2021.copy()
distritos_ajustados = 0

Para cada distrito in votos_2021:
    entidad_nombre = distrito['ENTIDAD']
    distrito_num = distrito['DISTRITO']
    
    # Convertir nombre a código
    entidad_codigo = ESTADOS_CON_SWING.get(entidad_nombre)
    
    Si entidad_codigo is None:
        # Estado sin swing - mantener votos originales
        continue
    
    # Construir dict de votos 2021
    votos_distrito_2021 = {
        'PAN': distrito['PAN'],
        'PRI': distrito['PRI'],
        'PRD': distrito['PRD'],
        'PVEM': distrito['PVEM'],
        'PT': distrito['PT'],
        'MC': distrito['MC'],
        'MORENA': distrito['MORENA']
    }
    
    # Aplicar swing
    votos_distrito_ajustados = swing.ajustar_votos(
        votos_2021=votos_distrito_2021,
        entidad=entidad_codigo,
        distrito=distrito_num,
        usar_coaliciones=usar_coaliciones
    )
    
    # Actualizar DataFrame
    Si votos cambiaron:
        Para cada partido:
            votos_ajustados.at[idx, partido] = votos_distrito_ajustados[partido]
        
        distritos_ajustados += 1

# 4. Guardar temporalmente
votos_ajustados.to_parquet('data/temp_2021_con_swing.parquet')

# 5. Procesar como año normal
resultado = procesar_diputados_v2(
    path_parquet='data/temp_2021_con_swing.parquet',
    ...
)

# 6. Limpiar
os.remove('data/temp_2021_con_swing.parquet')
```

**Resultado**: 18 escenarios adicionales etiquetados como `anio='2021_SWING'`

### 4.3 Diferencia entre Topes y Sin Topes

| Aspecto | CON Topes | SIN Topes |
|---------|-----------|-----------|
| **Sobrerrepresentación 8%** | ✅ Aplicado | ❌ No aplicado |
| **Máximo 300 escaños** | ✅ Aplicado | ❌ No aplicado |
| **Redistribución** | Escaños recortados → otros partidos | No hay redistribución |
| **Resultado** | Refleja ley electoral vigente | Distribución "pura" proporcional |

**Ejemplo (2024, 500 escaños, 50MR/50RP, CON coalición)**:
- CON TOPES: MORENA = 252 escaños (50.4%) — capado por 8%
- SIN TOPES: MORENA = 310 escaños (62.0%) — distribución proporcional pura

---

## 5. ARCHIVOS GENERADOS

### 5.1 Archivos de Salida

#### CSV de Escenarios CON TOPES
**Archivo**: `outputs/escenarios_morena_CON_TOPES_YYYYMMDD_HHMMSS.csv`

**Columnas**:
```
anio                           - Año electoral (2018, 2021, 2024, 2021_SWING)
total_escanos                  - Tamaño de cámara (400, 500, 600)
configuracion                  - Configuración MR/RP (50MR_50RP, 60MR_40RP, 75MR_25RP)
pct_mr                         - Porcentaje MR (50, 60, 75)
pct_rp                         - Porcentaje RP (50, 40, 25)
mr_seats                       - Número de escaños MR
rp_seats                       - Número de escaños RP
usar_coaliciones               - Modo coalición (CON, SIN)
morena_votos_pct               - % votos MORENA
morena_mr                      - Escaños MR MORENA
morena_rp                      - Escaños RP MORENA
morena_total                   - Total escaños MORENA
morena_pct_escanos             - % escaños MORENA
coalicion_total                - Total escaños coalición
coalicion_pct_escanos          - % escaños coalición
mayoria_simple_morena          - MORENA > 50% (True/False)
mayoria_calificada_morena      - MORENA >= 2/3 (True/False)
mayoria_simple_coalicion       - Coalición > 50% (True/False)
mayoria_calificada_coalicion   - Coalición >= 2/3 (True/False)
topes_aplicados                - SI
```

**Filas**: 72 escenarios

#### CSV de Escenarios SIN TOPES
**Archivo**: `outputs/escenarios_morena_SIN_TOPES_YYYYMMDD_HHMMSS.csv`

**Columnas** (similares pero con nombres ligeramente diferentes):
```
anio
escanos_totales                - (equivalente a total_escanos)
config_mr_rp                   - (equivalente a configuracion)
coalicion                      - (equivalente a usar_coaliciones)
morena_mr
morena_rp
morena_total
morena_pct
coalicion_total
coalicion_pct
mayoria_simple_morena
mayoria_calificada_morena
mayoria_simple_coalicion
mayoria_calificada_coalicion
```

**Filas**: 72 escenarios

### 5.2 Archivo de Swing
**Archivo**: `outputs/swing/swing_con_coaliciones_YYYYMMDD_HHMMSS.csv`

**Columnas**:
```
NOMBRE_ESTADO                  - Nombre del estado
ENTIDAD                        - Código de entidad (1, 5, 10, 13, 15, 20, 23, 28)
DF_2021                        - Distrito federal
AÑO_ELECCION                   - Año de elección local
swing_PAN                      - Swing % PAN
swing_PRI                      - Swing % PRI
swing_PRD                      - Swing % PRD
swing_PVEM                     - Swing % PVEM
swing_PT                       - Swing % PT
swing_MC                       - Swing % MC
swing_MORENA                   - Swing % MORENA
swing_VA_X_MEX_PAN_PRI_PRD     - Swing % coalición opositora
swing_JUNTOS_PT_MORENA         - Swing % coalición MORENA
```

**Filas**: 83 distritos en 8 estados

---

## 6. VALIDACIONES Y VERIFICACIONES

### 6.1 Verificación de Consistencia

**Regla fundamental**: `MR + RP = TOTAL`

```python
Para cada escenario:
    assert morena_mr + morena_rp == morena_total
```

### 6.2 Verificación de Topes (CON TOPES)

**Tope 8%**:
```python
Para escenarios CON TOPES:
    proporcion_votos = morena_votos_pct / 100
    proporcion_escanos = morena_total / total_escanos
    sobrerrepresentacion = proporcion_escanos - proporcion_votos
    
    assert sobrerrepresentacion <= 0.08 + tolerancia
```

**Tope 300**:
```python
Para escenarios CON TOPES con 500 escaños:
    assert morena_total <= 300
```

### 6.3 Verificación de Swing

**Diferencias esperadas entre 2021 y 2021_SWING**:
```python
# Solo 83 de 300 distritos tienen swing
# Esperamos cambios pequeños (~0.3-0.4% en votos agregados)

df_2021 = escenarios[escenarios['anio'] == '2021']
df_2021_swing = escenarios[escenarios['anio'] == '2021_SWING']

Para cada configuración:
    votos_2021 = df_2021[configuracion]['morena_votos_pct']
    votos_swing = df_2021_swing[configuracion]['morena_votos_pct']
    
    diff = abs(votos_swing - votos_2021)
    assert 0.1 <= diff <= 1.0  # Cambio esperado entre 0.1% y 1.0%
```

### 6.4 Verificación CON vs SIN Topes

**Regla**: SIN TOPES >= CON TOPES (siempre)

```python
Para cada configuración:
    escanos_con_topes = df_con[configuracion]['morena_total']
    escanos_sin_topes = df_sin[configuracion]['morena_total']
    
    assert escanos_sin_topes >= escanos_con_topes
```

---

## 7. LIMITACIONES Y SUPUESTOS

### 7.1 Supuestos

1. **Coaliciones constantes**: Se asume que las coaliciones se mantienen iguales en todos los tamaños de cámara
2. **Distribución distrital**: Se asume que la distribución de votos MR escala proporcionalmente
3. **Swing lineal**: Se asume que el swing observado 2021-2024 es aplicable de forma lineal
4. **Factor de confianza**: Se usa 70% de confianza para partidos pequeños con pocos datos en swing

### 7.2 Limitaciones

1. **Tamaños no históricos**: 400 y 600 escaños son contrafactuales (México solo ha tenido 500)
2. **Configuraciones MR/RP**: 50/50 y 60/40 nunca han existido (México usa 60% MR / 40% RP)
3. **Swing parcial**: Solo 8 estados tienen swing, resto usa votos 2021 sin ajustar
4. **Sin redistritación**: Se asume que los distritos MR se mantienen constantes

### 7.3 Datos Faltantes

**Swing estatal faltante**:
- Tamaulipas DF-9
- México DF-41

Estos distritos no tienen datos de swing por falta de equivalencia sección-DF o problemas en datos fuente.

---

## 8. CONTACTO Y SOPORTE

**Repositorio**: `back_electoral`
**Autores**: Equipo de análisis electoral
**Fecha**: Octubre 2025

---

## APÉNDICE A: Comandos de Ejecución

### Generar Swing Electoral
```bash
python calcular_swing.py
```

### Generar Escenarios CON TOPES
```bash
python tmp_generate_escenarios_con_topes.py
```

### Generar Escenarios SIN TOPES
```bash
python tmp_generate_escenarios_sin_topes.py
```

### Verificar Diferencias 2021 vs 2021_SWING
```bash
python tmp_compare_2021_swing.py
```

### Comparar CON vs SIN TOPES
```bash
python tmp_comparar_topes.py
```

---

## APÉNDICE B: Estructura de Datos

### Formato Parquet (Cómputos)
```
Columnas:
    ENTIDAD       - Nombre del estado (str)
    DISTRITO      - Número de distrito (int)
    PAN           - Votos PAN (int)
    PRI           - Votos PRI (int)
    PRD           - Votos PRD (int)
    PVEM          - Votos PVEM (int)
    PT            - Votos PT (int)
    MC            - Votos MC (int)
    MORENA        - Votos MORENA (int)
    [otros]       - Otros partidos/candidaturas
```

### Formato CSV (Siglado)
```
Columnas:
    ENTIDAD       - Código de entidad (int, 1-32)
    DISTRITO      - Número de distrito (int, 1-40)
    SIGLADO       - Siglas del partido ganador (str)
```

---

**FIN DEL DOCUMENTO**
