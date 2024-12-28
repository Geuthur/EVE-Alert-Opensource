import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

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


def setup_logger(name: str, level: str = "info"):
    """Create a logger with the given name and level."""

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(create_fh(name))
    return logger


# Create loggers
main_log = setup_logger("main", "INFO")
test_log = setup_logger("test", "INFO")
alert_log = setup_logger("alert", "INFO")
menu_log = setup_logger("menu", "INFO")
tools_log = setup_logger("tools", "INFO")

logging.StreamHandler()
