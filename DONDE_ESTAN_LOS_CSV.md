# 📂 ¿DÓNDE ESTÁN LOS CSV? - Guía de Archivos Generados

## 🎯 CSVs Principales (Los que probablemente buscas)

### 1️⃣ Análisis de Segundos Lugares (Primera Minoría)
**📄 Archivo:** `analisis_segundos_lugares_shh.csv`
- **Qué contiene:** Análisis de los 44 distritos donde perdió la coalición SHH (MORENA+PT+PVEM)
- **Columnas:** entidad, distrito, ganador_coalicion, segundo_lugar, votos por partido
- **Tamaño:** 4.1 KB
- **Script que lo genera:** `analizar_segundos_lugares_coalicion.py`

```bash
# Ver el archivo
cat analisis_segundos_lugares_shh.csv

# Regenerar
python analizar_segundos_lugares_coalicion.py
```

---

### 2️⃣ Simulación 300 MR + 100 PM + 100 RP (Por Coalición)
**📄 Archivo:** `simulacion_300mr_100pm_100rp.csv`
- **Qué contiene:** Simulación electoral por COALICIÓN (SHH, FCM, MC)
- **Años:** 2021 y 2024
- **Columnas:** Año, Coalición, MR_Escaños, PM_Escaños, RP_Escaños, Total_Escaños, Porcentaje
- **Tamaño:** 236 bytes (6 filas)
- **Script que lo genera:** `simular_escenario_300mr_100pm_100rp.py`

```bash
# Ver el archivo
cat simulacion_300mr_100pm_100rp.csv

# Regenerar
python simular_escenario_300mr_100pm_100rp.py
```

**Resultados 2024:**
- SHH: 343 escaños (68.6%)
- FCM: 127 escaños (25.4%)
- MC: 30 escaños (6.0%)

---

### 3️⃣ Simulación 300 MR + 100 PM + 100 RP (Por Partido)
**📄 Archivo:** `simulacion_300mr_100pm_100rp_por_partido.csv`
- **Qué contiene:** Simulación electoral DESGLOSADA por PARTIDO individual
- **Años:** 2021 y 2024
- **Partidos:** MORENA, PT, PVEM, PAN, PRI, PRD, MC
- **Columnas:** Año, Coalición, Partido, MR_Escaños, PM_Escaños, RP_Escaños, Total_Escaños, Porcentaje
- **Tamaño:** 480 bytes (14 filas)
- **Script que lo genera:** `simular_escenario_300mr_100pm_100rp_por_partido.py`

```bash
# Ver el archivo
cat simulacion_300mr_100pm_100rp_por_partido.csv

# Regenerar
python simular_escenario_300mr_100pm_100rp_por_partido.py
```

**Resultados 2024 (principales):**
- MORENA: 321 escaños (64.2%)
- PAN: 92 escaños (18.4%)
- MC: 30 escaños (6.0%)

---

### 4️⃣ Simulación COMPLETA con TODOS los Partidos (incluye PES, RSP, FXM, CI)
**📄 Archivo:** `simulacion_300mr_100pm_100rp_todos_partidos.csv`
- **Qué contiene:** Simulación electoral incluyendo TODOS los partidos que tuvieron votos
- **Años:** 2021 y 2024
- **Partidos 2021:** MORENA, PT, PVEM, PAN, PRI, PRD, MC, PES, RSP, FXM, CI (11 total)
- **Partidos 2024:** MORENA, PT, PVEM, PAN, PRI, PRD, MC (7 total, los menores tienen 0 votos)
- **Columnas:** Año, Coalición, Partido, MR_Escaños, PM_Escaños, RP_Escaños, Total_Escaños, Porcentaje
- **Tamaño:** 760 bytes (22 filas)
- **Script que lo genera:** `simular_escenario_300mr_100pm_100rp_todos_partidos.py`

```bash
# Ver el archivo
cat simulacion_300mr_100pm_100rp_todos_partidos.csv

# Regenerar
python simular_escenario_300mr_100pm_100rp_todos_partidos.py
```

**Nota:** PES, RSP, FXM y CI tienen 0 escaños (no alcanzaron umbral 3% para RP)

---

### 5️⃣ Análisis de Límite MR para Primera Minoría
**📄 Archivo:** `analisis_limite_mr_pm.csv`
- **Qué contiene:** Tabla mostrando el límite superior de distritos MR para recibir PM
- **Columnas:** MR_ganados, Distritos_perdidos, PM_potencial, PM_completo, Total_potencial
- **Tamaño:** 369 bytes
- **Script que lo genera:** `analizar_limite_mr_pm.py`

```bash
# Ver el archivo
cat analisis_limite_mr_pm.csv

# Regenerar
python analizar_limite_mr_pm.py
```

**Respuesta clave:** El límite para recibir los 100 PM completos es **200 MR**

---

## 📊 Otros CSVs (Análisis Anteriores)

### Simulaciones de Escenarios
- `simulacion_escenarios_20260126_114856.csv` (605 bytes)
- `simulacion_escenarios_20260126_115905.csv` (605 bytes)
- `simulacion_escenarios_20260126_155754.csv` (758 bytes)

### Comparaciones de Métodos
- `comparacion_MR_scale_vs_getmax_20260108_184106.csv` (1.4K)
- `comparacion_MR_scale_vs_getmax_20260108_184320.csv` (1.4K)
- `comparacion_MR_vs_RP_distrital_20260108_185021.csv` (1.4K)
- `comparacion_RP_nacional_vs_RP_distrital_20260108_185416.csv` (1.4K)

---

## 🚀 Cómo Descargar

### Si estás en GitHub:
1. Ve al repositorio: `https://github.com/tabatatgr/back_electoral`
2. Navega a la raíz del repositorio
3. Busca el archivo CSV que necesitas
4. Haz clic en el archivo
5. Haz clic en el botón "Raw" o "Download"

### Si estás en local (clonaste el repo):
```bash
# Los archivos están en la raíz del repositorio
cd back_electoral

# Ver lista de CSVs
ls -lh *.csv

# Copiar a tu carpeta de descargas
cp analisis_segundos_lugares_shh.csv ~/Downloads/
cp simulacion_300mr_100pm_100rp.csv ~/Downloads/
cp simulacion_300mr_100pm_100rp_por_partido.csv ~/Downloads/
cp simulacion_300mr_100pm_100rp_todos_partidos.csv ~/Downloads/
```

### Si estás usando la terminal:
```bash
# Ver el contenido directo
cat analisis_segundos_lugares_shh.csv

# Abrir en Excel/LibreOffice
libreoffice --calc simulacion_300mr_100pm_100rp.csv

# En Mac
open simulacion_300mr_100pm_100rp.csv
```

---

## 📖 Documentación Relacionada

Cada CSV tiene su documentación:

| CSV | README |
|-----|--------|
| `analisis_segundos_lugares_shh.csv` | `README_analisis_segundos_lugares.md` |
| `simulacion_300mr_100pm_100rp.csv` | `README_simulacion_300mr_100pm_100rp.md` |
| `simulacion_300mr_100pm_100rp_por_partido.csv` | `README_simulacion_por_partido.md` |
| `simulacion_300mr_100pm_100rp_todos_partidos.csv` | `README_simulacion_todos_partidos.md` |
| `analisis_limite_mr_pm.csv` | `README_analisis_limite_mr_pm.md` |

---

## 🔄 Regenerar CSVs

Si quieres regenerar cualquier CSV con datos actualizados:

```bash
# Instalar dependencias
pip install pandas pyarrow

# Análisis de segundos lugares
python analizar_segundos_lugares_coalicion.py

# Simulación por coalición
python simular_escenario_300mr_100pm_100rp.py

# Simulación por partido
python simular_escenario_300mr_100pm_100rp_por_partido.py

# Simulación con todos los partidos
python simular_escenario_300mr_100pm_100rp_todos_partidos.py

# Análisis de límite MR-PM
python analizar_limite_mr_pm.py
```

---

## 📞 Resumen Rápido

**¿Quieres ver los resultados electorales principales?**
→ `simulacion_300mr_100pm_100rp.csv`

**¿Quieres ver cómo le fue a cada partido?**
→ `simulacion_300mr_100pm_100rp_por_partido.csv`

**¿Quieres ver PES y candidatos independientes?**
→ `simulacion_300mr_100pm_100rp_todos_partidos.csv`

**¿Quieres ver dónde perdió MORENA?**
→ `analisis_segundos_lugares_shh.csv`

**¿Quieres saber el límite de MR para PM?**
→ `analisis_limite_mr_pm.csv`

---

## 💡 Tip

Todos los CSVs principales están en la **raíz del repositorio**, no en subcarpetas.

```
back_electoral/
├── analisis_segundos_lugares_shh.csv ✅
├── simulacion_300mr_100pm_100rp.csv ✅
├── simulacion_300mr_100pm_100rp_por_partido.csv ✅
├── simulacion_300mr_100pm_100rp_todos_partidos.csv ✅
└── analisis_limite_mr_pm.csv ✅
```

¡Todos listos para descargar! 🎉
