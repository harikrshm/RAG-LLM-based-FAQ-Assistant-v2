"""
Logging Configuration

Centralized logging configuration with appropriate log levels and formatters.
"""

import logging
import sys
from typing import Optional
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

from backend.config.settings import settings


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    enable_file_logging: bool = True,
    enable_console_logging: bool = True,
):
    """
    Configure application-wide logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (default: logs/app.log)
        enable_file_logging: Enable file logging
        enable_console_logging: Enable console logging
    """
    # Use provided level or from settings
    level = log_level or settings.LOG_LEVEL
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create logs directory if it doesn't exist
    if enable_file_logging:
        log_file_path = log_file or "logs/app.log"
        log_dir = Path(log_file_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    simple_formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    json_formatter = None
    try:
        # Try to use JSON formatter if available
        import json_log_formatter
        json_formatter = json_log_formatter.JSONFormatter()
    except ImportError:
        pass
    
    # Console handler
    if enable_console_logging:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        
        # Use simple formatter for console in production, detailed in debug
        if settings.DEBUG:
            console_handler.setFormatter(detailed_formatter)
        else:
            console_handler.setFormatter(simple_formatter)
        
        root_logger.addHandler(console_handler)
    
    # File handler with rotation
    if enable_file_logging:
        # Main application log
        file_handler = RotatingFileHandler(
            log_file_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8',
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)
        
        # Error log (only errors and above)
        error_log_path = Path(log_file_path).parent / "error.log"
        error_handler = RotatingFileHandler(
            str(error_log_path),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10,
            encoding='utf-8',
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(error_handler)
        
        # Access log (requests)
        access_log_path = Path(log_file_path).parent / "access.log"
        access_handler = TimedRotatingFileHandler(
            str(access_log_path),
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8',
        )
        access_handler.setLevel(logging.INFO)
        access_handler.setFormatter(simple_formatter)
        
        # Create access logger
        access_logger = logging.getLogger("access")
        access_logger.setLevel(logging.INFO)
        access_logger.addHandler(access_handler)
        access_logger.propagate = False
    
    # Configure third-party loggers
    configure_third_party_loggers(log_level)
    
    # Log configuration
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured: level={logging.getLevelName(log_level)}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")


def configure_third_party_loggers(level: int):
    """
    Configure logging levels for third-party libraries.
    
    Args:
        level: Base logging level
    """
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    
    # Vector database loggers
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("chromadb.telemetry").setLevel(logging.ERROR)
    
    # LLM library loggers
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("google.generativeai").setLevel(logging.WARNING)
    
    # Embedding model loggers
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    
    # Set our application loggers to appropriate levels
    logging.getLogger("backend").setLevel(level)
    logging.getLogger("backend.services").setLevel(level)
    logging.getLogger("backend.api").setLevel(level)
    logging.getLogger("backend.middleware").setLevel(level)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with proper naming.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class RequestContextFilter(logging.Filter):
    """
    Logging filter to add request context to log records.
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add request context to log record."""
        # Request ID from context (set by middleware)
        request_id = getattr(record, 'request_id', None)
        if request_id:
            record.request_id = request_id
        
        # Session ID from context
        session_id = getattr(record, 'session_id', None)
        if session_id:
            record.session_id = session_id
        
        return True


def setup_request_logging():
    """
    Set up request-specific logging configuration.
    """
    # Add request context filter to root logger
    request_filter = RequestContextFilter()
    
    for handler in logging.root.handlers:
        handler.addFilter(request_filter)


# Environment-specific log levels
LOG_LEVELS = {
    "development": logging.DEBUG,
    "staging": logging.INFO,
    "production": logging.WARNING,
    "test": logging.WARNING,
}


def get_log_level_for_environment(environment: str) -> int:
    """
    Get appropriate log level for environment.
    
    Args:
        environment: Environment name
        
    Returns:
        Logging level
    """
    return LOG_LEVELS.get(environment.lower(), logging.INFO)

