from main import transformar_resultado_a_formato_frontend, PARTY_COLORS

# Simular resultado de función de procesamiento
resultado_mock = {
    'tot': {
        'MORENA': 73,
        'PAN': 22,
        'PRI': 11,
        'MC': 10
    },
    'mr': {
        'MORENA': 59,
        'PAN': 16,
        'PRI': 7,
        'MC': 7
    },
    'rp': {
        'MORENA': 14,
        'PAN': 6,
        'PRI': 4,
        'MC': 3
    },
    'votos': {
        'MORENA': 25310278,
        'PAN': 10607104,
        'PRI': 7027205,
        'MC': 6528238
    }
}

print("=== PROBANDO FUNCION DE TRANSFORMACION ===")
resultado_formateado = transformar_resultado_a_formato_frontend(resultado_mock, "vigente")

print("Claves en resultado:", list(resultado_formateado.keys()))
print("Numero de resultados:", len(resultado_formateado.get('resultados', [])))
print("Tiene seat_chart:", 'seat_chart' in resultado_formateado)
print("Tiene kpis:", 'kpis' in resultado_formateado)

if 'seat_chart' in resultado_formateado:
    seat_chart = resultado_formateado['seat_chart']
    print(f"Seat chart con {len(seat_chart)} elementos")
    if seat_chart:
        print("Primer elemento seat chart:")
        print(seat_chart[0])

print("Colores disponibles:", PARTY_COLORS)
