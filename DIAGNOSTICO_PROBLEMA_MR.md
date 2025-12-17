# DIAGNÓSTICO: Por qué el motor calcula MR incorrectamente

## Fecha: 17 de diciembre de 2025

## El Problema

El motor da resultados de MR que no coinciden con los oficiales:

**Discrepancias encontradas (comparando Motor actual vs Oficial):**
- MORENA: -10 escaños (247 vs 257 oficial)
- PVEM: +16 escaños (76 vs 60 oficial)
- PRD: +17 escaños (18 vs 1 oficial)
- PRI: +11 escaños (47 vs 36 oficial)
- **Total: 38 escaños mal asignados**

## La Causa Raíz

### Datos disponibles:
1. **`computos_diputados_2024.parquet`**: Votos por partido individual (PAN, PRI, PRD, MORENA, PT, PVEM, MC) en 300 distritos
   - ❌ **NO tiene** columnas de votos de coalición (FXM, coalición = 0 en todos los distritos)
   
2. **`siglado-diputados-2024.csv`**: Mapa de atribución (a qué partido se acredita el escaño si gana la coalición)
   - ✅ Dice: "Si FCM gana en AGS D1 → escaño para PRI"
   - ❌ **NO dice**: "FCM en AGS D1 está formada por PAN+PRI" o "PAN+PRI+PRD" o "solo PRI"

### Lo que se necesita y NO tenemos:

**Tabla de integración de coalición por distrito:**
```
distrito | coalicion_fcm           | coalicion_shh
AGS_1    | [PAN, PRI]             | [MORENA, PT, PVEM]
AGS_2    | [PAN, PRI, PRD]        | [MORENA, PVEM]
BC_1     | [PAN, PRI]             | null
...
```

**Sin esto, es IMPOSIBLE calcular correctamente:**
- Qué votos sumar para FCM en cada distrito
- Qué votos sumar para SHH en cada distrito
- Por tanto, quién ganó cada distrito
- Por tanto, el reparto final de MR

## Lo que el motor hace (y está MAL)

El motor **asume** que las coaliciones son fijas en todos los distritos:
- FCM = PAN + PRI + PRD (siempre)
- SHH = MORENA + PT + PVEM (siempre)

**Esto es FALSO.** Las coaliciones varían por distrito. Ejemplos:
- En algunos distritos FCM puede ser solo PAN+PRI
- En otros FCM puede ser PRI+PRD
- En algunos puede haber solo SHH pero no FCM

Al asumir coaliciones fijas, el motor:
1. **Infla votos de coaliciones** sumando partidos que no iban coaligados en ese distrito
2. **Cambia ganadores** artificialmente (coaliciones "ganadoras" que en realidad no existían así)
3. **Descuadra el MR** por 38 escaños totales

## Intentos de Corrección y Por Qué Fallaron

### Intento 1: "Usar el siglado correctamente"
**Error:** El siglado dice A QUIÉN SE ACREDITA, no QUIÉNES INTEGRAN la coalición.

### Intento 2: "Calcular MR esperado como Total - RP"
**Error:** Los totales oficiales son por partido, pero MR se calculó por candidatura/coalición. No se pueden restar naive.

### Intento 3: "Inferir integración del siglado"
**Error:** Si siglado dice "FCM → PRI" no significa "FCM = solo PRI", significa "FCM existe y si gana, acredita a PRI". No implica composición.

## La Verdad Incómoda

### ❌ NO SE PUEDE CALCULAR MR CORRECTAMENTE CON LOS DATOS DISPONIBLES

**Razón:** Falta el mapa de integración de coaliciones por distrito.

### Opciones:

#### Opción A: Conseguir el dato faltante
- Buscar archivo con convenios/registros de coalición por distrito
- Archivo con columnas tipo: `distrito`, `partidos_en_fcm`, `partidos_en_shh`
- **Status:** No disponible en el repo actual

#### Opción B: Aproximación tosca (advertir limitaciones)
- Asumir coaliciones completas (PAN+PRI+PRD, MORENA+PT+PVEM) donde siglado indica coalición
- **ADVERTENCIA:** Esto dará resultados incorrectos
- **Utilidad:** Solo para testing/desarrollo, NO para reportes oficiales
- **Desviación esperada:** ~38 escaños mal asignados (el error actual)

#### Opción C: Modo degradado (sin coaliciones)
- Calcular ganadores solo por partido individual (ignorar coaliciones)
- **ADVERTENCIA:** Dará resultados completamente diferentes a los oficiales
- **Utilidad:** Solo para análisis hipotéticos "sin coaliciones"

## Recomendación

**PRIORIDAD 1:** Localizar o construir el mapa de integración de coaliciones por distrito.

Posibles fuentes:
1. Archivos INE de registro de candidaturas
2. Convenios de coalición por distrito
3. Base de datos de candidatos con partido/coalición
4. Reconstrucción manual de documentación oficial

**Mientras no se tenga ese dato:**
- Documentar claramente la limitación
- Marcar resultados de MR como "aproximados" o "NO confiables"
- NO usar para reportes oficiales ni comparaciones con datos reales

## Hallazgos Adicionales

### ✅ Lo que SÍ está bien:
- **RP (Representación Proporcional):** El cálculo con método Hare está CORRECTO
  - PVEM: 8.74% → 18 escaños RP ✓
  - MORENA: 42.49% → 85 escaños RP ✓
  
- **Límites constitucionales:** Implementación correcta de max 300 escaños por partido

### ❌ Lo que está mal:
- **MR:** Cálculo fundamentalmente imposible sin datos de integración de coaliciones
- **Siglado:** Tiene bug de duplicación (MEXICO vs MÉXICO) creando 32 distritos fantasma
  - **Solución:** Normalizar entidades (aplicar normalización Unicode)

## Código de Normalización del Siglado

```python
import unicodedata

def normalizar_entidad(texto):
    """Normalizar entidad: quitar acentos, mayúsculas"""
    texto = str(texto).upper().strip()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) 
                    if unicodedata.category(c) != 'Mn')
    return texto

siglado['entidad_norm'] = siglado['entidad'].apply(normalizar_entidad)
```

Esto corrige el problema de 332 "distritos" → 300 correctos.

## Conclusión

El motor de MR **no puede funcionar correctamente** con los datos actuales.

**La discrepancia de 38 escaños NO es un bug de código**, es una **limitación de datos**.

Para arreglarlo se necesita un insumo que actualmente no existe en el repositorio:
**mapa de integración de coaliciones por distrito**.

---

*Documentado por: GitHub Copilot*
*Fecha: 17/12/2025*
