from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import sys
import os
from typing import Dict, Any, Optional

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

def transformar_resultado_a_formato_frontend(resultado_dict: Dict, plan: str) -> Dict:
    """
    Transforma el resultado de las funciones de procesamiento al formato esperado por el frontend
    """
    try:
        if not resultado_dict or 'tot' not in resultado_dict:
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
            if escanos_dict.get(partido, 0) > 0:  # Solo partidos con escaños
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
        
        # Calcular KPIs
        votos_list = [r["votos"] for r in resultados]
        escanos_list = [r["total"] for r in resultados]
        
        kpis = {
            "total_votos": total_votos,
            "total_escanos": total_escanos,
            "gallagher": safe_gallagher(votos_list, escanos_list),
            "mae_votos_vs_escanos": safe_mae(votos_list, escanos_list),
            "partidos_con_escanos": len([r for r in resultados if r["total"] > 0])
        }
        
        return {
            "plan": plan,
            "resultados": resultados,
            "kpis": kpis,
            "seat_chart": seat_chart
        }
        
    except Exception as e:
        print(f"[ERROR] Error transformando resultado: {e}")
        return {"plan": plan, "resultados": [], "kpis": {"error": str(e)}, "seat_chart": []}

app = FastAPI(
    title="Backend Electoral API",
    description="API para procesamiento de datos electorales con soporte de coaliciones",
    version="2.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    return {"status": "healthy", "timestamp": pd.Timestamp.now().isoformat()}

@app.post("/procesar/senado")
async def procesar_senado(
    anio: int,
    plan: str = "vigente",
    escanos_totales: Optional[int] = None,
    sistema: Optional[str] = None,
    umbral: Optional[float] = None,
    mr_seats: Optional[int] = None,
    rp_seats: Optional[int] = None
):
    """
    Procesa los datos del senado para un año específico con soporte de coaliciones
    
    - **anio**: Año electoral (2018, 2024)
    - **plan**: Plan electoral ("vigente", "plan_a", "plan_c", "personalizado")
    - **escanos_totales**: Número total de escaños (opcional, se calcula automáticamente)
    - **sistema**: Sistema electoral para plan personalizado ("rp", "mixto", "mr")
    - **umbral**: Umbral electoral para plan personalizado (0.0-1.0)
    - **mr_seats**: Escaños de mayoría relativa para plan personalizado
    - **rp_seats**: Escaños de representación proporcional para plan personalizado
    """
    try:
        if anio not in [2018, 2024]:
            raise HTTPException(status_code=400, detail="Año no soportado. Use 2018 o 2024")
        
        # Configurar parámetros según el flujo de test_flujo.py
        if plan == "vigente":
            # Sistema vigente según test_flujo.py
            sistema_final = "mixto"
            mr_seats_final = 96
            rp_seats_final = 32
            umbral_final = 0.03
            max_seats = mr_seats_final + rp_seats_final
        elif plan == "plan_a":
            # Plan A: solo RP según test_flujo.py
            sistema_final = "rp"
            mr_seats_final = 0
            rp_seats_final = 96
            umbral_final = 0.03
            max_seats = rp_seats_final
        elif plan == "plan_c":
            # Plan C: solo MR según test_flujo.py
            sistema_final = "mr"
            mr_seats_final = 64
            rp_seats_final = 0
            umbral_final = 0.0
            max_seats = mr_seats_final
        elif plan == "personalizado":
            # Plan personalizado con parámetros del usuario
            if not sistema:
                raise HTTPException(status_code=400, detail="Sistema requerido para plan personalizado")
            sistema_final = sistema
            mr_seats_final = mr_seats or 96
            rp_seats_final = rp_seats or 32
            umbral_final = umbral if umbral is not None else 0.03
            max_seats = mr_seats_final + rp_seats_final
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
            umbral=umbral_final
        )
        
        # Transformar al formato esperado por el frontend con colores
        resultado_formateado = transformar_resultado_a_formato_frontend(resultado, plan)
        
        return resultado_formateado
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando senado: {str(e)}")

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
    quota_method: str = "hare",
    divisor_method: str = "dhondt"
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
    - **quota_method**: Método de cuota ("hare", "droop", "imperiali")
    - **divisor_method**: Método divisor ("dhondt", "sainte_lague", "webster")
    """
    try:
        if anio not in [2018, 2021, 2024]:
            raise HTTPException(status_code=400, detail="Año no soportado. Use 2018, 2021 o 2024")
        
        # Configurar parámetros según el flujo de test_flujo.py
        if plan == "vigente":
            # Sistema vigente según test_flujo.py
            sistema_final = "mixto"
            max_seats = 500
            mr_seats_final = 300
            rp_seats_final = 200
            umbral_final = 0.03
            max_seats_per_party_final = 300
            quota_method_final = quota_method
            divisor_method_final = divisor_method
        elif plan == "plan_a":
            # Plan A: solo RP según test_flujo.py
            sistema_final = "rp"
            max_seats = 300
            mr_seats_final = 0
            rp_seats_final = 300
            umbral_final = 0.03
            max_seats_per_party_final = None
            quota_method_final = quota_method
            divisor_method_final = None
        elif plan == "plan_c":
            # Plan C: solo MR según test_flujo.py
            sistema_final = "mr"
            max_seats = 300
            mr_seats_final = 300
            rp_seats_final = 0
            umbral_final = 0.0
            max_seats_per_party_final = None
            quota_method_final = quota_method
            divisor_method_final = None
        elif plan == "personalizado":
            # Plan personalizado con parámetros del usuario
            if not sistema:
                raise HTTPException(status_code=400, detail="Sistema requerido para plan personalizado")
            sistema_final = sistema
            max_seats = escanos_totales or 500
            mr_seats_final = mr_seats or 300
            rp_seats_final = rp_seats or 200
            umbral_final = umbral if umbral is not None else 0.03
            max_seats_per_party_final = max_seats_per_party
            quota_method_final = quota_method
            divisor_method_final = divisor_method if sistema_final == "mixto" else None
        else:
            raise HTTPException(status_code=400, detail="Plan no válido. Use 'vigente', 'plan_a', 'plan_c' o 'personalizado'")
            
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
            quota_method=quota_method_final,
            divisor_method=divisor_method_final
        )
        
        # Transformar al formato esperado por el frontend con colores
        resultado_formateado = transformar_resultado_a_formato_frontend(resultado, plan)
        
        return resultado_formateado
        
    except Exception as e:
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
            resultado = await procesar_senado(anio=anio, plan=plan)
        else:
            resultado = await procesar_diputados(anio=anio, plan=plan)
        
        # Calcular KPIs usando los resultados actualizados
        kpis = calcular_kpis_electorales(resultado, anio, camara)
        
        return kpis
        
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
            resultado = await procesar_senado(anio=anio, plan=plan)
        else:
            resultado = await procesar_diputados(anio=anio, plan=plan)
        
        # Formatear para seat-chart usando los resultados actualizados
        seat_chart_data = formato_seat_chart(resultado)
        
        return seat_chart_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo seat-chart: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
