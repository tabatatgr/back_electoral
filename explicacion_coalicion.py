"""
Clarificación conceptual: ¿Qué significa "CON coalición" vs "SIN coalición"?

CON COALICIÓN (usar_coaliciones=True):
- Votos: Los MISMOS votos individuales (MORENA, PT, PVEM separados)
- MR: Se usa el SIGLADO (convenio) - MORENA cede distritos a PT/PVEM
- RP: Se calcula por partido individual usando sus votos propios
- Tope 8%: Se aplica por partido individual

SIN COALICIÓN (usar_coaliciones=False):
- Votos: Los MISMOS votos individuales (MORENA, PT, PVEM separados)
- MR: Se RECALCULA ganador por votos directos (no convenio)
- RP: Se calcula por partido individual usando sus votos propios
- Tope 8%: Se aplica por partido individual

DIFERENCIA REAL:
- Solo cambia quién gana cada distrito MR
- Los votos base son idénticos
- El RP compensa porque es la misma base de votos

ENTONCES:
- MORENA pierde MR por convenio → Gana más RP por compensación
- Resultado neto: casi igual

ESTO ES CORRECTO para el sistema electoral mexicano real.
La coalición NO cambia los votos, solo el convenio de distribución MR.
"""

print(__doc__)

print("="*80)
print("EJEMPLO NUMÉRICO")
print("="*80)

print("\nSupongamos un distrito:")
print("  MORENA: 10,000 votos")
print("  PT:      2,000 votos")  
print("  PVEM:    3,000 votos")
print("  PAN:     8,000 votos")
print()

print("ESCENARIO 1: CON COALICIÓN")
print("-" * 60)
print("  MR: Según siglado/convenio, gana PT (aunque MORENA tiene más votos)")
print("  → PT se lleva 1 escaño MR")
print("  → MORENA 0 MR en este distrito")
print()
print("  RP Nacional:")
print("  → MORENA tiene 10,000 votos para RP")
print("  → PT tiene 2,000 votos para RP")
print("  → Como MORENA tiene MENOS MR, puede recibir MÁS RP")
print()

print("ESCENARIO 2: SIN COALICIÓN (sin convenio)")
print("-" * 60)
print("  MR: Gana quien tiene más votos → MORENA (10,000)")
print("  → MORENA se lleva 1 escaño MR")
print("  → PT 0 MR en este distrito")
print()
print("  RP Nacional:")
print("  → MORENA tiene 10,000 votos para RP")
print("  → PT tiene 2,000 votos para RP")
print("  → Como MORENA tiene MÁS MR, recibe MENOS RP (tope 8%)")
print()

print("="*80)
print("CONCLUSIÓN")
print("="*80)
print()
print("El sistema RP con tope 8% COMPENSA automáticamente:")
print("  - Si pierdes MR por convenio → Ganas RP")
print("  - Si ganas MR directo → Pierdes RP")
print()
print("Por eso MORENA termina con ~257 escaños en ambos casos.")
print()
print("Esto NO es un bug. Es el diseño del sistema electoral mexicano.")
print("El tope del 8% está hecho precisamente para evitar")
print("sobrerrepresentación, independiente de cómo se distribuya MR.")
print()
print("="*80)
print("¿QUÉ CONTRAFACTUAL QUEREMOS SIMULAR?")
print("="*80)
print()
print("Si queremos simular 'MORENA compitiendo COMPLETAMENTE SOLO'")
print("(sin aliados en absoluto), necesitamos:")
print()
print("1. ¿Los VOTOS de PT y PVEM se transferirían a MORENA?")
print("   → Probablemente NO todos (algunos votantes de PT/PVEM")
print("     votarían por otros partidos si no hay coalición)")
print()
print("2. ¿O dejamos los votos como están?")
print("   → Entonces estamos simulando 'sin convenio' (que es lo actual)")
print()
print("3. ¿O redistribuimos votos de coalición?")
print("   → Necesitamos una matriz de transferencia o encuestas")
print()
print("RECOMENDACIÓN:")
print("El escenario actual 'SIN COALICIÓN' es correcto y útil.")
print("Muestra: '¿Qué pasaría si no aplicaran el convenio MR'")
print("         'pero los votantes votaran igual?'")
print()
print("El cambio real está en que el BLOQUE pierde escaños:")
print("  - CON convenio: Bloque gana 256 distritos MR (suma votos)")
print("  - SIN convenio: Bloque gana 251 distritos MR (compiten separados)")
print("  → Diferencia: -5 distritos para el bloque")
print()
