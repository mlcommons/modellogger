import logging
import sys
import time
from logging import INFO


class DefaultFormatter(logging.Formatter):
    converter = time.gmtime  # type: ignore
    COLORS = {
        "DEBUG": "\x1b[38;21m",
        "INFO": "\x1b[97m",
        "WARNING": "\x1b[38;5;226m",
        "ERROR": "\x1b[38;5;196m",
        "CRITICAL": "\x1b[31;1m",
        "RESET": "\x1b[0m",
    }

    def __init__(self, app_name=".", include_colors=True):
        super().__init__()
        self.app_name = app_name
        self.include_colors = include_colors
        self.base_format = (
            "%(asctime)s - {app_name} - %(name)s - %(levelname)s - %(message)s"
        )

    def format(self, record):
        date_format = "%Y-%m-%dT%H:%M:%SZ"
        log_fmt = self.base_format.format(app_name=self.app_name)

        if self.include_colors:
            color = self.COLORS.get(record.levelname, "")
            log_fmt = f"{color}{log_fmt}{self.COLORS['RESET']}"

        formatter = logging.Formatter(log_fmt, datefmt=date_format)
        formatter.converter = time.gmtime
        return formatter.format(record)

def configure_logging(app_name=".", level=INFO, log_file=None):
    logger = logging.getLogger()
    if level:
        logger.setLevel(level)

    logger.handlers.clear()

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(DefaultFormatter(app_name, include_colors=False))
        logger.addHandler(file_handler)
    else:
        console_handler = logging.StreamHandler(stream=sys.stderr)
        console_handler.setLevel(level)
        console_handler.setFormatter(DefaultFormatter(app_name, include_colors=True))
        logger.addHandler(console_handler)


def get_logger(name):
    logger = logging.getLogger(name)
    return logger


def get_config_dict(app_name=".", log_file=None):
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default_console": {
                "()": f"{__name__}.DefaultFormatter",
                "app_name": app_name,
                "include_colors": True,
            },
            "default_file": {
                "()": f"{__name__}.DefaultFormatter",
                "app_name": app_name,
                "include_colors": False,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "default_console",
                "stream": "ext://sys.stdout",
            }
        },
        "root": {"level": "DEBUG", "handlers": ["console"]},
    }

    if log_file:
        config["handlers"]["file"] = {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "default_file",
            "filename": log_file,
            "mode": "a",
        }
        config["root"]["handlers"].append("file")

    return config
