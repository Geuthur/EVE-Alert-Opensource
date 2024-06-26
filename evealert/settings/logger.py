import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from evealert.managers.settingsmanager import SettingsManager

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


alert_log = logging.getLogger("alert")
alert_log.addHandler(create_fh("alert"))
settings_config = SettingsManager().open_settings()
log_level = settings_config.get("logging")

if log_level:
    try:
        alert_log.setLevel(log_level)
    except Exception as e:
        alert_log.setLevel(logging.ERROR)
        alert_log.error("Wrong Logging Level: %s", e)
else:
    alert_log.setLevel(logging.ERROR)

logging.StreamHandler()
