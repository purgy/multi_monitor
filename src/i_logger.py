import abc
import typing


class ILogger(abc.ABC):
    @abc.abstractmethod
    def debug(self, message: str) -> None:
        pass

    @abc.abstractmethod
    def info(self, message: str) -> None:
        pass

    @abc.abstractmethod
    def warning(self, message: str) -> None:
        pass

    @abc.abstractmethod
    def error(self, message: str) -> None:
        pass

    @abc.abstractmethod
    def exception(self, message: str) -> None:
        pass

    @abc.abstractmethod
    def bind_logger(self, **kwargs: typing.Any):
        """
        Binds a variable for the logger so it outputs in all subsequent calls
        """
        pass
