# Simulación con Desglose por Partido: 300 MR + 100 PM + 100 RP

## Descripción

Esta simulación es idéntica a `simulacion_300mr_100pm_100rp` pero **desglosa los resultados por partido individual** en lugar de por coalición.

**Importante:** Los totales por coalición son exactamente los mismos que en la simulación original, garantizando consistencia.

## Sistema

**500 escaños totales:**
- 300 Mayoría Relativa (MR) - Asignados al partido específico que ganó cada distrito
- 100 Primera Minoría (PM) - Asignados al partido que quedó segundo en los 100 distritos más competitivos
- 100 Representación Proporcional (RP) - Distribuidos proporcionalmente dentro de cada coalición

## Diferencias Clave vs Simulación por Coalición

### Simulación Original (por coalición)
- MR: Asignado a la coalición ganadora
- PM: Asignado a la coalición segunda
- RP: Asignado a la coalición proporcionalmente

### Esta Simulación (por partido)
- **MR:** Asignado al **partido específico** con más votos dentro de la coalición ganadora
- **PM:** Asignado al **partido específico** con más votos dentro de la coalición segunda
- **RP:** Distribuido proporcionalmente entre partidos **dentro de cada coalición** según sus votos

## Coaliciones y Partidos

- **SHH (Sigamos Haciendo Historia):** MORENA + PT + PVEM
- **FCM (Fuerza y Corazón por México):** PAN + PRI + PRD
- **MC (Movimiento Ciudadano):** va solo

## Resultados 2024 (por partido)

| Coalición | Partido | MR | PM | RP | Total | % |
|-----------|---------|----|----|-------|-------|-----|
| **SHH** | **MORENA** | 250 | 29 | 42 | **321** | **64.2%** |
| SHH | PT | 0 | 0 | 6 | 6 | 1.2% |
| SHH | PVEM | 6 | 1 | 9 | 16 | 3.2% |
| **→ TOTAL SHH** | | **256** | **30** | **57** | **343** | **68.6%** |
| | | | | | | |
| **FCM** | **PAN** | 36 | 38 | 18 | **92** | **18.4%** |
| FCM | PRI | 7 | 14 | 12 | 33 | 6.6% |
| FCM | PRD | 0 | 0 | 2 | 2 | 0.4% |
| **→ TOTAL FCM** | | **43** | **52** | **32** | **127** | **25.4%** |
| | | | | | | |
| **MC** | **MC** | 1 | 18 | 11 | **30** | **6.0%** |

### Análisis 2024

**MORENA dominante:**
- 250 MR (ganó 250 de 300 distritos individualmente)
- 29 PM (quedó segundo en 29 distritos competitivos)
- 42 RP (mayor parte del RP de SHH)
- **321 escaños totales (64.2%)**

**PAN como principal oposición:**
- 36 MR (principal ganador de FCM)
- 38 PM (muy competitivo en segundos lugares)
- 92 escaños totales (18.4%)

**MC competitivo en PM:**
- Solo 1 MR
- 18 PM (quedó segundo en muchos distritos competitivos)
- 30 escaños totales (6.0%)

## Resultados 2021 (por partido)

| Coalición | Partido | MR | PM | RP | Total | % |
|-----------|---------|----|----|-------|-------|-----|
| **SHH** | **MORENA** | 177 | 34 | 38 | **249** | **49.8%** |
| SHH | PT | 0 | 0 | 4 | 4 | 0.8% |
| SHH | PVEM | 5 | 0 | 6 | 11 | 2.2% |
| **→ TOTAL SHH** | | **182** | **34** | **48** | **264** | **52.8%** |
| | | | | | | |
| **FCM** | **PAN** | 77 | 16 | 20 | **113** | **22.6%** |
| FCM | PRI | 33 | 41 | 20 | 94 | 18.8% |
| FCM | PRD | 1 | 3 | 4 | 8 | 1.6% |
| **→ TOTAL FCM** | | **111** | **60** | **44** | **215** | **43.0%** |
| | | | | | | |
| **MC** | **MC** | 7 | 6 | 8 | **21** | **4.2%** |

## Validación

✅ **Todos los totales por coalición coinciden exactamente:**

### 2024:
- SHH: 343 escaños (256 MR + 30 PM + 57 RP) ✅
- FCM: 127 escaños (43 MR + 52 PM + 32 RP) ✅
- MC: 30 escaños (1 MR + 18 PM + 11 RP) ✅

### 2021:
- SHH: 264 escaños (182 MR + 34 PM + 48 RP) ✅
- FCM: 215 escaños (111 MR + 60 PM + 44 RP) ✅
- MC: 21 escaños (7 MR + 6 PM + 8 RP) ✅

## Archivos

### Script
**`simular_escenario_300mr_100pm_100rp_por_partido.py`**

```bash
python simular_escenario_300mr_100pm_100rp_por_partido.py
```

### Salida
**`simulacion_300mr_100pm_100rp_por_partido.csv`**

Columnas:
- `Año` - 2021 o 2024
- `Coalición` - SHH, FCM, MC
- `Partido` - MORENA, PT, PVEM, PAN, PRI, PRD, MC
- `MR_Escaños` - Mayoría Relativa
- `PM_Escaños` - Primera Minoría
- `RP_Escaños` - Representación Proporcional
- `Total_Escaños` - Total (MR + PM + RP)
- `Porcentaje` - % del total de 500 escaños

## Metodología

### 1. Mayoría Relativa (MR)
Para cada distrito:
1. Determinar coalición ganadora (suma de votos)
2. Dentro de esa coalición, asignar MR al **partido con más votos**

Ejemplo: Si SHH gana y MORENA tiene más votos que PT y PVEM → MR a MORENA

### 2. Primera Minoría (PM)
Para los 100 distritos más competitivos (menor margen):
1. Determinar coalición segunda
2. Dentro de esa coalición, asignar PM al **partido con más votos**

Ejemplo: Si FCM queda segunda y PAN tiene más votos que PRI y PRD → PM a PAN

### 3. Representación Proporcional (RP)
1. Calcular RP por coalición (método Hare nacional)
2. Distribuir el RP de cada coalición entre sus partidos proporcionalmente a sus votos

Ejemplo: Si SHH recibe 57 RP:
- MORENA recibe la mayor parte (42) por tener más votos
- PVEM recibe 9
- PT recibe 6

## Hallazgos Clave

### Concentración del Poder
**MORENA** concentra la mayor parte de los escaños de SHH:
- 2024: 321 de 343 (93.6% de SHH)
- 2021: 249 de 264 (94.3% de SHH)

PT y PVEM dependen casi exclusivamente de RP:
- PT 2024: 0 MR, 0 PM, 6 RP = 6 total
- PVEM 2024: 6 MR, 1 PM, 9 RP = 16 total

### Competitividad de PAN
Dentro de FCM, PAN es el partido más fuerte:
- 2024: 92 de 127 escaños (72.4% de FCM)
- 2021: 113 de 215 escaños (52.6% de FCM)

### MC muy competitivo en PM
A pesar de ganar muy pocos distritos:
- 2024: 1 MR pero 18 PM (fue segundo en muchos lugares)
- 2021: 7 MR y 6 PM

## Comparación con Simulación Original

| Aspecto | Por Coalición | Por Partido |
|---------|---------------|-------------|
| **Totales** | Por coalición completa | Suma de partidos = coalición |
| **MR** | A coalición ganadora | A partido ganador en coalición |
| **PM** | A coalición segunda | A partido segundo en coalición |
| **RP** | A coalición nacional | Distribuido entre partidos |
| **Utilidad** | Vista agregada | Vista detallada |

Ambas simulaciones son complementarias y **los totales por coalición coinciden exactamente**.

## Dependencias

```bash
pip install pandas pyarrow
```

## Uso

```bash
# Generar simulación con desglose por partido
python simular_escenario_300mr_100pm_100rp_por_partido.py

# Ver resultados
cat simulacion_300mr_100pm_100rp_por_partido.csv
```

## Conclusión

Esta simulación proporciona una **visión detallada** de cómo se distribuyen los escaños entre partidos individuales, manteniendo la **consistencia total** con la simulación por coalición. Es útil para entender:

- Qué partidos realmente ganan distritos
- La concentración del poder dentro de cada coalición
- La dependencia de partidos pequeños en RP
- La competitividad real de cada partido individual
