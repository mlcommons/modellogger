import inspect
import logging
import os
import sys
import time
from typing import Any, Dict, Optional


class VariantFormatter(logging.Formatter):
    """This allows us to pass arbitrary arguments to our Formatter class
    without breaking compatibility with the base Formatter class."""

    def __init__(self, *args, **kwargs):
        fmt = kwargs.get("fmt", None)
        datefmt = kwargs.get("datefmt", None)
        style = kwargs.get("style", "%")
        validate = kwargs.get("validate", True)
        defaults = kwargs.get("defaults", None)
        super().__init__(fmt, datefmt, style, validate, defaults=defaults)


class DefaultFormatter(VariantFormatter):
    converter = time.gmtime  # type: ignore
    COLORS = {
        "DEBUG": "\x1b[38;21m",
        "INFO": "\x1b[97m",
        "WARNING": "\x1b[38;5;226m",
        "ERROR": "\x1b[38;5;196m",
        "CRITICAL": "\x1b[31;1m",
        "RESET": "\x1b[0m",
    }
    base_format = "%(asctime)s - {app_name} - %(name)s - %(levelname)s - %(message)s"

    def __init__(self, app_name: str = ".", include_colors: bool = True):
        super().__init__()
        self.app_name = app_name
        self.include_colors = include_colors

    def format(self, record: logging.LogRecord) -> str:
        date_format = "%Y-%m-%dT%H:%M:%SZ"
        log_fmt = self.base_format.format(app_name=self.app_name)

        if self.include_colors:
            color = self.COLORS.get(record.levelname, "")
            log_fmt = f"{color}{log_fmt}{self.COLORS['RESET']}"

        formatter = logging.Formatter(log_fmt, datefmt=date_format)
        formatter.converter = time.gmtime
        return formatter.format(record)


class CallStackFilter(logging.Filter):
    """This filter finds and returns the fully-qualified call stack
    where the logger.debug|info|error (etc) call happened."""

    def filter(self, record: logging.LogRecord) -> bool:
        frame = inspect.currentframe()
        while frame is not None:
            if (
                frame.f_code.co_filename == record.pathname
                and frame.f_lineno == record.lineno
            ):
                chunks = []

                module = os.path.splitext(os.path.basename(record.pathname))[0]
                if module != "<module>":
                    chunks.append(module)

                qualname = frame.f_code.co_qualname
                if qualname != "<module>":
                    chunks.append(qualname)

                record.caller = ".".join(chunks)  # type: ignore[attr-defined]
                break

            frame = frame.f_back
        else:
            record.caller = f"{record.module}.{record.funcName}"  # type: ignore[attr-defined]
        return True


class DebuggingFormatter(DefaultFormatter):
    base_format = "%(asctime)s - {app_name} - %(name)s - %(levelname)s - %(caller)s:%(lineno)d - %(message)s"

    def format(self, record: logging.LogRecord) -> str:
        CallStackFilter().filter(record)
        return super().format(record)


def configure_logging(
    app_name: str = ".",
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    formatter: type[VariantFormatter] = DefaultFormatter,
) -> None:
    """Configures the root logger. Preserves existing handlers (if any).

    NOTE: if you call this function multiple times, you may end up with
    duplicate log messages, since each call adds new handlers to the root logger.

    Args:
        app_name: Name of the application to include in log messages.
        level: Logging level to set.
        log_file: If provided, log to this file instead of stderr.
    """
    logger = logging.getLogger()
    logger.setLevel(level)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter(app_name, include_colors=False))
        logger.addHandler(file_handler)
    else:
        console_handler = logging.StreamHandler(stream=sys.stderr)
        console_handler.setFormatter(formatter(app_name, include_colors=True))
        logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    return logger


def get_config_dict(
    app_name: str = ".",
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    include_colors: bool = False,
) -> Dict[str, Any]:
    config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default_console": {
                "()": f"{__name__}.DefaultFormatter",
                "app_name": app_name,
                "include_colors": include_colors,
            },
            "default_file": {
                "()": f"{__name__}.DefaultFormatter",
                "app_name": app_name,
                "include_colors": include_colors,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default_console",
                "stream": "ext://sys.stdout",
            }
        },
        "root": {"level": level, "handlers": ["console"]},
    }

    if log_file:
        config["handlers"]["file"] = {
            "class": "logging.FileHandler",
            "formatter": "default_file",
            "filename": log_file,
            "mode": "a",
        }
        config["root"]["handlers"].append("file")

    return config
