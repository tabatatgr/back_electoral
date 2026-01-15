"""
Analiza los límites constitucionales para que UN SOLO PARTIDO (sin coalición)
logre mayoría calificada en cada escenario.

En los escenarios CON TOPES:
- Límite de sobrerrepresentación: 8%
- Fórmula: tope = (votos_partido + 8%) * total_escaños

Para mayoría calificada (267/400 = 66.75%), calculamos:
- ¿Qué % de votos necesita un partido para que su tope permita 267 escaños?
- Fórmula: votos_min = (267/400) - 8% = 66.75% - 8% = 58.75%

En los escenarios SIN TOPES:
- Sin límite de sobrerrepresentación
- Solo limitado por competencia y 3% umbral nacional
"""

import pandas as pd

def analizar_limites_partido_individual():
    """
    Calcula límites para UN PARTIDO INDIVIDUAL (sin coalición).
    """
    
    escenarios = [
        {
            'nombre': '300-100 CON TOPES',
            'mr': 300,
            'rp': 100,
            'total': 400,
            'topes': True,
            'max_sobrerep': 8.0
        },
        {
            'nombre': '200-200 SIN TOPES',
            'mr': 200,
            'rp': 200,
            'total': 400,
            'topes': False,
            'max_sobrerep': None
        },
        {
            'nombre': '240-160 SIN TOPES',
            'mr': 240,
            'rp': 160,
            'total': 400,
            'topes': False,
            'max_sobrerep': None
        },
        {
            'nombre': '240-160 CON TOPES',
            'mr': 240,
            'rp': 160,
            'total': 400,
            'topes': True,
            'max_sobrerep': 8.0
        }
    ]
    
    print("="*100)
    print("ANÁLISIS: LÍMITES PARA UN PARTIDO INDIVIDUAL (SIN COALICIÓN)")
    print("="*100)
    
    resultados = []
    
    for esc in escenarios:
        print(f"\n{'─'*100}")
        print(f"{esc['nombre']}")
        print(f"  Configuración: {esc['mr']} MR + {esc['rp']} RP = {esc['total']} escaños")
        print(f"  Topes: {'SÍ' if esc['topes'] else 'NO'}")
        print(f"{'─'*100}")
        
        # MAYORÍA SIMPLE (201 escaños = 50.25%)
        mayoria_simple = 201
        pct_mayoria_simple = mayoria_simple / esc['total'] * 100
        
        # MAYORÍA CALIFICADA (267 escaños = 66.75%)
        mayoria_calificada = 267
        pct_mayoria_calificada = mayoria_calificada / esc['total'] * 100
        
        print(f"\n📊 MAYORÍA SIMPLE ({mayoria_simple} escaños = {pct_mayoria_simple:.2f}%)")
        print(f"{'─'*100}")
        
        if esc['topes']:
            # CON TOPES: tope = (votos + 8%) * 400
            # Para 201 escaños: votos + 8% >= 201/400 = 50.25%
            # votos >= 50.25% - 8% = 42.25%
            votos_min_simple = pct_mayoria_simple - esc['max_sobrerep']
            print(f"  ✅ CON TOPES (8%):")
            print(f"     Fórmula: tope = (votos + 8%) × 400")
            print(f"     Para {mayoria_simple} escaños: votos + 8% ≥ {pct_mayoria_simple:.2f}%")
            print(f"     → Votos mínimos: {votos_min_simple:.2f}%")
            print(f"     → FACTIBLE: Un partido con ≥{votos_min_simple:.2f}% puede lograr mayoría simple")
        else:
            # SIN TOPES: depende de competencia
            print(f"  ✅ SIN TOPES:")
            print(f"     No hay límite de sobrerrepresentación")
            print(f"     Depende de: competencia, distribución geográfica, umbral 3%")
            print(f"     → Teóricamente: un partido podría ganar 201+ escaños con <50% votos")
            print(f"     → En la práctica: requiere dominio en MR ({esc['mr']} distritos)")
        
        print(f"\n📊 MAYORÍA CALIFICADA ({mayoria_calificada} escaños = {pct_mayoria_calificada:.2f}%)")
        print(f"{'─'*100}")
        
        if esc['topes']:
            # CON TOPES: tope = (votos + 8%) * 400
            # Para 267 escaños: votos + 8% >= 267/400 = 66.75%
            # votos >= 66.75% - 8% = 58.75%
            votos_min_calificada = pct_mayoria_calificada - esc['max_sobrerep']
            print(f"  ⚠️  CON TOPES (8%):")
            print(f"     Fórmula: tope = (votos + 8%) × 400")
            print(f"     Para {mayoria_calificada} escaños: votos + 8% ≥ {pct_mayoria_calificada:.2f}%")
            print(f"     → Votos mínimos: {votos_min_calificada:.2f}%")
            print(f"")
            print(f"     🚨 CONCLUSIÓN: Un partido individual necesitaría ≥{votos_min_calificada:.2f}% de votos")
            print(f"        Históricamente IMPOSIBLE en México (ningún partido ha alcanzado ~59% solo)")
            print(f"        Máximo histórico: PRI ~48% (1991), MORENA ~43% (2024)")
            print(f"")
            print(f"     💡 Para mayoría calificada CON TOPES: SE REQUIERE COALICIÓN")
            
            factible_calificada = "NO - REQUIERE COALICIÓN"
        else:
            # SIN TOPES: depende de competencia y MR máximo
            max_mr_posible = esc['mr']
            rp_disponible = esc['rp']
            
            # Si gana TODOS los MR, necesita complementar con RP
            rp_necesario = mayoria_calificada - max_mr_posible
            
            print(f"  ✅ SIN TOPES:")
            print(f"     No hay límite de sobrerrepresentación")
            print(f"     MR máximo posible: {max_mr_posible} distritos")
            print(f"     RP disponible: {rp_disponible} escaños")
            print(f"")
            print(f"     Estrategia: Ganar todos los {max_mr_posible} MR + {rp_necesario} RP")
            
            if rp_necesario <= rp_disponible:
                # Calcular % votos para RP
                # Simplificación: si gana todos los MR, tiene ~{max_mr_posible/total}% de "presencia"
                # Necesita ~{rp_necesario/rp_disponible}% del RP
                
                pct_rp_necesario = rp_necesario / rp_disponible * 100
                
                print(f"     → Necesita {rp_necesario}/{rp_disponible} RP ({pct_rp_necesario:.1f}% del RP)")
                print(f"")
                print(f"     🤔 FACTIBILIDAD:")
                print(f"        - Ganar TODOS los {max_mr_posible} distritos MR: EXTREMADAMENTE DIFÍCIL")
                print(f"        - Históricamente: ningún partido ha ganado >85% de distritos solo")
                print(f"        - Ejemplo 2024: MORENA ganó 236/300 MR (78.7%) en coalición")
                print(f"")
                print(f"     💡 Conclusión: Técnicamente posible, prácticamente REQUIERE COALICIÓN")
                
                factible_calificada = "TÉCNICAMENTE SÍ, PRÁCTICAMENTE NO"
            else:
                print(f"     → ¡IMPOSIBLE! Incluso ganando todos los {max_mr_posible} MR,")
                print(f"       faltan {rp_necesario - rp_disponible} escaños (no hay suficiente RP)")
                
                factible_calificada = "NO - MATEMÁTICAMENTE IMPOSIBLE"
        
        # Guardar resultado
        resultados.append({
            'ESCENARIO': esc['nombre'],
            'MR': esc['mr'],
            'RP': esc['rp'],
            'TOTAL': esc['total'],
            'TOPES': 'SÍ' if esc['topes'] else 'NO',
            'MAYORIA_SIMPLE_FACTIBLE': 'SÍ',
            'MAYORIA_CALIFICADA_FACTIBLE': factible_calificada,
            'VOTOS_MIN_SIMPLE': f"{votos_min_simple:.2f}%" if esc['topes'] else 'Variable',
            'VOTOS_MIN_CALIFICADA': f"{votos_min_calificada:.2f}%" if esc['topes'] else 'Variable'
        })
    
    # Resumen final
    print("\n" + "="*100)
    print("RESUMEN: FACTIBILIDAD PARA PARTIDO INDIVIDUAL")
    print("="*100)
    
    df = pd.DataFrame(resultados)
    print("\n" + df.to_string(index=False))
    
    # Guardar
    output_path = 'redistritacion/outputs/limites_partido_individual.csv'
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n✓ Guardado en: {output_path}")
    
    # Conclusiones generales
    print("\n" + "="*100)
    print("CONCLUSIONES GENERALES")
    print("="*100)
    print("""
📌 MAYORÍA SIMPLE (201 escaños):
   ✅ FACTIBLE en todos los escenarios para un partido individual fuerte
   - CON TOPES: requiere ≥42.25% de votos (históricamente alcanzable)
   - SIN TOPES: más fácil, posible con menor % de votos

📌 MAYORÍA CALIFICADA (267 escaños):
   
   🔴 CON TOPES (300-100, 240-160 CON TOPES):
      ❌ IMPOSIBLE para partido individual
      Razón: Requiere ≥58.75% de votos
      Máximo histórico: ~48% (PRI 1991), ~43% (MORENA 2024)
      → SE REQUIERE COALICIÓN OBLIGATORIAMENTE
   
   🟡 SIN TOPES (200-200, 240-160 SIN TOPES):
      ⚠️  TÉCNICAMENTE POSIBLE, PRÁCTICAMENTE IMPROBABLE
      Requiere: Ganar >90% de distritos MR + dominar RP
      Ningún partido ha logrado esto históricamente sin coalición
      → EN LA PRÁCTICA, TAMBIÉN REQUIERE COALICIÓN

💡 IMPLICACIÓN POLÍTICA:
   Los topes de sobrerrepresentación (8%) funcionan como barrera
   constitucional que OBLIGA a la formación de coaliciones para
   lograr mayorías calificadas, promoviendo consenso político.
    """)


if __name__ == '__main__':
    analizar_limites_partido_individual()
