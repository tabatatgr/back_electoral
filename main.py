from fastapi import FastAPI, HTTPException, Query, Body, Request, Response
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
    - ratio_promedio: Promedio SIMPLE (no ponderado) de ratios escaños/votos de cada partido
      * Valor perfecto = 1.0 (cada partido proporcional a sus votos)
      * > 1.0 indica sobrerrepresentación promedio
      * < 1.0 indica subrepresentación promedio
    - desviacion_estandar: Dispersión de los ratios (qué tan dispersa es la desproporcionalidad)
    - coeficiente_variacion: Medida normalizada de desigualdad (desv_std / promedio)
    """
    import numpy as np
    
    if not resultados_list or total_votos == 0 or total_escanos == 0:
        return {"ratio_promedio": 1.0, "desviacion_estandar": 0, "coeficiente_variacion": 0}
    
    ratios = []
    
    for r in resultados_list:
        if r["porcentaje_votos"] > 0:
            # Ratio = % escaños / % votos (perfecto = 1.0)
            ratio = r["porcentaje_escanos"] / r["porcentaje_votos"]
            ratios.append(ratio)
    
    if not ratios:
        return {"ratio_promedio": 1.0, "desviacion_estandar": 0, "coeficiente_variacion": 0}
    
    # Promedio SIMPLE (no ponderado) - da el ratio promedio de cada partido
    ratios = np.array(ratios)
    
    ratio_promedio = np.mean(ratios)
    
    # Desviación estándar simple
    desviacion_estandar = np.std(ratios)
    
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
                "pm": resultado_dict.get('pm', {}).get(partido, 0),  # Primera minoría
                "rp": resultado_dict.get('rp', {}).get(partido, 0), 
                "total": escanos,
                "porcentaje_votos": round((votos / total_votos) * 100, 2) if total_votos > 0 else 0,
                "porcentaje_escanos": round((escanos / total_escanos) * 100, 2) if total_escanos > 0 else 0
            }
            resultados.append(resultado_partido)
            
            # Agregar al seat_chart con desglose MR/PM/RP
            mr_escanos = resultado_dict.get('mr', {}).get(partido, 0)
            pm_escanos = resultado_dict.get('pm', {}).get(partido, 0)
            rp_escanos = resultado_dict.get('rp', {}).get(partido, 0)
            
            seat_chart_item = {
                "party": partido,
                "seats": escanos,
                "color": PARTY_COLORS.get(partido, "#888888"),
                "percent": round((votos / total_votos) * 100, 2) if total_votos > 0 else 0,  # % de votos
                "votes": votos,
                "mr": mr_escanos,  # Mayoría Relativa
                "pm": pm_escanos,  # Primera Minoría / Plurinominal
                "rp": rp_escanos   # Representación Proporcional
            }
            
            # Validación: MR + PM + RP debe ser igual a TOTAL
            suma_verificacion = mr_escanos + pm_escanos + rp_escanos
            if suma_verificacion != escanos:
                print(f"[WARNING] {partido}: MR({mr_escanos}) + PM({pm_escanos}) + RP({rp_escanos}) = {suma_verificacion} != seats({escanos})")
            
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

        # Incluir metadatos completos (trazabilidad + distribución geográfica)
        try:
            meta = resultado_dict.get('meta', {}) if isinstance(resultado_dict, dict) else {}
            if meta and isinstance(meta, dict):
                out['meta'] = {}
                
                # Incluir scaled_info si existe
                if 'scaled_info' in meta:
                    out['meta']['scaled_info'] = meta.get('scaled_info')
                
                # 📍 NUEVO: Incluir distribución geográfica de MR por estado
                if 'mr_por_estado' in meta:
                    out['meta']['mr_por_estado'] = meta.get('mr_por_estado')
                
                # 📍 NUEVO: Incluir total de distritos por estado
                if 'distritos_por_estado' in meta:
                    out['meta']['distritos_por_estado'] = meta.get('distritos_por_estado')
        except Exception as e:
            print(f"[WARN] Error incluyendo meta en respuesta: {e}")

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
async def get_initial_data(camara: str = "diputados"):
    """
    Carga los datos iniciales por defecto: 2024 vigente
    
    Parámetros:
    - camara: "diputados" o "senadores" (default: "diputados")
    
    Devuelve datos completos incluyendo:
    - seat_chart: Gráfico de escaños
    - mr/rp/tot: Distribución de escaños por partido
    - meta.mr_por_estado: Distribución geográfica de MR por estado
    - meta.distritos_por_estado o meta.senadores_por_estado: Total por estado
    """
    try:
        camara_lower = camara.lower()
        print(f"[INFO] Cargando datos iniciales: {camara_lower.capitalize()} 2024 vigente")
        
        if camara_lower == "diputados":
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
                "mr_escanos": 300,
                "rp_escanos": 200,
                "fecha_carga": pd.Timestamp.now().isoformat()
            }
            
        elif camara_lower == "senadores" or camara_lower == "senado":
            # Procesar datos vigentes de senadores 2024
            resultado = await procesar_senado(
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
                "camara": "senadores", 
                "plan": "vigente",
                "descripcion": "Datos vigentes del Senado 2024-2030",
                "total_escanos": 128,
                "mr_escanos": 64,
                "pm_escanos": 32,
                "rp_escanos": 32,
                "fecha_carga": pd.Timestamp.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Cámara no válida: '{camara}'. Use 'diputados' o 'senadores'"
            )
        
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
        
        # VERIFICAR que los datos geográficos estén presentes
        if "meta" in data:
            if camara_lower == "diputados":
                if "mr_por_estado" not in data["meta"]:
                    print(f"[WARN] mr_por_estado NO presente en respuesta de diputados")
                else:
                    print(f"[INFO] ✅ mr_por_estado presente con {len(data['meta']['mr_por_estado'])} estados")
                    
                if "distritos_por_estado" not in data["meta"]:
                    print(f"[WARN] distritos_por_estado NO presente en respuesta de diputados")
                else:
                    total_distritos = sum(data['meta']['distritos_por_estado'].values())
                    print(f"[INFO] ✅ distritos_por_estado presente: {total_distritos} distritos totales")
            elif camara_lower in ["senadores", "senado"]:
                if "mr_por_estado" not in data["meta"]:
                    print(f"[WARN] mr_por_estado NO presente en respuesta de senadores")
                else:
                    print(f"[INFO] ✅ mr_por_estado presente con {len(data['meta']['mr_por_estado'])} estados")
                    
                if "senadores_por_estado" not in data["meta"]:
                    print(f"[WARN] senadores_por_estado NO presente en respuesta de senadores")
                else:
                    total_senadores = sum(data['meta']['senadores_por_estado'].values())
                    print(f"[INFO] ✅ senadores_por_estado presente: {total_senadores} senadores totales")
        else:
            print(f"[WARN] 'meta' NO presente en respuesta")
        
        print(f"[INFO] Datos iniciales de {camara_lower} cargados exitosamente")
        return data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Error cargando datos iniciales: {str(e)}")
        import traceback
        print(traceback.format_exc())
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
        
        # ============================================================================
        # DETECCIÓN AUTOMÁTICA DE MAYORÍAS (SENADO)
        # ============================================================================
        try:
            # Extraer total de escaños por partido
            resultado_tot = resultado.get('tot', {})
            
            if resultado_tot:
                # Calcular total de escaños y umbrales
                total_escanos = sum(resultado_tot.values())
                mayoria_simple_umbral = total_escanos / 2  # 50%
                mayoria_calificada_umbral = (total_escanos * 2) / 3  # 66.67%
                
                # Estructura para almacenar resultados
                mayorias_info = {
                    "mayoria_simple": {
                        "partido": None,
                        "escanos": 0,
                        "coalicion": False
                    },
                    "mayoria_calificada": {
                        "partido": None,
                        "escanos": 0,
                        "coalicion": False
                    }
                }
                
                # 1. Revisar partidos individuales (ordenados por escaños)
                partidos_ordenados = sorted(resultado_tot.items(), key=lambda x: x[1], reverse=True)
                
                for partido, escanos in partidos_ordenados:
                    # Mayoría calificada (2/3)
                    if escanos >= mayoria_calificada_umbral and mayorias_info["mayoria_calificada"]["partido"] is None:
                        mayorias_info["mayoria_calificada"]["partido"] = partido
                        mayorias_info["mayoria_calificada"]["escanos"] = escanos
                        mayorias_info["mayoria_calificada"]["coalicion"] = False
                    
                    # Mayoría simple (>50%)
                    if escanos > mayoria_simple_umbral and mayorias_info["mayoria_simple"]["partido"] is None:
                        mayorias_info["mayoria_simple"]["partido"] = partido
                        mayorias_info["mayoria_simple"]["escanos"] = escanos
                        mayorias_info["mayoria_simple"]["coalicion"] = False
                
                # 2. Si no hay mayoría individual, revisar coaliciones
                coaliciones_posibles = [
                    {"nombre": "MORENA+PT+PVEM", "partidos": ["MORENA", "PT", "PVEM"]},
                    {"nombre": "PAN+PRI+PRD", "partidos": ["PAN", "PRI", "PRD"]},
                    {"nombre": "MORENA+PT", "partidos": ["MORENA", "PT"]},
                ]
                
                for coalicion in coaliciones_posibles:
                    escanos_coalicion = sum(resultado_tot.get(p, 0) for p in coalicion["partidos"])
                    
                    # Mayoría calificada con coalición
                    if (escanos_coalicion >= mayoria_calificada_umbral and 
                        mayorias_info["mayoria_calificada"]["partido"] is None):
                        mayorias_info["mayoria_calificada"]["partido"] = coalicion["nombre"]
                        mayorias_info["mayoria_calificada"]["escanos"] = escanos_coalicion
                        mayorias_info["mayoria_calificada"]["coalicion"] = True
                    
                    # Mayoría simple con coalición
                    if (escanos_coalicion > mayoria_simple_umbral and 
                        mayorias_info["mayoria_simple"]["partido"] is None):
                        mayorias_info["mayoria_simple"]["partido"] = coalicion["nombre"]
                        mayorias_info["mayoria_simple"]["escanos"] = escanos_coalicion
                        mayorias_info["mayoria_simple"]["coalicion"] = True
                
                # 3. Agregar información de mayorías al resultado
                resultado_formateado["mayorias"] = {
                    "total_escaños": total_escanos,
                    "mayoria_simple": {
                        "umbral": int(mayoria_simple_umbral) + 1,  # >50%
                        "alcanzada": mayorias_info["mayoria_simple"]["partido"] is not None,
                        "partido": mayorias_info["mayoria_simple"]["partido"],
                        "escanos": mayorias_info["mayoria_simple"]["escanos"],
                        "es_coalicion": mayorias_info["mayoria_simple"]["coalicion"]
                    },
                    "mayoria_calificada": {
                        "umbral": int(mayoria_calificada_umbral) + 1,  # ≥66.67%
                        "alcanzada": mayorias_info["mayoria_calificada"]["partido"] is not None,
                        "partido": mayorias_info["mayoria_calificada"]["partido"],
                        "escanos": mayorias_info["mayoria_calificada"]["escanos"],
                        "es_coalicion": mayorias_info["mayoria_calificada"]["coalicion"]
                    }
                }
                
                print(f"[INFO] Senado - Mayorías detectadas:")
                print(f"  Total escaños: {total_escanos}")
                print(f"  Mayoría simple (>{int(mayoria_simple_umbral)}): {mayorias_info['mayoria_simple']['partido']} ({mayorias_info['mayoria_simple']['escanos']} escaños)")
                print(f"  Mayoría calificada (≥{int(mayoria_calificada_umbral)+1}): {mayorias_info['mayoria_calificada']['partido']} ({mayorias_info['mayoria_calificada']['escanos']} escaños)")
                
        except Exception as e_mayorias:
            print(f"[WARN] Error detectando mayorías en Senado: {e_mayorias}")
            # No fallar la petición si hay error en detección de mayorías
            pass
        # ============================================================================
        
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

@app.get("/calcular-limites-pm")
async def calcular_limites_pm(
    sistema: str = "mixto",
    escanos_totales: Optional[int] = None,
    mr_seats: Optional[int] = None
):
    """
    Calcula el límite máximo de Primera Minoría (PM) según el sistema y configuración
    
    - **sistema**: Sistema electoral ("mixto", "mr", "rp")
    - **escanos_totales**: Número total de escaños
    - **mr_seats**: Escaños de mayoría relativa (para sistema mixto)
    
    Returns:
        - max_pm: Límite máximo de PM
        - descripcion: Explicación del límite
    """
    try:
        if sistema == "rp":
            # RP puro: no puede haber PM (PM sale de MR)
            return {
                "max_pm": 0,
                "descripcion": "Sistema RP puro no permite Primera Minoría",
                "valido": False
            }
        
        elif sistema == "mr":
            # MR puro: PM puede ser hasta el tamaño total de la cámara
            max_pm = escanos_totales if escanos_totales else 300  # Default 300
            return {
                "max_pm": max_pm,
                "descripcion": f"Sistema MR puro: PM puede ser hasta {max_pm} (tamaño de cámara)",
                "valido": True
            }
        
        elif sistema == "mixto":
            # Mixto: PM puede ser hasta el número de escaños MR
            if mr_seats is not None:
                max_pm = mr_seats
                return {
                    "max_pm": max_pm,
                    "descripcion": f"Sistema mixto: PM puede ser hasta {max_pm} (escaños MR)",
                    "valido": True
                }
            elif escanos_totales is not None:
                # Si no se especificó mr_seats pero sí escanos_totales, usar 60% default
                max_pm = int(escanos_totales * 0.6)
                return {
                    "max_pm": max_pm,
                    "descripcion": f"Sistema mixto (60/40 default): PM puede ser hasta {max_pm}",
                    "valido": True
                }
            else:
                # Default: 300 escaños MR (sistema vigente)
                return {
                    "max_pm": 300,
                    "descripcion": "Sistema mixto (default): PM puede ser hasta 300 escaños MR",
                    "valido": True
                }
        
        else:
            raise HTTPException(status_code=400, detail="Sistema no válido")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculando límites PM: {str(e)}")

@app.get("/calcular/distribucion_estados")
async def calcular_distribucion_estados(
    anio: int = 2024,
    plan: str = "vigente",
    votos_redistribuidos: Optional[str] = None
):
    """
    Calcula la distribución geográfica de distritos MR por estado y partido.
    
    Útil para mostrar una tabla editable estado por estado con los distritos
    ganados por cada partido en cada entidad federativa.
    
    Parameters:
        - **anio**: Año electoral (2018, 2021, 2024)
        - **plan**: Plan electoral (vigente, plan_a, plan_c, 300_100_con_topes, etc.)
        - **votos_redistribuidos**: JSON opcional con porcentajes de votos personalizados
        
    Returns:
        - distribucion_estados: Lista de estados con distribución por partido
        - totales: Suma total de MR por partido
        - metadatos: Información del cálculo (año, plan, eficiencias)
    """
    try:
        from redistritacion.modulos.reparto_distritos import repartir_distritos_hare
        from redistritacion.modulos.distritacion import cargar_secciones_ine
        from engine.calcular_eficiencia_real import calcular_eficiencia_partidos
        import json
        
        # 1. Determinar configuración del plan
        if plan == "vigente":
            n_distritos = 300
        elif plan == "plan_a":
            n_distritos = 300
        elif plan == "plan_c":
            n_distritos = 300
        elif plan == "300_100_con_topes":
            n_distritos = 300
        elif plan == "300_100_sin_topes":
            n_distritos = 300
        elif plan == "200_200_sin_topes":
            n_distritos = 200
        else:
            n_distritos = 300
        
        # 2. Calcular distribución de distritos por estado (método Hare)
        secciones_df = cargar_secciones_ine()
        poblacion_estados = secciones_df.groupby("ENTIDAD")["POBTOT"].sum().to_dict()
        distribucion_hare = repartir_distritos_hare(poblacion_estados, n_distritos, piso_constitucional=2)
        
        # 3. Calcular eficiencias históricas
        eficiencias = calcular_eficiencia_partidos(anio, usar_coaliciones=True)
        
        # 4. Obtener porcentajes de votos (reales o redistribuidos)
        if votos_redistribuidos:
            votos_dict = json.loads(votos_redistribuidos)
        else:
            # Usar votos reales del año (simplificado - aquí deberías cargar desde computos)
            # Por ahora usamos distribución default como ejemplo
            votos_dict = {
                "MORENA": 35.0,
                "PAN": 22.0,
                "PRI": 18.0,
                "MC": 12.0,
                "PVEM": 8.0,
                "PT": 5.0
            }
        
        # 5. Calcular votos efectivos por partido (votos × eficiencia)
        votos_efectivos = {}
        total_efectivo = 0
        for partido, pct in votos_dict.items():
            if partido in eficiencias:
                efectivo = pct * eficiencias[partido]
                votos_efectivos[partido] = efectivo
                total_efectivo += efectivo
        
        # Normalizar a porcentajes
        votos_efectivos_pct = {p: (v / total_efectivo * 100) for p, v in votos_efectivos.items()}
        
        # 6. Distribuir distritos MR por estado usando votos efectivos
        distribucion_estados = []
        totales_partidos = {p: 0 for p in votos_efectivos_pct.keys()}
        
        # Mapeo de IDs a nombres de estados
        nombres_estados = {
            1: "Aguascalientes", 2: "Baja California", 3: "Baja California Sur",
            4: "Campeche", 5: "Coahuila", 6: "Colima", 7: "Chiapas", 8: "Chihuahua",
            9: "Ciudad de México", 10: "Durango", 11: "Guanajuato", 12: "Guerrero",
            13: "Hidalgo", 14: "Jalisco", 15: "México", 16: "Michoacán",
            17: "Morelos", 18: "Nayarit", 19: "Nuevo León", 20: "Oaxaca",
            21: "Puebla", 22: "Querétaro", 23: "Quintana Roo", 24: "San Luis Potosí",
            25: "Sinaloa", 26: "Sonora", 27: "Tabasco", 28: "Tamaulipas",
            29: "Tlaxcala", 30: "Veracruz", 31: "Yucatán", 32: "Zacatecas"
        }
        
        for estado_id in sorted(distribucion_hare.keys()):
            distritos_estado = distribucion_hare[estado_id]
            
            # Distribuir distritos del estado proporcionalmente a votos efectivos
            distribucion_partidos = {}
            asignados = 0
            
            # Primera vuelta: asignación proporcional
            for partido, pct in sorted(votos_efectivos_pct.items(), key=lambda x: x[1], reverse=True):
                cuota = (pct / 100) * distritos_estado
                asignacion = int(cuota)
                distribucion_partidos[partido] = asignacion
                asignados += asignacion
            
            # Segunda vuelta: residuos (asignar distritos restantes al partido con mayor residuo)
            restantes = distritos_estado - asignados
            if restantes > 0:
                residuos = []
                for partido, pct in votos_efectivos_pct.items():
                    cuota = (pct / 100) * distritos_estado
                    residuo = cuota - distribucion_partidos[partido]
                    residuos.append((partido, residuo))
                
                # Ordenar por residuo descendente
                residuos.sort(key=lambda x: x[1], reverse=True)
                
                # Asignar restantes
                for i in range(restantes):
                    partido = residuos[i][0]
                    distribucion_partidos[partido] += 1
            
            # Actualizar totales
            for partido, distritos in distribucion_partidos.items():
                totales_partidos[partido] += distritos
            
            # Agregar a lista de estados
            distribucion_estados.append({
                "estado_id": estado_id,
                "estado_nombre": nombres_estados.get(estado_id, f"Estado {estado_id}"),
                "distritos_totales": distritos_estado,
                "distribucion_partidos": distribucion_partidos
            })
        
        # 7. Construir respuesta
        return {
            "distribucion_estados": distribucion_estados,
            "totales": totales_partidos,
            "metadatos": {
                "anio": anio,
                "plan": plan,
                "n_distritos": n_distritos,
                "eficiencias": eficiencias,
                "votos_efectivos_pct": votos_efectivos_pct,
                "metodo": "Hare con redistribución geográfica"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculando distribución por estados: {str(e)}")

@app.get("/calcular/mayoria_forzada")
async def calcular_mayoria_forzada_endpoint(
    partido: str,
    tipo_mayoria: str = "simple",
    plan: str = "vigente",
    aplicar_topes: bool = True,
    votos_base: Optional[str] = None,
    anio: int = 2024,
    # Parámetros para configuración personalizada
    escanos_totales: Optional[int] = None,
    mr_seats: Optional[int] = None,
    rp_seats: Optional[int] = None,
    sistema: Optional[str] = None
):
    """
    Calcula y EJECUTA el sistema electoral completo para forzar mayoría.
    
    Devuelve seat_chart completo + KPIs recalculados con TODOS los partidos ajustados.
    
    **IMPORTANTE**:
    - Mayoría simple: funciona en TODOS los escenarios
    - Mayoría calificada: SOLO funciona con aplicar_topes=False
      (con topes del 8%, es matemáticamente imposible para un partido individual)
    
    Parameters:
        - **partido**: Nombre del partido (MORENA, PAN, PRI, MC, PVEM, PT, etc.)
        - **tipo_mayoria**: "simple" (251 dip) o "calificada" (334 dip)
        - **plan**: Plan electoral (vigente, plan_a, plan_c, 200_200_sin_topes, personalizado, etc.)
        - **aplicar_topes**: Si se aplican topes de sobrerrepresentación del 8%
        - **votos_base**: JSON opcional con distribución de votos base (ej: {"MORENA":38,"PAN":22,...})
        - **anio**: Año electoral (2018, 2021, 2024)
        - **escanos_totales**: Total de escaños (para plan personalizado)
        - **mr_seats**: Escaños de mayoría relativa (para plan personalizado)
        - **rp_seats**: Escaños de representación proporcional (para plan personalizado)
        - **sistema**: Sistema electoral: "mixto", "mr", "rp" (requerido para plan personalizado)
    
    Returns:
        - viable: Si es posible alcanzar la mayoría con esa configuración
        - diputados_necesarios: Umbral de mayoría (251 o 334)
        - diputados_obtenidos: Total alcanzado
        - votos_porcentaje: % de votos necesarios
        - mr_asignados: Escaños MR del partido
        - rp_asignados: Escaños RP del partido
        - **seat_chart**: Array completo de todos los partidos RECALCULADOS
        - **kpis**: Gallagher, ratio, total_votos recalculados
    
    Ejemplo de uso:
        GET /calcular/mayoria_forzada?partido=MORENA&tipo_mayoria=simple&plan=vigente&aplicar_topes=true
        GET /calcular/mayoria_forzada?partido=MORENA&tipo_mayoria=simple&plan=personalizado&escanos_totales=128&mr_seats=64&rp_seats=64&sistema=mixto
    """
    try:
        from engine.calcular_mayoria_forzada_v2 import calcular_mayoria_forzada
        import json
        
        # Validar tipo_mayoria
        if tipo_mayoria not in ["simple", "calificada"]:
            raise HTTPException(
                status_code=400,
                detail=f"tipo_mayoria debe ser 'simple' o 'calificada', recibido: '{tipo_mayoria}'"
            )
        
        # Determinar configuración del plan
        # Si el usuario proporcionó parámetros personalizados, usarlos
        if escanos_totales is not None and mr_seats is not None and rp_seats is not None:
            # Configuración personalizada del usuario
            mr_total = mr_seats
            rp_total = rp_seats
            print(f"[DEBUG] Usando configuración personalizada: mr={mr_total}, rp={rp_total}, total={mr_total+rp_total}")
        elif plan == "vigente" or plan == "plan_a" or plan == "plan_c":
            mr_total = 300
            rp_total = 100
        elif plan == "300_100_con_topes":
            mr_total = 300
            rp_total = 100
        elif plan == "300_100_sin_topes":
            mr_total = 300
            rp_total = 100
            aplicar_topes = False  # Forzar sin topes
        elif plan == "200_200_sin_topes":
            mr_total = 200
            rp_total = 200
            aplicar_topes = False  # Forzar sin topes
        elif plan == "240_160_sin_topes":
            mr_total = 240
            rp_total = 160
            aplicar_topes = False  # Forzar sin topes
        elif plan == "240_160_con_topes":
            mr_total = 240
            rp_total = 160
        else:
            mr_total = 300
            rp_total = 100
        
        # Parsear votos_base si se proporcionó
        votos_base_dict = None
        if votos_base:
            try:
                votos_base_dict = json.loads(votos_base)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="votos_base debe ser un JSON válido"
                )
        
        # PASO 1: Calcular configuración de mayoría forzada
        config = calcular_mayoria_forzada(
            partido=partido,
            tipo_mayoria=tipo_mayoria,
            mr_total=mr_total,
            rp_total=rp_total,
            aplicar_topes=aplicar_topes,
            votos_base=votos_base_dict
        )
        
        # Si no es viable, devolver solo eso
        if not config.get('viable', False):
            return {
                "viable": False,
                "mensaje": config.get('razon', 'Mayoría no alcanzable'),
                "diputados_necesarios": 251 if tipo_mayoria == "simple" else 334,
                "max_posible": int(mr_total + rp_total) * 0.60 if aplicar_topes else None,
                "diputados_obtenidos": 0,
                "votos_porcentaje": None
            }
        
        # PASO 2: EJECUTAR sistema electoral completo con votos ajustados
        # Convertir votos_custom a JSON string si es dict
        votos_custom_str = json.dumps(config['votos_custom']) if isinstance(config.get('votos_custom'), dict) else config.get('votos_custom')
        mr_distritos_str = json.dumps(config.get('mr_distritos_manuales')) if isinstance(config.get('mr_distritos_manuales'), dict) else config.get('mr_distritos_manuales')
        
        resultado_completo = await procesar_diputados(
            anio=anio,
            plan=plan,
            aplicar_topes=aplicar_topes,
            votos_custom=votos_custom_str,  # ← Votos ajustados (JSON string)
            mr_distritos_manuales=mr_distritos_str,  # ← MR manual si existe (JSON string)
            # Pasar parámetros de configuración personalizada si vienen del frontend
            escanos_totales=escanos_totales,
            mr_seats=mr_seats,
            rp_seats=rp_seats,
            sistema=sistema
        )
        
        # Extraer el contenido del JSONResponse
        if hasattr(resultado_completo, 'body'):
            import json
            resultado_data = json.loads(resultado_completo.body.decode())
        else:
            resultado_data = resultado_completo
        
        # PASO 3: Extraer datos del partido objetivo
        # El seat_chart está en la raíz, NO en mayorias
        seat_chart = resultado_data.get('seat_chart', [])
        
        if not seat_chart:
            raise HTTPException(
                status_code=500,
                detail=f"No se pudo obtener seat_chart del resultado. Keys disponibles: {list(resultado_data.keys())}"
            )
        
        partido_data = next((p for p in seat_chart if p['party'] == partido), None)
        
        if not partido_data:
            raise HTTPException(
                status_code=500,
                detail=f"Partido {partido} no encontrado en seat_chart. Partidos disponibles: {[p['party'] for p in seat_chart]}"
            )
        
        # PASO 4: Construir respuesta completa
        # Calcular umbral dinámicamente basado en escaños totales
        total_escanos = escanos_totales if escanos_totales is not None else (mr_total + rp_total)
        umbral = (total_escanos // 2) + 1 if tipo_mayoria == "simple" else int(total_escanos * 2 / 3) + 1
        
        # Extraer distribución geográfica del resultado original (no del transformado)
        # Necesitamos acceder al resultado_dict original antes de transformación
        from engine.procesar_diputados_v2 import procesar_diputados_v2
        
        # Re-ejecutar pero ahora capturando resultado directo sin transformar
        resultado_dict_raw = procesar_diputados_v2(
            path_parquet=f"data/computos_diputados_{anio}.parquet",
            anio=anio,
            max_seats=escanos_totales if escanos_totales else (mr_total + rp_total),
            sistema=sistema if sistema else 'mixto',
            mr_seats=mr_total,
            rp_seats=rp_total,
            umbral=0.03,
            aplicar_topes=aplicar_topes,
            usar_coaliciones=True,
            votos_redistribuidos=config.get('votos_custom'),
            mr_ganados_geograficos=config.get('mr_distritos_manuales'),
            print_debug=False
        )
        
        mr_por_estado = resultado_dict_raw.get('meta', {}).get('mr_por_estado')
        distritos_por_estado = resultado_dict_raw.get('meta', {}).get('distritos_por_estado')
        
        # Extraer KPIs del resultado transformado
        kpis = resultado_data.get('kpis', {})
        
        return {
            "viable": True,
            "diputados_necesarios": umbral,
            "diputados_obtenidos": partido_data.get('seats', 0),
            "votos_porcentaje": round(config['detalle']['pct_votos'], 2),
            "mr_asignados": partido_data.get('mr_seats', partido_data.get('mr', 0)),
            "rp_asignados": partido_data.get('rp_seats', partido_data.get('rp', 0)),
            "partido": partido,
            "plan": plan,
            "tipo_mayoria": tipo_mayoria,
            
            # 🔑 CRÍTICO: Seat chart completo RECALCULADO
            "seat_chart": seat_chart,
            
            # 🔑 CRÍTICO: KPIs recalculados (están en la raíz, NO en mayorias)
            "kpis": kpis,
            
            # 📊 NUEVO: Distribución geográfica de MR por estado y partido
            # Estructura: { "AGUASCALIENTES": { "PAN": 2, "MORENA": 1, ... }, ... }
            "mr_por_estado": mr_por_estado,
            
            # 📍 NUEVO: Total de distritos por estado (para mostrar "3/3" en el frontend)
            # Estructura: { "AGUASCALIENTES": 3, "BAJA CALIFORNIA": 8, ... }
            "distritos_por_estado": distritos_por_estado,
            
            # Información adicional
            "advertencias": config.get('advertencias', []),
            "metodo": config.get('metodo', 'Redistritación realista')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculando mayoría forzada: {str(e)}")

@app.get("/calcular/mayoria_forzada_senado")
async def calcular_mayoria_forzada_senado_endpoint(
    partido: str,
    tipo_mayoria: str = "simple",
    plan: str = "vigente",
    aplicar_topes: bool = True,
    anio: int = 2024
):
    """
    Calcula y EJECUTA el sistema electoral completo para forzar mayoría en SENADO.
    
    Devuelve seat_chart completo + KPIs recalculados con TODOS los partidos ajustados.
    
    Parámetros:
    - **partido**: Partido objetivo (MORENA, PAN, PRI, etc.)
    - **tipo_mayoria**: "simple" (>64 senadores) o "calificada" (>=86 senadores)
    - **plan**: Plan electoral
        - "vigente": 64 MR + 32 PM + 32 RP = 128 total
        - "plan_a": 96 RP puro
        - "plan_c": 64 MR+PM sin RP
    - **aplicar_topes**: Si aplica el tope del 8% de sobrerrepresentación
    - **anio**: Año electoral (2024, 2018)
    
    Returns:
        - viable: Si es posible alcanzar la mayoría
        - senadores_necesarios: Umbral (65 o 86)
        - senadores_obtenidos: Total alcanzado
        - votos_porcentaje: % necesario
        - estados_ganados: Número de estados ganados
        - mr_senadores: Senadores MR
        - pm_senadores: Senadores PM
        - rp_senadores: Senadores RP
        - **seat_chart**: Array completo RECALCULADO
        - **kpis**: Datos recalculados
    
    Ejemplo:
        GET /calcular/mayoria_forzada_senado?partido=MORENA&tipo_mayoria=simple&plan=vigente&aplicar_topes=true
    """
    try:
        from engine.calcular_mayoria_forzada_senado import calcular_mayoria_forzada_senado
        from engine.procesar_senadores_v2 import procesar_senadores_v2
        
        # PASO 1: Calcular configuración de mayoría forzada para Senado
        config = calcular_mayoria_forzada_senado(
            partido=partido,
            tipo_mayoria=tipo_mayoria,
            plan=plan,
            aplicar_topes=aplicar_topes,
            anio=anio
        )
        
        # Si no es viable, devolver solo eso
        if not config.get('viable', False):
            return {
                "viable": False,
                "mensaje": config.get('razon', 'Mayoría no alcanzable en Senado'),
                "senadores_necesarios": 65 if tipo_mayoria == "simple" else 86,
                "senadores_obtenidos": 0,
                "votos_porcentaje": None
            }
        
        # PASO 2: EJECUTAR sistema electoral completo con votos ajustados
        resultado_completo = procesar_senadores_v2(
            anio=anio,
            plan=plan,
            aplicar_topes=aplicar_topes,
            votos_custom=config.get('votos_custom'),  # ← Votos ajustados
            estados_ganados_manual=config.get('estados_ganados_manuales')  # ← Estados manuales
        )
        
        # PASO 3: Extraer datos del partido objetivo
        # El seat_chart está en la raíz, NO en mayorias
        seat_chart = resultado_completo['seat_chart']
        partido_data = next((p for p in seat_chart if p['party'] == partido), None)
        
        if not partido_data:
            raise HTTPException(
                status_code=500,
                detail=f"Partido {partido} no encontrado en resultado Senado"
            )
        
        # PASO 4: Construir respuesta completa
        umbral = 65 if tipo_mayoria == "simple" else 86
        
        return {
            "viable": True,
            "senadores_necesarios": umbral,
            "senadores_obtenidos": partido_data['seats'],
            "votos_porcentaje": round(config['detalle']['pct_votos'], 2),
            "estados_ganados": config['detalle'].get('estados_ganados', 0),
            "mr_senadores": partido_data.get('mr_seats', 0),
            "pm_senadores": partido_data.get('pm_seats', 0),
            "rp_senadores": partido_data.get('rp_seats', 0),
            "partido": partido,
            "plan": plan,
            "tipo_mayoria": tipo_mayoria,
            
            # 🔑 CRÍTICO: Seat chart completo RECALCULADO
            "seat_chart": seat_chart,
            
            # 🔑 CRÍTICO: KPIs recalculados (están en la raíz, NO en mayorias)
            "kpis": resultado_completo.get('kpis', {}),
            
            # Información adicional
            "advertencias": config.get('advertencias', []),
            "metodo": config.get('metodo', 'Redistritación realista Senado')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ERROR] Error calculando mayoría forzada Senado: {str(e)}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error calculando mayoría forzada Senado: {str(e)}")

@app.get("/generar/tabla_estados_senado")
async def generar_tabla_estados_senado_endpoint(
    partido: str,
    votos_porcentaje: float,
    anio: int = 2024,
    formato: str = "json"
):
    """
    Genera tabla de estados con el partido ganador y distribución de votos
    
    Parámetros:
    - **partido**: Partido objetivo (MORENA, PAN, etc.)
    - **votos_porcentaje**: Porcentaje de votos a nivel nacional (30-70)
    - **anio**: Año electoral (2024, 2018)
    - **formato**: "json" o "csv"
    
    Ejemplo:
        GET /generar/tabla_estados_senado?partido=MORENA&votos_porcentaje=45&anio=2024
    
    Returns: Tabla con estado, partido_ganador, senadores_mr, votos, porcentaje
    """
    try:
        from engine.calcular_mayoria_forzada_senado import generar_tabla_estados_senado
        
        # Generar tabla
        df = generar_tabla_estados_senado(
            partido=partido,
            votos_porcentaje=votos_porcentaje,
            anio=anio
        )
        
        if df.empty:
            return {
                'error': 'No se pudo generar la tabla',
                'partido': partido,
                'votos_porcentaje': votos_porcentaje
            }
        
        # Convertir a formato solicitado
        if formato == "csv":
            from io import StringIO
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False, encoding='utf-8')
            csv_content = csv_buffer.getvalue()
            
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=estados_senado_{partido}_{int(votos_porcentaje)}pct.csv"
                }
            )
        else:
            # JSON por defecto
            return {
                'partido': partido,
                'votos_porcentaje': votos_porcentaje,
                'total_estados': len(df),
                'total_senadores_mr': len(df) * 2,
                'estados': df.to_dict(orient='records')
            }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ERROR] Error generando tabla estados Senado: {str(e)}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error generando tabla: {str(e)}")

@app.post("/editar/estados_senado")
async def editar_estados_senado_endpoint(
    request: Request
):
    """
    Procesa Senado con distribución manual de estados MR
    
    Body (JSON):
    {
        "anio": 2024,
        "plan": "vigente",
        "estados_manuales": {
            "MORENA": ["CDMX", "MEXICO", "VERACRUZ", ...],
            "PAN": ["GUANAJUATO", "JALISCO", ...],
            "PRI": ["COAHUILA", ...]
        },
        "aplicar_topes": true,
        "usar_coaliciones": true
    }
    
    Returns:
        Resultado completo del procesamiento de Senado con mayorías detectadas
    
    Ejemplo:
        POST /editar/estados_senado
        Body: {"anio": 2024, "plan": "vigente", "estados_manuales": {...}}
    """
    try:
        body = await request.json()
        
        anio = body.get('anio', 2024)
        plan = body.get('plan', 'vigente')
        estados_manuales = body.get('estados_manuales', {})
        aplicar_topes = body.get('aplicar_topes', True)
        usar_coaliciones = body.get('usar_coaliciones', True)
        
        # Validar
        if not estados_manuales:
            raise HTTPException(status_code=400, detail="estados_manuales requerido")
        
        if anio not in [2018, 2024]:
            raise HTTPException(status_code=400, detail="Año no soportado")
        
        # Normalizar nombre del plan
        plan_normalizado = normalizar_plan(plan)
        
        # Configurar según plan
        if plan_normalizado == "vigente":
            sistema_final = "mixto"
            mr_seats_final = 96  # 64 MR + 32 PM
            rp_seats_final = 32
            umbral_final = 0.03
            max_seats = 128
            pm_escanos = 32
        elif plan_normalizado == "plan_a":
            sistema_final = "rp"
            mr_seats_final = 0
            rp_seats_final = 96
            umbral_final = 0.03
            max_seats = 96
            pm_escanos = 0
        elif plan_normalizado == "plan_c":
            sistema_final = "mr"
            mr_seats_final = 64
            rp_seats_final = 0
            umbral_final = 0.0
            max_seats = 64
            pm_escanos = 32
        else:
            raise HTTPException(status_code=400, detail=f"Plan '{plan}' no válido")
        
        # Construir paths
        path_parquet = f"data/computos_senado_{anio}.parquet"
        if anio == 2018:
            path_siglado = "data/siglado_senado_2018_corregido.csv"
        else:
            path_siglado = f"data/siglado-senado-{anio}.csv"
        
        # Verificar archivos
        if not os.path.exists(path_parquet):
            raise HTTPException(status_code=404, detail=f"Archivo no encontrado: {path_parquet}")
        if not os.path.exists(path_siglado):
            raise HTTPException(status_code=404, detail=f"Archivo siglado no encontrado: {path_siglado}")
        
        # Procesar con estados manuales
        # TODO: Implementar modificación del siglado basado en estados_manuales
        # Por ahora, procesar normalmente
        resultado = procesar_senadores_v2(
            path_parquet=path_parquet,
            anio=anio,
            path_siglado=path_siglado,
            max_seats=max_seats,
            sistema=sistema_final,
            mr_seats=mr_seats_final,
            rp_seats=rp_seats_final,
            umbral=umbral_final,
            pm_seats=pm_escanos,
            usar_coaliciones=usar_coaliciones
        )
        
        # Transformar al formato del frontend
        resultado_formateado = transformar_resultado_a_formato_frontend(resultado, plan)
        
        # Detectar mayorías (mismo código que en POST /procesar/senado)
        try:
            resultado_tot = resultado.get('tot', {})
            
            if resultado_tot:
                total_escanos = sum(resultado_tot.values())
                mayoria_simple_umbral = total_escanos / 2
                mayoria_calificada_umbral = (total_escanos * 2) / 3
                
                mayorias_info = {
                    "mayoria_simple": {"partido": None, "escanos": 0, "coalicion": False},
                    "mayoria_calificada": {"partido": None, "escanos": 0, "coalicion": False}
                }
                
                # Revisar partidos individuales
                partidos_ordenados = sorted(resultado_tot.items(), key=lambda x: x[1], reverse=True)
                
                for partido, escanos in partidos_ordenados:
                    if escanos >= mayoria_calificada_umbral and mayorias_info["mayoria_calificada"]["partido"] is None:
                        mayorias_info["mayoria_calificada"]["partido"] = partido
                        mayorias_info["mayoria_calificada"]["escanos"] = escanos
                        mayorias_info["mayoria_calificada"]["coalicion"] = False
                    
                    if escanos > mayoria_simple_umbral and mayorias_info["mayoria_simple"]["partido"] is None:
                        mayorias_info["mayoria_simple"]["partido"] = partido
                        mayorias_info["mayoria_simple"]["escanos"] = escanos
                        mayorias_info["mayoria_simple"]["coalicion"] = False
                
                # Coaliciones
                coaliciones_posibles = [
                    {"nombre": "MORENA+PT+PVEM", "partidos": ["MORENA", "PT", "PVEM"]},
                    {"nombre": "PAN+PRI+PRD", "partidos": ["PAN", "PRI", "PRD"]},
                    {"nombre": "MORENA+PT", "partidos": ["MORENA", "PT"]},
                ]
                
                for coalicion in coaliciones_posibles:
                    escanos_coalicion = sum(resultado_tot.get(p, 0) for p in coalicion["partidos"])
                    
                    if (escanos_coalicion >= mayoria_calificada_umbral and 
                        mayorias_info["mayoria_calificada"]["partido"] is None):
                        mayorias_info["mayoria_calificada"]["partido"] = coalicion["nombre"]
                        mayorias_info["mayoria_calificada"]["escanos"] = escanos_coalicion
                        mayorias_info["mayoria_calificada"]["coalicion"] = True
                    
                    if (escanos_coalicion > mayoria_simple_umbral and 
                        mayorias_info["mayoria_simple"]["partido"] is None):
                        mayorias_info["mayoria_simple"]["partido"] = coalicion["nombre"]
                        mayorias_info["mayoria_simple"]["escanos"] = escanos_coalicion
                        mayorias_info["mayoria_simple"]["coalicion"] = True
                
                # Agregar mayorías al resultado
                resultado_formateado["mayorias"] = {
                    "total_escanos": total_escanos,
                    "mayoria_simple": {
                        "umbral": int(mayoria_simple_umbral) + 1,
                        "alcanzada": mayorias_info["mayoria_simple"]["partido"] is not None,
                        "partido": mayorias_info["mayoria_simple"]["partido"],
                        "escanos": mayorias_info["mayoria_simple"]["escanos"],
                        "es_coalicion": mayorias_info["mayoria_simple"]["coalicion"]
                    },
                    "mayoria_calificada": {
                        "umbral": int(mayoria_calificada_umbral) + 1,
                        "alcanzada": mayorias_info["mayoria_calificada"]["partido"] is not None,
                        "partido": mayorias_info["mayoria_calificada"]["partido"],
                        "escanos": mayorias_info["mayoria_calificada"]["escanos"],
                        "es_coalicion": mayorias_info["mayoria_calificada"]["coalicion"]
                    }
                }
        except Exception as e_mayorias:
            print(f"[WARN] Error detectando mayorías: {e_mayorias}")
        
        # Agregar info de estados editados
        resultado_formateado['estados_editados'] = {
            partido: len(estados) for partido, estados in estados_manuales.items()
        }
        
        return JSONResponse(
            content=resultado_formateado,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ERROR] Error en /editar/estados_senado: {str(e)}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error procesando: {str(e)}")

@app.post("/exportar/escenario_senado")
async def exportar_escenario_senado_endpoint(
    request: Request
):
    """
    Exporta un escenario de distribución de estados a CSV
    
    Body (JSON):
    {
        "nombre_escenario": "MORENA_Mayoria_2024",
        "estados_por_partido": {
            "MORENA": ["CDMX", "MEXICO", ...],
            "PAN": ["GUANAJUATO", ...],
            ...
        },
        "descripcion": "Escenario de mayoría simple MORENA"
    }
    
    Returns:
        CSV file con la distribución de estados
    """
    try:
        body = await request.json()
        
        nombre = body.get('nombre_escenario', 'escenario_senado')
        estados_por_partido = body.get('estados_por_partido', {})
        descripcion = body.get('descripcion', '')
        
        if not estados_por_partido:
            raise HTTPException(status_code=400, detail="estados_por_partido requerido")
        
        # Crear DataFrame
        datos = []
        for partido, estados in estados_por_partido.items():
            for estado in estados:
                datos.append({
                    'estado': estado,
                    'partido_ganador': partido,
                    'senadores_mr': 2  # Siempre 2 por estado en sistema vigente
                })
        
        df = pd.DataFrame(datos)
        
        # Agregar metadata
        import datetime
        metadata_rows = [
            {'estado': f'# Escenario: {nombre}', 'partido_ganador': '', 'senadores_mr': ''},
            {'estado': f'# Descripción: {descripcion}', 'partido_ganador': '', 'senadores_mr': ''},
            {'estado': f'# Fecha: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}', 'partido_ganador': '', 'senadores_mr': ''},
            {'estado': '# ---', 'partido_ganador': '', 'senadores_mr': ''},
        ]
        df_metadata = pd.DataFrame(metadata_rows)
        df_final = pd.concat([df_metadata, df], ignore_index=True)
        
        # Convertir a CSV
        from io import StringIO
        csv_buffer = StringIO()
        df_final.to_csv(csv_buffer, index=False, encoding='utf-8')
        csv_content = csv_buffer.getvalue()
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={nombre}.csv"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ERROR] Error exportando escenario: {str(e)}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error exportando: {str(e)}")

@app.post("/importar/escenario_senado")
async def importar_escenario_senado_endpoint(
    request: Request
):
    """
    Importa un escenario de distribución de estados desde CSV
    
    Body (JSON):
    {
        "csv_content": "estado,partido_ganador,senadores_mr\\nCDMX,MORENA,2\\n..."
    }
    
    Returns:
        {
            "nombre_escenario": "...",
            "estados_por_partido": {...},
            "total_estados": 32,
            "descripcion": "..."
        }
    """
    try:
        body = await request.json()
        csv_content = body.get('csv_content', '')
        
        if not csv_content:
            raise HTTPException(status_code=400, detail="csv_content requerido")
        
        # Leer CSV
        from io import StringIO
        csv_buffer = StringIO(csv_content)
        
        # Extraer metadata (líneas que empiezan con #)
        metadata = {}
        lineas_datos = []
        
        for linea in csv_content.split('\n'):
            linea_limpia = linea.strip()
            if linea_limpia.startswith('#'):
                # Parsear metadata - remover # y parsear
                contenido = linea_limpia[1:].strip()
                if ':' in contenido:
                    key, value = contenido.split(':', 1)
                    # Limpiar comas finales del CSV y espacios
                    value_limpio = value.strip().rstrip(',')
                    metadata[key.strip()] = value_limpio
            else:
                if linea_limpia:  # Solo agregar líneas no vacías
                    lineas_datos.append(linea)
        
        # Leer datos
        csv_datos = '\n'.join(lineas_datos)
        df = pd.read_csv(StringIO(csv_datos))
        
        # Agrupar por partido
        estados_por_partido = {}
        for _, row in df.iterrows():
            partido = row['partido_ganador']
            estado = row['estado']
            
            if partido not in estados_por_partido:
                estados_por_partido[partido] = []
            estados_por_partido[partido].append(estado)
        
        return {
            'nombre_escenario': metadata.get('Escenario', 'Importado'),
            'descripcion': metadata.get('Descripción', ''),
            'fecha': metadata.get('Fecha', ''),
            'estados_por_partido': estados_por_partido,
            'total_estados': len(df),
            'partidos': list(estados_por_partido.keys())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ERROR] Error importando escenario: {str(e)}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error importando: {str(e)}")

@app.get("/generar/tabla_distritos_diputados")
async def generar_tabla_distritos_diputados_endpoint(
    partido: str,
    votos_porcentaje: float,
    anio: int = 2024,
    mr_total: int = 300,
    formato: str = "json"
):
    """
    Genera tabla de distritos con el partido ganador y distribución de votos
    
    Parámetros:
    - **partido**: Partido objetivo (MORENA, PAN, etc.)
    - **votos_porcentaje**: Porcentaje de votos a nivel nacional (30-70)
    - **anio**: Año electoral (2024, 2021, 2018)
    - **mr_total**: Total de distritos MR (default 300)
    - **formato**: "json" o "csv"
    
    Ejemplo:
        GET /generar/tabla_distritos_diputados?partido=MORENA&votos_porcentaje=45&anio=2024
    
    Returns: Tabla con entidad, distrito, partido_ganador, votos, porcentaje
    """
    try:
        from engine.calcular_mayoria_forzada_v2 import calcular_distritos_mr_realistas
        
        # Calcular distribución realista
        votos_decimal = votos_porcentaje / 100.0
        resultado = calcular_distritos_mr_realistas(
            partido=partido,
            votos_objetivo=votos_decimal,
            anio=anio,
            mr_total=mr_total
        )
        
        if not resultado.get('viable'):
            return {
                'error': 'No se pudo generar la tabla',
                'partido': partido,
                'votos_porcentaje': votos_porcentaje
            }
        
        # Obtener distribución por estado
        distribucion = resultado.get('distribucion_por_estado', {})
        
        # Crear DataFrame con distritos
        datos = []
        for estado, info in distribucion.items():
            distritos_ganados = info.get('distritos_mr', 0)
            for distrito in range(1, distritos_ganados + 1):
                datos.append({
                    'ENTIDAD': estado,
                    'DISTRITO': distrito,
                    'partido_ganador': partido,
                    'votos_estimados': info.get('votos_partido', 0) // distritos_ganados if distritos_ganados > 0 else 0
                })
        
        df = pd.DataFrame(datos)
        
        if df.empty:
            return {
                'error': 'No se pudo generar la tabla',
                'partido': partido,
                'votos_porcentaje': votos_porcentaje
            }
        
        # Convertir a formato solicitado
        if formato == "csv":
            from io import StringIO
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False, encoding='utf-8')
            csv_content = csv_buffer.getvalue()
            
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=distritos_diputados_{partido}_{int(votos_porcentaje)}pct.csv"
                }
            )
        else:
            # JSON por defecto
            return {
                'partido': partido,
                'votos_porcentaje': votos_porcentaje,
                'total_distritos': len(df),
                'distribucion_por_estado': df.groupby('ENTIDAD').size().to_dict(),
                'distritos': df.to_dict(orient='records')
            }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ERROR] Error generando tabla distritos Diputados: {str(e)}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error generando tabla: {str(e)}")

@app.post("/exportar/escenario_diputados")
async def exportar_escenario_diputados_endpoint(
    request: Request
):
    """
    Exporta un escenario de distribución de distritos MR a CSV
    
    Body (JSON):
    {
        "nombre_escenario": "MORENA_Mayoria_300MR_2024",
        "distritos_por_partido": {
            "MORENA": [
                {"entidad": "CDMX", "distrito": 1},
                {"entidad": "CDMX", "distrito": 2},
                ...
            ],
            "PAN": [...],
            ...
        },
        "descripcion": "Escenario de mayoría simple MORENA con 145 MR"
    }
    
    Returns:
        CSV file con la distribución de distritos
    """
    try:
        body = await request.json()
        
        nombre = body.get('nombre_escenario', 'escenario_diputados')
        distritos_por_partido = body.get('distritos_por_partido', {})
        descripcion = body.get('descripcion', '')
        
        if not distritos_por_partido:
            raise HTTPException(status_code=400, detail="distritos_por_partido requerido")
        
        # Crear DataFrame
        datos = []
        for partido, distritos in distritos_por_partido.items():
            for distrito_info in distritos:
                datos.append({
                    'entidad': distrito_info.get('entidad'),
                    'distrito': distrito_info.get('distrito'),
                    'partido_ganador': partido
                })
        
        df = pd.DataFrame(datos)
        
        # Agregar metadata
        import datetime
        metadata_rows = [
            {'entidad': f'# Escenario: {nombre}', 'distrito': '', 'partido_ganador': ''},
            {'entidad': f'# Descripción: {descripcion}', 'distrito': '', 'partido_ganador': ''},
            {'entidad': f'# Fecha: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}', 'distrito': '', 'partido_ganador': ''},
            {'entidad': f'# Total distritos: {len(df)}', 'distrito': '', 'partido_ganador': ''},
            {'entidad': '# ---', 'distrito': '', 'partido_ganador': ''},
        ]
        df_metadata = pd.DataFrame(metadata_rows)
        df_final = pd.concat([df_metadata, df], ignore_index=True)
        
        # Convertir a CSV
        from io import StringIO
        csv_buffer = StringIO()
        df_final.to_csv(csv_buffer, index=False, encoding='utf-8')
        csv_content = csv_buffer.getvalue()
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={nombre}.csv"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ERROR] Error exportando escenario diputados: {str(e)}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error exportando: {str(e)}")

@app.post("/importar/escenario_diputados")
async def importar_escenario_diputados_endpoint(
    request: Request
):
    """
    Importa un escenario de distribución de distritos MR desde CSV
    
    Body (JSON):
    {
        "csv_content": "entidad,distrito,partido_ganador\\nCDMX,1,MORENA\\n..."
    }
    
    Returns:
        {
            "nombre_escenario": "...",
            "distritos_por_partido": {...},
            "total_distritos": 300,
            "descripcion": "..."
        }
    """
    try:
        body = await request.json()
        csv_content = body.get('csv_content', '')
        
        if not csv_content:
            raise HTTPException(status_code=400, detail="csv_content requerido")
        
        # Leer CSV
        from io import StringIO
        
        # Extraer metadata (líneas que empiezan con #)
        metadata = {}
        lineas_datos = []
        
        for linea in csv_content.split('\n'):
            linea_limpia = linea.strip()
            if linea_limpia.startswith('#'):
                # Parsear metadata - remover # y parsear
                contenido = linea_limpia[1:].strip()
                if ':' in contenido:
                    key, value = contenido.split(':', 1)
                    # Limpiar comas finales del CSV y espacios
                    value_limpio = value.strip().rstrip(',')
                    metadata[key.strip()] = value_limpio
            else:
                if linea_limpia:  # Solo agregar líneas no vacías
                    lineas_datos.append(linea)
        
        # Leer datos
        csv_datos = '\n'.join(lineas_datos)
        df = pd.read_csv(StringIO(csv_datos))
        
        # Agrupar por partido
        distritos_por_partido = {}
        for _, row in df.iterrows():
            partido = row['partido_ganador']
            distrito_info = {
                'entidad': row['entidad'],
                'distrito': row['distrito']
            }
            
            if partido not in distritos_por_partido:
                distritos_por_partido[partido] = []
            distritos_por_partido[partido].append(distrito_info)
        
        return {
            'nombre_escenario': metadata.get('Escenario', 'Importado'),
            'descripcion': metadata.get('Descripción', ''),
            'fecha': metadata.get('Fecha', ''),
            'total_distritos': metadata.get('Total distritos', len(df)),
            'distritos_por_partido': distritos_por_partido,
            'partidos': list(distritos_por_partido.keys()),
            'distribucion_por_estado': df.groupby(['entidad', 'partido_ganador']).size().to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ERROR] Error importando escenario diputados: {str(e)}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error importando: {str(e)}")

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
    umbral: Optional[float] = 0.03,  # Default 3% (umbral oficial IFE/INE)
    mr_seats: Optional[int] = None,
    pm_seats: Optional[int] = None,  # ← NUEVO: Escaños de primera minoría
    rp_seats: Optional[int] = None,
    total_distritos: Optional[int] = None,  # ← NUEVO: Total de distritos electorales (default: 300)
    max_seats_per_party: Optional[int] = None,
    sobrerrepresentacion: Optional[float] = None,
    aplicar_topes: bool = True,  # ← NUEVO: Controlar si se aplican topes constitucionales
    reparto_mode: str = "cuota",  # Default: cuota (Hare es el método oficial en México)
    reparto_method: str = "hare",  # Default: Hare (método oficial IFE/INE)
    usar_coaliciones: bool = True,
    # redistritacion_geografica REMOVIDO - SIEMPRE True internamente
    mr_distritos_manuales: Optional[str] = None,  # ← NUEVO: JSON con MR manuales por partido {"MORENA": 150, "PAN": 60, ...}
    mr_distritos_por_estado: Optional[str] = None,  # ← NUEVO: JSON con MR por estado y partido {"15": {"MORENA": 22, "PAN": 6, ...}, "9": {"MORENA": 14, ...}}
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
    - **pm_seats**: Escaños de primera minoría (opcional, sale de mr_seats)
    - **rp_seats**: Escaños de representación proporcional
    - **max_seats_per_party**: Máximo de escaños por partido
    - **sobrerrepresentacion**: Límite de sobrerrepresentación como porcentaje (ej: 10.8)
    - **aplicar_topes**: Si se aplican topes constitucionales (True) o no (False). Default: True
    - **reparto_mode**: Modo de reparto ("cuota" o "divisor")
    - **reparto_method**: Método específico:
      - Si reparto_mode="cuota": "hare", "droop", "imperiali"
      - Si reparto_mode="divisor": "dhondt", "sainte_lague", "webster"
    - **mr_distritos_manuales**: JSON con número de distritos MR ganados por partido. Formato: {"MORENA": 150, "PAN": 60, "PRI": 45, ...}. Si se proporciona, sobrescribe el cálculo automático de eficiencias geográficas.
    - **mr_distritos_por_estado**: JSON con distribución estado por estado de distritos MR por partido. Formato: {"15": {"MORENA": 22, "PAN": 6, "PRI": 8}, "9": {"MORENA": 14, "PAN": 5}}. Las claves son IDs de estados (1-32), los valores son diccionarios partido→distritos. Si se proporciona, se valida que la suma por estado coincida con la distribución Hare y se convierte automáticamente a mr_distritos_manuales (suma total).
    - **votos_custom**: JSON con % de votos por partido {"MORENA":45, "PAN":30, ...}
    - **partidos_fijos**: JSON con partidos fijos {"MORENA":2, "PAN":40}
    - **overrides_pool**: JSON con overrides del pool {"PAN":20, "MC":10}
    - **porcentajes_partidos**: JSON con % de votos por partido {"MORENA":42.5, "PAN":20.7, ...}
    
    NOTA: La redistritación geográfica está SIEMPRE ACTIVA. El sistema usa el método Hare 
    para distribuir distritos por estado según población y aplica eficiencias históricas 
    calculadas por partido. Esto garantiza que los MR se calculen correctamente en todos los casos.
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
                # Si logramos parsear JSON pero el Content-Type no es application/json,
                # marcar telemetría para identificar clientes que envían headers incorrectos.
                try:
                    content_type_tmp = request.headers.get('content-type', '') or ''
                except Exception:
                    content_type_tmp = ''
                if isinstance(body_obj, dict) and 'application/json' not in content_type_tmp.lower():
                    raw_body_parsed = True
                    print(f"[WARN] Parsed JSON from body despite Content-Type={content_type_tmp}; marking raw_body_parsed=True")
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
                                # No es JSON válido, mantener None y caer a heurísticas
                                body_obj = body_obj or None
                        else:
                            # Si no es JSON completo, intentar otros parseos tolerantes.
                            # 1) Intentar parseo como x-www-form-urlencoded (key1=val1&key2=val2)
                            try:
                                from urllib.parse import parse_qs, unquote_plus
                                parsed_qs = parse_qs(raw_text, keep_blank_values=True)
                                # Si parse_qs devuelve keys relevantes, convertir a dict simple
                                if parsed_qs and len(parsed_qs) > 0:
                                    # simplificar valores de listas a scalars cuando aplica
                                    simple = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in parsed_qs.items()}
                                    # Detectar si alguno de los valores es JSON (percent-encoded)
                                    decoded = {}
                                    potential_json_found = False
                                    for k, v in simple.items():
                                        if isinstance(v, str):
                                            v_str = v.strip()
                                            # Si parece JSON percent-encoded, intentar decodificar y cargar
                                            if (v_str.startswith('%7B') or v_str.startswith('%5B')) or ('%7B' in v_str or '%5B' in v_str):
                                                try:
                                                    candidate = unquote_plus(v_str)
                                                    parsed_inner = json.loads(candidate)
                                                    decoded[k] = parsed_inner
                                                    potential_json_found = True
                                                    continue
                                                except Exception:
                                                    pass
                                            # mantener raw string si no es JSON
                                            decoded[k] = v
                                        else:
                                            decoded[k] = v

                                    # Si detectamos keys directas como porcentajes (ej: PRD=90), considerarlo JSON-desnudo
                                    potential_parties_qs = {k: float(v) for k, v in decoded.items() if isinstance(k, str) and k.isupper() and isinstance(v, (str, float, int)) and str(v).replace('.', '', 1).isdigit()}
                                    if potential_parties_qs and not porcentajes_partidos:
                                        # mapear y marcar
                                        porcentajes_partidos = {k: float(v) for k, v in potential_parties_qs.items()}
                                        body_obj = porcentajes_partidos
                                        raw_body_parsed = True
                                        print(f"[WARN] Parsed URL-encoded form as porcentajes_partidos (Content-Type={request.headers.get('content-type')})")
                                    elif potential_json_found and not isinstance(body_obj, dict):
                                        # si encontramos JSON percent-encoded dentro de alguno de los campos, priorizamos
                                        # seleccionar el primer valor parseable
                                        for val in decoded.values():
                                            if isinstance(val, (dict, list)):
                                                body_obj = val
                                                raw_body_parsed = True
                                                print(f"[WARN] Extracted JSON from percent-encoded form field (Content-Type={request.headers.get('content-type')})")
                                                break
                                    else:
                                        # heurística clásica: buscar primer bloque JSON en el texto
                                        try:
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
                                # Si falla parse_qs o cualquier heuristic, intentar heurística clásica
                                try:
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
            total_distritos = body_obj.get('total_distritos', total_distritos)  # ← NUEVO
            max_seats_per_party = body_obj.get('max_seats_per_party', max_seats_per_party)
            sobrerrepresentacion = body_obj.get('sobrerrepresentacion', sobrerrepresentacion)
            reparto_mode = body_obj.get('reparto_mode', reparto_mode)
            reparto_method = body_obj.get('reparto_method', reparto_method)
            usar_coaliciones = body_obj.get('usar_coaliciones', usar_coaliciones)
            votos_custom = body_obj.get('votos_custom', votos_custom)
            partidos_fijos = body_obj.get('partidos_fijos', partidos_fijos)
            overrides_pool = body_obj.get('overrides_pool', overrides_pool)
            porcentajes_partidos = body_obj.get('porcentajes_partidos', porcentajes_partidos)
            mr_distritos_manuales = body_obj.get('mr_distritos_manuales', mr_distritos_manuales)  # ← FIX CRÍTICO
            mr_distritos_por_estado = body_obj.get('mr_distritos_por_estado', mr_distritos_por_estado)  # ← FIX CRÍTICO
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
            # Si no hay body útil pero el frontend pudo haber incluido porcentajes en la query string
            # (algunos clientes mal configurados envían PRD=90 como query param), intentar detectarlo.
            try:
                if not porcentajes_partidos and request is not None:
                    qp = {k: v for k, v in request.query_params.items()} if hasattr(request, 'query_params') else {}
                    potential_qp = {}
                    for k, v in qp.items():
                        try:
                            if isinstance(k, str) and k.isupper() and (isinstance(v, str) and v.replace('.', '', 1).isdigit()):
                                potential_qp[k] = float(v)
                        except Exception:
                            continue
                    if potential_qp:
                        porcentajes_partidos = potential_qp
                        raw_body_parsed = True
                        print(f"[WARN] Detected party percentages in query params, mapping to porcentajes_partidos: {list(potential_qp.keys())}")
            except Exception:
                pass
        print(f"[DEBUG] Iniciando /procesar/diputados con:")
        print(f"[DEBUG] - anio: {anio}")
        print(f"[DEBUG] - plan: {plan}")
        print(f"[DEBUG] - escanos_totales: {escanos_totales}")
        print(f"[DEBUG] - sistema: {sistema}")
        print(f"[DEBUG] - mr_seats: {mr_seats}")
        print(f"[DEBUG] - rp_seats: {rp_seats}")
        print(f"[DEBUG] - total_distritos: {total_distritos}")  # ← NUEVO
        print(f"[DEBUG] [MR MANUAL] mr_distritos_manuales (inicial): {mr_distritos_manuales[:100] if isinstance(mr_distritos_manuales, str) and mr_distritos_manuales else mr_distritos_manuales}")
        print(f"[DEBUG] [MR ESTADO] mr_distritos_por_estado (inicial): {mr_distritos_por_estado[:100] if isinstance(mr_distritos_por_estado, str) and mr_distritos_por_estado else mr_distritos_por_estado}")

        # FORZAR redistritación geográfica SIEMPRE activa
        # Esto garantiza que los MR se calculen correctamente en todos los casos
        redistritacion_geografica = True
        print(f"[DEBUG] - redistritacion_geografica: FORZADO a True (SIEMPRE activo)")

        # NUEVO: Procesar parámetros de redistribución de votos
        votos_redistribuidos = None
        # Si generamos un parquet temporal con votos redistribuidos, lo almacenamos aquí
        parquet_replacement = None
        # Si generamos un siglado temporal con ganadores redistribuidos, lo almacenamos aquí
        path_siglado = None
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
            print(f"[DEBUG] NOTA: redistritacion_geografica se activará automáticamente para recalcular MR")
            
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
                        # Si la función devolvió un DataFrame en formato 'largo' (PARTIDO, VOTOS_CALCULADOS)
                        # convertimos a formato ancho (cada partido como columna) porque
                        # el procesador `procesar_diputados_v2` espera columnas por partido.
                        try:
                            tmp_to_save = df_redistribuido
                            if 'PARTIDO' in df_redistribuido.columns and 'VOTOS_CALCULADOS' in df_redistribuido.columns:
                                id_cols = [c for c in ['ENTIDAD', 'DISTRITO', 'TOTAL_BOLETAS', 'CI'] if c in df_redistribuido.columns]
                                df_wide = df_redistribuido.pivot_table(index=id_cols, columns='PARTIDO', values='VOTOS_CALCULADOS', aggfunc='sum').reset_index()
                                # quitar nombre del eje de columnas que crea pivot_table
                                df_wide.columns.name = None
                                tmp_to_save = df_wide
                                print(f"[DEBUG] Converted df_redistribuido to wide-format for parquet (id_cols={id_cols})")

                        except Exception as e:
                            print(f"[WARN] No se pudo pivotar df_redistribuido a formato ancho: {e}; se guardará tal cual")

                        tmp_to_save.to_parquet(tmp_name, index=False)
                        print(f"[DEBUG] Parquet temporal con votos redistribuidos creado: {tmp_name}")

                        votos_redistribuidos = porcentajes_finales
                        
                        # GENERAR SIGLADO TEMPORAL con ganadores según votos redistribuidos
                        # Esto es crucial para que el motor sepa quién gana cada distrito
                        try:
                            from redistritacion.modulos.tabla_puente import generar_siglado_new
                            
                            print(f"[DEBUG] Generando siglado temporal con ganadores redistribuidos...")
                            siglado_temporal = generar_siglado_new(tmp_to_save, print_debug=False)
                            
                            # Guardar siglado temporal
                            siglado_tmp_name = f'outputs/tmp_siglado_{uuid.uuid4().hex}.csv'
                            siglado_temporal.to_csv(siglado_tmp_name, index=False, encoding='utf-8-sig')
                            print(f"[DEBUG] Siglado temporal creado: {siglado_tmp_name}")
                            print(f"[DEBUG] Ganadores por distrito actualizados según redistribución")
                            
                            # Actualizar path_siglado para usar el temporal
                            path_siglado = siglado_tmp_name
                            
                        except Exception as e_siglado:
                            print(f"[WARN] No se pudo generar siglado temporal: {e_siglado}")
                            # Continuar sin siglado temporal (usará el histórico)
                            import traceback
                            print(traceback.format_exc())
                        
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
            # VIGENTE: 500 total, 200 RP fijos, umbral 3%, tope 300, SIN PM
            max_seats = 500
            mr_seats_final = None  # NO forzar MR, usar cálculo real del siglado
            pm_seats_final = 0     # SIN primera minoría en vigente
            rp_seats_final = 200   # SÍ forzar 200 RP como en la realidad
            umbral_final = 0.03
            max_seats_per_party_final = 300
            quota_method_final = "hare"
            divisor_method_final = None
            sistema_final = "mixto"
            
        elif plan_normalizado == "plan_a":
            # PLAN A: 300 total (0 MR + 300 RP), umbral 3%, sin tope, SIN PM
            # Ignorar cualquier escanos_totales enviado desde el frontend: plan_a es RP puro 300
            if escanos_totales is not None:
                print(f"[DEBUG] plan_a recibido escanos_totales={escanos_totales} pero será IGNORADO (plan_a fuerza 300)")
            max_seats = 300
            mr_seats_final = 0
            pm_seats_final = 0  # SIN PM en plan A (es RP puro)
            rp_seats_final = 300
            umbral_final = 0.03
            max_seats_per_party_final = None
            quota_method_final = "hare"
            divisor_method_final = None
            sistema_final = "rp"  # Solo RP
            
        elif plan_normalizado == "plan_c":
            # PLAN C: 300 total (300 MR + 0 RP), sin umbral, sin tope, SIN PM
            # Ignorar cualquier escanos_totales enviado desde el frontend: plan_c es MR puro 300
            if escanos_totales is not None:
                print(f"[DEBUG] plan_c recibido escanos_totales={escanos_totales} pero será IGNORADO (plan_c fuerza 300)")
            max_seats = 300
            mr_seats_final = 300
            pm_seats_final = 0  # SIN PM en plan C (solo MR)
            rp_seats_final = 0
            umbral_final = 0.0
            max_seats_per_party_final = None
            quota_method_final = None
            divisor_method_final = None
            sistema_final = "mr"  # Solo MR
            
        elif plan_normalizado == "300_100_con_topes":
            # 300 MR + 100 RP = 400 total, CON TOPES (300 max por partido), CON REDISTRITACIÓN GEOGRÁFICA (por defecto)
            max_seats = 400
            mr_seats_final = 300
            pm_seats_final = 0
            rp_seats_final = 100
            umbral_final = 0.03
            max_seats_per_party_final = 300  # Tope constitucional
            quota_method_final = "hare"
            divisor_method_final = None
            sistema_final = "mixto"
            aplicar_topes = True
            print(f"[DEBUG] Escenario 300-100 CON TOPES activado (redistritación geográfica por defecto)")
            
        elif plan_normalizado == "300_100_sin_topes":
            # 300 MR + 100 RP = 400 total, SIN TOPES, CON REDISTRITACIÓN GEOGRÁFICA (por defecto)
            max_seats = 400
            mr_seats_final = 300
            pm_seats_final = 0
            rp_seats_final = 100
            umbral_final = 0.03
            max_seats_per_party_final = None  # Sin tope
            quota_method_final = "hare"
            divisor_method_final = None
            sistema_final = "mixto"
            aplicar_topes = False
            print(f"[DEBUG] Escenario 300-100 SIN TOPES activado (redistritación geográfica por defecto)")
            
        elif plan_normalizado == "200_200_sin_topes":
            # 200 MR + 200 RP = 400 total, SIN TOPES, CON REDISTRITACIÓN GEOGRÁFICA (por defecto)
            max_seats = 400
            mr_seats_final = 200
            pm_seats_final = 0
            rp_seats_final = 200
            umbral_final = 0.03
            max_seats_per_party_final = None  # Sin tope
            quota_method_final = "hare"
            divisor_method_final = None
            sistema_final = "mixto"
            aplicar_topes = False
            print(f"[DEBUG] Escenario 200-200 SIN TOPES activado (redistritación geográfica por defecto)")
            
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
                    # MR PURO: TODOS los escaños van a MR (puede incluir PM si se especifica)
                    mr_seats_final = max_seats
                    rp_seats_final = 0
                    print(f"[DEBUG] Sistema MR puro: {mr_seats_final} MR + {rp_seats_final} RP = {max_seats}")
                elif sistema_final == "rp":
                    # RP PURO: TODOS los escaños van a RP (sin PM)
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
                
                # CONFIGURAR PRIMERA MINORÍA (PM)
                # PM "sale" de MR, no suma al total
                pm_escanos = pm_seats if pm_seats is not None else 0
                if pm_escanos > 0:
                    # Validar que PM no sea mayor que MR
                    if mr_seats_final is not None and pm_escanos > mr_seats_final:
                        raise HTTPException(
                            status_code=400, 
                            detail=f"PM ({pm_escanos}) no puede ser mayor que MR ({mr_seats_final})"
                        )
                    pm_seats_final = pm_escanos
                    print(f"[DEBUG] PM activado: {pm_seats_final} escaños de primera minoría (salen de MR)")
                else:
                    pm_seats_final = 0
                    print(f"[DEBUG] PM desactivado (pm_seats=0 o None)")
                    
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
                    # Para mixto, respetar desagregados si se proporcionan; si no, dejar que defaults en wrappers manejen
                    mr_seats_final = mr_seats if mr_seats is not None else None
                    rp_seats_final = rp_seats if rp_seats is not None else None
                    if mr_seats_final is not None and rp_seats_final is not None:
                        max_seats = mr_seats_final + rp_seats_final
                
                # CONFIGURAR PM también en fallback
                pm_escanos = pm_seats if pm_seats is not None else 0
                if pm_escanos > 0:
                    if mr_seats_final is not None and pm_escanos > mr_seats_final:
                        raise HTTPException(
                            status_code=400, 
                            detail=f"PM ({pm_escanos}) no puede ser mayor que MR ({mr_seats_final})"
                        )
                    pm_seats_final = pm_escanos
                    print(f"[DEBUG] PM activado (fallback): {pm_seats_final} escaños")
                else:
                    pm_seats_final = 0
            
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
        print(f"[DEBUG] LÍMITES: aplicar_topes={aplicar_topes}, sobrerrepresentacion={sobrerrepresentacion}, max_seats_per_party={max_seats_per_party}")
        print(f"[DEBUG] TYPE: sobrerrepresentacion type={type(sobrerrepresentacion)}, value={repr(sobrerrepresentacion)}")

        # Construir paths (si hay un parquet temporal generado por redistribución, usarlo)
        path_parquet = parquet_replacement if parquet_replacement else f"data/computos_diputados_{anio}.parquet"
        
        # IMPORTANTE: Si ya se generó un siglado temporal (por redistribución de votos),
        # NO sobrescribirlo con el siglado histórico
        if 'path_siglado' not in locals() or path_siglado is None:
            path_siglado = f"data/siglado-diputados-{anio}.csv"
        
        print(f"[DEBUG] path_parquet: {path_parquet}")
        print(f"[DEBUG] path_siglado: {path_siglado}")
        
        # Verificar que existen los archivos
        if not os.path.exists(path_parquet):
            raise HTTPException(status_code=404, detail=f"Archivo no encontrado: {path_parquet}")
        if not os.path.exists(path_siglado):
            raise HTTPException(status_code=404, detail=f"Archivo siglado no encontrado: {path_siglado}")
            
        # Seed fijo para reproducibilidad cuando no se aplican topes
        # Esto garantiza que los resultados coincidan exactamente con los CSVs exportados
        seed_value = 42 if not aplicar_topes else None
        
        # DEBUG: Log completo de parámetros antes de llamar al motor
        print(f"[DEBUG] ========== PARÁMETROS PARA MOTOR ==========")
        print(f"[DEBUG] path_parquet: {path_parquet}")
        print(f"[DEBUG] anio: {anio}")
        print(f"[DEBUG] max_seats: {max_seats}")
        print(f"[DEBUG] sistema: {sistema_final}")
        print(f"[DEBUG] mr_seats: {mr_seats_final}")
        print(f"[DEBUG] rp_seats: {rp_seats_final}")
        print(f"[DEBUG] pm_seats: {pm_seats_final}")
        print(f"[DEBUG] umbral: {umbral_final}")
        print(f"[DEBUG] max_seats_per_party: {max_seats_per_party_final}")
        print(f"[DEBUG] sobrerrepresentacion: {sobrerrepresentacion}")
        print(f"[DEBUG] aplicar_topes: {aplicar_topes}")
        print(f"[DEBUG] quota_method: {quota_method_final}")
        print(f"[DEBUG] divisor_method: {divisor_method_final}")
        print(f"[DEBUG] usar_coaliciones: {usar_coaliciones}")
        print(f"[DEBUG] votos_redistribuidos: {votos_redistribuidos}")
        print(f"[DEBUG] seed: {seed_value}")
        print(f"[DEBUG] redistritacion_geografica: {redistritacion_geografica} (SIEMPRE True)")
        print(f"[DEBUG] =============================================")
        
        # 🔥 FIX CRÍTICO: Si hay mr_distritos_manuales y mr_seats_final es None, calcularlo
        # Esto es necesario porque plan="vigente" pone mr_seats_final=None por defecto
        if mr_distritos_manuales and (mr_seats_final is None or mr_seats_final == 0):
            try:
                mr_temp = json.loads(mr_distritos_manuales) if isinstance(mr_distritos_manuales, str) else mr_distritos_manuales
                total_mr_temp = sum(mr_temp.values())
                mr_seats_final = total_mr_temp
                print(f"[DEBUG] 🔧 mr_seats_final calculado desde mr_distritos_manuales: {mr_seats_final}")
            except Exception as e:
                print(f"[DEBUG] ⚠️  No se pudo calcular mr_seats_final desde mr_distritos_manuales: {e}")
        
        # APLICAR REDISTRITACIÓN GEOGRÁFICA (siempre activa)
        # La redistritación geográfica está SIEMPRE activada para garantizar
        # que los MR se calculen correctamente en todos los casos
        
        mr_ganados_geograficos = None
        if redistritacion_geografica and mr_seats_final and mr_seats_final > 0:
            
            # PRIORIDAD 1: Si hay distribución por estado, convertirla a MR manuales totales
            if mr_distritos_por_estado:
                print(f"[DEBUG] Procesando distribución por estado: {mr_distritos_por_estado}")
                try:
                    from redistritacion.modulos.reparto_distritos import repartir_distritos_hare
                    from redistritacion.modulos.distritacion import cargar_secciones_ine
                    
                    # Parsear JSON
                    distribucion_estados = json.loads(mr_distritos_por_estado)
                    
                    # Cargar distribución Hare real para validación
                    secciones = cargar_secciones_ine()
                    poblacion_por_estado = secciones.groupby('ENTIDAD')['POBTOT'].sum().to_dict()
                    
                    # Usar total_distritos si fue especificado, sino usar mr_seats_final
                    n_distritos_param = total_distritos if total_distritos is not None else mr_seats_final
                    print(f"[DEBUG] Distribución Hare con {n_distritos_param} distritos (total_distritos={total_distritos}, mr_seats={mr_seats_final})")
                    
                    asignacion_hare = repartir_distritos_hare(
                        poblacion_estados=poblacion_por_estado,
                        n_distritos=n_distritos_param,
                        piso_constitucional=2
                    )
                    
                    # Validar y sumar
                    totales_por_partido = {}
                    for estado_id_str, partidos_dict in distribucion_estados.items():
                        estado_id = int(estado_id_str)
                        
                        # Validar que el estado existe en la distribución Hare
                        if estado_id not in asignacion_hare:
                            raise HTTPException(
                                status_code=400,
                                detail=f"Estado {estado_id} no válido (rango: 1-32)"
                            )
                        
                        # Validar que la suma de partidos = distritos asignados al estado
                        distritos_esperados = asignacion_hare[estado_id]
                        distritos_asignados = sum(partidos_dict.values())
                        
                        if distritos_asignados != distritos_esperados:
                            raise HTTPException(
                                status_code=400,
                                detail=f"Estado {estado_id}: suma de distritos ({distritos_asignados}) != esperados ({distritos_esperados})"
                            )
                        
                        # Sumar a totales
                        for partido, distritos in partidos_dict.items():
                            totales_por_partido[partido] = totales_por_partido.get(partido, 0) + distritos
                    
                    # Convertir a mr_distritos_manuales (para que la lógica existente lo procese)
                    mr_distritos_manuales = json.dumps(totales_por_partido)
                    print(f"[DEBUG] Distribución por estado convertida a MR manuales: {mr_distritos_manuales}")
                    
                except json.JSONDecodeError:
                    raise HTTPException(status_code=400, detail="mr_distritos_por_estado debe ser un JSON válido")
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"Error procesando mr_distritos_por_estado: {str(e)}")
            
            # PRIORIDAD 2: Si hay MR manuales (o fueron convertidos desde mr_distritos_por_estado), usarlos
            if mr_distritos_manuales:
                print(f"[DEBUG] 🎯 mr_distritos_manuales RECIBIDO (tipo: {type(mr_distritos_manuales)}): {mr_distritos_manuales[:200] if isinstance(mr_distritos_manuales, str) else mr_distritos_manuales}")
                try:
                    mr_ganados_geograficos = json.loads(mr_distritos_manuales)
                    
                    # Validar que el total no exceda mr_seats_final
                    total_mr_manuales = sum(mr_ganados_geograficos.values())
                    if total_mr_manuales > mr_seats_final:
                        raise HTTPException(
                            status_code=400,
                            detail=f"La suma de MR manuales ({total_mr_manuales}) excede el total de escaños MR ({mr_seats_final})"
                        )
                    
                    print(f"[DEBUG] ✅ MR manuales validados: {mr_ganados_geograficos} (total={total_mr_manuales}/{mr_seats_final})")
                    
                    # ========================================================================
                    # AJUSTE DE VOTOS PARA MR MANUALES (REGLA DE TRES INVERSA)
                    # ========================================================================
                    # Cuando el usuario usa sliders para especificar MR manualmente, necesitamos
                    # ajustar los porcentajes de votos para que sean consistentes con esos MR.
                    # 
                    # Algoritmo:
                    # 1. Calcular MR BASE (sin sliders) usando datos históricos
                    # 2. Para cada partido: nuevo_% = (MR_manual / MR_base) * %_base
                    # 3. Renormalizar para que sumen 100%
                    # 4. Generar parquet ajustado con simular_escenario_electoral
                    # 5. Usar ese parquet para el resto del cálculo
                    #
                    print(f"[DEBUG] 🔄 Iniciando ajuste de votos para MR manuales...")
                    
                    try:
                        from engine.procesar_diputados_v2 import procesar_diputados_v2
                        import pandas as pd
                        import uuid
                        
                        # PASO 1: Calcular MR BASE (históricos) usando el motor SIN sliders
                        print(f"[DEBUG] 📊 Calculando MR base históricos desde {path_parquet}...")
                        
                        resultado_base = procesar_diputados_v2(
                            path_parquet=path_parquet,
                            anio=anio,
                            max_seats=max_seats,
                            sistema=sistema_final,
                            mr_seats=mr_seats_final,
                            rp_seats=rp_seats_final,
                            pm_seats=pm_seats_final,
                            umbral=umbral_final,
                            max_seats_per_party=None,  # Sin topes para obtener valores reales
                            sobrerrepresentacion=None,
                            aplicar_topes=False,  # Sin topes para cálculo base
                            quota_method=quota_method_final,
                            divisor_method=divisor_method_final,
                            usar_coaliciones=usar_coaliciones,
                            votos_redistribuidos=None,  # Sin redistribución
                            seed=seed_value,
                            print_debug=False,  # Sin debug para no contaminar logs
                            mr_ganados_geograficos=None  # ← SIN sliders (calcular base real)
                        )
                        
                        mr_base = resultado_base.get('mr', {})
                        votos_base = resultado_base.get('votos', {})
                        total_votos_base = sum(votos_base.values())
                        
                        print(f"[DEBUG] MR base calculados: {mr_base}")
                        print(f"[DEBUG] Votos base: {votos_base}")
                        
                        # PASO 2: Calcular porcentajes ajustados usando regla de tres
                        porcentajes_ajustados = {}
                        
                        for partido, mr_manual in mr_ganados_geograficos.items():
                            mr_historico = mr_base.get(partido, 0)
                            votos_historicos = votos_base.get(partido, 0)
                            pct_historico = (votos_historicos / total_votos_base * 100) if total_votos_base > 0 else 0
                            
                            if mr_historico > 0:
                                # Regla de tres: si con X% sacaba Y distritos, con Z distritos necesita...
                                # nuevo_% = (mr_manual / mr_historico) * pct_historico
                                pct_ajustado = (mr_manual / mr_historico) * pct_historico
                            else:
                                # Si el partido no tenía MR históricos pero ahora tiene manuales,
                                # asignar un porcentaje proporcional mínimo
                                pct_ajustado = (mr_manual / total_mr_manuales) * 3.0 if total_mr_manuales > 0 else 0
                            
                            porcentajes_ajustados[partido] = pct_ajustado
                            print(f"[DEBUG] {partido}: {pct_historico:.2f}% ({mr_historico} MR) → {pct_ajustado:.2f}% ({mr_manual} MR)")
                        
                        # PASO 3: Renormalizar para que sumen 100%
                        total_ajustado = sum(porcentajes_ajustados.values())
                        if total_ajustado > 0:
                            factor = 100.0 / total_ajustado
                            porcentajes_ajustados = {
                                partido: pct * factor 
                                for partido, pct in porcentajes_ajustados.items()
                            }
                            print(f"[DEBUG] Porcentajes renormalizados (total=100%): {porcentajes_ajustados}")
                        
                        # PASO 4: Generar parquet ajustado con simular_escenario_electoral
                        print(f"[DEBUG] 📝 Generando parquet con votos ajustados...")
                        
                        df_redistribuido, porcentajes_finales = simular_escenario_electoral(
                            path_parquet,
                            porcentajes_objetivo=porcentajes_ajustados,
                            partidos_fijos={},
                            overrides_pool={},
                            mantener_geografia=True
                        )
                        
                        # PASO 5: Guardar parquet temporal
                        tmp_name = f"outputs/tmp_mr_ajustado_{uuid.uuid4().hex}.parquet"
                        os.makedirs(os.path.dirname(tmp_name), exist_ok=True)
                        
                        # Convertir a formato ancho si es necesario
                        tmp_to_save = df_redistribuido
                        if 'PARTIDO' in df_redistribuido.columns and 'VOTOS_CALCULADOS' in df_redistribuido.columns:
                            id_cols = [c for c in ['ENTIDAD', 'DISTRITO', 'TOTAL_BOLETAS', 'CI'] if c in df_redistribuido.columns]
                            df_wide = df_redistribuido.pivot_table(
                                index=id_cols, 
                                columns='PARTIDO', 
                                values='VOTOS_CALCULADOS', 
                                aggfunc='sum'
                            ).reset_index()
                            df_wide.columns.name = None
                            tmp_to_save = df_wide
                            print(f"[DEBUG] Parquet convertido a formato ancho")
                        
                        tmp_to_save.to_parquet(tmp_name, index=False)
                        print(f"[DEBUG] ✅ Parquet ajustado guardado en: {tmp_name}")
                        
                        # PASO 6: Usar el parquet ajustado para el resto del procesamiento
                        path_parquet = tmp_name
                        print(f"[INFO] 🎯 MR manuales + votos ajustados: sistema recalculará RP con porcentajes consistentes")
                        
                    except Exception as e_ajuste:
                        print(f"[ERROR] ❌ Error ajustando votos para MR manuales: {e_ajuste}")
                        import traceback
                        traceback.print_exc()
                        # Continuar sin ajuste (usar datos originales)
                        print(f"[WARN] Continuando sin ajuste de votos (puede haber inconsistencias)")
                    
                    # ========================================================================
                    # FIN AJUSTE DE VOTOS
                    # ========================================================================
                
                except json.JSONDecodeError:
                    raise HTTPException(status_code=400, detail="mr_distritos_manuales debe ser un JSON válido")
            
            # Si NO hay MR manuales, calcularlos automáticamente
            else:
                print(f"[DEBUG] ❌ NO se recibieron MR manuales, calculando automáticamente...")
                try:
                    from redistritacion.modulos.reparto_distritos import repartir_distritos_hare
                    from redistritacion.modulos.distritacion import cargar_secciones_ine
                    from engine.calcular_eficiencia_real import calcular_eficiencia_partidos
                    
                    # PASO 1: Calcular eficiencias reales de los partidos en el año seleccionado
                    print(f"[DEBUG] Calculando eficiencias históricas para {anio}...")
                    eficiencias_por_partido = calcular_eficiencia_partidos(anio, usar_coaliciones=usar_coaliciones)
                    print(f"[DEBUG] Eficiencias calculadas: {eficiencias_por_partido}")
                    
                    # PASO 2: Cargar secciones para población
                    secciones = cargar_secciones_ine()
                    poblacion_por_estado = secciones.groupby('ENTIDAD')['POBTOT'].sum().to_dict()
                    
                    # Usar total_distritos si fue especificado, sino usar mr_seats_final
                    n_distritos_param = total_distritos if total_distritos is not None else mr_seats_final
                    print(f"[DEBUG] Redistritación geográfica con {n_distritos_param} distritos (total_distritos={total_distritos}, mr_seats={mr_seats_final})")
                    
                    # Repartir distritos usando método Hare
                    asignacion_distritos = repartir_distritos_hare(
                        poblacion_estados=poblacion_por_estado,
                        n_distritos=n_distritos_param,
                        piso_constitucional=2
                    )
                    
                    print(f"[DEBUG] Asignación de distritos por estado: {asignacion_distritos}")
                    
                    # Cargar votos reales
                    df_votos = pd.read_parquet(path_parquet)
                    
                    # Mapeo de nombres de estados
                    estado_nombres = {
                        1: 'AGUASCALIENTES', 2: 'BAJA CALIFORNIA', 3: 'BAJA CALIFORNIA SUR',
                        4: 'CAMPECHE', 5: 'CHIAPAS', 6: 'CHIHUAHUA', 7: 'COAHUILA',
                        8: 'COLIMA', 9: 'CIUDAD DE MEXICO', 10: 'DURANGO', 11: 'GUANAJUATO',
                        12: 'GUERRERO', 13: 'HIDALGO', 14: 'JALISCO', 15: 'MEXICO',
                        16: 'MICHOACAN', 17: 'MORELOS', 18: 'NAYARIT', 19: 'NUEVO LEON',
                        20: 'OAXACA', 21: 'PUEBLA', 22: 'QUERETARO', 23: 'QUINTANA ROO',
                        24: 'SAN LUIS POTOSI', 25: 'SINALOA', 26: 'SONORA', 27: 'TABASCO',
                        28: 'TAMAULIPAS', 29: 'TLAXCALA', 30: 'VERACRUZ', 31: 'YUCATAN',
                        32: 'ZACATECAS'
                    }
                    
                    # Normalizar nombres
                    df_votos['ENTIDAD_NOMBRE'] = df_votos['ENTIDAD'].str.strip().str.upper()
                    
                    # Calcular MR ganados por partido usando votos redistribuidos o reales
                    mr_ganados_por_partido = {}
                    
                    # Obtener lista de partidos
                    columnas_excluir = ['ENTIDAD', 'DISTRITO', 'TOTAL_BOLETAS', 'CI', 'ENTIDAD_NOMBRE']
                    partidos_disponibles = [col for col in df_votos.columns if col not in columnas_excluir]
                    
                    # Calcular % nacional de cada partido (usar votos_redistribuidos si existe)
                    if votos_redistribuidos:
                        print(f"[DEBUG] Usando votos redistribuidos para geografía: {votos_redistribuidos}")
                        porcentajes_partidos_dict = votos_redistribuidos
                    else:
                        # Calcular de los datos reales
                        porcentajes_partidos_dict = {}
                        for partido in partidos_disponibles:
                            total_partido = df_votos[partido].sum()
                            total_nacional = df_votos['TOTAL_BOLETAS'].sum()
                            porcentajes_partidos_dict[partido] = (total_partido / total_nacional * 100) if total_nacional > 0 else 0
                    
                    print(f"[DEBUG] Porcentajes para redistritación geográfica: {porcentajes_partidos_dict}")
                    
                    # Por cada partido, calcular MR ganados por estado
                    for partido in partidos_disponibles:
                        pct_nacional = porcentajes_partidos_dict.get(partido, 0)
                        
                        if pct_nacional == 0:
                            mr_ganados_por_partido[partido] = 0
                            continue
                        
                        # Obtener eficiencia real del partido (histórica)
                        eficiencia_partido = eficiencias_por_partido.get(partido, 1.0)
                        print(f"[DEBUG] {partido}: usando eficiencia {eficiencia_partido:.3f}")
                        
                        total_mr_ganados = 0
                        
                        for entidad_id, nombre in estado_nombres.items():
                            # Buscar datos del estado
                            df_estado = df_votos[df_votos['ENTIDAD_NOMBRE'] == nombre]
                            
                            if len(df_estado) == 0:
                                df_estado = df_votos[df_votos['ENTIDAD_NOMBRE'].str.contains(nombre.split()[0], na=False)]
                            
                            if len(df_estado) > 0:
                                votos_partido = df_estado[partido].sum()
                                votos_totales = df_estado['TOTAL_BOLETAS'].sum()
                                pct_estado_real = (votos_partido / votos_totales * 100) if votos_totales > 0 else 0
                                
                                # Escalar proporcionalmente si hay redistribución
                                if pct_nacional > 0:
                                    # Factor de cambio nacional aplicado al estado
                                    # Si a nivel nacional el partido pasó de X% real a pct_nacional, aplicar el mismo factor
                                    df_temp_nacional = pd.read_parquet(f"data/computos_diputados_{anio}.parquet")
                                    pct_real_nacional = (df_temp_nacional[partido].sum() / df_temp_nacional['TOTAL_BOLETAS'].sum() * 100) if df_temp_nacional['TOTAL_BOLETAS'].sum() > 0 else 0
                                    
                                    if pct_real_nacional > 0:
                                        factor_escala = pct_nacional / pct_real_nacional
                                        pct_estado = pct_estado_real * factor_escala
                                    else:
                                        pct_estado = pct_nacional
                                else:
                                    pct_estado = pct_estado_real
                            else:
                                pct_estado = pct_nacional
                            
                            distritos_totales = asignacion_distritos.get(entidad_id, 0)
                            
                            # Calcular distritos ganados con eficiencia REAL del partido
                            distritos_ganados = int(distritos_totales * (pct_estado / 100) * eficiencia_partido)
                            distritos_ganados = min(distritos_ganados, distritos_totales)
                            
                            total_mr_ganados += distritos_ganados
                        
                        mr_ganados_por_partido[partido] = total_mr_ganados
                        print(f"[DEBUG] {partido}: {total_mr_ganados} MR (de {mr_seats_final} total)")
                    
                    mr_ganados_geograficos = mr_ganados_por_partido
                    print(f"[DEBUG] MR ganados con redistritación geográfica: {mr_ganados_geograficos}")
                    print(f"[DEBUG] Total MR asignados: {sum(mr_ganados_geograficos.values())} de {mr_seats_final}")
                    
                except Exception as e:
                    print(f"[ERROR] Error en redistritación geográfica automática: {e}")
                    import traceback
                    print(traceback.format_exc())
                    # Continuar sin redistritación geográfica
                    mr_ganados_geograficos = None
        
        # Logging explicativo sobre cómo se determinarán los MR
        if mr_ganados_geograficos is not None:
            print(f"[INFO] ✅ MR se calcularán con REDISTRITACIÓN GEOGRÁFICA (eficiencias reales + nuevos porcentajes)")
            print(f"[INFO] Total MR pre-calculados: {sum(mr_ganados_geograficos.values())}")
        else:
            print(f"[INFO] ⚠️  MR se calcularán DISTRITO POR DISTRITO desde siglado histórico")
            print(f"[INFO] Esto es correcto SOLO si NO hay redistribución de votos")
            if votos_redistribuidos:
                print(f"[WARN] ⚠️⚠️⚠️  HAY VOTOS REDISTRIBUIDOS pero mr_ganados_geograficos es None!")
                print(f"[WARN] Los resultados pueden NO reflejar los cambios de porcentajes solicitados")
        
        resultado = procesar_diputados_v2(
            path_parquet=path_parquet,
            anio=anio,
            path_siglado=path_siglado,
            max_seats=max_seats,
            sistema=sistema_final,
            mr_seats=mr_seats_final,
            rp_seats=rp_seats_final,
            pm_seats=pm_seats_final,  # Primera minoría
            umbral=umbral_final,
            max_seats_per_party=max_seats_per_party_final,
            sobrerrepresentacion=sobrerrepresentacion,
            aplicar_topes=aplicar_topes,  # ← NUEVO: Pasar el parámetro del frontend
            quota_method=quota_method_final,
            divisor_method=divisor_method_final,
            usar_coaliciones=usar_coaliciones,
            votos_redistribuidos=votos_redistribuidos,
            mr_ganados_geograficos=mr_ganados_geograficos,  # ← NUEVO: MR calculados con redistritación geográfica
            seed=seed_value,  # ← NUEVO: Seed fijo para reproducibilidad
            print_debug=True
        )
        
        # Debug: Verificar qué devuelve procesar_diputados_v2
        print(f"[DEBUG] Resultado de procesar_diputados_v2: {resultado}")
        if 'tot' in resultado:
            print(f"[DEBUG] Escaños totales por partido: {resultado['tot']}")
            print(f"[DEBUG] Suma total escaños: {sum(resultado['tot'].values())}")
        
        # Transformar al formato esperado por el frontend con colores
        resultado_formateado = transformar_resultado_a_formato_frontend(resultado, plan)

        # ========================================================================
        # DETECCIÓN AUTOMÁTICA DE MAYORÍAS (SIMPLE Y CALIFICADA)
        # ========================================================================
        try:
            # Calcular total de escaños
            total_escanos = sum(resultado.get('tot', {}).values())
            mayoria_simple_umbral = total_escanos / 2  # 50%
            mayoria_calificada_umbral = (total_escanos * 2) / 3  # 66.67%
            
            # Buscar mayorías por partido individual
            mayorias_info = {
                "mayoria_simple": {
                    "partido": None,
                    "escanos": 0,
                    "coalicion": False
                },
                "mayoria_calificada": {
                    "partido": None,
                    "escanos": 0,
                    "coalicion": False
                }
            }
            
            # Revisar partidos individuales
            partidos_ordenados = sorted(
                resultado.get('tot', {}).items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            for partido, escanos in partidos_ordenados:
                # Mayoría calificada individual
                if escanos >= mayoria_calificada_umbral and mayorias_info["mayoria_calificada"]["partido"] is None:
                    mayorias_info["mayoria_calificada"]["partido"] = partido
                    mayorias_info["mayoria_calificada"]["escanos"] = escanos
                    mayorias_info["mayoria_calificada"]["coalicion"] = False
                
                # Mayoría simple individual
                if escanos > mayoria_simple_umbral and mayorias_info["mayoria_simple"]["partido"] is None:
                    mayorias_info["mayoria_simple"]["partido"] = partido
                    mayorias_info["mayoria_simple"]["escanos"] = escanos
                    mayorias_info["mayoria_simple"]["coalicion"] = False
            
            # Buscar mayorías de coalición (solo si no hay mayoría calificada individual)
            # Revisar coaliciones típicas
            coaliciones_posibles = [
                # Coalición 4T (MORENA + PT + PVEM)
                {
                    "nombre": "MORENA+PT+PVEM",
                    "partidos": ["MORENA", "PT", "PVEM"]
                },
                # Coalición Va por México (PAN + PRI + PRD)
                {
                    "nombre": "PAN+PRI+PRD",
                    "partidos": ["PAN", "PRI", "PRD"]
                },
                # MORENA + aliados
                {
                    "nombre": "MORENA+PT",
                    "partidos": ["MORENA", "PT"]
                }
            ]
            
            for coalicion in coaliciones_posibles:
                escanos_coalicion = sum(
                    resultado.get('tot', {}).get(p, 0) 
                    for p in coalicion["partidos"]
                )
                
                # Mayoría calificada de coalición
                if (escanos_coalicion >= mayoria_calificada_umbral and 
                    mayorias_info["mayoria_calificada"]["partido"] is None):
                    mayorias_info["mayoria_calificada"]["partido"] = coalicion["nombre"]
                    mayorias_info["mayoria_calificada"]["escanos"] = escanos_coalicion
                    mayorias_info["mayoria_calificada"]["coalicion"] = True
                
                # Mayoría simple de coalición (solo si no hay simple individual)
                if (escanos_coalicion > mayoria_simple_umbral and 
                    mayorias_info["mayoria_simple"]["partido"] is None):
                    mayorias_info["mayoria_simple"]["partido"] = coalicion["nombre"]
                    mayorias_info["mayoria_simple"]["escanos"] = escanos_coalicion
                    mayorias_info["mayoria_simple"]["coalicion"] = True
            
            # Agregar información al resultado
            resultado_formateado["mayorias"] = {
                "total_escanos": total_escanos,
                "mayoria_simple": {
                    "umbral": int(mayoria_simple_umbral) + 1,  # +1 porque necesita más del 50%
                    "alcanzada": mayorias_info["mayoria_simple"]["partido"] is not None,
                    "partido": mayorias_info["mayoria_simple"]["partido"],
                    "escanos": mayorias_info["mayoria_simple"]["escanos"],
                    "es_coalicion": mayorias_info["mayoria_simple"]["coalicion"]
                },
                "mayoria_calificada": {
                    "umbral": int(mayoria_calificada_umbral) + 1,  # Redondear hacia arriba
                    "alcanzada": mayorias_info["mayoria_calificada"]["partido"] is not None,
                    "partido": mayorias_info["mayoria_calificada"]["partido"],
                    "escanos": mayorias_info["mayoria_calificada"]["escanos"],
                    "es_coalicion": mayorias_info["mayoria_calificada"]["coalicion"]
                }
            }
            
        except Exception as e_mayorias:
            print(f"[WARN] No se pudo calcular mayorías: {e_mayorias}")
            # Si falla, agregar info básica
            resultado_formateado["mayorias"] = {
                "error": str(e_mayorias),
                "mayoria_simple": {"alcanzada": False},
                "mayoria_calificada": {"alcanzada": False}
            }
        # ========================================================================

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
        # Mejor manejo de excepciones: anexar siempre un resumen del error a meta.trace
        from fastapi import HTTPException as _HTTPException
        import traceback
        traceback_str = traceback.format_exc()

        # Si ya es un HTTPException, intentar anexar resumen de la excepción al resultado formateado
        if isinstance(e, _HTTPException):
            # Construir trace si es posible
            try:
                msg = e.detail if getattr(e, 'detail', None) else '<empty>'
                trace_block = {}
                tb_lines = [ln for ln in traceback_str.splitlines() if ln.strip()][:10]
                trace_block['error'] = {
                    'type': 'HTTPException',
                    'message': str(msg),
                    'status_code': getattr(e, 'status_code', None),
                    'trace_sample': tb_lines[-5:]
                }
                # Si tenemos resultado_formateado, inyectarlo allí; si no, construir un payload mínimo
                if 'resultado_formateado' in locals() and isinstance(resultado_formateado, dict):
                    resultado_formateado.setdefault('meta', {}).setdefault('trace', {}).update(trace_block)
                    content_payload = resultado_formateado
                else:
                    content_payload = {'detail': str(msg), 'meta': {'trace': trace_block}}
            except Exception as _inner:
                print(f"[WARN] No se pudo anexar HTTPException al trace: {_inner}")
                content_payload = {'detail': str(getattr(e, 'detail', repr(e)))}

            print(f"[ERROR] HTTPException interceptada desde /procesar/diputados: {getattr(e, 'detail', repr(e))}")
            # Devolver JSONResponse con el mismo status code y payload enriquecido
            return JSONResponse(status_code=getattr(e, 'status_code', 500), content=content_payload)

        # Para cualquier otra excepción, registrar y anexar resumen en meta.trace
        error_msg = str(e)
        error_type = type(e).__name__
        print(f"[ERROR] Error en /procesar/diputados: {error_msg}")
        print(f"[ERROR] Tipo de error: {error_type}")
        print(f"[ERROR] Traceback completo: {traceback_str}")

        # Intentar enriquecer meta.trace con información resumida del error para diagnóstico
        try:
            if 'resultado_formateado' in locals() and isinstance(resultado_formateado, dict):
                tr = resultado_formateado.setdefault('meta', {}).setdefault('trace', {})
                # Limitar traceback a 10 líneas y tomar las últimas 5 para contexto
                tb_lines = [ln for ln in traceback_str.splitlines() if ln.strip()][:10]
                tr['error'] = {
                    'type': error_type,
                    'message': (error_msg or '<empty>').strip(),
                    'trace_sample': tb_lines[-5:]
                }
        except Exception as _inner:
            print(f"[WARN] No se pudo anexar error al trace: {_inner}")

        # Crear mensaje de error más informativo para el cliente
        safe_msg = error_msg.strip() or '<no message>'
        detail_msg = f"Error procesando diputados: {error_type} - {safe_msg}"

        # Para facilitar debugging en frontend/ops devolvemos un mensaje consistente
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
    Frontend puede enviar: A, B, C, vigente, plan_a, plan_c, personalizado,
    300_100_con_topes, 300_100_sin_topes, 200_200_sin_topes
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
        'personalizado': 'personalizado',
        # Nuevos escenarios con redistritación geográfica
        '300_100_con_topes': '300_100_con_topes',
        '300_100_sin_topes': '300_100_sin_topes',
        '200_200_sin_topes': '200_200_sin_topes',
        '240_160_sin_topes': '240_160_sin_topes',
        '240_160_con_topes': '240_160_con_topes',
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
