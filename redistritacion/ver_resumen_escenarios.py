"""
Ver resumen comparativo de los 3 escenarios
"""
import pandas as pd

df = pd.read_csv('redistritacion/outputs/comparacion_escenarios_completa.csv')

print("\n" + "="*100)
print("RESUMEN COMPARATIVO - ELECCIONES 2024")
print("="*100)

for esc in ['300-100 CON TOPES', '200-200 SIN TOPES', '240-160 SIN TOPES']:
    print(f"\n{'─'*100}")
    print(f"{esc}")
    print(f"{'─'*100}")
    
    subset = df[(df['AÑO'] == 2024) & (df['ESCENARIO'] == esc)][
        ['PARTIDO', 'ESCAÑOS_MR', 'ESCAÑOS_RP', 'ESCAÑOS_TOTAL', 'PCT_ESCAÑOS']
    ].sort_values('ESCAÑOS_TOTAL', ascending=False)
    
    print(subset.to_string(index=False))
    print(f"\nTOTAL: {subset['ESCAÑOS_TOTAL'].sum()} escaños")

print("\n" + "="*100)
print("RESUMEN COMPARATIVO - ELECCIONES 2021")
print("="*100)

for esc in ['300-100 CON TOPES', '200-200 SIN TOPES', '240-160 SIN TOPES']:
    print(f"\n{'─'*100}")
    print(f"{esc}")
    print(f"{'─'*100}")
    
    subset = df[(df['AÑO'] == 2021) & (df['ESCENARIO'] == esc)][
        ['PARTIDO', 'ESCAÑOS_MR', 'ESCAÑOS_RP', 'ESCAÑOS_TOTAL', 'PCT_ESCAÑOS']
    ].sort_values('ESCAÑOS_TOTAL', ascending=False)
    
    print(subset.to_string(index=False))
    print(f"\nTOTAL: {subset['ESCAÑOS_TOTAL'].sum()} escaños")

# Impacto MORENA comparativo
print("\n" + "="*100)
print("IMPACTO EN MORENA POR ESCENARIO")
print("="*100)

morena_data = df[df['PARTIDO'] == 'MORENA'][['AÑO', 'ESCENARIO', 'ESCAÑOS_MR', 'ESCAÑOS_RP', 'ESCAÑOS_TOTAL', 'PCT_ESCAÑOS']]
print(morena_data.to_string(index=False))

print("\n" + "="*100)
print("HALLAZGOS CLAVE:")
print("="*100)
print("""
1. 300-100 CON TOPES (baseline):
   - Limita sobrerrepresentación al +8%
   - MORENA 2024: 201 escaños (50.25%) con 42.6% de votos
   - Topes activos impiden mayoría calificada
   
2. 200-200 SIN TOPES (reforma equilibrada):
   - Sin límite de sobrerrepresentación
   - MORENA 2024: 259 escaños (64.75%) - ¡MAYORÍA CALIFICADA!
   - Más proporcional en RP (200 vs 100)
   
3. 240-160 SIN TOPES (reforma intermedia):
   - Híbrido entre baseline y 200-200
   - MORENA 2024: 273 escaños (68.25%) - ¡MAYORÍA CALIFICADA AMPLIA!
   - Mayor representación MR que 200-200
   
CONCLUSIÓN:
- Eliminar topes permite mayorías calificadas con <50% votos
- Redistritación a 200 MR reduce ventaja de MORENA en MR
- 240 MR sin topes = máxima sobrerrepresentación para MORENA
""")
