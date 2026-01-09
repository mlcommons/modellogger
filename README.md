# Modellogger

The modellogger package provides a standardized logging configuration for AIRR applications.

## Usage

Install in a poetry project: `poetry add git+https://github.com/mlcommons/modellogger.git`

Near the top of any file where you want to log, do something like:

```python
from modellogger.log_config import get_logger
logger = get_logger(__name__)
```

Then as early as possible in your program's startup, tell it how to
handle the logging:

```python
import logging
from modellogger.log_config import configure_logging

configure_logging(app_name="myapp", level=logging.INFO)
```


You can then log like this
```python
    logger.info("some info logging")
```

The default output looks like this:

```
2026-01-09T21:14:13Z - myapp - __main__ - INFO - some info logging
```


### DefaultFormatter

A class that formats log messages with UTC timestamps and optional ANSI color codes for console output.

### configure_logging

A function that configure the root logger with console and optional file output.

```
from modellogger.log_config import configure_logging

logger = configure_logging(app_name="modelrunner-api", file="./app.log", level=logging.DEBUG)
```

### get_config_dict

Generates logging configuration dictionaries for use with logging.config.dictConfig. By default, the app name is derived from the package name, but that can be overridden.

This is particularly useful for FastAPI applications, which can adopt this logger by using something like:

```
run(app, host="0.0.0.0", port=port, log_config=get_config_dict(app_name="modelrunner-api"))
```

## Example Output

`2025-12-19T14:10:24Z - modelrunner-api - INFO - 127.0.0.1:36054 - "GET /health HTTP/1.1" 200`
