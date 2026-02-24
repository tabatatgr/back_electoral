"""
Genera el archivo simulacion_300mr_100pm_100rp.csv

Este script ejecuta dos escenarios complementarios para los años 2021 y 2024:
  - Escenario A: 300 MR + 100 PM  (primera minoría, sin RP)
  - Escenario B: 300 MR + 100 RP  (representación proporcional, sin PM)

El CSV resultante permite comparar cómo cambia la distribución de escaños
entre ambas variantes y analizar el desempeño de cada partido/coalición
en cada tipo de asignación.

Columnas del CSV:
  Año, Escenario, MR_config, PM_config, RP_config, Total_Escaños,
  Partido, MR_escaños, PM_escaños, RP_escaños, Total_partido,
  Pct_partido, Es_Coalicion_4T
"""

import sys
import os
sys.path.append('.')

import pandas as pd
from datetime import datetime
from engine.procesar_diputados_v2 import procesar_diputados_v2

OUTPUT_FILE = "simulacion_300mr_100pm_100rp.csv"
PARTIDOS_4T = ["MORENA", "PT", "PVEM"]


def _ejecutar_escenario(anio: int, mr_seats: int, pm_seats: int, rp_seats: int,
                        nombre: str) -> list:
    """Ejecuta un escenario y devuelve lista de filas para el CSV.

    PM y RP son mutuamente excluyentes en el motor electoral: sólo uno de los
    dos puede ser mayor que cero en cada llamada.
    """
    if pm_seats > 0 and rp_seats > 0:
        raise ValueError(
            f"PM ({pm_seats}) y RP ({rp_seats}) son mutuamente excluyentes. "
            "Especifica sólo uno de los dos en cada escenario."
        )
    total = mr_seats + pm_seats + rp_seats  # uno de pm/rp siempre es 0
    resultado = procesar_diputados_v2(
        path_parquet=f"data/computos_diputados_{anio}.parquet",
        anio=anio,
        path_siglado=f"data/siglado-diputados-{anio}.csv",
        max_seats=total,
        mr_seats=mr_seats,
        rp_seats=rp_seats,
        pm_seats=pm_seats if pm_seats > 0 else None,
        aplicar_topes=True,
        max_seats_per_party=int(total * 0.60),
        usar_coaliciones=True,
        sobrerrepresentacion=8.0,
        umbral=0.03,
        print_debug=False,
    )

    mr_d = resultado.get("mr", {})
    pm_d = resultado.get("pm", {})
    rp_d = resultado.get("rp", {})
    tot_d = resultado.get("tot", {})
    total_real = sum(tot_d.values())

    filas = []
    for partido, escanos_tot in sorted(tot_d.items(), key=lambda x: x[1], reverse=True):
        if escanos_tot == 0:
            continue
        pct = round(escanos_tot / total_real * 100, 2) if total_real else 0
        filas.append({
            "Año": anio,
            "Escenario": nombre,
            "MR_config": mr_seats,
            "PM_config": pm_seats,
            "RP_config": rp_seats,
            "Total_Escaños": total_real,
            "Partido": partido,
            "MR_escaños": mr_d.get(partido, 0),
            "PM_escaños": pm_d.get(partido, 0),
            "RP_escaños": rp_d.get(partido, 0),
            "Total_partido": escanos_tot,
            "Pct_partido": pct,
            "Es_Coalicion_4T": partido in PARTIDOS_4T,
        })
    return filas


def main():
    print("=" * 70)
    print("GENERANDO: simulacion_300mr_100pm_100rp.csv")
    print("=" * 70)

    escenarios = [
        # (mr, pm, rp, nombre)
        (300, 100,   0, "300 MR + 100 PM"),
        (300,   0, 100, "300 MR + 100 RP"),
    ]

    filas_totales = []
    for anio in [2021, 2024]:
        for mr, pm, rp, nombre in escenarios:
            print(f"  Procesando {anio} – {nombre}...", end=" ", flush=True)
            filas = _ejecutar_escenario(anio, mr, pm, rp, nombre)
            filas_totales.extend(filas)
            print(f"OK ({len(filas)} partidos)")

    df = pd.DataFrame(filas_totales)
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print(f"\n✅ Archivo generado: {OUTPUT_FILE}")
    print(f"   Filas: {len(df)}")
    print(f"   Columnas: {list(df.columns)}")
    print(f"   Años: {sorted(df['Año'].unique())}")
    print(f"   Escenarios: {df['Escenario'].unique().tolist()}")
    print(f"   Partidos únicos: {df['Partido'].nunique()}")


if __name__ == "__main__":
    main()
