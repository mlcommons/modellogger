# These tests ensure that this logger remains backward compatible with the standard Python logger and should only be altered with that goal in mind.
# Mostly, these tests just try to do a thing and should not fail.


import logging

import pytest

from modellogger.log_config import DefaultFormatter, get_logger


def test_standard_logging_levels():
    logger = get_logger("test")

    # Should raise no errors
    logger.debug("debug message")
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")
    logger.critical("critical message")


def test_exception_logging():
    logger = get_logger("test")
    try:
        raise ValueError("test error")
    except ValueError:
        logger.exception("exception occurred")


def test_log_record_attributes():
    logger = get_logger("test")
    try:
        logger.info("test message", extra={"custom_field": "value"})
    except Exception as e:
        pytest.fail(f"Standard logging call failed: {e}")

    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = DefaultFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.info("formatted message")


def test_logger_adapter_compatibility():
    logger = get_logger("test")
    adapter = logging.LoggerAdapter(logger, {"context": "value"})
    adapter.info("adapted message")
