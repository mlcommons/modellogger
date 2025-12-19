# Modellogger

The modellogger package provides a standardized logging configuration for AIRR applications.

## DefaultFormatter

A class that formats log messages with UTC timestamps and optional ANSI color codes for console output.

## get_logger

A function that creates configured loggers with console and optional file output.

```
from modellogger.log_config import get_logger

logger = get_logger(__name__, app_name="modelrunner-api")

```

## get_config_dict

Generates logging configuration dictionaries for use with logging.config.dictConfig. By default, the app name is derived from the package name, but that can be overridden.

This is particularly useful for FastAPI applications, which can adopt this logger by using something like:

```
run(app, host="0.0.0.0", port=port, log_config=get_config_dict(app_name="modelrunner-api"))
```

## Example Output

`2025-12-19T14:10:24Z - modelrunner-api - INFO - 127.0.0.1:36054 - "GET /health HTTP/1.1" 200`
