"""
ANÁLISIS: ¿Qué dice realmente el siglado sobre las coaliciones?
"""

import pandas as pd
import unicodedata

def normalizar_entidad(texto):
    """Normalizar texto"""
    texto = str(texto).upper().strip()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) 
                    if unicodedata.category(c) != 'Mn')
    return texto

siglado = pd.read_csv('data/siglado-diputados-2024.csv')
siglado['entidad_norm'] = siglado['entidad'].apply(normalizar_entidad)
siglado['clave'] = siglado['entidad_norm'] + '_' + siglado['distrito'].astype(str)

print("=" * 80)
print("¿QUÉ DICE EL SIGLADO REALMENTE?")
print("=" * 80)

# Ejemplo: ver algunos distritos con detalle
ejemplos = [
    ('AGUASCALIENTES', 1),
    ('BAJA CALIFORNIA', 1),
    ('CAMPECHE', 1),
    ('CHIAPAS', 1),
]

for entidad, distrito in ejemplos:
    ent_norm = normalizar_entidad(entidad)
    clave = f"{ent_norm}_{distrito}"
    
    filas = siglado[siglado['clave'] == clave]
    
    print(f"\n{entidad} DISTRITO {distrito}:")
    print("-" * 60)
    
    for _, fila in filas.iterrows():
        coal = fila['coalicion']
        partido = fila['grupo_parlamentario']
        print(f"  Coalición: {coal}")
        print(f"  Si gana → escaño para: {partido}")
        print()

print("\n" + "=" * 80)
print("LA PREGUNTA CRÍTICA:")
print("=" * 80)
print("¿El siglado dice QUÉ PARTIDOS FORMAN la coalición en ese distrito?")
print("O solo dice A QUIÉN VA EL ESCAÑO si esa coalición gana?")
print()
print("Según tu explicación: el siglado dice A QUIÉN VA EL ESCAÑO")
print("Pero entonces... ¿cómo sé QUÉ votos sumar para esa coalición?")
print()
print("Ejemplo AGUASCALIENTES_1:")
print("  Siglado dice: FUERZA Y CORAZON POR MEXICO → PRI")
print("  ¿Debo sumar PAN+PRI+PRD?")
print("  ¿O solo PRI?")
print("  ¿O PAN+PRI (porque PRD no aparece en el siglado)?")
