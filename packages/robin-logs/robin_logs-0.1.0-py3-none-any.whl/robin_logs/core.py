"""
Core del sistema de logging
"""

import os
import logging
import json
from typing import Dict, Any, Optional
from logging.handlers import RotatingFileHandler
from pathlib import Path
from pythonjsonlogger import jsonlogger


# Registry global de loggers
_loggers: Dict[str, logging.Logger] = {}
_config: Optional['LogConfig'] = None


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Formateador JSON personalizado para logs estructurados"""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]):
        """Añade campos personalizados al log"""
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        # Añadir timestamp
        if not log_record.get('timestamp'):
            log_record['timestamp'] = self.formatTime(record, self.datefmt)
        
        # Añadir nivel de log
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname
        
        # Añadir módulo/nombre del logger
        log_record['module'] = record.name
        
        # Asegurar que el mensaje esté presente
        if not log_record.get('message'):
            log_record['message'] = record.getMessage()


def setup_logging(config: 'LogConfig') -> None:
    """
    Inicializa el sistema de logging con la configuración proporcionada
    
    Args:
        config: Configuración del sistema de logs
    """
    global _config
    _config = config
    
    # Crear directorio de logs si no existe
    log_dir = Path(config.log_directory)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Si auto_cleanup está habilitado, iniciar tarea de limpieza
    if config.auto_cleanup:
        from .cleanup import start_cleanup_task
        start_cleanup_task(config)


def get_logger(module_name: str, config: Optional['LogConfig'] = None) -> logging.Logger:
    """
    Obtiene o crea un logger para el módulo especificado
    
    Args:
        module_name: Nombre del módulo (ej. "whatsapp", "instagram")
        config: Configuración opcional (usa la global si no se proporciona)
    
    Returns:
        Logger configurado para el módulo
    
    Example:
        >>> logger = get_logger("whatsapp")
        >>> logger.info("Mensaje enviado", extra={"phone": "+57300..."})
    """
    global _config, _loggers
    
    # Usar configuración proporcionada o la global
    if config is None:
        if _config is None:
            # Usar configuración por defecto si no se ha inicializado
            from .config import LogConfig
            config = LogConfig()
            _config = config
        else:
            config = _config
    
    # Si el logger ya existe, devolverlo
    if module_name in _loggers:
        return _loggers[module_name]
    
    # Crear nuevo logger
    logger = logging.getLogger(f"robin_logs.{module_name}")
    logger.setLevel(getattr(logging, config.log_level.upper()))
    logger.propagate = False
    
    # Crear directorio de logs si no existe
    log_dir = Path(config.log_directory)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Construir path del archivo de log
    log_filename = config.log_filename_pattern.format(module=module_name)
    log_path = log_dir / log_filename
    
    # Configurar handler con rotación
    handler = RotatingFileHandler(
        filename=str(log_path),
        maxBytes=config.max_bytes,
        backupCount=config.backup_count,
        encoding='utf-8'
    )
    
    # Configurar formateador
    if config.json_format:
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Guardar en registry
    _loggers[module_name] = logger
    
    return logger


def get_all_module_names() -> list[str]:
    """
    Retorna lista de todos los módulos que tienen logs
    
    Returns:
        Lista de nombres de módulos
    """
    global _config
    
    if _config is None:
        return []
    
    log_dir = Path(_config.log_directory)
    if not log_dir.exists():
        return []
    
    modules = set()
    pattern = _config.log_filename_pattern.replace("{module}", "*")
    
    for log_file in log_dir.glob(pattern):
        # Extraer nombre del módulo del nombre del archivo
        module_name = log_file.stem
        # Remover sufijos de rotación (.1, .2, etc.)
        if module_name and not module_name.split('.')[-1].isdigit():
            modules.add(module_name)
    
    return sorted(list(modules))


def get_config() -> Optional['LogConfig']:
    """Retorna la configuración global actual"""
    return _config
