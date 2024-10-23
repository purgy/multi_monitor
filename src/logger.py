import structlog


class Logger:
    @staticmethod
    def get_logger(name: str):
        """
        Retrieves a logger for use as an argument, taking the module name __name__ as input.
        """
        logger = structlog.get_logger(name)
        return logger

    @staticmethod
    def bind_logger(**kwargs):
        """
        Binds a variable for the logger so it outputs in all subsequent calls
        """
        return structlog.contextvars.bind_contextvars(**kwargs)
