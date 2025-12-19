"""Logging utilities for HOS SecSuite"""

import logging
import os
from typing import Dict, Any, Optional


class Logger:
    """Custom logger class with structured logging support"""
    
    def __init__(self,
                 name: str = "hos-secsuite",
                 level: int = logging.INFO,
                 log_file: Optional[str] = None,
                 file_level: int = logging.DEBUG,
                 formatter: Optional[logging.Formatter] = None):
        """Initialize logger
        
        Args:
            name: Logger name
            level: Console logging level
            log_file: Log file path
            file_level: File logging level
            formatter: Custom formatter
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)  # Set to lowest level, handlers will filter
        
        # Remove existing handlers if any
        self.logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        
        # Default formatter if not provided
        if formatter is None:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler if log_file is provided
        if log_file:
            # Create directory if it doesn't exist
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(file_level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str, **kwargs):
        """Log debug message
        
        Args:
            message: Log message
            **kwargs: Additional parameters for structured logging
        """
        if kwargs:
            message = f"{message} {kwargs}"
        self.logger.debug(message)
    
    def info(self, message: str, **kwargs):
        """Log info message
        
        Args:
            message: Log message
            **kwargs: Additional parameters for structured logging
        """
        if kwargs:
            message = f"{message} {kwargs}"
        self.logger.info(message)
    
    def warning(self, message: str, **kwargs):
        """Log warning message
        
        Args:
            message: Log message
            **kwargs: Additional parameters for structured logging
        """
        if kwargs:
            message = f"{message} {kwargs}"
        self.logger.warning(message)
    
    def error(self, message: str, **kwargs):
        """Log error message
        
        Args:
            message: Log message
            **kwargs: Additional parameters for structured logging
        """
        if kwargs:
            message = f"{message} {kwargs}"
        self.logger.error(message)
    
    def critical(self, message: str, **kwargs):
        """Log critical message
        
        Args:
            message: Log message
            **kwargs: Additional parameters for structured logging
        """
        if kwargs:
            message = f"{message} {kwargs}"
        self.logger.critical(message)
    
    def exception(self, message: str, **kwargs):
        """Log exception message with traceback
        
        Args:
            message: Log message
            **kwargs: Additional parameters for structured logging
        """
        if kwargs:
            message = f"{message} {kwargs}"
        self.logger.exception(message)


# Global logger instances
_loggers: Dict[str, Logger] = {}


def get_logger(
    name: str = "hos-secsuite",
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    file_level: int = logging.DEBUG
) -> Logger:
    """Get or create a logger instance
    
    Args:
        name: Logger name
        level: Console logging level
        log_file: Log file path
        file_level: File logging level
        
    Returns:
        Logger: Logger instance
    """
    global _loggers
    
    # Return existing logger if already created
    if name in _loggers:
        return _loggers[name]
    
    # Create new logger
    logger = Logger(name, level, log_file, file_level)
    _loggers[name] = logger
    
    return logger


def set_global_log_level(level: int):
    """Set global log level for all loggers
    
    Args:
        level: Logging level
    """
    for logger in _loggers.values():
        for handler in logger.logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setLevel(level)
