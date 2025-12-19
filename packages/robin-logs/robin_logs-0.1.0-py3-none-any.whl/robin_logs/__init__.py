"""
robin-logs - Sistema de logs estructurado y desacoplado para FastAPI
"""

from .core import get_logger, setup_logging
from .routes import register_log_routes
from .config import LogConfig

__version__ = "0.1.0"
__all__ = [
    "get_logger",
    "setup_logging",
    "register_log_routes",
    "LogConfig",
]
