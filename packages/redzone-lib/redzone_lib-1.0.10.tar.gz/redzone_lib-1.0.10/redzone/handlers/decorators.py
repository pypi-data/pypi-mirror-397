import asyncio
import traceback
from functools import wraps
from typing import Callable

import sentry_sdk

from ..utils.logger import logger


def aws_handler(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return asyncio.run(func(*args, **kwargs))
        except Exception as e:
            sentry_sdk.capture_exception(e)
            sentry_sdk.flush(2)
            logger.debug("internal server error", priority=1)
            logger.debug("{}: {}".format(e.__class__.__name__, e))
            logger.debug(traceback.format_exc())
            raise

    return wrapper
