"""Logging configuration for Autonomous YouTube Pipeline."""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from config.settings import settings

def setup_logger(name: str = "pipeline") -> logging.Logger:
    """Configures and returns a logger instance with console and file handlers.
    
    Args:
        name: Name of the logger.
        
    Returns:
        Configured logging.Logger.
    """
    settings.ensure_directories()
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    # Prevent duplicate handlers if already configured
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s:%(filename)s:%(lineno)d]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console output handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Rotating file handler (10 MB per file, max 5 backups)
    log_file_path = settings.LOGS_DIR / "pipeline.log"
    file_handler = RotatingFileHandler(
        filename=str(log_file_path),
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
