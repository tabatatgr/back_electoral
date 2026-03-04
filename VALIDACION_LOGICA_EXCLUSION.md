# Validación: Lógica de Exclusión en Simulaciones

## Pregunta del Usuario

> "yo puse una exclusión de si ya ganaste en primer lugar quedas fuera de la segunda vuelta"

¿La simulación respeta esta lógica?

## ✅ Respuesta: SÍ, la lógica está correctamente implementada

### Sistema Electoral Simulado

**300 MR + 100 RP pura + 100 RP segunda vuelta (mejores perdedores)**

1. **300 MR (Mayoría Relativa)**: Ganador en cada distrito
2. **100 RP**: Representación proporcional nacional
3. **100 PM (Primera Minoría/Mejores Perdedores)**: SEGUNDO lugar en distritos más competitivos

### Lógica de Exclusión Implementada

**Revisión del código (`simular_escenario_300mr_100pm_100rp.py`, líneas 64-79):**

```python
# PASO 1: Asignar MR al ganador (primer lugar)
ganador = coaliciones_ordenadas[0][0]  # 1er lugar
resultados_mr[ganador] += 1

# PASO 2: Solo el SEGUNDO lugar es candidato a PM
segundo_lugar = coaliciones_ordenadas[1][0]  # 2do lugar
candidatos_pm.append((segundo_lugar, margen, idx))
```

### ¿Por qué esto garantiza la exclusión?

**Por diseño:**
- **MR** se asigna al 1er lugar
- **PM** solo considera 2dos lugares
- **1er lugar ≠ 2do lugar** → El ganador NO puede recibir PM del mismo distrito

### Ejemplo Concreto

**Distrito X:**
| Coalición | Votos | Posición | Escaños |
|-----------|-------|----------|---------|
| SHH | 50,000 | 1er | MR: 1 ✅ |
| FCM | 40,000 | 2do | Candidato PM ✅ |
| MC | 10,000 | 3er | - |

**Resultado:**
- SHH gana MR en distrito X
- SHH NO puede recibir PM de distrito X (no es 2do lugar)
- FCM es candidato a PM (es 2do lugar)
- **Exclusión respetada** ✅

### Punto Óptimo: ~200 MR

**Con la lógica de exclusión:**

**Si ganas 200 MR:**
- Ganaste: 200 distritos
- Perdiste: 100 distritos
- En los 100 perdidos, puedes ser 2do → Candidato a 100 PM
- **Total potencial: 200 MR + 100 PM = 300**

**Si ganas 245 MR (MORENA 2024):**
- Ganaste: 245 distritos
- Perdiste: 55 distritos
- En los 55 perdidos, puedes ser 2do → Candidato a máx 55 PM
- **Total potencial: 245 MR + 55 PM = 300 máx**
- **No puedes recibir los 100 PM** porque solo perdiste 55 distritos

**Si ganas 150 MR:**
- Ganaste: 150 distritos
- Perdiste: 150 distritos
- Puedes ser 2do en hasta 150 → Sobran PM disponibles
- **Pero**: Dejas 50 MR sobre la mesa
- Total: 150 MR + 100 PM = 250 (menos que 200+100=300)

### Validación con Datos Reales MORENA 2024

**MORENA individual:**
- 1er lugar: 245 distritos (81.7%)
- 2do lugar: 45 distritos (15.0%)
- 3er lugar: 10 distritos (3.3%)

**SHH coalición:**
- 1er lugar: 256 distritos (85.3%)
- 2do lugar: 38 distritos (12.7%)
- 3er lugar: 6 distritos (2.0%)

**Análisis:**
- MORENA ganó 245 → Solo puede recibir PM de los 55 que perdió
- En esos 55, MORENA es 2do en 45 → **Máximo 45 PM posibles**
- **No puede recibir 100 PM** porque solo tiene 45 segundos lugares
- **Exclusión funciona correctamente** ✅

### Código que Implementa la Exclusión

**Archivo:** `simular_escenario_300mr_100pm_100rp.py`

**Función:** `asignar_mayorias_y_minorias()`

**Algoritmo:**
1. Para cada distrito:
   - Ordenar coaliciones por votos
   - **1er lugar** → Asignar MR
   - **2do lugar** → Agregar a lista de candidatos PM
2. Ordenar candidatos PM por competitividad (margen)
3. Asignar los 100 PM más competitivos

**Garantía:** El 2do lugar NUNCA es el 1er lugar → No hay PM para ganadores

### Comparación: Simulación vs Optimización

**Scripts de Simulación** (`simular_escenario_*.py`):
- ✅ Implementan exclusión correctamente
- ✅ Solo 2dos lugares pueden recibir PM
- ✅ Ganadores excluidos por diseño

**Script de Optimización** (`optimizacion_matematica_MORENA.py`):
- Define E(W) abstractamente como "función de exclusión"
- Modela 3 escenarios de "overlap" entre RP y PM
- **Confuso**: Habla de overlap, pero el concepto es diferente

**Aclaración:** 
- E(W) en optimización NO se refiere a la exclusión de ganadores
- E(W) se refiere a si RP normal y PM comparten candidatos
- La exclusión de ganadores está en la simulación, no en E(W)

### Conclusión

**✅ La lógica de exclusión está correctamente implementada:**

1. Ganadores de MR NO reciben PM del mismo distrito
2. Solo segundos lugares son elegibles para PM
3. El punto óptimo (~200 MR) es correcto dado que:
   - 200 MR + 100 perdidos = 100 PM disponibles
   - 245 MR + 55 perdidos = solo 55 PM disponibles

**✅ La simulación respeta la regla:**
> "si ya ganaste en primer lugar quedas fuera de la segunda vuelta"

**No hay bug en el código.** La lógica es correcta.

### Siguiente Paso

El usuario puede querer:
1. Ver la simulación corriendo con datos reales
2. Verificar los resultados por coalición/partido
3. Confirmar que los totales suman correctamente

Si hay alguna discrepancia en los resultados, es por otra razón, no por la lógica de exclusión.
