# 📚 Índice de Documentación - Escenarios Electorales

## Proyecto: Análisis Electoral MORENA 2018-2024 + Swing Electoral

Este índice conecta toda la documentación generada para el análisis de escenarios electorales y el cálculo de swing electoral basado en elecciones locales.

---

## 📊 Documentos Principales

### 1. [README_escenarios_morena.md](./README_escenarios_morena.md)
**Documento maestro con análisis completo**

📄 **Contenido**:
- Explicación de columnas del CSV
- Escenarios 2021 con SWING electoral (metodología completa)
- Tablas comparativas 2021 vs 2021_CON_SWING
- Resumen de mayorías por año (2018, 2021, 2024)
- Conclusiones sobre impacto del swing
- Notas metodológicas detalladas
- Referencias a archivos relacionados

🎯 **Usar cuando**: Necesites la visión completa del proyecto con todas las configuraciones, resultados y metodología.

---

### 2. [RESUMEN_SWING_ELECTORAL.txt](./RESUMEN_SWING_ELECTORAL.txt)
**Resumen ejecutivo en texto plano**

📄 **Contenido**:
- Datos procesados (8 estados, 43 distritos)
- Comparación visual 2021 vs 2021_CON_SWING (4 configuraciones)
- Hallazgos clave sobre impacto del swing
- Casos especiales documentados (Coahuila, México, Quintana Roo)
- Conclusión sobre robustez de resultados 2021

🎯 **Usar cuando**: Necesites un resumen ejecutivo rápido para presentaciones o reportes.

---

### 3. [INVESTIGACION_OUTLIERS_SWING.md](../INVESTIGACION_OUTLIERS_SWING.md)
**Investigación técnica de anomalías en datos de swing**

📄 **Contenido**:
- **Caso 1**: Coahuila PT +3,797% (rotación PT-MORENA)
  - Análisis distrito por distrito
  - Comparación swing individual vs coalición
  - Código Python para corrección
- **Caso 2**: México -100% en 4 partidos (coalición completa)
  - Estructura de columnas CSV
  - Recomendaciones de tratamiento
- **Caso 3**: Quintana Roo PVEM/MC +200% (crecimiento real)
  - Validación de datos
  - Simulación de impacto en escaños

🎯 **Usar cuando**: Necesites entender por qué ciertos estados tienen tratamiento especial o investigar datos anómalos.

---

## 📁 Archivos de Datos

### CSV Generados

#### [escenarios_morena_20251022_171034.csv](./escenarios_morena_20251022_171034.csv) ⭐ **ACTUAL**
**32 escenarios completos** (24 base + 8 con swing)

**Estructura**:
- **2018**: 8 escenarios (400/500 escaños × 50-50/75-25 MR-RP × con/sin coalición)
- **2021**: 8 escenarios (misma estructura)
- **2021_CON_SWING**: 8 escenarios (votos ajustados con swing electoral)
- **2024**: 8 escenarios (misma estructura)

**Columnas clave**:
- `año`, `magnitud`, `configuracion`, `mr_seats`, `rp_seats`
- `escenario`, `partidos_coalicion`
- `morena_escaños`, `coalicion_escaños`
- `mayoría_simple_morena`, `mayoría_calificada_morena`
- `mayoría_simple_coalición`, `mayoría_calificada_coalición`
- `nota` (explicación metodológica para escenarios con swing)

---

### Archivos de Swing (Directorio raíz)

#### swing_con_coaliciones_20251022_155610.csv
**83 distritos con datos de swing** (individual + coaliciones)

**Columnas**:
- `ENTIDAD`, `DF_2021` (código estado, número distrito)
- Swing individual: `swing_PAN`, `swing_PRI`, `swing_PRD`, `swing_PVEM`, `swing_PT`, `swing_MC`, `swing_MORENA`
- Swing coaliciones: `swing_JUNTOS_PT_MORENA`, `swing_VA_X_MEX_PAN_PRI_PRD`

**Estados incluidos**: AGS, COAH, DGO, HGO, MEX, OAX, QROO, TAMPS

---

#### swing_para_api.csv
**Formato simplificado para integración en API**

**Uso**: Endpoint `/api/swing?entidad=XX&distrito=Y`

---

#### tabla_equivalencia_seccion_df.csv
**Mapeo geográfico sección → distrito federal**

**Registros**: 18,322 secciones
**Uso**: Validar mapeo INEGI entre secciones electorales y distritos federales

---

## 🔧 Scripts de Generación

### Scripts Principales

| Script | Propósito | Output |
|--------|-----------|--------|
| `generate_escenarios_morena.py` | Generar 32 escenarios completos | `escenarios_morena_*.csv` |
| `calcular_swing.py` | Calcular swing electoral inicial | `swings_por_df_*.csv` |
| `recalcular_swing_coaliciones.py` | Agregar swing de coaliciones | `swing_con_coaliciones_*.csv` |
| `investigar_outliers_swing.py` | Detectar y analizar anomalías | `outliers_detectados.csv` |
| `usar_swing.py` | Clase SwingElectoral para integración | (módulo Python) |

---

## 📈 Resultados Clave

### Impacto del Swing Electoral

| Configuración | 2021 Sin Swing | 2021 Con Swing | Diferencia |
|---------------|----------------|----------------|------------|
| **400 escaños 50-50** | Coalición 209 (52.25%) | Coalición 208 (52.0%) | **-1 escaño** |
| **400 escaños 75-25** | MORENA 173 (43.25%) | MORENA 171 (42.75%) | **-2 escaños** |
| **500 escaños 50-50** | Coalición 261 (52.2%) | Coalición 261 (52.2%) | Sin cambio |
| **500 escaños 75-25** | Coalición 258 (51.6%) | Coalición 258 (51.6%) | Sin cambio |

**Conclusión**: Impacto mínimo. La coalición mantiene mayoría simple en todos los escenarios.

---

### Mayorías Alcanzadas (Todos los Años)

#### MORENA Solo
- ✅ **2018**: Mayoría simple en todos los escenarios
- ❌ **2021**: NO alcanza mayoría simple (máx. 46%)
- ❌ **2021_CON_SWING**: NO alcanza mayoría simple (máx. 46%)
- ✅ **2024**: Mayoría simple en todos los escenarios

#### Coalición
- ✅ **2018**: Mayoría simple en todos + mayoría calificada en 400/75-25 (71.75%)
- ✅ **2021**: Mayoría simple en todos (52-59%)
- ✅ **2021_CON_SWING**: Mayoría simple en todos (52-59%)
- ✅ **2024**: Mayoría simple en todos + mayoría calificada en 400/75-25 (78.5%)

---

## 🎓 Metodología

### Swing Electoral

**Fórmula**:
```
Swing = (Votos_Locales_2022/23 - Votos_Federales_2021) / Votos_Federales_2021 × 100
```

**Proceso**:
1. Mapear 18,322 secciones → 84 distritos federales (shapefiles INEGI)
2. Agregar votos locales y federales por distrito
3. Calcular swing por partido y por coalición
4. Identificar y corregir outliers (Coahuila, México)
5. Aplicar swing a votos 2021 con factor de confianza
6. Generar escenarios 2021_CON_SWING

**Limitaciones**:
- Cobertura parcial: 43 distritos de 300 (14.3%)
- Contexto diferente: Elecciones locales vs federales
- Temporalidad: 1-2 años de diferencia

---

## 🔍 Casos de Uso

### Para Analistas Políticos
→ Consultar [README_escenarios_morena.md](./README_escenarios_morena.md) sección "Resumen de Hallazgos"

### Para Desarrolladores de API
→ Usar `usar_swing.py` (clase SwingElectoral) y `swing_para_api.csv`

### Para Investigadores
→ Revisar [INVESTIGACION_OUTLIERS_SWING.md](../INVESTIGACION_OUTLIERS_SWING.md) para validación metodológica

### Para Presentaciones Ejecutivas
→ Usar [RESUMEN_SWING_ELECTORAL.txt](./RESUMEN_SWING_ELECTORAL.txt) y tablas comparativas

---

## 📞 Contacto y Mantenimiento

**Última actualización**: 22 de octubre de 2025  
**Versión**: 1.0  
**Scripts**: `generate_escenarios_morena.py` + suite de análisis de swing

---

## ⚠️ Notas Importantes

1. **Archivo CSV actual**: `escenarios_morena_20251022_171034.csv` (32 escenarios)
2. **Archivos anteriores**: `escenarios_morena_20251022_170220.csv` (24 escenarios, sin swing) - **OBSOLETO**
3. **Swing de coaliciones**: Siempre preferir sobre swing individual para PT+MORENA en COAH/DGO/HGO/OAX
4. **México**: No aplicar swing individual a PVEM/PT/MC/MORENA (usar solo si hay coalición agregada)
5. **Factor de confianza**: 0.7 para partidos pequeños (PVEM, MC) en estados con crecimiento extremo

---

**🎯 Siguiente paso recomendado**: Leer [README_escenarios_morena.md](./README_escenarios_morena.md) para visión completa del proyecto.
