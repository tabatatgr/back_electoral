from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import sys
import os
from typing import Dict, Any, Optional
from datetime import datetime

# Agregar el directorio actual al path para importaciones
sys.path.append('.')

from engine.procesar_senadores_v2 import procesar_senadores_v2  
from engine.procesar_diputados_v2 import procesar_diputados_v2
from outputs.kpi_utils import calcular_kpis_electorales, formato_seat_chart

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
        
        return {
            "plan": plan,
            "resultados": resultados,
            "kpis": kpis,
            "seat_chart": seat_chart,
            "timestamp": datetime.now().isoformat(),
            "cache_buster": datetime.now().timestamp()
        }
        
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
        elif plan_normalizado == "plan_a":
            # Plan A: solo RP = 96 total
            sistema_final = "rp"
            mr_seats_final = 0
            rp_seats_final = 96
            umbral_final = 0.03
            max_seats = 96
            pm_escanos = 0  # Sin PM en plan A
        elif plan_normalizado == "plan_c":
            # Plan C: solo MR+PM = 64 total (32 MR + 32 PM, sin RP)
            sistema_final = "mr"
            mr_seats_final = 64  # 64 escaños como MR+PM
            rp_seats_final = 0
            umbral_final = 0.0
            max_seats = 64
            pm_escanos = 32  # PM para plan C
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
            usar_coaliciones=usar_coaliciones  # ⬅️ NUEVO: toggle coaliciones
        )
        
        # Transformar al formato esperado por el frontend con colores
        resultado_formateado = transformar_resultado_a_formato_frontend(resultado, plan)
        
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
    plan: str = "vigente",
    escanos_totales: Optional[int] = None,
    sistema: Optional[str] = None,
    umbral: Optional[float] = None,
    mr_seats: Optional[int] = None,
    rp_seats: Optional[int] = None,
    max_seats_per_party: Optional[int] = None,
    sobrerrepresentacion: Optional[float] = None,
    quota_method: str = "hare",
    divisor_method: str = "dhondt",
    usar_coaliciones: bool = True
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
    - **quota_method**: Método de cuota ("hare", "droop", "imperiali")
    - **divisor_method**: Método divisor ("dhondt", "sainte_lague", "webster")
    """
    try:
        print(f"[DEBUG] Iniciando /procesar/diputados con:")
        print(f"[DEBUG] - anio: {anio}")
        print(f"[DEBUG] - plan: {plan}")
        print(f"[DEBUG] - escanos_totales: {escanos_totales}")
        print(f"[DEBUG] - sistema: {sistema}")
        print(f"[DEBUG] - mr_seats: {mr_seats}")
        print(f"[DEBUG] - rp_seats: {rp_seats}")
        
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
                if sistema_final == "mr":
                    # Para MR puro, usar mr_seats como magnitud total
                    mr_seats_final = mr_seats if mr_seats is not None else 300
                    rp_seats_final = 0
                    max_seats = mr_seats_final
                elif sistema_final == "rp":
                    # Para RP puro, usar rp_seats como magnitud total
                    mr_seats_final = 0
                    rp_seats_final = rp_seats if rp_seats is not None else 300
                    max_seats = rp_seats_final
                else:  # mixto
                    mr_seats_final = mr_seats if mr_seats is not None else 300
                    rp_seats_final = rp_seats if rp_seats is not None else 200
                    max_seats = mr_seats_final + rp_seats_final
            
            umbral_final = umbral if umbral is not None else 0.03
            max_seats_per_party_final = max_seats_per_party
            print(f"[DEBUG] max_seats_per_party recibido: {max_seats_per_party}")
            print(f"[DEBUG] max_seats_per_party_final: {max_seats_per_party_final}")
            quota_method_final = quota_method
            divisor_method_final = divisor_method
        else:
            raise HTTPException(status_code=400, detail="Plan no válido. Use 'vigente', 'plan_a', 'plan_c' o 'personalizado'")
        
        print(f"[DEBUG] Plan {plan_normalizado}: max_seats={max_seats}, mr={mr_seats_final}, rp={rp_seats_final}, umbral={umbral_final}")
            
        # Construir paths
        path_parquet = f"data/computos_diputados_{anio}.parquet"
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
            print_debug=True
        )
        
        # Debug: Verificar qué devuelve procesar_diputados_v2
        print(f"[DEBUG] Resultado de procesar_diputados_v2: {resultado}")
        if 'tot' in resultado:
            print(f"[DEBUG] Escaños totales por partido: {resultado['tot']}")
            print(f"[DEBUG] Suma total escaños: {sum(resultado['tot'].values())}")
        
        # Transformar al formato esperado por el frontend con colores
        resultado_formateado = transformar_resultado_a_formato_frontend(resultado, plan)
        
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
        print(f"[ERROR] Error en /procesar/diputados: {str(e)}")
        print(f"[ERROR] Tipo de error: {type(e).__name__}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error procesando diputados: {str(e)}")

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
async def obtener_kpis(camara: str, anio: int, plan: str = "vigente"):
    """
    Obtiene los KPIs electorales para una cámara y año específicos
    Usa los nuevos endpoints de procesamiento para obtener datos actualizados
    """
    try:
        if camara not in ["senado", "diputados"]:
            raise HTTPException(status_code=400, detail="Cámara debe ser 'senado' o 'diputados'")
        
        # Llamar al endpoint de procesamiento correspondiente
        if camara == "senado":
            response = await procesar_senado(anio=anio, plan=plan)
        else:
            response = await procesar_diputados(anio=anio, plan=plan)
        
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
async def obtener_seat_chart(camara: str, anio: int, plan: str = "vigente"):
    """
    Obtiene los datos formateados para el seat-chart
    Usa los nuevos endpoints de procesamiento para obtener datos actualizados
    """
    try:
        if camara not in ["senado", "diputados"]:
            raise HTTPException(status_code=400, detail="Cámara debe ser 'senado' o 'diputados'")
        
        # Llamar al endpoint de procesamiento correspondiente
        if camara == "senado":
            response = await procesar_senado(anio=anio, plan=plan)
        else:
            response = await procesar_diputados(anio=anio, plan=plan)
        
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
