"""
EXPERIMENTO: Comparar RP NACIONAL vs RP DISTRITAL

Objetivo:
---------
Comparar dos formas de asignar los 200 escaños de RP:

1. MÉTODO REAL: RP Nacional (Tu código actual)
   - 200 MR usando scale_siglado (muestreo estratificado)
   - 200 RP calculados a nivel NACIONAL (Hare sobre votos totales)
   
2. MÉTODO SINTÉTICO: RP Distrital (Código R-style)
   - 200 MR usando scale_siglado (MISMO que método real)
   - 200 RP calculados a nivel DISTRITAL (Hare por distrito con magnitudes variables)

Ambos métodos usan:
- Mismos 200 MR (scale_siglado)
- Umbral 3%
- Topes constitucionales (+8%, max 300)
- Total: 200 MR + 200 RP = 400 escaños

Diferencia clave: 
- REAL usa RP NACIONAL (un solo cálculo con votos totales)
- SINTÉTICO usa RP DISTRITAL (Hare en cada distrito con magnitudes variables)
"""

import numpy as np
import pandas as pd
from datetime import datetime
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.procesar_diputados_v2 import procesar_diputados_v2, LR_ties, norm_ascii_up, normalize_entidad_ascii

# ==================== CONFIGURACIÓN ====================
ANIO = 2024
PATH_PARQUET = f'data/computos_diputados_{ANIO}.parquet'
PATH_SIGLADO = f'data/siglado-diputados-{ANIO}.csv'

PARTIDOS = ['MORENA', 'PAN', 'PRI', 'PVEM', 'PT', 'MC', 'PRD']

MR_SEATS = 200
RP_SEATS = 200
TOTAL_SEATS = 400

SEED = 42

print(f"{'='*80}")
print("EXPERIMENTO: RP NACIONAL vs RP DISTRITAL")
print(f"{'='*80}")
print("\nObjetivo: Comparar RP calculado nacionalmente vs RP calculado por distrito")
print(f"\nConfiguración:")
print(f"  - MR escaños: {MR_SEATS} (MISMO método scale_siglado para ambos)")
print(f"  - RP escaños: {RP_SEATS}")
print(f"  - Total: {TOTAL_SEATS}")
print(f"  - Umbral: 3%")
print(f"  - Topes: SÍ (+8%, max 300)")
print(f"  - Seed: {SEED}")
print(f"\nDiferencia clave:")
print(f"  - REAL: RP NACIONAL (Hare sobre votos totales del país)")
print(f"  - SINTÉTICO: RP DISTRITAL (Hare por distrito con magnitudes variables)")

# ==================== FUNCIÓN: ASIGNAR MAGNITUDES SINTÉTICAS ====================
def asignar_magnitudes_sinteticas(df_distritos, total_escanos, partidos=PARTIDOS):
    """
    Asigna magnitudes variables a cada distrito según tamaño
    Usa magnitud promedio de 2/3 de total_escanos/n_distritos para tener rango 1-3
    
    Args:
        df_distritos: DataFrame con votos por distrito (300 distritos)
        total_escanos: Total de escaños MR a repartir (200)
        partidos: Lista de partidos
    
    Returns:
        tuple: (magnitudes array que suma total_escanos, sizes array)
    """
    n_distritos = len(df_distritos)
    
    # Calcular tamaño de cada distrito (votos totales)
    sizes = np.array([df_distritos.iloc[i][partidos].sum() for i in range(n_distritos)])
    
    # Estrategia: Asignar magnitudes que tengan varianza 1-3
    # Usamos 2/3 de promedio para tener espacio de ajuste
    promedio_target = (2/3) * total_escanos / n_distritos  # Con 200/300 = ~0.44, usamos ~0.3
    
    # Normalizar sizes a rango [0, 1]
    sizes_norm = (sizes - sizes.min()) / (sizes.max() - sizes.min())
    
    # Asignar magnitudes en rango [1, 3] basadas en tamaño normalizado
    # Distritos pequeños → 1, medianos → 2, grandes → 3
    magnitudes = 1 + np.round(2 * sizes_norm).astype(int)
    magnitudes = np.clip(magnitudes, 1, 3)
    
    # Ahora tenemos magnitudes en [1, 3], pero suman ~600
    # Necesitamos reducir estratégicamente a 200
    
    # Opción: Seleccionar CUÁLES distritos usan magnitud > 1
    # Similar a lo que hace scale_siglado pero para magnitudes
    
    # Calcular cuántos distritos necesitan m>1 para llegar a 200
    # Si todos tienen m=1 → 300 escaños
    # Necesitamos quitar 100 escaños
    # O sea, necesitamos que solo ~100 distritos tengan m>1
    
    # Reset: todos parten con m=1
    magnitudes = np.ones(n_distritos, dtype=int)
    escanos_actuales = n_distritos  # 300
    
    # Necesitamos reducir a total_escanos
    # Estrategia: QUITAR distritos pequeños (dejarlos con m=0 implícitamente)
    # O mejor: Asignar magnitudes solo a los más grandes
    
    # Ordenar por tamaño (descendente)
    idx_sorted = np.argsort(-sizes)
    
    # Asignar escaños comenzando por los más grandes
    escanos_asignados = 0
    for i, idx in enumerate(idx_sorted):
        # Calcular magnitud proporcional al tamaño relativo
        # Distritos más grandes pueden tener hasta 3
        if i < n_distritos / 3:  # Top 1/3
            mag = 2 if escanos_asignados + 2 <= total_escanos else 1
        elif i < 2 * n_distritos / 3:  # Mid 1/3
            mag = 1
        else:  # Bottom 1/3
            mag = 1
        
        if escanos_asignados + mag <= total_escanos:
            magnitudes[idx] = mag
            escanos_asignados += mag
        else:
            # No hay espacio para este distrito
            remaining = total_escanos - escanos_asignados
            if remaining > 0:
                magnitudes[idx] = remaining
                escanos_asignados += remaining
            else:
                magnitudes[idx] = 0
    
    # Ajuste final con restos mayores
    diff = total_escanos - magnitudes.sum()
    
    if diff > 0:
        # Agregar a los más grandes que puedan
        idx_can_add = np.where((magnitudes > 0) & (magnitudes < 3))[0]
        if len(idx_can_add) > 0:
            idx_sorted_add = idx_can_add[np.argsort(-sizes[idx_can_add])]
            for i in range(min(diff, len(idx_sorted_add))):
                magnitudes[idx_sorted_add[i]] += 1
    elif diff < 0:
        # Quitar de los más pequeños
        idx_can_remove = np.where(magnitudes > 0)[0]
        if len(idx_can_remove) > 0:
            idx_sorted_remove = idx_can_remove[np.argsort(sizes[idx_can_remove])]
            for i in range(min(-diff, len(idx_sorted_remove))):
                if magnitudes[idx_sorted_remove[i]] > 0:
                    magnitudes[idx_sorted_remove[i]] -= 1
    
    return magnitudes, sizes

# ==================== FUNCIÓN: CALCULAR MR CON RP DISTRITAL ====================
def calcular_mr_con_rp_distrital(df_distritos, magnitudes, partidos=PARTIDOS, seed=42):
    """
    Calcula MR usando RP DISTRITAL con magnitudes variables
    Equivalente al código R que hace: Restos_Mayores(votos_distrito, M[d], "Hare")
    
    Args:
        df_distritos: DataFrame con votos por distrito
        magnitudes: Array con magnitud de cada distrito
        partidos: Lista de partidos
        seed: Semilla para reproducibilidad
    
    Returns:
        dict: escaños MR por partido
    """
    np.random.seed(seed)
    
    escanos_mr = {p: 0 for p in partidos}
    
    # Aplicar RP distrital en CADA distrito
    for idx, row in df_distritos.iterrows():
        magnitud = int(magnitudes[idx])
        
        # Votos en este distrito
        votos_distrito = np.array([row[p] for p in partidos])
        
        # Aplicar Hare con restos mayores (RP distrital)
        # Esto es equivalente a Restos_Mayores(v, M[i], "Hare") en R
        escanos_distrito = LR_ties(
            v_abs=votos_distrito,
            n=magnitud,
            q=None,
            seed=seed
        )
        
        # Acumular escaños MR
        for i, partido in enumerate(partidos):
            escanos_mr[partido] += int(escanos_distrito[i])
    
    return escanos_mr

# ==================== MÉTODO 1: TU CÓDIGO (RP nacional) ====================
print(f"\n{'='*80}")
print("MÉTODO 1: TU CÓDIGO (scale_siglado MR + RP NACIONAL)")
print(f"{'='*80}")
print("\nEjecución:")
print(f"  - MR: scale_siglado (200 distritos)")
print(f"  - RP: Nacional (Hare sobre votos totales)")
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
    usar_coaliciones=True,
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

# ==================== MÉTODO 2: SINTÉTICO (RP distrital) ====================
print(f"\n{'='*80}")
print("MÉTODO 2: SINTÉTICO (scale_siglado MR + RP DISTRITAL)")
print(f"{'='*80}")

print("\n[1/5] Calculando MR con tu método (scale_siglado)...")
print(f"  - Usa el MISMO siglado que el método REAL")
print(f"  - MR: {MR_SEATS} escaños")

# Usar procesar_diputados_v2 SOLO para obtener los MR
# (sin aplicar RP todavía)
resultado_mr_base = procesar_diputados_v2(
    path_parquet=PATH_PARQUET,
    path_siglado=PATH_SIGLADO,
    anio=ANIO,
    partidos_base=PARTIDOS,
    max_seats=TOTAL_SEATS,
    mr_seats=MR_SEATS,
    rp_seats=0,  # NO calcular RP todavía
    pm_seats=0,
    sistema='mayoritario',  # Solo MR
    usar_coaliciones=True,
    umbral=0.03,
    aplicar_topes=False,  # Sin topes en esta etapa
    seed=SEED,
    print_debug=False
)

# Extraer MR
escanos_mr_sint = resultado_mr_base['mr'].copy()
votos_nacionales = resultado_mr_base['votos'].copy()

print(f"\n✓ MR calculado (mismos que método REAL):")
total_mr_check = sum(escanos_mr_sint.values())
for partido in PARTIDOS:
    mr = escanos_mr_sint.get(partido, 0)
    print(f"  {partido:8s}: {mr:3d} MR")
print(f"  Total MR: {total_mr_check}")

print(f"\n[2/5] Cargando datos de distritos para RP distrital...")
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

print(f"\n[3/5] Asignando magnitudes variables (1-3) para RP distrital...")
print(f"  - Método: Magnitud proporcional a votos totales del distrito")
print(f"  - Total escaños RP a repartir: {RP_SEATS}")

magnitudes_rp, sizes = asignar_magnitudes_sinteticas(
    distrito_votos,
    RP_SEATS,
    PARTIDOS
)

print(f"\nEstadísticas de magnitudes para {RP_SEATS} RP:")
print(f"  - Total escaños RP: {magnitudes_rp.sum()}")
print(f"  - Magnitud mínima: {magnitudes_rp.min()}")
print(f"  - Magnitud máxima: {magnitudes_rp.max()}")
print(f"  - Magnitud promedio: {magnitudes_rp.mean():.2f}")
print(f"  - Magnitud mediana: {np.median(magnitudes_rp):.0f}")

# Distribución de magnitudes
from collections import Counter
dist_mag = Counter(magnitudes_rp)
print(f"\nDistribución de magnitudes RP:")
for mag in sorted(dist_mag.keys()):
    count = dist_mag[mag]
    if mag > 0:
        print(f"  Magnitud {mag:2d}: {count:3d} distritos ({count/len(magnitudes_rp)*100:5.2f}%)")

print(f"\n[4/5] Calculando RP con RP distrital (Hare por distrito)...")
print(f"  - Método: Restos_Mayores(votos, M[distrito], 'Hare') para cada distrito")
print(f"  - En distritos con m>1, pueden ganar múltiples partidos")

escanos_rp_distrital = calcular_mr_con_rp_distrital(
    distrito_votos,
    magnitudes_rp,
    PARTIDOS,
    SEED
)

total_rp_sint = sum(escanos_rp_distrital.values())

print(f"\n✓ RP calculado por RP distrital:")
for partido in PARTIDOS:
    rp_sint = escanos_rp_distrital.get(partido, 0)
    print(f"  {partido:8s}: {rp_sint:3d} RP ({rp_sint/total_rp_sint*100:5.2f}%)")

if total_rp_sint != RP_SEATS:
    print(f"\n⚠️  ERROR: Se esperaban {RP_SEATS} RP, se obtuvieron {total_rp_sint}")
    raise ValueError(f"Error en cálculo de RP distrital: {total_rp_sint} != {RP_SEATS}")

print(f"  Total RP: {total_rp_sint}")

print(f"\n[5/5] Aplicando topes constitucionales...")

# Calcular votos nacionales
total_votos = sum(votos_nacionales.values())
votos_pct_sint = {p: (votos_nacionales[p] / total_votos) * 100 for p in PARTIDOS}

# Aplicar topes constitucionales usando la MISMA función

# Convertir a arrays numpy (orden de PARTIDOS)
s_mr_array = np.array([escanos_mr_sint[p] for p in PARTIDOS])
s_rp_array = np.array([escanos_rp_distrital[p] for p in PARTIDOS])
v_nacional_array = np.array([votos_nacionales[p] / total_votos for p in PARTIDOS])

# Importar la función de topes
from engine.procesar_diputados_v2 import aplicar_topes_nacionales

# Aplicar topes (misma función que el método REAL)
resultado_topes = aplicar_topes_nacionales(
    s_mr=s_mr_array,
    s_rp=s_rp_array,
    v_nacional=v_nacional_array,
    S=TOTAL_SEATS,
    max_pp=0.08,
    max_seats=300,
    max_seats_per_party=300,
    threshold=0.03,
    partidos_nombres=PARTIDOS
)

# Extraer resultados
s_rp_final = resultado_topes['s_rp']
s_tot_final = resultado_topes['s_tot']

# Convertir de arrays a diccionarios
rp_sint_final = {PARTIDOS[i]: int(s_rp_final[i]) for i in range(len(PARTIDOS))}
totales_finales = {PARTIDOS[i]: int(s_tot_final[i]) for i in range(len(PARTIDOS))}

# Verificar totales
total_mr_check = sum(escanos_mr_sint.values())
total_rp_check = sum(rp_sint_final.values())
total_check = sum(totales_finales.values())

print(f"\n✓ Topes aplicados:")
print(f"  Total MR: {total_mr_check}")
print(f"  Total RP: {total_rp_check}")
print(f"  Total escaños: {total_check}")

if total_check != TOTAL_SEATS:
    print(f"  ⚠️  ADVERTENCIA: Total = {total_check}, esperado {TOTAL_SEATS}")

# Construir resultados_metodo_sint
resultados_metodo_sint = {}
for partido in PARTIDOS:
    mr = escanos_mr_sint.get(partido, 0)
    rp = rp_sint_final.get(partido, 0)
    total = totales_finales.get(partido, 0)
    votos_pct = votos_pct_sint[partido]
    
    resultados_metodo_sint[partido] = {
        'mr': mr,
        'rp': rp,
        'total': total,
        'votos_pct': votos_pct,
        'escanos_pct': (total / TOTAL_SEATS) * 100
    }
    
    print(f"  {partido:8s}: {total:3d} escaños ({total/TOTAL_SEATS*100:5.2f}%) | MR={mr:3d} RP={rp:3d} | Votos={votos_pct:5.2f}%")

# ==================== COMPARACIÓN ====================
print(f"\n{'='*80}")
print("COMPARACIÓN DE RESULTADOS")
print(f"{'='*80}")

# Crear tabla comparativa
comparacion = []
for partido in PARTIDOS:
    real = resultados_metodo_real[partido]
    sint = resultados_metodo_sint[partido]
    
    comparacion.append({
        'partido': partido,
        'votos_pct': real['votos_pct'],
        
        # Método REAL (scale_siglado)
        'real_mr': real['mr'],
        'real_rp': real['rp'],
        'real_total': real['total'],
        'real_escanos_pct': real['escanos_pct'],
        
        # Método SINTÉTICO (get.max)
        'sint_mr': sint['mr'],
        'sint_rp': sint['rp'],
        'sint_total': sint['total'],
        'sint_escanos_pct': sint['escanos_pct'],
        
        # Diferencias
        'diff_mr': sint['mr'] - real['mr'],
        'diff_rp': sint['rp'] - real['rp'],
        'diff_total': sint['total'] - real['total'],
        'diff_escanos_pct': sint['escanos_pct'] - real['escanos_pct']
    })

df_comparacion = pd.DataFrame(comparacion)

print("\nTabla comparativa (MR):")
print(df_comparacion[['partido', 'real_mr', 'sint_mr', 'diff_mr']].to_string(index=False))

print("\nTabla comparativa (RP):")
print(df_comparacion[['partido', 'real_rp', 'sint_rp', 'diff_rp']].to_string(index=False))

print("\nTabla comparativa (TOTAL):")
print(df_comparacion[['partido', 'votos_pct', 'real_total', 'sint_total', 'diff_total']].to_string(index=False))

# ==================== ÍNDICE DE GALLAGHER ====================
print(f"\n{'='*80}")
print("ÍNDICE DE GALLAGHER (Desproporcionalidad)")
print(f"{'='*80}")

def calcular_gallagher(votos_pct, escanos_pct, partidos):
    """
    Gallagher = sqrt(1/2 * sum((v_i - s_i)^2))
    donde v_i = % votos, s_i = % escaños
    """
    suma = 0.0
    for p in partidos:
        v = votos_pct[p]
        s = escanos_pct[p]
        suma += (v - s) ** 2
    return np.sqrt(suma / 2.0)

# Método REAL
votos_pct_real_dict = {p: resultados_metodo_real[p]['votos_pct'] for p in PARTIDOS}
escanos_pct_real_dict = {p: resultados_metodo_real[p]['escanos_pct'] for p in PARTIDOS}
gallagher_real = calcular_gallagher(votos_pct_real_dict, escanos_pct_real_dict, PARTIDOS)

# Método SINTÉTICO
votos_pct_sint_dict = {p: resultados_metodo_sint[p]['votos_pct'] for p in PARTIDOS}
escanos_pct_sint_dict = {p: resultados_metodo_sint[p]['escanos_pct'] for p in PARTIDOS}
gallagher_sint = calcular_gallagher(votos_pct_sint_dict, escanos_pct_sint_dict, PARTIDOS)

print(f"\n1. MÉTODO REAL (scale_siglado + RP nacional):")
print(f"   Gallagher: {gallagher_real:.3f}")

print(f"\n2. MÉTODO SINTÉTICO (get.max + RP nacional):")
print(f"   Gallagher: {gallagher_sint:.3f}")

print(f"\n3. DIFERENCIA:")
print(f"   Δ Gallagher: {gallagher_sint - gallagher_real:+.3f}")

if gallagher_real < gallagher_sint:
    print(f"\n✓ MÉTODO REAL es más proporcional (Gallagher menor)")
    print(f"   - Diferencia: {gallagher_sint - gallagher_real:.3f}")
    print(f"   - RP NACIONAL es más proporcional que RP DISTRITAL")
    print(f"   - RP nacional compensa mejor las desproporciones del MR")
elif gallagher_sint < gallagher_real:
    print(f"\n✓ MÉTODO SINTÉTICO es más proporcional (Gallagher menor)")
    print(f"   - Diferencia: {gallagher_real - gallagher_sint:.3f}")
    print(f"   - RP DISTRITAL es más proporcional que RP NACIONAL")
    print(f"   - RP distrital distribuye mejor los escaños localmente")
else:
    print(f"\n= Ambos métodos tienen la misma proporcionalidad (Gallagher igual)")

print(f"\nNota:")
print("   - Ambos usan MR idéntico (scale_siglado, 200 escaños)")
print("   - REAL usa RP NACIONAL (Hare sobre votos totales)")
print("   - SINTÉTICO usa RP DISTRITAL (Hare por distrito con magnitudes variables)")
print("   - Ambos aplican topes constitucionales idénticos")
print("   - El Gallagher mide desviación entre % votos y % escaños finales")

# ==================== EXPORTAR RESULTADOS ====================
print(f"\n{'='*80}")
print("EXPORTANDO RESULTADOS")
print(f"{'='*80}")

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_file = f'outputs/comparacion_RP_nacional_vs_RP_distrital_{timestamp}.csv'

# Agregar metadata
metadata = pd.DataFrame([
    {
        'fecha_generacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'metodo_real': 'scale_siglado MR + RP NACIONAL',
        'metodo_sintetico': 'scale_siglado MR + RP DISTRITAL (magnitudes variables)',
        'mr_seats': MR_SEATS,
        'rp_seats': RP_SEATS,
        'total_seats': TOTAL_SEATS,
        'umbral': '3%',
        'topes': 'SÍ (+8%, max 300)',
        'num_distritos_total': len(distrito_votos),
        'magnitudes_rp': f"min={magnitudes_rp.min()}, max={magnitudes_rp.max()}, mean={magnitudes_rp.mean():.2f}",
        'gallagher_real': gallagher_real,
        'gallagher_sintetico': gallagher_sint,
        'diferencia_gallagher': gallagher_sint - gallagher_real,
        'seed': SEED
    }
])

# Combinar metadata y comparación
df_final = pd.concat([
    metadata.assign(tipo='metadata'),
    df_comparacion.assign(tipo='comparacion')
], ignore_index=True)

df_final.to_csv(output_file, index=False)
print(f"\n✓ Resultados exportados a: {output_file}")
print(f"  - Metadata: 1 fila")
print(f"  - Comparación: {len(df_comparacion)} partidos")

print(f"\n{'='*80}")
print("EXPERIMENTO COMPLETADO")
print(f"{'='*80}")
