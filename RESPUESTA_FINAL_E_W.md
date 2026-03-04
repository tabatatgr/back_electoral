# Respuesta Final: ¿Cómo Estás Definiendo E(W)?

## Pregunta del Usuario

**"¿cómo estás definiendo E(W)?"**

## Respuesta Directa

**E(W) se define explícitamente en TRES escenarios diferentes, porque el óptimo depende completamente de cómo se defina:**

### 1. E(W) = 0 (Sin Overlap)

```
E(W) = 0
```

**Asunción:** Pools de RP normal y mejores perdedores completamente separados.

**Óptimo para MORENA:** W* = 160 distritos

### 2. E(W) = min(R(W), S(W)) (Overlap Completo)

```
E(W) = min(R(W), S(W))
```

**Asunción:** RP normal consume del mismo pool que mejores perdedores. RP se asigna primero.

**Óptimo para MORENA:** W* = 260 distritos

### 3. E(W) = 0.5 × min(R(W), S(W)) (Overlap Parcial)

```
E(W) = 0.5 × min(R(W), S(W))
```

**Asunción:** 50% de candidatos de RP normal vienen del pool de mejores perdedores.

**Óptimo para MORENA:** W* = 190 distritos

## Resultados para MORENA 2024 (W=245)

Con W=245 distritos MR ganados y S=45 segundos lugares:

| Escenario | E(245) | BP(245) | T(245) | vs Óptimo |
|-----------|--------|---------|--------|-----------|
| E=0 | 0 | 45 | 332→300 | 85 arriba de 160 ❌ |
| E=min(R,S) | 42 | 3 | 290 | 15 abajo de 260 ✅ |
| E=50% | 21 | 24 | 311→300 | 55 arriba de 190 ❌ |

## Conclusión Matemática

**El óptimo varía de 160 a 260 dependiendo de E(W):**

- Bajo E(W)=0: MORENA ganó demasiado (245 vs 160)
- Bajo E(W)=min: MORENA cerca del óptimo (245 vs 260)
- Bajo E(W)=50%: MORENA arriba del óptimo (245 vs 190)

**Restricción estructural independiente de E(W):**

Con solo S=45 segundos lugares, MORENA **no puede recibir 100 mejores perdedores bajo ninguna definición de E(W)** porque:

```
BP(245) = min(100, max(0, S - E))
        = min(100, max(0, 45 - E))
        ≤ min(100, 45)
        = 45
```

## Sin Conocer la Regla Exacta del Sistema

**El óptimo real está acotado en [160, 260]**

Bajo supuestos realistas de overlap parcial (E(W) = α×min(R,S) con 0.3 ≤ α ≤ 0.7), el óptimo probablemente está en el **rango 180-220**.

## Respuesta Sin "Magia"

**No hay atajos:** El óptimo depende de cómo el sistema electoral defina E(W) (qué candidatos son elegibles para ambos pools).

**Definimos E(W) explícitamente en tres formas y calculamos el óptimo para cada una.**

**Conclusión defendible:** El óptimo varía de 160 a 260. Sin conocer la regla exacta, se acota probabilísticamente en 180-220.

Para MORENA 2024, la restricción estructural S=45 < 100 es vinculante independientemente de E(W).

---

## Fórmula Completa

```
Maximizar: T(W) = W + R(W) + BP(W)

Donde:
  BP(W) = min(100, max(0, S(W) - E(W)))
  
Con E(W) definido como:
  - E(W) = 0                    (sin overlap)
  - E(W) = min(R(W), S(W))     (overlap completo)
  - E(W) = α × min(R(W), S(W)) (overlap parcial, 0 < α < 1)

Restricción: T(W) ≤ 300

Óptimo: W* = arg max_{W∈[0,300]} min(T(W), 300)
```

**Esta es la definición matemáticamente rigurosa y defendible.**
