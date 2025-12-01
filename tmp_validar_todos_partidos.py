"""
Validación detallada: Escaños de TODOS los partidos
Desglosados por MR y RP para comparar con datos oficiales
"""
import sys
sys.path.insert(0, '.')

from engine.procesar_diputados_v2 import procesar_diputados_v2

print("="*80)
print("VALIDACIÓN DETALLADA - TODOS LOS PARTIDOS 2024")
print("Desglose MR + RP = TOTAL")
print("="*80)

# ========== ESCENARIO 1: SIN COALICIÓN ==========
print("\n" + "="*80)
print("ESCENARIO 1: SIN COALICIÓN (MORENA compite solo)")
print("="*80)

resultado_sin = procesar_diputados_v2(
    path_parquet='data/computos_diputados_2024.parquet',
    anio=2024,
    path_siglado='data/siglado-diputados-2024.csv',
    max_seats=500,
    sistema='mixto',
    mr_seats=300,
    rp_seats=200,
    umbral=0.03,
    quota_method='hare',
    usar_coaliciones=False,
    print_debug=False
)

print("\n{:<15} {:>8} {:>8} {:>10} {:>8}".format(
    "PARTIDO", "MR", "RP", "TOTAL", "%"
))
print("-" * 60)

partidos = ['MORENA', 'PT', 'PVEM', 'PAN', 'PRI', 'PRD', 'MC']
total_mr_sin = 0
total_rp_sin = 0
total_sin = 0

for partido in partidos:
    mr = resultado_sin['mr'].get(partido, 0)
    rp = resultado_sin['rp'].get(partido, 0)
    total = resultado_sin['tot'].get(partido, 0)
    pct = (total / 500) * 100
    
    print("{:<15} {:>8} {:>8} {:>10} {:>7.2f}%".format(
        partido, mr, rp, total, pct
    ))
    
    total_mr_sin += mr
    total_rp_sin += rp
    total_sin += total

print("-" * 60)
print("{:<15} {:>8} {:>8} {:>10}".format(
    "TOTAL", total_mr_sin, total_rp_sin, total_sin
))

# Bloque
bloque_sin = resultado_sin['tot']['MORENA'] + resultado_sin['tot']['PT'] + resultado_sin['tot']['PVEM']
print(f"\nBloque MORENA+PT+PVEM: {bloque_sin} ({(bloque_sin/500)*100:.1f}%)")

# ========== ESCENARIO 2: CON COALICIÓN ==========
print("\n" + "="*80)
print("ESCENARIO 2: CON COALICIÓN (Convenio MORENA-PT-PVEM)")
print("="*80)

resultado_con = procesar_diputados_v2(
    path_parquet='data/computos_diputados_2024.parquet',
    anio=2024,
    path_siglado='data/siglado-diputados-2024.csv',
    max_seats=500,
    sistema='mixto',
    mr_seats=300,
    rp_seats=200,
    umbral=0.03,
    quota_method='hare',
    usar_coaliciones=True,
    print_debug=False
)

print("\n{:<15} {:>8} {:>8} {:>10} {:>8}".format(
    "PARTIDO", "MR", "RP", "TOTAL", "%"
))
print("-" * 60)

total_mr_con = 0
total_rp_con = 0
total_con = 0

for partido in partidos:
    mr = resultado_con['mr'].get(partido, 0)
    rp = resultado_con['rp'].get(partido, 0)
    total = resultado_con['tot'].get(partido, 0)
    pct = (total / 500) * 100
    
    print("{:<15} {:>8} {:>8} {:>10} {:>7.2f}%".format(
        partido, mr, rp, total, pct
    ))
    
    total_mr_con += mr
    total_rp_con += rp
    total_con += total

print("-" * 60)
print("{:<15} {:>8} {:>8} {:>10}".format(
    "TOTAL", total_mr_con, total_rp_con, total_con
))

# Bloque
bloque_con = resultado_con['tot']['MORENA'] + resultado_con['tot']['PT'] + resultado_con['tot']['PVEM']
print(f"\nBloque MORENA+PT+PVEM: {bloque_con} ({(bloque_con/500)*100:.1f}%)")

# ========== COMPARACIÓN DIRECTA ==========
print("\n" + "="*80)
print("COMPARACIÓN: DIFERENCIAS ENTRE ESCENARIOS")
print("="*80)

print("\n{:<15} {:>15} {:>15} {:>15}".format(
    "PARTIDO", "SIN COAL (MR)", "CON COAL (MR)", "DIFERENCIA"
))
print("-" * 65)

for partido in partidos:
    mr_sin = resultado_sin['mr'].get(partido, 0)
    mr_con = resultado_con['mr'].get(partido, 0)
    diff = mr_con - mr_sin
    
    print("{:<15} {:>15} {:>15} {:>15}".format(
        partido, mr_sin, mr_con, f"{diff:+d}"
    ))

print("\n" + "="*80)
print("DATOS OFICIALES 2024 (Para que compares)")
print("="*80)
print("""
Según INE, la distribución oficial 2024 fue:
(CON coalición MORENA-PT-PVEM)

MORENA:  236 escaños totales
PT:       51 escaños totales  
PVEM:     76 escaños totales
PAN:      71 escaños totales
PRI:      35 escaños totales
PRD:       1 escaño total
MC:       27 escaños totales
PVEM-PRI: 2 escaños
PAN-PRI-PRD: 1 escaño
-------------------------------
TOTAL:   500 escaños

MR (Mayoría Relativa) según siglado:
MORENA:  148 distritos
PT:       46 distritos
PVEM:     71 distritos
PAN:      33 distritos
PRI:       2 distritos
PRD:       0 distritos
MC:        0 distritos
-------------------------------
TOTAL:   300 distritos

** Nota: Los escaños RP (200) se calculan por fórmula nacional
   y están sujetos al límite de sobrerrepresentación del 8%
""")

print("\n" + "="*80)
print("INSTRUCCIONES PARA VALIDAR")
print("="*80)
print("""
1. Compara los numeros MR del ESCENARIO 2 (CON COALICION) 
   con los datos oficiales del siglado arriba.
   
2. Los totales pueden variar ligeramente porque:
   - El siglado tiene logica de convenio especifica distrito por distrito
   - Hay distritos con coaliciones parciales (PVEM-PRI, PAN-PRI-PRD)
   - El tope del 8% ajusta los escanos RP finales
   
3. Lo CRITICO es que:
   [OK] MORENA tenga menos MR con coalicion que sin coalicion
   [OK] PT y PVEM ganen MR con la coalicion
   [OK] El bloque total mejore con la coalicion
   
4. Si los numeros estan dentro de un margen de +/- 15 distritos,
   la correccion es valida.
""")
