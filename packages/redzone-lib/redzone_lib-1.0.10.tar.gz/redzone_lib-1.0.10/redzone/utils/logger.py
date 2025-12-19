import logging

from microgue.loggers.logger import Logger as _Logger

from ..settings import PROJECT_NAME


class Logger(_Logger):
    __instance = None
    max_log_length = 1000

    def log(self, message, priority=None, level=logging.DEBUG):
        message = str(message)
        if len(message) > self.max_log_length:
            message = message[:self.max_log_length] + "... (truncated)"  # fmt: skip
        super().log(message, priority, level)


logger = Logger(PROJECT_NAME)
