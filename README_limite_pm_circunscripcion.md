# Análisis: Límite de Perdedores por Circunscripción para Asignar PM

## Pregunta

**"Si se asignan 100 PM (mejores perdedores) de acuerdo a la proporción de votos por partido... POR circunscripción... y en el total nadie puede tener más de 300 diputados... a partir de cuántos distritos ganados por circunscripción te quedas sin perdedores para acomodar?"**

## Respuesta Directa

### Fórmula General

```
Perdedores_disponibles = Distritos_en_circunscripción - MR_ganados
```

**Si quieres recibir 20 PM en una circunscripción:**

| Circunscripción | Distritos | Umbral MR | Interpretación |
|-----------------|-----------|-----------|----------------|
| 1ª (Guadalajara) | 61 | ≤ 41 | Gana hasta 41 MR → Recibes 20 PM |
| 2ª (Monterrey) | 59 | ≤ 39 | Gana hasta 39 MR → Recibes 20 PM |
| 3ª (Xalapa) | 60 | ≤ 40 | Gana hasta 40 MR → Recibes 20 PM |
| 4ª (CDMX) | 61 | ≤ 41 | Gana hasta 41 MR → Recibes 20 PM |
| 5ª (Toluca) | 59 | ≤ 39 | Gana hasta 39 MR → Recibes 20 PM |

### Conclusión

**Si ganas MÁS de estos umbrales → Te quedas sin suficientes perdedores!**

## Sistema Electoral

### Estructura de Circunscripciones

México tiene 5 circunscripciones plurinominales:

1. **1ª Circunscripción** (Guadalajara): 61 distritos
   - BC, BCS, Chihuahua, Durango, Jalisco, Nayarit, Sinaloa, Sonora

2. **2ª Circunscripción** (Monterrey): 59 distritos
   - Aguascalientes, Coahuila, Guanajuato, Nuevo León, SLP, Tamaulipas, Zacatecas

3. **3ª Circunscripción** (Xalapa): 60 distritos
   - Campeche, Chiapas, Oaxaca, Q.Roo, Tabasco, Veracruz, Yucatán

4. **4ª Circunscripción** (CDMX): 61 distritos
   - CDMX, Guerrero, Hidalgo, Morelos, Puebla, Tlaxcala

5. **5ª Circunscripción** (Toluca): 59 distritos
   - Colima, EdoMex, Michoacán, Querétaro

**Total: 300 distritos MR**

### Sistema Propuesto

- 300 MR (Mayoría Relativa)
- 100 PM (Primera Minoría / Mejores Perdedores) - Asignados por circunscripción
- Límite constitucional: Máximo 300 diputados por partido

## Caso Real: MORENA 2024

### Distribución MR de MORENA (SHH Coalition)

MORENA ganó **168 distritos MR** (coalición SHH) distribuidos como:

| Circunscripción | MR Ganados | Perdidos | PM Disponibles | ¿Suficiente para 20 PM? |
|-----------------|------------|----------|----------------|-------------------------|
| 1ª (Guadalajara) | 51 | 10 | 10 | ❌ NO (faltan 10) |
| 2ª (Monterrey) | 23 | 36 | 36 | ✅ SÍ |
| 3ª (Xalapa) | 53 | 7 | 7 | ❌ NO (faltan 13) |
| 4ª (CDMX) | 39 | 22 | 22 | ✅ SÍ |
| 5ª (Toluca) | 2 | 57 | 57 | ✅ SÍ |

### Análisis

**Total PM máximo posible para MORENA: 132**
- 1ª Circ: 10 perdedores
- 2ª Circ: 36 perdedores
- 3ª Circ: 7 perdedores
- 4ª Circ: 22 perdedores
- 5ª Circ: 57 perdedores

**Problema:** 
- MORENA domina en Circunscripciones 1ª y 3ª
- En esas 2 circunscripciones, no tiene suficientes perdedores para 20 PM
- Si se asignan PM proporcionalmente, MORENA tiene límite físico de perdedores

### Límite Constitucional (300 Total)

```
MR: 168
PM máximo (por perdedores): 132
Total: 300 diputados
```

**MORENA alcanzaría exactamente el límite constitucional con MR + PM!**

No habría espacio para RP bajo este sistema.

## Implicaciones del Sistema

### 1. Dominancia Electoral

Cuando un partido gana demasiados MR en una circunscripción:
- Se queda sin "perdedores" disponibles
- No puede recibir todos los PM que le corresponderían proporcionalmente
- Los PM deben redistribuirse a otros partidos

### 2. Redistribución Forzada

Si MORENA "debería" recibir 20 PM en Circunscripción 1ª pero solo tiene 10 perdedores:
- Opción A: Solo recibe 10 PM (su máximo físico)
- Opción B: Los 10 PM restantes van a otros partidos
- Opción C: Se cambia el sistema de asignación

### 3. Trade-off MR vs PM

Existe un trade-off natural:
- Más MR ganados → Menos perdedores disponibles → Menos PM potenciales
- El "punto óptimo" para maximizar MR+PM es ganar ~67% de los distritos

## Uso del Script

```bash
python analizar_limite_pm_por_circunscripcion.py
```

### Output

El script genera:
1. Estructura de circunscripciones
2. Análisis de perdedores disponibles por coalición/circunscripción
3. Cálculo de umbrales MR
4. Caso real MORENA 2024
5. Análisis de límite constitucional

## Archivos

- `mapeo_circunscripciones.csv` - Mapeo de estados a circunscripciones
- `analizar_limite_pm_por_circunscripcion.py` - Script de análisis
- `README_limite_pm_circunscripcion.md` - Este documento

## Conclusión

La respuesta a la pregunta original:

**Te quedas sin perdedores cuando:**
```
MR_ganados > (Distritos_circunscripción - PM_a_asignar)
```

**Para 20 PM por circunscripción:**
- Circ 1ª/4ª (61 distritos): Si ganas > 41 MR
- Circ 2ª/5ª (59 distritos): Si ganas > 39 MR  
- Circ 3ª (60 distritos): Si ganas > 40 MR

**En el caso MORENA 2024:**
- Superó el umbral en 2 de 5 circunscripciones (1ª y 3ª)
- Solo puede recibir 132 PM máximo (no 100+ proporcionales)
- Con MR+PM llegaría exactamente a 300 (límite constitucional)
