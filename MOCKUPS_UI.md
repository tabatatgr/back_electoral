# 🎨 MOCKUPS Y EJEMPLOS VISUALES PARA FRONTEND

## 1️⃣ BADGE DE MAYORÍAS (INTEGRAR EN RESULTADOS ACTUALES)

### Ejemplo: Mayoría Calificada
```html
<div style="
  background: #E6F2FF;
  border-left: 4px solid #0066CC;
  padding: 16px;
  border-radius: 8px;
  margin: 16px 0;
">
  <div style="display: flex; align-items: center; gap: 12px;">
    <span style="font-size: 24px;">🔵</span>
    <div>
      <h3 style="margin: 0; color: #0066CC; font-size: 18px;">
        Mayoría Calificada (2/3)
      </h3>
      <p style="margin: 4px 0 0 0; font-size: 16px;">
        <strong>MORENA</strong> - 270 de 400 escaños (67.5%)
      </p>
    </div>
  </div>
</div>
```

**Se ve así:**
```
╔════════════════════════════════════════════════╗
║ 🔵  Mayoría Calificada (2/3)                  ║
║     MORENA - 270 de 400 escaños (67.5%)       ║
╚════════════════════════════════════════════════╝
   (fondo azul claro, borde azul izquierdo)
```

---

### Ejemplo: Mayoría Simple con Coalición
```html
<div style="
  background: #E6FFE6;
  border-left: 4px solid #00AA00;
  padding: 16px;
  border-radius: 8px;
">
  <div style="display: flex; align-items: center; gap: 12px;">
    <span style="font-size: 24px;">🟢</span>
    <div>
      <h3 style="margin: 0; color: #00AA00; font-size: 18px;">
        Mayoría Simple
      </h3>
      <p style="margin: 4px 0; font-size: 16px;">
        <strong>MORENA+PT+PVEM</strong> - 210 de 400 escaños (52.5%)
      </p>
      <p style="margin: 0; color: #FF8C00; font-size: 14px;">
        ⚠️ Solo alcanzada con coalición
      </p>
    </div>
  </div>
</div>
```

**Se ve así:**
```
╔════════════════════════════════════════════════╗
║ 🟢  Mayoría Simple                            ║
║     MORENA+PT+PVEM - 210 de 400 escaños       ║
║     ⚠️ Solo alcanzada con coalición           ║
╚════════════════════════════════════════════════╝
   (fondo verde claro, borde verde izquierdo)
```

---

### Ejemplo: Sin Mayoría
```html
<div style="
  background: #F5F5F5;
  border-left: 4px solid #999999;
  padding: 16px;
  border-radius: 8px;
">
  <div style="display: flex; align-items: center; gap: 12px;">
    <span style="font-size: 24px;">⚪</span>
    <div>
      <h3 style="margin: 0; color: #666666; font-size: 18px;">
        Congreso Dividido
      </h3>
      <p style="margin: 4px 0; font-size: 16px;">
        Ningún partido alcanza mayoría
      </p>
      <p style="margin: 0; color: #FF6B6B; font-size: 14px;">
        ⚠️ Se requieren pactos entre partidos
      </p>
    </div>
  </div>
</div>
```

---

## 2️⃣ FORMULARIO: CALCULAR MAYORÍA FORZADA

```
┌─────────────────────────────────────────────────────────┐
│ 🎯 Calcular Mayoría Forzada - Senado                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Partido:                                               │
│  ┌──────────────────────┐                              │
│  │ MORENA            ▼ │                               │
│  └──────────────────────┘                              │
│                                                          │
│  Tipo de Mayoría:                                       │
│  ○ Mayoría Simple (>64 senadores, 50%)                 │
│  ● Mayoría Calificada (≥86 senadores, 2/3)             │
│                                                          │
│  Plan Electoral:                                        │
│  ┌──────────────────────┐                              │
│  │ Vigente (128)     ▼ │                               │
│  └──────────────────────┘                              │
│  (64 MR + 32 PM + 32 RP)                               │
│                                                          │
│  ☑ Aplicar topes del 8%                                │
│                                                          │
│  ┌──────────────────────┐                              │
│  │   CALCULAR 🔍       │                               │
│  └──────────────────────┘                              │
└─────────────────────────────────────────────────────────┘
```

**Después de calcular, mostrar resultado:**

```
┌─────────────────────────────────────────────────────────┐
│ ✅ Resultado                                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Para alcanzar MAYORÍA CALIFICADA con MORENA:          │
│                                                          │
│  📊 Necesitas obtener:                                  │
│     • 52% de los votos a nivel nacional                │
│     • Ganar 28 de 32 estados                           │
│                                                          │
│  🏛️ Obtendrías:                                         │
│     • 90 senadores totales (necesitas ≥86)             │
│     • 60 MR + 30 RP                                    │
│     • ✅ Alcanzas mayoría calificada                   │
│                                                          │
│  ┌──────────────────────────┐                          │
│  │  Ver detalle de estados │                           │
│  └──────────────────────────┘                          │
└─────────────────────────────────────────────────────────┘
```

---

## 3️⃣ TABLA DE ESTADOS GANADOS

```
┌───────────────────────────────────────────────────────────────────┐
│ 📋 Estados que ganaría MORENA con 52% de votos                  │
├───────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Total: 28 de 32 estados | 56 senadores MR                       │
│                                                                    │
│  ┌──────────────┬─────────────────┬──────────┬─────────────┐    │
│  │ Estado       │ Partido Ganador │ Senadores│ % Votos     │    │
│  ├──────────────┼─────────────────┼──────────┼─────────────┤    │
│  │ CDMX         │ MORENA          │    2     │ 65%         │    │
│  │ MEXICO       │ MORENA          │    2     │ 58%         │    │
│  │ VERACRUZ     │ MORENA          │    2     │ 56%         │    │
│  │ PUEBLA       │ MORENA          │    2     │ 54%         │    │
│  │ JALISCO      │ MORENA          │    2     │ 51%         │    │
│  │ GUANAJUATO   │ PAN             │    0     │ 35%         │    │
│  │ ...          │ ...             │   ...    │ ...         │    │
│  └──────────────┴─────────────────┴──────────┴─────────────┘    │
│                                                                    │
│  ┌─────────────────┐  ┌──────────────────┐                      │
│  │ Exportar CSV   │  │ Editar Manual   │                       │
│  └─────────────────┘  └──────────────────┘                      │
└───────────────────────────────────────────────────────────────────┘
```

**Colorear filas:**
- MORENA (guinda/morado): `background: #FFEBF0;`
- PAN (azul): `background: #E6F2FF;`
- PRI (rojo): `background: #FFE6E6;`
- etc.

---

## 4️⃣ EDICIÓN MANUAL DE ESTADOS

### Opción A: Tabla con Dropdowns

```
┌───────────────────────────────────────────────────────────┐
│ ✏️ Editar Estados Manualmente - Senado                   │
├───────────────────────────────────────────────────────────┤
│                                                            │
│  Asigna el partido ganador en cada estado:               │
│                                                            │
│  ┌──────────────┬─────────────────────────────┐          │
│  │ Estado       │ Partido Ganador             │          │
│  ├──────────────┼─────────────────────────────┤          │
│  │ CDMX         │ [MORENA          ▼]         │          │
│  │ MEXICO       │ [MORENA          ▼]         │          │
│  │ JALISCO      │ [PAN             ▼]         │          │
│  │ GUANAJUATO   │ [PAN             ▼]         │          │
│  │ PUEBLA       │ [MORENA          ▼]         │          │
│  │ ...          │ ...                         │          │
│  └──────────────┴─────────────────────────────┘          │
│                                                            │
│  Resumen actual:                                          │
│  • MORENA: 15 estados (30 senadores)                     │
│  • PAN: 10 estados (20 senadores)                        │
│  • PRI: 7 estados (14 senadores)                         │
│                                                            │
│  ┌──────────────────────┐                                │
│  │  CALCULAR RESULTADO │                                 │
│  └──────────────────────┘                                │
└───────────────────────────────────────────────────────────┘
```

### Opción B: Mapa Interactivo (más complejo pero bonito)

```
┌───────────────────────────────────────────────────────────┐
│ 🗺️ Mapa de México - Click en cada estado                 │
├───────────────────────────────────────────────────────────┤
│                                                            │
│           ┌─────────────────────────┐                    │
│           │    [Mapa SVG aquí]      │                    │
│           │  Estados clickeables    │                    │
│           │  Coloreados por partido │                    │
│           └─────────────────────────┘                    │
│                                                            │
│  Leyenda:                                                 │
│  🟣 MORENA  🔵 PAN  🔴 PRI  🟠 MC  🟡 PRD                │
│                                                            │
│  Click en un estado para cambiar el partido ganador      │
│                                                            │
│  ┌──────────────────────┐                                │
│  │  CALCULAR RESULTADO │                                 │
│  └──────────────────────┘                                │
└───────────────────────────────────────────────────────────┘
```

---

## 5️⃣ EXPORTAR ESCENARIO

```
┌───────────────────────────────────────────────────────────┐
│ 💾 Guardar Escenario                                      │
├───────────────────────────────────────────────────────────┤
│                                                            │
│  Nombre del escenario:                                    │
│  ┌──────────────────────────────────────────────┐        │
│  │ MORENA_Mayoria_Calificada_2024               │        │
│  └──────────────────────────────────────────────┘        │
│                                                            │
│  Descripción (opcional):                                  │
│  ┌──────────────────────────────────────────────┐        │
│  │ Escenario donde MORENA gana 28 estados       │        │
│  │ alcanzando mayoría calificada en Senado      │        │
│  └──────────────────────────────────────────────┘        │
│                                                            │
│  Este escenario incluye:                                  │
│  • 28 estados asignados                                   │
│  • MORENA: 20 estados, PAN: 5, PRI: 3                    │
│  • Fecha: 15/01/2026 14:30                               │
│                                                            │
│  ┌──────────────┐  ┌──────────┐                          │
│  │  GUARDAR CSV│  │ CANCELAR │                           │
│  └──────────────┘  └──────────┘                          │
└───────────────────────────────────────────────────────────┘
```

---

## 6️⃣ IMPORTAR ESCENARIO

```
┌───────────────────────────────────────────────────────────┐
│ 📂 Cargar Escenario                                       │
├───────────────────────────────────────────────────────────┤
│                                                            │
│  Selecciona un archivo CSV previamente guardado:         │
│                                                            │
│  ┌──────────────────────────────────────────────┐        │
│  │  📁 Examinar...                              │        │
│  └──────────────────────────────────────────────┘        │
│                                                            │
│  Archivo seleccionado:                                    │
│  ✅ MORENA_Mayoria_Calificada_2024.csv                   │
│                                                            │
│  Preview del escenario:                                   │
│  ┌──────────────────────────────────────────────┐        │
│  │ Escenario: MORENA_Mayoria_Calificada_2024    │        │
│  │ Descripción: Escenario donde MORENA gana...  │        │
│  │ Fecha: 15/01/2026 14:30                      │        │
│  │                                                │        │
│  │ Distribución:                                 │        │
│  │ • MORENA: 20 estados (40 senadores)          │        │
│  │ • PAN: 8 estados (16 senadores)              │        │
│  │ • PRI: 4 estados (8 senadores)               │        │
│  └──────────────────────────────────────────────┘        │
│                                                            │
│  ┌──────────────┐  ┌──────────┐                          │
│  │  APLICAR    │  │ CANCELAR │                           │
│  └──────────────┘  └──────────┘                          │
└───────────────────────────────────────────────────────────┘
```

---

## 7️⃣ PÁGINA COMPLETA: CALCULADORA DE MAYORÍAS

```
╔═══════════════════════════════════════════════════════════════╗
║  🏛️ Sistema Electoral - Calculadora de Mayorías              ║
╠═══════════════════════════════════════════════════════════════╣
║                                                                ║
║  [ Diputados ]  [ Senado ]  <-- Tabs                          ║
║                                                                ║
║  ┌────────────────────────────────────────────────────────┐  ║
║  │ 🎯 Opción 1: Calcular Mayoría Forzada                  │  ║
║  │                                                          │  ║
║  │  ¿Qué necesita tu partido para ganar?                  │  ║
║  │                                                          │  ║
║  │  [Formulario aquí]                                      │  ║
║  │  ┌──────────────┐                                       │  ║
║  │  │  CALCULAR   │                                        │  ║
║  │  └──────────────┘                                       │  ║
║  └──────────────────────────────────────────────────────────┘  ║
║                                                                ║
║  ┌────────────────────────────────────────────────────────┐  ║
║  │ ✏️ Opción 2: Editar Manualmente                         │  ║
║  │                                                          │  ║
║  │  Asigna el partido ganador en cada estado              │  ║
║  │                                                          │  ║
║  │  [Tabla/Mapa aquí]                                      │  ║
║  │                                                          │  ║
║  │  ┌──────────────┐  ┌─────────────┐  ┌──────────────┐  │  ║
║  │  │  CALCULAR   │  │  GUARDAR    │  │   CARGAR     │  │  ║
║  │  └──────────────┘  └─────────────┘  └──────────────┘  │  ║
║  └──────────────────────────────────────────────────────────┘  ║
║                                                                ║
║  ┌────────────────────────────────────────────────────────┐  ║
║  │ 📊 Resultado                                            │  ║
║  │                                                          │  ║
║  │  [Badge de Mayoría aquí]                               │  ║
║  │                                                          │  ║
║  │  Distribución de escaños:                              │  ║
║  │  • MORENA: 90 senadores (70%)                          │  ║
║  │  • PAN: 25 senadores (19%)                             │  ║
║  │  • PRI: 13 senadores (10%)                             │  ║
║  │                                                          │  ║
║  │  [Gráfica de barras o pastel]                          │  ║
║  └──────────────────────────────────────────────────────────┘  ║
║                                                                ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## 🎨 CÓDIGO CSS SUGERIDO

```css
/* Badge de Mayoría Calificada */
.mayoria-badge.calificada {
  background: #E6F2FF;
  border-left: 4px solid #0066CC;
  padding: 16px;
  border-radius: 8px;
  margin: 16px 0;
}

.mayoria-badge.calificada .icon {
  font-size: 24px;
}

.mayoria-badge.calificada h3 {
  color: #0066CC;
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

/* Badge de Mayoría Simple */
.mayoria-badge.simple {
  background: #E6FFE6;
  border-left: 4px solid #00AA00;
}

.mayoria-badge.simple h3 {
  color: #00AA00;
}

/* Badge Sin Mayoría */
.mayoria-badge.sin-mayoria {
  background: #F5F5F5;
  border-left: 4px solid #999999;
}

.mayoria-badge.sin-mayoria h3 {
  color: #666666;
}

/* Warning de Coalición */
.mayoria-warning {
  color: #FF8C00;
  font-size: 14px;
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* Filas de tabla por partido */
.fila-morena {
  background: #FFEBF0;
}

.fila-pan {
  background: #E6F2FF;
}

.fila-pri {
  background: #FFE6E6;
}

.fila-mc {
  background: #FFE8CC;
}

.fila-prd {
  background: #FFFFCC;
}
```

---

## 📱 RESPONSIVE (MOBILE)

En mobile, cambiar a stack vertical:

```
┌──────────────────────┐
│ 🔵 Mayoría          │
│    Calificada       │
│                     │
│ MORENA              │
│ 270 escaños         │
└──────────────────────┘

┌──────────────────────┐
│ Formulario          │
│                     │
│ [Partido ▼]        │
│                     │
│ ○ Simple           │
│ ● Calificada       │
│                     │
│ [CALCULAR]         │
└──────────────────────┘
```

---

## ✅ CHECKLIST DE COMPONENTES

- [ ] `MayoriaBadge.jsx` - Badge visual de mayorías
- [ ] `CalculadoraMayoria.jsx` - Formulario de mayoría forzada
- [ ] `TablaEstados.jsx` - Tabla de 32 estados
- [ ] `EditorEstados.jsx` - Editor manual con dropdowns
- [ ] `ExportarEscenario.jsx` - Modal de exportación
- [ ] `ImportarEscenario.jsx` - Input file + preview
- [ ] `ResultadoMayoria.jsx` - Card de resultados
- [ ] `GraficaDistribucion.jsx` - Gráfica de escaños (opcional)

---

🎨 **Estos mockups son solo sugerencias - adapta al diseño de tu app!**
