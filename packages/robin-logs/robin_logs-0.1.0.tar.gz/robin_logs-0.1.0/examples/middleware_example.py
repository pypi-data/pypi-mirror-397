"""
Ejemplo con middleware de logging automático
"""

from fastapi import FastAPI, Request
from robin_logs import setup_logging, register_log_routes, get_logger, LogConfig
import time
from typing import Callable

app = FastAPI(title="Robin Logs - Con Middleware")

# Configurar logs
config = LogConfig(
    log_directory="./logs",
    enable_api=True,
    api_prefix="/logs"
)

setup_logging(config)
register_log_routes(app, config)

# Logger para requests
request_logger = get_logger("requests")
business_logger = get_logger("business")


@app.middleware("http")
async def log_requests_middleware(request: Request, call_next: Callable):
    """
    Middleware que registra todas las peticiones HTTP
    """
    start_time = time.time()
    
    # Log de inicio
    request_logger.info("Request iniciado", extra={
        "method": request.method,
        "path": request.url.path,
        "client_ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown")
    })
    
    # Procesar request
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Log de respuesta exitosa
        request_logger.info("Request completado", extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
            "success": response.status_code < 400
        })
        
        return response
    
    except Exception as e:
        duration = time.time() - start_time
        
        # Log de error
        request_logger.error("Request falló", extra={
            "method": request.method,
            "path": request.url.path,
            "error": str(e),
            "error_type": type(e).__name__,
            "duration_ms": round(duration * 1000, 2)
        })
        
        raise


@app.get("/")
async def root():
    return {"message": "API con logging automático"}


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """Obtener usuario por ID"""
    business_logger.info("Consultando usuario", extra={
        "user_id": user_id
    })
    
    return {"user_id": user_id, "name": f"Usuario {user_id}"}


@app.post("/users")
async def create_user(name: str):
    """Crear nuevo usuario"""
    business_logger.info("Creando nuevo usuario", extra={
        "name": name
    })
    
    return {"user_id": 1, "name": name}


@app.get("/slow")
async def slow_endpoint():
    """Endpoint lento para probar logs de duración"""
    import asyncio
    await asyncio.sleep(2)
    return {"message": "Respuesta lenta"}


@app.get("/error")
async def error_endpoint():
    """Endpoint que genera un error"""
    raise ValueError("Error intencional para testing")


if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("Middleware de logging activo!")
    print("Todos los requests serán registrados automáticamente")
    print("Ver logs en: GET http://localhost:8000/logs/requests")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
