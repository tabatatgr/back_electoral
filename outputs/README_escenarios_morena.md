# Escenarios MORENA: Análisis de Mayorías
## Cámara de Diputados 2018-2024 + Swing Electoral 2022-2023

Este documento explica el contenido del archivo CSV generado con escenarios de MORENA, incluyendo proyecciones ajustadas por swing electoral basadas en elecciones locales.

---

## Columnas del CSV

| Columna | Descripción |
|---------|-------------|
| `año` | Año electoral: 2018, 2021, 2021_CON_SWING o 2024 |
| `magnitud` | Total de escaños en la cámara: 400 o 500 |
| `configuracion` | Distribución MR/RP: "50MR_50RP" o "75MR_25RP" |
| `mr_seats` | Número de escaños de Mayoría Relativa |
| `rp_seats` | Número de escaños de Representación Proporcional |
| `escenario` | "CON_COALICION", "SIN_COALICION", "CON_COALICION_Y_SWING" o "SIN_COALICION_CON_SWING" |
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
| `nota` | Nota metodológica (aparece en escenarios con swing) |

---

## 🔄 Escenarios 2021 con SWING Electoral

Los escenarios **2021_CON_SWING** aplican ajustes basados en el desempeño electoral en **elecciones locales 2022-2023** vs **elecciones federales 2021**.

### Metodología del Swing

**Fórmula**: `Swing = (Votos_Locales - Votos_Federales) / Votos_Federales × 100`

**Cobertura**:
- **43 distritos ajustados** de 300 (14.3%)
- **8 estados con datos**: Aguascalientes, Coahuila, Durango, Hidalgo, México, Oaxaca, Quintana Roo, Tamaulipas
- **257 distritos sin datos**: Mantienen votos originales de 2021

### Casos Especiales Documentados

1. **Coahuila**: Rotación PT-MORENA dentro de coalición
   - PT individual: +3,797% (outlier por cambio de candidaturas)
   - Coalición PT+MORENA: +34.5% → **Se usa swing de coalición (-11.1%)**
   
2. **México**: Coalición completa en elecciones locales
   - Sin desglose individual de PVEM, PT, MC, MORENA en CSV local
   - **Se mantienen votos federales 2021 sin ajuste**

3. **Quintana Roo**: Crecimiento real validado
   - PVEM: +198%, MC: +183%
   - **Se aplica con factor de confianza 0.7**

### Comparación: 2021 vs 2021_CON_SWING

#### 400 escaños | 50MR-50RP
| Escenario | MORENA solo | Coalición | Mayoría |
|-----------|-------------|-----------|---------|
| 2021 (sin swing) | 184 (46.0%) | 209 (52.25%) | ✓ Simple |
| 2021_CON_SWING | 184 (46.0%) | 208 (52.0%) | ✓ Simple |
| **Diferencia** | 0 | **-1 escaño (-0.25pp)** | Sin cambio |

#### 400 escaños | 75MR-25RP
| Escenario | MORENA solo | Coalición | Mayoría |
|-----------|-------------|-----------|---------|
| 2021 (sin swing) | 173 (43.25%) | 238 (59.5%) | ✓ Simple |
| 2021_CON_SWING | 171 (42.75%) | 238 (59.5%) | ✓ Simple |
| **Diferencia** | **-2 escaños (-0.5pp)** | 0 | Sin cambio |

#### 500 escaños | 50MR-50RP
| Escenario | MORENA solo | Coalición | Mayoría |
|-----------|-------------|-----------|---------|
| 2021 (sin swing) | 230 (46.0%) | 261 (52.2%) | ✓ Simple |
| 2021_CON_SWING | 230 (46.0%) | 261 (52.2%) | ✓ Simple |
| **Diferencia** | 0 | 0 | Sin cambio |

#### 500 escaños | 75MR-25RP
| Escenario | MORENA solo | Coalición | Mayoría |
|-----------|-------------|-----------|---------|
| 2021 (sin swing) | 230 (46.0%) | 258 (51.6%) | ✓ Simple |
| 2021_CON_SWING | 230 (46.0%) | 258 (51.6%) | ✓ Simple |
| **Diferencia** | 0 | 0 | Sin cambio |

### 📊 Conclusión del Swing

**Impacto del swing electoral: MÍNIMO**

- Cambios de **-1 a -2 escaños** (máximo -0.5 puntos porcentuales)
- La coalición **mantiene mayoría simple (>50%)** en todos los escenarios
- Swing promedio **ligeramente negativo** en los 8 estados analizados
- El ajuste refleja un **pequeño retroceso local vs federal 2021**

**Interpretación**: Los datos de elecciones locales 2022-2023 no alteran sustancialmente el panorama de 2021. La coalición MORENA-PT-PVEM mantuvo su base electoral en los estados analizados.

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

#### 2021_CON_SWING (MORENA + PT + PVEM + ajuste electoral local)
- **400 escaños** (50MR/50RP): 208 (52.0%) → -1 vs 2021
- **400 escaños** (75MR/25RP): 238 (59.5%) → Sin cambio
- **500 escaños** (50MR/50RP): 261 (52.2%) → Sin cambio
- **500 escaños** (75MR/25RP): 258 (51.6%) → Sin cambio

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

### Configuración General
- **Umbral**: 3% (configuración estándar)
- **Método de reparto**: Hare (cuota)
- **Coaliciones**:
  - 2018: MORENA + PT + PES
  - 2021: MORENA + PT + PVEM
  - 2021_CON_SWING: MORENA + PT + PVEM (votos ajustados)
  - 2024: MORENA + PT + PVEM
- **Datos fuente**: Cómputos oficiales INE por distrito
- **Siglado**: Distribución oficial de escaños MR

### Swing Electoral (2021_CON_SWING)

#### Fuentes de Datos
- **Elecciones locales**: Gubernaturas 2022 (AGS, DGO, HGO, OAX, QROO, TAMPS) y 2023 (COAH, MEX)
- **Elecciones federales**: Diputados federales 2021
- **Shapefiles**: INEGI Marco Geoelectoral 2024 (SECCION.shp con columnas ENTIDAD, SECCION, DISTRITO_F)

#### Proceso de Cálculo
1. **Mapeo geográfico**: 18,322 secciones electorales → 84 distritos federales
2. **Agregación**: Sumar votos locales y federales por distrito
3. **Cálculo swing**: `(Votos_Local - Votos_Fed_2021) / Votos_Fed_2021 × 100`
4. **Ajuste de votos 2021**: Aplicar swing a 43 distritos con datos
5. **Simulación**: Ejecutar procesar_diputados_v2() con votos ajustados

#### Tratamiento Especial
- **Coahuila/Durango/Hidalgo/Oaxaca**: Usar swing de coalición PT+MORENA (evita outliers por rotación)
- **México**: Sin ajuste individual (solo coalición en datos locales)
- **Otros estados**: Aplicar swing individual × factor_confianza=0.7

#### Limitaciones
- **Cobertura parcial**: Solo 14.3% de distritos (43/300)
- **Temporalidad**: 1-2 años de diferencia entre elecciones
- **Contexto diferente**: Elecciones locales vs federales (temas, candidatos distintos)

#### Validación
- Outlier Coahuila PT +3,797%: Explicado por rotación intracoalición → Corregido
- México -100% en 4 partidos: Coalición completa en local → Excluido
- Quintana Roo PVEM/MC +200%: Crecimiento real validado → Aplicado con prudencia

---

## 📂 Archivos Relacionados

- **Escenarios CSV**: `outputs/escenarios_morena_20251022_171034.csv` (32 escenarios)
- **Swing por distrito**: `swing_con_coaliciones_20251022_155610.csv` (83 distritos)
- **Investigación outliers**: `INVESTIGACION_OUTLIERS_SWING.md`
- **Script generación**: `generate_escenarios_morena.py`
- **Script swing**: `calcular_swing.py`, `recalcular_swing_coaliciones.py`
- **Utilidad integración**: `usar_swing.py` (clase SwingElectoral)

---

**Generado**: 22 de octubre de 2025  
**Script**: `generate_escenarios_morena.py`  
**Total escenarios**: 32 (24 base + 8 con swing electoral)
