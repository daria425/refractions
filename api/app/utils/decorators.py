import time
from functools import wraps
from typing import Literal, ParamSpec, TypeVar

from app.utils.logger import logger
from app.utils.response_handlers import ResponseFailure

P = ParamSpec("P")
T = TypeVar("T")


def retry_on_failure(
    max_retries: int = 3, delay: float = 1.0, backoff_exp: float = 2.0
):
    def decorator(func):
        @wraps(func)
        def retry_wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    logger.info(
                        f"{func.__name__} attempt {attempt + 1}/{max_retries + 1}"
                    )
                    return func(*args, **kwargs)

                except Exception as e:
                    last_exception = e
                    logger.warning(
                        f"{func.__name__} attempt {attempt + 1} failed: {str(e)}"
                    )

                    if attempt < max_retries:
                        wait_time = delay * (backoff_exp**attempt)
                        logger.info(
                            f"Retrying {func.__name__} in {wait_time} seconds..."
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error(
                            f"All {func.__name__} attempts failed after {max_retries + 1} tries"
                        )
                        error_message = (
                            f"Function {func.__name__} failed: {str(last_exception)}"
                        )
                        return ResponseFailure(
                            error=error_message, details=str(last_exception)
                        )

        return retry_wrapper

    return decorator