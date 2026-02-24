# ✅ Recordatorio: Simulación 300 MR + 100 PM + 100 RP

## Sí, me acuerdo del escenario

Este es el escenario electoral que generamos con **500 escaños totales** distribuidos así:

- **300 Mayoría Relativa (MR)** - Ganador por coalición en cada distrito
- **100 Primera Minoría (PM)** - Segundo lugar en los 100 distritos más competitivos
- **100 Representación Proporcional (RP)** - Método Hare a nivel nacional

## Archivos Disponibles

### 1. Script Principal
📄 **`simular_escenario_300mr_100pm_100rp.py`**
- Genera la simulación completa
- Procesa años 2021 y 2024
- Primera Minoría calculada por COALICIÓN

### 2. Resultados
📊 **`simulacion_300mr_100pm_100rp.csv`**

```csv
Año,Coalición,MR_Escaños,PM_Escaños,RP_Escaños,Total_Escaños,Porcentaje
2021,SHH,182,34,48,264,52.8
2021,FCM,111,60,44,215,43.0
2021,MC,7,6,8,21,4.2
2024,SHH,256,30,57,343,68.6
2024,FCM,43,52,32,127,25.4
2024,MC,1,18,11,30,6.0
```

### 3. Documentación
📖 **`README_simulacion_300mr_100pm_100rp.md`**
- Explicación completa del sistema
- Interpretación de resultados
- Notas técnicas

📋 **`RESUMEN_SIMULACION.txt`**
- Resumen visual con tablas
- Comparación entre años

## Resultados Clave 2024

| Coalición | MR | PM | RP | Total | % |
|-----------|----|----|-------|-------|-----|
| **SHH** | 256 | 30 | 57 | **343** | **68.6%** |
| **FCM** | 43 | 52 | 32 | **127** | **25.4%** |
| **MC** | 1 | 18 | 11 | **30** | **6.0%** |

### Análisis 2024

- **SHH domina** con 343 escaños (68.6%)
  - Ganó 256/300 distritos (85.3% en MR)
  - Solo 30 PM (baja competitividad en distritos perdidos)
  - 57 escaños por RP

- **FCM** con 127 escaños (25.4%)
  - Solo 43 distritos en MR
  - 52 PM (muy competitivo en segundos lugares)
  - 32 escaños por RP

- **MC** con 30 escaños (6.0%)
  - Solo 1 distrito en MR
  - 18 PM (competitivo a pesar de pocas victorias)
  - 11 escaños por RP

## Coaliciones

- **SHH** (Sigamos Haciendo Historia): MORENA + PT + PVEM
- **FCM** (Fuerza y Corazón por México): PAN + PRI + PRD
- **MC** (Movimiento Ciudadano): va solo

## Cómo Usar

```bash
# Regenerar la simulación
python simular_escenario_300mr_100pm_100rp.py

# Ver resultados
cat simulacion_300mr_100pm_100rp.csv

# Ver documentación completa
cat README_simulacion_300mr_100pm_100rp.md
```

## Características Especiales

### Primera Minoría por Coalición
- **NO** se calcula por partido individual
- Se asigna al **segundo lugar por coalición**
- Los 100 PM van a los distritos más competitivos (menor margen entre 1° y 2°)

### Representación Proporcional
- Método **Hare** (cociente + mayores residuos)
- Basado en votos nacionales totales por coalición
- Distribuye 100 escaños proporcionalmente

## Análisis Complementario

También generamos:

### Límite MR para PM
📄 **`analizar_limite_mr_pm.py`**
- Análisis del límite superior de MR para recibir PM
- **Respuesta**: 200 distritos MR (límite práctico)
- Fórmula: `PM_máximo = min(300 - MR_ganados, 100)`

📊 **`analisis_limite_mr_pm.csv`**
- Tabla de escenarios de 0 a 300 MR

## Evolución 2021 → 2024

| Coalición | 2021 | 2024 | Cambio |
|-----------|------|------|--------|
| **SHH** | 264 (52.8%) | 343 (68.6%) | +79 (+15.8pp) 📈 |
| **FCM** | 215 (43.0%) | 127 (25.4%) | -88 (-17.6pp) 📉 |
| **MC** | 21 (4.2%) | 30 (6.0%) | +9 (+1.8pp) 📈 |

## Validación

El script verifica:
- ✅ 300 escaños de MR asignados (uno por distrito)
- ✅ 100 escaños de PM asignados
- ✅ 100 escaños de RP asignados
- ✅ **Total: 500 escaños**

## Estado Actual

✅ **Todo está listo y funcionando**
- Scripts validados
- Datos generados
- Documentación completa
- CSV exportable

## ¿Qué Necesitas Hacer con Esto?

Dime si quieres:
- Modificar algún parámetro
- Generar una variante
- Analizar algún aspecto específico
- Exportar en otro formato
- Hacer comparaciones adicionales

¡Estoy listo para ayudarte! 🚀
