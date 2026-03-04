# Análisis del Punto Óptimo: Sistema MR + RP Normal + RP Mejores Perdedores

## Pregunta

**"¿A partir de cuántos distritos ganados por circunscripción te quedas sin perdedores para acomodar?"**

Bajo el sistema electoral mexicano con:
- 300 distritos de Mayoría Relativa (MR)
- Primera vuelta RP: 100 asientos (proporcional normal)
- Segunda vuelta RP: 100 asientos (mejores perdedores - de distritos perdidos)

## Respuesta Directa

### 🎯 PUNTO ÓPTIMO: 200 Distritos MR (67% tasa de victoria)

**Fórmula:**
```
MR_óptimo = Distritos_totales - RP_mejores_perdedores
MR_óptimo = 300 - 100 = 200 MR
```

**Por circunscripción (para 20 mejores perdedores cada una):**

| Circunscripción | Distritos Totales | MR Óptimo | Perdidos Necesarios |
|-----------------|-------------------|-----------|---------------------|
| 1ª (Guadalajara) | 61 | 41 | 20 |
| 2ª (Monterrey) | 59 | 39 | 20 |
| 3ª (Xalapa) | 60 | 40 | 20 |
| 4ª (CDMX) | 61 | 41 | 20 |
| 5ª (Toluca) | 59 | 39 | 20 |
| **TOTAL** | **300** | **200** | **100** |

## ¿Por Qué 200 MR es Óptimo?

### En 200 MR Ganados:
✅ Ganas 200 distritos → Pierdes 100 distritos  
✅ 100 pérdidas = Exactamente suficiente para 100 asientos mejores perdedores  
✅ Puedes recibir la asignación COMPLETA de ambas rondas RP  
✅ Maximiza MR manteniendo capacidad completa de mejores perdedores

### Arriba de 200 MR (ejemplo: 250):
❌ Ganas 250 → Pierdes solo 50  
❌ Solo 50 asientos de mejores perdedores posibles (no 100)  
❌ ¡Te quedas sin perdedores!

### Abajo de 200 MR (ejemplo: 150):
✅ Ganas 150 → Pierdes 150  
✅ Suficientes perdedores (150 > 100)  
❌ Pero menos asientos MR (150 < 200)  
❌ No es el total óptimo

## Tabla de Escenarios

| MR Ganados | Distritos Perdidos | MP Posibles | ¿Puede 100 MP? | Comentario |
|------------|-------------------|-------------|----------------|------------|
| 0 | 300 | 100 | ✅ SÍ | Muchos perdedores, pocos MR |
| 100 | 200 | 100 | ✅ SÍ | Aún suficientes perdedores |
| **200** | **100** | **100** | ✅ **SÍ** | ⭐ **ÓPTIMO** |
| 210 | 90 | 90 | ❌ NO | Empiezas a quedarte sin |
| 250 | 50 | 50 | ❌ NO | Insuficientes perdedores |
| 300 | 0 | 0 | ❌ NO | Sin perdedores |

## Límite Constitucional (300 Diputados Máximo)

### Restricción Adicional:
```
MR + RP_normal + RP_mejores_perdedores ≤ 300
```

### En el Punto Óptimo de 200 MR:

**Sin límite constitucional:**
- 200 MR + 100 RP normal + 100 RP mejores perdedores = 400 total

**Con límite constitucional:**
- 200 MR + 100 RP (combinado) = 300 ✅
- Debe limitarse la asignación RP total a 100

**Esto significa:**
- El límite constitucional es MÁS restrictivo que la disponibilidad de perdedores
- Óptimo real considerando límite: rango 100-200 MR

## Ejemplo Real: MORENA 2024

### Distribución MR Ganados:

| Circunscripción | Óptimo | Real MORENA | Estado | Perdidos |
|-----------------|--------|-------------|---------|----------|
| 1ª | 41 | 51 | ❌ +10 | Solo 10 |
| 2ª | 39 | 23 | ✅ OK | 36 |
| 3ª | 40 | 53 | ❌ +13 | Solo 7 |
| 4ª | 41 | 39 | ✅ OK | 22 |
| 5ª | 39 | 2 | ✅ OK | 57 |
| **TOTAL** | **200** | **168** | | **132** |

### Análisis:

**MR Ganados por MORENA (SHH): 168** (basado en datos 2024)
- Por debajo del óptimo nacional de 200
- Tiene 132 perdedores disponibles (más de 100 necesarios)
- ✅ Puede recibir asignación completa de mejores perdedores

**Pero:**
- Excedió óptimo en 2 circunscripciones (1ª y 3ª)
- Distribución desigual entre circunscripciones
- Con 168 MR + 100 MP + X RP ≤ 300 → Espacio limitado

## Trade-offs y Consideraciones

### 1. **Más MR Ganados → Menos Oportunidades de Mejores Perdedores**
- Win too much → Few losses → Can't use all MP seats
- Need balance to maximize total

### 2. **Límite Constitucional es Frecuentemente Vinculante**
- 300-seat cap is stricter than loser availability
- Must balance MR + all RP ≤ 300

### 3. **Distribución Regional Importa**
- Must consider per-circumscription performance
- Dominating some regions while weak in others creates imbalance
- Optimal requires balanced performance across all 5 circumscriptions

### 4. **Punto Óptimo Real Depende de Asignación RP**
- If total RP = 100: Optimal ~200 MR (200+100=300)
- If total RP = 200: Optimal ~100 MR (100+200=300)
- Balance depends on how RP seats are distributed

## Conclusión

### Respuesta Final:

**El punto óptimo es 200 distritos MR (67% tasa de victoria)**

- **Antes de 200 MR:** Puedes recibir asignación completa de mejores perdedores (100)
- **En 200 MR:** Exactamente en óptimo (100 pérdidas = 100 mejores perdedores)
- **Después de 200 MR:** Empiezas a quedarte sin perdedores

### Pero:

El **límite constitucional (300 total)** es frecuentemente la restricción real vinculante.

Con 200 MR + 200 RP = 400 (excede 300), así que el óptimo práctico considerando el límite constitucional está en el rango **100-200 MR** dependiendo de la asignación RP.

## Uso del Script

```bash
python analizar_punto_optimo_mr_rp_perdedores.py
```

El script genera:
- Tabla de escenarios (0-300 MR)
- Análisis de MORENA 2024
- Óptimo por circunscripción
- Impacto del límite constitucional
- Distribución regional

## Archivos Relacionados

- `analizar_punto_optimo_mr_rp_perdedores.py` - Script de análisis
- `mapeo_circunscripciones.csv` - Mapeo de estados a circunscripciones
- `data/computos_diputados_2024.parquet` - Datos electorales 2024
