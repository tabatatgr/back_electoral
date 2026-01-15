# 🔧 OPTIMIZACIONES DE MEMORIA PARA RENDER

## ⚠️ PROBLEMA DETECTADO:
- **Plan FREE Render: 512 MB RAM**
- **Uso actual estimado: 300-400 MB por request**
- **Archivo pesado: INE_SECCION_2020.csv = 50 MB**

## ✅ SOLUCIONES APLICADAS:

### 1. **Conversión CSV → Parquet** ✅
```
INE_SECCION_2020.csv:     49.89 MB
INE_SECCION_2020.parquet: 20.86 MB
REDUCCIÓN: 58.2% (29 MB ahorrados)
```

**Beneficios:**
- ✅ Carga 3-5x más rápida (parquet es binario)
- ✅ Menor uso de RAM (compresión snappy)
- ✅ No requiere parsing de texto

**Archivo modificado:**
- `redistritacion/modulos/distritacion.py` - ahora usa `.parquet` con fallback a `.csv`

### 2. **Actualizar .gitignore** ✅
Evitar subir archivos temporales y cachés:
```gitignore
__pycache__/
*.pyc
tmp_*.py
test_*.py
outputs/*.csv
```

---

## 📊 USO DE MEMORIA ESTIMADO (DESPUÉS):

```
Inicio FastAPI:
├─ Base: ~150 MB
└─ OK para FREE ✅

Request con redistritacion/:
├─ Parquet (21 MB): ~50 MB en RAM
├─ Procesamiento: 100-150 MB
└─ PICO: 200-300 MB ✅ (dentro de 512 MB)
```

---

## 🚀 RECOMENDACIONES ADICIONALES:

### Si sigue crasheando Render:

#### Opción A: Lazy imports (no cargar todo al inicio)
```python
# En lugar de importar al inicio:
# from redistritacion.modulos.distritacion import cargar_secciones_ine

# Importar solo cuando se usa:
def endpoint_que_usa_redistritacion():
    from redistritacion.modulos.distritacion import cargar_secciones_ine
    secciones = cargar_secciones_ine()
    ...
```

#### Opción B: Cache con TTL
```python
from functools import lru_cache
import time

@lru_cache(maxsize=1)
def cargar_secciones_cached():
    return cargar_secciones_ine()

# Se carga 1 vez y se reutiliza
```

#### Opción C: Subir a plan PAID ($7/mes)
- 512 MB → 2 GB RAM
- Sin sleep automático
- Deploy más rápidos

---

## 📝 CHECKLIST DEPLOY:

### Antes de hacer push:
- [x] Convertir CSV a Parquet
- [x] Actualizar código para usar Parquet
- [x] Agregar .gitignore
- [ ] Agregar Parquet al repo
- [ ] Hacer commit y push
- [ ] Verificar que Render despierte

### Comandos:
```bash
# Agregar archivos optimizados
git add redistritacion/data/INE_SECCION_2020.parquet
git add redistritacion/modulos/distritacion.py
git add .gitignore

# Commit
git commit -m "perf: optimizar memoria - CSV→Parquet (50MB→21MB)"

# Push (Render auto-deploya)
git push
```

---

## 🔍 MONITOREAR DESPUÉS DEL DEPLOY:

1. **Ver logs en Render:**
   https://dashboard.render.com → back_electoral → Logs

2. **Buscar en logs:**
   - `MemoryError` - Se quedó sin RAM
   - `503 Service Unavailable` - Crasheó
   - `Request timeout` - Tardó >30s

3. **Test rápido:**
```bash
# Ping básico
curl https://back-electoral.onrender.com/

# Endpoint pesado (usa redistritacion)
curl https://back-electoral.onrender.com/calcular/mayoria_forzada_senado?partido=MORENA&tipo_mayoria=simple
```

---

## 💡 NOTAS FINALES:

**Si el servidor sigue muriendo:**
- Es probable que otros endpoints también carguen datos pesados
- Considera migrar TODOS los CSV grandes a Parquet
- O usar SQLite/DuckDB para queries eficientes

**Archivos a revisar:**
```
data/computos_*.parquet  → Ya están en parquet ✅
data/siglado-*.csv       → Pesan poco (30 KB) ✅
redistritacion/data/INE_DISTRITO_2020.CSV → 370 KB (OK)
```

Todo listo para deploy optimizado 🚀
