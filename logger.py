import structlog


class Logger:
    @staticmethod
    def get_logger(name: str):
        """
        Получает логгер для использования
        в качестве аргумента принимает имя модуля __name__
        """
        logger = structlog.get_logger(name)
        return logger

    @staticmethod
    def bind_logger(**kwargs):
        """
        Закрепляет переменную для логгера, чтобы она выводилась во всех последующих вызовах
        """
        return structlog.contextvars.bind_contextvars(**kwargs)
