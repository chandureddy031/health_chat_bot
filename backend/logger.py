import logging
import sys
from datetime import datetime

def get_logger(name: str) -> logging.Logger:
    """
    Create and configure a logger instance
    
    Args:
        name: Name of the logger
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
   
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)
    
   
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger