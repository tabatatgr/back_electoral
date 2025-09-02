from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import sys
import os
from typing import Dict, Any, Optional

# Agregar el directorio actual al path para importaciones
sys.path.append('.')

from engine.procesar_senadores_v2 import procesar_senadores_v2  
from engine.procesar_diputados_v2 import procesar_diputados_v2
from outputs.kpi_utils import calcular_kpis_electorales, formato_seat_chart

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
    plan: str = "A",
    escanos_totales: Optional[int] = None
):
    """
    Procesa los datos del senado para un año específico con soporte de coaliciones
    
    - **anio**: Año electoral (2018, 2024)
    - **plan**: Plan electoral ("A", "B", "C")
    - **escanos_totales**: Número total de escaños (opcional, se calcula automáticamente)
    """
    try:
        if anio not in [2018, 2024]:
            raise HTTPException(status_code=400, detail="Año no soportado. Use 2018 o 2024")
        
        if plan not in ["A", "B", "C"]:
            raise HTTPException(status_code=400, detail="Plan no válido. Use A, B o C")
        
        # Configurar sistema y escaños según plan
        if plan == "A":
            sistema = "rp"
            escanos_totales = escanos_totales or 96
        elif plan == "B":
            sistema = "mixto"
            escanos_totales = escanos_totales or 128
        elif plan == "C":
            sistema = "mr"
            escanos_totales = escanos_totales or 64
            
        # Construir paths
        path_parquet = f"data/computos_senado_{anio}.parquet"
        path_siglado = f"data/siglado-senado-{anio}.csv"
        
        # Verificar que existen los archivos
        if not os.path.exists(path_parquet):
            raise HTTPException(status_code=404, detail=f"Archivo no encontrado: {path_parquet}")
            
        resultado = procesar_senadores_v2(
            path_parquet=path_parquet,
            anio=anio,
            path_siglado=path_siglado,
            max_seats=escanos_totales,
            sistema=sistema
        )
        
        return {
            "status": "success",
            "anio": anio,
            "plan": plan,
            "sistema": sistema,
            "escanos_totales": escanos_totales,
            "partidos_procesados": len(resultado.get("resultados", [])),
            "resultados": resultado.get("resultados", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando senado: {str(e)}")

@app.post("/procesar/diputados")
async def procesar_diputados(
    anio: int,
    plan: str = "A"
):
    """
    Procesa los datos de diputados para un año específico con soporte de coaliciones
    
    - **anio**: Año electoral (2018, 2021, 2024)
    - **plan**: Plan electoral ("A", "B", "C")
    """
    try:
        if anio not in [2018, 2021, 2024]:
            raise HTTPException(status_code=400, detail="Año no soportado. Use 2018, 2021 o 2024")
            
        if plan not in ["A", "B", "C"]:
            raise HTTPException(status_code=400, detail="Plan no válido. Use A, B o C")
        
        # Configurar sistema según plan
        if plan == "A":
            sistema = "rp"
            max_seats = 300
        elif plan == "B":
            sistema = "mixto"
            max_seats = 300
        elif plan == "C":
            sistema = "mr"
            max_seats = 200
            
        # Construir paths
        path_parquet = f"data/computos_diputados_{anio}.parquet"
        path_siglado = f"data/siglado-diputados-{anio}.csv"
        
        # Verificar que existen los archivos
        if not os.path.exists(path_parquet):
            raise HTTPException(status_code=404, detail=f"Archivo no encontrado: {path_parquet}")
            
        resultado = procesar_diputados_v2(
            path_parquet=path_parquet,
            anio=anio,
            path_siglado=path_siglado,
            max_seats=max_seats,
            sistema=sistema
        )
        
        return {
            "status": "success",
            "anio": anio,
            "plan": plan,
            "sistema": sistema,
            "max_seats": max_seats,
            "partidos_procesados": len(resultado.get("resultados", [])),
            "resultados": resultado.get("resultados", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando diputados: {str(e)}")

@app.get("/años-disponibles")
async def años_disponibles():
    """Retorna los años disponibles para procesamiento"""
    return {
        "senado": [2018, 2024],
        "diputados": [2018, 2021, 2024],
        "planes": ["A", "B", "C"]
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
async def obtener_kpis(camara: str, anio: int, plan: str = "A"):
    """
    Obtiene los KPIs electorales para una cámara y año específicos
    """
    try:
        if camara not in ["senado", "diputados"]:
            raise HTTPException(status_code=400, detail="Cámara debe ser 'senado' o 'diputados'")
        
        # Procesar datos según la cámara
        if camara == "senado":
            if anio not in [2018, 2024]:
                raise HTTPException(status_code=400, detail="Año no soportado para senado. Use 2018 o 2024")
            
            # Configurar sistema según plan
            if plan == "A":
                sistema = "rp"
                escanos_totales = 96
            elif plan == "B":
                sistema = "mixto"
                escanos_totales = 128
            elif plan == "C":
                sistema = "mr"
                escanos_totales = 64
            else:
                raise HTTPException(status_code=400, detail="Plan no válido. Use A, B o C")
            
            path_parquet = f"data/computos_senado_{anio}.parquet"
            path_siglado = f"data/siglado-senado-{anio}.csv"
            
            if not os.path.exists(path_parquet):
                raise HTTPException(status_code=404, detail=f"Archivo no encontrado: {path_parquet}")
                
            resultado = procesar_senadores_v2(
                path_parquet=path_parquet,
                anio=anio,
                path_siglado=path_siglado,
                max_seats=escanos_totales,
                sistema=sistema
            )
        
        else:  # diputados
            if anio not in [2018, 2021, 2024]:
                raise HTTPException(status_code=400, detail="Año no soportado para diputados. Use 2018, 2021 o 2024")
            
            if plan == "A":
                sistema = "rp"
                max_seats = 300
            elif plan == "B":
                sistema = "mixto"
                max_seats = 300
            elif plan == "C":
                sistema = "mr"
                max_seats = 200
            else:
                raise HTTPException(status_code=400, detail="Plan no válido. Use A, B o C")
            
            path_parquet = f"data/computos_diputados_{anio}.parquet"
            path_siglado = f"data/siglado-diputados-{anio}.csv"
            
            if not os.path.exists(path_parquet):
                raise HTTPException(status_code=404, detail=f"Archivo no encontrado: {path_parquet}")
                
            resultado = procesar_diputados_v2(
                path_parquet=path_parquet,
                anio=anio,
                path_siglado=path_siglado,
                max_seats=max_seats,
                sistema=sistema
            )
        
        # Estructurar resultado para KPIs
        resultado_formateado = {
            "status": "success",
            "anio": anio,
            "plan": plan,
            "sistema": sistema if camara == "senado" else sistema,
            "resultados": resultado.get("resultados", [])
        }
        
        # Calcular KPIs
        kpis = calcular_kpis_electorales(resultado_formateado, anio, camara)
        
        return kpis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo KPIs: {str(e)}")

@app.get("/seat-chart/{camara}/{anio}")
async def obtener_seat_chart(camara: str, anio: int, plan: str = "A"):
    """
    Obtiene los datos formateados para el seat-chart
    """
    try:
        if camara not in ["senado", "diputados"]:
            raise HTTPException(status_code=400, detail="Cámara debe ser 'senado' o 'diputados'")
        
        # Procesar datos según la cámara (reutilizar lógica del endpoint de KPIs)
        if camara == "senado":
            if anio not in [2018, 2024]:
                raise HTTPException(status_code=400, detail="Año no soportado para senado. Use 2018 o 2024")
            
            if plan == "A":
                sistema = "rp"
                escanos_totales = 96
            elif plan == "B":
                sistema = "mixto"
                escanos_totales = 128
            elif plan == "C":
                sistema = "mr"
                escanos_totales = 64
            else:
                raise HTTPException(status_code=400, detail="Plan no válido. Use A, B o C")
            
            path_parquet = f"data/computos_senado_{anio}.parquet"
            path_siglado = f"data/siglado-senado-{anio}.csv"
            
            if not os.path.exists(path_parquet):
                raise HTTPException(status_code=404, detail=f"Archivo no encontrado: {path_parquet}")
                
            resultado = procesar_senadores_v2(
                path_parquet=path_parquet,
                anio=anio,
                path_siglado=path_siglado,
                max_seats=escanos_totales,
                sistema=sistema
            )
        
        else:  # diputados
            if anio not in [2018, 2021, 2024]:
                raise HTTPException(status_code=400, detail="Año no soportado para diputados. Use 2018, 2021 o 2024")
            
            if plan == "A":
                sistema = "rp"
                max_seats = 300
            elif plan == "B":
                sistema = "mixto"
                max_seats = 300
            elif plan == "C":
                sistema = "mr"
                max_seats = 200
            else:
                raise HTTPException(status_code=400, detail="Plan no válido. Use A, B o C")
            
            path_parquet = f"data/computos_diputados_{anio}.parquet"
            path_siglado = f"data/siglado-diputados-{anio}.csv"
            
            if not os.path.exists(path_parquet):
                raise HTTPException(status_code=404, detail=f"Archivo no encontrado: {path_parquet}")
                
            resultado = procesar_diputados_v2(
                path_parquet=path_parquet,
                anio=anio,
                path_siglado=path_siglado,
                max_seats=max_seats,
                sistema=sistema
            )
        
        # Estructurar resultado para seat-chart
        resultado_formateado = {
            "status": "success",
            "anio": anio,
            "plan": plan,
            "sistema": sistema,
            "resultados": resultado.get("resultados", [])
        }
        
        # Formatear para seat-chart
        seat_chart_data = formato_seat_chart(resultado_formateado)
        
        return seat_chart_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo seat-chart: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
