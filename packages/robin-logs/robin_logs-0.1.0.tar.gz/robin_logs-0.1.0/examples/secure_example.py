"""
Ejemplo con autenticación y seguridad
"""

import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from robin_logs import setup_logging, register_log_routes, get_logger, LogConfig

app = FastAPI(title="Robin Logs - Seguro")

# Configuración con autenticación
config = LogConfig(
    log_directory="./logs",
    enable_api=True,
    api_prefix="/api/logs",
    require_auth=True,
    api_key="mi-super-clave-secreta-123"  # En producción: os.getenv("LOGS_API_KEY")
)

setup_logging(config)
register_log_routes(app, config)

# Logger para la API
api_logger = get_logger("secure_api")

# Security scheme para otros endpoints
security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verificar token de autenticación para endpoints propios"""
    token = credentials.credentials
    
    # En producción, verificar contra base de datos o JWT
    if token != "mi-token-de-prueba":
        api_logger.warning("Intento de acceso no autorizado", extra={
            "token": token[:10] + "..."
        })
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    return token


@app.get("/")
async def root():
    """Endpoint público"""
    return {
        "message": "API Segura",
        "docs": "/docs",
        "note": "Los endpoints de logs requieren X-API-Key header"
    }


@app.get("/protected")
async def protected_endpoint(token: str = Depends(verify_token)):
    """Endpoint protegido con Bearer token"""
    api_logger.info("Acceso a endpoint protegido", extra={
        "authenticated": True
    })
    
    return {"message": "Acceso autorizado", "data": "información sensible"}


@app.post("/action")
async def perform_action(token: str = Depends(verify_token)):
    """Simular una acción que genera logs"""
    api_logger.info("Acción ejecutada", extra={
        "action": "example_action",
        "user": "authenticated_user"
    })
    
    return {"status": "completed"}


if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("INFORMACIÓN DE SEGURIDAD")
    print("="*60)
    print(f"Para acceder a endpoints propios, usar:")
    print(f"  Authorization: Bearer mi-token-de-prueba")
    print(f"\nPara acceder a /api/logs/*, usar:")
    print(f"  X-API-Key: mi-super-clave-secreta-123")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
