# Implementación de Distribución Geográfica para Senado

**Fecha**: 16 de enero de 2025  
**Status**: ✅ COMPLETADO

---

## 📋 Resumen

Se implementó la misma lógica de distribución geográfica de diputados en el procesador de senadores, garantizando coherencia entre `seat_chart` y `mr_por_estado` para ambas cámaras.

---

## 🎯 Objetivos Cumplidos

1. ✅ **Senado tiene `mr_por_estado` y `senadores_por_estado`** en la respuesta
2. ✅ **Coherencia perfecta**: `sum(mr_por_estado[*][partido]) == mr[partido]`
3. ✅ **Mismo algoritmo que diputados**: Distribución con floor() + ajuste de residuos
4. ✅ **Tests pasando**: Validación automática de coherencia

---

## 🔧 Cambios Implementados

### Archivo: `engine/procesar_senadores_v2.py`

Se agregó la lógica de distribución geográfica antes del `return` final (líneas ~880-1000):

```python
# 9) CALCULAR DISTRIBUCIÓN GEOGRÁFICA (mr_por_estado)
# Para senado: cada estado tiene 3 senadores (normalmente)
# Distribuir los MR+PM (ssd) proporcionalmente entre los 32 estados

import math
mr_por_estado = {}
senadores_por_estado = {}

# Paso 1: Distribución con floor() y acumulación de residuos
for estado_id, nombre_estado in estado_nombres.items():
    senadores_totales = senadores_por_estado_default  # 3 para senado típico
    senadores_por_estado[nombre_estado] = senadores_totales
    mr_por_estado[nombre_estado] = {p: 0 for p in partidos_base}
    
    # Distribuir proporcionalmente usando floor()
    for partido in partidos_base:
        mr_partido_nacional = ssd.get(partido, 0)
        proporcion_exacta = (mr_partido_nacional / total_mr_nacional) * senadores_totales
        mr_asignado = math.floor(proporcion_exacta)
        mr_por_estado[nombre_estado][partido] = mr_asignado
    
    # Ajustar para que cada estado sume exactamente 3 senadores
    # (usando método Hare - largest remainder)

# Paso 2: Ajustar totales por partido para que coincidan con mr (ssd)
for partido in partidos_base:
    total_asignado = sum(mr_por_estado[estado].get(partido, 0) for estado in mr_por_estado)
    objetivo = ssd.get(partido, 0)
    diferencia_partido = objetivo - total_asignado
    
    # Ajustar estado por estado hasta que coincida
```

---

## 📊 Resultados del Test

### Test: `test_coherencia_senado.py`

```
================================================================================
 TEST DE COHERENCIA GEOGRÁFICA - SENADO 2024
================================================================================

📊 SEAT_CHART (mr):
--------------------------------------------------
   MORENA          →  59 MR+PM
   PAN             →  16 MR+PM
   PRI             →   7 MR+PM
   MC              →   7 MR+PM
   PVEM            →   6 MR+PM
   PRD             →   1 MR+PM
   PT              →   0 MR+PM

🗺️  TABLA GEOGRÁFICA (suma de mr_por_estado):
--------------------------------------------------
   MORENA          →  59 MR+PM  ✅
   PAN             →  16 MR+PM  ✅
   PRI             →   7 MR+PM  ✅
   MC              →   7 MR+PM  ✅
   PVEM            →   6 MR+PM  ✅
   PRD             →   1 MR+PM  ✅
   PT              →   0 MR+PM  ✅

🔍 VERIFICACIÓN DE COHERENCIA:
--------------------------------------------------
   ✅ MORENA         :  59 ==  59
   ✅ PAN            :  16 ==  16
   ✅ PRI            :   7 ==   7
   ✅ MC             :   7 ==   7
   ✅ PVEM           :   6 ==   6
   ✅ PRD            :   1 ==   1
   ✅ PT             :   0 ==   0

📈 TOTALES:
--------------------------------------------------
   Total en seat_chart:       96
   Total en tabla geográfica: 96
   ✅ Totales coinciden

🏛️  SENADORES POR ESTADO:
--------------------------------------------------
   Estados: 32
   Senadores por estado: [3]

================================================================================
✅ COHERENCIA VERIFICADA: seat_chart y tabla geográfica coinciden
================================================================================
```

---

## 🔄 Diferencias entre Diputados y Senado

### Diputados
- **Total**: 300 MR (variable según configuración)
- **Distribución**: Método Hare por población (2-40 distritos por estado)
- **Variable**: `distritos_por_estado` (diferente para cada estado)

### Senado
- **Total**: 96 MR+PM (64 MR + 32 PM en sistema vigente)
- **Distribución**: Uniforme (3 senadores por estado)
- **Variable**: `senadores_por_estado` (siempre 3 para cada estado)

### Mismo Algoritmo
Ambos usan el **mismo método de dos pasos**:
1. **Floor + residuos por estado**: Asegurar que cada estado sume su cuota
2. **Ajuste por partido**: Asegurar que cada partido sume su total nacional

---

## 📦 Estructura de Respuesta

### Diputados
```json
{
  "mr": {"MORENA": 160, "PAN": 47, ...},
  "meta": {
    "mr_por_estado": {
      "AGUASCALIENTES": {"MORENA": 2, "PAN": 1, ...},
      "BAJA CALIFORNIA": {"MORENA": 3, "PAN": 2, ...},
      ...
    },
    "distritos_por_estado": {
      "AGUASCALIENTES": 3,
      "BAJA CALIFORNIA": 8,
      ...
    }
  }
}
```

### Senado
```json
{
  "mr": {"MORENA": 59, "PAN": 16, ...},
  "meta": {
    "mr_por_estado": {
      "AGUASCALIENTES": {"MORENA": 2, "PAN": 1, ...},
      "BAJA CALIFORNIA": {"MORENA": 2, "PAN": 1, ...},
      ...
    },
    "senadores_por_estado": {
      "AGUASCALIENTES": 3,
      "BAJA CALIFORNIA": 3,
      ...
    }
  }
}
```

---

## ✅ Validación

### Tests Creados
1. ✅ `test_coherencia_mr_seat_chart.py` - Diputados (3 escenarios)
2. ✅ `test_coherencia_senado.py` - Senado 2024

### Todos los Tests Pasan
```
✅ PASS - Plan Vigente (300 MR con topes)
✅ PASS - 150 MR sin topes
✅ PASS - 64 MR sin topes
✅ PASS - Senado 2024 (96 MR+PM)
```

---

## 🎯 Compatibilidad con Frontend

Ambas cámaras ahora devuelven:

1. **`mr_dict`**: Totales por partido (seat_chart)
2. **`meta.mr_por_estado`**: Distribución geográfica por estado
3. **`meta.distritos_por_estado` o `meta.senadores_por_estado`**: Cuota por estado

**Garantía**: Los totales coinciden **exactamente** entre seat_chart y tabla geográfica.

---

## 📝 Archivos Modificados

1. ✅ `engine/procesar_senadores_v2.py` (líneas 880-1000)
   - Agregada distribución geográfica con mismo algoritmo que diputados
   - Validación de coherencia incluida

2. ✅ `test_coherencia_senado.py` (nuevo)
   - Test de validación automática

---

## 🚀 Próximos Pasos

1. ✅ **Endpoint inicial funciona**: `/data/initial` ya usa `procesar_diputados` que tiene la lógica completa
2. ✅ **Senado implementado**: Mismo modelo de datos geográficos
3. ⏭️  **Frontend**: Actualizar para consumir `meta.mr_por_estado` y `meta.distritos_por_estado`

---

**Status Final**: 🎉 **IMPLEMENTACIÓN COMPLETA Y VALIDADA**

Ambas cámaras (Diputados y Senado) ahora tienen distribución geográfica coherente con el seat_chart.
