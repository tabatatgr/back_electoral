# 🎯 PROMPT PARA IA DEL FRONTEND

Copia y pega esto directamente a tu IA del frontend:

---

## CONTEXTO

El backend electoral tiene **8 endpoints nuevos** ya funcionando que necesitan integrarse. NO es solo diseño - hay funcionalidad completa de detección de mayorías y cálculo de mayoría forzada.

## LO MÁS IMPORTANTE (HAZ ESTO PRIMERO)

### 1. Los endpoints `/procesar/diputados` y `/procesar/senado` YA devuelven esto:

```json
{
  "tot": { "MORENA": 210, "PAN": 80, ... },
  "mayorias": {
    "total_escanos": 400,
    "mayoria_simple": {
      "umbral": 201,
      "alcanzada": true,
      "partido": "MORENA",
      "escanos": 210,
      "es_coalicion": false
    },
    "mayoria_calificada": {
      "umbral": 267,
      "alcanzada": false,
      "partido": null,
      "escanos": 0,
      "es_coalicion": false
    }
  }
}
```

**ACCIÓN:** Crear un componente que muestre un badge visual con:
- 🔵 Fondo azul si `mayoria_calificada.alcanzada == true`
- 🟢 Fondo verde si `mayoria_simple.alcanzada == true` 
- ⚪ Fondo gris si ninguna alcanzada
- Mostrar: "Mayoría Calificada - MORENA 270 escaños" o "Mayoría Simple - PAN 210 escaños"
- Si `es_coalicion == true`, agregar warning: "⚠️ Solo con coalición"

## 8 ENDPOINTS NUEVOS A INTEGRAR

### SENADO (5 endpoints)

#### 1. Calcular Mayoría Forzada
```http
GET /calcular/mayoria_forzada_senado?partido=MORENA&tipo_mayoria=simple&plan=vigente&aplicar_topes=true&anio=2024
```
Devuelve cuántos votos/estados necesita para ganar.

**UI:** Formulario con selects (partido, tipo mayoría, plan) + botón calcular → mostrar resultado en cards

#### 2. Generar Tabla de Estados
```http
GET /generar/tabla_estados_senado?partido=MORENA&votos_porcentaje=45&anio=2024
```
Lista de estados que ganaría con X% de votos.

**UI:** Tabla con 32 estados, colorear por partido ganador

#### 3. Edición Manual
```http
POST /editar/estados_senado
Body: {
  "anio": 2024,
  "estados_manuales": {
    "MORENA": ["CDMX", "MEXICO"],
    "PAN": ["GUANAJUATO"]
  }
}
```
Asignar manualmente partidos a estados.

**UI:** Tabla/mapa donde usuario selecciona partido ganador por estado → botón calcular

#### 4. Exportar Escenario
```http
POST /exportar/escenario_senado
Body: {
  "nombre_escenario": "Mi_Escenario",
  "estados_por_partido": {...},
  "descripcion": "..."
}
```
Descarga CSV del escenario.

**UI:** Botón "Guardar" → modal pide nombre → descarga CSV

#### 5. Importar Escenario
```http
POST /importar/escenario_senado
Body: { "csv_content": "..." }
```
Carga CSV previamente guardado.

**UI:** Input file → leer contenido → enviar como string

### DIPUTADOS (2 endpoints similares)

#### 6. Generar Tabla Distritos
```http
GET /generar/tabla_distritos_diputados?partido=MORENA&votos_porcentaje=45&anio=2024
```

#### 7-8. Exportar/Importar Escenarios Diputados
Igual que Senado pero para 300 distritos.

## COLORES Y DISEÑO

```javascript
function getMayoriaStyle(mayorias) {
  if (mayorias.mayoria_calificada.alcanzada) {
    return {
      color: '#0066CC',     // Azul
      bg: '#E6F2FF',
      icon: '🔵',
      text: 'Mayoría Calificada (2/3)',
      partido: mayorias.mayoria_calificada.partido,
      escanos: mayorias.mayoria_calificada.escanos
    };
  } else if (mayorias.mayoria_simple.alcanzada) {
    return {
      color: '#00AA00',     // Verde
      bg: '#E6FFE6',
      icon: '🟢',
      text: 'Mayoría Simple',
      partido: mayorias.mayoria_simple.partido,
      escanos: mayorias.mayoria_simple.escanos
    };
  } else {
    return {
      color: '#999999',     // Gris
      bg: '#F5F5F5',
      icon: '⚪',
      text: 'Sin Mayoría',
      warning: 'Congreso dividido'
    };
  }
}
```

## UMBRALES IMPORTANTES

| Cámara | Total | Mayoría Simple | Mayoría Calificada |
|--------|-------|----------------|-------------------|
| Diputados | 400 | >200 | ≥267 (2/3) |
| Senado | 128 | >64 | ≥86 (2/3) |

## CHECKLIST RÁPIDO

**PRIORIDAD ALTA (hacer primero):**
- [ ] Badge de mayorías en `/procesar/diputados` y `/procesar/senado` (10 min)
- [ ] Formulario "Calcular Mayoría Forzada" para Senado (30 min)
- [ ] Mostrar tabla de estados ganados (20 min)

**PRIORIDAD MEDIA:**
- [ ] Edición manual de estados (1 hora)
- [ ] Exportar/importar CSV (45 min)

**PRIORIDAD BAJA:**
- [ ] Mismo flujo para Diputados
- [ ] Mapa interactivo

## EJEMPLO DE FLUJO

1. Usuario selecciona MORENA + Mayoría Simple
2. Frontend llama: `GET /calcular/mayoria_forzada_senado?partido=MORENA&tipo_mayoria=simple`
3. Backend devuelve: `{ "votos_porcentaje": 52, "estados_ganados": 24 }`
4. Frontend muestra: "Necesitas 52% de votos y ganar 24 estados"
5. Botón "Ver detalle" → llama `/generar/tabla_estados_senado?partido=MORENA&votos_porcentaje=52`
6. Muestra tabla de 24 estados que ganaría

## TESTING

Levanta el servidor:
```bash
uvicorn main:app --reload --port 8000
```

Prueba endpoint:
```bash
GET http://localhost:8000/calcular/mayoria_forzada_senado?partido=MORENA&tipo_mayoria=simple&plan=vigente
```

## RECURSOS

- Documentación completa: `DOCUMENTACION_API.md`
- Instrucciones detalladas: `INSTRUCCIONES_FRONTEND.md`
- Base URL: `http://localhost:8000`

---

**RESUMEN:** El backend está 100% listo. Tu trabajo es:
1. Mostrar badges de mayorías (YA está en el response)
2. Crear formularios para los 8 endpoints nuevos
3. Diseño bonito con los colores sugeridos

**Tiempo estimado:** 4-6 horas frontend puro
