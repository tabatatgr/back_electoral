# 📊 Documentación: Cálculo de Distritos MR (Mayoría Relativa)

## 🎯 Propósito

Este documento explica cómo el sistema calcula los distritos de Mayoría Relativa (MR) usando **redistritación geográfica SIEMPRE activa**.

## ⚡ IMPORTANTE: Redistritación Geográfica SIEMPRE Activa

La redistritación geográfica está **FORZADA a True en todos los casos** (desde 16 Enero 2026).

**Razones:**
- ✅ Garantiza cálculo correcto de MR en todos los escenarios
- ✅ Usa eficiencias históricas reales por partido
- ✅ Distribuye distritos por estado según método Hare (oficial INE)
- ✅ No puede desactivarse desde el frontend o API
- ✅ Consistencia total en el comportamiento del sistema

**Implementación:**
```python
# En main.py línea ~2283
redistritacion_geografica = True  # FORZADO, no es parámetro
```

## 🔄 Flujo de Cálculo de MR

### Caso 1: Datos Históricos (SIN cambios de porcentajes)

**Cuándo:** Usuario consulta resultados de un año electoral sin modificar porcentajes

**Proceso:**
1. ✅ Lee archivo `siglado-diputados-{año}.csv` (resultados reales oficiales)
2. ✅ **Activa redistritación geográfica** (siempre)
3. ✅ Calcula eficiencias históricas de cada partido
4. ✅ Calcula MR geográficos basándose en votos históricos
5. ✅ Determina ganador distrito por distrito basado en votos históricos
6. ✅ Usa coaliciones reales del siglado para descomponer escaños
7. ✅ Resultado: **Refleja exactamente los resultados oficiales del año**

**Parámetros:**
- `votos_redistribuidos = None`
- `redistritacion_geografica = True` ← **SIEMPRE**
- `mr_ganados_geograficos = {calculados con eficiencias históricas}`
- `path_siglado = data/siglado-diputados-{año}.csv`

**Por qué es correcto:**
- El siglado contiene los resultados oficiales certificados
- No hay cambios que simular, solo mostrar la realidad

---

### Caso 2: Usuario Cambia Porcentajes/Parámetros

**Cuándo:** Usuario modifica porcentajes de votos, usa sliders, o cambia parámetros

**Proceso:**
1. ✅ Detecta que hay `votos_redistribuidos` o `porcentajes_partidos`
2. ✅ Redistribuye votos por distrito según nuevos porcentajes
3. ✅ **GENERA SIGLADO TEMPORAL** con ganadores según votos redistribuidos
4. ✅ Calcula quién gana cada distrito con los nuevos votos
5. ✅ **ACTIVA automáticamente `redistritacion_geografica=True`**
6. ✅ Calcula eficiencias históricas reales por partido del siglado original
7. ✅ Aplica esas eficiencias a los NUEVOS porcentajes
8. ✅ Recalcula MR por estado usando distribución geográfica Hare
9. ✅ Genera `mr_ganados_geograficos` con totales por partido
10. ✅ Pasa votos redistribuidos + siglado temporal + mr_ganados al motor

**Parámetros:**
- `votos_redistribuidos = {dict con % por partido}`
- `redistritacion_geografica = True` ← **SIEMPRE**
- `mr_ganados_geograficos = {dict con MR por partido}`
- `path_siglado = outputs/tmp_siglado_xxx.csv` (siglado temporal)

**Por qué es correcto:**
- Los nuevos porcentajes alteran quién ganaría cada distrito
- El **siglado temporal** refleja los ganadores con los nuevos votos
- La eficiencia histórica del partido se mantiene (refleja su fortaleza geográfica)
- Los MR se recalculan dinámicamente según el nuevo escenario
- El motor usa el siglado temporal como **base** para determinar ganadores

---

### Caso 3: Mayoría Forzada

**Cuándo:** Usuario usa endpoint `/calcular/mayoria_forzada`

**Proceso:**
1. ✅ Calcula % de votos necesarios para mayoría simple/calificada
2. ✅ Llama a `calcular_distritos_mr_realistas()` con ese %
3. ✅ Usa eficiencias históricas + distribución Hare
4. ✅ Genera `mr_ganados_geograficos` directamente
5. ✅ Pasa al motor sin usar siglado para determinar ganadores

**Por qué es correcto:**
- Escenario hipotético que NO existe en el siglado
- Requiere proyección basada en datos históricos pero con nuevo %

---

## 🔧 Componentes Clave

### 1. Siglado (`data/siglado-diputados-{año}.csv`)

**Contiene:**
- Resultados oficiales distrito por distrito
- Coaliciones reales del año
- Grupo parlamentario de cada diputado electo
- Base para calcular eficiencias históricas

**Se usa para:**
- ✅ Extraer coaliciones del año
- ✅ Calcular eficiencias geográficas históricas por partido
- ✅ Determinar ganadores cuando NO hay cambios (resultados oficiales)
- ✅ **BASE para generar siglado temporal** cuando hay redistribución

**Siglado Temporal:**
Cuando hay redistribución de votos, se genera automáticamente un **siglado temporal** que:
- Calcula ganadores distrito por distrito según votos redistribuidos
- Se guarda en `outputs/tmp_siglado_{uuid}.csv`
- Se pasa al motor en lugar del siglado histórico
- Garantiza que el motor use los ganadores correctos para el nuevo escenario

### 2. Redistritación Geográfica

**Módulo:** `redistritacion/modulos/`

**Funciones:**
- `repartir_distritos_hare()`: Distribuye distritos por estado según población
- `cargar_secciones_ine()`: Carga datos de población por estado
- `calcular_eficiencia_partidos()`: Calcula eficiencia histórica real por partido

**Eficiencia Geográfica:**
- Mide qué tan bien un partido convierte votos en escaños MR
- Ejemplo: MORENA 2024 = 1.15 (gana 15% más MR de lo proporcional)
- Ejemplo: MC 2024 = 0.85 (gana 15% menos MR de lo proporcional)
- Se calcula comparando MR reales vs. MR proporcionales

### 3. Motor de Procesamiento

**Archivo:** `engine/procesar_diputados_v2.py`

**Lógica de MR:**
```python
if mr_ganados_geograficos is not None:
    # CASO: Hay MR pre-calculados con redistritación geográfica
    usar_mr_geograficos()  # ✅ Refleja cambios del usuario
    
elif coaliciones_detectadas and usar_coaliciones:
    # CASO: Hay siglado (histórico o temporal)
    # Lee distrito por distrito del siglado para determinar ganadores
    calcular_desde_siglado_distrito_por_distrito()  
    # ✅ Si hay siglado temporal → refleja redistribución
    # ✅ Si hay siglado histórico → resultados oficiales
    
else:
    # CASO: Cálculo simple sin coaliciones
    calcular_desde_votos_directos()
```

### 4. Tabla Puente (`redistritacion/modulos/tabla_puente.py`)

**Propósito:** Generar siglado temporal cuando hay redistribución de votos

**Funciones clave:**
- `generar_siglado_new()`: Calcula ganadores por distrito según votos redistribuidos
- `reagregar_votos_por_distrito_new()`: Reagrega votos según nueva cartografía

**Proceso:**
1. Lee votos redistribuidos (formato WIDE con partidos en columnas)
2. Calcula ganador por distrito basándose en máximo de votos
3. Genera DataFrame con estructura compatible con siglado
4. Guarda en archivo temporal CSV

**Ejemplo de siglado temporal generado:**
```csv
ENTIDAD,DISTRITO,grupo_parlamentario,VOTOS,coalicion,tipo_eleccion
AGUASCALIENTES,1,MORENA,45000,,MR
AGUASCALIENTES,2,PAN,38000,,MR
BAJA CALIFORNIA,1,MORENA,52000,,MR
```

---

## ✅ RESUMEN DE CAMBIOS IMPLEMENTADOS (16 Enero 2026)

### 🎯 Problema Identificado
1. El siglado histórico se usaba para determinar ganadores incluso cuando el usuario cambiaba porcentajes
2. La redistritación geográfica era un parámetro opcional que podía desactivarse
3. Sin redistritación geográfica, los MR no se calculaban correctamente

### 🔧 Solución Implementada

**4 cambios críticos en `main.py`:**

#### 1. Redistritación Geográfica SIEMPRE Activa (línea ~2283)
```python
# FORZAR redistritación geográfica SIEMPRE activa
redistritacion_geografica = True
print(f"[DEBUG] - redistritacion_geografica: FORZADO a True (SIEMPRE activo)")
```

**Efecto:** La redistritación geográfica NO puede desactivarse, garantizando cálculo correcto en todos los casos.

#### 2. Parámetro Removido de Firma (línea ~2055)
```python
# Antes:
redistritacion_geografica: bool = True,  # ❌ Podía pasarse como False

# Ahora: REMOVIDO de la firma de la función
# redistritacion_geografica se fuerza internamente
```

**Efecto:** El frontend no puede desactivar la redistritación geográfica.

#### 3. Generación de Siglado Temporal (línea ~2476)
```python
# GENERAR SIGLADO TEMPORAL con ganadores según votos redistribuidos
from redistritacion.modulos.tabla_puente import generar_siglado_new

siglado_temporal = generar_siglado_new(tmp_to_save, print_debug=False)
siglado_temporal.to_csv(siglado_tmp_name, index=False)

# Actualizar path_siglado para usar el temporal
path_siglado = siglado_tmp_name
```

**Efecto:** Cuando el usuario cambia porcentajes, el sistema genera un nuevo siglado con los ganadores calculados según los nuevos votos.

#### 4. Protección de Path Siglado (línea ~2762)
```python
# IMPORTANTE: Si ya se generó un siglado temporal, NO sobrescribirlo
if 'path_siglado' not in locals() or path_siglado is None:
    path_siglado = f"data/siglado-diputados-{anio}.csv"
```

**Efecto:** Preserva el siglado temporal generado, evitando que se sobrescriba con el histórico.

---

## 🔄 Flujo Completo con Redistribución

```
Usuario cambia porcentajes → 
  ↓
Redistribuir votos por distrito →
  ↓
Generar siglado temporal (ganadores según nuevos votos) →
  ↓
Activar redistritación geográfica →
  ↓
Calcular eficiencias históricas del siglado original →
  ↓
Aplicar eficiencias a nuevos porcentajes →
  ↓
Calcular mr_ganados_geograficos →
  ↓
Pasar al motor:
  - votos redistribuidos
  - siglado temporal ← CRUCIAL
  - mr_ganados_geograficos
  ↓
Motor usa siglado temporal como BASE para determinar ganadores →
  ↓
Resultados reflejan correctamente los cambios del usuario ✅
```

El sistema **activa automáticamente** `redistritacion_geografica=True` cuando detecta:

1. ✅ `votos_redistribuidos != None`
2. ✅ `porcentajes_partidos != None`
3. ✅ `votos_custom != None`
4. ✅ `partidos_fijos != None`
5. ✅ `overrides_pool != None`

**Código:**
```python
# En main.py línea ~2761
if votos_redistribuidos and not redistritacion_geografica:
    print(f"[DEBUG] Activando redistritación geográfica automáticamente")
    redistritacion_geografica = True
```

---

## 🚨 Validaciones y Warnings

El sistema genera warnings cuando detecta inconsistencias:

```
[INFO] ✅ MR se calcularán con REDISTRITACIÓN GEOGRÁFICA
[INFO] Total MR pre-calculados: 300

[INFO] ⚠️  MR se calcularán DISTRITO POR DISTRITO desde siglado histórico
[INFO] Esto es correcto SOLO si NO hay redistribución de votos

[WARN] ⚠️⚠️⚠️  HAY VOTOS REDISTRIBUIDOS pero mr_ganados_geograficos es None!
[WARN] Los resultados pueden NO reflejar los cambios solicitados
```

---

## 📋 Ejemplos de Uso

### Ejemplo 1: Ver resultados oficiales 2024
```python
POST /procesar/diputados
{
  "anio": 2024,
  "plan": "vigente"
}
```
→ Usa siglado directamente, muestra resultados oficiales

### Ejemplo 2: Simular MORENA con 50%
```python
POST /procesar/diputados
{
  "anio": 2024,
  "plan": "vigente",
  "porcentajes_partidos": {"MORENA": 50, "PAN": 25, "PRI": 25}
}
```
→ Activa redistritación geográfica automáticamente
→ Recalcula MR con eficiencia histórica de MORENA aplicada al 50%

### Ejemplo 3: Mayoría forzada
```python
GET /calcular/mayoria_forzada?partido=MORENA&tipo_mayoria=simple
```
→ Calcula % necesario
→ Genera `mr_ganados_geograficos` directamente
→ NO usa siglado para determinar ganadores

---

## 🎓 Conceptos Clave

### Eficiencia Geográfica
**Definición:** Ratio entre MR ganados reales y MR proporcionales esperados

**Fórmula:**
```
Eficiencia = MR_reales / MR_proporcionales
```

**Interpretación:**
- `1.0` = Conversión perfectamente proporcional
- `>1.0` = Sobrerrepresentación geográfica (gana más MR de lo esperado)
- `<1.0` = Subrepresentación geográfica (gana menos MR de lo esperado)

**Ejemplos 2024:**
- MORENA: 1.15 (muy eficiente geográficamente)
- PAN: 0.95 (ligeramente ineficiente)
- MC: 0.85 (muy concentrado, pierde MR)

### Método Hare
**Propósito:** Distribuir distritos por estado según población

**Características:**
- Método oficial usado por el INE
- Garantiza piso constitucional de 2 distritos por estado
- Basado en cuota exacta con residuos

---

## 🔍 Debugging

Para verificar qué método se está usando, busca en los logs:

```bash
[DEBUG] redistritacion_geografica: True/False
[DEBUG] votos_redistribuidos: {dict} or None
[DEBUG] MR ganados con redistritación geográfica: {dict}
[INFO] ✅ MR se calcularán con REDISTRITACIÓN GEOGRÁFICA
```

Si ves:
```
[WARN] HAY VOTOS REDISTRIBUIDOS pero mr_ganados_geograficos es None!
```
→ Hay un bug, el sistema no está recalculando MR correctamente

---

## 📚 Referencias

- `main.py` líneas 2755-2970: Lógica de activación de redistritación
- `engine/procesar_diputados_v2.py` líneas 1260-1500: Cálculo de MR
- `engine/calcular_eficiencia_real.py`: Cálculo de eficiencias históricas
- `redistritacion/modulos/reparto_distritos.py`: Método Hare

---

**Última actualización:** 16 de enero de 2026
**Versión:** 2.0
