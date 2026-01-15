# MR_DISTRITOS_MANUALES - Documentación

## Descripción

El parámetro `mr_distritos_manuales` permite especificar manualmente el número de distritos de Mayoría Relativa (MR) ganados por cada partido cuando se utiliza redistritación geográfica (`redistritacion_geografica=True`).

## Cuándo usar

- **Escenarios contrafactuales**: Simular victorias hipotéticas de partidos en diferentes escenarios
- **Proyecciones electorales**: Probar cómo cambia la composición final con diferentes resultados de MR
- **Análisis de sensibilidad**: Evaluar el impacto de cambios en MR sobre la asignación de RP
- **Validación de modelos**: Comparar resultados reales vs predicciones

## Sintaxis

```json
{
  "MORENA": 150,
  "PAN": 60,
  "PRI": 45,
  "PVEM": 25,
  "PT": 10,
  "MC": 10
}
```

**Importante**: La suma de todos los valores NO puede exceder el total de escaños MR configurados en el escenario.

## Ejemplo de uso en el endpoint

```bash
POST /procesar/diputados

{
  "anio": 2024,
  "plan": "300_100_sin_topes",
  "redistritacion_geografica": true,
  "mr_distritos_manuales": "{\"MORENA\": 200, \"PAN\": 50, \"PRI\": 30, \"PVEM\": 10, \"PT\": 5, \"MC\": 5}"
}
```

## Comportamiento

### Si `mr_distritos_manuales` está presente:

1. **Validación**: Se verifica que la suma no exceda `mr_seats`
2. **Override**: Los valores especificados sobrescriben el cálculo geográfico automático
3. **RP normal**: La asignación de RP se calcula normalmente usando el pool restante
4. **Partidos no especificados**: Reciben 0 MR

### Si `mr_distritos_manuales` NO está presente:

1. Se calcula automáticamente usando:
   - Redistritación geográfica (método Hare por población)
   - Eficiencias históricas del partido en ese año
   - Votos reales o redistribuidos por estado

## Diferencia con otros parámetros

| Parámetro | Qué modifica | Cuándo aplicar |
|-----------|--------------|----------------|
| `votos_redistribuidos` | % de votos nacionales por partido | Para cambiar la votación base |
| `mr_distritos_manuales` | Distritos MR ganados por partido | Para override específico de victorias MR |
| `redistritacion_geografica` | Método de cálculo (geo vs proporcional) | Para activar cálculo realista de MR |

## Validaciones

✅ **Permitido**:
- Total de MR <= mr_seats configurado
- Partidos no listados reciben 0 MR
- Decimales (se redondean a enteros)

❌ **Bloqueado**:
- Suma de MR > mr_seats: `HTTP 400`
- JSON inválido: `HTTP 400`
- Valores negativos: `HTTP 400`

## Casos de uso

### Caso 1: Victoria aplastante de un partido
```json
{
  "MORENA": 280,
  "PAN": 10,
  "PRI": 5,
  "MC": 5
}
```
**Resultado**: MORENA domina MR, pero RP se distribuye proporcionalmente según votos

### Caso 2: Distribución equilibrada
```json
{
  "MORENA": 100,
  "PAN": 100,
  "PRI": 50,
  "MC": 50
}
```
**Resultado**: Poder compartido en MR, RP compensa según votación

### Caso 3: Partido minoritario gana muchos distritos
```json
{
  "MC": 150,
  "MORENA": 80,
  "PAN": 40,
  "PRI": 30
}
```
**Resultado**: Simula alta eficiencia electoral de MC en distritos pequeños

## Compatibilidad con escenarios preconfigurados

| Escenario | MR disponibles | Compatible |
|-----------|----------------|------------|
| vigente | 300 | ✅ |
| plan_a | 0 | ❌ (no hay MR) |
| plan_c | 300 | ✅ |
| 300_100_con_topes | 300 | ✅ |
| 300_100_sin_topes | 300 | ✅ |
| 200_200_sin_topes | 200 | ✅ |

## Ejemplo completo

```python
import requests
import json

url = "http://localhost:8000/procesar/diputados"

# Simular que MORENA gana 200 MR (vs 245 reales en 2024)
mr_manuales = {
    "MORENA": 200,
    "PAN": 50,
    "PRI": 30,
    "PVEM": 10,
    "PT": 5,
    "MC": 5
}

payload = {
    "anio": 2024,
    "plan": "300_100_sin_topes",
    "redistritacion_geografica": True,
    "mr_distritos_manuales": json.dumps(mr_manuales)
}

response = requests.post(url, json=payload)
resultado = response.json()

print(f"MORENA MR: {resultado['mr']['MORENA']}")  # → 200 (manual)
print(f"MORENA RP: {resultado['rp']['MORENA']}")  # → Calculado por el motor
print(f"MORENA TOTAL: {resultado['tot']['MORENA']}")  # → 200 + RP
```

## Notas técnicas

1. **Formato**: Debe ser un string JSON válido (por HTTP) o dict de Python (por script directo)
2. **Prioridad**: Si está presente, SIEMPRE sobrescribe el cálculo geográfico
3. **Independencia**: No afecta el cálculo de RP (que sigue usando votos reales/redistribuidos)
4. **Redondeo**: Los valores se convierten a enteros (int())
5. **Logging**: Se registra en debug cuando se usan valores manuales

## Ejemplo de salida de debug

```
[DEBUG] ===== APLICANDO REDISTRITACIÓN GEOGRÁFICA =====
[DEBUG] Usando MR manuales: {"MORENA": 200, "PAN": 50, "PRI": 30, ...}
[DEBUG] MR manuales validados: {'MORENA': 200, 'PAN': 50, ...} (total=300/300)
```

vs

```
[DEBUG] ===== APLICANDO REDISTRITACIÓN GEOGRÁFICA =====
[DEBUG] Calculando eficiencias históricas para 2024...
[DEBUG] Eficiencias calculadas: {'MORENA': 0.604, 'PAN': 1.172, ...}
[DEBUG] Asignación de distritos por estado: {1: 3, 2: 8, 3: 2, ...}
...
[DEBUG] MR ganados con redistritación geográfica: {'MORENA': 245, ...}
```

## Ver también

- [ESCENARIOS_PRECONFIGURADOS.md](ESCENARIOS_PRECONFIGURADOS.md) - Escenarios disponibles
- [REDISTRITACION_GEOGRAFICA.md](REDISTRITACION_GEOGRAFICA.md) - Cómo funciona el cálculo automático
- [EFICIENCIAS_REALES.md](EFICIENCIAS_REALES.md) - Eficiencias históricas por partido
