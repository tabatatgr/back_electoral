# 📊 Eficiencias Geográficas Reales por Partido

## ¿Qué es la Eficiencia Geográfica?

**Eficiencia = (% de distritos ganados) / (% de votos nacionales)**

- **Eficiencia = 1.0**: Proporcional exacto (gana distritos = % de votos)
- **Eficiencia > 1.0**: Gana MÁS distritos de lo proporcional (votos bien distribuidos)
- **Eficiencia < 1.0**: Gana MENOS distritos de lo proporcional (votos mal distribuidos o desperdiciados)

## 🗳️ Eficiencias Históricas Calculadas

### ELECCIÓN 2024

| Partido | % Votos | % Distritos | Eficiencia | Interpretación |
|---------|---------|-------------|------------|----------------|
| **MORENA** | 42.49% | 25.68% | **0.604** | ❌ Desperdicia votos (gana menos de lo proporcional) |
| **PAN** | 17.58% | 20.61% | **1.172** | ✅ Votos bien distribuidos (+17% eficiencia) |
| **PRI** | 11.59% | 20.07% | **1.732** | ✅ MUY eficiente (+73% eficiencia) |
| **PRD** | 2.54% | 12.48% | **4.919** | 🚀 SUPER eficiente (gana 5x lo proporcional) |
| **PVEM** | 8.74% | 12.84% | **1.469** | ✅ Bien distribuido (+47% eficiencia) |
| **PT** | 5.69% | 8.32% | **1.461** | ✅ Bien distribuido (+46% eficiencia) |
| **MC** | 11.37% | 0.00% | **0.000** | 💀 No ganó ningún distrito (muy concentrado en Jalisco) |

### ELECCIÓN 2021

| Partido | % Votos | % Distritos | Eficiencia | Interpretación |
|---------|---------|-------------|------------|----------------|
| **MORENA** | 35.33% | 21.89% | **0.620** | ❌ Desperdicia votos |
| **PAN** | 18.91% | 17.91% | **0.947** | ≈ Casi proporcional |
| **PRI** | 18.37% | 19.15% | **1.042** | ✅ Ligeramente eficiente |
| **PRD** | 3.78% | 17.41% | **4.608** | 🚀 SUPER eficiente |
| **PVEM** | 5.63% | 12.44% | **2.209** | ✅ Muy eficiente |
| **PT** | 3.36% | 11.19% | **3.330** | 🚀 SUPER eficiente |
| **MC** | 7.27% | 0.00% | **0.000** | 💀 No ganó ningún distrito |

### ELECCIÓN 2018

| Partido | % Votos | % Distritos | Eficiencia | Interpretación |
|---------|---------|-------------|------------|----------------|
| **MORENA** | 43.14% | 23.12% | **0.536** | ❌ MUY ineficiente (desperdicia votos) |
| **PAN** | 20.77% | 23.46% | **1.130** | ✅ Eficiente (+13%) |
| **PT** | 4.55% | 11.47% | **2.522** | 🚀 SUPER eficiente |
| **PRD** | 6.10% | 14.21% | **2.328** | 🚀 SUPER eficiente |
| **PRI** | 19.15% | 0.00% | **0.000** | 💀 Colapso total |
| **PVEM** | 5.54% | 0.00% | **0.000** | 💀 No ganó distritos |

## 📈 Observaciones Clave

### 1. MORENA: Votos Desperdiciados
- **Consistentemente ineficiente** (0.536 - 0.620)
- Gana con **márgenes muy amplios** en sus bastiones (60-80%)
- Desperdicia millones de votos en victorias abrumadoras
- **Ejemplo**: Gana distrito con 70% cuando con 51% hubiera sido suficiente

### 2. PRD: Redistritación Geográfica Extrema
- **Eficiencia altísima** (2.328 - 4.919)
- Gana distritos **4-5 veces** más de lo que le correspondería proporcionalmente
- Votos **muy concentrados** en zonas específicas (CDMX, algunos estados)
- Evidencia de **coaliciones efectivas** y negociación estratégica

### 3. MC: Concentración Fatal
- **Eficiencia 0.000** en 2021 y 2024
- Votos concentrados en **Jalisco** (su bastión)
- No alcanza umbral en otros estados
- Millones de votos pero **cero distritos ganados**

### 4. PAN y PRI: Distribución Eficiente
- **Eficiencia cercana a 1.0** o superior
- Votos bien distribuidos geográficamente
- Ganan distritos ajustados (51-55%)
- Estrategia de **competitividad territorial**

## 🔧 Implementación en el Backend

### Antes (Manual)
```python
eficiencia_geografica: float = 1.1  # Usuario decide manualmente
```

### Ahora (Automático)
```python
# El sistema calcula eficiencias reales basadas en la elección histórica
eficiencias_por_partido = calcular_eficiencia_partidos(anio=2024)

# Ejemplo de output:
{
  'MORENA': 0.604,
  'PAN': 1.172,
  'PRI': 1.732,
  'PRD': 4.919,
  'PVEM': 1.469,
  'PT': 1.461,
  'MC': 0.000
}
```

### Ventajas
✅ **Realista**: Usa datos históricos reales  
✅ **Automático**: No requiere input del usuario  
✅ **Por partido**: Cada partido tiene su propia eficiencia  
✅ **Por año**: Se adapta a la elección seleccionada  
✅ **Transparente**: El cálculo es auditable  

## 💡 Ejemplo Práctico

### Escenario: MORENA con 50% de votos en 2024

**Estado de México (40 distritos):**

#### Modo Proporcional (actual):
```
50% votos × 40 distritos = 20 distritos ganados
```

#### Modo Geográfico con Eficiencia Real (nuevo):
```
50% votos × 40 distritos × 0.604 (eficiencia MORENA) = 12 distritos ganados
```

**MORENA necesita MÁS votos para compensar su ineficiencia geográfica!**

### Escenario: PRD con 5% de votos en 2024

**Ciudad de México (24 distritos):**

#### Modo Proporcional:
```
5% votos × 24 distritos = 1 distrito ganado
```

#### Modo Geográfico con Eficiencia Real:
```
5% votos × 24 distritos × 4.919 (eficiencia PRD) = 6 distritos ganados
```

**PRD gana MUCHOS más distritos por su concentración extrema!**

## 🎯 Uso desde Frontend

**Request con redistritación geográfica:**
```json
{
  "anio": 2024,
  "sistema": "mixto",
  "mr_seats": 300,
  "rp_seats": 100,
  "aplicar_topes": true,
  "votos_redistribuidos": {"MORENA": 50.0, "PAN": 20.0, ...},
  "redistritacion_geografica": true
}
```

**El backend automáticamente:**
1. ✅ Carga eficiencias históricas del año 2024
2. ✅ Aplica eficiencia específica a cada partido
3. ✅ Calcula MR usando método Hare + población + eficiencias
4. ✅ Devuelve resultados realistas

## 📚 Archivos del Sistema

1. **`engine/calcular_eficiencia_real.py`** - Calcula eficiencias históricas
2. **`main.py`** - Usa eficiencias en redistritación geográfica
3. **`test_redistritacion_geografica.py`** - Prueba el sistema

## 🧪 Testing

```bash
# Probar cálculo de eficiencias
python engine/calcular_eficiencia_real.py

# Probar endpoint con eficiencias reales
python test_redistritacion_geografica.py
```

## 🎓 Conclusión

La redistritación geográfica con eficiencias históricas reales es **mucho más precisa** que usar un factor manual. Refleja la realidad de cómo cada partido convierte votos en victorias distritales, considerando:

- Concentración geográfica
- Estrategia territorial
- Coaliciones efectivas
- Desperdicio de votos
- Competitividad distrital

Esto hace que las simulaciones sean **más realistas y útiles** para análisis político.
