"""
Logging configuration module.

This module configures the loguru logger for the entire application,
providing consistent logging across all components.
"""

import sys
import os
from datetime import datetime
from loguru import logger
import logging
import inspect

from models import MOSCOW_TZ
from settings import settings
from custom_types import LogLevels
# Define log directory

os.makedirs(settings.LOG_DIR, exist_ok=True)

# Current date in Moscow timezone for log file naming
current_date = datetime.now(MOSCOW_TZ).strftime("%Y-%m-%d")
log_file_path = os.path.join(settings.LOG_DIR, f"bot_{current_date}.log")

class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame:
            filename = frame.f_code.co_filename
            is_logging = filename == logging.__file__
            is_frozen = "importlib" in filename and "_bootstrap" in filename
            if depth > 0 and not (is_logging or is_frozen):
                break
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging(level: LogLevels = "INFO"):
    """
    Set up application logging configuration.

    Args:
        level: The minimum log level to capture. Default is "INFO".
            Valid options are "TRACE", "DEBUG", "INFO", "SUCCESS",
            "WARNING", "ERROR", "CRITICAL".

    Returns:
        The configured logger instance
    """
    logger.remove()
    
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    
    # Add console handler with color
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=level,
        colorize=True,
    )

    # Add file handler for all levels
    logger.add(
        log_file_path,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=level,
        rotation="12:00",  # New file at noon Moscow time
        compression="zip",
        retention="30 days",
    )

    # Log startup message
    logger.info("Logging system initialized")