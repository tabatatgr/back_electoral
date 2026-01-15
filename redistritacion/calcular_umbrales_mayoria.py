"""
Calcula umbrales de mayoría simple y calificada para cada escenario electoral.

ENFOQUE SIMPLE:
1. Mayoría simple = 201 escaños (50% + 1 de 400)
2. Mayoría calificada = 267 escaños (2/3 de 400)
3. Calcular cuántos distritos MR se necesitan ganar
4. Si no alcanza con solo MR, calcular votos nacionales necesarios para RP
"""

import pandas as pd


def calcular_umbrales(nombre_escenario, mr_seats, rp_seats, tiene_topes):
    """
    Calcula umbrales de mayoría para un escenario.
    
    LÓGICA:
    - Primero intentar alcanzar mayoría SOLO con MR
    - Si no alcanza, calcular cuántos RP adicionales se necesitan
    - Calcular % de votos nacionales necesarios para esos RP
    """
    total_seats = mr_seats + rp_seats
    
    # Mayorías (siempre sobre 400)
    mayoria_simple = 201  # 50% + 1
    mayoria_calificada = 267  # 2/3
    
    # ========== MAYORÍA SIMPLE ==========
    # CASO 1: Máximo MR (ganar todos los distritos posibles)
    if mayoria_simple <= mr_seats:
        # Se puede lograr SOLO con MR
        mr_simple_max = mayoria_simple
        rp_simple_max = 0
        votos_simple_max = "No necesarios"
    else:
        # Se necesitan TODOS los MR + algunos RP
        mr_simple_max = mr_seats
        rp_simple_max = mayoria_simple - mr_seats
        
        # Calcular votos nacionales para esos RP
        votos_pct_base = (rp_simple_max / rp_seats) * 100
        
        if tiene_topes:
            votos_pct_min = max(3.0, ((mr_simple_max + rp_simple_max) / total_seats - 0.08) * 100)
            votos_simple_max = f"{votos_pct_min:.1f}%"
        else:
            votos_simple_max = f"~{votos_pct_base:.1f}%"
    
    # CASO 2: Mínimo MR (maximizar RP con alta votación)
    # Estrategia: ganar pocos distritos pero mucha votación nacional
    if tiene_topes:
        # Con topes: máximo (votos% + 8%) * 400 escaños
        # Para 201 escaños: (votos% + 8%) * 400 >= 201
        # votos% >= 50.25% - 8% = 42.25%
        votos_necesarios_simple = (mayoria_simple / total_seats - 0.08)
        votos_necesarios_simple = max(0.03, votos_necesarios_simple)  # Mínimo 3% umbral
        
        # Si tienes votos_necesarios_simple%, ganarías aprox ese % de distritos MR
        mr_simple_min = int(votos_necesarios_simple * mr_seats)
        rp_simple_min = int(votos_necesarios_simple * rp_seats)
        # Total aproximado
        total_aprox = mr_simple_min + rp_simple_min
        # Ajustar para llegar exacto a 201
        if total_aprox < mayoria_simple:
            rp_simple_min += (mayoria_simple - total_aprox)
        
        votos_simple_min = f"{votos_necesarios_simple*100:.1f}%"
    else:
        # Sin topes, se puede lograr con ~30-35% de votos
        # Con 35% votos → ~35% de MR + mucho más RP (sin límite)
        # Puede llegar a 60%+ de escaños con solo 35% votos
        votos_necesarios_simple = 0.30  # Aproximación conservadora
        mr_simple_min = int(votos_necesarios_simple * mr_seats * 0.9)  # Un poco menos
        rp_simple_min = mayoria_simple - mr_simple_min
        votos_simple_min = f"~{votos_necesarios_simple*100:.0f}%"
    
    # ========== MAYORÍA CALIFICADA ==========
    # CASO 1: Máximo MR (ganar todos los distritos posibles)
    if mayoria_calificada <= mr_seats:
        # Se puede lograr SOLO con MR
        mr_calificada_max = mayoria_calificada
        rp_calificada_max = 0
        votos_calificada_max = "No necesarios"
    else:
        # Se necesitan TODOS los MR + muchos RP
        mr_calificada_max = mr_seats
        rp_calificada_max = mayoria_calificada - mr_seats
        
        # Calcular votos nacionales
        votos_pct_base = (rp_calificada_max / rp_seats) * 100
        
        if tiene_topes:
            votos_pct_min = max(3.0, ((mr_calificada_max + rp_calificada_max) / total_seats - 0.08) * 100)
            votos_calificada_max = f"{votos_pct_min:.1f}%"
        else:
            votos_calificada_max = f"~{votos_pct_base:.1f}%"
    
    # CASO 2: Mínimo MR (maximizar RP con alta votación)
    if tiene_topes:
        # Para 267 escaños: (votos% + 8%) * 400 >= 267
        # votos% >= 66.75% - 8% = 58.75%
        votos_necesarios_calif = (mayoria_calificada / total_seats - 0.08)
        votos_necesarios_calif = max(0.03, votos_necesarios_calif)
        
        mr_calificada_min = int(votos_necesarios_calif * mr_seats)
        rp_calificada_min = int(votos_necesarios_calif * rp_seats)
        total_aprox = mr_calificada_min + rp_calificada_min
        if total_aprox < mayoria_calificada:
            rp_calificada_min += (mayoria_calificada - total_aprox)
        
        votos_calificada_min = f"{votos_necesarios_calif*100:.1f}%"
    else:
        # Sin topes, con ~45-50% votos puedes llegar a 67%+ escaños
        votos_necesarios_calif = 0.45
        mr_calificada_min = int(votos_necesarios_calif * mr_seats * 0.85)
        rp_calificada_min = mayoria_calificada - mr_calificada_min
        votos_calificada_min = f"~{votos_necesarios_calif*100:.0f}%"
    
    return {
        'ESCENARIO': nombre_escenario,
        'MR': mr_seats,
        'RP': rp_seats,
        'TOTAL': total_seats,
        'TOPES': 'SÍ' if tiene_topes else 'NO',
        
        # MAYORÍA SIMPLE - MÁXIMO MR
        'SIMPLE_MR_MAX': mr_simple_max,
        'SIMPLE_RP_MAX': rp_simple_max,
        'SIMPLE_VOTOS_MAX': votos_simple_max,
        
        # MAYORÍA SIMPLE - MÍNIMO MR
        'SIMPLE_MR_MIN': mr_simple_min,
        'SIMPLE_RP_MIN': rp_simple_min,
        'SIMPLE_VOTOS_MIN': votos_simple_min,
        
        # MAYORÍA CALIFICADA - MÁXIMO MR
        'CALIFICADA_MR_MAX': mr_calificada_max,
        'CALIFICADA_RP_MAX': rp_calificada_max,
        'CALIFICADA_VOTOS_MAX': votos_calificada_max,
        
        # MAYORÍA CALIFICADA - MÍNIMO MR
        'CALIFICADA_MR_MIN': mr_calificada_min,
        'CALIFICADA_RP_MIN': rp_calificada_min,
        'CALIFICADA_VOTOS_MIN': votos_calificada_min,
    }


def main():
    print("="*100)
    print("UMBRALES DE MAYORÍA PARA ESCENARIOS ELECTORALES")
    print("="*100)
    print("\nNOTA: Usando redistritación geográfica con municipios como semillas")
    print("="*100)
    
    escenarios = [
        {
            'nombre': '300-100 CON TOPES',
            'mr': 300,
            'rp': 100,
            'topes': True
        },
        {
            'nombre': '200-200 SIN TOPES',
            'mr': 200,
            'rp': 200,
            'topes': False
        },
        {
            'nombre': '240-160 SIN TOPES',
            'mr': 240,
            'rp': 160,
            'topes': False
        },
        {
            'nombre': '240-160 CON TOPES',
            'mr': 240,
            'rp': 160,
            'topes': True
        }
    ]
    
    resultados = []
    for esc in escenarios:
        res = calcular_umbrales(
            nombre_escenario=esc['nombre'],
            mr_seats=esc['mr'],
            rp_seats=esc['rp'],
            tiene_topes=esc['topes']
        )
        resultados.append(res)
    
    # Crear DataFrame
    df = pd.DataFrame(resultados)
    
    # Guardar CSV
    output_path = 'redistritacion/outputs/umbrales_mayoria.csv'
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n✓ Tabla guardada en: {output_path}\n")
    
    # Imprimir resultados por escenario
    for res in resultados:
        print(f"\n{'='*100}")
        print(f"ESCENARIO: {res['ESCENARIO']}")
        print(f"{'='*100}")
        print(f"Configuración: {res['MR']} MR + {res['RP']} RP = {res['TOTAL']} escaños")
        print(f"Topes de sobrerrepresentación: {res['TOPES']}")
        
        print(f"\n{'─'*100}")
        print(f"MAYORÍA SIMPLE (201 escaños = 50.25%)")
        print(f"{'─'*100}")
        print(f"\n  ESTRATEGIA 1: Máximo MR (ganar más distritos)")
        if res['SIMPLE_RP_MAX'] == 0:
            print(f"    ✓ Ganar {res['SIMPLE_MR_MAX']} distritos MR")
            print(f"    ✓ No necesitas RP")
        else:
            print(f"    ✓ Ganar TODOS los {res['SIMPLE_MR_MAX']} distritos MR")
            print(f"    ✓ Más {res['SIMPLE_RP_MAX']} escaños RP")
            print(f"    ✓ Votación nacional: {res['SIMPLE_VOTOS_MAX']}")
        
        print(f"\n  ESTRATEGIA 2: Mínimo MR (maximizar votación nacional + RP)")
        print(f"    ✓ Ganar mínimo {res['SIMPLE_MR_MIN']} distritos MR")
        print(f"    ✓ Más {res['SIMPLE_RP_MIN']} escaños RP")
        print(f"    ✓ Votación nacional necesaria: {res['SIMPLE_VOTOS_MIN']}")
        
        print(f"\n{'─'*100}")
        print(f"MAYORÍA CALIFICADA (267 escaños = 66.75% para reformas constitucionales)")
        print(f"{'─'*100}")
        print(f"\n  ESTRATEGIA 1: Máximo MR (ganar más distritos)")
        if res['CALIFICADA_RP_MAX'] == 0:
            print(f"    ✓ Ganar {res['CALIFICADA_MR_MAX']} distritos MR")
            print(f"    ✓ No necesitas RP")
        else:
            print(f"    ✓ Ganar TODOS los {res['CALIFICADA_MR_MAX']} distritos MR")
            print(f"    ✓ Más {res['CALIFICADA_RP_MAX']} escaños RP")
            print(f"    ✓ Votación nacional: {res['CALIFICADA_VOTOS_MAX']}")
        
        print(f"\n  ESTRATEGIA 2: Mínimo MR (maximizar votación nacional + RP)")
        print(f"    ✓ Ganar mínimo {res['CALIFICADA_MR_MIN']} distritos MR")
        print(f"    ✓ Más {res['CALIFICADA_RP_MIN']} escaños RP")
        print(f"    ✓ Votación nacional necesaria: {res['CALIFICADA_VOTOS_MIN']}")
    
    # Tabla comparativa final
    print(f"\n\n{'='*100}")
    print("TABLA COMPARATIVA DE UMBRALES")
    print(f"{'='*100}\n")
    
    print("MAYORÍA SIMPLE (201 escaños):")
    print("-" * 100)
    tabla_simple = pd.DataFrame({
        'ESCENARIO': [r['ESCENARIO'] for r in resultados],
        'TOPES': [r['TOPES'] for r in resultados],
        'MR_MAX': [r['SIMPLE_MR_MAX'] for r in resultados],
        'RP_MAX': [r['SIMPLE_RP_MAX'] for r in resultados],
        'VOTOS_MAX': [r['SIMPLE_VOTOS_MAX'] for r in resultados],
        'MR_MIN': [r['SIMPLE_MR_MIN'] for r in resultados],
        'RP_MIN': [r['SIMPLE_RP_MIN'] for r in resultados],
        'VOTOS_MIN': [r['SIMPLE_VOTOS_MIN'] for r in resultados],
    })
    print(tabla_simple.to_string(index=False))
    
    print(f"\n\nMAYORÍA CALIFICADA (267 escaños):")
    print("-" * 100)
    tabla_calificada = pd.DataFrame({
        'ESCENARIO': [r['ESCENARIO'] for r in resultados],
        'TOPES': [r['TOPES'] for r in resultados],
        'MR_MAX': [r['CALIFICADA_MR_MAX'] for r in resultados],
        'RP_MAX': [r['CALIFICADA_RP_MAX'] for r in resultados],
        'VOTOS_MAX': [r['CALIFICADA_VOTOS_MAX'] for r in resultados],
        'MR_MIN': [r['CALIFICADA_MR_MIN'] for r in resultados],
        'RP_MIN': [r['CALIFICADA_RP_MIN'] for r in resultados],
        'VOTOS_MIN': [r['CALIFICADA_VOTOS_MIN'] for r in resultados],
    })
    print(tabla_calificada.to_string(index=False))
    
    print(f"\n\n{'='*100}")
    print("NOTAS IMPORTANTES")
    print(f"{'='*100}")
    print("""
REDISTRITACIÓN GEOGRÁFICA:
- Los escenarios 200-200, 240-160 usan redistritación con municipios como semillas
- Distritos geográficamente compactos y contiguos
- El escenario 300-100 usa la cartografía actual del INE

MAYORÍA SIMPLE (201 escaños):
- Controlar la agenda legislativa
- Aprobar leyes ordinarias
- Elegir mesa directiva

MAYORÍA CALIFICADA (267 escaños):
- Reformas constitucionales
- Juicio político
- Aprobación de tratados internacionales  
- Leyes orgánicas

CON TOPES (+8%):
- Límite constitucional: un partido no puede tener más de votación% + 8% de escaños
- Ejemplo: con 42% de votos, máximo 50% de escaños (200/400)

SIN TOPES:
- No hay límite de sobrerrepresentación
- Permite mayor desproporción entre votos y escaños
- Favorece al partido ganador
""")
    
    print(f"\n✓ Análisis completo guardado en: {output_path}\n")


if __name__ == '__main__':
    main()
