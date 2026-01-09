"""
EXPERIMENTO: Comparar método REAL (scale_siglado) vs método SINTÉTICO (R-style)

Configuración del experimento:
- 200 MR (mayoría relativa)
- 200 RP (representación proporcional)
- Total: 400 escaños

Compara:
1. TU MÉTODO: scale_siglado (escala 300 distritos reales a 200 MR) + 200 RP nacional
2. MÉTODO R: Inventar magnitudes variables por distrito + PR distrital

Genera tabla comparativa con métricas de proporcionalidad.
"""

import pandas as pd
import numpy as np
from engine.procesar_diputados_v2 import procesar_diputados_v2, LR_ties, norm_ascii_up, normalize_entidad_ascii
from engine.core import largest_remainder
import sys
from datetime import datetime

print("\n" + "="*80)
print("EXPERIMENTO: MÉTODO REAL (scale_siglado) vs MÉTODO SINTÉTICO (R-style)")
print("="*80)
print("\nConfiguración: 200 MR + 200 RP = 400 escaños totales")
print("="*80)

# ==================== CONFIGURACIÓN ====================
ANIO = 2024
PATH_PARQUET = f'data/computos_diputados_{ANIO}.parquet'
PATH_SIGLADO = f'data/siglado-diputados-{ANIO}.csv'

MR_SEATS = 200
RP_SEATS = 200
TOTAL_SEATS = 400

PARTIDOS = ['MORENA', 'PAN', 'PRI', 'PVEM', 'PT', 'MC', 'PRD']
SEED = 42

# ==================== MÉTODO 1: TU CÓDIGO (scale_siglado) ====================
print(f"\n{'='*80}")
print("MÉTODO 1: TU CÓDIGO (scale_siglado + RP nacional)")
print(f"{'='*80}")
print("\nEjecución:")
print(f"  - Escala 300 distritos reales → {MR_SEATS} MR")
print(f"  - Aplica {RP_SEATS} RP nacionalmente")
print(f"  - Coaliciones: NO")
print(f"  - Topes: SÍ (+8%, max 300)")

resultado_real = procesar_diputados_v2(
    path_parquet=PATH_PARQUET,
    path_siglado=PATH_SIGLADO,
    anio=ANIO,
    partidos_base=PARTIDOS,
    max_seats=TOTAL_SEATS,
    mr_seats=MR_SEATS,
    rp_seats=RP_SEATS,
    pm_seats=0,
    sistema='mixto',
    usar_coaliciones=False,
    umbral=0.03,
    aplicar_topes=True,
    sobrerrepresentacion=8.0,
    max_seats_per_party=300,
    seed=SEED,
    print_debug=False
)

print("\n✓ Método REAL completado")

# Calcular votos % desde el resultado
votos_dict_real = resultado_real['votos']
total_votos_real = sum(votos_dict_real.values())
votos_pct_real = {p: (votos_dict_real[p] / total_votos_real) * 100 for p in PARTIDOS}

print("\nResultados (MR + RP):")

resultados_metodo_real = {}
for partido in PARTIDOS:
    mr = resultado_real['mr'].get(partido, 0)
    rp = resultado_real['rp'].get(partido, 0)
    total = resultado_real['tot'].get(partido, 0)
    votos_pct = votos_pct_real[partido]
    
    resultados_metodo_real[partido] = {
        'mr': mr,
        'rp': rp,
        'total': total,
        'votos_pct': votos_pct,
        'escanos_pct': (total / TOTAL_SEATS) * 100
    }
    
    print(f"  {partido:8s}: {total:3d} escaños ({total/TOTAL_SEATS*100:5.2f}%) | MR={mr:3d} RP={rp:3d} | Votos={votos_pct:5.2f}%")

# ==================== MÉTODO 2: SINTÉTICO (get.max MR) ====================
print(f"\n{'='*80}")
print("MÉTODO 2: SINTÉTICO (mayoría relativa con get.max)")
print(f"{'='*80}")

print("\n[1/4] Cargando datos de distritos...")
df = pd.read_parquet(PATH_PARQUET)
df.columns = [norm_ascii_up(c) for c in df.columns]

# Normalizar entidad
if 'ENTIDAD' in df.columns:
    df['ENTIDAD'] = df['ENTIDAD'].apply(
        lambda x: x.decode('utf-8') if isinstance(x, bytes) else str(x)
    )
    df['ENTIDAD'] = df['ENTIDAD'].apply(normalize_entidad_ascii)
if 'DISTRITO' in df.columns:
    df['DISTRITO'] = pd.to_numeric(df['DISTRITO'], errors='coerce').fillna(0).astype(int)

# Agrupar por distrito
distrito_votos = df.groupby(['ENTIDAD', 'DISTRITO']).agg({
    p: 'sum' for p in PARTIDOS
}).reset_index()

print(f"  Total distritos cargados: {len(distrito_votos)}")

# ==================== FUNCIÓN: ASIGNAR MAGNITUDES SINTÉTICAS ====================
def asignar_magnitudes_sinteticas(df_distritos, total_escanos, partidos=PARTIDOS):
    """
    Asigna magnitudes variables a cada distrito según su tamaño (votos totales)
    
    Lógica:
    1. Calcula "tamaño" de cada distrito = suma de votos de todos los partidos
    2. Magnitud proporcional a tamaño: M_d = round(size_d * S / sum(sizes))
    3. Ajusta para que sum(M_d) = total_escanos exacto
    
    Similar al código R:
        size <- c(100, 200, ..., 1000)
        M <- round(size * 100 / sum(size))
    """
    n_distritos = len(df_distritos)
    
    # Calcular tamaño (votos totales) por distrito
    df_distritos = df_distritos.copy()
    df_distritos['size'] = df_distritos[partidos].sum(axis=1)
    
    sizes = df_distritos['size'].values
    total_size = sizes.sum()
    
    # Magnitud proporcional a tamaño
    magnitudes = np.round(sizes * total_escanos / total_size).astype(int)
    
    # Asegurar que ningún distrito tenga magnitud 0
    magnitudes = np.maximum(magnitudes, 1)
    
    # Ajustar para que sumen exactamente total_escanos
    delta = total_escanos - magnitudes.sum()
    
    if delta != 0:
        # Ordenar por tamaño (descendente si delta > 0, ascendente si delta < 0)
        indices = np.argsort(sizes)[::-1 if delta > 0 else 1]
        
        # Distribuir el ajuste
        for i in range(abs(delta)):
            idx = indices[i % len(indices)]
            if delta > 0:
                magnitudes[idx] += 1
            else:
                if magnitudes[idx] > 1:  # No bajar de 1
                    magnitudes[idx] -= 1
    
    return magnitudes, sizes



# ==================== MÉTODO 2: SINTÉTICO (magnitudes variables para MR) ====================

print("\n[2/4] Asignando magnitudes variables SOLO para MR (proporcionales a votos)...")
magnitudes_mr, sizes = asignar_magnitudes_sinteticas(
    distrito_votos, 
    MR_SEATS,  # SOLO 200 MR (no 400)
    PARTIDOS
)

print(f"\nEstadísticas de magnitudes para {MR_SEATS} MR:")
print(f"  - Total escaños MR: {magnitudes_mr.sum()}")
print(f"  - Magnitud mínima: {magnitudes_mr.min()}")
print(f"  - Magnitud máxima: {magnitudes_mr.max()}")
print(f"  - Magnitud promedio: {magnitudes_mr.mean():.2f}")
print(f"  - Magnitud mediana: {np.median(magnitudes_mr):.0f}")

# Distribución de magnitudes
from collections import Counter
dist_mag = Counter(magnitudes_mr)
print(f"\nDistribución de magnitudes MR:")
for mag in sorted(dist_mag.keys()):
    count = dist_mag[mag]
    print(f"  Magnitud {mag:2d}: {count:3d} distritos ({count/len(magnitudes_mr)*100:5.2f}%)")

print(f"\n[3/4] Calculando MR con PR distrital y magnitudes variables...")
mr_sintetico = calcular_mr_con_magnitudes_variables(
    distrito_votos,
    magnitudes_mr,
    partidos=PARTIDOS,
    seed=SEED
)

total_mr_sint = sum(mr_sintetico.values())
print(f"\nResultados MR (magnitudes variables, total={total_mr_sint}):")
for partido in PARTIDOS:
    mr = mr_sintetico[partido]
    pct = (mr / total_mr_sint * 100) if total_mr_sint > 0 else 0
    print(f"  {partido:8s}: {mr:3d} MR ({pct:5.2f}%)")

# Verificar que suma exactamente MR_SEATS
if total_mr_sint != MR_SEATS:
    print(f"\n⚠️  WARNING: Total MR = {total_mr_sint}, esperado {MR_SEATS}")
    print(f"   Ajustando...")
    # No debería pasar si asignar_magnitudes_sinteticas funciona bien
else:
    print(f"\n✓ Total MR correcto: {total_mr_sint} = {MR_SEATS}")

# ==================== PASO 3: APLICAR RP NACIONAL CON TU CÓDIGO ====================
print(f"\n{'='*80}")
print("MÉTODO SINTÉTICO - PASO 2: Aplicar RP Nacional (tu código)")
print(f"{'='*80}")

print(f"\n[3/4] Calculando {RP_SEATS} RP usando tu motor (procesar_diputados_v2)...")
print("  - Usa los MR calculados con magnitudes variables")
print("  - Aplica RP nacional (mismo que método REAL)")
print("  - Aplica topes constitucionales (+8%, max 300)")

# Necesitamos "inyectar" los MR sintéticos en procesar_diputados_v2
# Para esto, creamos un siglado sintético basado en los MR calculados

# Calcular votos nacionales para RP
votos_nacionales = distrito_votos[PARTIDOS].sum().to_dict()
total_votos = sum(votos_nacionales.values())
votos_pct_dict = {p: (votos_nacionales[p] / total_votos) * 100 for p in PARTIDOS}

# Aplicar RP usando la misma lógica que procesar_diputados_v2
# (sin topes primero, para ver diferencia)
votos_array = np.array([votos_nacionales[p] for p in PARTIDOS])
rp_array = LR_ties(v_abs=votos_array, n=RP_SEATS, q=None, seed=SEED)
rp_sintetico_sin_topes = {p: int(rp_array[i]) for i, p in enumerate(PARTIDOS)}

# Calcular totales sin topes
total_sin_topes = {p: mr_sintetico[p] + rp_sintetico_sin_topes[p] for p in PARTIDOS}

print(f"\n✓ RP calculado (sin topes aún)")
print("\nResultados SIN TOPES (MR sintético + RP nacional):")
for partido in PARTIDOS:
    mr = mr_sintetico[partido]
    rp = rp_sintetico_sin_topes[partido]
    total = total_sin_topes[partido]
    votos = votos_pct_dict[partido]
    print(f"  {partido:8s}: {total:3d} escaños ({total/TOTAL_SEATS*100:5.2f}%) | MR={mr:3d} RP={rp:3d} | Votos={votos:5.2f}%")

# Aplicar topes (lógica simplificada de aplicar_topes_nacionales)
print(f"\n[4/4] Aplicando topes constitucionales (+8%, max 300)...")

# Calcular topes
SOBREREP = 8.0
MAX_SEATS_PARTY = 300
umbral = 0.03

escanos_finales_sintetico = {}
rp_final_sintetico = {}

for partido in PARTIDOS:
    votos_pct = votos_pct_dict[partido]
    mr = mr_sintetico[partido]
    rp_inicial = rp_sintetico_sin_topes[partido]
    
    # Filtrar por umbral
    if votos_pct < (umbral * 100):
        escanos_finales_sintetico[partido] = mr  # Solo MR, sin RP
        rp_final_sintetico[partido] = 0
        continue
    
    # Calcular tope
    tope = min(
        int(np.floor((votos_pct/100 + SOBREREP/100) * TOTAL_SEATS)),
        MAX_SEATS_PARTY
    )
    
    total_inicial = mr + rp_inicial
    
    if total_inicial > tope:
        # Reducir RP para cumplir tope
        rp_ajustado = max(0, tope - mr)
        escanos_finales_sintetico[partido] = tope
        rp_final_sintetico[partido] = rp_ajustado
        print(f"  ⚠️  {partido}: capado de {total_inicial} → {tope} (RP: {rp_inicial} → {rp_ajustado})")
    else:
        escanos_finales_sintetico[partido] = total_inicial
        rp_final_sintetico[partido] = rp_inicial

print("\n✓ Método SINTÉTICO completado")
print("\nResultados FINALES (MR sintético + RP nacional CON TOPES):")

resultados_metodo_sintetico = {}
for partido in PARTIDOS:
    mr = mr_sintetico[partido]
    rp = rp_final_sintetico[partido]
    total = escanos_finales_sintetico[partido]
    votos_pct = votos_pct_dict[partido]
    
    resultados_metodo_sintetico[partido] = {
        'mr': mr,
        'rp': rp,
        'total': total,
        'votos_pct': votos_pct,
        'escanos_pct': (total / TOTAL_SEATS) * 100
    }
    
    print(f"  {partido:8s}: {total:3d} escaños ({total/TOTAL_SEATS*100:5.2f}%) | MR={mr:3d} RP={rp:3d} | Votos={votos_pct:5.2f}%")

# ==================== CALCULAR MÉTRICAS DE PROPORCIONALIDAD ====================
print(f"\n{'='*80}")
print("MÉTRICAS DE PROPORCIONALIDAD")
print(f"{'='*80}")

print("\n[4/4] Calculando Loosemore-Hanby y Gallagher...")

def calcular_metricas_proporcionalidad(escanos_dict, votos_pct_dict, partidos=PARTIDOS):
    """
    Calcula métricas de proporcionalidad
    
    - Loosemore-Hanby: sum(|v% - s%|) / 2
    - Gallagher (LSq): sqrt(sum((v% - s%)^2) / 2)
    """
    total_escanos = sum(escanos_dict.values())
    escanos_pct = {p: (escanos_dict[p] / total_escanos) * 100 for p in partidos}
    
    # Loosemore-Hanby
    lh = sum(abs(votos_pct_dict[p] - escanos_pct[p]) for p in partidos) / 2
    
    # Gallagher
    gallagher = np.sqrt(sum((votos_pct_dict[p] - escanos_pct[p])**2 for p in partidos) / 2)
    
    return lh, gallagher, escanos_pct

# Votos % para métricas
votos_pct_dict = {p: (votos_nacionales[p] / total_votos) * 100 for p in PARTIDOS}

# Métricas método REAL
escanos_real_dict = {p: resultados_metodo_real[p]['total'] for p in PARTIDOS}
lh_real, gal_real, escanos_pct_real = calcular_metricas_proporcionalidad(
    escanos_real_dict, 
    votos_pct_dict
)

# Métricas método SINTÉTICO
escanos_sint_dict = {p: resultados_metodo_sintetico[p]['total'] for p in PARTIDOS}
lh_sint, gal_sint, escanos_pct_sint = calcular_metricas_proporcionalidad(
    escanos_sint_dict,
    votos_pct_dict
)

print("\n" + "─"*80)
print("MÉTODO REAL (scale_siglado + RP nacional):")
print(f"  Loosemore-Hanby: {lh_real:.3f}")
print(f"  Gallagher:       {gal_real:.3f}")

print("\nMÉTODO SINTÉTICO (magnitudes variables + PR distrital):")
print(f"  Loosemore-Hanby: {lh_sint:.3f}")
print(f"  Gallagher:       {gal_sint:.3f}")

print("\n" + "─"*80)
print("DIFERENCIA (Sintético - Real):")
print(f"  Δ Loosemore-Hanby: {lh_sint - lh_real:+.3f}")
print(f"  Δ Gallagher:       {gal_sint - gal_real:+.3f}")

if gal_sint > gal_real:
    print(f"\n⚠️  Método SINTÉTICO es MENOS proporcional ({gal_sint - gal_real:.3f} más distorsión)")
else:
    print(f"\n✓ Método SINTÉTICO es MÁS proporcional ({gal_real - gal_sint:.3f} menos distorsión)")

# ==================== TABLA COMPARATIVA ====================
print(f"\n{'='*80}")
print("TABLA COMPARATIVA DETALLADA")
print(f"{'='*80}\n")

# Crear DataFrame comparativo
filas = []

for partido in PARTIDOS:
    votos = votos_pct_dict[partido]
    
    # Método REAL
    mr_real = resultados_metodo_real[partido]['mr']
    rp_real = resultados_metodo_real[partido]['rp']
    total_real = resultados_metodo_real[partido]['total']
    pct_real = resultados_metodo_real[partido]['escanos_pct']
    desv_real = pct_real - votos
    
    # Método SINTÉTICO
    mr_sint = resultados_metodo_sintetico[partido]['mr']
    rp_sint = resultados_metodo_sintetico[partido]['rp']
    total_sint = resultados_metodo_sintetico[partido]['total']
    pct_sint = resultados_metodo_sintetico[partido]['escanos_pct']
    desv_sint = pct_sint - votos
    
    filas.append({
        'Partido': partido,
        'Votos_%': f"{votos:.2f}",
        'REAL_MR': mr_real,
        'REAL_RP': rp_real,
        'REAL_Total': total_real,
        'REAL_%': f"{pct_real:.2f}",
        'REAL_Desv': f"{desv_real:+.2f}",
        'SINT_MR': mr_sint,
        'SINT_RP': rp_sint,
        'SINT_Total': total_sint,
        'SINT_%': f"{pct_sint:.2f}",
        'SINT_Desv': f"{desv_sint:+.2f}",
        'Diff_MR': mr_sint - mr_real,
        'Diff_RP': rp_sint - rp_real,
        'Diff_Total': total_sint - total_real
    })

df_comparativo = pd.DataFrame(filas)

# Agregar fila de totales
filas.append({
    'Partido': 'TOTAL',
    'Votos_%': '100.00',
    'REAL_MR': MR_SEATS,
    'REAL_RP': RP_SEATS,
    'REAL_Total': TOTAL_SEATS,
    'REAL_%': '100.00',
    'REAL_Desv': '─',
    'SINT_MR': sum(resultados_metodo_sintetico[p]['mr'] for p in PARTIDOS),
    'SINT_RP': sum(resultados_metodo_sintetico[p]['rp'] for p in PARTIDOS),
    'SINT_Total': TOTAL_SEATS,
    'SINT_%': '100.00',
    'SINT_Desv': '─',
    'Diff_MR': sum(resultados_metodo_sintetico[p]['mr'] for p in PARTIDOS) - MR_SEATS,
    'Diff_RP': sum(resultados_metodo_sintetico[p]['rp'] for p in PARTIDOS) - RP_SEATS,
    'Diff_Total': 0
})

df_comparativo = pd.DataFrame(filas)

print(df_comparativo.to_string(index=False))

# ==================== EXPORTAR RESULTADOS ====================
print(f"\n{'='*80}")
print("EXPORTANDO RESULTADOS")
print(f"{'='*80}")

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_csv = f'outputs/comparacion_metodo_real_vs_sintetico_{timestamp}.csv'

# Crear DataFrame para exportar
df_export = pd.DataFrame(filas)

# Agregar metadatos
df_metadata = pd.DataFrame([
    {'Métrica': 'Configuración', 'REAL': f'{MR_SEATS} MR + {RP_SEATS} RP', 'SINTÉTICO': f'{MR_SEATS} MR (magnitud variable) + {RP_SEATS} RP'},
    {'Métrica': 'Loosemore-Hanby', 'REAL': f'{lh_real:.4f}', 'SINTÉTICO': f'{lh_sint:.4f}'},
    {'Métrica': 'Gallagher', 'REAL': f'{gal_real:.4f}', 'SINTÉTICO': f'{gal_sint:.4f}'},
    {'Métrica': 'Magnitud MR min', 'REAL': '1', 'SINTÉTICO': f'{magnitudes_mr.min()}'},
    {'Métrica': 'Magnitud MR max', 'REAL': '1', 'SINTÉTICO': f'{magnitudes_mr.max()}'},
    {'Métrica': 'Magnitud MR promedio', 'REAL': '1.00', 'SINTÉTICO': f'{magnitudes_mr.mean():.2f}'},
])

# Guardar ambos en un solo CSV con separador
with open(output_csv, 'w', encoding='utf-8-sig') as f:
    f.write(f"# COMPARACIÓN: Método REAL vs SINTÉTICO\n")
    f.write(f"# Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"# Configuración: {MR_SEATS} MR + {RP_SEATS} RP = {TOTAL_SEATS} escaños\n\n")
    f.write("# MÉTRICAS DE PROPORCIONALIDAD\n")
    df_metadata.to_csv(f, index=False)
    f.write("\n# RESULTADOS POR PARTIDO\n")
    df_export.to_csv(f, index=False)

print(f"\n✓ Resultados exportados: {output_csv}")

# ==================== CONCLUSIONES ====================
print(f"\n{'='*80}")
print("CONCLUSIONES")
print(f"{'='*80}\n")

print("\n1. MÉTODO REAL (scale_siglado + RP nacional):")
print("   - MR: Escala 300 distritos reales a 200 MR preservando proporcionalidad geográfica")
print("   - RP: Aplica 200 RP a nivel NACIONAL (sin fragmentación distrital)")
print(f"   - Gallagher: {gal_real:.3f}")

print("\n2. MÉTODO SINTÉTICO (magnitudes variables para MR + RP nacional):")
print("   - MR: Asigna magnitudes proporcionales al tamaño y aplica PR DISTRITAL para 200 MR")
print("   - RP: Aplica 200 RP a nivel NACIONAL (igual que método REAL)")
print("   - Topes: Aplica topes constitucionales (+8%, max 300)")
print(f"   - Gallagher: {gal_sint:.3f}")

if gal_sint > gal_real:
    print(f"\n3. RESULTADO:")
    print(f"   ⚠️  El método SINTÉTICO produce {gal_sint - gal_real:.3f} puntos MÁS de distorsión")
    print(f"   - Razón: Las magnitudes variables para MR crean más distorsión que scale_siglado")
    print(f"   - Aunque ambos usan RP nacional, el MR sintético parte con más desbalance")
else:
    print(f"\n3. RESULTADO:")
    print(f"   ✓ El método SINTÉTICO produce {gal_real - gal_sint:.3f} puntos MENOS de distorsión")
    print(f"   - Las magnitudes variables para MR pueden ser más proporcionales que scale_siglado")

print("\n4. IMPLICACIONES:")
print("   - Esta comparación AÍSLA el efecto de cómo se calculan los MR")
print("   - Ambos métodos usan RP nacional + topes (solo difieren en MR)")
print("   - Diferencia muestra si magnitudes variables vs scale_siglado es mejor para MR")

print(f"\n{'='*80}\n")
