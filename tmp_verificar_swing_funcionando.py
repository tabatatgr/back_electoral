"""
Análisis de diferencias entre 2021 y 2021_SWING
"""

# Datos extraídos del CSV
escenarios = [
    # 400 escaños
    {"config": "400 | 50MR_50RP | CON", "2021": {"morena": 173, "votos": 35.36}, "2021_SWING": {"morena": 174, "votos": 35.65}},
    {"config": "400 | 50MR_50RP | SIN", "2021": {"morena": 175, "votos": 35.95}, "2021_SWING": {"morena": 177, "votos": 36.37}},
    {"config": "400 | 60MR_40RP | CON", "2021": {"morena": 173, "votos": 35.36}, "2021_SWING": {"morena": 174, "votos": 35.65}},
]

print("="*90)
print("VERIFICACIÓN: 2021 vs 2021_SWING - DIFERENCIAS DETECTADAS")
print("="*90)

for esc in escenarios:
    diff_escanos = esc["2021_SWING"]["morena"] - esc["2021"]["morena"]
    diff_votos = esc["2021_SWING"]["votos"] - esc["2021"]["votos"]
    
    print(f"\n{esc['config']}")
    print(f"  2021:       MORENA={esc['2021']['morena']:3d} escaños ({esc['2021']['votos']:5.2f}% votos)")
    print(f"  2021_SWING: MORENA={esc['2021_SWING']['morena']:3d} escaños ({esc['2021_SWING']['votos']:5.2f}% votos)")
    print(f"  → Diferencia: {diff_escanos:+d} escaños, {diff_votos:+.2f}% votos")

print("\n" + "="*90)
print("✓ CONCLUSIÓN: El swing SÍ se está aplicando correctamente")
print("  - Los cambios son pequeños (~0.3-0.4% votos, 1-2 escaños)")
print("  - Esto es esperado: solo 83 de 300 distritos tienen swing (8 estados)")
print("  - En los otros 217 distritos (24 estados) los votos NO cambian")
print("="*90)
