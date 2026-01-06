import logging
import time


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

    def __init__(self, app_name=None, include_colors=True):
        super().__init__()
        if app_name is None:
            app_name = __name__.split(".")[0]
        self.app_name = app_name
        self.include_colors = include_colors
        self.base_format = "%(asctime)s - {app_name} - %(levelname)s - %(message)s"

    def format(self, record):
        date_format = "%Y-%m-%dT%H:%M:%SZ"
        log_fmt = self.base_format.format(app_name=self.app_name)

        if self.include_colors:
            color = self.COLORS.get(record.levelname, "")
            log_fmt = f"{color}{log_fmt}{self.COLORS['RESET']}"

        formatter = logging.Formatter(log_fmt, datefmt=date_format)
        formatter.converter = time.gmtime
        return formatter.format(record)


def get_logger(name, app_name=None, level=logging.INFO, log_file=None):
    if app_name is None and name is not None:
        app_name = name.split(".")[0]
    logger = logging.getLogger(name)

    logger.handlers.clear()

    logger.setLevel(level)
    logger.propagate = False

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(DefaultFormatter(app_name, include_colors=True))
    logger.addHandler(console_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(DefaultFormatter(app_name, include_colors=False))
        logger.addHandler(file_handler)

    return logger


def get_config_dict(app_name=None, log_file=None):
    if app_name is None:
        app_name = __name__.split(".")[0]
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
