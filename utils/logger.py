import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path("logs")


def get_logger(name: str, filename: str) -> logging.Logger:
    LOG_DIR.mkdir(exist_ok=True)
    logger = logging.getLogger(name)
    if logger.handlers:          # évite les doublons si on l'appelle 2 fois
        return logger
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter(
        fmt='%(asctime)s|%(name)s|%(levelname)s|%(message)s',
        datefmt='%d/%m/%Y %H:%M:%S')
    handler = RotatingFileHandler(
        LOG_DIR / filename, maxBytes=1_000_000, backupCount=3, encoding='utf-8')
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    return logger