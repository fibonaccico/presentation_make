import logging
import os
from pathlib import Path


def get_logger() -> logging.Logger:
    def log_file(file_path: str = "./fibo_log.log"):
        if not os.path.exists(file_path):
            Path(file_path).touch()
        return file_path

    logger = logging.getLogger("consumer")
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.setLevel(logging.DEBUG)
    py_handler = logging.FileHandler(log_file(), mode="a")
    py_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
    py_handler.setFormatter(py_formatter)
    logger.addHandler(py_handler)

    return logger