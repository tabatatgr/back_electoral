# API de Mayoría Forzada - Documentación para Frontend

## Endpoint
```
GET /calcular/mayoria_forzada
```

## Parámetros de Entrada

### Obligatorios
- `partido` (string): Partido objetivo (ej: "MORENA")
- `tipo_mayoria` (string): "simple" o "calificada"
- `plan` (string): "vigente", "senado_2018", "personalizado", etc.
- `anio` (int): Año electoral (2018, 2021, 2024)

### Opcionales (para configuraciones personalizadas)
- `escanos_totales` (int): Total de escaños del sistema
- `mr_seats` (int): Escaños de Mayoría Relativa
- `rp_seats` (int): Escaños de Representación Proporcional  
- `sistema` (string): "mixto", "mr", "rp"
- `aplicar_topes` (bool): Aplicar límites constitucionales (default: true)
- `votos_base` (JSON string): Distribución de votos base (opcional)

## Ejemplo de Llamada

### Configuración Estándar (500 escaños)
```javascript
const params = new URLSearchParams({
  partido: 'MORENA',
  tipo_mayoria: 'simple',
  plan: 'vigente',
  anio: 2024,
  aplicar_topes: true
});

const response = await fetch(`/calcular/mayoria_forzada?${params}`);
const data = await response.json();
```

### Configuración Personalizada (128 escaños)
```javascript
const params = new URLSearchParams({
  partido: 'MORENA',
  tipo_mayoria: 'simple',
  plan: 'personalizado',
  anio: 2024,
  escanos_totales: 128,
  mr_seats: 64,
  rp_seats: 64,
  sistema: 'mixto',
  aplicar_topes: true
});

const response = await fetch(`/calcular/mayoria_forzada?${params}`);
const data = await response.json();
```

## Estructura de Respuesta

```typescript
interface MayoriaForzadaResponse {
  // Información básica
  viable: boolean;                    // Si es posible alcanzar la mayoría
  diputados_necesarios: number;       // Umbral de mayoría (65 para simple en 128 escaños)
  diputados_obtenidos: number;        // Escaños que obtendría el partido
  votos_porcentaje: number;           // % de votos necesario (ej: 55.0)
  mr_asignados: number;               // Escaños MR asignados al partido
  rp_asignados: number;               // Escaños RP asignados al partido
  partido: string;                    // Partido objetivo
  plan: string;                       // Plan utilizado
  tipo_mayoria: string;               // "simple" o "calificada"
  
  // 🔑 Distribución completa de escaños (TODOS los partidos recalculados)
  seat_chart: Array<{
    party: string;                    // Nombre del partido
    seats: number;                    // Total de escaños
    mr: number;                       // Escaños de Mayoría Relativa
    pm: number;                       // Escaños de Primera Minoría (0 si no aplica)
    rp: number;                       // Escaños de Representación Proporcional
    votes: number;                    // Votos totales
    percent: number;                  // Porcentaje de votos
    color: string;                    // Color del partido (hex)
  }>;
  
  // 📊 Indicadores de proporcionalidad
  kpis: {
    total_votos: number;              // Total de votos emitidos
    total_escanos: number;            // Total de escaños distribuidos
    gallagher: number;                // Índice de Gallagher (desproporcionalidad)
    ratio_promedio: number;           // Ratio promedio votos/escaños
    desviacion_proporcionalidad: number;
    partidos_con_escanos: number;     // Partidos que superaron el umbral
  };
  
  // 📍 NUEVO: Distribución geográfica por estado
  mr_por_estado: {
    [estado: string]: {               // Nombre del estado (32 estados)
      [partido: string]: number;      // MR ganados por cada partido
    };
  };
  
  // 📍 NUEVO: Total de distritos por estado
  distritos_por_estado: {
    [estado: string]: number;         // Total de distritos MR en cada estado
  };
  
  // Información adicional
  advertencias: string[];             // Mensajes de advertencia
  metodo: string;                     // Método usado (redistritación realista/simplificado)
}
```

## Ejemplo de Respuesta Real

```json
{
  "viable": true,
  "diputados_necesarios": 65,
  "diputados_obtenidos": 68,
  "votos_porcentaje": 55.0,
  "mr_asignados": 32,
  "rp_asignados": 36,
  "partido": "MORENA",
  "plan": "personalizado",
  "tipo_mayoria": "simple",
  
  "seat_chart": [
    {
      "party": "MORENA",
      "seats": 68,
      "mr": 32,
      "pm": 0,
      "rp": 36,
      "votes": 31435391,
      "percent": 53.64,
      "color": "#9d2449"
    },
    {
      "party": "PAN",
      "seats": 23,
      "mr": 13,
      "pm": 0,
      "rp": 10,
      "votes": 9130314,
      "percent": 15.58,
      "color": "#0066CC"
    }
    // ... resto de partidos
  ],
  
  "kpis": {
    "total_votos": 58604910,
    "total_escanos": 128,
    "gallagher": 2.74,
    "ratio_promedio": 0.8492,
    "desviacion_proporcionalidad": 0.3944,
    "partidos_con_escanos": 6
  },
  
  "mr_por_estado": {
    "AGUASCALIENTES": {
      "PAN": 3,
      "PRI": 0,
      "PRD": 0,
      "PVEM": 0,
      "PT": 0,
      "MC": 0,
      "MORENA": 0
    },
    "BAJA CALIFORNIA": {
      "PAN": 0,
      "PRI": 0,
      "PRD": 0,
      "PVEM": 0,
      "PT": 0,
      "MC": 0,
      "MORENA": 9
    },
    "MEXICO": {
      "PAN": 1,
      "PRI": 0,
      "PRD": 0,
      "PVEM": 0,
      "PT": 0,
      "MC": 0,
      "MORENA": 39
    }
    // ... 32 estados en total
  },
  
  "distritos_por_estado": {
    "AGUASCALIENTES": 3,
    "BAJA CALIFORNIA": 9,
    "MEXICO": 40,
    "JALISCO": 20
    // ... 32 estados en total
  },
  
  "advertencias": [],
  "metodo": "Redistritación geográfica realista (Hare + eficiencia 0.9)"
}
```

## Casos de Uso para el Frontend

### 1. Mostrar Resumen General
```javascript
const { 
  viable, 
  diputados_necesarios, 
  diputados_obtenidos, 
  votos_porcentaje 
} = data;

console.log(`Necesitas ${votos_porcentaje}% de votos`);
console.log(`Obtendrías ${diputados_obtenidos}/${diputados_necesarios} escaños`);
```

### 2. Tabla de Distribución de Escaños
```javascript
data.seat_chart.forEach(partido => {
  console.log(
    `${partido.party}: ${partido.seats} escaños ` +
    `(MR: ${partido.mr}, RP: ${partido.rp}) - ${partido.percent}% votos`
  );
});
```

### 3. Mapa Geográfico por Estado
```javascript
// Mostrar cuántos distritos ganó cada partido en cada estado
Object.entries(data.mr_por_estado).forEach(([estado, partidos]) => {
  const total = data.distritos_por_estado[estado];
  const ganador = Object.entries(partidos)
    .filter(([_, count]) => count > 0)
    .sort(([_, a], [__, b]) => b - a)[0];
  
  if (ganador) {
    const [partido, mr_ganados] = ganador;
    console.log(`${estado}: ${partido} ganó ${mr_ganados}/${total} distritos`);
  }
});
```

### 4. Tabla Detallada por Estado
```javascript
// Para cada estado, mostrar la competencia
Object.entries(data.mr_por_estado).forEach(([estado, partidos]) => {
  const total = data.distritos_por_estado[estado];
  const competencia = Object.entries(partidos)
    .filter(([_, count]) => count > 0)
    .map(([partido, count]) => ({
      partido,
      mr: count,
      porcentaje: (count / total * 100).toFixed(1)
    }));
  
  console.log(`\n${estado} (${total} distritos):`);
  competencia.forEach(({ partido, mr, porcentaje }) => {
    console.log(`  ${partido}: ${mr} distritos (${porcentaje}%)`);
  });
});
```

### 5. Gráfica de Barras Apiladas
```javascript
// Datos para Chart.js o similar
const estados = Object.keys(data.mr_por_estado);
const partidos = ['MORENA', 'PAN', 'PRI', 'MC', 'PVEM', 'PT'];

const datasets = partidos.map(partido => ({
  label: partido,
  data: estados.map(estado => data.mr_por_estado[estado][partido]),
  backgroundColor: getColorForParty(partido)
}));

// Usar con Chart.js
new Chart(ctx, {
  type: 'bar',
  data: {
    labels: estados,
    datasets: datasets
  },
  options: {
    scales: {
      x: { stacked: true },
      y: { stacked: true }
    }
  }
});
```

### 6. Filtro por Estado
```javascript
function getMRDetailForState(estado) {
  const total = data.distritos_por_estado[estado];
  const distribucion = data.mr_por_estado[estado];
  
  return {
    estado,
    total_distritos: total,
    partidos: Object.entries(distribucion)
      .filter(([_, count]) => count > 0)
      .map(([partido, count]) => ({
        partido,
        mr_ganados: count,
        porcentaje: (count / total * 100).toFixed(1)
      }))
      .sort((a, b) => b.mr_ganados - a.mr_ganados)
  };
}

// Ejemplo de uso
const jalisco = getMRDetailForState('JALISCO');
console.log(jalisco);
// {
//   estado: 'JALISCO',
//   total_distritos: 20,
//   partidos: [
//     { partido: 'MORENA', mr_ganados: 12, porcentaje: '60.0' },
//     { partido: 'MC', mr_ganados: 5, porcentaje: '25.0' },
//     { partido: 'PAN', mr_ganados: 3, porcentaje: '15.0' }
//   ]
// }
```

## Validaciones Importantes

### Verificar que el cálculo es correcto
```javascript
// 1. Suma de MR por partido debe coincidir con mr_asignados
const totalMRPartido = Object.values(data.mr_por_estado)
  .reduce((sum, estado) => sum + estado[data.partido], 0);
  
console.assert(
  totalMRPartido === data.mr_asignados,
  'MR total debe coincidir'
);

// 2. Suma de todos los seat_chart debe ser escanos_totales
const totalSeats = data.seat_chart.reduce((sum, p) => sum + p.seats, 0);
console.assert(
  totalSeats === data.kpis.total_escanos,
  'Total de escaños debe coincidir'
);

// 3. Para cada partido: MR + PM + RP = seats
data.seat_chart.forEach(partido => {
  const suma = partido.mr + partido.pm + partido.rp;
  console.assert(
    suma === partido.seats,
    `${partido.party}: MR+PM+RP debe igualar seats`
  );
});
```

## Notas Técnicas

1. **Algoritmo de cálculo**: Usa búsqueda binaria iterativa para encontrar el porcentaje exacto de votos necesario
2. **Eficiencia geográfica**: Aplica factor 0.9 para configs <100 MR, 1.1 para >=300 MR
3. **Umbral electoral**: 3% para obtener escaños de RP
4. **Redistritación**: Usa datos reales del parquet 2024 con redistribución geográfica por estado
5. **Topes constitucionales**: Si `aplicar_topes=true`, limita sobrerrepresentación al 8%

## Cambios vs Versión Anterior

✅ **Agregado**: `mr_por_estado` - Distribución MR por estado y partido
✅ **Agregado**: `distritos_por_estado` - Total de distritos por estado  
✅ **Mejorado**: Cálculo con búsqueda binaria (más preciso que fórmula algebraica)
✅ **Corregido**: Umbral dinámico según escaños_totales (no hardcoded a 251)
✅ **Corregido**: seat_chart ahora incluye TODOS los partidos recalculados
