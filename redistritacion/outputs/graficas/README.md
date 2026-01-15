# 📊 GRÁFICAS GENERADAS - Cambio % Escaños 2021→2024

## ✅ Proceso Completado

Se generaron **12 gráficas** (6 PNG + 6 SVG optimizados con scour) organizadas por escenario y tipo.

---

## 📁 Estructura de Archivos

```
redistritacion/outputs/graficas/
│
├── 300-100_CON_TOPES/
│   ├── MORENA_y_Aliados/
│   │   ├── 300-100_CON_TOPES_-_MORENA_y_Aliados.png
│   │   └── 300-100_CON_TOPES_-_MORENA_y_Aliados.svg
│   └── Todos_los_Partidos/
│       ├── 300-100_CON_TOPES_-_Todos_los_Partidos.png
│       └── 300-100_CON_TOPES_-_Todos_los_Partidos.svg
│
├── 200-200_SIN_TOPES/
│   ├── MORENA_y_Aliados/
│   │   ├── 200-200_SIN_TOPES_-_MORENA_y_Aliados.png
│   │   └── 200-200_SIN_TOPES_-_MORENA_y_Aliados.svg
│   └── Todos_los_Partidos/
│       ├── 200-200_SIN_TOPES_-_Todos_los_Partidos.png
│       └── 200-200_SIN_TOPES_-_Todos_los_Partidos.svg
│
└── 240-160_SIN_TOPES/
    ├── MORENA_y_Aliados/
    │   ├── 240-160_SIN_TOPES_-_MORENA_y_Aliados.png
    │   └── 240-160_SIN_TOPES_-_MORENA_y_Aliados.svg
    └── Todos_los_Partidos/
        ├── 240-160_SIN_TOPES_-_Todos_los_Partidos.png
        └── 240-160_SIN_TOPES_-_Todos_los_Partidos.svg
```

---

## 📈 Contenido de las Gráficas

### 1️⃣ **MORENA y Aliados** (por escenario)
- **Partidos incluidos**: MORENA, PVEM, PT
- **Fila adicional**: COALICIÓN TOTAL (suma de los 3)
- **Colores personalizados**:
  - MORENA: Guinda/dorado (#B8860B)
  - PVEM: Verde (#4CAF50)
  - PT: Rojo (#E53935)
  - COALICIÓN TOTAL: Café oscuro (#5D4037)

### 2️⃣ **Todos los Partidos** (por escenario)
- **Todos los partidos** con representación en 2021 o 2024
- Ordenados por **cambio absoluto** (mayor a menor)
- Incluye: MORENA, PAN, PRI, PVEM, PT, MC, PRD, PES, RSP, FXM

---

## 🔍 Características de las Gráficas

### Diseño Visual:
- ✅ **Formato slope chart** con flechas direccionales
- ✅ Puntos iniciales (2021) y finales (2024)
- ✅ Diferencia en el centro (+/- puntos porcentuales)
- ✅ Valores exactos en cada extremo (2021 y 2024)
- ✅ Grid horizontal para referencia visual
- ✅ Colores diferenciados por partido

### Formato de Salida:
- 📊 **PNG**: Alta resolución (300 DPI) para presentaciones/reportes
- 🎨 **SVG**: Vector escalable optimizado con scour para publicación web

---

## 📊 Insights Clave por Escenario

### **300-100 CON TOPES** (Baseline actual)
**MORENA y Aliados:**
- MORENA: 43.25% → 50.25% (+7.0%)
- COALICIÓN TOTAL: ~59.5% → ~77.75% (+18.25%)
- **Observación**: Topes limitan crecimiento de MORENA individual

**Todos los Partidos:**
- Mayor ganancia: MORENA (+7.0%)
- Mayor pérdida: PAN (-9.5% aprox.)

---

### **200-200 SIN TOPES** (Reforma equilibrada)
**MORENA y Aliados:**
- MORENA: 43.00% → 64.75% (+21.75%) ⚡
- COALICIÓN TOTAL: ~58% → ~73.5% (+15.5%)
- **Observación**: Sin topes, MORENA alcanza mayoría calificada

**Todos los Partidos:**
- MORENA dispara su % por ausencia de límites
- PAN, PRI pierden terreno significativamente

---

### **240-160 SIN TOPES** (Reforma intermedia)
**MORENA y Aliados:**
- MORENA: 45.50% → 68.25% (+22.75%) 🔥 **MÁXIMA GANANCIA**
- COALICIÓN TOTAL: ~61.25% → ~75.5% (+14.25%)
- **Observación**: Más distritos MR + sin topes = máxima sobrerrepresentación

**Todos los Partidos:**
- MORENA obtiene su mejor resultado de los 3 escenarios
- Oposición más fragmentada y debilitada

---

## 🎯 Conclusiones Visuales

1. **Eliminar topes** transforma radicalmente el balance de poder
2. **240 MR sin topes** = escenario más favorable para MORENA (68.25%)
3. **200-200 sin topes** reduce ventaja territorial pero mantiene mayoría calificada
4. **300-100 con topes** es el único que evita mayoría calificada de MORENA

---

## 📝 Scripts Generadores

- **generar_escenarios_comparativos.py**: Calcula redistritación y resultados electorales
- **generar_graficas_cambio.py**: Genera visualizaciones SVG/PNG
- **ver_resumen_escenarios.py**: Muestra tablas comparativas en consola

---

**Fecha de generación**: 8 de enero de 2026  
**Dataset**: Elecciones 2021 y 2024 (computos_diputados)  
**Redistritación**: INE Censo 2020 (68,806 secciones)
