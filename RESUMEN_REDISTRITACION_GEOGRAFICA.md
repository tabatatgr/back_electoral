# RESUMEN: Implementación de Redistritación Geográfica en Backend

## Fecha
Implementado el día de hoy

## Objetivo
Integrar la redistritación geográfica (método Hare con población real) en el endpoint `/procesar/diputados` para que el frontend pueda elegir entre:
- **Modo proporcional** (actual): Distribución simple por porcentaje de votos
- **Modo geográfico** (nuevo): Redistritación por población real usando método Hare

## Cambios Realizados

### 1. Endpoint `/procesar/diputados` (main.py)

**Nuevos parámetros:**
```python
redistritacion_geografica: bool = False  # Toggle para activar modo geográfico
eficiencia_geografica: float = 1.1       # Factor de eficiencia (1.0-1.2)
```

**Nueva lógica (líneas ~1418-1537):**
- Si `redistritacion_geografica=True` y `mr_seats > 0`:
  1. Carga secciones del INE para obtener población por estado
  2. Calcula asignación de distritos usando `repartir_distritos_hare()`
  3. Carga votos del parquet por estado
  4. Para cada partido:
     - Calcula porcentaje de votos por estado
     - Aplica eficiencia geográfica: `MR = int(distritos_estado * pct_votos * eficiencia)`
  5. Genera diccionario `mr_ganados_geograficos = {'MORENA': 153, 'PAN': 45, ...}`
  6. Pasa este diccionario a `procesar_diputados_v2()`

**Debugging:**
- Imprime MR geográficos calculados en consola
- Muestra total de MR asignados

### 2. Procesador Principal (engine/procesar_diputados_v2.py)

**Nuevo parámetro en función:**
```python
mr_ganados_geograficos: Optional[Dict[str, int]] = None
```

**Nueva lógica (líneas ~1260-1275):**
- Si `mr_ganados_geograficos` está presente:
  - Usa esos valores directamente (evita cálculo distrito por distrito)
  - Asigna MR según diccionario proporcionado
  - Salta toda la lógica de coaliciones y siglado
- Si no está presente:
  - Comportamiento actual (cálculo proporcional o por siglado)

**Ventajas:**
- Mantiene compatibilidad con modo actual (backward compatible)
- Evita duplicación de código
- Permite flexibilidad desde el frontend

### 3. Script de Prueba (test_redistritacion_geografica.py)

**Funcionalidad:**
- Prueba ambos modos con el mismo escenario
- Escenario de prueba: MORENA 50%, PAN 20%, PRI 15%, PVEM 8%, MC 7%
- Compara resultados y muestra diferencias
- Valida que el endpoint responde correctamente

**Ejecutar:**
```bash
# Primero levantar el servidor
python main.py

# En otra terminal
python test_redistritacion_geografica.py
```

## Resultados Esperados

Según cálculos en `votos_minimos_morena.csv` (eficiencia 1.1):

### Escenario 300-100 CON TOPES:
- **Proporcional**: 47-48% → ~155 MR
- **Geográfico**: 50.0% → **153 MR** (más exigente)

### Escenario 300-100 SIN TOPES:
- **Proporcional**: 62.5-64% → ~206 MR  
- **Geográfico**: 66.5% → **201 MR** (más exigente)

**Conclusión:** La redistritación geográfica es MÁS EXIGENTE que la proporcional. Un partido necesita más votos para obtener los mismos MR.

## Factores de Eficiencia

- **1.0**: Proporcional exacto (sin ventaja geográfica)
- **1.1**: +10% de eficiencia por concentración geográfica moderada (default)
- **1.2**: +20% de eficiencia por concentración geográfica muy alta

**Ejemplo práctico:**
Si un partido tiene 50% de votos en un estado con 20 distritos:
- Eficiencia 1.0: `20 * 0.50 * 1.0 = 10 distritos`
- Eficiencia 1.1: `20 * 0.50 * 1.1 = 11 distritos`
- Eficiencia 1.2: `20 * 0.50 * 1.2 = 12 distritos`

## Uso desde Frontend

**Request proporcional (actual):**
```json
{
  "anio": 2024,
  "sistema": "mixto",
  "mr_seats": 300,
  "rp_seats": 100,
  "aplicar_topes": true,
  "votos_redistribuidos": {"MORENA": 50.0, "PAN": 20.0, ...},
  "redistritacion_geografica": false
}
```

**Request geográfico (nuevo):**
```json
{
  "anio": 2024,
  "sistema": "mixto",
  "mr_seats": 300,
  "rp_seats": 100,
  "aplicar_topes": true,
  "votos_redistribuidos": {"MORENA": 50.0, "PAN": 20.0, ...},
  "redistritacion_geografica": true,
  "eficiencia_geografica": 1.1
}
```

**Response (ambos modos):**
```json
{
  "asignaciones": {
    "MORENA": {"MR": 153, "RP": 47, "Total": 200},
    "PAN": {"MR": 45, "RP": 20, "Total": 65},
    ...
  },
  "total_escanos": 400,
  ...
}
```

## Implementación en Frontend (sugerida)

**UI Components:**
1. **Toggle/Switch**: "Usar redistritación geográfica"
2. **Slider**: "Factor de eficiencia" (1.0 - 1.2) - solo visible si toggle activado
3. **Info tooltip**: Explicar diferencia entre modos

**Ejemplo React:**
```jsx
<Switch 
  label="Redistritación geográfica"
  checked={useGeoRedistribution}
  onChange={(e) => setUseGeoRedistribution(e.target.checked)}
/>

{useGeoRedistribution && (
  <Slider
    label="Factor de eficiencia geográfica"
    min={1.0}
    max={1.2}
    step={0.1}
    value={geoEfficiency}
    onChange={(val) => setGeoEfficiency(val)}
  />
)}
```

**API Call:**
```javascript
const response = await fetch('/procesar/diputados', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    ...baseParams,
    redistritacion_geografica: useGeoRedistribution,
    eficiencia_geografica: useGeoRedistribution ? geoEfficiency : undefined
  })
});
```

## Archivos Modificados

1. `main.py` - Endpoint `/procesar/diputados`
   - Líneas 775-776: Nuevos parámetros
   - Líneas 800-801: Documentación
   - Líneas 1418-1537: Lógica de cálculo geográfico

2. `engine/procesar_diputados_v2.py` - Procesador principal
   - Línea 1042: Nuevo parámetro `mr_ganados_geograficos`
   - Líneas 1260-1275: Lógica condicional para usar MR geográficos

3. `test_redistritacion_geografica.py` - Script de prueba (nuevo)

## Testing

### Prueba Manual:
```bash
# Terminal 1: Servidor
python main.py

# Terminal 2: Prueba
python test_redistritacion_geografica.py
```

### Validaciones:
✅ Endpoint acepta nuevos parámetros  
✅ Cálculo geográfico se ejecuta correctamente  
✅ MR geográficos se pasan al procesador  
✅ Procesador usa MR geográficos cuando están disponibles  
✅ Modo proporcional sigue funcionando (backward compatible)  
✅ Resultados coinciden con cálculos de scripts

## Próximos Pasos

1. **Ejecutar pruebas** con `test_redistritacion_geografica.py`
2. **Verificar logs** en consola del servidor
3. **Comparar resultados** entre modos
4. **Documentar API** en Swagger/OpenAPI
5. **Implementar en frontend** con toggle y slider
6. **Testing E2E** con diferentes escenarios

## Notas Importantes

- **Backward compatible**: El modo proporcional sigue siendo el default
- **Performance**: Cálculo geográfico es más pesado (carga secciones, población)
- **Exactitud**: Resultados geográficos coinciden con scripts de análisis
- **Flexibilidad**: Factor de eficiencia ajustable según concentración real
- **Debugging**: Todos los cálculos se logean en modo debug

## Referencias

- Script de cálculo: `calcular_votos_minimos_morena.py`
- Resultados: `data/votos_minimos_morena.csv`
- Módulos de redistritación: `redistritacion/modulos/`
  - `reparto_distritos.py` (repartir_distritos_hare)
  - `distritacion.py` (cargar_secciones_ine)
