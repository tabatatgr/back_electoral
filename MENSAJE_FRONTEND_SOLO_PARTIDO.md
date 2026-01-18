# 📨 Mensaje para Frontend - Parámetro `solo_partido` en Mayoría Forzada

## 🎯 Resumen Ejecutivo

Implementé el parámetro **`solo_partido`** en los endpoints de mayoría forzada para diferenciar entre partido individual y coalición.

---

## ⚡ Cambios Inmediatos

### Nuevo parámetro en ambos endpoints:

**Diputados:**
```
GET /calcular/mayoria_forzada?partido=MORENA&tipo_mayoria=simple&solo_partido=true
```

**Senado:**
```
GET /calcular/mayoria_forzada_senado?partido=MORENA&tipo_mayoria=simple&solo_partido=true
```

---

## 🔧 Uso del Parámetro

### `solo_partido=true` (DEFAULT)
✅ Cuenta **SOLO** el partido especificado (ej: solo MORENA, sin PT ni PVEM)

```bash
GET /calcular/mayoria_forzada?partido=MORENA&tipo_mayoria=simple&solo_partido=true
```

**Respuesta:**
```json
{
  "diputados_obtenidos": 251,  // ← Solo MORENA
  "mr_asignados": 180,          // ← Solo MORENA
  "rp_asignados": 71,           // ← Solo MORENA
  "solo_partido": true
}
```

---

### `solo_partido=false`
🤝 Cuenta **toda la coalición** (ej: MORENA + PT + PVEM sumados)

```bash
GET /calcular/mayoria_forzada?partido=MORENA&tipo_mayoria=simple&solo_partido=false
```

**Respuesta:**
```json
{
  "diputados_obtenidos": 334,  // ← MORENA + PT + PVEM
  "mr_asignados": 230,          // ← Suma de los 3
  "rp_asignados": 104,          // ← Suma de los 3
  "solo_partido": false
}
```

---

## 🎨 Detección Automática

Si el parámetro `partido` contiene **`+`**, el backend **automáticamente** establece `solo_partido=false`:

```bash
# Esto automáticamente usa solo_partido=false
GET /calcular/mayoria_forzada?partido=MORENA+PT+PVEM&tipo_mayoria=calificada
```

---

## 🏛️ Coaliciones Reconocidas

### Coalición 4T:
- **Miembros:** MORENA, PT, PVEM
- Si envías `partido=MORENA` con `solo_partido=false`, suma los 3

### Coalición Fuerza y Corazón:
- **Miembros:** PAN, PRI, PRD
- Si envías `partido=PAN` con `solo_partido=false`, suma los 3

### Coalición Personalizada:
- Usa `partido=PARTIDO1+PARTIDO2+PARTIDO3`
- Ejemplo: `partido=PAN+PRI` (solo suma PAN y PRI, NO incluye PRD)

---

## 📋 Implementación Sugerida (Frontend)

### Opción 1: Toggle Simple
```jsx
<label>
  <input
    type="checkbox"
    checked={soloPartido}
    onChange={(e) => setSoloPartido(e.target.checked)}
  />
  Contar solo {partido} (sin coalición)
</label>
```

### Opción 2: Selector de Coalición
```jsx
<select onChange={(e) => setPartido(e.target.value)}>
  <option value="MORENA">Solo MORENA</option>
  <option value="MORENA+PT+PVEM">Coalición 4T</option>
</select>

// El backend detecta el "+" automáticamente
```

---

## ✅ Testing

### Test 1: Solo MORENA
```bash
curl "http://localhost:8000/calcular/mayoria_forzada?partido=MORENA&tipo_mayoria=simple&plan=vigente&solo_partido=true&anio=2024"
```

**Verificar:**
- `solo_partido` = `true`
- `diputados_obtenidos` < 300 (solo MORENA)

---

### Test 2: Coalición 4T
```bash
curl "http://localhost:8000/calcular/mayoria_forzada?partido=MORENA&tipo_mayoria=simple&plan=vigente&solo_partido=false&anio=2024"
```

**Verificar:**
- `solo_partido` = `false`
- `diputados_obtenidos` > 300 (incluye PT y PVEM)

---

### Test 3: Coalición con "+"
```bash
curl "http://localhost:8000/calcular/mayoria_forzada?partido=MORENA+PT+PVEM&tipo_mayoria=calificada&plan=vigente&aplicar_topes=false&anio=2024"
```

**Verificar:**
- `solo_partido` = `false` (forzado por el "+")
- `diputados_obtenidos` incluye los 3 partidos

---

## 🔄 Compatibilidad

✅ **Backward compatible**: Las llamadas sin `solo_partido` funcionan (default=true)
✅ **Funciona en ambos**: Diputados y Senado
✅ **Respuesta incluye confirmación**: El campo `solo_partido` en la respuesta indica cómo se calculó

---

## 📞 Contacto

¿Dudas o necesitas más ejemplos?
- Ver documentación completa: `FIX_MAYORIA_FORZADA_SOLO_PARTIDO.md`
- Prueba los endpoints en: `http://localhost:8000/docs`

---

¡El fix ya está deployado y listo para usar! 🚀
