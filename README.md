# airrlogger

The airrlogger package provides a standardized logging configuration for AIRR applications.

## Usage

Install in a poetry project: `poetry add airrlogger`

Near the top of any module where you want to log, do something like:

```python
from airrlogger.log_config import get_logger
logger = get_logger(__name__)
```

Then as early as possible in your program's startup, tell it how to handle the logging:

```python
import logging
from airrlogger.log_config import configure_logging

configure_logging(app_name="myapp", level=logging.INFO)
```

You can then log like this:

```python
    logger.info("some info logging")
```

The default output looks like this:

```
2026-01-09T21:14:13Z - myapp - __main__ - INFO - some info logging
```

### DefaultFormatter

A class that formats log messages with UTC timestamps and optional ANSI color codes for console output.

### DebuggingFormatter

A class that formats log messages mostly like `DefaultFormatter`, adding the fully-qualified scope and lined number
where the logging event happens.

To use it:

```python
import logging

from log_config import DebuggingFormatter, configure_logging, get_logger
logger = get_logger("my app")
configure_logging("test_module", logging.DEBUG, formatter=DebuggingFormatter)
```

The output looks like this:

```
2026-03-24T20:43:13Z - test_module - my app - ERROR - test:8 - calling from top-level scope before everything else
2026-03-24T20:43:13Z - test_module - my app - ERROR - test:25 - calling from main block in top-level scope
2026-03-24T20:43:13Z - test_module - my app - ERROR - test.MyClass.my_method:13 - calling from my_method
2026-03-24T20:43:13Z - test_module - my app - ERROR - test.MyClass.my_static_method:17 - calling from my_static_method
```

This formatter is independent of the log level. You can use it even if your log level is not `logging.DEBUG`.

There is some performance overhead with this method you should keep in mind in a production environment.

### configure_logging

A function that configure the root logger with console and optional file output. You can call it multiple times
with different loggers or formatters and they will be added to the root logger's log handlers.

```python
from airrlogger.log_config import configure_logging

logger = configure_logging(app_name="modelrunner-api", file="./app.log", level=logging.DEBUG)
```

### get_config_dict

Generates logging configuration dictionaries for use with `logging.config.dictConfig`. By default, the app name
is derived from the package name, but that can be overridden.

This is particularly useful for FastAPI applications, which can adopt this logger by using something like:

```python
run(app, host="0.0.0.0", port=port, log_config=get_config_dict(app_name="modelrunner-api"))
```

## Example Output

`2025-12-19T14:10:24Z - modelrunner-api - INFO - 127.0.0.1:36054 - "GET /health HTTP/1.1" 200`
