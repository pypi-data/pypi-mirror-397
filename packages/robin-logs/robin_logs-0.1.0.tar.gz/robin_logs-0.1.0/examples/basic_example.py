"""
Ejemplo básico de integración de robin-logs con FastAPI
"""

from fastapi import FastAPI
from robin_logs import setup_logging, register_log_routes, get_logger, LogConfig

# Crear aplicación FastAPI
app = FastAPI(
    title="Robin Logs - Ejemplo Básico",
    description="Ejemplo de integración de robin-logs",
    version="1.0.0"
)

# Configurar sistema de logs
config = LogConfig(
    log_directory="./logs",
    retention_hours=72,
    max_bytes=10 * 1024 * 1024,
    enable_api=True,
    api_prefix="/logs",
    require_auth=False  # Cambiar a True en producción
)

# Inicializar logs
setup_logging(config)

# Registrar endpoints de logs
register_log_routes(app, config)

# Obtener loggers para diferentes módulos
api_logger = get_logger("api")
business_logger = get_logger("business")


@app.on_event("startup")
async def startup_event():
    """Evento al iniciar la aplicación"""
    api_logger.info("Aplicación iniciada", extra={
        "version": "1.0.0",
        "environment": "development"
    })


@app.on_event("shutdown")
async def shutdown_event():
    """Evento al cerrar la aplicación"""
    api_logger.info("Aplicación detenida")


@app.get("/")
async def root():
    """Endpoint principal"""
    api_logger.info("Acceso a endpoint raíz")
    return {"message": "Bienvenido a Robin Logs", "docs": "/docs"}


@app.get("/test-log")
async def test_log():
    """Endpoint para probar logs"""
    business_logger.info("Test de logging", extra={
        "test_id": "123",
        "user": "demo"
    })
    
    return {
        "message": "Log creado exitosamente",
        "check_logs": "GET /logs/business"
    }


@app.get("/test-error")
async def test_error():
    """Endpoint para probar logs de error"""
    try:
        # Simular un error
        result = 1 / 0
    except Exception as e:
        business_logger.error("Error simulado", extra={
            "error": str(e),
            "error_type": type(e).__name__
        })
        
        return {
            "message": "Error registrado",
            "check_logs": "GET /logs/business?level=ERROR"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
