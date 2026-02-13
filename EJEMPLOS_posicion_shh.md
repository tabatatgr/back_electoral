# Ejemplos Concretos: ¿Qué significa "posicion_shh"?

## Resumen Rápido

**`posicion_shh`** = En qué lugar quedó el mejor partido de SHH en el ranking de **TODOS** los partidos (no solo de SHH).

- **Posición 1** = El partido de SHH fue el **más votado** de todos
- **Posición 2** = El partido de SHH fue el **segundo más votado**
- **Posición 3** = El partido de SHH fue el **tercero más votado**
- Y así sucesivamente...

## Ejemplos Reales de los Datos

### Ejemplo 1: Posición 1 (5 distritos)

**NUEVO LEÓN, Distrito 2:**

**Por coalición (suma de partidos aliados):**
- SHH (MORENA+PT+PVEM): 68,209 votos
- **FCM (PAN+PRI+PRD): 79,337 votos** ← Ganador
- MC: 37,457 votos

**Por partido individual:**
1. **MORENA: 53,978 votos** ← Posición 1 🥇
2. MC: 37,457 votos
3. (Algún partido de FCM)
4. PT: 6,392 votos
5. PVEM: 7,839 votos

**Resultado:**
- `ganador_coalicion`: FCM
- `partido_shh_2do`: MORENA
- `posicion_shh`: **1** ← MORENA fue el partido individual con MÁS votos de todos

**¿Cómo perdió SHH si MORENA fue 1º?**
Porque aunque MORENA individualmente tuvo más votos que cualquier otro partido, la **suma** de PAN+PRI+PRD (FCM) fue mayor que la **suma** de MORENA+PT+PVEM (SHH).

---

### Ejemplo 2: Posición 2 (30 distritos)

**AGUASCALIENTES, Distrito 1:**

**Por coalición:**
- SHH: 90,589 votos
- **FCM: 109,134 votos** ← Ganador
- MC: 15,288 votos

**Por partido individual (estimado):**
1. (Algún partido de FCM, probablemente PAN): ~60,000 votos
2. **MORENA: 72,219 votos** ← Posición 2 🥈
3. Otro partido
4. ...

**Resultado:**
- `ganador_coalicion`: FCM
- `partido_shh_2do`: MORENA
- `posicion_shh`: **2** ← MORENA fue el segundo partido con más votos

---

### Ejemplo 3: Posición 3 (7 distritos)

**JALISCO, Distrito 2:**

**Por coalición:**
- SHH: 52,937 votos
- FCM: 60,474 votos
- **MC: 61,009 votos** ← Ganador

**Por partido individual:**
1. **MC: 61,009 votos** ← MC es partido único, no coalición
2. (Algún partido de FCM): ~35,000 votos
3. **MORENA: 41,015 votos** ← Posición 3 🥉
4. PT: 4,188 votos
5. PVEM: 7,734 votos

**Resultado:**
- `ganador_coalicion`: MC
- `partido_shh_2do`: MORENA
- `posicion_shh`: **3** ← MORENA fue el tercer partido con más votos

---

### Ejemplo 4: El único caso de PVEM (San Luis Potosí D5)

**SAN LUIS POTOSÍ, Distrito 5:**

**Por coalición:**
- SHH: 90,179 votos
- **FCM: 102,448 votos** ← Ganador
- MC: 18,644 votos

**Por partido individual (estimado):**
1. (Algún partido de FCM): ~55,000 votos
2. **PVEM: 45,519 votos** ← Posición 2 🥈
3. MORENA: 39,474 votos
4. PT: 5,186 votos
5. ...

**Resultado:**
- `ganador_coalicion`: FCM
- `partido_shh_2do`: **PVEM** ← ¡Único distrito donde PVEM > MORENA!
- `posicion_shh`: **2**

---

## Distribución General

De los 44 distritos donde SHH perdió:

| Posición | Distritos | Significado |
|----------|----------:|-------------|
| 1º lugar | 5 (11.4%) | El partido de SHH tuvo más votos que CUALQUIER otro partido |
| 2º lugar | 30 (68.2%) | Solo 1 partido tuvo más votos que el mejor de SHH |
| 3º lugar | 7 (15.9%) | Dos partidos tuvieron más votos que el mejor de SHH |
| 4º lugar | 2 (4.5%) | Tres partidos tuvieron más votos que el mejor de SHH |

## Conclusión

**posicion_shh** te dice **qué tan competitivo** fue el mejor partido de SHH:

- Si `posicion_shh = 1`: Muy competitivo (fue el partido más votado)
- Si `posicion_shh = 2`: Competitivo (quedó segundo)
- Si `posicion_shh = 3 o 4`: Menos competitivo (quedó en lugares más bajos)

En **todos** los casos, la coalición SHH perdió, pero la posición individual nos dice qué tan cerca estuvo el partido más fuerte de SHH de ganar.
