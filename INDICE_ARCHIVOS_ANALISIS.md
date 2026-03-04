# 📁 ÍNDICE DE ARCHIVOS - ANÁLISIS ELECTORAL

Todos los archivos están en el directorio raíz del repositorio: `/home/runner/work/back_electoral/back_electoral/`

## 📊 ARCHIVOS PRINCIPALES DE ANÁLISIS

### 1. Análisis de Segundos Lugares (Primera Minoría)

**Script:**
- `analizar_segundos_lugares_coalicion.py` (5.0K) - Análisis de segundos lugares en distritos perdidos por SHH

**CSV:**
- `analisis_segundos_lugares_shh.csv` (4.1K) - 44 distritos donde SHH perdió, quién quedó 2º

**Documentación:**
- `README_analisis_segundos_lugares.md` (4.6K)
- `EJEMPLOS_posicion_shh.md` (3.7K)

---

### 2. Simulaciones Electorales (300 MR + 100 PM + 100 RP)

#### A) Por Coalición

**Script:**
- `simular_escenario_300mr_100pm_100rp.py` (12K)

**CSV:**
- `simulacion_300mr_100pm_100rp.csv` (236 bytes) - Resultados por coalición (SHH, FCM, MC)

**Documentación:**
- `README_simulacion_300mr_100pm_100rp.md` (3.9K)
- `RESUMEN_SIMULACION.txt` (7.6K)
- `RECORDATORIO_SIMULACION_300MR_100PM_100RP.md` (3.9K)

**Resultados 2024:**
- SHH: 343 escaños (MR:256, PM:30, RP:57)
- FCM: 127 escaños (MR:43, PM:52, RP:32)
- MC: 30 escaños (MR:1, PM:18, RP:11)

#### B) Por Partido Individual (manteniendo totales de coalición)

**Script:**
- `simular_escenario_300mr_100pm_100rp_por_partido.py` (16K)

**CSV:**
- `simulacion_300mr_100pm_100rp_por_partido.csv` (480 bytes) - Desglose MORENA, PT, PVEM, PAN, PRI, PRD, MC

**Output:**
- `simulacion_partido_output.txt` (7.1K)

**Documentación:**
- `README_simulacion_por_partido.md` (6.7K)

**Resultados 2024:**
- MORENA: 321 escaños (MR:250, PM:29, RP:42)
- PT: 6 escaños (MR:0, PM:0, RP:6)
- PVEM: 16 escaños (MR:6, PM:1, RP:9)

#### C) Todos los Partidos (incluyendo PES, RSP, FXM, CI)

**Script:**
- `simular_escenario_300mr_100pm_100rp_todos_partidos.py` (16K)

**CSV:**
- `simulacion_300mr_100pm_100rp_todos_partidos.csv` (760 bytes) - Incluye partidos menores

**Output:**
- `simulacion_todos_partidos_output.txt` (8.2K)

**Documentación:**
- `README_simulacion_todos_partidos.md` (6.9K)

---

### 3. Análisis de Límites (MR vs PM)

#### A) Límite Nacional (300 distritos)

**Script:**
- `analizar_limite_mr_pm.py` (8.1K)

**CSV:**
- `analisis_limite_mr_pm.csv` (369 bytes) - Escenarios 0-300 MR

**Documentación:**
- `README_analisis_limite_mr_pm.md` (5.8K)
- `RESPUESTA_LIMITE_MR_PM.txt` (3.2K)

**Respuesta:** Límite superior = 200 MR para recibir 100 PM completos

#### B) Límite por Circunscripción

**Script:**
- `analizar_limite_pm_por_circunscripcion.py` (7.6K)

**CSV:**
- `mapeo_circunscripciones.csv` (494 bytes) - Estados → Circunscripciones

**Documentación:**
- `README_limite_pm_circunscripcion.md` (5.0K)
- `RESPUESTA_LIMITE_PM_CIRCUNSCRIPCION.txt` (5.2K)
- `VISUAL_LIMITE_PERDEDORES.txt` (9.4K)

**Respuesta:** Por circunscripción, límite es ~39-41 MR para recibir 20 PM

---

### 4. Punto Óptimo (Sistema de Dos Vueltas RP)

#### A) Análisis Inicial

**Script:**
- `analizar_punto_optimo_mr_rp_perdedores.py` (9.9K)

**Documentación:**
- `README_punto_optimo_mr_rp.md` (5.4K)
- `RESPUESTA_FINAL_PUNTO_OPTIMO.txt` (7.6K)

#### B) Sistema Correcto (Segundos Lugares)

**Script:**
- `analizar_segundos_lugares_sistema_correcto.py` (8.9K)

**CSV:**
- `analisis_primeros_segundos_lugares_2024.csv` (12K) - 300 distritos con 1º, 2º, 3º

**Documentación:**
- `README_sistema_correcto_mejores_perdedores.md` (5.8K)

#### C) Análisis MORENA Solo (NO coalición)

**Script:**
- `analizar_punto_optimo_MORENA_solo.py` (incluido en sistema correcto)

**CSV:**
- `analisis_MORENA_solo_2024.csv` (generado si se ejecuta script)

**Documentación:**
- `EXPLICACION_ANALISIS_MORENA_SOLO.md` (incluido)
- `EXPLICACION_ANALISIS_PUNTO_OPTIMO.md` (7.3K)

---

### 5. Optimización Matemática Rigurosa (con E(W) formal)

**Script:**
- `optimizacion_matematica_MORENA.py` (12K) - ⭐ ANÁLISIS MÁS RIGUROSO

**Documentación:**
- `README_optimizacion_matematica.md` (5.6K)
- `RESPUESTA_FINAL_E_W.md` (2.9K)
- `RESUMEN_FINAL_OPTIMIZACION_MORENA.md` (2.1K)

**Define E(W) en tres escenarios:**
1. E(W) = 0 → Optimal W* = 160
2. E(W) = min(R,S) → Optimal W* = 260
3. E(W) = 0.5×min(R,S) → Optimal W* = 190

---

### 6. Desglose MR/PM/RP

**Documentación:**
- `DESGLOSE_MR_PM_RP.md` (7.4K) - Tablas detalladas de distribución

---

### 7. Correcciones y Aclaraciones

- `CORRECCION_CRITICA_256.md` (4.6K) - Explica 256 distritos vs escaños totales
- `CONFIRMACION_256_DISTRITOS_SON_CORRECTOS.md` (si existe) - Confirma números
- `CORRECCION_CRITICA_DISTRITOS_VS_ESCAÑOS.md` (si existe)

---

### 8. Resúmenes Ejecutivos

- `RESUMEN_EJECUTIVO_ANALISIS.md` (si existe) - Párrafo explicativo
- `EXPLICACION_ANALISIS_PUNTO_OPTIMO.md` (7.3K) - Explicación completa

---

### 9. Guías de Descarga

- `DONDE_ESTAN_LOS_CSV.md` (6.9K) - Guía de ubicación de CSVs
- `LISTA_CSV.txt` (4.7K) - Lista simple de CSVs

---

## 📈 RESUMEN DE RESULTADOS CLAVE

### MORENA 2024 (Individual, NO coalición)

**Distritos MR:**
- 1er lugar: 245 distritos (81.7%)
- 2do lugar: 45 distritos (15.0%)
- 3er lugar: 10 distritos (3.3%)

**Punto Óptimo (depende de E(W)):**
- E(W) = 0: Optimal = 160 MR
- E(W) = min(R,S): Optimal = 260 MR
- E(W) = 0.5×min(R,S): Optimal = 190 MR

**MORENA actual:**
- W = 245 MR
- Arriba del óptimo en escenarios E=0 y E=50%
- Cerca del óptimo en escenario E=min(R,S)

**Restricción estructural:**
- Solo 45 segundos lugares
- Máximo 45 mejores perdedores posibles (no 100)
- Independiente de E(W)

---

## 🔍 ARCHIVOS POR PREGUNTA

### "¿En cuántos quedó cada partido en 2º lugar?"
→ `analisis_segundos_lugares_shh.csv`

### "¿Simulación 300MR + 100PM + 100RP?"
→ `simulacion_300mr_100pm_100rp.csv` (coalición)
→ `simulacion_300mr_100pm_100rp_por_partido.csv` (partido)

### "¿Y el PES y los independientes?"
→ `simulacion_300mr_100pm_100rp_todos_partidos.csv`

### "¿Desglose de MR/PM/RP?"
→ `DESGLOSE_MR_PM_RP.md`

### "¿Límite superior de distritos MR?"
→ `analisis_limite_mr_pm.csv`
→ `README_analisis_limite_mr_pm.md`

### "¿Punto óptimo con dos vueltas RP?"
→ `optimizacion_matematica_MORENA.py` ⭐
→ `README_optimizacion_matematica.md`

### "¿Cómo estás definiendo E(W)?"
→ `RESPUESTA_FINAL_E_W.md`
→ `optimizacion_matematica_MORENA.py`

---

## 🎯 ARCHIVO RECOMENDADO PARA EMPEZAR

**Para análisis completo y riguroso:**
```bash
python optimizacion_matematica_MORENA.py
```

Lee: `README_optimizacion_matematica.md`

**Para entender el concepto:**
Lee: `RESUMEN_FINAL_OPTIMIZACION_MORENA.md`

**Para resultados rápidos:**
Lee: `RESPUESTA_FINAL_E_W.md`

---

## 📥 CÓMO DESCARGAR

**Desde GitHub:**
1. Ve a: https://github.com/tabatatgr/back_electoral
2. Encuentra el archivo
3. Click en "Raw" o botón de descarga

**Desde clon local:**
```bash
cd /home/runner/work/back_electoral/back_electoral
ls *.csv    # Ver CSVs
ls *.py     # Ver scripts
ls *.md     # Ver documentación
```

---

## 🧮 FÓRMULA CLAVE

```
T(W) = W + R(W) + min(100, S(W) - E(W))

Donde:
- W = Distritos MR ganados por MORENA
- R(W) = RP normal (~42 para MORENA)
- S(W) = Segundos lugares de MORENA
- E(W) = Exclusión (definida en 3 escenarios)
- T(W) = Total escaños

Restricción: T(W) ≤ 300
```

---

## 🎓 CONCLUSIÓN MATEMÁTICA

El punto óptimo para MORENA está acotado en [160, 260] dependiendo de E(W), probablemente en [180, 220] bajo overlap parcial realista. MORENA 2024 con W=245 y S=45 tiene restricción estructural S<100 que impide capturar 100 mejores perdedores bajo cualquier E(W).

---

**Todos los archivos están en el directorio raíz del repositorio.**
