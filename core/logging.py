"""Structured logging setup using structlog.

This module configures structured JSON logging using structlog, which
provides better log formatting and context management compared to
standard Python logging. Logs are output as JSON in production and
formatted for console in debug mode. Optionally logs can be saved to a file.

Example:
    ```python
    from core.logging import get_logger
    
    # Regular logger (stdout only)
    logger = get_logger(__name__)
    logger.info("User logged in", user_id=123)
    
    # AI logger (automatically logs to file)
    ai_logger = get_logger("ai")
    ai_logger.info("AI request processed", question="What is AI?")
    ```
"""

import logging
import sys
import os
from pathlib import Path
from datetime import datetime
import structlog
from core.settings import settings


def setup_logging() -> None:
    """Configure structured JSON logging.
    
    Sets up both standard library logging and structlog with appropriate
    processors for JSON output (production) or console output (debug).
    The log level is determined by settings.log_level.
    
    File handlers are created on-demand for the "ai" logger, which automatically
    creates logs in the structure: logs/ai/YYYY-MM-DD.log
    
    Note:
        This should be called once at application startup before any
        logging occurs.
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
    )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer() if settings.log_level.upper() != "DEBUG" else structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )


def get_logger(name: str = __name__):
    """Get a structured logger instance.
    
    Args:
        name: Logger name (typically __name__ of the calling module)
              If name is "ai", automatically enables file logging to logs/ai/YYYY-MM-DD.log
        
    Returns:
        structlog.BoundLogger: Configured logger instance
        
    Example:
        ```python
        # Regular logger (stdout only)
        logger = get_logger(__name__)
        logger.info("Operation completed", duration=1.5)
        
        # AI logger (automatically logs to file)
        ai_logger = get_logger("ai")
        # Creates: logs/ai/2025-11-09.log (date auto-generated)
        ```
    """
    # Auto-enable file logging for "ai" logger
    if name == "ai":
        # Use logger name as folder, current system date as filename
        # Structure: logs/ai/YYYY-MM-DD.log
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_dir = Path("logs") / name
        log_file = log_dir / f"{date_str}.log"
        
        # Ensure logs directory exists
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Get or create logger with file handler
        # Use a unique logger name based on the file path to avoid conflicts
        logger_name = f"{name}_file_{log_file}"
        file_logger = logging.getLogger(logger_name)
        
        # Only add handler if it doesn't already exist
        if not file_logger.handlers:
            file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
            file_handler.setLevel(logging.INFO)
            # Use simple formatter - structlog will format the message
            file_handler.setFormatter(logging.Formatter("%(message)s"))
            file_logger.setLevel(logging.INFO)
            file_logger.addHandler(file_handler)
            file_logger.propagate = False  # Don't propagate to root logger
        
        # Wrap with structlog - this will use the global structlog config
        # which includes JSONRenderer for INFO level
        return structlog.wrap_logger(file_logger)
    
    # Regular logger (stdout only)
    return structlog.get_logger(name)

