"""
Sistema de limpieza automática de logs antiguos
"""

import os
import asyncio
import time
from pathlib import Path
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from .config import LogConfig

_cleanup_task = None
_logger = logging.getLogger(__name__)


async def cleanup_old_logs(config: 'LogConfig') -> int:
    """
    Elimina archivos de log más antiguos que el período de retención
    
    Args:
        config: Configuración del sistema
    
    Returns:
        Número de archivos eliminados
    """
    log_dir = Path(config.log_directory)
    if not log_dir.exists():
        return 0
    
    # Calcular timestamp límite
    retention_seconds = config.retention_hours * 3600
    cutoff_time = time.time() - retention_seconds
    
    deleted_count = 0
    
    # Buscar todos los archivos de log
    for log_file in log_dir.glob("*.log*"):
        try:
            # Verificar tiempo de modificación
            mtime = log_file.stat().st_mtime
            
            if mtime < cutoff_time:
                log_file.unlink()
                deleted_count += 1
                _logger.info(f"Eliminado log antiguo: {log_file.name}")
        
        except Exception as e:
            _logger.error(f"Error eliminando {log_file.name}: {e}")
    
    return deleted_count


async def cleanup_loop(config: 'LogConfig') -> None:
    """
    Tarea en background que ejecuta limpieza periódica
    
    Args:
        config: Configuración del sistema
    """
    interval_seconds = config.cleanup_interval_hours * 3600
    
    _logger.info(f"Iniciada tarea de limpieza automática (cada {config.cleanup_interval_hours}h)")
    
    while True:
        try:
            await asyncio.sleep(interval_seconds)
            deleted = await cleanup_old_logs(config)
            
            if deleted > 0:
                _logger.info(f"Limpieza completada: {deleted} archivos eliminados")
        
        except asyncio.CancelledError:
            _logger.info("Tarea de limpieza cancelada")
            break
        
        except Exception as e:
            _logger.error(f"Error en tarea de limpieza: {e}")


def start_cleanup_task(config: 'LogConfig') -> None:
    """
    Inicia la tarea de limpieza automática en background
    
    Args:
        config: Configuración del sistema
    """
    global _cleanup_task
    
    if _cleanup_task is not None:
        _logger.warning("Tarea de limpieza ya está en ejecución")
        return
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # No hay event loop, crear uno nuevo
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    _cleanup_task = asyncio.create_task(cleanup_loop(config))


def stop_cleanup_task() -> None:
    """Detiene la tarea de limpieza automática"""
    global _cleanup_task
    
    if _cleanup_task is not None:
        _cleanup_task.cancel()
        _cleanup_task = None
