from modellogger.log_config import get_logger

logger = get_logger(__name__)


def lower_library_function():
    logger.info(f"info in {__name__}")
    logger.debug(f"debug in {__name__}")