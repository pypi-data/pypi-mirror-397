"""
Utilidades para lectura y parseo de logs
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum


class LogLevel(str, Enum):
    """Niveles de log soportados"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class SortOrder(str, Enum):
    """Orden de resultados"""
    ASC = "asc"
    DESC = "desc"


def parse_log_line(line: str, is_json: bool = True) -> Optional[Dict[str, Any]]:
    """
    Parsea una línea de log
    
    Args:
        line: Línea del archivo de log
        is_json: Si el log está en formato JSON
    
    Returns:
        Diccionario con los datos del log o None si no se puede parsear
    """
    try:
        if is_json:
            return json.loads(line.strip())
        else:
            # Parseo básico para logs de texto
            # Formato: YYYY-MM-DD HH:MM:SS - module - LEVEL - message
            pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - (.*?) - (.*?) - (.*)$'
            match = re.match(pattern, line)
            
            if match:
                return {
                    'timestamp': match.group(1),
                    'module': match.group(2),
                    'level': match.group(3),
                    'message': match.group(4),
                }
    except Exception:
        pass
    
    return None


def read_logs(
    log_directory: str,
    module: Optional[str] = None,
    level: Optional[LogLevel] = None,
    from_time: Optional[datetime] = None,
    to_time: Optional[datetime] = None,
    limit: int = 1000,
    order: SortOrder = SortOrder.DESC,
    is_json: bool = True,
) -> List[Dict[str, Any]]:
    """
    Lee y filtra logs del sistema
    
    Args:
        log_directory: Directorio donde se almacenan los logs
        module: Filtrar por módulo específico
        level: Filtrar por nivel de log
        from_time: Timestamp inicial (inclusivo)
        to_time: Timestamp final (inclusivo)
        limit: Número máximo de resultados
        order: Orden de resultados (asc/desc)
        is_json: Si los logs están en formato JSON
    
    Returns:
        Lista de logs que cumplen los filtros
    """
    log_dir = Path(log_directory)
    
    if not log_dir.exists():
        return []
    
    results = []
    
    # Determinar qué archivos leer
    if module:
        # Solo archivos del módulo específico
        pattern = f"{module}.log*"
    else:
        # Todos los archivos de log
        pattern = "*.log*"
    
    # Leer archivos de log
    for log_file in sorted(log_dir.glob(pattern)):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    log_entry = parse_log_line(line, is_json)
                    
                    if log_entry is None:
                        continue
                    
                    # Aplicar filtros
                    if level and log_entry.get('level') != level.value:
                        continue
                    
                    if from_time or to_time:
                        try:
                            log_time = datetime.fromisoformat(
                                log_entry.get('timestamp', '').replace('Z', '+00:00')
                            )
                            
                            if from_time and log_time < from_time:
                                continue
                            
                            if to_time and log_time > to_time:
                                continue
                        
                        except (ValueError, AttributeError):
                            # Si no se puede parsear el timestamp, incluir el log
                            pass
                    
                    results.append(log_entry)
        
        except Exception as e:
            # Log el error pero continuar
            print(f"Error leyendo {log_file}: {e}")
            continue
    
    # Ordenar resultados
    try:
        results.sort(
            key=lambda x: x.get('timestamp', ''),
            reverse=(order == SortOrder.DESC)
        )
    except Exception:
        pass
    
    # Aplicar límite
    return results[:limit]


def parse_time_range(last: Optional[str]) -> Optional[datetime]:
    """
    Parsea rangos de tiempo relativos como "2h", "30m", "1d"
    
    Args:
        last: String con el rango (ej. "2h", "30m", "1d")
    
    Returns:
        Datetime calculado o None
    """
    if not last:
        return None
    
    # Expresión regular para parsear: número + unidad
    match = re.match(r'^(\d+)([smhd])$', last.lower())
    
    if not match:
        return None
    
    value = int(match.group(1))
    unit = match.group(2)
    
    now = datetime.utcnow()
    
    if unit == 's':
        return now - timedelta(seconds=value)
    elif unit == 'm':
        return now - timedelta(minutes=value)
    elif unit == 'h':
        return now - timedelta(hours=value)
    elif unit == 'd':
        return now - timedelta(days=value)
    
    return None
