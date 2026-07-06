import sys
from loguru import logger
from app.core.config import settings, LogLevel


logger.remove()


# 1. Console Handler (DEBUG level)
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG",
    colorize=True,
)

# 2. File Handler (with rotation)
log_file = settings.logging.directory / "keel-backend.log"
logger.add(
    log_file,
    rotation=settings.logging.rotation,
    retention=settings.logging.retention,
    level=settings.logging.level.name,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    enqueue=settings.logging.enqueue,
    backtrace=settings.logging.backtrace,
    serialize=True,
)


# 3. Error specific File Handler
error_log_file = settings.logging.directory / "error-keel-backend.log"
logger.add(
    error_log_file,
    rotation=settings.logging.rotation,
    retention=settings.logging.retention,
    level=LogLevel.ERROR,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    enqueue=settings.logging.enqueue,
    backtrace=settings.logging.backtrace,
    serialize=True,
)

# 4. Critical specific File Handler
error_log_file = settings.logging.directory / "error-keel-backend.log"
logger.add(
    error_log_file,
    rotation=settings.logging.rotation,
    retention=settings.logging.retention,
    level=LogLevel.CRITICAL,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    enqueue=settings.logging.enqueue,
    backtrace=settings.logging.backtrace,
    serialize=True,
)

__all__ = ["logger"]
