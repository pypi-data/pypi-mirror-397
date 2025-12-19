"""
Configuración para robin-logs
"""

from typing import Optional
from dataclasses import dataclass, field


@dataclass
class LogConfig:
    """Configuración del sistema de logs"""
    
    # Directorio donde se almacenan los logs
    log_directory: str = "./logs"
    
    # Formato del archivo de log
    log_filename_pattern: str = "{module}.log"
    
    # Tamaño máximo por archivo antes de rotar (en bytes)
    # Por defecto: 10MB
    max_bytes: int = 10 * 1024 * 1024
    
    # Número de archivos de backup a mantener
    backup_count: int = 5
    
    # Retención de logs en horas (para limpieza automática)
    # Por defecto: 72 horas (3 días)
    retention_hours: int = 72
    
    # Nivel de log mínimo a capturar
    log_level: str = "INFO"
    
    # Formato JSON personalizado
    json_format: bool = True
    
    # Incluir timestamp en cada log
    include_timestamp: bool = True
    
    # Timezone para timestamps
    timezone: str = "UTC"
    
    # Configuración de endpoints
    enable_api: bool = True
    api_prefix: str = "/logs"
    
    # Protección de endpoints
    require_auth: bool = False
    api_key_header: str = "X-API-Key"
    api_key: Optional[str] = None
    
    # Limpieza automática de logs antiguos
    auto_cleanup: bool = True
    cleanup_interval_hours: int = 24
    
    def __post_init__(self):
        """Validación de configuración"""
        if self.require_auth and not self.api_key:
            raise ValueError("API key requerida cuando require_auth=True")
