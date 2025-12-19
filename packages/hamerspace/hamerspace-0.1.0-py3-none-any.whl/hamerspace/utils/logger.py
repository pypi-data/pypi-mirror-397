"""
Logging configuration for Hamerspace.
"""

import logging
import sys
from typing import Optional


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Get a configured logger.
    
    Args:
        name: Logger name (typically __name__)
        level: Logging level (default: INFO)
    
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Create handler
        handler = logging.StreamHandler(sys.stdout)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(handler)
        
        # Set level
        if level is None:
            level = logging.INFO
        logger.setLevel(level)
    
    return logger


def set_log_level(level: int) -> None:
    """
    Set log level for all Hamerspace loggers.
    
    Args:
        level: Logging level (logging.DEBUG, logging.INFO, etc.)
    """
    logging.getLogger('hamerspace').setLevel(level)
