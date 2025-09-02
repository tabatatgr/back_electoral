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
            quota_method = "hare"
            divisor_method = "dhondt"
            max_seats = mr_seats_final + rp_seats_final
        elif plan == "plan_a":
            # Plan A: solo RP según test_flujo.py
            sistema_final = "rp"
            mr_seats_final = 0
            rp_seats_final = 96
            umbral_final = 0.03
            quota_method = "hare"
            divisor_method = None
            max_seats = rp_seats_final
        elif plan == "plan_c":
            # Plan C: solo MR según test_flujo.py
            sistema_final = "mr"
            mr_seats_final = 64
            rp_seats_final = 0
            umbral_final = 0.0
            quota_method = "hare"
            divisor_method = None
            max_seats = mr_seats_final
        elif plan == "personalizado":
            # Plan personalizado con parámetros del usuario
            if not sistema:
                raise HTTPException(status_code=400, detail="Sistema requerido para plan personalizado")
            sistema_final = sistema
            mr_seats_final = mr_seats or 96
            rp_seats_final = rp_seats or 32
            umbral_final = umbral if umbral is not None else 0.03
            quota_method = "hare"
            divisor_method = "dhondt" if sistema_final == "mixto" else None
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
        
        # Transformar resultado al formato esperado por el frontend
        resultados_lista = []
        if 'tot' in resultado:
            for partido, escanos in resultado['tot'].items():
                resultados_lista.append({
                    'partido': partido,
                    'escanos_totales': escanos,
                    'escanos_mr': resultado.get('mr', {}).get(partido, 0),
                    'escanos_rp': resultado.get('rp', {}).get(partido, 0),
                    'votos': resultado.get('votos', {}).get(partido, 0),
                    'supera_umbral': resultado.get('ok', {}).get(partido, False)
                })
        
        return {
            "status": "success",
            "anio": anio,
            "plan": plan,
            "sistema": sistema_final,
            "max_seats": max_seats,
            "mr_seats": mr_seats_final,
            "rp_seats": rp_seats_final,
            "umbral": umbral_final,
            "partidos_procesados": len(resultados_lista),
            "resultados": resultados_lista
        }
        
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
    max_seats_per_party: Optional[int] = None
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
            quota_method = "hare"
            divisor_method = "dhondt"
        elif plan == "plan_a":
            # Plan A: solo RP según test_flujo.py
            sistema_final = "rp"
            max_seats = 300
            mr_seats_final = 0
            rp_seats_final = 300
            umbral_final = 0.03
            max_seats_per_party_final = None
            quota_method = "hare"
            divisor_method = None
        elif plan == "plan_c":
            # Plan C: solo MR según test_flujo.py
            sistema_final = "mr"
            max_seats = 300
            mr_seats_final = 300
            rp_seats_final = 0
            umbral_final = 0.0
            max_seats_per_party_final = None
            quota_method = "hare"
            divisor_method = None
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
            quota_method = "hare"
            divisor_method = "dhondt" if sistema_final == "mixto" else None
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
            quota_method=quota_method,
            divisor_method=divisor_method
        )
        
        # Transformar resultado al formato esperado por el frontend
        resultados_lista = []
        if 'tot' in resultado:
            for partido, escanos in resultado['tot'].items():
                resultados_lista.append({
                    'partido': partido,
                    'escanos_totales': escanos,
                    'escanos_mr': resultado.get('mr', {}).get(partido, 0),
                    'escanos_rp': resultado.get('rp', {}).get(partido, 0),
                    'votos': resultado.get('votos', {}).get(partido, 0),
                    'supera_umbral': resultado.get('ok', {}).get(partido, False)
                })
        
        return {
            "status": "success",
            "anio": anio,
            "plan": plan,
            "sistema": sistema_final,
            "max_seats": max_seats,
            "mr_seats": mr_seats_final,
            "rp_seats": rp_seats_final,
            "umbral": umbral_final,
            "max_seats_per_party": max_seats_per_party_final,
            "quota_method": quota_method,
            "divisor_method": divisor_method,
            "partidos_procesados": len(resultados_lista),
            "resultados": resultados_lista
        }
        
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
