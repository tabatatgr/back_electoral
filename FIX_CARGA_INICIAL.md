# 🔧 Fix: Carga Inicial de Datos (Diputados y Senado)

## ❌ Problemas Identificados

1. **No había datos de "quién ganó" al cargar**: El endpoint `/data/initial` no incluía la distribución geográfica (`mr_por_estado`, `distritos_por_estado`)
2. **Senado no funcionaba**: No había soporte para cargar datos iniciales del Senado
3. **Sin manera de cambiar cámara**: Frontend no podía solicitar datos de Senado fácilmente

## ✅ Solución Implementada

### 1. Endpoint Mejorado: `/data/initial`

**Antes:**
```http
GET /data/initial
→ Solo Diputados, sin datos geográficos
```

**Ahora:**
```http
GET /data/initial?camara=diputados
GET /data/initial?camara=senadores
→ Ambas cámaras con datos geográficos completos
```

### 2. Cambios en el Backend

**Archivo:** `main.py` (líneas 275-350)

**Mejoras:**
- ✅ Parámetro `camara` opcional (`"diputados"` por default)
- ✅ Soporta ambas cámaras: `"diputados"` y `"senadores"`
- ✅ Devuelve datos geográficos completos en `meta`
- ✅ Validación automática y logging detallado
- ✅ Manejo de errores mejorado

**Datos Incluidos en la Respuesta:**

```json
{
  "seat_chart": [...],
  "mr": {...},
  "rp": {...},
  "tot": {...},
  "meta": {
    "mr_por_estado": {
      "AGUASCALIENTES": {"MORENA": 2, "PAN": 1, ...},
      "BAJA CALIFORNIA": {"MORENA": 7, "PAN": 1, ...},
      ...
    },
    "distritos_por_estado": {      // Para Diputados
      "AGUASCALIENTES": 3,
      "BAJA CALIFORNIA": 8,
      ...
    },
    "senadores_por_estado": {      // Para Senado
      "AGUASCALIENTES": 3,
      "BAJA CALIFORNIA": 3,
      ...
    }
  },
  "mayorias": {...},
  "config_inicial": {
    "anio": 2024,
    "camara": "diputados",
    "plan": "vigente",
    "total_escanos": 500,
    "mr_escanos": 300,
    "rp_escanos": 200
  }
}
```

## 📋 Qué Debe Hacer el Frontend

### 1. Actualizar Llamada Inicial

**Antes:**
```javascript
fetch('/data/initial')
```

**Ahora:**
```javascript
// Para Diputados
fetch('/data/initial?camara=diputados')

// Para Senado
fetch('/data/initial?camara=senadores')
```

### 2. Procesar Datos Geográficos

```javascript
const response = await fetch('/data/initial?camara=diputados');
const data = await response.json();

// IMPORTANTE: Usar los datos de meta
const mrPorEstado = data.meta.mr_por_estado;
const distritosPorEstado = data.meta.distritos_por_estado;

// Renderizar tabla geográfica
renderTablaGeografica(mrPorEstado, distritosPorEstado);
```

### 3. Ejemplo Completo

```jsx
function App() {
  const [camara, setCamara] = useState('diputados');
  const [datos, setDatos] = useState(null);
  
  useEffect(() => {
    async function cargar() {
      const res = await fetch(`/data/initial?camara=${camara}`);
      const data = await res.json();
      setDatos(data);
    }
    cargar();
  }, [camara]);
  
  return (
    <div>
      <select value={camara} onChange={e => setCamara(e.target.value)}>
        <option value="diputados">Diputados</option>
        <option value="senadores">Senado</option>
      </select>
      
      {datos && (
        <>
          <SeatChart data={datos.seat_chart} />
          <TablaGeografica 
            mrPorEstado={datos.meta.mr_por_estado}
            totalPorEstado={
              camara === 'diputados' 
                ? datos.meta.distritos_por_estado 
                : datos.meta.senadores_por_estado
            }
          />
        </>
      )}
    </div>
  );
}
```

## 🧪 Testing

Ejecutar test:
```bash
python test_data_initial.py
```

**Verificaciones:**
- ✅ Diputados devuelve 32 estados con 300 distritos totales
- ✅ Senado devuelve 32 estados con 96 senadores totales (3 por estado)
- ✅ Coherencia: suma de `mr_por_estado` = total en `mr`
- ✅ Default es Diputados
- ✅ Rechaza cámaras inválidas con HTTP 400

## 📚 Documentación Adicional

- **Guía Frontend**: `GUIA_FRONTEND_CARGA_INICIAL.md` - Ejemplos completos de implementación
- **Test**: `test_data_initial.py` - Validación automática del endpoint
- **Sliders por Partido**: `DOCS_SLIDERS_DISTRITOS_POR_PARTIDO.md` - Cómo usar sliders para ajustar MR manualmente

## 🎯 Siguiente Paso

El frontend debe:

1. **Actualizar llamada inicial** a `/data/initial?camara=diputados`
2. **Leer datos geográficos** de `meta.mr_por_estado` y `meta.distritos_por_estado`
3. **Renderizar tabla geográfica** mostrando quién ganó en cada estado
4. **Agregar selector de cámara** para cambiar entre Diputados/Senado

## ✅ Checklist Backend

- [x] Endpoint `/data/initial` mejorado
- [x] Soporte para `camara=diputados`
- [x] Soporte para `camara=senadores`
- [x] Datos geográficos incluidos en `meta`
- [x] Validación y logging
- [x] Tests creados
- [x] Documentación completa

## 📊 Ejemplo de Logs del Backend

```
[INFO] Cargando datos iniciales: Diputados 2024 vigente
[INFO] ✅ mr_por_estado presente con 32 estados
[INFO] ✅ distritos_por_estado presente: 300 distritos totales
[INFO] Datos iniciales de diputados cargados exitosamente
```

---

**Status**: ✅ **LISTO PARA FRONTEND**

El backend está completamente funcional y devuelve todos los datos necesarios. El frontend solo necesita actualizar la llamada y procesar los nuevos datos de `meta`.
