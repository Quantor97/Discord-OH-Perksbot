import os
import logging
from logging.config import dictConfig

current_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(current_dir, "../logs")
db_dir = os.path.join(current_dir, "../db")

os.makedirs(log_dir, exist_ok=True)
os.makedirs(db_dir, exist_ok=True)

log_file_path = os.path.join(log_dir, "bot.log")

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)-10s - %(asctime)s - %(module)s: %(message)s",
        },
        "default": {
            "format": "%(levelname)-10s - %(name)s: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "console2": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "class": "logging.FileHandler",
            "formatter": "verbose",
            "level": "DEBUG",
            "filename": log_file_path,
            "mode": "w",
        },
    },
    "loggers": {
        "scraper": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "database": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "bot": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "discord": {
            "handlers": ["console2", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

dictConfig(LOGGING_CONFIG)