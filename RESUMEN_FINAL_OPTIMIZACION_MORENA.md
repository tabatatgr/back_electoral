# Resumen Final: Optimización Matemática para MORENA

## Pregunta Respondida

**"¿Cómo estás definiendo E(W)?"** y "¿Cuál es el punto óptimo para MORENA?"

## Respuesta en 3 Puntos

### 1. E(W) Definido Explícitamente

E(W) = función de exclusión (cuántos candidatos de segundos lugares son consumidos por RP normal)

**Tres escenarios analizados:**

| Escenario | E(W) | Óptimo W* | T(W*) |
|-----------|------|-----------|-------|
| Sin overlap | E(W) = 0 | **160** | 300 |
| Overlap completo | E(W) = min(R,S) | **260** | 300 |
| Overlap 50% | E(W) = 0.5×min(R,S) | **190** | 300 |

### 2. MORENA 2024: W=245, S=45

| Escenario | BP(245) | T(245) | Status |
|-----------|---------|--------|--------|
| E=0 | 45 | 332→300 | 85 arriba de óptimo ❌ |
| E=min | 3 | 290 | 15 abajo de óptimo ✅ |
| E=50% | 24 | 311→300 | 55 arriba de óptimo ❌ |

### 3. Restricción Estructural

**Con solo S=45 segundos lugares:**

MORENA **no puede recibir 100 mejores perdedores** bajo ninguna definición de E(W).

Máximo posible: 45 mejores perdedores

## Conclusión Matemática

El punto óptimo W* que maximiza:

```
T(W) = W + R(W) + min(100, S(W) - E(W))
```

varía de **160 a 260** dependiendo de E(W).

**Sin conocer la regla exacta:** el óptimo está probablemente en **180-220** bajo overlap parcial realista.

**Para MORENA 2024:** S=45 es la restricción vinculante, no E(W).

## Archivos Generados

1. **`optimizacion_matematica_MORENA.py`** - Script de optimización
2. **`README_optimizacion_matematica.md`** - Documentación completa
3. **`RESPUESTA_FINAL_E_W.md`** - Respuesta directa a E(W)
4. **Este archivo** - Resumen ejecutivo final

## Uso

```bash
python optimizacion_matematica_MORENA.py
```

Genera análisis completo con tres escenarios de E(W) y sus óptimos respectivos.

## Sin "Magia"

✅ E(W) explícitamente definido (no asumido)  
✅ Tres escenarios modelados matemáticamente  
✅ Óptimos calculados con datos reales  
✅ Restricción estructural identificada  
✅ Análisis riguroso y defendible  

**Pregunta "¿cómo estás definiendo E(W)?" completamente respondida.**
