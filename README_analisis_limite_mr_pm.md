# Análisis: Límite Superior de Distritos MR para Recibir PM

## Pregunta

**¿Cuál es el límite superior de distritos en mayoría relativa (MR) para que aún te toquen diputados de mejor perdedor (primera minoría/PM)?**

## Respuesta Rápida

### Límite Teórico: **299 distritos MR**
- Puedes ganar hasta 299 distritos y aún recibir 1 escaño PM

### Límite Práctico: **200 distritos MR**
- Para recibir los 100 escaños PM completos

## Explicación

### Regla Fundamental

Los escaños de **Primera Minoría (PM)** se asignan a quien queda en **SEGUNDO LUGAR** en un distrito. Por lo tanto:

- Si **ganas** un distrito en MR → NO puedes recibir PM de ese distrito
- Si **pierdes** un distrito → Puedes quedar 2° y recibir PM

### Fórmula

```
PM máximo posible = min(300 - MR_ganados, 100)
```

Donde:
- 300 = Total de distritos
- 100 = Escaños PM disponibles en el sistema
- MR_ganados = Distritos que ganaste en Mayoría Relativa

## Escenarios Detallados

| MR Ganados | Distritos Perdidos | PM Potencial | PM Completo | Total |
|------------|-------------------|--------------|-------------|-------|
| 0 | 300 | 100 | ✅ SÍ | 100 |
| 50 | 250 | 100 | ✅ SÍ | 150 |
| 100 | 200 | 100 | ✅ SÍ | 200 |
| 150 | 150 | 100 | ✅ SÍ | 250 |
| **200** | **100** | **100** | ✅ **SÍ** | **300** |
| 210 | 90 | 90 | ❌ NO | 300 |
| 220 | 80 | 80 | ❌ NO | 300 |
| 250 | 50 | 50 | ❌ NO | 300 |
| 280 | 20 | 20 | ❌ NO | 300 |
| 290 | 10 | 10 | ❌ NO | 300 |
| 299 | 1 | 1 | ❌ NO | 300 |
| 300 | 0 | 0 | ❌ NO | 300 |

### Punto de Inflexión

**A partir de 201 distritos MR**, ya no se pueden obtener los 100 escaños PM completos.

## Ejemplos Prácticos

### Ejemplo 1: Coalición Dominante (256 MR - SHH 2024)

```
MR ganados:    256 distritos
Perdidos:       44 distritos
PM máximo:      44 escaños (no los 100)
PM reales:      30 escaños (quedó 2° en 30 competitivos)
```

⚠️ **Por encima del límite** → PM limitado por falta de distritos perdidos

### Ejemplo 2: Coalición Moderada (200 MR)

```
MR ganados:    200 distritos
Perdidos:      100 distritos
PM máximo:     100 escaños ✓
PM reales:     100 escaños (si queda 2° en todos)
```

✅ **En el límite exacto** → Puede recibir PM completo

### Ejemplo 3: Coalición Débil (43 MR - FCM 2024)

```
MR ganados:     43 distritos
Perdidos:      257 distritos
PM máximo:     100 escaños ✓
PM reales:      52 escaños (quedó 2° en 52 competitivos)
```

✅ **Por debajo del límite** → No hay restricción de PM

## Visualización

```
MR Ganados │ PM Potencial │ Visualización
───────────┼──────────────┼────────────────────────────
  0        │  100         │ PM: ░░░░░░░░░░░░░░░░░░░░
100        │  100         │ MR: ██████████  PM: ░░░░░░░░░░░░░░░░░░░░
200        │  100         │ MR: ████████████████████  PM: ░░░░░░░░░░░░░░░░░░░░ ← LÍMITE
220        │   80         │ MR: ██████████████████████  PM: ░░░░░░░░░░░░░░░░
250        │   50         │ MR: █████████████████████████  PM: ░░░░░░░░░░
280        │   20         │ MR: ████████████████████████████  PM: ░░░░
300        │    0         │ MR: ██████████████████████████████  PM: (ninguno)
```

## ¿Por Qué Existe Este Límite?

### Lógica del Sistema

1. **PM = Segunda posición**: Solo quien queda segundo recibe PM
2. **Exclusión mutua**: No puedes ser primero Y segundo en el mismo distrito
3. **Competitividad**: PM se asigna a los 100 distritos más competitivos

### Consecuencia

Si ganas **demasiados** distritos en MR:
- ✓ Aumentas tus escaños MR
- ✗ Reduces los distritos donde puedes quedar 2°
- ✗ Reduces tus escaños PM potenciales

## Estrategia Electoral

### Escenario Óptimo para PM Completo

Para maximizar PM (100 escaños):
- Ganar **máximo 200 distritos** en MR
- Quedar **2° en 100 distritos** más competitivos
- Total potencial: **300 escaños** (200 MR + 100 PM)

### Trade-off

- **Más MR** → Menos distritos perdidos → Menos PM posibles
- **Menos MR** → Más distritos perdidos → Más PM posibles (hasta 100)

## Datos Reales 2024

Basado en `simulacion_300mr_100pm_100rp.csv`:

| Coalición | MR | Perdidos | PM Potencial | PM Real | ¿PM Completo? |
|-----------|----|---------:|-------------:|--------:|---------------|
| **SHH** | 256 | 44 | 44 | 30 | ❌ NO (limitado) |
| **FCM** | 43 | 257 | 100 | 52 | ✅ SÍ (sin límite) |
| **MC** | 1 | 299 | 100 | 18 | ✅ SÍ (sin límite) |

### Observaciones

- **SHH** ganó tantos distritos MR (256) que solo puede aspirar a 44 PM máximo
- **FCM** y **MC** tienen suficientes distritos perdidos para recibir 100 PM si fueran competitivos

## Archivos

### Script
```bash
python analizar_limite_mr_pm.py
```

### Output
- **CSV**: `analisis_limite_mr_pm.csv` - Tabla completa de escenarios
- **Console**: Análisis detallado, visualización y respuesta directa

## Conclusión

**Respuesta a la pregunta original:**

> ¿Cuál es el límite superior de distritos MR para recibir PM?

**200 distritos** es el límite práctico para recibir los **100 escaños PM completos**.

Si ganas **más de 200 MR**:
- Pierdes menos de 100 distritos
- Tu PM máximo = 300 - MR_ganados
- Ejemplo: 250 MR → Máximo 50 PM

**Regla de oro:**
```
PM_máximo = min(300 - MR_ganados, 100)
```
