import pandas as pd
from engine.procesar_diputados import procesar_diputados_parquet
from engine.procesar_senadores_fixed import procesar_senadores_parquet

# Configuración de escenarios y parámetros para TODOS los años y cámaras
escenarios = [
    # DIPUTADOS 2018
    {"camara": "diputados", "anio": 2018, "max_seats": 500, "mr_seats": 300, "rp_seats": 200, "umbral": 0.03, "max_seats_per_party": 300, "quota_method": "hare", "divisor_method": "dhondt", "desc": "vigente"},
    {"camara": "diputados", "anio": 2018, "max_seats": 300, "mr_seats": 0,   "rp_seats": 300, "umbral": 0.03, "max_seats_per_party": None, "quota_method": "hare", "divisor_method": None, "desc": "plan_a"},
    {"camara": "diputados", "anio": 2018, "max_seats": 300, "mr_seats": 300, "rp_seats": 0,   "umbral": 0.0,  "max_seats_per_party": None, "quota_method": "hare", "divisor_method": None, "desc": "plan_c"},
    # DIPUTADOS 2021
    {"camara": "diputados", "anio": 2021, "max_seats": 500, "mr_seats": 300, "rp_seats": 200, "umbral": 0.03, "max_seats_per_party": 300, "quota_method": "hare", "divisor_method": "dhondt", "desc": "vigente"},
    {"camara": "diputados", "anio": 2021, "max_seats": 300, "mr_seats": 0,   "rp_seats": 300, "umbral": 0.03, "max_seats_per_party": None, "quota_method": "hare", "divisor_method": None, "desc": "plan_a"},
    {"camara": "diputados", "anio": 2021, "max_seats": 300, "mr_seats": 300, "rp_seats": 0,   "umbral": 0.0,  "max_seats_per_party": None, "quota_method": "hare", "divisor_method": None, "desc": "plan_c"},
    # DIPUTADOS 2024
    {"camara": "diputados", "anio": 2024, "max_seats": 500, "mr_seats": 300, "rp_seats": 200, "umbral": 0.03, "max_seats_per_party": 300, "quota_method": "hare", "divisor_method": "dhondt", "desc": "vigente"},
    {"camara": "diputados", "anio": 2024, "max_seats": 300, "mr_seats": 0,   "rp_seats": 300, "umbral": 0.03, "max_seats_per_party": None, "quota_method": "hare", "divisor_method": None, "desc": "plan_a"},
    {"camara": "diputados", "anio": 2024, "max_seats": 300, "mr_seats": 300, "rp_seats": 0,   "umbral": 0.0,  "max_seats_per_party": None, "quota_method": "hare", "divisor_method": None, "desc": "plan_c"},
    # SENADO 2018
    {"camara": "senado", "anio": 2018, "total_mr_seats": 96, "total_rp_seats": 32, "umbral": 0.03, "quota_method": "hare", "divisor_method": "dhondt", "desc": "vigente"},
    {"camara": "senado", "anio": 2018, "total_mr_seats": 0,  "total_rp_seats": 96, "umbral": 0.03, "quota_method": "hare", "divisor_method": None, "desc": "plan_a"},
    {"camara": "senado", "anio": 2018, "total_mr_seats": 64, "total_rp_seats": 0,  "umbral": 0.0,  "quota_method": "hare", "divisor_method": None, "desc": "plan_c"},
    # SENADO 2024
    {"camara": "senado", "anio": 2024, "total_mr_seats": 96, "total_rp_seats": 32, "umbral": 0.03, "quota_method": "hare", "divisor_method": "dhondt", "desc": "vigente"},
    {"camara": "senado", "anio": 2024, "total_mr_seats": 0,  "total_rp_seats": 96, "umbral": 0.03, "quota_method": "hare", "divisor_method": None, "desc": "plan_a"},
    {"camara": "senado", "anio": 2024, "total_mr_seats": 64, "total_rp_seats": 0,  "umbral": 0.0,  "quota_method": "hare", "divisor_method": None, "desc": "plan_c"},
]

resultados = []

for esc in escenarios:
    camara = esc["camara"]
    anio = esc["anio"]
    desc = esc["desc"]
    if camara == "diputados":
        path_parquet = f"data/computos_diputados_{anio}.parquet"
        path_siglado = f"data/siglado-diputados-{anio}.csv"
        res = procesar_diputados_parquet(
            path_parquet=path_parquet,
            partidos_base=None,
            anio=anio,
            path_siglado=path_siglado,
            max_seats=esc["max_seats"],
            sistema="mixto",
            mr_seats=esc["mr_seats"],
            rp_seats=esc["rp_seats"],
            umbral=esc["umbral"],
            max_seats_per_party=esc["max_seats_per_party"],
            quota_method=esc["quota_method"],
            divisor_method=esc["divisor_method"]
        )
    else:
        path_parquet = f"data/computos_senado_{anio}.parquet"
        # Usar archivos específicos de siglado para cada año
        if anio == 2018:
            path_siglado = "data/siglado_senado_2018_corregido.csv"
        else:
            path_siglado = f"data/siglado-senado-{anio}.csv"
        # Convertir parámetros de senado al formato esperado por la función
        max_seats = esc.get("total_mr_seats", 64) + esc.get("total_rp_seats", 32)
        mr_seats = esc.get("total_mr_seats", 64)  
        rp_seats = esc.get("total_rp_seats", 32)
        res = procesar_senadores_parquet(
            path_parquet=path_parquet,
            partidos_base=None,
            anio=anio,
            path_siglado=path_siglado,
            max_seats=max_seats,
            sistema="mixto",
            mr_seats=mr_seats,
            rp_seats=rp_seats,
            umbral=esc["umbral"],
            quota_method=esc["quota_method"],
            divisor_method=esc["divisor_method"]
        )
    for partido, escanos in res["tot"].items():
        resultados.append({
            "anio": anio,
            "camara": camara,
            "esquema": desc,
            "partido": partido,
            "escanos": escanos,
            "mr": res["mr"].get(partido, 0),
            "rp": res["rp"].get(partido, 0),
            "votos": res["votos"].get(partido, 0),
            "ok": res["ok"].get(partido, False)
        })

# Guardar resultados
pd.DataFrame(resultados).to_csv("resultados_pipeline.csv", index=False)
print("Resultados guardados en resultados_pipeline.csv")