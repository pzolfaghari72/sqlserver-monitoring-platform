import logging
import sys

from collector.core.config import get_settings


def setup_logger(name: str) -> logging.Logger:
    settings = get_settings()

    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
            )
        )
        logger.addHandler(handler)

    logger.setLevel(settings.LOG_LEVEL)
    logger.propagate = False

    return logger