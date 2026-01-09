from modellogger.log_config import get_logger
from tests.example_lower_library import lower_library_function

logger = get_logger(__name__)


def top_library_function():
    logger.info(f"info in top_library_function")
    logger.debug(f"debug in top_library_function")
    lower_library_function()
