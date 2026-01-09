"""
Generar tabla comparativa 2021 vs 2024 usando MOTOR DIRECTO (no API)
Con 4 escenarios y verificación de umbral 3% para PRD
"""
import pandas as pd
from datetime import datetime
import sys
import os

# Importar motor directamente
sys.path.insert(0, os.path.abspath('.'))
from engine.procesar_diputados_v2 import procesar_diputados_v2

print("=" * 80)
print("📊 GENERANDO TABLA COMPARATIVA 2021 vs 2024 (MOTOR DIRECTO)")
print("=" * 80)

# Definir escenarios
escenarios = [
    {
        "nombre": "MR 200 - RP 200",
        "mr_seats": 200,
        "rp_seats": 200,
        "pm_seats": 0,
        "sistema": "mixto"
    },
    {
        "nombre": "MR 300 - RP 100",
        "mr_seats": 300,
        "rp_seats": 100,
        "pm_seats": 0,
        "sistema": "mixto"
    },
    {
        "nombre": "MR 200 - PM 200",
        "mr_seats": 200,
        "rp_seats": 0,
        "pm_seats": 200,
        "sistema": "mixto"
    },
    {
        "nombre": "MR 300 - PM 100",
        "mr_seats": 300,
        "rp_seats": 0,
        "pm_seats": 100,
        "sistema": "mixto"
    }
]

# Supuestos fijos
supuestos = {
    "umbral": 0.03,  # 3%
    "sobrerrepresentacion_max": 0.08,  # +8%
    "max_seats_per_party": 300,
    "aplicar_topes": True,
    "usar_coaliciones": True
}

print(f"\n📋 Supuestos aplicados:")
print(f"  • Umbral de representación: 3% (solo partidos ≥3% acceden a RP)")
print(f"  • Tope de sobrerrepresentación: +8% sobre voto nacional")
print(f"  • Límite máximo: 300 curules por partido")
print(f"  • Coaliciones: Activadas")

resultados_finales = []

for escenario in escenarios:
    print(f"\n{'=' * 80}")
    print(f"🔄 Procesando: {escenario['nombre']}")
    print(f"{'=' * 80}")
    
    for anio in [2021, 2024]:
        print(f"\n  📅 Año {anio}...")
        
        try:
            # Path del parquet según el año
            path_parquet = f"data/computos_diputados_{anio}.parquet"
            path_siglado = f"data/siglado-diputados-{anio}.csv"
            
            # Llamar motor directamente
            resultado = procesar_diputados_v2(
                path_parquet=path_parquet,
                path_siglado=path_siglado,
                anio=anio,
                max_seats=400,
                mr_seats=escenario["mr_seats"],
                pm_seats=escenario["pm_seats"],
                rp_seats=escenario["rp_seats"],
                umbral=supuestos["umbral"],
                sobrerrepresentacion=supuestos["sobrerrepresentacion_max"],
                max_seats_per_party=supuestos["max_seats_per_party"],
                aplicar_topes=supuestos["aplicar_topes"],
                usar_coaliciones=supuestos["usar_coaliciones"],
                quota_method="hare"
            )
            
            # Verificar estructura del resultado
            if not isinstance(resultado, dict):
                print(f"  WARNING: Resultado no es dict: {type(resultado)}")
                continue
            
            # El motor devuelve un dict con keys: mr, pm, rp, tot, ok, votos, votos_ok, meta
            # mr/pm/rp/tot son dicts {partido: escanos}
            if "mr" not in resultado or "tot" not in resultado:
                print(f"  WARNING: Keys disponibles: {list(resultado.keys())}")
                continue
            
            # Obtener todos los partidos únicos
            partidos_todos = set()
            for key in ["mr", "pm", "rp", "tot"]:
                if key in resultado and isinstance(resultado[key], dict):
                    partidos_todos.update(resultado[key].keys())
            
            # Extraer votos si están disponibles
            votos_dict = resultado.get("votos", {})
            votos_ok_dict = resultado.get("votos_ok", {})
            
            # Total votos para calcular porcentajes
            total_votos = sum(votos_ok_dict.values()) if votos_ok_dict else sum(votos_dict.values()) if votos_dict else 1
            
            # Crear fila por cada partido
            for partido in sorted(partidos_todos):
                votos = votos_ok_dict.get(partido, votos_dict.get(partido, 0))
                votos_pct = (votos / total_votos * 100) if total_votos > 0 else 0
                
                mr_escanos = resultado.get("mr", {}).get(partido, 0)
                pm_escanos = resultado.get("pm", {}).get(partido, 0)
                rp_escanos = resultado.get("rp", {}).get(partido, 0)
                total_escanos = resultado.get("tot", {}).get(partido, 0)
                
                # Verificar PRD específicamente
                if partido == "PRD" and anio == 2024:
                    if rp_escanos > 0 and votos_pct < 3.0:
                        print(f"  ⚠️  WARNING: PRD con {votos_pct:.2f}% tiene {rp_escanos} RP (debería ser 0)")
                
                resultados_finales.append({
                    "Año": anio,
                    "Escenario": escenario["nombre"],
                    "Partido": partido,
                    "Votos_%": round(votos_pct, 2),
                    "MR": mr_escanos,
                    "PM": pm_escanos,
                    "RP": rp_escanos,
                    "Total": total_escanos
                })
            
            print(f"  ✅ Completado")
            
        except Exception as e:
            print(f"  ❌ Error en {anio}: {e}")
            import traceback
            traceback.print_exc()

# Crear DataFrame
df = pd.DataFrame(resultados_finales)

# Calcular diferencias MORENA 2024 vs 2021
print(f"\n{'=' * 80}")
print(f"📊 Calculando diferencias MORENA (2024 - 2021)...")
print(f"{'=' * 80}")

diferencias_morena = []

for escenario in escenarios:
    escenario_nombre = escenario["nombre"]
    
    # Datos 2021
    morena_2021 = df[(df["Escenario"] == escenario_nombre) & 
                     (df["Año"] == 2021) & 
                     (df["Partido"] == "MORENA")]
    
    # Datos 2024
    morena_2024 = df[(df["Escenario"] == escenario_nombre) & 
                     (df["Año"] == 2024) & 
                     (df["Partido"] == "MORENA")]
    
    if not morena_2021.empty and not morena_2024.empty:
        diff_mr = morena_2024["MR"].values[0] - morena_2021["MR"].values[0]
        diff_pm = morena_2024["PM"].values[0] - morena_2021["PM"].values[0]
        diff_rp = morena_2024["RP"].values[0] - morena_2021["RP"].values[0]
        diff_total = morena_2024["Total"].values[0] - morena_2021["Total"].values[0]
        
        diferencias_morena.append({
            "Escenario": escenario_nombre,
            "Diff_MORENA_MR": diff_mr,
            "Diff_MORENA_PM": diff_pm,
            "Diff_MORENA_RP": diff_rp,
            "Diff_MORENA_Total": diff_total
        })
        
        print(f"\n{escenario_nombre}:")
        print(f"  MR: {diff_mr:+d}")
        print(f"  PM: {diff_pm:+d}")
        print(f"  RP: {diff_rp:+d}")
        print(f"  Total: {diff_total:+d}")

# Agregar columnas de diferencias al DataFrame principal
df_diff = pd.DataFrame(diferencias_morena)
df = df.merge(df_diff, on="Escenario", how="left")

# Verificación PRD 2024
print(f"\n{'=' * 80}")
print(f"🔍 VERIFICACIÓN PRD 2024:")
print(f"{'=' * 80}")

prd_2024 = df[(df["Año"] == 2024) & (df["Partido"] == "PRD")]
for _, row in prd_2024.iterrows():
    print(f"\n{row['Escenario']}:")
    print(f"  Votos: {row['Votos_%']:.2f}%")
    print(f"  MR: {row['MR']}")
    print(f"  PM: {row['PM']}")
    print(f"  RP: {row['RP']}")
    
    if row['RP'] > 0 and row['Votos_%'] < 3.0:
        print(f"  ❌ ERROR: PRD tiene {row['RP']} RP pero solo {row['Votos_%']:.2f}%")
    elif row['RP'] == 0:
        print(f"  ✅ CORRECTO: PRD sin RP (no alcanzó 3% umbral)")

# Guardar CSV
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"outputs/comparativa_escenarios_motor_directo_{timestamp}.csv"
df.to_csv(filename, index=False, encoding='utf-8-sig')

print(f"\n{'=' * 80}")
print(f"✅ TABLA GENERADA EXITOSAMENTE")
print(f"{'=' * 80}")
print(f"📄 Archivo: {filename}")
print(f"📊 Total de filas: {len(df)}")
print(f"📅 Años: {sorted(df['Año'].unique())}")
print(f"🎯 Escenarios: {len(escenarios)}")
print(f"🏛️  Partidos por escenario: {df[df['Año']==2024].groupby('Escenario')['Partido'].count().iloc[0]}")

# Mostrar primeras filas
print(f"\n{'=' * 80}")
print(f"📋 VISTA PREVIA (primeras 20 filas):")
print(f"{'=' * 80}")
print(df.head(20).to_string())

print(f"\n{'=' * 80}")
print(f"🎯 COLUMNAS INCLUIDAS:")
print(f"{'=' * 80}")
for col in df.columns:
    print(f"  • {col}")
