# Backend Electoral API

API REST para procesamiento de datos electorales con soporte de coaliciones, desarrollada con FastAPI.

## Características

- ✅ **Procesamiento de Senado**: Planes A (96 escaños RP), B (96 MR+PM + 32 RP), C (64 escaños MR)
- ✅ **Procesamiento de Diputados**: Planes A (300 RP), B (200 MR + 100 RP), C (200 MR)  
- ✅ **Soporte de Coaliciones**: Detección automática y asignación correcta de escaños
- ✅ **Datos 2018-2024**: Información electoral completa
- ✅ **Documentación Automática**: Swagger UI en `/docs`

## Deployment en Render

### Configuración Automática

El proyecto está configurado para deployment automático en Render con:

- **Comando de Inicio**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Archivo de Configuración**: `Procfile` y `render.yaml`
- **Python Version**: 3.11+
- **Build Command**: `pip install -r requirements.txt`

### Pasos para Deploy

1. **Conectar Repositorio**: 
   - Crear nuevo Web Service en Render
   - Conectar tu repositorio GitHub
   - Seleccionar rama `main` o `iteraciones`

2. **Configuración del Servicio**:
   ```
   Name: backend-electoral
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

3. **Variables de Entorno** (Opcionales):
   ```
   PYTHON_VERSION=3.11
   ```

4. **Deploy**: Render detectará automáticamente la configuración y comenzará el deployment.

## Endpoints Disponibles

### GET /
Información básica de la API

### GET /health
Health check del servicio

### POST /procesar/senado
Procesa datos del senado
```json
{
  "anio": 2018,
  "plan": "A",
  "escanos_totales": 96
}
```

### POST /procesar/diputados  
Procesa datos de diputados
```json
{
  "anio": 2021,
  "plan": "B"
}
```

### GET /años-disponibles
Retorna años y planes disponibles

### GET /coaliciones/{anio}
Obtiene coaliciones para un año específico

## Estructura de Respuesta

```json
{
  "status": "success",
  "anio": 2018,
  "plan": "A",
  "sistema": "rp",
  "escanos_totales": 96,
  "partidos_procesados": 8,
  "resultados": [
    {
      "PARTIDO": "MORENA",
      "VOTOS": 25567852,
      "ESCANOS": 32,
      "PORCENTAJE_VOTOS": 35.7,
      "PORCENTAJE_ESCANOS": 33.3
    }
  ]
}
```

## Coaliciones Soportadas

### 2018
- **Por México al Frente**: PAN + PRD + MC
- **Juntos Haremos Historia**: MORENA + PT

### 2024  
- **Fuerza y Corazón por México**: PAN + PRD + PRI
- **Sigamos Haciendo Historia**: MORENA + PT + PVEM

## Desarrollo Local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
python main.py

# O con uvicorn directamente
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Documentación API

Una vez desplegado, la documentación interactiva estará disponible en:
- **Swagger UI**: `https://tu-app.onrender.com/docs`
- **ReDoc**: `https://tu-app.onrender.com/redoc`
