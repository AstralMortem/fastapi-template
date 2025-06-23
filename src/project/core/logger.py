import logging
from logging.handlers import RotatingFileHandler
import sys
import colorlog
from project.config import settings
from pathlib import Path

def setup_logger(
    name: str = "fastapi_app", log_file: str | Path = "app.log"
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    color_formatter = colorlog.ColoredFormatter(
        fmt="%(log_color)s[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )

    file_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s", "%Y-%m-%d %H:%M:%S"
    )

    # Console with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(color_formatter)

    # File handler without color
    file_handler = RotatingFileHandler(log_file, maxBytes=5_000_000, backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    if not logger.handlers:
        if settings.LOGGER_OUT_IN_CONSOLE:
            logger.addHandler(console_handler)
        if settings.LOGGER_OUT_IN_FILE:
            logger.addHandler(file_handler)

    logger.propagate = False
    return logger


log = setup_logger(settings.LOGGER_NAME, settings.LOGGER_LOG_FILE_PATH)
