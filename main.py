from fastapi import FastAPI, HTTPException, Query, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import sys
import os
import json
from typing import Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

# Agregar el directorio actual al path para importaciones
sys.path.append('.')

from engine.procesar_senadores_v2 import procesar_senadores_v2  
from engine.procesar_diputados_v2 import procesar_diputados_v2
from engine.redistribucion_votos import simular_escenario_electoral, redistribuir_votos_mixto
# kpi_utils se encuentra en el paquete engine (no en outputs)
from engine.kpi_utils import calcular_kpis_electorales, formato_seat_chart

# Mapea colores por partido
PARTY_COLORS = {
    "MORENA": "#8B2231",
    "PAN": "#0055A5",
    "PRI": "#0D7137",
    "PT": "#D52B1E",
    "PVEM": "#1E9F00",
    "MC": "#F58025",
    "PRD": "#FFCC00",
    "PES": "#6A1B9A",
    "NA": "#00B2E3",
    "FXM": "#FF69B4",
}

# Funciones auxiliares para KPIs
def safe_mae(v, s):
    v = [x for x in v if x is not None]
    s = [x for x in s if x is not None]
    if not v or not s or len(v) != len(s): return 0
    return sum(abs(a-b) for a,b in zip(v,s)) / len(v)

def safe_gallagher(v, s):
    v = [x for x in v if x is not None]
    s = [x for x in s if x is not None]
    if not v or not s or len(v) != len(s): return 0
    return (0.5 * sum((100*(a/(sum(v) or 1)) - 100*(b/(sum(s) or 1)))**2 for a,b in zip(v,s)))**0.5

def calcular_ratios_proporcionalidad(resultados_list, total_votos, total_escanos):
    """
    Calcula métricas de proporcionalidad basadas en ratios escaños/votos
    
    Devuelve métricas más interpretables que el MAE tradicional:
    - ratio_promedio: Promedio ponderado de ratios escaños/votos
    - desviacion_estandar: Dispersión de los ratios
    - coeficiente_variacion: Medida normalizada de desigualdad
    """
    import numpy as np
    
    if not resultados_list or total_votos == 0 or total_escanos == 0:
        return {"ratio_promedio": 1.0, "desviacion_estandar": 0, "coeficiente_variacion": 0}
    
    ratios = []
    pesos_votos = []
    
    for r in resultados_list:
        if r["porcentaje_votos"] > 0:
            # Ratio = % escaños / % votos (perfecto = 1.0)
            ratio = r["porcentaje_escanos"] / r["porcentaje_votos"]
            ratios.append(ratio)
            pesos_votos.append(r["porcentaje_votos"])
    
    if not ratios:
        return {"ratio_promedio": 1.0, "desviacion_estandar": 0, "coeficiente_variacion": 0}
    
    # Promedio ponderado por votos
    ratios = np.array(ratios)
    pesos = np.array(pesos_votos)
    
    ratio_promedio = np.average(ratios, weights=pesos)
    
    # Desviación estándar ponderada
    varianza_ponderada = np.average((ratios - ratio_promedio)**2, weights=pesos)
    desviacion_estandar = np.sqrt(varianza_ponderada)
    
    # Coeficiente de variación (dispersión relativa)
    coeficiente_variacion = desviacion_estandar / ratio_promedio if ratio_promedio != 0 else 0
    
    return {
        "ratio_promedio": round(ratio_promedio, 4),
        "desviacion_estandar": round(desviacion_estandar, 4), 
        "coeficiente_variacion": round(coeficiente_variacion, 4)
    }

def transformar_resultado_a_formato_frontend(resultado_dict: Dict, plan: str) -> Dict:
    """
    Transforma el resultado de las funciones de procesamiento al formato esperado por el frontend
    """
    try:
        print(f"[DEBUG] Transformando resultado para plan: {plan}")
        print(f"[DEBUG] Keys en resultado_dict: {list(resultado_dict.keys()) if resultado_dict else 'None'}")
        
        if not resultado_dict or 'tot' not in resultado_dict:
            print(f"[DEBUG] Resultado vacío o sin 'tot', devolviendo vacío")
            return {"plan": plan, "resultados": [], "kpis": {}, "seat_chart": []}
        
        # Obtener datos base
        escanos_dict = resultado_dict.get('tot', {})
        votos_dict = resultado_dict.get('votos', {})
        
        # Crear lista de resultados para el frontend
        resultados = []
        seat_chart = []
        total_votos = sum(votos_dict.values()) if votos_dict else 1
        total_escanos = sum(escanos_dict.values()) if escanos_dict else 1
        
        for partido in escanos_dict.keys():
            # Incluir todos los partidos, incluso con 0 escaños
            votos = votos_dict.get(partido, 0)
            escanos = escanos_dict.get(partido, 0)
            
            resultado_partido = {
                "partido": partido,
                "votos": votos,
                "mr": resultado_dict.get('mr', {}).get(partido, 0),
                "rp": resultado_dict.get('rp', {}).get(partido, 0), 
                "total": escanos,
                "porcentaje_votos": round((votos / total_votos) * 100, 2) if total_votos > 0 else 0,
                "porcentaje_escanos": round((escanos / total_escanos) * 100, 2) if total_escanos > 0 else 0
            }
            resultados.append(resultado_partido)
            
            # Agregar al seat_chart
            seat_chart_item = {
                "party": partido,
                "seats": escanos,
                "color": PARTY_COLORS.get(partido, "#888888"),
                "percent": round((escanos / total_escanos) * 100, 2) if total_escanos > 0 else 0,
                "votes": votos
            }
            seat_chart.append(seat_chart_item)
        
        print(f"[DEBUG] Seat chart construido: {len(seat_chart)} partidos")
        for item in seat_chart:
            print(f"[DEBUG] {item['party']}: {item['seats']} escaños")
        
        # Calcular KPIs
        votos_list = [r["votos"] for r in resultados]
        escanos_list = [r["total"] for r in resultados]
        
        print(f"[DEBUG] Calculando KPIs con:")
        print(f"[DEBUG] Total votos: {total_votos}")
        print(f"[DEBUG] Total escaños: {total_escanos}")
        print(f"[DEBUG] Votos por partido: {votos_list}")
        print(f"[DEBUG] Escaños por partido: {escanos_list}")
        
        # Calcular métricas de proporcionalidad mejoradas
        metricas_proporcionalidad = calcular_ratios_proporcionalidad(resultados, total_votos, total_escanos)
        
        kpis = {
            "total_votos": total_votos,
            "total_escanos": total_escanos,
            "gallagher": safe_gallagher(votos_list, escanos_list),
            "mae_votos_vs_escanos": metricas_proporcionalidad["coeficiente_variacion"],  # Usar coef. variación como "MAE mejorado"
            "ratio_promedio": metricas_proporcionalidad["ratio_promedio"],
            "desviacion_proporcionalidad": metricas_proporcionalidad["desviacion_estandar"],
            "partidos_con_escanos": len([r for r in resultados if r["total"] > 0])
        }
        
        print(f"[DEBUG] KPIs calculados: {kpis}")

        # Campos adicionales de diagnóstico para ayudar al frontend a reproducir/visualizar
        try:
            # diferencias por partido en puntos porcentuales (votos% - escaños%)
            diffs = []
            sum_v = sum(votos_list) or 1
            sum_s = sum(escanos_list) or 1
            for a, b in zip(votos_list, escanos_list):
                diffs.append(round(100 * (a / sum_v) - 100 * (b / sum_s), 6))

            # Añadir campos de diagnóstico (no deben romper al frontend que ya espera 'kpis')
            kpis["_debug"] = {
                "n_parties": len(resultados),
                "diffs_percentage_points": diffs,
                "gallagher_raw": kpis.get("gallagher"),
                # una representación en 'porcentaje' alternativa por si el frontend espera otra escala
                "gallagher_pct": round(kpis.get("gallagher", 0) * 100, 6)
            }
            print(f"[DEBUG] KPIs debug fields: {kpis['_debug']}")
        except Exception:
            pass
        
        out = {
            "plan": plan,
            "resultados": resultados,
            "kpis": kpis,
            "seat_chart": seat_chart,
            "timestamp": datetime.now().isoformat(),
            "cache_buster": datetime.now().timestamp()
        }

        # Incluir metadatos de escalado si existen (trazabilidad)
        try:
            meta = resultado_dict.get('meta', {}) if isinstance(resultado_dict, dict) else {}
            if meta and isinstance(meta, dict) and 'scaled_info' in meta:
                out['meta'] = {
                    'scaled_info': meta.get('scaled_info')
                }
        except Exception:
            pass

        return out
        
    except Exception as e:
        print(f"[ERROR] Error transformando resultado: {e}")
        return {"plan": plan, "resultados": [], "kpis": {"error": str(e)}, "seat_chart": []}

app = FastAPI(
    title="Backend Electoral API",
    description="API para procesamiento de datos electorales con soporte de coaliciones",
    version="2.0.0"
)

# Configurar CORS con opciones más específicas
origins = [
    "http://localhost:3000",  # React dev server
    "http://localhost:3001",  # React dev server alt
    "http://localhost:8000",  # FastAPI docs
    "http://localhost:8080",  # Frontend local
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
    "https://back-electoral.onrender.com",  # Render deployment
    "*"  # Permitir cualquier origen (solo para desarrollo)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Backend Electoral API v2.0", 
        "status": "running",
        "features": ["coalition_processing", "senate", "deputies"]
    }

@app.get("/data/initial")
async def get_initial_data():
    """
    Carga los datos iniciales por defecto: Diputados 2024 vigente
    Este endpoint se usa para cargar los datos al inicializar el frontend
    """
    try:
        print("[INFO] Cargando datos iniciales: Diputados 2024 vigente")
        
        # Procesar datos vigentes de diputados 2024
        resultado = await procesar_diputados(
            anio=2024,
            plan="vigente"
        )
        
        # Agregar metadatos de configuración inicial
        if hasattr(resultado, 'body'):
            import json
            data = json.loads(resultado.body.decode())
        else:
            data = resultado
            
        # Agregar información de configuración inicial
        data["config_inicial"] = {
            "anio": 2024,
            "camara": "diputados", 
            "plan": "vigente",
            "descripcion": "Datos vigentes de la Cámara de Diputados 2024-2027",
            "total_escanos": 500,
            "fecha_carga": pd.Timestamp.now().isoformat()
        }
        
        # Agregar lista de partidos principales para el frontend
        if "resultados" in data and data["resultados"]:
            partidos_principales = []
            for partido_data in data["resultados"]:
                if partido_data.get("porcentaje_votos", 0) > 1:  # Solo partidos con más del 1%
                    partidos_principales.append({
                        "partido": partido_data["partido"],
                        "porcentaje_votos": partido_data["porcentaje_votos"],
                        "escanos": partido_data.get("total", partido_data.get("escanos", 0)),  # Compatibilidad con diferentes formatos
                        "color": PARTY_COLORS.get(partido_data["partido"], "#666666")
                    })
            
            data["partidos_principales"] = sorted(
                partidos_principales, 
                key=lambda x: x["porcentaje_votos"], 
                reverse=True
            )
        
        print(f"[INFO] Datos iniciales cargados exitosamente")
        return data
        
    except Exception as e:
        print(f"[ERROR] Error cargando datos iniciales: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error cargando datos iniciales: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Endpoint de salud del servidor"""
    try:
        return {
            "status": "healthy", 
            "timestamp": pd.Timestamp.now().isoformat(),
            "version": "2.0.0",
            "cors_enabled": True,
            "endpoints": ["procesar/senado", "procesar/diputados"]
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.get("/data/options")
async def get_data_options():
    """
    Obtiene las opciones disponibles de años, cámaras y planes
    Útil para poblar dropdowns en el frontend
    """
    try:
        # Verificar qué archivos de datos están disponibles
        data_dir = "data"
        available_files = os.listdir(data_dir) if os.path.exists(data_dir) else []
        
        # Extraer años disponibles
        anos_diputados = []
        anos_senado = []
        
        for file in available_files:
            if file.startswith("computos_diputados_") and file.endswith(".parquet"):
                ano = file.replace("computos_diputados_", "").replace(".parquet", "")
                if ano.isdigit():
                    anos_diputados.append(int(ano))
            elif file.startswith("computos_senado_") and file.endswith(".parquet"):
                ano = file.replace("computos_senado_", "").replace(".parquet", "")
                if ano.isdigit():
                    anos_senado.append(int(ano))
        
        return {
            "camaras": ["diputados", "senado"],
            "anos_disponibles": {
                "diputados": sorted(anos_diputados, reverse=True),
                "senado": sorted(anos_senado, reverse=True)
            },
            "planes": ["vigente", "actual", "personalizado"],
            "default_config": {
                "camara": "diputados",
                "ano": 2024,
                "plan": "vigente"
            },
            "partidos_conocidos": list(PARTY_COLORS.keys()),
            "colores_partidos": PARTY_COLORS
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo opciones de datos: {str(e)}"
        )

@app.get("/partidos/por-anio")
async def obtener_partidos_por_anio(
    anio: int,
    camara: str = "diputados"
):
    """
    Devuelve partidos disponibles para un año específico con sus porcentajes vigentes
    """
    try:
        print(f"[DEBUG] Obteniendo partidos para año {anio}, cámara {camara}")
        
        # Cargar datos según cámara
        if camara == "diputados":
            path_datos = f"data/computos_diputados_{anio}.parquet"
        elif camara == "senado":  
            path_datos = f"data/computos_senado_{anio}.parquet"
        else:
            raise ValueError(f"Cámara no válida: {camara}")
        
        # Verificar que el archivo existe
        if not os.path.exists(path_datos):
            raise FileNotFoundError(f"No hay datos disponibles para {camara} {anio}")
        
        # Cargar datos
        df = pd.read_parquet(path_datos)
        print(f"[DEBUG] Datos cargados: {len(df)} filas")
        
        # Los datos están en formato ancho (cada partido es una columna)
        # Excluir columnas no partidarias
        columnas_excluir = ['ENTIDAD', 'DISTRITO', 'TOTAL_BOLETAS', 'CI']
        columnas_partidos = [col for col in df.columns if col not in columnas_excluir]
        
        # Calcular votos por partido (suma de cada columna)
        votos_por_partido = {}
        for partido in columnas_partidos:
            votos_por_partido[partido] = df[partido].sum()
        
        # Filtrar partidos con votos > 0 (solo partidos que participaron)
        votos_por_partido = {k: v for k, v in votos_por_partido.items() if v > 0}
        print(f"[DEBUG] Partidos que participaron en {anio}: {list(votos_por_partido.keys())}")
        
        total_votos = sum(votos_por_partido.values())
        
        print(f"[DEBUG] Total votos: {total_votos}")
        print(f"[DEBUG] Partidos encontrados: {list(votos_por_partido.keys())}")
        
        # Crear lista de partidos con porcentajes
        partidos_data = []
        for partido, votos in votos_por_partido.items():
            porcentaje = (votos / total_votos) * 100
            partidos_data.append({
                "partido": partido,
                "votos": int(votos),
                "porcentaje_vigente": round(porcentaje, 2)
            })
        
        # Ordenar por porcentaje descendente
        partidos_data.sort(key=lambda x: x['porcentaje_vigente'], reverse=True)
        
        print(f"[DEBUG] Partidos procesados correctamente: {len(partidos_data)}")
        
        return {
            "anio": anio,
            "camara": camara,
            "partidos": partidos_data,
            "total_votos": int(total_votos),
            "success": True
        }
        
    except Exception as e:
        print(f"[ERROR] Error obteniendo partidos: {e}")
        raise HTTPException(
            status_code=400, 
            detail=f"Error obteniendo partidos para {camara} {anio}: {str(e)}"
        )

@app.options("/procesar/senado")
async def options_procesar_senado():
    """Manejo de CORS preflight para senado"""
    return JSONResponse(
        status_code=200,
        content={"message": "CORS preflight OK"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.post("/procesar/senado")
async def procesar_senado(
    anio: int,
    plan: str = "vigente",
    escanos_totales: Optional[int] = None,
    sistema: Optional[str] = None,
    umbral: Optional[float] = None,
    mr_seats: Optional[int] = None,
    pm_seats: Optional[int] = None,
    rp_seats: Optional[int] = None,
    reparto_mode: str = "divisor",
    reparto_method: str = "dhondt",
    usar_coaliciones: bool = True
):
    """
    Procesa los datos del senado para un año específico con soporte de coaliciones
    
    - **anio**: Año electoral (2018, 2024)
    - **plan**: Plan electoral ("vigente", "plan_a", "plan_c", "personalizado")
    - **escanos_totales**: Número total de escaños (opcional, se calcula automáticamente)
    - **sistema**: Sistema electoral para plan personalizado ("rp", "mixto", "mr")
    - **umbral**: Umbral electoral para plan personalizado (0.0-1.0)
    - **mr_seats**: Escaños de mayoría relativa pura para plan personalizado
    - **pm_seats**: Escaños de primera minoría para plan personalizado (opcional)
    - **rp_seats**: Escaños de representación proporcional para plan personalizado
    - **reparto_mode**: Modo de reparto ("cuota" o "divisor")
    - **reparto_method**: Método específico:
      - Si reparto_mode="cuota": "hare", "droop", "imperiali"
      - Si reparto_mode="divisor": "dhondt", "sainte_lague", "webster"
    """
    try:
        # Normalizar el nombre del plan para compatibilidad con frontend
        plan_normalizado = normalizar_plan(plan)
        print(f"[DEBUG] Senado - Plan original: '{plan}' -> Plan normalizado: '{plan_normalizado}'")
        
        if anio not in [2018, 2024]:
            raise HTTPException(status_code=400, detail="Año no soportado. Use 2018 o 2024")
        
        # Configurar parámetros según el flujo correcto para Senado
        if plan_normalizado == "vigente":
            # Sistema vigente: 64 MR + 32 PM + 32 RP = 128 total
            # mr_seats incluye MR+PM = 96, rp_seats = 32
            sistema_final = "mixto"
            mr_seats_final = 96  # 64 MR + 32 PM (primera minoría)
            rp_seats_final = 32  # 32 RP
            umbral_final = 0.03
            max_seats = 128
            pm_escanos = 32  # PM para sistema vigente
            # Métodos por defecto para vigente
            quota_method_final = "hare"
            divisor_method_final = None
        elif plan_normalizado == "plan_a":
            # Plan A: solo RP = 96 total
            sistema_final = "rp"
            mr_seats_final = 0
            rp_seats_final = 96
            umbral_final = 0.03
            max_seats = 96
            pm_escanos = 0  # Sin PM en plan A
            # Métodos por defecto para Plan A
            quota_method_final = "hare"
            divisor_method_final = None
        elif plan_normalizado == "plan_c":
            # Plan C: solo MR+PM = 64 total (32 MR + 32 PM, sin RP)
            sistema_final = "mr"
            mr_seats_final = 64  # 64 escaños como MR+PM
            rp_seats_final = 0
            umbral_final = 0.0
            max_seats = 64
            pm_escanos = 32  # PM para plan C
            # Métodos por defecto para Plan C (no aplica para MR puro)
            quota_method_final = None
            divisor_method_final = None
        elif plan_normalizado == "personalizado":
            # Plan personalizado con parámetros del usuario
            if not sistema:
                raise HTTPException(status_code=400, detail="Sistema requerido para plan personalizado")
            sistema_final = sistema
            
            # Configurar escaños por separado
            mr_puro = mr_seats if mr_seats is not None else 64
            pm_escanos = pm_seats if pm_seats is not None else 0  # Primera minoría opcional
            rp_escanos = rp_seats if rp_seats is not None else 32
            
            # CORRECCIÓN: PM sale de MR, no se suma al total
            # Si hay PM, se reduce MR proporcionalmente
            if pm_escanos > 0:
                if pm_escanos > mr_puro:
                    raise HTTPException(status_code=400, detail=f"PM ({pm_escanos}) no puede ser mayor que MR ({mr_puro})")
                # Los escaños PM "salen" de los escaños MR
                mr_final_efectivo = mr_puro - pm_escanos
            else:
                mr_final_efectivo = mr_puro
            
            # Para el backend: mr_seats es solo MR efectivo + PM se maneja aparte
            mr_seats_final = mr_puro  # Total MR disponible (incluye PM dentro)
            rp_seats_final = rp_escanos
            umbral_final = umbral if umbral is not None else 0.03
            max_seats = mr_puro + rp_escanos  # Total fijo, PM no suma
            
            print(f"[DEBUG] Plan personalizado - MR original: {mr_puro}, PM: {pm_escanos}, RP: {rp_escanos}")
            print(f"[DEBUG] MR efectivo: {mr_final_efectivo}, PM: {pm_escanos}, Total: {max_seats}")
            print(f"[DEBUG] Total para backend - mr_seats: {mr_seats_final}, rp_seats: {rp_seats_final}")
        else:
            raise HTTPException(status_code=400, detail="Plan no válido. Use 'vigente', 'plan_a', 'plan_c' o 'personalizado'")
            
        # Configurar métodos de reparto según el modo seleccionado
        if reparto_mode == "cuota":
            quota_method_final = reparto_method
            divisor_method_final = None
            print(f"[DEBUG] Senado - Modo cuota seleccionado: {quota_method_final}")
        elif reparto_mode == "divisor":
            quota_method_final = None
            divisor_method_final = reparto_method
            print(f"[DEBUG] Senado - Modo divisor seleccionado: {divisor_method_final}")
        else:
            raise HTTPException(status_code=400, detail="reparto_mode debe ser 'cuota' o 'divisor'")
            
        # Construir paths (corregir para 2018)
        path_parquet = f"data/computos_senado_{anio}.parquet"
        if anio == 2018:
            path_siglado = "data/siglado_senado_2018_corregido.csv"
        else:
            path_siglado = f"data/siglado-senado-{anio}.csv"
        
        # Verificar que existen los archivos
        if not os.path.exists(path_parquet):
            raise HTTPException(status_code=404, detail=f"Archivo no encontrado: {path_parquet}")
        if not os.path.exists(path_siglado):
            raise HTTPException(status_code=404, detail=f"Archivo siglado no encontrado: {path_siglado}")
            
        resultado = procesar_senadores_v2(
            path_parquet=path_parquet,
            anio=anio,
            path_siglado=path_siglado,
            max_seats=max_seats,
            sistema=sistema_final,
            mr_seats=mr_seats_final,
            rp_seats=rp_seats_final,
            umbral=umbral_final,
            pm_seats=pm_escanos,  # ⬅️ AGREGAR PARÁMETRO PM
            quota_method=quota_method_final,
            divisor_method=divisor_method_final,
            usar_coaliciones=usar_coaliciones  # ⬅️ NUEVO: toggle coaliciones
        )
        
        # Transformar al formato esperado por el frontend con colores
        resultado_formateado = transformar_resultado_a_formato_frontend(resultado, plan)
        # Añadir trazas de diagnóstico sobre la redistribución (si existen)
        try:
            trace = {}
            # parquet temporal generado en este request (si existe)
            if locals().get('parquet_replacement'):
                trace['tmp_parquet'] = locals().get('parquet_replacement')
            else:
                trace['tmp_parquet'] = None

            # porcentajes / votos redistribuidos que se usaron (si existen)
            try:
                trace['votos_redistribuidos'] = locals().get('votos_redistribuidos')
            except Exception:
                trace['votos_redistribuidos'] = None

            # Agregar scaled_info si está en la meta del resultado original
            try:
                meta_in = resultado.get('meta', {}) if isinstance(resultado, dict) else {}
                if meta_in and isinstance(meta_in, dict) and 'scaled_info' in meta_in:
                    trace['scaled_info'] = meta_in.get('scaled_info')
            except Exception:
                pass

            # Añadir telemetría raw_body_parsed si existe (por compatibilidad con diputados)
            try:
                trace['raw_body_parsed'] = bool(locals().get('raw_body_parsed', False))
            except Exception:
                trace['raw_body_parsed'] = False

            if trace:
                if 'meta' not in resultado_formateado:
                    resultado_formateado['meta'] = {}
                resultado_formateado['meta']['trace'] = trace
        except Exception as _e:
            print(f"[WARN] No se pudo añadir trace meta: {_e}")

        # Retornar con headers anti-caché para evitar problemas de actualización
        return JSONResponse(
            content=resultado_formateado,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
        
    except Exception as e:
        print(f"[ERROR] Error en /procesar/senado: {str(e)}")
        print(f"[ERROR] Tipo de error: {type(e).__name__}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error procesando senado: {str(e)}")

@app.options("/procesar/diputados")
async def options_procesar_diputados():
    """Manejo de CORS preflight para diputados"""
    return JSONResponse(
        status_code=200,
        content={"message": "CORS preflight OK"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.post("/procesar/diputados")
async def procesar_diputados(
    anio: int,
    request: Request = None,
    plan: str = "vigente",
    escanos_totales: Optional[int] = None,
    sistema: Optional[str] = None,
    umbral: Optional[float] = None,
    mr_seats: Optional[int] = None,
    rp_seats: Optional[int] = None,
    max_seats_per_party: Optional[int] = None,
    sobrerrepresentacion: Optional[float] = None,
    reparto_mode: str = "divisor",
    reparto_method: str = "dhondt",
    usar_coaliciones: bool = True,
    votos_custom: Optional[str] = None,  # JSON string con redistribución
    partidos_fijos: Optional[str] = None,  # JSON string con partidos fijos
    overrides_pool: Optional[str] = None,   # JSON string con overrides del pool
    porcentajes_partidos: Optional[str] = None  # JSON string con porcentajes por partido
):
    """
    Procesa los datos de diputados para un año específico con soporte de coaliciones
    
    - **anio**: Año electoral (2018, 2021, 2024)
    - **plan**: Plan electoral ("vigente", "plan_a", "plan_c", "personalizado")
    - **escanos_totales**: Número total de escaños (opcional, se calcula automáticamente)
    - **sistema**: Sistema electoral para plan personalizado
    - **umbral**: Umbral electoral
    - **mr_seats**: Escaños de mayoría relativa
    - **rp_seats**: Escaños de representación proporcional
    - **max_seats_per_party**: Máximo de escaños por partido
    - **sobrerrepresentacion**: Límite de sobrerrepresentación como porcentaje (ej: 10.8)
    - **reparto_mode**: Modo de reparto ("cuota" o "divisor")
    - **reparto_method**: Método específico:
      - Si reparto_mode="cuota": "hare", "droop", "imperiali"
      - Si reparto_mode="divisor": "dhondt", "sainte_lague", "webster"
    - **votos_custom**: JSON con % de votos por partido {"MORENA":45, "PAN":30, ...}
    - **partidos_fijos**: JSON con partidos fijos {"MORENA":2, "PAN":40}
    - **overrides_pool**: JSON con overrides del pool {"PAN":20, "MC":10}
    - **porcentajes_partidos**: JSON con % de votos por partido {"MORENA":42.5, "PAN":20.7, ...}
    """
    try:
        # Intentar leer body JSON si fue enviado (si el cliente envía JSON en el body
        # preferimos esos valores sobre los query params). Usamos Request para
        # acceder al body de forma segura.
        body_obj = None
        # Telemetría: si usamos el parsing heurístico desde raw body
        raw_body_parsed = False
        if request is not None:
            # Primero intentamos el parseo normal de JSON
            try:
                body_obj = await request.json()
            except Exception:
                body_obj = None
            # Si no obtuvimos un dict, intentar un parsing tolerante desde el body raw
            if not isinstance(body_obj, dict):
                try:
                    raw_bytes = await request.body()
                    if raw_bytes:
                        try:
                            raw_text = raw_bytes.decode('utf-8')
                        except Exception:
                            raw_text = raw_bytes.decode('utf-8', errors='replace')

                        raw_text_stripped = raw_text.strip()
                        # Intentar cargar si parece JSON (comienza con { o [)
                        if raw_text_stripped and raw_text_stripped[0] in ('{', '['):
                            try:
                                parsed = json.loads(raw_text_stripped)
                                body_obj = parsed
                                raw_body_parsed = True
                                print(f"[WARN] Parsed raw body as JSON despite Content-Type: {request.headers.get('content-type')}")
                            except Exception:
                                # No es JSON válido, mantener None
                                body_obj = body_obj or None
                        else:
                            # Si no es JSON completo, pero es un string conteniendo un objecto JSON
                            # (por ejemplo el cliente envía directamente el JSON como text/plain),
                            # intentamos localizar un primer objeto JSON usando heurística sencilla.
                            try:
                                # heurística: buscar la primera ocurrencia de '{' y la última '}'
                                start = raw_text.find('{')
                                end = raw_text.rfind('}')
                                if start != -1 and end != -1 and end > start:
                                    fragment = raw_text[start:end+1]
                                    parsed = json.loads(fragment)
                                    body_obj = parsed
                                    raw_body_parsed = True
                                    print(f"[WARN] Heuristically parsed JSON fragment from raw body (Content-Type={request.headers.get('content-type')})")
                            except Exception:
                                body_obj = body_obj or None
                except Exception:
                    # Si falla leer body raw, simplemente seguimos con body_obj tal cual
                    body_obj = body_obj or None

        # Preferir valores enviados en el body si existen
        if isinstance(body_obj, dict):
            anio = body_obj.get('anio', anio)
            plan = body_obj.get('plan', plan)
            escanos_totales = body_obj.get('escanos_totales', escanos_totales)
            sistema = body_obj.get('sistema', sistema)
            umbral = body_obj.get('umbral', umbral)
            mr_seats = body_obj.get('mr_seats', mr_seats)
            rp_seats = body_obj.get('rp_seats', rp_seats)
            max_seats_per_party = body_obj.get('max_seats_per_party', max_seats_per_party)
            sobrerrepresentacion = body_obj.get('sobrerrepresentacion', sobrerrepresentacion)
            reparto_mode = body_obj.get('reparto_mode', reparto_mode)
            reparto_method = body_obj.get('reparto_method', reparto_method)
            usar_coaliciones = body_obj.get('usar_coaliciones', usar_coaliciones)
            votos_custom = body_obj.get('votos_custom', votos_custom)
            partidos_fijos = body_obj.get('partidos_fijos', partidos_fijos)
            overrides_pool = body_obj.get('overrides_pool', overrides_pool)
            porcentajes_partidos = body_obj.get('porcentajes_partidos', porcentajes_partidos)
            # Soporte para payloads 'desnudos' como {"PRD":90, "PAN":5, ...}
            # Detectar si el body contiene solo claves de partidos en mayúsculas y valores numéricos
            try:
                potential_parties = {k:v for k,v in body_obj.items() if isinstance(k, str) and k.isupper() and isinstance(v, (int,float))}
                # Si hay al menos 2 claves que lucen como partidos y no vienen ya en porcentajes_partidos
                if potential_parties and not porcentajes_partidos:
                    print(f"[DEBUG] Detectado payload desnudo de partidos, mapeando a porcentajes_partidos: {list(potential_parties.keys())}")
                    porcentajes_partidos = potential_parties
            except Exception:
                pass
        print(f"[DEBUG] Iniciando /procesar/diputados con:")
        print(f"[DEBUG] - anio: {anio}")
        print(f"[DEBUG] - plan: {plan}")
        print(f"[DEBUG] - escanos_totales: {escanos_totales}")
        print(f"[DEBUG] - sistema: {sistema}")
        print(f"[DEBUG] - mr_seats: {mr_seats}")
        print(f"[DEBUG] - rp_seats: {rp_seats}")

        # NUEVO: Procesar parámetros de redistribución de votos
        votos_redistribuidos = None
        # Si generamos un parquet temporal con votos redistribuidos, lo almacenamos aquí
        parquet_replacement = None
        # DEBUG CRÍTICO: loguear las keys que llegaron para redistribución (facilita ver en producción)
        keys_present = {
            'votos_custom': bool(votos_custom),
            'partidos_fijos': bool(partidos_fijos),
            'overrides_pool': bool(overrides_pool),
            'porcentajes_partidos': bool(porcentajes_partidos)
        }
        print(f"[DEBUG-REDISTRIB] keys_present: {keys_present}")
        # Si ninguna key relevante llegó, imprimimos un diagnóstico ligero
        if not any(keys_present.values()):
            try:
                body_summary = None
                if isinstance(body_obj, dict):
                    # mostrar solo las primeras 20 keys para no saturar logs
                    keys = list(body_obj.keys())[:20]
                    body_summary = f"dict with keys={keys} (total {len(body_obj)})"
                else:
                    body_summary = repr(body_obj)[:200]

                content_type = None
                try:
                    content_type = request.headers.get('content-type')
                except Exception:
                    content_type = '<unknown>'

                print(f"[DEBUG-REDISTRIB] No redistrib keys present. body_summary={body_summary}, Content-Type={content_type}")
            except Exception as e:
                print(f"[DEBUG-REDISTRIB] Error inspeccionando body para diagnóstico: {e}")
        if votos_custom or partidos_fijos or overrides_pool or porcentajes_partidos:
            print(f"[DEBUG] Redistribución de votos solicitada:")
            print(f"[DEBUG] - votos_custom: {votos_custom}")
            print(f"[DEBUG] - partidos_fijos: {partidos_fijos}")
            print(f"[DEBUG] - overrides_pool: {overrides_pool}")
            print(f"[DEBUG] - porcentajes_partidos: {porcentajes_partidos}")
            
            try:
                # Parsear JSON strings o aceptar dicts ya parseados (frontend puede enviar objeto JSON)
                def _ensure_dict(val):
                    if not val:
                        return {}
                    if isinstance(val, dict):
                        return val
                    if isinstance(val, str):
                        try:
                            return json.loads(val)
                        except Exception as e:
                            raise ValueError(f"No se pudo parsear JSON: {e}")
                    raise ValueError(f"Tipo de dato no soportado para JSON: {type(val)}")

                votos_custom_dict = _ensure_dict(votos_custom)
                partidos_fijos_dict = _ensure_dict(partidos_fijos)
                overrides_pool_dict = _ensure_dict(overrides_pool)
                porcentajes_dict = _ensure_dict(porcentajes_partidos)
                
                # Normalizar porcentajes a 100% si están presentes.
                # Nuevo comportamiento: permitir "overrides" parciales (ej: PRD=90)
                # - Si la suma de porcentajes especificados es > 100 => escalar esos especificados para sumar 100
                # - Si la suma es < 100 => distribuir el remanente (100 - suma) entre los partidos NO especificados
                #   proporcionalmente a sus votos reales en el archivo del año.
                # - Si por alguna razón no se puede leer el archivo de votos, hacemos la normalización clásica (escala total).
                if porcentajes_dict:
                    total_porcentajes = sum(porcentajes_dict.values())
                    print(f"[DEBUG] Suma de porcentajes recibidos: {total_porcentajes}")

                    if total_porcentajes > 0 and abs(total_porcentajes - 100) > 0.01:
                        try:
                            # Intentamos aplicar normalización parcial soportando overrides
                            path_datos_tmp = f"data/computos_diputados_{anio}.parquet"
                            if os.path.exists(path_datos_tmp):
                                df_base = pd.read_parquet(path_datos_tmp)
                                columnas_excluir = ['ENTIDAD', 'DISTRITO', 'TOTAL_BOLETAS', 'CI']
                                partidos_en_archivo = [col for col in df_base.columns if col not in columnas_excluir and df_base[col].sum() > 0]

                                # Separar especificados (overrides) de no especificados
                                specified = {p: v for p, v in porcentajes_dict.items() if p in partidos_en_archivo}
                                unspecified = [p for p in partidos_en_archivo if p not in specified]

                                fixed_sum = sum(specified.values())
                                print(f"[DEBUG] Porcentajes especificados (fijos): {specified}, suma={fixed_sum}")

                                if fixed_sum >= 100.0:
                                    # Escalar los especificados para sumar 100 (no hay remanente)
                                    factor = 100.0 / (fixed_sum or 1.0)
                                    porcentajes_dict = {p: v * factor for p, v in specified.items()}
                                    print(f"[DEBUG] Se escaló especificados a 100% con factor {factor}")
                                else:
                                    # Distribuir el remanente entre los no especificados
                                    remaining = 100.0 - fixed_sum
                                    if unspecified:
                                        votos_unspec = df_base[unspecified].sum()
                                        total_votes_unspec = votos_unspec.sum()
                                        if total_votes_unspec > 0:
                                            distributed = {p: (votos_unspec[p] / total_votes_unspec) * remaining for p in unspecified}
                                        else:
                                            # Si no hay información, repartir equitativamente
                                            distributed = {p: remaining / len(unspecified) for p in unspecified}

                                        # Combinar especificados + distribuidos
                                        porcentajes_dict = {**specified, **distributed}
                                        print(f"[DEBUG] Remanente {remaining} distribuido proporcionalmente entre no-especificados")
                                    else:
                                        # No hay no-especificados: escalar especificados para sumar 100
                                        factor = 100.0 / (fixed_sum or 1.0)
                                        porcentajes_dict = {p: v * factor for p, v in specified.items()}
                                        print(f"[DEBUG] No hubo partidos para distribuir remanente; se escaló especificados con factor {factor}")
                            else:
                                # Fallback: archivo no existe, aplicar la normalización clásica
                                factor_normalizacion = 100.0 / total_porcentajes
                                porcentajes_dict = {partido: porcentaje * factor_normalizacion for partido, porcentaje in porcentajes_dict.items()}
                                print(f"[WARN] No se pudo leer {path_datos_tmp}; aplicada normalización clásica con factor {factor_normalizacion}")

                        except Exception as e:
                            # En caso de cualquier error, usar la normalización simple (comportamiento antiguo)
                            print(f"[WARN] Error normalizando porcentajes parcialmente: {e}; aplicando escala simple")
                            factor_normalizacion = 100.0 / total_porcentajes
                            porcentajes_dict = {partido: porcentaje * factor_normalizacion for partido, porcentaje in porcentajes_dict.items()}

                        nueva_suma = sum(porcentajes_dict.values())
                        print(f"[DEBUG] Porcentajes tras normalización/parcial: {nueva_suma}")
                
                # Determinar archivo de datos
                path_datos = f"data/computos_diputados_{anio}.parquet"
                
                if porcentajes_dict:
                    # Filtrar partidos que SÍ existen en el archivo del año
                    df_temp = pd.read_parquet(path_datos)
                    columnas_excluir = ['ENTIDAD', 'DISTRITO', 'TOTAL_BOLETAS', 'CI']
                    partidos_validos = [col for col in df_temp.columns if col not in columnas_excluir and df_temp[col].sum() > 0]

                    # Filtrar porcentajes para solo incluir partidos válidos del año
                    porcentajes_filtrados = {
                        partido: porcentaje 
                        for partido, porcentaje in porcentajes_dict.items() 
                        if partido in partidos_validos
                    }

                    print(f"[DEBUG] Partidos válidos para {anio}: {partidos_validos}")
                    print(f"[DEBUG] Porcentajes filtrados: {porcentajes_filtrados}")

                    # Re-normalizar después del filtrado
                    if porcentajes_filtrados:
                        total_filtrado = sum(porcentajes_filtrados.values())
                        if total_filtrado > 0:
                            factor = 100.0 / total_filtrado
                            porcentajes_filtrados = {
                                partido: porcentaje * factor 
                                for partido, porcentaje in porcentajes_filtrados.items()
                            }
                            print(f"[DEBUG] Porcentajes re-normalizados: {porcentajes_filtrados}")

                    # Para asegurar un recálculo completo (incluyendo MR por distrito),
                    # generamos un parquet temporal con votos redistribuidos por distrito
                    # usando la función existente `simular_escenario_electoral` que devuelve
                    # (df_redistribuido, porcentajes_finales).
                    try:
                        df_redistribuido, porcentajes_finales = simular_escenario_electoral(
                            path_datos,
                            porcentajes_objetivo=porcentajes_filtrados,
                            partidos_fijos={},
                            overrides_pool={},
                            mantener_geografia=True
                        )
                        # Persistir parquet temporal en outputs/ para ser consumido por el procesador
                        import tempfile
                        import uuid
                        tmp_name = f"outputs/tmp_redistrib_{uuid.uuid4().hex}.parquet"
                        # Asegurarse de que la carpeta exista
                        os.makedirs(os.path.dirname(tmp_name), exist_ok=True)
                        df_redistribuido.to_parquet(tmp_name, index=False)
                        print(f"[DEBUG] Parquet temporal con votos redistribuidos creado: {tmp_name}")

                        votos_redistribuidos = porcentajes_finales
                        # Reemplazar el path_datos por el parquet temporal para forzar
                        # a `procesar_diputados_v2` a recalcular MR a partir de estos votos
                        path_datos = tmp_name
                        # IMPORTANT: si estamos en la ruta del endpoint (no en script), también
                        # asignar parquet_replacement para que la variable usada más abajo
                        # por el endpoint apunte al parquet temporal.
                        try:
                            parquet_replacement = tmp_name
                        except Exception:
                            # En entornos donde parquet_replacement no está definido o es inmutable,
                            # simplemente ignoramos y confiamos en path_datos
                            pass
                    except Exception as e:
                        print(f"[WARN] No se pudo generar parquet temporal redistribuido: {e}")
                        # Caer hacia atrás a usar solo porcentajes_filtrados para redistribución
                        votos_redistribuidos = porcentajes_filtrados
                elif votos_custom_dict:
                    # Usar porcentajes directos proporcionados (funcionalidad anterior)
                    print(f"[DEBUG] Usando porcentajes directos: {votos_custom_dict}")
                    votos_redistribuidos = votos_custom_dict
                else:
                    # Usar redistribución mixta basada en datos reales
                    print(f"[DEBUG] Aplicando redistribución mixta")
                    df_datos, porcentajes_finales = simular_escenario_electoral(
                        path_datos,
                        porcentajes_objetivo={},
                        partidos_fijos=partidos_fijos_dict,
                        overrides_pool=overrides_pool_dict,
                        mantener_geografia=True
                    )
                    votos_redistribuidos = porcentajes_finales
                    print(f"[DEBUG] Votos redistribuidos: {votos_redistribuidos}")
                
            except Exception as e:
                print(f"[ERROR] Error en redistribución de votos: {e}")
                raise HTTPException(status_code=400, detail=f"Error en redistribución de votos: {str(e)}")
        
        # Normalizar el nombre del plan para compatibilidad con frontend
        plan_normalizado = normalizar_plan(plan)
        print(f"[DEBUG] Diputados - Plan original: '{plan}' -> Plan normalizado: '{plan_normalizado}'")
        
        if anio not in [2018, 2021, 2024]:
            raise HTTPException(status_code=400, detail="Año no soportado. Use 2018, 2021 o 2024")
        
        # Configurar parámetros específicos según el plan (solo los básicos)
        if plan_normalizado == "vigente":
            # VIGENTE: 500 total, 200 RP fijos, umbral 3%, tope 300
            max_seats = 500
            mr_seats_final = None  # NO forzar MR, usar cálculo real del siglado
            rp_seats_final = 200   # SÍ forzar 200 RP como en la realidad
            umbral_final = 0.03
            max_seats_per_party_final = 300
            quota_method_final = "hare"
            divisor_method_final = None
            sistema_final = "mixto"
            
        elif plan_normalizado == "plan_a":
            # PLAN A: 300 total (0 MR + 300 RP), umbral 3%, sin tope
            # Ignorar cualquier escanos_totales enviado desde el frontend: plan_a es RP puro 300
            if escanos_totales is not None:
                print(f"[DEBUG] plan_a recibido escanos_totales={escanos_totales} pero será IGNORADO (plan_a fuerza 300)")
            max_seats = 300
            mr_seats_final = 0
            rp_seats_final = 300
            umbral_final = 0.03
            max_seats_per_party_final = None
            quota_method_final = "hare"
            divisor_method_final = None
            sistema_final = "rp"  # Solo RP
            
        elif plan_normalizado == "plan_c":
            # PLAN C: 300 total (300 MR + 0 RP), sin umbral, sin tope
            # Ignorar cualquier escanos_totales enviado desde el frontend: plan_c es MR puro 300
            if escanos_totales is not None:
                print(f"[DEBUG] plan_c recibido escanos_totales={escanos_totales} pero será IGNORADO (plan_c fuerza 300)")
            max_seats = 300
            mr_seats_final = 300
            rp_seats_final = 0
            umbral_final = 0.0
            max_seats_per_party_final = None
            quota_method_final = None
            divisor_method_final = None
            sistema_final = "mr"  # Solo MR
            
        elif plan_normalizado == "personalizado":
            # Plan personalizado con parámetros del usuario
            if not sistema:
                raise HTTPException(status_code=400, detail="Sistema requerido para plan personalizado")
            sistema_final = sistema
            
            # Lógica inteligente para parámetros personalizados
            # SIEMPRE usar escanos_totales como base si está definido
            if escanos_totales is not None:
                max_seats = escanos_totales
                print(f"[DEBUG] Usando magnitud base: {max_seats} escaños")
                
                # Distribuir según el sistema elegido
                if sistema_final == "mr":
                    # MR PURO: TODOS los escaños van a MR
                    mr_seats_final = max_seats
                    rp_seats_final = 0
                    print(f"[DEBUG] Sistema MR puro: {mr_seats_final} MR + {rp_seats_final} RP = {max_seats}")
                elif sistema_final == "rp":
                    # RP PURO: TODOS los escaños van a RP
                    mr_seats_final = 0
                    rp_seats_final = max_seats
                    print(f"[DEBUG] Sistema RP puro: {mr_seats_final} MR + {rp_seats_final} RP = {max_seats}")
                else:  # mixto
                    # MIXTO: Usuario debe especificar MR/RP o usar proporción default
                    if mr_seats is not None and rp_seats is not None:
                        # Usuario especificó ambos
                        mr_seats_final = mr_seats
                        rp_seats_final = rp_seats
                        print(f"[DEBUG] Sistema mixto especificado: {mr_seats_final} MR + {rp_seats_final} RP")
                    else:
                        # Usar proporción default 60% MR, 40% RP
                        mr_seats_final = int(max_seats * 0.6)
                        rp_seats_final = max_seats - mr_seats_final
                        print(f"[DEBUG] Sistema mixto automático (60/40): {mr_seats_final} MR + {rp_seats_final} RP = {max_seats}")
            else:
                # FALLBACK: Usuario no especificó magnitud total
                print(f"[DEBUG] No se especificó magnitud, usando parámetros individuales o defaults")
                # Respetar explícitamente los valores individuales si están presentes.
                if sistema_final == "mr":
                    # Para MR puro, usar mr_seats como magnitud total si se proporcionó,
                    # si no, mantener el comportamiento por defecto histórico (usar 300 puede ser sorprendente),
                    # mejor usar el número de distritos calculado a partir del siglado si está disponible;
                    # aquí usamos mr_seats si existe, si no dejamos max_seats sin cambios para que el wrapper asigne por defecto.
                    if mr_seats is not None:
                        mr_seats_final = mr_seats
                        rp_seats_final = 0
                        max_seats = mr_seats_final
                    else:
                        # No se proporcionó mr_seats: dejar que la lógica superior/wrappers decida la magnitud
                        mr_seats_final = None
                        rp_seats_final = 0
                elif sistema_final == "rp":
                    if rp_seats is not None:
                        mr_seats_final = 0
                        rp_seats_final = rp_seats
                        max_seats = rp_seats_final
                    else:
                        mr_seats_final = 0
                        rp_seats_final = None
                else:  # mixto
                    # Para mixto, respetar desagregados si se proporcionan; si no, dejar que defaults en wrappers manejen S
                    mr_seats_final = mr_seats if mr_seats is not None else None
                    rp_seats_final = rp_seats if rp_seats is not None else None
                    if mr_seats_final is not None and rp_seats_final is not None:
                        max_seats = mr_seats_final + rp_seats_final
            
            umbral_final = umbral if umbral is not None else 0.03
            max_seats_per_party_final = max_seats_per_party
            print(f"[DEBUG] max_seats_per_party recibido: {max_seats_per_party}")
            print(f"[DEBUG] max_seats_per_party_final: {max_seats_per_party_final}")
            
            # Configurar métodos de reparto según el modo seleccionado
            if reparto_mode == "cuota":
                quota_method_final = reparto_method
                divisor_method_final = None
                print(f"[DEBUG] Modo cuota seleccionado: {quota_method_final}")
            elif reparto_mode == "divisor":
                quota_method_final = None
                divisor_method_final = reparto_method
                print(f"[DEBUG] Modo divisor seleccionado: {divisor_method_final}")
            else:
                raise HTTPException(status_code=400, detail="reparto_mode debe ser 'cuota' o 'divisor'")
        else:
            raise HTTPException(status_code=400, detail="Plan no válido. Use 'vigente', 'plan_a', 'plan_c' o 'personalizado'")
        
        print(f"[DEBUG] Plan {plan_normalizado}: max_seats={max_seats}, mr={mr_seats_final}, rp={rp_seats_final}, umbral={umbral_final}")

        # Construir paths (si hay un parquet temporal generado por redistribución, usarlo)
        path_parquet = parquet_replacement if parquet_replacement else f"data/computos_diputados_{anio}.parquet"
        path_siglado = f"data/siglado-diputados-{anio}.csv"
        
        # Verificar que existen los archivos
        if not os.path.exists(path_parquet):
            raise HTTPException(status_code=404, detail=f"Archivo no encontrado: {path_parquet}")
        if not os.path.exists(path_siglado):
            raise HTTPException(status_code=404, detail=f"Archivo siglado no encontrado: {path_siglado}")
            
        resultado = procesar_diputados_v2(
            path_parquet=path_parquet,
            anio=anio,
            path_siglado=path_siglado,
            max_seats=max_seats,
            sistema=sistema_final,
            mr_seats=mr_seats_final,
            rp_seats=rp_seats_final,
            umbral=umbral_final,
            max_seats_per_party=max_seats_per_party_final,
            sobrerrepresentacion=sobrerrepresentacion,
            quota_method=quota_method_final,
            divisor_method=divisor_method_final,
            usar_coaliciones=usar_coaliciones,
            votos_redistribuidos=votos_redistribuidos,
            print_debug=True
        )
        
        # Debug: Verificar qué devuelve procesar_diputados_v2
        print(f"[DEBUG] Resultado de procesar_diputados_v2: {resultado}")
        if 'tot' in resultado:
            print(f"[DEBUG] Escaños totales por partido: {resultado['tot']}")
            print(f"[DEBUG] Suma total escaños: {sum(resultado['tot'].values())}")
        
        # Transformar al formato esperado por el frontend con colores
        resultado_formateado = transformar_resultado_a_formato_frontend(resultado, plan)

        # Intentar añadir trazas de redistribución (tmp_parquet, votos_redistribuidos, scaled_info)
        try:
            trace = {}
            if 'parquet_replacement' in locals() and parquet_replacement:
                trace['tmp_parquet'] = parquet_replacement
            else:
                trace['tmp_parquet'] = None

            try:
                trace['votos_redistribuidos'] = votos_redistribuidos if 'votos_redistribuidos' in locals() else None
            except Exception:
                trace['votos_redistribuidos'] = None

            try:
                meta_in = resultado.get('meta', {}) if isinstance(resultado, dict) else {}
                if meta_in and isinstance(meta_in, dict) and 'scaled_info' in meta_in:
                    trace['scaled_info'] = meta_in.get('scaled_info')
            except Exception:
                pass

            # Añadir telemetría raw_body_parsed si existe
            try:
                trace['raw_body_parsed'] = bool(locals().get('raw_body_parsed', False))
            except Exception:
                trace['raw_body_parsed'] = False

            if trace:
                if 'meta' not in resultado_formateado:
                    resultado_formateado['meta'] = {}
                resultado_formateado['meta']['trace'] = trace
        except Exception as _e:
            print(f"[WARN] No se pudo añadir trace meta en diputados: {_e}")

        # Preparar headers; añadir X-Redistrib-Trace para diagnóstico en production si existe parquet
        headers = {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
        try:
            if 'parquet_replacement' in locals() and parquet_replacement:
                headers['X-Redistrib-Trace'] = os.path.basename(parquet_replacement)
        except Exception:
            pass

        # Retornar con headers anti-caché para evitar problemas de actualización
        return JSONResponse(
            content=resultado_formateado,
            headers=headers
        )
        
    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__
        print(f"[ERROR] Error en /procesar/diputados: {error_msg}")
        print(f"[ERROR] Tipo de error: {error_type}")
        import traceback
        traceback_str = traceback.format_exc()
        print(f"[ERROR] Traceback completo: {traceback_str}")
        
        # Crear mensaje de error más informativo
        detail_msg = f"Error procesando diputados: {error_type} - {error_msg}"
        if not error_msg.strip():
            detail_msg = f"Error procesando diputados: {error_type} - Error silencioso en el procesamiento"
        
        raise HTTPException(status_code=500, detail=detail_msg)

@app.get("/años-disponibles")
async def años_disponibles():
    """Retorna los años disponibles para procesamiento"""
    return {
        "senado": [2018, 2024],
        "diputados": [2018, 2021, 2024],
        "planes": ["vigente", "plan_a", "plan_c", "personalizado"]
    }

@app.get("/coaliciones/{anio}")
async def obtener_coaliciones(anio: int):
    """
    Obtiene las coaliciones detectadas para un año específico
    """
    try:
        coaliciones_conocidas = {
            2018: {
                "senado": {
                    "POR MEXICO AL FRENTE": ["PAN", "PRD", "MC"],
                    "JUNTOS HAREMOS HISTORIA": ["MORENA", "PT"]
                },
                "diputados": {
                    "POR MEXICO AL FRENTE": ["PAN", "PRD", "MC"],
                    "JUNTOS HAREMOS HISTORIA": ["MORENA", "PT"]
                }
            },
            2024: {
                "senado": {
                    "FUERZA Y CORAZON POR MEXICO": ["PAN", "PRD", "PRI"],
                    "SIGAMOS HACIENDO HISTORIA": ["MORENA", "PT", "PVEM"]
                },
                "diputados": {
                    "FUERZA Y CORAZON POR MEXICO": ["PAN", "PRD", "PRI"],
                    "SIGAMOS HACIENDO HISTORIA": ["MORENA", "PT", "PVEM"]
                }
            }
        }
        
        return {
            "anio": anio,
            "coaliciones_senado": coaliciones_conocidas.get(anio, {}).get("senado", {}),
            "coaliciones_diputados": coaliciones_conocidas.get(anio, {}).get("diputados", {})
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo coaliciones: {str(e)}")

@app.get("/kpis/{camara}/{anio}")
async def obtener_kpis(
    camara: str,
    anio: int,
    plan: str = "vigente",
    escanos_totales: Optional[int] = None,
    sistema: Optional[str] = None,
    umbral: Optional[float] = None,
    mr_seats: Optional[int] = None,
    rp_seats: Optional[int] = None,
    max_seats_per_party: Optional[int] = None,
    sobrerrepresentacion: Optional[float] = None,
    reparto_mode: str = "divisor",
    reparto_method: str = "dhondt",
    usar_coaliciones: bool = True,
    votos_custom: Optional[str] = None,
    partidos_fijos: Optional[str] = None,
    overrides_pool: Optional[str] = None,
    porcentajes_partidos: Optional[str] = None,
):
    """
    Obtiene los KPIs electorales para una cámara y año específicos
    Usa los nuevos endpoints de procesamiento para obtener datos actualizados
    """
    try:
        if camara not in ["senado", "diputados"]:
            raise HTTPException(status_code=400, detail="Cámara debe ser 'senado' o 'diputados'")
        
        # Llamar al endpoint de procesamiento correspondiente y reenviar parámetros
        if camara == "senado":
            response = await procesar_senado(
                anio=anio,
                plan=plan,
                escanos_totales=escanos_totales,
                sistema=sistema,
                umbral=umbral,
                mr_seats=mr_seats,
                rp_seats=rp_seats,
                reparto_mode=reparto_mode,
                reparto_method=reparto_method,
                usar_coaliciones=usar_coaliciones,
            )
        else:
            response = await procesar_diputados(
                anio=anio,
                plan=plan,
                escanos_totales=escanos_totales,
                sistema=sistema,
                umbral=umbral,
                mr_seats=mr_seats,
                rp_seats=rp_seats,
                max_seats_per_party=max_seats_per_party,
                sobrerrepresentacion=sobrerrepresentacion,
                reparto_mode=reparto_mode,
                reparto_method=reparto_method,
                usar_coaliciones=usar_coaliciones,
                votos_custom=votos_custom,
                partidos_fijos=partidos_fijos,
                overrides_pool=overrides_pool,
                porcentajes_partidos=porcentajes_partidos,
            )
        
        # Extraer el contenido del JSONResponse
        if hasattr(response, 'body'):
            # Es un JSONResponse, extraer el contenido
            import json
            resultado = json.loads(response.body.decode())
        else:
            # Es un diccionario directo
            resultado = response
        
        # Calcular KPIs usando los resultados actualizados
        kpis = calcular_kpis_electorales(resultado, anio, camara)
        
        # Retornar con headers anti-caché
        return JSONResponse(
            content=kpis,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo KPIs: {str(e)}")

@app.get("/seat-chart/{camara}/{anio}")
async def obtener_seat_chart(
    camara: str,
    anio: int,
    plan: str = "vigente",
    escanos_totales: Optional[int] = None,
    sistema: Optional[str] = None,
    umbral: Optional[float] = None,
    mr_seats: Optional[int] = None,
    rp_seats: Optional[int] = None,
    max_seats_per_party: Optional[int] = None,
    sobrerrepresentacion: Optional[float] = None,
    reparto_mode: str = "divisor",
    reparto_method: str = "dhondt",
    usar_coaliciones: bool = True,
    votos_custom: Optional[str] = None,
    partidos_fijos: Optional[str] = None,
    overrides_pool: Optional[str] = None,
    porcentajes_partidos: Optional[str] = None,
):
    """
    Obtiene los datos formateados para el seat-chart
    Usa los nuevos endpoints de procesamiento para obtener datos actualizados
    """
    try:
        if camara not in ["senado", "diputados"]:
            raise HTTPException(status_code=400, detail="Cámara debe ser 'senado' o 'diputados'")
        
        # Llamar al endpoint de procesamiento correspondiente y reenviar parámetros
        if camara == "senado":
            response = await procesar_senado(
                anio=anio,
                plan=plan,
                escanos_totales=escanos_totales,
                sistema=sistema,
                umbral=umbral,
                mr_seats=mr_seats,
                rp_seats=rp_seats,
                reparto_mode=reparto_mode,
                reparto_method=reparto_method,
                usar_coaliciones=usar_coaliciones,
            )
        else:
            response = await procesar_diputados(
                anio=anio,
                plan=plan,
                escanos_totales=escanos_totales,
                sistema=sistema,
                umbral=umbral,
                mr_seats=mr_seats,
                rp_seats=rp_seats,
                max_seats_per_party=max_seats_per_party,
                sobrerrepresentacion=sobrerrepresentacion,
                reparto_mode=reparto_mode,
                reparto_method=reparto_method,
                usar_coaliciones=usar_coaliciones,
                votos_custom=votos_custom,
                partidos_fijos=partidos_fijos,
                overrides_pool=overrides_pool,
                porcentajes_partidos=porcentajes_partidos,
            )
        
        # Extraer el contenido del JSONResponse
        if hasattr(response, 'body'):
            # Es un JSONResponse, extraer el contenido
            import json
            resultado = json.loads(response.body.decode())
        else:
            # Es un diccionario directo
            resultado = response
        
        # Formatear para seat-chart usando los resultados actualizados
        seat_chart_data = formato_seat_chart(resultado)
        # Pasar metadatos si existen para que el frontend pueda mostrar trazabilidad
        try:
            if isinstance(resultado, dict) and 'meta' in resultado and isinstance(resultado['meta'], dict):
                seat_chart_data.setdefault('metadata', {})
                seat_chart_data['metadata']['scaled_info'] = resultado['meta'].get('scaled_info')
        except Exception:
            pass
        
        # Retornar con headers anti-caché
        return JSONResponse(
            content=seat_chart_data,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo seat-chart: {str(e)}")

def normalizar_plan(plan: str) -> str:
    """
    Normaliza los nombres de planes para compatibilidad con frontend
    Frontend puede enviar: A, B, C, vigente, plan_a, plan_c, personalizado
    """
    plan_lower = plan.lower().strip()
    
    # Mapeo de frontend a backend
    mapeo_planes = {
        'a': 'plan_a',
        'b': 'vigente',  # Plan B es el vigente
        'c': 'plan_c',
        'vigente': 'vigente',
        'plan_a': 'plan_a',
        'plan_c': 'plan_c', 
        'personalizado': 'personalizado'
    }
    
    resultado = mapeo_planes.get(plan_lower, plan_lower)
    print(f"[DEBUG] Normalizando plan: '{plan}' -> '{resultado}'")
    return resultado

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)


@app.get("/scaled-siglado/{anio}")
async def obtener_scaled_siglado(anio: int, plan: str = "personalizado"):
    """
    Endpoint de auditoría: devuelve el CSV generado por el escalado del siglado
    si el procesamiento incluyó 'scaled_info' en meta.
    """
    try:
        # Llamar al endpoint de procesamiento para generar metadata (si no está en cache)
        response = await procesar_diputados(anio=anio, plan=plan)
        if hasattr(response, 'body'):
            import json
            resultado = json.loads(response.body.decode())
        else:
            resultado = response

        meta = resultado.get('meta', {}) if isinstance(resultado, dict) else {}
        scaled_info = meta.get('scaled_info') if isinstance(meta, dict) else None
        if not scaled_info:
            raise HTTPException(status_code=404, detail="No hay scaled_siglado disponible para este año/plan")

        # Preferir archivo persistido si existe
        path = scaled_info.get('scaled_csv_path')
        if path:
            import os
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as fh:
                        csv_text = fh.read()
                    return JSONResponse(content={"scaled_csv": csv_text, 'path': path})
                except Exception as e:
                    # Fall back to inline CSV if lectura falla
                    print(f"Error leyendo scaled CSV desde {path}: {e}")

        # Fallback: buscar scaled_csv inline
        csv_text = scaled_info.get('scaled_csv')
        if csv_text:
            return JSONResponse(content={"scaled_csv": csv_text})

        raise HTTPException(status_code=404, detail="No hay scaled_siglado disponible (ni archivo ni inline)")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo scaled_siglado: {str(e)}")
