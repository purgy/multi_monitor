import logging

import structlog

from i_logger import ILogger


class Logger(ILogger):

    def __init__(self, is_debug: bool, name: str) -> None:
        self.is_debug = is_debug
        if self.is_debug:
            structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG))
        else:
            structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(logging.INFO))
        logger = structlog.get_logger(name)
        self.logger = logger

    def debug(self, message: str):
        return self.logger.debug(message)

    def info(self, message: str):
        return self.logger.info(message)

    def warning(self, message: str):
        return self.logger.warning(message)

    def error(self, message: str):
        return self.logger.error(message)

    def exception(self, message: str):
        return self.logger.exception(message)

    def bind_logger(self, **kwargs):
        """
        Binds a variable for the logger so it outputs in all subsequent calls
        """
        structlog.contextvars.bind_contextvars(**kwargs)
