import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def get_logger() -> logging.Logger:
    def log_file(file_path: str = "./log/fibo_maker.log"):
        if not os.path.exists(file_path):
            Path(file_path).touch()
        return file_path

    logger = logging.getLogger("consumer")
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.setLevel(logging.DEBUG)
    log_file_path = log_file()
    rotating_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=10 * 1024 * 1024,
        backupCount=10
    )
    py_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
    rotating_handler.setFormatter(py_formatter)
    logger.addHandler(rotating_handler)

    return logger