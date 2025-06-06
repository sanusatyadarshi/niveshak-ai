"""
Logging configuration and utilities for NiveshakAI.

This module provides:
- Centralized logging configuration
- Logger creation with proper formatting
- Log level management
- File and console logging setup
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional
import yaml
from datetime import datetime

# Default logging configuration
DEFAULT_LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S',
    'file': 'logs/niveshak.log',
    'max_file_size': '10MB',
    'backup_count': 5
}


def setup_logging(config_path: str = "config/settings.yaml") -> None:
    """
    Set up logging configuration for the application.
    
    Args:
        config_path: Path to configuration file
    """
    # Load configuration
    log_config = DEFAULT_LOG_CONFIG.copy()
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                if 'logging' in config:
                    log_config.update(config['logging'])
    except Exception as e:
        print(f"Warning: Could not load logging config from {config_path}: {e}")
    
    # Create logs directory if it doesn't exist
    log_file = log_config['file']
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Parse log level
    log_level = getattr(logging, log_config['level'].upper(), logging.INFO)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        fmt=log_config['format'],
        datefmt=log_config['date_format']
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    try:
        max_bytes = _parse_size(log_config['max_file_size'])
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=max_bytes,
            backupCount=log_config['backup_count'],
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not set up file logging: {e}")
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info("Logging initialized for NiveshakAI")
    logger.info(f"Log level: {log_config['level']}")
    logger.info(f"Log file: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def _parse_size(size_str: str) -> int:
    """
    Parse size string (e.g., '10MB') to bytes.
    
    Args:
        size_str: Size string with unit
        
    Returns:
        Size in bytes
    """
    size_str = size_str.upper().strip()
    
    if size_str.endswith('KB'):
        return int(size_str[:-2]) * 1024
    elif size_str.endswith('MB'):
        return int(size_str[:-2]) * 1024 * 1024
    elif size_str.endswith('GB'):
        return int(size_str[:-2]) * 1024 * 1024 * 1024
    else:
        # Assume bytes
        return int(size_str)


def log_function_call(func):
    """
    Decorator to log function calls with parameters and execution time.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        
        # Log function entry
        func_name = f"{func.__module__}.{func.__name__}"
        logger.debug(f"Entering {func_name}")
        
        start_time = datetime.now()
        
        try:
            # Execute function
            result = func(*args, **kwargs)
            
            # Log successful completion
            duration = (datetime.now() - start_time).total_seconds()
            logger.debug(f"Completed {func_name} in {duration:.3f}s")
            
            return result
            
        except Exception as e:
            # Log exception
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"Exception in {func_name} after {duration:.3f}s: {str(e)}")
            raise
    
    return wrapper


def log_execution_time(logger: logging.Logger, operation: str):
    """
    Context manager to log execution time of operations.
    
    Usage:
        with log_execution_time(logger, "data processing"):
            # Your code here
            process_data()
    
    Args:
        logger: Logger instance
        operation: Description of the operation
    """
    class ExecutionTimer:
        def __init__(self, logger, operation):
            self.logger = logger
            self.operation = operation
            self.start_time = None
        
        def __enter__(self):
            self.start_time = datetime.now()
            self.logger.info(f"Starting {self.operation}")
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            duration = (datetime.now() - self.start_time).total_seconds()
            
            if exc_type is None:
                self.logger.info(f"Completed {self.operation} in {duration:.3f}s")
            else:
                self.logger.error(f"Failed {self.operation} after {duration:.3f}s: {exc_val}")
    
    return ExecutionTimer(logger, operation)


def configure_third_party_loggers():
    """Configure logging levels for third-party libraries."""
    # Reduce verbosity of common third-party libraries
    third_party_loggers = [
        'urllib3',
        'requests',
        'openai',
        'langchain',
        'qdrant_client',
        'weaviate',
        'matplotlib',
        'pandas'
    ]
    
    for logger_name in third_party_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def create_performance_logger() -> logging.Logger:
    """
    Create a dedicated logger for performance metrics.
    
    Returns:
        Performance logger instance
    """
    perf_logger = logging.getLogger('niveshak.performance')
    
    # Create dedicated handler for performance logs
    if not perf_logger.handlers:
        perf_file = Path('logs/performance.log')
        perf_file.parent.mkdir(parents=True, exist_ok=True)
        
        handler = logging.handlers.RotatingFileHandler(
            filename=perf_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=3
        )
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        perf_logger.addHandler(handler)
        perf_logger.setLevel(logging.INFO)
    
    return perf_logger


def log_memory_usage(logger: logging.Logger, context: str = ""):
    """
    Log current memory usage.
    
    Args:
        logger: Logger instance
        context: Context description for the log
    """
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        
        logger.info(f"Memory usage {context}: {memory_mb:.1f} MB")
        
    except ImportError:
        logger.debug("psutil not available for memory monitoring")
    except Exception as e:
        logger.debug(f"Could not log memory usage: {e}")


def log_system_info(logger: logging.Logger):
    """
    Log system information for debugging.
    
    Args:
        logger: Logger instance
    """
    try:
        import platform
        import sys
        
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Platform: {platform.platform()}")
        logger.info(f"Architecture: {platform.architecture()}")
        logger.info(f"Processor: {platform.processor()}")
        
        try:
            import psutil
            logger.info(f"CPU cores: {psutil.cpu_count()}")
            memory = psutil.virtual_memory()
            logger.info(f"Total memory: {memory.total / 1024 / 1024 / 1024:.1f} GB")
        except ImportError:
            pass
            
    except Exception as e:
        logger.debug(f"Could not log system info: {e}")


# Initialize logging when module is imported
if __name__ != "__main__":
    try:
        setup_logging()
        configure_third_party_loggers()
    except Exception as e:
        print(f"Warning: Could not initialize logging: {e}")


# Example usage
if __name__ == "__main__":
    # Test logging setup
    setup_logging()
    
    logger = get_logger(__name__)
    logger.info("Testing logging configuration")
    logger.debug("Debug message")
    logger.warning("Warning message")
    logger.error("Error message")
    
    # Test performance logging
    perf_logger = create_performance_logger()
    perf_logger.info("Performance test message")
    
    # Test system info logging
    log_system_info(logger)
    log_memory_usage(logger, "test")
