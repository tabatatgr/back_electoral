"""
analizar_simulacion_300mr_100pm_100rp.py

Demostración de cómo localizar, leer y analizar el archivo
simulacion_300mr_100pm_100rp.csv.

Cubre los cuatro objetivos del issue:
  1. Confirmar ubicación y existencia del archivo.
  2. Mostrar estructura (encabezados y tipos de columna).
  3. Analizar el contenido: filas totales, conteos clave.
  4. Consultas útiles: escaños MR / PM / RP por partido y coalición.

Uso:
    python analizar_simulacion_300mr_100pm_100rp.py
"""

import os
import sys
import pandas as pd

CSV_FILE = "simulacion_300mr_100pm_100rp.csv"
PARTIDOS_4T = ["MORENA", "PT", "PVEM"]

# ──────────────────────────────────────────────────────────────────────────────
# 1. CONFIRMAR UBICACIÓN Y EXISTENCIA
# ──────────────────────────────────────────────────────────────────────────────

print("=" * 70)
print("1. UBICACIÓN Y EXISTENCIA DEL ARCHIVO")
print("=" * 70)

ruta_absoluta = os.path.abspath(CSV_FILE)
existe = os.path.isfile(ruta_absoluta)

print(f"  Archivo : {CSV_FILE}")
print(f"  Ruta    : {ruta_absoluta}")
print(f"  Existe  : {'✅ SÍ' if existe else '❌ NO'}")

if not existe:
    print(f"\n⚠️  El archivo no existe. Ejecútalo primero con:")
    print(f"       python generar_simulacion_300mr_100pm_100rp.py")
    sys.exit(1)

tamaño_kb = os.path.getsize(ruta_absoluta) / 1024
print(f"  Tamaño  : {tamaño_kb:.1f} KB")

# ──────────────────────────────────────────────────────────────────────────────
# 2. ESTRUCTURA (ENCABEZADOS Y COLUMNAS)
# ──────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("2. ESTRUCTURA DEL ARCHIVO")
print("=" * 70)

df = pd.read_csv(CSV_FILE)

print(f"\n  Filas    : {len(df)}")
print(f"  Columnas : {len(df.columns)}")
print("\n  Encabezados y tipos de dato:")
for col in df.columns:
    print(f"    {col:<20}  {df[col].dtype}")

print("\n  Primeras 3 filas de muestra:")
print(df.head(3).to_string(index=False))

# ──────────────────────────────────────────────────────────────────────────────
# 3. ANÁLISIS BÁSICO DEL CONTENIDO
# ──────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("3. ANÁLISIS DEL CONTENIDO")
print("=" * 70)

print(f"\n  Total de filas        : {len(df)}")
print(f"  Años disponibles      : {sorted(df['Año'].unique())}")
print(f"  Escenarios            : {df['Escenario'].unique().tolist()}")
print(f"  Partidos únicos       : {df['Partido'].nunique()}")
print(f"  Partidos              : {sorted(df['Partido'].unique())}")

print("\n  Filas por escenario:")
print(df.groupby("Escenario")["Partido"].count().rename("num_partidos").to_string())

print("\n  Rango de escaños totales por partido (todos los escenarios/años):")
resumen = df.groupby("Partido")["Total_partido"].agg(["min", "max", "mean"]).round(1)
resumen.columns = ["Mín", "Máx", "Promedio"]
print(resumen.to_string())

# ──────────────────────────────────────────────────────────────────────────────
# 4. CONSULTAS MR / PM / RP POR PARTIDO Y COALICIÓN
# ──────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("4. ESCAÑOS MR / PM / RP POR PARTIDO Y COALICIÓN")
print("=" * 70)

for anio in sorted(df["Año"].unique()):
    for escenario in df["Escenario"].unique():
        subset = df[(df["Año"] == anio) & (df["Escenario"] == escenario)].copy()
        if subset.empty:
            continue

        total_esc = subset["Total_Escaños"].iloc[0]
        print(f"\n  📅 {anio} — {escenario}  (total cámara: {total_esc} escaños)")
        print(f"  {'Partido':<10} {'MR':>6} {'PM':>6} {'RP':>6} {'Total':>7} {'%':>7}  {'4T?':>4}")
        print("  " + "-" * 52)

        for _, row in subset.iterrows():
            marca_4t = "✓" if row["Es_Coalicion_4T"] else " "
            print(
                f"  {row['Partido']:<10}"
                f" {row['MR_escaños']:>6}"
                f" {row['PM_escaños']:>6}"
                f" {row['RP_escaños']:>6}"
                f" {row['Total_partido']:>7}"
                f" {row['Pct_partido']:>6.2f}%"
                f"  {marca_4t:>4}"
            )

        # Sub-total coalición 4T
        sub_4t = subset[subset["Es_Coalicion_4T"]]
        mr_4t = sub_4t["MR_escaños"].sum()
        pm_4t = sub_4t["PM_escaños"].sum()
        rp_4t = sub_4t["RP_escaños"].sum()
        tot_4t = sub_4t["Total_partido"].sum()
        pct_4t = round(tot_4t / total_esc * 100, 2) if total_esc else 0
        print("  " + "-" * 52)
        print(
            f"  {'COALICIÓN 4T':<10}"
            f" {mr_4t:>6}"
            f" {pm_4t:>6}"
            f" {rp_4t:>6}"
            f" {tot_4t:>7}"
            f" {pct_4t:>6.2f}%"
        )

# ──────────────────────────────────────────────────────────────────────────────
# CÓMO USAR EL CSV EN TUS PROPIOS ANÁLISIS
# ──────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("EJEMPLO DE USO EN CÓDIGO PROPIO")
print("=" * 70)

print("""
  import pandas as pd

  df = pd.read_csv("simulacion_300mr_100pm_100rp.csv")

  # Escaños totales de la coalición 4T en el escenario 300 MR + 100 RP, 2024
  coalicion_rp_2024 = (
      df[(df["Año"] == 2024)
         & (df["Escenario"] == "300 MR + 100 RP")
         & (df["Es_Coalicion_4T"])]
      ["Total_partido"].sum()
  )

  # Escaños PM por partido en el escenario 300 MR + 100 PM, 2024
  pm_por_partido = (
      df[(df["Año"] == 2024) & (df["Escenario"] == "300 MR + 100 PM")]
      .set_index("Partido")["PM_escaños"]
  )

  # Comparar los dos escenarios para MORENA en 2024
  morena_2024 = (
      df[(df["Año"] == 2024) & (df["Partido"] == "MORENA")]
      [["Escenario", "MR_escaños", "PM_escaños", "RP_escaños", "Total_partido"]]
  )
""")

print("=" * 70)
print("✅ Análisis completado")
print("=" * 70)
