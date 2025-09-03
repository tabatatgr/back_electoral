// CÓDIGO JAVASCRIPT ACTUALIZADO PARA DESPUÉS DE CORREGIR EL BACKEND

// 1. REMOVER el bypass temporal del umbral
function construirParametrosParaEnvio() {
    // ... código existente ...
    
    // ANTES (bypass temporal):
    // if (camara === 'senado') {
    //     console.log('[DEBUG] 🚨 BLOQUEANDO umbral para senado (backend bug)');
    //     params.umbral = 0;
    // }
    
    // DESPUÉS (umbral real para senado):
    if (camara === 'senado' && modelo === 'personalizado') {
        // Incluir parámetro de primera minoría
        const pmToggle = document.getElementById('pm-toggle')?.checked || false;
        const pmSeats = pmToggle ? parseInt(document.getElementById('input-pm')?.value || 0) : 0;
        
        params.pm_seats = pmSeats;
        params.umbral = parseFloat(document.getElementById('umbral-slider')?.value || 0.03);
        
        console.log('[DEBUG] 🏛️ SENADO personalizado con PM y umbral real:', {
            mr_seats: params.mr_seats,
            pm_seats: params.pm_seats,
            rp_seats: params.rp_seats,
            umbral: params.umbral,
            total: (params.mr_seats || 0) + (params.pm_seats || 0) + (params.rp_seats || 0)
        });
    }
    
    return params;
}

// 2. AGREGAR validación robusta
function validarParametrosSenado(params) {
    if (params.camara !== 'senado') return true;
    
    const mr = parseInt(params.mr_seats || 0);
    const pm = parseInt(params.pm_seats || 0);
    const rp = parseInt(params.rp_seats || 0);
    const total = mr + pm + rp;
    
    // Validaciones
    if (total !== 128) {
        console.warn(`⚠️ Senado: Total escaños (${total}) no suma 128`);
        return false;
    }
    
    if (params.umbral < 0 || params.umbral > 1) {
        console.warn(`⚠️ Senado: Umbral inválido (${params.umbral})`);
        return false;
    }
    
    console.log('[DEBUG] ✅ Parámetros senado válidos:', {
        MR: mr, PM: pm, RP: rp, 
        Total: total, 
        Umbral: `${(params.umbral * 100).toFixed(1)}%`
    });
    
    return true;
}

// 3. MANEJAR errores específicos de umbral
async function manejarRespuestaBackend(response) {
    if (!response.ok) {
        const errorText = await response.text();
        
        if (response.status === 500 && errorText.includes('IndexError')) {
            console.error('❌ IndexError en backend - problema con algoritmo de umbral');
            throw new Error('Error interno en cálculo de umbral. Intenta con umbral más bajo.');
        }
        
        throw new Error(`Error ${response.status}: ${errorText}`);
    }
    
    return await response.json();
}

// 4. UI FEEDBACK para umbrales problemáticos
function mostrarEstadoUmbral(umbral, camara) {
    const indicator = document.getElementById('umbral-indicator');
    if (!indicator) return;
    
    if (camara === 'senado') {
        if (umbral > 0.15) {
            indicator.textContent = '⚠️ Umbral muy alto - pocos partidos';
            indicator.className = 'warning';
        } else if (umbral > 0.05) {
            indicator.textContent = '⚡ Umbral alto';
            indicator.className = 'caution';
        } else {
            indicator.textContent = '✅ Umbral normal';
            indicator.className = 'normal';
        }
    }
}
