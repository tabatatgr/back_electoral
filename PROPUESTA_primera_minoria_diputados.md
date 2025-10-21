# Propuesta: Agregar Primera Minoría (PM) a Diputados

## Contexto

Actualmente el sistema de **Senado** ya soporta Primera Minoría (PM), pero **Diputados** no lo tiene implementado.

## Estado actual

### Senado ✅
```python
# Endpoint /procesar/senado
pm_seats: Optional[int] = None  # Parámetro existe

# engine/procesar_senadores_v2.py
def procesar_senadores_v2(..., pm_seats: int = 0, ...):
    escanos_pm = pm_seats if pm_seats is not None else 0
    escanos_mr_efectivos = escanos_mr_total - escanos_pm
```

### Diputados ❌
```python
# Endpoint /procesar/diputados
# NO existe parámetro pm_seats

# engine/procesar_diputados_v2.py
# NO existe lógica de PM
```

## Lógica de Primera Minoría

### ¿Qué es PM?
- En cada entidad/circunscripción, el **primer lugar** gana MR
- El **segundo lugar** gana PM (primera minoría)
- Los demás van a la bolsa de RP

### Ejemplo con 300 escaños de MR + 200 RP:
Sin PM:
- 300 ganadores directos (1er lugar)
- 200 distribuidos por RP

Con PM=100:
- 200 ganadores directos (1er lugar) [300 - 100]
- 100 segundos lugares (PM)
- 200 distribuidos por RP

## Cambios necesarios

### 1. Endpoint `/procesar/diputados` (main.py)

#### Agregar parámetro:
```python
@app.post("/procesar/diputados")
async def procesar_diputados_api(
    ...
    pm_seats: Optional[int] = None,  # ← NUEVO
    ...
):
```

#### Configurar PM según plan:

**Vigente** (mantener actual - sin PM):
```python
if plan_normalizado == "vigente":
    max_seats = 500
    mr_seats_final = None  # Calcular del siglado
    rp_seats_final = 200
    pm_seats_final = 0  # Sin PM en vigente
```

**Personalizado** (permitir PM):
```python
elif plan_normalizado == "personalizado":
    # Usuario puede especificar PM
    mr_puro = mr_seats if mr_seats is not None else 300
    pm_escanos = pm_seats if pm_seats is not None else 0
    rp_escanos = rp_seats if rp_seats is not None else 200
    
    # Validar: PM no puede ser mayor que MR
    if pm_escanos > mr_puro:
        raise HTTPException(
            status_code=400, 
            detail=f"PM ({pm_escanos}) no puede ser mayor que MR ({mr_puro})"
        )
    
    # PM sale de MR (no suma al total)
    mr_seats_final = mr_puro
    pm_seats_final = pm_escanos
    rp_seats_final = rp_escanos
    max_seats = mr_puro + rp_escanos  # Total fijo
```

#### Pasar a procesador:
```python
resultado = procesar_diputados_v2(
    ...
    mr_seats=mr_seats_final,
    pm_seats=pm_seats_final,  # ← NUEVO
    rp_seats=rp_seats_final,
    ...
)
```

### 2. Motor `procesar_diputados_v2.py`

#### Agregar parámetro:
```python
def procesar_diputados_v2(
    path_parquet: Optional[str] = None, 
    ...
    mr_seats: Optional[int] = None, 
    pm_seats: Optional[int] = None,  # ← NUEVO
    rp_seats: Optional[int] = None,
    ...
):
```

#### Implementar lógica PM:

**1. Configurar escaños efectivos:**
```python
# Si hay PM, calcular MR efectivo
if pm_seats is not None and pm_seats > 0:
    escanos_pm = pm_seats
    escanos_mr_efectivos = mr_seats - pm_seats  # MR puro
    print(f"[DEBUG] PM activado: {escanos_pm} PM, {escanos_mr_efectivos} MR efectivo de {mr_seats} total")
else:
    escanos_pm = 0
    escanos_mr_efectivos = mr_seats
```

**2. Calcular ganadores MR y PM por distrito:**
```python
# Leer siglado
df_siglado = pd.read_csv(path_siglado)

# Agrupar por entidad/distrito y rankear
mr_ganadores = {}  # 1er lugar (MR)
pm_ganadores = {}  # 2do lugar (PM)

for (entidad, distrito), group in df_siglado.groupby(['ENTIDAD', 'DISTRITO']):
    # Ordenar por votos descendente
    ranked = group.sort_values('VOTOS', ascending=False)
    
    # 1er lugar = MR
    primer_lugar = ranked.iloc[0]
    mr_ganadores[(entidad, distrito)] = primer_lugar['PARTIDO']
    
    # 2do lugar = PM (si hay PM habilitado)
    if escanos_pm > 0 and len(ranked) > 1:
        segundo_lugar = ranked.iloc[1]
        pm_ganadores[(entidad, distrito)] = segundo_lugar['PARTIDO']

# Contar escaños MR por partido
escanos_mr_por_partido = {}
for partido in mr_ganadores.values():
    escanos_mr_por_partido[partido] = escanos_mr_por_partido.get(partido, 0) + 1

# Contar escaños PM por partido
escanos_pm_por_partido = {}
if escanos_pm > 0:
    for partido in pm_ganadores.values():
        escanos_pm_por_partido[partido] = escanos_pm_por_partido.get(partido, 0) + 1
```

**3. Ajustar si PM excede el configurado:**
```python
# Si se asignaron más PM de los permitidos, recortar
total_pm_asignados = sum(escanos_pm_por_partido.values())
if total_pm_asignados > escanos_pm:
    # Recortar proporcionalmente o por criterio de votos
    # (implementar lógica de recorte)
    pass
```

**4. Devolver resultados con PM separado:**
```python
return {
    'mr': escanos_mr_por_partido,
    'pm': escanos_pm_por_partido,  # ← NUEVO
    'rp': escanos_rp_por_partido,
    'tot': escanos_totales_por_partido,
    'meta': {
        'pm_seats': escanos_pm,
        'mr_effective': escanos_mr_efectivos,
        ...
    }
}
```

### 3. Frontend (transformar_resultado_a_formato_frontend)

Agregar PM al formato de respuesta:

```python
def transformar_resultado_a_formato_frontend(resultado: Dict, plan: str) -> Dict:
    ...
    return {
        "partidos": [
            {
                "nombre": partido,
                "color": color,
                "escanos": {
                    "mr": mr_dict.get(partido, 0),
                    "pm": pm_dict.get(partido, 0),  # ← NUEVO
                    "rp": rp_dict.get(partido, 0),
                    "total": tot_dict.get(partido, 0)
                },
                ...
            }
            for partido in partidos_ordenados
        ],
        ...
    }
```

## Ejemplo de uso

### Request:
```json
POST /procesar/diputados
{
  "anio": 2024,
  "plan": "personalizado",
  "sistema": "mixto",
  "escanos_totales": 500,
  "mr_seats": 300,
  "pm_seats": 50,   // ← NUEVO: 50 segundos lugares
  "rp_seats": 200
}
```

### Response:
```json
{
  "partidos": [
    {
      "nombre": "MORENA",
      "escanos": {
        "mr": 150,      // 1eros lugares
        "pm": 25,       // 2dos lugares ← NUEVO
        "rp": 75,       // Proporcional
        "total": 250
      }
    },
    ...
  ],
  "meta": {
    "pm_seats": 50,
    "mr_effective": 250,  // 300 - 50 PM
    ...
  }
}
```

## Prioridad de implementación

1. **Alta**: Agregar parámetro `pm_seats` a endpoint y validaciones
2. **Alta**: Implementar cálculo de 2do lugar en siglado
3. **Media**: Lógica de recorte si PM excede límite
4. **Baja**: Tests y validaciones adicionales

## Preguntas pendientes

1. ¿Cómo recortar si hay más segundos lugares que `pm_seats` configurados?
   - Por votación (los 2dos lugares con más votos)
   - Por entidad (primeras X entidades en ranking)
   
2. ¿Aplicar sobrerrepresentación a PM también?
   - En senado: PM no aplica sobrerep
   - ¿Misma lógica para diputados?

3. ¿PM debe cumplir umbral del 3%?
   - En senado: PM es por distrito, no aplica umbral nacional
   - ¿Misma lógica para diputados?

---

**Fecha:** 21 de octubre de 2025
**Autor:** GitHub Copilot
