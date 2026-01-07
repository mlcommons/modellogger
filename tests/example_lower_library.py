from modellogger.log_config import get_logger

logger = get_logger(__name__)


def lower_library_function():
    logger.info(f"info in lower_library_function")
    logger.debug(f"debug in lower_library_function")
