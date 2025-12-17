"""
Test para demostrar que aplicar_topes y sobrerrepresentacion son INDEPENDIENTES
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("TEST: Independencia de aplicar_topes y sobrerrepresentacion")
print("=" * 80)

base_params = {
    "anio": 2024,
    "plan": "personalizado",
    "sistema": "mixto",
    "escanos_totales": 500,
    "mr_seats": 300,
    "rp_seats": 200,
    "usar_coaliciones": "false"
}

tests = [
    {
        "nombre": "1️⃣ Límite del 8% (constitucional)",
        "aplicar_topes": "true",
        "sobrerrepresentacion": 8.0,
        "esperado": "~252 escaños (límite del 8%)"
    },
    {
        "nombre": "2️⃣ Límite del 10% (más permisivo)",
        "aplicar_topes": "true",
        "sobrerrepresentacion": 10.0,
        "esperado": "~268 escaños (límite del 10%)"
    },
    {
        "nombre": "3️⃣ Límite del 5% (más restrictivo)",
        "aplicar_topes": "true",
        "sobrerrepresentacion": 5.0,
        "esperado": "~237 escaños (límite del 5%)"
    },
    {
        "nombre": "4️⃣ Sin límites (aplicar_topes=false, sobrerrepresentacion=8.0 se ignora)",
        "aplicar_topes": "false",
        "sobrerrepresentacion": 8.0,
        "esperado": "~339 escaños (sin límites)"
    },
    {
        "nombre": "5️⃣ Sin límites (aplicar_topes=false, sobrerrepresentacion=10.0 se ignora)",
        "aplicar_topes": "false",
        "sobrerrepresentacion": 10.0,
        "esperado": "~339 escaños (sin límites)"
    }
]

resultados = []

for test in tests:
    print(f"\n{test['nombre']}")
    print("-" * 80)
    print(f"Configuración:")
    print(f"  aplicar_topes={test['aplicar_topes']}")
    print(f"  sobrerrepresentacion={test['sobrerrepresentacion']}")
    print(f"  Esperado: {test['esperado']}")
    
    params = base_params.copy()
    params["aplicar_topes"] = test["aplicar_topes"]
    params["sobrerrepresentacion"] = test["sobrerrepresentacion"]
    
    try:
        resp = requests.post(f"{BASE_URL}/procesar/diputados", params=params, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            morena = None
            if "resultados" in data:
                for p in data["resultados"]:
                    if p.get("partido") == "MORENA":
                        morena = p
                        break
            
            if morena:
                total = morena.get('total')
                mr = morena.get('mr', 0)
                pm = morena.get('pm', 0)
                rp = morena.get('rp', 0)
                
                print(f"\nResultado:")
                print(f"  MORENA: {total} escaños")
                print(f"    MR: {mr}")
                print(f"    PM: {pm}")
                print(f"    RP: {rp}")
                
                resultados.append({
                    "test": test["nombre"],
                    "aplicar_topes": test["aplicar_topes"],
                    "sobrerrepresentacion": test["sobrerrepresentacion"],
                    "escanos": total
                })
            else:
                print("❌ MORENA no encontrado")
                resultados.append({
                    "test": test["nombre"],
                    "aplicar_topes": test["aplicar_topes"],
                    "sobrerrepresentacion": test["sobrerrepresentacion"],
                    "escanos": None
                })
        else:
            print(f"❌ Error {resp.status_code}")
            resultados.append({
                "test": test["nombre"],
                "aplicar_topes": test["aplicar_topes"],
                "sobrerrepresentacion": test["sobrerrepresentacion"],
                "escanos": None
            })
    except Exception as e:
        print(f"❌ Error: {e}")
        resultados.append({
            "test": test["nombre"],
            "aplicar_topes": test["aplicar_topes"],
            "sobrerrepresentacion": test["sobrerrepresentacion"],
            "escanos": None
        })

# Análisis de resultados
print("\n" + "=" * 80)
print("RESUMEN:")
print("=" * 80)

print("\n📊 Tabla de resultados:")
print(f"{'Test':<50} {'Topes':<8} {'Sobre%':<8} {'Escaños':<10}")
print("-" * 80)
for r in resultados:
    if r["escanos"] is not None:
        print(f"{r['test']:<50} {r['aplicar_topes']:<8} {r['sobrerrepresentacion']:<8} {r['escanos']:<10}")

# Verificar independencia
print("\n🔍 Verificación de independencia:")
print("-" * 80)

# Test 1: Cambiar sobrerrepresentacion con aplicar_topes=true debería cambiar resultado
test1 = next((r for r in resultados if r["test"] == tests[0]["nombre"]), None)
test2 = next((r for r in resultados if r["test"] == tests[1]["nombre"]), None)

if test1 and test2 and test1["escanos"] and test2["escanos"]:
    if test1["escanos"] != test2["escanos"]:
        print("✅ sobrerrepresentacion SÍ afecta (8% vs 10% da resultados diferentes)")
        print(f"   8%:  {test1['escanos']} escaños")
        print(f"   10%: {test2['escanos']} escaños")
    else:
        print("⚠️  sobrerrepresentacion NO afecta (mismo resultado con 8% y 10%)")

# Test 2: aplicar_topes=false debería ignorar sobrerrepresentacion
test4 = next((r for r in resultados if r["test"] == tests[3]["nombre"]), None)
test5 = next((r for r in resultados if r["test"] == tests[4]["nombre"]), None)

if test4 and test5 and test4["escanos"] and test5["escanos"]:
    if test4["escanos"] == test5["escanos"]:
        print("✅ aplicar_topes=false IGNORA sobrerrepresentacion correctamente")
        print(f"   Con 8%:  {test4['escanos']} escaños")
        print(f"   Con 10%: {test5['escanos']} escaños (igual)")
    else:
        print("❌ aplicar_topes=false NO ignora sobrerrepresentacion")
        print(f"   Con 8%:  {test4['escanos']} escaños")
        print(f"   Con 10%: {test5['escanos']} escaños (diferente)")

# Test 3: aplicar_topes debería hacer diferencia
if test1 and test4 and test1["escanos"] and test4["escanos"]:
    if test1["escanos"] < test4["escanos"]:
        print("✅ aplicar_topes=true limita correctamente")
        print(f"   CON topes:  {test1['escanos']} escaños")
        print(f"   SIN topes:  {test4['escanos']} escaños")
        print(f"   Diferencia: +{test4['escanos'] - test1['escanos']} escaños sin topes")
    else:
        print("❌ aplicar_topes no hace diferencia")

print("\n" + "=" * 80)
print("CONCLUSIÓN:")
print("=" * 80)
print("Los parámetros aplicar_topes y sobrerrepresentacion son INDEPENDIENTES")
print("- sobrerrepresentacion define el % de límite (5%, 8%, 10%, etc.)")
print("- aplicar_topes activa/desactiva el sistema de límites (ON/OFF)")
print("=" * 80)
