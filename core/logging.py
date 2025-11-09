"""Structured logging setup using structlog.

This module configures structured JSON logging using structlog, which
provides better log formatting and context management compared to
standard Python logging. Logs are output as JSON in production and
formatted for console in debug mode.

Example:
    ```python
    from core.logging import get_logger
    
    logger = get_logger(__name__)
    logger.info("User logged in", user_id=123)
    ```
"""

import logging
import sys
import structlog
from core.settings import settings


def setup_logging() -> None:
    """Configure structured JSON logging.
    
    Sets up both standard library logging and structlog with appropriate
    processors for JSON output (production) or console output (debug).
    The log level is determined by settings.log_level.
    
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
        
    Returns:
        structlog.BoundLogger: Configured logger instance
        
    Example:
        ```python
        logger = get_logger(__name__)
        logger.info("Operation completed", duration=1.5)
        ```
    """
    return structlog.get_logger(name)

