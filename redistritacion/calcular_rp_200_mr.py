"""
Calcula cuántos RP le tocarían a un partido que gana 
TODOS los distritos MR en el escenario 200-200.
"""

print("="*80)
print("ESCENARIO 200-200: ¿Cuántos RP si gana TODOS los 200 MR?")
print("="*80)

mr_total = 200
rp_total = 200
total_seats = 400
mr_ganados = 200  # TODOS

print(f"\nSi un partido gana TODOS los {mr_ganados} distritos MR:")
print(f"\nLos RP se distribuyen proporcionalmente a la votación nacional.")
print(f"Método Hare: RP = votos% × {rp_total}")
print(f"\n{'-'*80}")
print(f"{'% Votos':<12} {'MR':<8} {'RP':<8} {'Total':<10} {'% Escaños':<12} {'Mayoría'}")
print(f"{'-'*80}")

for pct_votos in [40, 45, 50, 55, 60, 65, 70, 75, 80]:
    rp_ganados = int(rp_total * pct_votos / 100)
    total = mr_ganados + rp_ganados
    pct_escanos = total / total_seats * 100
    
    if total >= 267:
        mayoria = "✅ Calificada"
    elif total >= 201:
        mayoria = "✅ Simple"
    else:
        mayoria = "❌"
    
    print(f"{pct_votos:>3}%         {mr_ganados:<8} {rp_ganados:<8} {total:<10} {pct_escanos:>6.1f}%       {mayoria}")

print(f"{'-'*80}")
print(f"\n💡 CONCLUSIONES:")
print(f"""
1. Si un partido gana TODOS los 200 MR (hazaña histórica imposible):
   - Con 50% votos: 200 MR + 100 RP = 300 escaños (75%) ✅ Mayoría calificada
   - Con 60% votos: 200 MR + 120 RP = 320 escaños (80%) ✅ Supermayoría
   - Con 70% votos: 200 MR + 140 RP = 340 escaños (85%) ✅ Hegemonía

2. En el escenario SIN TOPES 200-200:
   - Un partido dominante (60%+ votos que gane todos los MR) 
     podría obtener 75-85% de escaños
   - Esto permite sobrerrepresentación masiva
   - ⚠️ Riesgo de concentración de poder

3. Comparación con TOPES (8%):
   - CON TOPES: Máximo ~68% de escaños (272/400) con 60% votos
   - SIN TOPES: Podría llegar a 80% de escaños (320/400) con 60% votos
   - Los topes limitan la sobrerrepresentación en ~12 puntos porcentuales

4. Realidad práctica:
   - Ganar TODOS los distritos MR es históricamente imposible
   - Máximo histórico: PRI ~88% de distritos en los 80s (no democrático)
   - Era democrática: MORENA ganó 78.7% en 2024 (en coalición)
""")
