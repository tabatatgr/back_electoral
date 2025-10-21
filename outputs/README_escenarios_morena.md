# Escenarios MORENA: Análisis de Mayorías
## Cámara de Diputados 2018-2024

Este documento explica el contenido del archivo CSV generado con escenarios de MORENA.

---

## Columnas del CSV

| Columna | Descripción |
|---------|-------------|
| `año` | Año electoral: 2018, 2021 o 2024 |
| `magnitud` | Total de escaños en la cámara: 400 o 500 |
| `configuracion` | Distribución MR/RP: "50MR_50RP" o "75MR_25RP" |
| `mr_seats` | Número de escaños de Mayoría Relativa |
| `rp_seats` | Número de escaños de Representación Proporcional |
| `escenario` | "CON_COALICION" o "SIN_COALICION" |
| `partidos_coalicion` | Partidos que integran la coalición |
| `morena_escaños` | Escaños obtenidos solo por MORENA |
| `morena_porcentaje` | Porcentaje de escaños de MORENA |
| `coalicion_escaños` | Escaños totales de la coalición (o solo MORENA) |
| `coalicion_porcentaje` | Porcentaje de escaños de la coalición |
| `mayoría_simple_morena` | ¿MORENA tiene >50% solo? (SÍ/NO) |
| `mayoría_calificada_morena` | ¿MORENA tiene ≥66.67% solo? (SÍ/NO) |
| `mayoría_simple_coalición` | ¿La coalición tiene >50%? (SÍ/NO) |
| `mayoría_calificada_coalición` | ¿La coalición tiene ≥66.67%? (SÍ/NO) |
| `umbral_mayoría_simple` | Escaños necesarios para mayoría simple |
| `umbral_mayoría_calificada` | Escaños necesarios para mayoría calificada |

---

## Resumen de Hallazgos

###  MAYORÍA SIMPLE - SOLO MORENA (>50%)

**MORENA alcanza mayoría simple SIN COALICIÓN en:**

#### 2018
- **400 escaños** (50MR/50RP): 205 escaños (51.25%)
- **400 escaños** (75MR/25RP): 205 escaños (51.25%)
- **500 escaños** (50MR/50RP): 257 escaños (51.40%)
- **500 escaños** (75MR/25RP): 257 escaños (51.40%)

#### 2021
-  **Ningún escenario** (máximo: 184/400 = 46%)

#### 2024
- **400 escaños** (50MR/50RP): 206 escaños (51.5%)
- **400 escaños** (75MR/25RP): 206 escaños (51.5%)
- **500 escaños** (50MR/50RP): 257 escaños (51.4%)
- **500 escaños** (75MR/25RP): 257 escaños (51.4%)

---

###  MAYORÍA CALIFICADA - SOLO MORENA (≥66.67%)

**MORENA NO alcanza mayoría calificada en ningún escenario sin coalición.**

---

### MAYORÍA SIMPLE - CON COALICIÓN (>50%)

**La coalición de MORENA alcanza mayoría simple en:**

#### 2018 (MORENA + PT + PES)
- Todos los escenarios 
- Mejor: **75MR/25RP en 400 escaños**: 287 (71.75%) 

#### 2021 (MORENA + PT + PVEM)
- **400 escaños** (50MR/50RP): 209 (52.25%)
- **400 escaños** (75MR/25RP): 238 (59.5%)
- **500 escaños** (50MR/50RP): 261 (52.2%)
- **500 escaños** (75MR/25RP): 258 (51.6%)

#### 2024 (MORENA + PT + PVEM)
- Todos los escenarios
- Mejor: **75MR/25RP en 400 escaños**: 314 (78.5%) 

---

### MAYORÍA CALIFICADA - CON COALICIÓN (≥66.67%)

**La coalición de MORENA alcanza mayoría calificada en:**

#### 2018
- **400 escaños** (75MR/25RP): 287 (71.75%)

#### 2024
- **400 escaños** (75MR/25RP): 314 (78.5%) 

---

## Conclusiones Clave

### MORENA Solo (Sin Coalición)

1. **2018 y 2024**: MORENA alcanza mayoría simple en TODOS los escenarios (400 y 500 escaños)
2. **2021**: MORENA NO alcanza mayoría simple en ningún escenario
3. **Ningún año**: MORENA alcanza mayoría calificada sin coalición

### Con Coalición

1. **Mayoría Calificada (2/3)**: Solo se logra en escenarios con **75% MR / 25% RP** y **400 escaños**:
   - 2018: 287/400 (71.75%)
   - 2024: 314/400 (78.5%) ← **Mejor escenario**

2. **Mejor configuración para MORENA**: 
   - **75MR/25RP + 400 escaños** maximiza escaños de la coalición

3. **Reducir cámara a 400**: 
   - Favorece a MORENA en todos los años
   - Permite alcanzar mayoría calificada con coalición en años fuertes (2018, 2024)

4. **Aumentar MR (75%)**: 
   - Beneficia más a MORENA que aumentar RP
   - Efecto más pronunciado en años de victoria amplia (2024)

---

## 📝 Notas Metodológicas

- **Umbral**: 3% (configuración estándar)
- **Método de reparto**: Hare (cuota)
- **Coaliciones**:
  - 2018: MORENA + PT + PES
  - 2021: MORENA + PT + PVEM
  - 2024: MORENA + PT + PVEM
- **Datos fuente**: Cómputos oficiales INE por distrito
- **Siglado**: Distribución oficial de escaños MR

---

**Generado**: 21 de octubre de 2025  
**Script**: `generate_escenarios_morena.py`
