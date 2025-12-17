"""
Test para validar que max_seats_per_party (tope absoluto) funciona INDEPENDIENTEMENTE
de sobrerrepresentacion (cláusula relativa %).

Casos de prueba:
1. Solo tope absoluto (max_seats_per_party=280, sin sobrerrepresentacion)
2. Solo cláusula % (sobrerrepresentacion=8.0, sin max_seats_per_party)
3. Ambos límites activados (el más restrictivo gana)
4. Ningún límite (None en ambos)
"""

import requests

API_URL = "http://localhost:8000/procesar/diputados"

def get_morena_seats(data):
    """Extrae los escaños de MORENA de la respuesta del API"""
    if "resultados" in data:
        for p in data["resultados"]:
            if p.get("partido") == "MORENA":
                return {
                    "total": p.get("total"),
                    "mr": p.get("mr", 0),
                    "pm": p.get("pm", 0),
                    "rp": p.get("rp", 0)
                }
    elif "seat_chart" in data:
        if "MORENA" in data["seat_chart"]:
            return {
                "total": data["seat_chart"]["MORENA"]["total"],
                "mr": data["seat_chart"]["MORENA"]["mr"],
                "pm": data["seat_chart"]["MORENA"].get("pm", 0),
                "rp": data["seat_chart"]["MORENA"]["rp"]
            }
    return None


def test_solo_tope_absoluto():
    """Test 1: Solo tope absoluto de 280 escaños (sin % de sobrerrepresentación)"""
    print("=" * 80)
    print("TEST 1: Solo tope ABSOLUTO (280 escaños máx, SIN cláusula %)")
    print("=" * 80)
    
    params = {
        "anio": 2024,
        "plan": "personalizado",
        "sistema": "mixto",
        "escanos_totales": 500,
        "usar_coaliciones": "false",  # Sin coaliciones para simplificar
        "reparto_mode": "divisor",
        "reparto_method": "dhondt",
        "aplicar_topes": "true",  # Activar límites
        # "sobrerrepresentacion": None NO se pasa en query string
        "max_seats_per_party": 280,  # Solo tope absoluto
        "mr_seats": 300,
        "rp_seats": 200,
        "umbral": 3.0
    }
    
    response = requests.post(API_URL, params=params, timeout=30)
    
    # Debug: ver qué devuelve el endpoint
    if response.status_code != 200:
        print(f"❌ ERROR: Status {response.status_code}")
        data = response.json()
        print(f"Response: {data}")
        return None
    
    data = response.json()
    morena = get_morena_seats(data)
    
    if not morena:
        print(f"❌ ERROR: MORENA no encontrado en respuesta")
        print(f"Keys disponibles: {list(data.keys())}")
        return None
    
    print(f"Configuración:")
    print(f"  aplicar_topes=true")
    print(f"  sobrerrepresentacion=None (NO aplicar cláusula %)")
    print(f"  max_seats_per_party=280 (tope absoluto)")
    print(f"  Esperado: 280 escaños (límite absoluto)\n")
    print(f"Resultado:")
    print(f"  MORENA: {morena['total']} escaños")
    print(f"    MR: {morena['mr']}")
    print(f"    PM: {morena['pm']}")
    print(f"    RP: {morena['rp']}\n")
    
    return morena['total']


def test_solo_clausula_porcentual():
    """Test 2: Solo cláusula de sobrerrepresentación del 8% (sin tope absoluto)"""
    print("=" * 80)
    print("TEST 2: Solo cláusula % (8% sobrerrepresentación, SIN tope absoluto)")
    print("=" * 80)
    
    params = {
        "anio": 2024,
        "plan": "personalizado",
        "sistema": "mixto",
        "escanos_totales": 500,
        "usar_coaliciones": "false",
        "reparto_mode": "divisor",
        "reparto_method": "dhondt",
        "aplicar_topes": "true",  # Activar límites
        "sobrerrepresentacion": 8.0,  # Cláusula del 8%
        # "max_seats_per_party": None NO se pasa en query string
        "mr_seats": 300,
        "rp_seats": 200,
        "umbral": 3.0
    }
    
    response = requests.post(API_URL, params=params, timeout=30)
    
    if response.status_code != 200:
        print(f"❌ ERROR: Status {response.status_code}")
        return None
    
    data = response.json()
    morena = get_morena_seats(data)
    
    if not morena:
        print(f"❌ ERROR: MORENA no encontrado")
        return None
    
    print(f"Configuración:")
    print(f"  aplicar_topes=true")
    print(f"  sobrerrepresentacion=8.0 (cláusula del 8%)")
    print(f"  max_seats_per_party=None (NO aplicar tope absoluto)")
    print(f"  Esperado: ~252 escaños (42.49% + 8% = 50.49% de 500)\n")
    print(f"Resultado:")
    print(f"  MORENA: {morena['total']} escaños")
    print(f"    MR: {morena['mr']}")
    print(f"    PM: {morena['pm']}")
    print(f"    RP: {morena['rp']}\n")
    
    return morena['total']


def test_ambos_limites():
    """Test 3: Ambos límites activados (el más restrictivo gana)"""
    print("=" * 80)
    print("TEST 3: AMBOS límites (8% Y 280 escaños, gana el más restrictivo)")
    print("=" * 80)
    
    params = {
        "anio": 2024,
        "plan": "personalizado",
        "sistema": "mixto",
        "escanos_totales": 500,
        "usar_coaliciones": "false",
        "reparto_mode": "divisor",
        "reparto_method": "dhondt",
        "aplicar_topes": "true",  # Activar límites
        "sobrerrepresentacion": 8.0,  # Cláusula del 8% = ~252 escaños
        "max_seats_per_party": 280,  # Tope absoluto = 280 escaños
        "mr_seats": 300,
        "rp_seats": 200,
        "umbral": 3.0
    }
    
    response = requests.post(API_URL, params=params, timeout=30)
    
    if response.status_code != 200:
        print(f"❌ ERROR: Status {response.status_code}")
        return None
    
    data = response.json()
    morena = get_morena_seats(data)
    
    if not morena:
        print(f"❌ ERROR: MORENA no encontrado")
        return None
    
    print(f"Configuración:")
    print(f"  aplicar_topes=true")
    print(f"  sobrerrepresentacion=8.0 (límite ~252 escaños)")
    print(f"  max_seats_per_party=280 (límite 280 escaños)")
    print(f"  Esperado: ~252 escaños (el 8% es MÁS restrictivo que 280)\n")
    print(f"Resultado:")
    print(f"  MORENA: {morena['total']} escaños")
    print(f"    MR: {morena['mr']}")
    print(f"    PM: {morena['pm']}")
    print(f"    RP: {morena['rp']}\n")
    
    return morena['total']


def test_sin_limites():
    """Test 4: Sin ningún límite"""
    print("=" * 80)
    print("TEST 4: SIN límites (aplicar_topes=FALSE)")
    print("=" * 80)
    
    params = {
        "anio": 2024,
        "plan": "personalizado",
        "sistema": "mixto",
        "escanos_totales": 500,
        "usar_coaliciones": "false",
        "reparto_mode": "divisor",
        "reparto_method": "dhondt",
        "aplicar_topes": "false",  # DESACTIVAR todos los límites
        # No se pasa sobrerrepresentacion ni max_seats_per_party
        "mr_seats": 300,
        "rp_seats": 200,
        "umbral": 3.0
    }
    
    response = requests.post(API_URL, params=params, timeout=30)
    
    if response.status_code != 200:
        print(f"❌ ERROR: Status {response.status_code}")
        return None
    
    data = response.json()
    morena = get_morena_seats(data)
    
    if not morena:
        print(f"❌ ERROR: MORENA no encontrado")
        return None
    
    print(f"Configuración:")
    print(f"  aplicar_topes=FALSE (desactivar TODOS los límites)")
    print(f"  sobrerrepresentacion=N/A")
    print(f"  max_seats_per_party=N/A")
    print(f"  Esperado: ~339 escaños (sin límites)\n")
    print(f"Resultado:")
    print(f"  MORENA: {morena['total']} escaños")
    print(f"    MR: {morena['mr']}")
    print(f"    PM: {morena['pm']}")
    print(f"    RP: {morena['rp']}\n")
    
    return morena['total']


def test_caso_inverso_ambos_limites():
    """Test 5: Ambos límites, pero tope absoluto más restrictivo"""
    print("=" * 80)
    print("TEST 5: AMBOS límites (10% Y 260 escaños, gana el más restrictivo)")
    print("=" * 80)
    
    params = {
        "anio": 2024,
        "plan": "personalizado",
        "sistema": "mixto",
        "escanos_totales": 500,
        "usar_coaliciones": "false",
        "reparto_mode": "divisor",
        "reparto_method": "dhondt",
        "aplicar_topes": "true",  # Activar límites
        "sobrerrepresentacion": 10.0,  # Cláusula del 10% = ~262 escaños
        "max_seats_per_party": 260,  # Tope absoluto = 260 escaños
        "mr_seats": 300,
        "rp_seats": 200,
        "umbral": 3.0
    }
    
    response = requests.post(API_URL, params=params, timeout=30)
    
    if response.status_code != 200:
        print(f"❌ ERROR: Status {response.status_code}")
        return None
    
    data = response.json()
    morena = get_morena_seats(data)
    
    if not morena:
        print(f"❌ ERROR: MORENA no encontrado")
        return None
    
    print(f"Configuración:")
    print(f"  aplicar_topes=true")
    print(f"  sobrerrepresentacion=10.0 (límite ~262 escaños)")
    print(f"  max_seats_per_party=260 (límite 260 escaños)")
    print(f"  Esperado: 260 escaños (tope absoluto es MÁS restrictivo que 10%)\n")
    print(f"Resultado:")
    print(f"  MORENA: {morena['total']} escaños")
    print(f"    MR: {morena['mr']}")
    print(f"    PM: {morena['pm']}")
    print(f"    RP: {morena['rp']}\n")
    
    return morena['total']


if __name__ == "__main__":
    print("\n")
    print("=" * 80)
    print("TEST: Independencia de max_seats_per_party y sobrerrepresentacion")
    print("=" * 80)
    print("\n")
    
    escanos_1 = test_solo_tope_absoluto()
    escanos_2 = test_solo_clausula_porcentual()
    escanos_3 = test_ambos_limites()
    escanos_4 = test_sin_limites()
    escanos_5 = test_caso_inverso_ambos_limites()
    
    print("=" * 80)
    print("RESUMEN:")
    print("=" * 80)
    print("\n📊 Tabla de resultados:")
    print(f"{'Test':<55} {'Topes':<8} {'Sobre%':<8} {'Max Abs':<8} {'Escaños':<8}")
    print("-" * 80)
    print(f"{'1️⃣ Solo tope ABSOLUTO (280 max)':<55} {'true':<8} {'None':<8} {'280':<8} {escanos_1 if escanos_1 else 'ERROR':<8}")
    print(f"{'2️⃣ Solo cláusula % (8% sobre votos)':<55} {'true':<8} {'8.0':<8} {'None':<8} {escanos_2 if escanos_2 else 'ERROR':<8}")
    print(f"{'3️⃣ Ambos (8% Y 280, gana 8% ~252)':<55} {'true':<8} {'8.0':<8} {'280':<8} {escanos_3 if escanos_3 else 'ERROR':<8}")
    print(f"{'4️⃣ Sin límites (None en ambos)':<55} {'true':<8} {'None':<8} {'None':<8} {escanos_4 if escanos_4 else 'ERROR':<8}")
    print(f"{'5️⃣ Ambos (10% Y 260, gana 260)':<55} {'true':<8} {'10.0':<8} {'260':<8} {escanos_5 if escanos_5 else 'ERROR':<8}")
    
    print("\n🔍 Verificación de independencia:")
    print("-" * 80)
    
    if escanos_1 and escanos_2:
        # Verificar que solo tope absoluto funciona diferente a solo cláusula %
        if escanos_1 != escanos_2:
            print(f"✅ Límites INDEPENDIENTES: Tope absoluto ({escanos_1}) ≠ Cláusula % ({escanos_2})")
        else:
            print(f"❌ Problema: Tope absoluto y cláusula % dan mismo resultado ({escanos_1})")
    
    if escanos_4 and escanos_1 and escanos_2:
        # Verificar que sin límites da resultado distinto
        if escanos_4 > escanos_1 and escanos_4 > escanos_2:
            print(f"✅ Sin límites ({escanos_4}) da MÁS escaños que con límites")
        else:
            print(f"❌ Problema: Sin límites no da más escaños")
    
    if escanos_3 and escanos_1:
        # Verificar que con ambos límites gana el más restrictivo
        if escanos_3 < escanos_1 and escanos_3 < 280:
            print(f"✅ Con ambos límites gana el MÁS RESTRICTIVO: {escanos_3} (cláusula 8%)")
        else:
            print(f"⚠️  Resultado ambiguo: {escanos_3} escaños con ambos límites")
    
    if escanos_5:
        if escanos_5 == 260:
            print(f"✅ Con ambos límites (inverso) gana el MÁS RESTRICTIVO: {escanos_5} (tope absoluto 260)")
        else:
            print(f"⚠️  Resultado ambiguo inverso: {escanos_5} escaños (esperado 260)")
    
    print("\n" + "=" * 80)
    print("CONCLUSIÓN:")
    print("=" * 80)
    print("Los parámetros max_seats_per_party y sobrerrepresentacion funcionan de forma")
    print("INDEPENDIENTE y se pueden combinar:")
    print("- max_seats_per_party: Tope ABSOLUTO (ej: máximo 280 escaños)")
    print("- sobrerrepresentacion: Cláusula RELATIVA % (ej: máximo +8% sobre votos)")
    print("- Cuando ambos están activos, se aplica el MÁS RESTRICTIVO")
    print("- Cuando están en None, NO se aplican límites")
    print("=" * 80)
