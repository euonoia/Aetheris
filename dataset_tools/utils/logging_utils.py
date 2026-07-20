"""
Logging utilities for Dataset Engineering Toolkit.

Provides centralized logging configuration for all components.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional

from config import LOG_FILE_NAME, LOG_FORMAT, LOG_DATE_FORMAT, DEFAULT_LOGS_FOLDER


class LoggerManager:
    """Manages logger creation and configuration."""

    _instance: Optional["LoggerManager"] = None
    _loggers: dict = {}

    def __new__(cls) -> "LoggerManager":
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize logger manager."""
        self.log_dir = DEFAULT_LOGS_FOLDER
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / LOG_FILE_NAME

    def get_logger(self, name: str) -> logging.Logger:
        """
        Get or create a logger with the given name.

        Args:
            name: Logger name (typically __name__ from calling module)

        Returns:
            Configured logger instance
        """
        if name in self._loggers:
            return self._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        # Remove existing handlers to avoid duplicates
        if logger.handlers:
            logger.handlers.clear()

        # File handler
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_file, maxBytes=10 * 1024 * 1024, backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        logger.propagate = False

        self._loggers[name] = logger
        return logger

    @staticmethod
    def clear_handlers(logger: logging.Logger) -> None:
        """
        Clear all handlers from a logger.

        Args:
            logger: Logger instance
        """
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """
    Convenience function to get a logger.

    Args:
        name: Logger name

    Returns:
        Configured logger instance
    """
    manager = LoggerManager()
    return manager.get_logger(name)
