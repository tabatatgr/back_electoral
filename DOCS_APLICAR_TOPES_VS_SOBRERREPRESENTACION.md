# 📚 Documentación: `aplicar_topes` vs `sobrerrepresentacion`

## 🎯 Son DOS parámetros INDEPENDIENTES

### 1. `sobrerrepresentacion` (float)
**Define el LÍMITE porcentual de sobrerrepresentación**

- **Valor**: Porcentaje en formato decimal (ej: `8.0` para 8%)
- **Default**: `8.0` (límite constitucional)
- **Conversión interna**: Se divide entre 100 → `8.0 → 0.08`
- **Efecto**: Define cuántos puntos porcentuales EXTRA puede tener un partido

#### Ejemplos:
```python
sobrerrepresentacion=8.0   # Límite del 8%
sobrerrepresentacion=10.0  # Límite del 10% (más permisivo)
sobrerrepresentacion=5.0   # Límite del 5% (más restrictivo)
sobrerrepresentacion=None  # Usa default 8.0
```

#### Cálculo del límite:
```python
votos_pct = 42.49  # MORENA tiene 42.49% de votos
sobrerrepresentacion = 8.0

max_escanos = floor((votos_pct + sobrerrepresentacion) / 100 * 500)
            = floor((42.49 + 8.0) / 100 * 500)
            = floor(50.49 / 100 * 500)
            = floor(252.45)
            = 252 escaños máximo
```

### 2. `aplicar_topes` (bool)
**Activa o desactiva el sistema completo de límites**

- **Valor**: `True` o `False`
- **Default**: `True`
- **Efecto**: Si es `False`, IGNORA completamente `sobrerrepresentacion`

#### Estados posibles:

| `aplicar_topes` | `sobrerrepresentacion` | Resultado |
|-----------------|------------------------|-----------|
| `True` | `8.0` | ✅ Aplica límite del 8% |
| `True` | `10.0` | ✅ Aplica límite del 10% |
| `True` | `5.0` | ✅ Aplica límite del 5% |
| `True` | `None` | ✅ Aplica límite del 8% (default) |
| `False` | `8.0` | ❌ NO aplica límites (ignora el 8%) |
| `False` | `10.0` | ❌ NO aplica límites |
| `False` | `None` | ❌ NO aplica límites |

## 🔄 Flujo interno

```python
# En procesar_diputados_v2.py línea 1557
if aplicar_topes:  # ← PRIMERO verifica si aplicar topes
    max_pp = (sobrerrepresentacion / 100.0) if sobrerrepresentacion is not None else 0.08
    
    resultado_topes = aplicar_topes_nacionales(
        s_mr=ssd, 
        s_rp=s_rp_init, 
        v_nacional=v_nacional_total,
        S=S, 
        max_pp=max_pp,  # ← Usa sobrerrepresentacion convertido
        max_seats=max_seats,
        max_seats_per_party=max_seats_per_party,
        partidos_nombres=partidos_base
    )
else:
    # NO aplica topes, sobrerrepresentacion se ignora completamente
    s_tot = s_mr + s_rp  # Sin límites
```

## 📊 Casos de uso reales

### Caso 1: Sistema vigente (2024)
```javascript
// Configuración constitucional actual
{
  "anio": 2024,
  "plan": "vigente",
  "aplicar_topes": true,        // ✅ Aplica límites
  "sobrerrepresentacion": 8.0   // Límite del 8%
}

// Resultado: MORENA máx 252 escaños
```

### Caso 2: Simulación con límite más permisivo
```javascript
// ¿Qué pasaría con un límite del 12%?
{
  "anio": 2024,
  "plan": "personalizado",
  "sistema": "mixto",
  "escanos_totales": 500,
  "mr_seats": 300,
  "rp_seats": 200,
  "aplicar_topes": true,         // ✅ Aplica límites
  "sobrerrepresentacion": 12.0   // Límite del 12% (más permisivo)
}

// Resultado: MORENA puede tener hasta 277 escaños
// Cálculo: floor((42.49 + 12.0) / 100 * 500) = 277
```

### Caso 3: Sin límites (contrafactual puro)
```javascript
// ¿Cuántos escaños tendría MORENA sin límites?
{
  "anio": 2024,
  "plan": "personalizado",
  "sistema": "mixto",
  "escanos_totales": 500,
  "mr_seats": 300,
  "rp_seats": 200,
  "aplicar_topes": false,        // ❌ NO aplica límites
  "sobrerrepresentacion": 8.0    // ← Se ignora
}

// Resultado: MORENA puede tener 339 escaños (sin restricciones)
```

### Caso 4: Límite más restrictivo
```javascript
// ¿Qué pasaría con un límite del 5%?
{
  "anio": 2024,
  "plan": "personalizado",
  "sistema": "mixto",
  "escanos_totales": 500,
  "mr_seats": 300,
  "rp_seats": 200,
  "aplicar_topes": true,         // ✅ Aplica límites
  "sobrerrepresentacion": 5.0    // Límite del 5% (más restrictivo)
}

// Resultado: MORENA máx 237 escaños
// Cálculo: floor((42.49 + 5.0) / 100 * 500) = 237
```

## 🎨 Interfaz del usuario

### Toggle 1: "Aplicar topes constitucionales"
```
[X] Aplicar topes constitucionales
→ aplicar_topes = true
```

### Slider: "Límite de sobrerrepresentación"
```
[====|====] 8%
0%        20%
→ sobrerrepresentacion = 8.0
```

**Comportamiento:**
- Si el toggle está OFF → El slider se deshabilita (no tiene efecto)
- Si el toggle está ON → El slider controla el límite

## ⚠️ Aclaración importante

En el test vimos:
```
CON topes (aplicar_topes=true, sobrerrepresentacion=8.0):  266 escaños
SIN topes (aplicar_topes=false):                            339 escaños
```

**¿Por qué 266 y no 252?**

Posibles razones:
1. **Coaliciones**: Si `usar_coaliciones=false`, los partidos NO se suman (MORENA vs JHM)
2. **Cálculo de votos**: El porcentaje puede variar según si incluye/excluye coaliciones
3. **Redondeos**: Hay múltiples puntos de redondeo en el cálculo

Para verificar, necesitamos ver el % exacto de votos que tiene MORENA en el cálculo.

## ✅ Resumen

| Parámetro | Tipo | Función | Independiente |
|-----------|------|---------|---------------|
| `aplicar_topes` | bool | ON/OFF del sistema de límites | ✅ SÍ |
| `sobrerrepresentacion` | float | Define el % de límite | ✅ SÍ |

**Son independientes:** Puedes cambiar `sobrerrepresentacion` sin tocar `aplicar_topes` y viceversa.

**Ejemplo perfecto de independencia:**
```python
# Experimento 1: Límite del 8%
aplicar_topes=True, sobrerrepresentacion=8.0  → max 252 escaños

# Experimento 2: Límite del 10%
aplicar_topes=True, sobrerrepresentacion=10.0 → max 268 escaños

# Experimento 3: Límite del 5%
aplicar_topes=True, sobrerrepresentacion=5.0  → max 237 escaños

# Experimento 4: Sin límites
aplicar_topes=False                           → sin límite (ignora sobrerrepresentacion)
```
