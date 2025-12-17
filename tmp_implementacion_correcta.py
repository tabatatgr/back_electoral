"""
IMPLEMENTACIÓN CORRECTA: Calcular MR por distrito usando siglado correctamente
"""

import pandas as pd
import unicodedata

def normalizar_entidad(texto):
    """Normalizar texto: quitar acentos, mayúsculas, espacios"""
    texto = str(texto).upper().strip()
    # Quitar acentos
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) 
                    if unicodedata.category(c) != 'Mn')
    return texto

# Cargar datos
parquet = pd.read_parquet('data/computos_diputados_2024.parquet')
siglado_raw = pd.read_csv('data/siglado-diputados-2024.csv')

print("=" * 80)
print("CÁLCULO CORRECTO DE MR 2024")
print("=" * 80)

# Normalizar siglado
siglado = siglado_raw.copy()
siglado['entidad_norm'] = siglado['entidad'].apply(normalizar_entidad)
siglado['clave_distrito'] = siglado['entidad_norm'] + '_' + siglado['distrito'].astype(str)

print(f"\n✓ Siglado original: {len(siglado_raw)} filas")
print(f"✓ Después de normalizar: {siglado['clave_distrito'].nunique()} distritos únicos")

# Normalizar parquet
parquet['entidad_norm'] = parquet['ENTIDAD'].apply(normalizar_entidad)
parquet['clave_distrito'] = parquet['entidad_norm'] + '_' + parquet['DISTRITO'].astype(str)

print(f"✓ Parquet: {len(parquet)} distritos")

# Verificar
distritos_parquet = set(parquet['clave_distrito'])
distritos_siglado = set(siglado['clave_distrito'])

print(f"\nDistritos en siglado: {len(distritos_siglado)}")
print(f"Distritos sin coalición: {len(distritos_parquet - distritos_siglado)}")

print("\n" + "=" * 80)
print("CALCULAR GANADORES POR DISTRITO")
print("=" * 80)

resultados_mr = {}

for idx, row in parquet.iterrows():
    entidad = row['entidad_norm']
    distrito = row['DISTRITO']
    clave = row['clave_distrito']
    
    # ¿Este distrito tiene coaliciones en el siglado?
    filas_siglado = siglado[siglado['clave_distrito'] == clave]
    
    if len(filas_siglado) == 0:
        # NO hay coalición → competencia individual
        partidos = ['MORENA', 'PAN', 'PRI', 'PRD', 'PT', 'PVEM', 'MC']
        votos = {p: row.get(p, 0) for p in partidos}
        ganador = max(votos, key=votos.get)
        
        resultados_mr[ganador] = resultados_mr.get(ganador, 0) + 1
        
        if idx < 5:  # Debug primeros 5
            print(f"\n{clave}: SIN coalición")
            print(f"   Ganador: {ganador} ({votos[ganador]:,.0f} votos)")
    
    else:
        # SÍ hay coalición → sumar votos por coalición
        
        # Identificar qué coaliciones compiten
        coaliciones_distrito = {}
        
        for _, fila_siglado in filas_siglado.iterrows():
            coal_nombre = fila_siglado['coalicion']
            partido_siglado = fila_siglado['grupo_parlamentario']
            
            if coal_nombre not in coaliciones_distrito:
                coaliciones_distrito[coal_nombre] = {'partido': partido_siglado, 'partidos_coalicion': []}
        
        # Determinar qué partidos forman cada coalición
        # FCM = PAN + PRI + PRD
        # SHH = MORENA + PT + PVEM
        for coal_nombre in coaliciones_distrito.keys():
            if 'FUERZA' in coal_nombre.upper():
                coaliciones_distrito[coal_nombre]['partidos_coalicion'] = ['PAN', 'PRI', 'PRD']
            elif 'SIGAMOS' in coal_nombre.upper():
                coaliciones_distrito[coal_nombre]['partidos_coalicion'] = ['MORENA', 'PT', 'PVEM']
        
        # Calcular votos por coalición
        votos_coaliciones = {}
        for coal_nombre, info in coaliciones_distrito.items():
            partidos_coal = info['partidos_coalicion']
            votos_total = sum(row.get(p, 0) for p in partidos_coal)
            votos_coaliciones[coal_nombre] = votos_total
        
        # MC compite individual
        votos_mc = row.get('MC', 0)
        
        # Determinar ganador
        ganador_final = None
        
        if votos_coaliciones:
            # Comparar coaliciones vs MC
            max_coal_nombre = max(votos_coaliciones, key=votos_coaliciones.get)
            max_coal_votos = votos_coaliciones[max_coal_nombre]
            
            if max_coal_votos > votos_mc:
                # Ganó coalición → asignar al partido siglado
                ganador_final = coaliciones_distrito[max_coal_nombre]['partido']
            else:
                # Ganó MC
                ganador_final = 'MC'
        elif votos_mc > 0:
            ganador_final = 'MC'
        
        if ganador_final:
            resultados_mr[ganador_final] = resultados_mr.get(ganador_final, 0) + 1
        
        if idx < 5:  # Debug primeros 5
            print(f"\n{clave}: CON coalición")
            for coal, votos in votos_coaliciones.items():
                partido = coaliciones_distrito[coal]['partido']
                print(f"   {coal}: {votos:,.0f} votos → {partido}")
            print(f"   MC: {votos_mc:,.0f} votos")
            print(f"   Ganador: {ganador_final}")

print("\n" + "=" * 80)
print("RESULTADOS FINALES - MR POR PARTIDO")
print("=" * 80)

print(f"\n{'Partido':<10} {'MR':>10}")
print("-" * 25)
for partido in sorted(resultados_mr.keys()):
    print(f"{partido:<10} {resultados_mr[partido]:>10}")

total_mr = sum(resultados_mr.values())
print("-" * 25)
print(f"{'TOTAL':<10} {total_mr:>10}")

if total_mr != 300:
    print(f"\n⚠️  ERROR: Total MR = {total_mr}, debería ser 300")

print("\n" + "=" * 80)
print("Estos son los MR. Para comparar con datos oficiales necesito sumarles RP")
print("=" * 80)
