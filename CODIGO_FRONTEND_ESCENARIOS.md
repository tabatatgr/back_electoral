# 📦 Código Copy-Paste para Frontend

## 🎯 Componente React Completo

```jsx
import React, { useState, useEffect } from 'react';

/**
 * Selector de Escenarios Predeterminados
 * Carga automáticamente los escenarios desde el backend
 */
function EscenarioSelector({ camara = 'diputados', onChange }) {
  const [escenarios, setEscenarios] = useState([]);
  const [selectedPlan, setSelectedPlan] = useState('vigente');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Cargar escenarios desde el backend
  useEffect(() => {
    fetch('http://localhost:8000/data/escenarios')
      .then(res => {
        if (!res.ok) throw new Error('Error cargando escenarios');
        return res.json();
      })
      .then(data => {
        setEscenarios(data[camara] || []);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error:', err);
        setError(err.message);
        setLoading(false);
      });
  }, [camara]);

  // Handle cambio de escenario
  const handleChange = (planId) => {
    setSelectedPlan(planId);
    if (onChange) {
      onChange(planId);
    }
  };

  if (loading) {
    return <div className="loading">Cargando escenarios...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  // Agrupar por categoría
  const porCategoria = {
    oficial: escenarios.filter(e => e.categoria === 'oficial'),
    reforma: escenarios.filter(e => e.categoria === 'reforma'),
    nuevo: escenarios.filter(e => e.categoria === 'nuevo'),
    custom: escenarios.filter(e => e.categoria === 'custom')
  };

  return (
    <div className="escenario-selector">
      <label htmlFor="plan-select">
        <strong>Escenario Electoral:</strong>
      </label>
      
      <select 
        id="plan-select"
        value={selectedPlan} 
        onChange={(e) => handleChange(e.target.value)}
        className="form-select"
      >
        {/* Sistema Actual */}
        {porCategoria.oficial.length > 0 && (
          <optgroup label="📌 Sistema Actual">
            {porCategoria.oficial.map(esc => (
              <option key={esc.id} value={esc.id}>
                {esc.icon} {esc.nombre} - {esc.descripcion}
              </option>
            ))}
          </optgroup>
        )}
        
        {/* Propuestas de Reforma */}
        {porCategoria.reforma.length > 0 && (
          <optgroup label="📋 Propuestas de Reforma">
            {porCategoria.reforma.map(esc => (
              <option key={esc.id} value={esc.id}>
                {esc.icon} {esc.nombre} - {esc.descripcion}
              </option>
            ))}
          </optgroup>
        )}
        
        {/* Nuevos Escenarios */}
        {porCategoria.nuevo.length > 0 && (
          <optgroup label="🆕 Nuevos Escenarios">
            {porCategoria.nuevo.map(esc => (
              <option key={esc.id} value={esc.id}>
                {esc.icon} {esc.nombre} - {esc.descripcion} {esc.badge ? `[${esc.badge}]` : ''}
              </option>
            ))}
          </optgroup>
        )}
        
        {/* Personalizado */}
        {porCategoria.custom.length > 0 && (
          <optgroup label="⚙️ Personalizar">
            {porCategoria.custom.map(esc => (
              <option key={esc.id} value={esc.id}>
                {esc.icon} {esc.nombre} - {esc.descripcion}
              </option>
            ))}
          </optgroup>
        )}
      </select>
      
      {/* Detalles del escenario seleccionado */}
      <DetallesEscenario 
        escenario={escenarios.find(e => e.id === selectedPlan)} 
      />
    </div>
  );
}

/**
 * Componente para mostrar detalles del escenario seleccionado
 */
function DetallesEscenario({ escenario }) {
  if (!escenario || !escenario.detalles) return null;
  
  const { detalles } = escenario;
  
  return (
    <div className="detalles-escenario">
      <small>
        {detalles.total && (
          <span>Total: <strong>{detalles.total}</strong> escaños</span>
        )}
        {detalles.mr !== undefined && detalles.mr > 0 && (
          <span> | MR: <strong>{detalles.mr}</strong></span>
        )}
        {detalles.rp !== undefined && detalles.rp > 0 && (
          <span> | RP: <strong>{detalles.rp}</strong></span>
        )}
        {detalles.pm !== undefined && detalles.pm > 0 && (
          <span> | PM: <strong>{detalles.pm}</strong></span>
        )}
        {detalles.umbral !== undefined && (
          <span> | Umbral: <strong>{(detalles.umbral * 100).toFixed(0)}%</strong></span>
        )}
        {detalles.tope_max && (
          <span> | Tope: <strong>{detalles.tope_max}</strong></span>
        )}
      </small>
    </div>
  );
}

export default EscenarioSelector;
```

---

## 🎨 CSS Sugerido

```css
/* Selector de escenarios */
.escenario-selector {
  margin: 1rem 0;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.escenario-selector label {
  display: block;
  margin-bottom: 0.5rem;
  color: #333;
}

.form-select {
  width: 100%;
  padding: 0.5rem;
  font-size: 1rem;
  border: 2px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  transition: border-color 0.2s;
}

.form-select:hover {
  border-color: #007bff;
}

.form-select:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

/* Detalles del escenario */
.detalles-escenario {
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: white;
  border-left: 4px solid #007bff;
  border-radius: 4px;
}

.detalles-escenario small {
  color: #666;
  display: block;
  line-height: 1.6;
}

.detalles-escenario strong {
  color: #007bff;
  font-weight: 600;
}

.detalles-escenario span {
  margin-right: 0.5rem;
}

/* Loading y error */
.loading, .error {
  padding: 1rem;
  border-radius: 4px;
  text-align: center;
}

.loading {
  background: #e3f2fd;
  color: #1976d2;
}

.error {
  background: #ffebee;
  color: #c62828;
}
```

---

## 📲 Versión Vanilla JavaScript (sin React)

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Selector de Escenarios</title>
  <style>
    /* Usa el CSS de arriba */
  </style>
</head>
<body>
  <div id="app"></div>

  <script>
    // Cargar y renderizar escenarios
    async function cargarEscenarios() {
      const app = document.getElementById('app');
      
      try {
        const response = await fetch('http://localhost:8000/data/escenarios');
        const data = await response.json();
        
        // Renderizar selector
        app.innerHTML = `
          <div class="escenario-selector">
            <label for="plan-select">
              <strong>Escenario Electoral:</strong>
            </label>
            
            <select id="plan-select" class="form-select" onchange="handlePlanChange(this.value)">
              ${renderOptGroups(data.diputados)}
            </select>
            
            <div id="detalles" class="detalles-escenario"></div>
          </div>
        `;
        
        // Guardar data global para uso posterior
        window.escenariosData = data;
        
        // Mostrar detalles del primero
        handlePlanChange('vigente');
        
      } catch (error) {
        app.innerHTML = `<div class="error">Error: ${error.message}</div>`;
      }
    }

    // Renderizar grupos de opciones
    function renderOptGroups(escenarios) {
      const grupos = {
        'oficial': { label: '📌 Sistema Actual', items: [] },
        'reforma': { label: '📋 Propuestas de Reforma', items: [] },
        'nuevo': { label: '🆕 Nuevos Escenarios', items: [] },
        'custom': { label: '⚙️ Personalizar', items: [] }
      };
      
      // Agrupar escenarios
      escenarios.forEach(esc => {
        if (grupos[esc.categoria]) {
          grupos[esc.categoria].items.push(esc);
        }
      });
      
      // Renderizar HTML
      let html = '';
      for (const [key, grupo] of Object.entries(grupos)) {
        if (grupo.items.length > 0) {
          html += `<optgroup label="${grupo.label}">`;
          grupo.items.forEach(esc => {
            const badge = esc.badge ? ` [${esc.badge}]` : '';
            html += `
              <option value="${esc.id}">
                ${esc.icon} ${esc.nombre} - ${esc.descripcion}${badge}
              </option>
            `;
          });
          html += `</optgroup>`;
        }
      }
      
      return html;
    }

    // Manejar cambio de plan
    function handlePlanChange(planId) {
      const escenario = window.escenariosData.diputados.find(e => e.id === planId);
      
      if (!escenario || !escenario.detalles) {
        document.getElementById('detalles').innerHTML = '';
        return;
      }
      
      const d = escenario.detalles;
      let html = '<small>';
      
      if (d.total) html += `Total: <strong>${d.total}</strong> escaños`;
      if (d.mr > 0) html += ` | MR: <strong>${d.mr}</strong>`;
      if (d.rp > 0) html += ` | RP: <strong>${d.rp}</strong>`;
      if (d.pm > 0) html += ` | PM: <strong>${d.pm}</strong>`;
      if (d.umbral !== undefined) html += ` | Umbral: <strong>${(d.umbral * 100).toFixed(0)}%</strong>`;
      if (d.tope_max) html += ` | Tope: <strong>${d.tope_max}</strong>`;
      
      html += '</small>';
      document.getElementById('detalles').innerHTML = html;
      
      // Aquí puedes llamar a tu función para procesar el escenario
      console.log('Escenario seleccionado:', planId);
      // procesarEscenario(planId);
    }

    // Procesar escenario (enviar al backend)
    async function procesarEscenario(planId) {
      const response = await fetch('http://localhost:8000/procesar/diputados', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          anio: 2024,
          plan: planId
        })
      });
      
      const data = await response.json();
      console.log('Resultado:', data);
      
      // Actualizar UI con resultados...
    }

    // Cargar al inicio
    cargarEscenarios();
  </script>
</body>
</html>
```

---

## 🔌 Vue.js Component

```vue
<template>
  <div class="escenario-selector">
    <label for="plan-select">
      <strong>Escenario Electoral:</strong>
    </label>
    
    <select 
      id="plan-select"
      v-model="selectedPlan"
      @change="handleChange"
      class="form-select"
    >
      <optgroup 
        v-for="(grupo, categoria) in escenariosPorCategoria" 
        :key="categoria"
        :label="grupo.label"
      >
        <option 
          v-for="esc in grupo.items" 
          :key="esc.id" 
          :value="esc.id"
        >
          {{ esc.icon }} {{ esc.nombre }} - {{ esc.descripcion }}
          {{ esc.badge ? `[${esc.badge}]` : '' }}
        </option>
      </optgroup>
    </select>
    
    <div v-if="escenarioActual" class="detalles-escenario">
      <small>
        <span v-if="detalles.total">
          Total: <strong>{{ detalles.total }}</strong> escaños
        </span>
        <span v-if="detalles.mr > 0">
          | MR: <strong>{{ detalles.mr }}</strong>
        </span>
        <span v-if="detalles.rp > 0">
          | RP: <strong>{{ detalles.rp }}</strong>
        </span>
        <span v-if="detalles.pm > 0">
          | PM: <strong>{{ detalles.pm }}</strong>
        </span>
        <span v-if="detalles.umbral !== undefined">
          | Umbral: <strong>{{ (detalles.umbral * 100).toFixed(0) }}%</strong>
        </span>
        <span v-if="detalles.tope_max">
          | Tope: <strong>{{ detalles.tope_max }}</strong>
        </span>
      </small>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EscenarioSelector',
  props: {
    camara: {
      type: String,
      default: 'diputados'
    }
  },
  data() {
    return {
      escenarios: [],
      selectedPlan: 'vigente',
      loading: true,
      error: null
    };
  },
  computed: {
    escenariosPorCategoria() {
      const grupos = {
        oficial: { label: '📌 Sistema Actual', items: [] },
        reforma: { label: '📋 Propuestas de Reforma', items: [] },
        nuevo: { label: '🆕 Nuevos Escenarios', items: [] },
        custom: { label: '⚙️ Personalizar', items: [] }
      };
      
      this.escenarios.forEach(esc => {
        if (grupos[esc.categoria]) {
          grupos[esc.categoria].items.push(esc);
        }
      });
      
      return grupos;
    },
    escenarioActual() {
      return this.escenarios.find(e => e.id === this.selectedPlan);
    },
    detalles() {
      return this.escenarioActual?.detalles || {};
    }
  },
  methods: {
    async cargarEscenarios() {
      try {
        const response = await fetch('http://localhost:8000/data/escenarios');
        const data = await response.json();
        this.escenarios = data[this.camara] || [];
        this.loading = false;
      } catch (err) {
        this.error = err.message;
        this.loading = false;
      }
    },
    handleChange() {
      this.$emit('change', this.selectedPlan);
    }
  },
  mounted() {
    this.cargarEscenarios();
  }
};
</script>

<style scoped>
/* Usa el CSS de arriba */
</style>
```

---

## 🚀 Hook Personalizado para React

```javascript
import { useState, useEffect } from 'react';

/**
 * Hook para cargar y gestionar escenarios del backend
 * @param {string} camara - 'diputados' o 'senado'
 * @returns {object} { escenarios, loading, error, selectedPlan, setSelectedPlan }
 */
export function useEscenarios(camara = 'diputados') {
  const [escenarios, setEscenarios] = useState([]);
  const [selectedPlan, setSelectedPlan] = useState('vigente');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;

    fetch('http://localhost:8000/data/escenarios')
      .then(res => {
        if (!res.ok) throw new Error('Error cargando escenarios');
        return res.json();
      })
      .then(data => {
        if (isMounted) {
          setEscenarios(data[camara] || []);
          setLoading(false);
        }
      })
      .catch(err => {
        if (isMounted) {
          setError(err.message);
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [camara]);

  const escenarioActual = escenarios.find(e => e.id === selectedPlan);

  return {
    escenarios,
    loading,
    error,
    selectedPlan,
    setSelectedPlan,
    escenarioActual
  };
}

// Uso del hook:
function MiComponente() {
  const { 
    escenarios, 
    loading, 
    error, 
    selectedPlan, 
    setSelectedPlan,
    escenarioActual 
  } = useEscenarios('diputados');

  if (loading) return <div>Cargando...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <select value={selectedPlan} onChange={(e) => setSelectedPlan(e.target.value)}>
      {escenarios.map(esc => (
        <option key={esc.id} value={esc.id}>
          {esc.nombre}
        </option>
      ))}
    </select>
  );
}
```

---

¿Necesitas el código en otro framework? (Angular, Svelte, etc.) 🚀
