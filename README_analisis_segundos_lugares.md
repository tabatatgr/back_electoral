# Análisis de Segundos Lugares en Distritos Perdidos por SHH

## ¿Qué hace este análisis?

Este script analiza los **44 distritos donde la coalición SHH (MORENA+PT+PVEM) perdió** en las elecciones de 2024, y determina **cuál de los 3 partidos de la coalición quedó mejor posicionado individualmente** en cada uno de esos distritos.

## Archivos

- **Script:** `analizar_segundos_lugares_coalicion.py`
- **Resultado:** `analisis_segundos_lugares_shh.csv`

## ¿Qué significa "posicion_shh"?

`posicion_shh` indica **en qué lugar quedó el partido de SHH mejor posicionado en el ranking de TODOS los partidos** (no solo de SHH).

### Ejemplos:

#### Posición 1 (1er lugar individual)
En **5 distritos**, aunque la coalición SHH perdió, el partido individual de SHH quedó en **1er lugar**:

```
NUEVO LEÓN, Distrito 2: MORENA obtuvo 53,978 votos (1º individual)
  - Ganó FCM como coalición (79,337 votos)
  - Pero MORENA individualmente tuvo más votos que cualquier otro partido
  - MC individual: 37,457 votos
```

**¿Cómo es posible?** La coalición SHH (MORENA+PT+PVEM) sumó menos que FCM (PAN+PRI+PRD), pero MORENA individualmente superó a todos los partidos individuales.

#### Posición 2 (2do lugar individual)
En **30 distritos**, el mejor partido de SHH quedó en **2do lugar** individualmente:

```
AGUASCALIENTES, Distrito 1: MORENA obtuvo 72,219 votos (2º individual)
  - Ganó FCM como coalición
  - Algún partido de FCM (PAN, PRI o PRD) tuvo más votos que MORENA
  - MORENA quedó en segundo lugar individual
```

#### Posición 3 (3er lugar individual)
En **7 distritos**, el mejor partido de SHH quedó en **3er lugar** individualmente:

```
JALISCO, Distrito 2: MORENA obtuvo 41,015 votos (3º individual)
  - Ganó MC como coalición (61,009 votos)
  - MC individual también tuvo 61,009 votos (1º)
  - Algún partido de FCM quedó 2º
  - MORENA quedó en tercer lugar individual
```

#### Posición 4 (4to lugar individual)
En **2 distritos**, el mejor partido de SHH quedó en **4to lugar** individualmente.

## Concepto Clave: Coalición vs. Partido Individual

**Importante:** Hay una diferencia entre:

1. **Ganador por coalición**: Suma de votos de partidos aliados
   - SHH = MORENA + PT + PVEM
   - FCM = PAN + PRI + PRD
   - MC = MC (solo)

2. **Ranking individual**: Cada partido por separado
   - Ejemplo: MORENA, PT, PVEM, PAN, PRI, PRD, MC

### Caso Real: NUEVO LEÓN, Distrito 2

**Por coalición:**
- FCM: 79,337 votos ← **Ganador**
- SHH: 68,209 votos
- MC: 37,457 votos

**Por partido individual:**
1. MORENA: 53,978 votos ← **1er lugar individual**
2. MC: 37,457 votos
3. (Algún partido de FCM)
4. PT: 6,392 votos
5. PVEM: 7,839 votos

**Conclusión:** FCM ganó como coalición, pero MORENA fue el partido individual con más votos.

## Columnas del CSV

| Columna | Descripción |
|---------|-------------|
| `entidad` | Estado |
| `distrito` | Número de distrito |
| `ganador_coalicion` | Coalición ganadora (FCM o MC) |
| `partido_shh_2do` | Partido de SHH mejor posicionado (MORENA, PT o PVEM) |
| `posicion_shh` | Posición del partido SHH en el ranking de TODOS los partidos (1, 2, 3, 4...) |
| `votos_morena` | Votos individuales de MORENA |
| `votos_pt` | Votos individuales de PT |
| `votos_pvem` | Votos individuales de PVEM |
| `votos_shh_total` | Total de votos de la coalición SHH |
| `votos_fcm_total` | Total de votos de la coalición FCM |
| `votos_mc_total` | Total de votos de MC |

## Resultados Principales

De los 44 distritos donde SHH perdió:

- **MORENA** fue el partido mejor posicionado en **43 distritos (97.7%)**
- **PVEM** fue el partido mejor posicionado en **1 distrito (2.3%)**
  - San Luis Potosí, Distrito 5: PVEM 45,519 votos vs MORENA 39,474 votos
- **PT** no fue el mejor posicionado en ningún distrito **(0.0%)**

### Distribución de Posiciones

| Posición | Cantidad de Distritos |
|----------|----------------------:|
| 1º lugar | 5 |
| 2º lugar | 30 |
| 3º lugar | 7 |
| 4º lugar | 2 |
| **Total** | **44** |

## Uso

```bash
# Ejecutar el análisis
python analizar_segundos_lugares_coalicion.py

# Ver el CSV
cat analisis_segundos_lugares_shh.csv
```

## Interpretación

Este análisis es útil para entender:

1. **Fortaleza individual vs. coalición**: En algunos distritos, MORENA es fuerte individualmente pero la coalición pierde
2. **Concentración de votos**: MORENA concentra casi todos los votos de SHH en distritos perdidos
3. **Competitividad**: En 5 distritos, MORENA fue 1º individual pero SHH perdió como coalición
4. **Partido más competitivo**: MORENA es claramente el partido más fuerte de SHH (97.7%)
