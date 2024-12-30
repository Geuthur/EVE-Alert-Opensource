import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from evealert.settings.helper import get_resource_path

# Logging
LOG_PATH = Path("logs")
LOG_PATH.mkdir(exist_ok=True)

LOG_FORMAT = logging.Formatter(
    "%(asctime)s %(levelname)s %(module)s %(funcName)s %(lineno)d: %(message)s",
    datefmt="[%Y-%m-%d %H:%M:%S]",
)


def create_fh(name: str):
    """Create a logging filehandler based on given file path."""

    fh = RotatingFileHandler(
        filename=Path(LOG_PATH, f"{name}.log"),
        encoding="utf-8",
        mode="a",
    )
    fh.setFormatter(LOG_FORMAT)
    return fh


def setup_logger(name: str, level: str = None):
    """Create a logger with the given name and level."""
    config_path = get_resource_path("client.json")

    try:
        with open(config_path, encoding="utf-8") as config_file:
            settings = json.load(config_file)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Logger System: Error loading settings file. Use default settings.")
        level = "INFO"

    if level is None:
        level = settings.get("log_level", "INFO")

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(create_fh(name))
    return logger


# Create loggers
main_log = setup_logger("main")

logging.StreamHandler()
