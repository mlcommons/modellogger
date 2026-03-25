import logging

import airrlogger.log_config as log_config
from airrlogger.log_config import (
    DebuggingFormatter,
    DefaultFormatter,
    _redact,
    configure_logging,
    get_config_dict,
    get_logger,
    redacted,
)


def test_default_formatter_no_colors():
    formatter = DefaultFormatter(app_name="test_app", include_colors=False)
    record = logging.LogRecord(
        "name", logging.INFO, "pathname", 123, "message", [], None
    )
    formatted = formatter.format(record)
    assert "test_app" in formatted
    assert "INFO" in formatted
    assert "message" in formatted
    assert "\x1b[" not in formatted


def test_default_formatter_with_colors():
    formatter = DefaultFormatter(app_name="test_app", include_colors=True)
    record = logging.LogRecord(
        "name", logging.WARNING, "pathname", 123, "message", [], None
    )
    formatted = formatter.format(record)
    assert "test_app" in formatted
    assert "WARNING" in formatted
    assert "message" in formatted
    assert "\x1b[38;5;226m" in formatted
    assert "\x1b[0m" in formatted


def test_default_formatter_timestamp_utc():
    formatter = DefaultFormatter(include_colors=False)
    record = logging.LogRecord(
        "name", logging.INFO, "pathname", 123, "message", [], None
    )
    # this is 2021-01-01 00:00:00 UTC
    record.created = 1609459200.0
    formatted = formatter.format(record)
    assert "2021-01-01T00:00:00Z" in formatted


def test_debugging_formatter():
    formatter = DebuggingFormatter(app_name="test_app", include_colors=False)
    record = logging.LogRecord(
        "name",
        logging.WARNING,
        "pathname",
        123,
        "message",
        [],
        None,
        "test_debugging_formatter",
    )
    # this is 2021-01-01 00:00:00 UTC
    record.created = 1609459200.0
    formatted = formatter.format(record)
    assert "test_app" in formatted
    assert "WARNING" in formatted
    assert "message" in formatted
    assert "pathname.test_debugging_formatter:123" in formatted
    assert formatted.startswith("2021-01-01T00:00:00Z")


def test_configure_logging():
    configure_logging("an_app")
    root_logger = logging.getLogger()
    assert root_logger.name == "root"
    assert root_logger.level == logging.INFO
    assert isinstance(root_logger.handlers[-1], logging.StreamHandler)


def test_configure_logging_is_idempotent(tmp_path):
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    starting_num_handlers = len(root_logger.handlers)

    # stream handlers
    configure_logging("an_app")
    assert len(root_logger.handlers) == starting_num_handlers + 1
    configure_logging("an_app")
    configure_logging("an_app")
    assert len(root_logger.handlers) == starting_num_handlers + 1
    # add another stream handler with a different formatter
    configure_logging("an_app", formatter=DebuggingFormatter)
    assert len(root_logger.handlers) == starting_num_handlers + 2

    # file handlers
    log_file = tmp_path / "test.log"
    configure_logging("an_app", log_file=log_file)
    assert len(root_logger.handlers) == starting_num_handlers + 3
    configure_logging("an_app", log_file=log_file)
    configure_logging("an_app", log_file=log_file)
    assert len(root_logger.handlers) == starting_num_handlers + 3
    # add another file handler with a different formatter
    configure_logging("an_app", log_file=log_file, formatter=DebuggingFormatter)
    assert len(root_logger.handlers) == starting_num_handlers + 4
    configure_logging("an_app", log_file=log_file, formatter=DebuggingFormatter)
    assert len(root_logger.handlers) == starting_num_handlers + 4
    new_log_file = tmp_path / "other_test.log"
    configure_logging("an_app", log_file=new_log_file, formatter=DebuggingFormatter)
    assert len(root_logger.handlers) == starting_num_handlers + 5


def test_configure_logging_with_file(tmp_path):
    log_file = tmp_path / "test.log"
    configure_logging("an_app", log_file=log_file)

    root_logger = logging.getLogger()
    assert root_logger.name == "root"
    assert root_logger.level == logging.INFO
    assert isinstance(root_logger.handlers[-1], logging.FileHandler)


def test_get_logger_basic():
    logger = get_logger("test_logger")
    assert logger.name == "test_logger"


def test_get_config_dict_basic():
    config = get_config_dict(app_name="test_app")
    assert config["version"] == 1
    assert "default_console" in config["formatters"]
    console_formatter = config["formatters"]["default_console"]
    assert console_formatter["app_name"] == "test_app"
    assert console_formatter["include_colors"] is False
    assert "root" in config
    assert "level" in config["root"]
    assert config["root"]["level"] == logging.INFO


def test_get_config_dict_with_include_colors():
    config = get_config_dict(app_name="test_app", include_colors=True)
    assert config["version"] == 1
    assert "default_console" in config["formatters"]
    console_formatter = config["formatters"]["default_console"]
    assert console_formatter["app_name"] == "test_app"
    assert console_formatter["include_colors"] is True
    assert "root" in config
    assert "level" in config["root"]
    assert config["root"]["level"] == logging.INFO


def test_get_config_dict_with_debug_file():
    config = get_config_dict(
        app_name="test_app", level=logging.WARN, log_file="/tmp/app.log"
    )
    assert "file" in config["handlers"]
    file_handler = config["handlers"]["file"]
    assert file_handler["filename"] == "/tmp/app.log"
    assert "default_file" in config["formatters"]
    file_formatter = config["formatters"]["default_file"]
    assert file_formatter["include_colors"] is False
    assert "root" in config
    assert "level" in config["root"]
    assert config["root"]["level"] == logging.WARN


def test_default_formatter_app_name_default(monkeypatch):
    # Patch the __name__ attribute using the imported module
    monkeypatch.setattr(log_config, "__name__", "mypackage.submodule")
    formatter = DefaultFormatter()
    assert formatter.app_name == "."

    monkeypatch.setattr(log_config, "__name__", "mymodule")
    formatter = DefaultFormatter()
    assert formatter.app_name == "."


def test__redact():
    assert _redact("a") == "xx"
    assert _redact("ab") == "xx"
    assert _redact("abc") == "a...c"
    assert _redact("abcd") == "a...d"
    assert _redact("abcde") == "ab...de"
    assert _redact("abcdef") == "ab...ef"
    assert _redact("abcdefg") == "ab...fg"
    assert _redact("abcdefgh") == "ab...gh"


def test_redacted():
    assert redacted("a") == "xx"
    assert redacted("ab") == "xx"
    assert redacted("abc") == "a...c"
    assert redacted("abcd") == "a...d"
    assert redacted("abcde") == "ab...de"
    assert redacted("abcdef") == "ab...ef"
    assert redacted("abcdefg") == "ab...fg"
    assert redacted("abcdefgh") == "ab...gh"

    assert redacted({"a": "abcdefgh", "b": 1}) == {"a": "ab...gh", "b": 1}
    assert redacted({"a": "abcdefgh", "b": "ijklmnop"}) == {
        "a": "ab...gh",
        "b": "ij...op",
    }
    assert redacted(["a", "b", "cdefgh", 1]) == ["xx", "xx", "cd...gh", 1]
    assert redacted(("a", "b", "cdefgh", 1)) == ("xx", "xx", "cd...gh", 1)
    assert redacted(("a", "b", "cdefgh", {})) == ("xx", "xx", "cd...gh", {})
    assert redacted(("a", "b", "cdefgh", {"thing": "abcdefghijkl"})) == (
        "xx",
        "xx",
        "cd...gh",
        {"thing": "ab...kl"},
    )
