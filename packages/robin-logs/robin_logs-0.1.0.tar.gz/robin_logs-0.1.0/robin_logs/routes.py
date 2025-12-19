"""
Rutas FastAPI para consulta de logs
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Query, HTTPException, Header, Depends
from pydantic import BaseModel, Field

from .core import get_all_module_names, get_config
from .reader import read_logs, LogLevel, SortOrder, parse_time_range


class LogResponse(BaseModel):
    """Modelo de respuesta para logs"""
    total: int = Field(..., description="Número total de logs retornados")
    module: Optional[str] = Field(None, description="Módulo filtrado")
    logs: List[Dict[str, Any]] = Field(..., description="Lista de logs")


class ModulesResponse(BaseModel):
    """Modelo de respuesta para lista de módulos"""
    modules: List[str] = Field(..., description="Lista de módulos disponibles")


def verify_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
) -> None:
    """
    Dependencia para verificar API key
    
    Args:
        x_api_key: API key del header
    
    Raises:
        HTTPException: Si la autenticación falla
    """
    config = get_config()
    
    if config is None or not config.require_auth:
        return
    
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="API key requerida",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if x_api_key != config.api_key:
        raise HTTPException(
            status_code=403,
            detail="API key inválida",
        )


def create_log_router(require_auth: bool = False) -> APIRouter:
    """
    Crea el router de logs con autenticación opcional
    
    Args:
        require_auth: Si se requiere autenticación
    
    Returns:
        Router configurado
    """
    # Determinar dependencias
    dependencies = []
    if require_auth:
        dependencies.append(Depends(verify_api_key))
    
    router = APIRouter(
        prefix="",
        tags=["logs"],
        dependencies=dependencies,
    )
    
    @router.get("/", response_model=LogResponse)
    async def get_logs(
        module: Optional[str] = Query(None, description="Filtrar por módulo específico"),
        level: Optional[LogLevel] = Query(None, description="Filtrar por nivel de log"),
        from_time: Optional[datetime] = Query(None, alias="from", description="Timestamp inicial (ISO 8601)"),
        to_time: Optional[datetime] = Query(None, alias="to", description="Timestamp final (ISO 8601)"),
        last: Optional[str] = Query(None, description="Rango relativo (ej: 2h, 30m, 1d)", pattern=r"^\d+[smhd]$"),
        limit: int = Query(1000, ge=1, le=10000, description="Número máximo de resultados"),
        order: SortOrder = Query(SortOrder.DESC, description="Orden de resultados"),
    ) -> LogResponse:
        """
        Obtiene logs con filtros opcionales
        
        - **module**: Nombre del módulo (whatsapp, instagram, etc.)
        - **level**: Nivel de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        - **from**: Timestamp inicial en formato ISO 8601
        - **to**: Timestamp final en formato ISO 8601
        - **last**: Rango relativo (ej: "2h" = últimas 2 horas, "30m" = últimos 30 minutos, "1d" = último día)
        - **limit**: Máximo número de resultados (default: 1000, max: 10000)
        - **order**: Orden de resultados - "asc" o "desc" (default: desc)
        """
        config = get_config()
        
        if config is None:
            raise HTTPException(
                status_code=500,
                detail="Sistema de logs no inicializado"
            )
        
        # Si se especifica 'last', calcular from_time
        if last:
            calculated_from = parse_time_range(last)
            if calculated_from:
                from_time = calculated_from
        
        # Leer logs
        logs = read_logs(
            log_directory=config.log_directory,
            module=module,
            level=level,
            from_time=from_time,
            to_time=to_time,
            limit=limit,
            order=order,
            is_json=config.json_format,
        )
        
        return LogResponse(
            total=len(logs),
            module=module,
            logs=logs,
        )
    
    @router.get("/{module}", response_model=LogResponse)
    async def get_module_logs(
        module: str,
        level: Optional[LogLevel] = Query(None, description="Filtrar por nivel de log"),
        from_time: Optional[datetime] = Query(None, alias="from", description="Timestamp inicial (ISO 8601)"),
        to_time: Optional[datetime] = Query(None, alias="to", description="Timestamp final (ISO 8601)"),
        last: Optional[str] = Query(None, description="Rango relativo (ej: 2h, 30m, 1d)", pattern=r"^\d+[smhd]$"),
        limit: int = Query(1000, ge=1, le=10000, description="Número máximo de resultados"),
        order: SortOrder = Query(SortOrder.DESC, description="Orden de resultados"),
    ) -> LogResponse:
        """
        Obtiene logs de un módulo específico
        
        - **module**: Nombre del módulo (path parameter)
        - **level**: Nivel de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        - **from**: Timestamp inicial en formato ISO 8601
        - **to**: Timestamp final en formato ISO 8601
        - **last**: Rango relativo (ej: "2h", "30m", "1d")
        - **limit**: Máximo número de resultados (default: 1000, max: 10000)
        - **order**: Orden de resultados - "asc" o "desc" (default: desc)
        """
        config = get_config()
        
        if config is None:
            raise HTTPException(
                status_code=500,
                detail="Sistema de logs no inicializado"
            )
        
        # Si se especifica 'last', calcular from_time
        if last:
            calculated_from = parse_time_range(last)
            if calculated_from:
                from_time = calculated_from
        
        # Leer logs del módulo
        logs = read_logs(
            log_directory=config.log_directory,
            module=module,
            level=level,
            from_time=from_time,
            to_time=to_time,
            limit=limit,
            order=order,
            is_json=config.json_format,
        )
        
        if not logs:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontraron logs para el módulo '{module}'"
            )
        
        return LogResponse(
            total=len(logs),
            module=module,
            logs=logs,
        )
    
    @router.get("/modules/list", response_model=ModulesResponse)
    async def get_modules() -> ModulesResponse:
        """
        Obtiene la lista de módulos disponibles
        
        Returns:
            Lista de nombres de módulos que tienen logs
        """
        modules = get_all_module_names()
        
        return ModulesResponse(
            modules=modules
        )
    
    return router


def register_log_routes(app, config: Optional['LogConfig'] = None) -> None:
    """
    Registra las rutas de logs en una aplicación FastAPI existente
    
    Args:
        app: Instancia de FastAPI
        config: Configuración opcional (usa la global si no se proporciona)
    
    Example:
        >>> from fastapi import FastAPI
        >>> from robin_logs import register_log_routes, LogConfig
        >>> 
        >>> app = FastAPI()
        >>> config = LogConfig(api_prefix="/api/logs")
        >>> register_log_routes(app, config)
    """
    # Usar configuración proporcionada o la global
    if config is None:
        config = get_config()
    
    if config is None:
        from .config import LogConfig
        config = LogConfig()
    
    # Solo registrar si está habilitado
    if not config.enable_api:
        return
    
    # Crear router con o sin autenticación
    router = create_log_router(require_auth=config.require_auth)
    
    # Incluir router en la app con el prefijo configurado
    app.include_router(router, prefix=config.api_prefix)
