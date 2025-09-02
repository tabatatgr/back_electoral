from typing import Dict, List, Any
import pandas as pd

def calcular_kpis_electorales(resultados: Dict[str, Any], anio: int, camara: str) -> Dict[str, Any]:
    """
    Calcula KPIs electorales a partir de los resultados procesados
    """
    try:
        if not resultados or "resultados" not in resultados:
            return {"error": "No hay datos para calcular KPIs"}
        
        datos = resultados["resultados"]
        if not datos:
            return {"error": "Resultados vacíos"}
        
        # Convertir a DataFrame para facilitar cálculos
        df = pd.DataFrame(datos)
        
        if df.empty:
            return {"error": "DataFrame vacío"}
        
        # Calcular KPIs básicos
        total_votos = df['VOTOS'].sum() if 'VOTOS' in df.columns else 0
        total_escanos = df['ESCANOS'].sum() if 'ESCANOS' in df.columns else 0
        partidos_representados = len(df[df['ESCANOS'] > 0]) if 'ESCANOS' in df.columns else 0
        
        # Partido más votado
        partido_mas_votado = ""
        votos_max = 0
        if 'VOTOS' in df.columns and not df.empty:
            idx_max = df['VOTOS'].idxmax()
            partido_mas_votado = df.loc[idx_max, 'PARTIDO'] if 'PARTIDO' in df.columns else ""
            votos_max = df.loc[idx_max, 'VOTOS']
        
        # Partido con más escaños
        partido_mas_escanos = ""
        escanos_max = 0
        if 'ESCANOS' in df.columns and not df.empty:
            idx_max_escanos = df['ESCANOS'].idxmax()
            partido_mas_escanos = df.loc[idx_max_escanos, 'PARTIDO'] if 'PARTIDO' in df.columns else ""
            escanos_max = df.loc[idx_max_escanos, 'ESCANOS']
        
        # Índice de proporcionalidad (diferencia promedio entre % votos y % escaños)
        indice_proporcionalidad = 0
        if 'PORCENTAJE_VOTOS' in df.columns and 'PORCENTAJE_ESCANOS' in df.columns:
            diferencias = abs(df['PORCENTAJE_VOTOS'] - df['PORCENTAJE_ESCANOS'])
            indice_proporcionalidad = round(diferencias.mean(), 2)
        
        return {
            "anio": anio,
            "camara": camara,
            "sistema": resultados.get("sistema", ""),
            "plan": resultados.get("plan", ""),
            "total_votos": int(total_votos),
            "total_escanos": int(total_escanos),
            "partidos_representados": int(partidos_representados),
            "partido_mas_votado": {
                "nombre": partido_mas_votado,
                "votos": int(votos_max),
                "porcentaje": round((votos_max / total_votos * 100) if total_votos > 0 else 0, 2)
            },
            "partido_mas_escanos": {
                "nombre": partido_mas_escanos,
                "escanos": int(escanos_max),
                "porcentaje": round((escanos_max / total_escanos * 100) if total_escanos > 0 else 0, 2)
            },
            "indice_proporcionalidad": indice_proporcionalidad,
            "efectividad_electoral": round((partidos_representados / len(df) * 100) if len(df) > 0 else 0, 2)
        }
        
    except Exception as e:
        return {"error": f"Error calculando KPIs: {str(e)}"}

def formato_seat_chart(resultados: Dict[str, Any]) -> Dict[str, Any]:
    """
    Formatea los resultados para el componente seat-chart del frontend
    """
    try:
        if not resultados or "resultados" not in resultados:
            return {"error": "No hay datos para el seat-chart"}
        
        datos = resultados["resultados"]
        if not datos:
            return {"error": "Resultados vacíos para seat-chart"}
        
        # Formatear datos para el seat-chart
        seats_data = []
        colores_partidos = {
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
            "OTROS": "#808080"
        }
        
        for partido_data in datos:
            partido = partido_data.get('PARTIDO', '')
            escanos = partido_data.get('ESCANOS', 0)
            
            if escanos > 0:
                seats_data.append({
                    "party": partido,
                    "seats": int(escanos),
                    "color": colores_partidos.get(partido, "#808080"),
                    "percentage": round(partido_data.get('PORCENTAJE_ESCANOS', 0), 1)
                })
        
        # Ordenar por número de escaños (descendente)
        seats_data.sort(key=lambda x: x['seats'], reverse=True)
        
        total_seats = sum(item['seats'] for item in seats_data)
        
        return {
            "seats": seats_data,
            "total_seats": total_seats,
            "metadata": {
                "anio": resultados.get("anio", ""),
                "plan": resultados.get("plan", ""),
                "sistema": resultados.get("sistema", "")
            }
        }
        
    except Exception as e:
        return {"error": f"Error formateando seat-chart: {str(e)}"}