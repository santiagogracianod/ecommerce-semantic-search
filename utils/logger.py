"""Sistema de logging configurado para la aplicación."""
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional

from config import get_settings

settings = get_settings()


class StructuredFormatter(logging.Formatter):
    """Formatter personalizado para logs estructurados."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Formatea el log record con estructura adicional."""
        # Agregar timestamp
        record.timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Formatear el mensaje base
        formatted = super().format(record)
        
        # Agregar información extra si existe
        if hasattr(record, 'extra_data'):
            extra_info = " | ".join([f"{k}={v}" for k, v in record.extra_data.items()])
            formatted += f" | {extra_info}"
            
        return formatted


def get_logger(name: str) -> logging.Logger:
    """Configura y retorna un logger estructurado."""
    logger = logging.getLogger(name)
    
    # Solo configurar si no está ya configurado
    if not logger.handlers:
        # Configurar nivel
        log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
        logger.setLevel(log_level)
        
        # Crear handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        
        # Configurar formato
        formatter = StructuredFormatter(
            fmt='%(timestamp)s | %(levelname)s | %(name)s | %(message)s'
        )
        handler.setFormatter(formatter)
        
        # Agregar handler
        logger.addHandler(handler)
        
        # Evitar propagación para prevenir duplicados
        logger.propagate = False
    
    return logger


def log_with_extra(logger: logging.Logger, level: str, message: str, **extra: Any) -> None:
    """Helper para logging con información extra."""
    # Crear un LogRecord temporal con información extra
    record = logging.LogRecord(
        name=logger.name,
        level=getattr(logging, level.upper()),
        pathname="",
        lineno=0,
        msg=message,
        args=(),
        exc_info=None
    )
    record.extra_data = extra
    logger.handle(record)