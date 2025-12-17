# 🎯 RESUMEN: Problema hardcodeado en el backend

## 🔴 El problema

**Tu teoría era CORRECTA:** El frontend mandaba la consulta bien, pero el backend tenía algo **hardcodeado**.

### Lo que pasaba:

1. **Frontend:** Envía `aplicar_topes=false` (usuario selecciona "Personalizado SIN topes")
2. **Backend:** ❌ Ignora el parámetro porque el endpoint NO lo acepta
3. **Backend:** ❌ Llama `procesar_diputados_v2()` SIN pasar `aplicar_topes`
4. **Motor:** Usa valor por defecto `aplicar_topes=True` (hardcodeado)
5. **Resultado:** SIEMPRE aplica topes, aunque el usuario los desactive

## ✅ La solución

### 3 cambios en `main.py`:

```python
# 1. Agregar parámetro al endpoint (línea 706)
async def procesar_diputados(
    # ...
    aplicar_topes: bool = True,  # ← NUEVO
    # ...
):

# 2. Actualizar documentación (línea 728)
- **aplicar_topes**: Si se aplican topes constitucionales (True) o no (False)

# 3. Pasar parámetro al motor (línea 1332)
resultado = procesar_diputados_v2(
    # ...
    aplicar_topes=aplicar_topes,  # ← NUEVO
    # ...
)
```

## 📊 Prueba que funciona

```bash
$ python tmp_test_aplicar_topes_endpoint.py

1️⃣ CON TOPES (aplicar_topes=True):
   MORENA: 266 escaños

2️⃣ SIN TOPES (aplicar_topes=False):
   MORENA: 339 escaños

✅ Diferencia: +73 escaños sin topes
```

## 🚀 Cómo usarlo desde el frontend

### Antes (NO funcionaba):
```javascript
// El backend ignoraba esto ❌
fetch('/procesar/diputados?anio=2024&aplicar_topes=false')
```

### Ahora (SÍ funciona):
```javascript
// El backend respeta el parámetro ✅
fetch('/procesar/diputados?anio=2024&aplicar_topes=false')
// Resultado: Sin límites constitucionales

fetch('/procesar/diputados?anio=2024&aplicar_topes=true&sobrerrepresentacion=8.0')
// Resultado: Con límite del 8%
```

## 🎨 En la interfaz del usuario

### Escenario 1: Plan "Vigente" (con topes)
```
Usuario selecciona: "2024 - Sistema Vigente"
Frontend envía: aplicar_topes=true, sobrerrepresentacion=8.0
Backend aplica: Límite constitucional del 8%
Resultado: MORENA max 266 escaños ✅
```

### Escenario 2: Plan "Personalizado" SIN topes
```
Usuario selecciona: "Personalizado" + toggle "Sin topes constitucionales"
Frontend envía: aplicar_topes=false
Backend aplica: Sin límites
Resultado: MORENA puede tener 339 escaños ✅
```

## 📋 Otros parámetros que el frontend puede controlar

Ahora que vimos que `aplicar_topes` estaba hardcodeado, revisé y **estos SÍ están implementados correctamente:**

✅ `usar_coaliciones` - Funciona
✅ `sobrerrepresentacion` - Funciona
✅ `umbral` - Funciona
✅ `mr_seats` - Funciona
✅ `rp_seats` - Funciona
✅ `pm_seats` - Funciona
✅ `reparto_mode` - Funciona
✅ `reparto_method` - Funciona

**Solo faltaba `aplicar_topes`** ← Ya corregido

## 🔍 ¿Por qué los datos se veían "mal" en el frontend?

No era que los datos estuvieran mal formateados (MR/PM/RP sí se envían correctamente).

El problema era que el **cálculo interno estaba mal** porque:
- Siempre aplicaba topes (incluso cuando NO debía)
- Esto daba resultados diferentes a los esperados
- El frontend mostraba correctamente los datos... pero los datos eran incorrectos

### Ejemplo concreto:

```
Usuario: "Dame 500 escaños SIN topes para MORENA"
Frontend: aplicar_topes=false ✅ (correcto)
Backend (antes): aplicar_topes=True 😱 (ignoraba el frontend)
Backend (ahora): aplicar_topes=False ✅ (respeta el frontend)

Resultado antes: 266 escaños (con topes) ❌
Resultado ahora: 339 escaños (sin topes) ✅
```

## 🎉 Conclusión

**Tu intuición era correcta al 100%:**
- ✅ El frontend enviaba bien los datos
- ✅ Había algo hardcodeado en el backend
- ✅ El backend ignoraba los parámetros del frontend

**Fix aplicado:**
- ✅ `aplicar_topes` ahora se acepta en el endpoint
- ✅ Se pasa correctamente al motor de cálculo
- ✅ El frontend tiene control total sobre los topes

**Próximo paso:**
- Reiniciar el backend en producción para que tome los cambios
- Probar en el frontend que ahora sí funciona el toggle de topes
