# Simulación Electoral: 300 MR + 100 PM + 100 RP

## Descripción

Este script simula un escenario electoral mexicano con un sistema de **500 escaños totales**:

- **300 escaños de Mayoría Relativa (MR)**: El ganador por coalición en cada distrito
- **100 escaños de Primera Minoría (PM)**: El segundo lugar por coalición en los 100 distritos más competitivos
- **100 escaños de Representación Proporcional (RP)**: Distribuidos proporcionalmente a nivel nacional

## Características Clave

### Primera Minoría por Coalición
La **primera minoría se calcula por COALICIÓN**, no por partido individual:

- **SHH (Sigamos Haciendo Historia)**: MORENA + PT + PVEM
- **FCM (Fuerza y Corazón por México)**: PAN + PRI + PRD
- **MC (Movimiento Ciudadano)**: va solo

### Asignación de PM
Los 100 escaños de primera minoría se asignan a los **100 distritos más competitivos**, es decir, aquellos donde el margen entre el primer y segundo lugar fue menor.

### Representación Proporcional
Se usa el **método Hare** para distribuir los 100 escaños de RP basados en los votos totales a nivel nacional de cada coalición.

## Uso

```bash
python simular_escenario_300mr_100pm_100rp.py
```

## Resultados

El script genera:

1. **Salida en consola** con resultados detallados por año
2. **CSV**: `simulacion_300mr_100pm_100rp.csv` con el desglose completo

### Estructura del CSV

| Columna | Descripción |
|---------|-------------|
| `Año` | Año electoral (2021 o 2024) |
| `Coalición` | SHH, FCM o MC |
| `MR_Escaños` | Escaños de Mayoría Relativa |
| `PM_Escaños` | Escaños de Primera Minoría |
| `RP_Escaños` | Escaños de Representación Proporcional |
| `Total_Escaños` | Total de escaños (MR + PM + RP) |
| `Porcentaje` | Porcentaje del total de 500 escaños |

## Resultados 2024

| Coalición | MR | PM | RP | Total | % |
|-----------|----|----|-------|-------|-----|
| **SHH** | 256 | 30 | 57 | **343** | **68.6%** |
| **FCM** | 43 | 52 | 32 | **127** | **25.4%** |
| **MC** | 1 | 18 | 11 | **30** | **6.0%** |

### Interpretación 2024

- **SHH** domina con 343 escaños (68.6% del total)
  - Ganó 256 de 300 distritos en MR (85.3%)
  - Obtuvo solo 30 PM (competitividad baja en distritos perdidos)
  - Recibió 57 escaños por RP
  
- **FCM** quedó segunda con 127 escaños (25.4%)
  - Ganó 43 distritos en MR (14.3%)
  - Obtuvo 52 PM (fue segundo lugar en muchos distritos competitivos)
  - Recibió 32 escaños por RP
  
- **MC** obtuvo 30 escaños (6.0%)
  - Ganó solo 1 distrito en MR
  - Obtuvo 18 PM (fue competitivo en varios distritos)
  - Recibió 11 escaños por RP

## Resultados 2021

| Coalición | MR | PM | RP | Total | % |
|-----------|----|----|-------|-------|-----|
| **SHH** | 182 | 34 | 48 | **264** | **52.8%** |
| **FCM** | 111 | 60 | 44 | **215** | **43.0%** |
| **MC** | 7 | 6 | 8 | **21** | **4.2%** |

### Comparación 2021 vs 2024

**SHH Coalition:**
- 2021: 264 escaños (52.8%)
- 2024: 343 escaños (68.6%)
- **Diferencia: +79 escaños (+15.8 puntos porcentuales)**

**FCM Coalition:**
- 2021: 215 escaños (43.0%)
- 2024: 127 escaños (25.4%)
- **Diferencia: -88 escaños (-17.6 puntos porcentuales)**

**MC:**
- 2021: 21 escaños (4.2%)
- 2024: 30 escaños (6.0%)
- **Diferencia: +9 escaños (+1.8 puntos porcentuales)**

## Notas Técnicas

### Datos de Entrada
- `data/computos_diputados_2021.parquet`: 300 distritos electorales de 2021
- `data/computos_diputados_2024.parquet`: 300 distritos electorales de 2024

### Validación
El script verifica que:
- Se asignen exactamente 300 escaños de MR (uno por distrito)
- Se asignen exactamente 100 escaños de PM
- Se asignen exactamente 100 escaños de RP
- **Total: 500 escaños**

## Archivos Generados

- `simulacion_300mr_100pm_100rp.csv`: Resultados comparativos para 2021 y 2024

## Dependencias

```bash
pip install pandas pyarrow
```

## Autor

Script creado para simular escenarios electorales mexicanos bajo diferentes sistemas de asignación de escaños.
