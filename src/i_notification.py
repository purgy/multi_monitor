import abc


class INotification(abc.ABC):
    @abc.abstractmethod
    def send(
        self,
        message: str,
        title: str = "multi_monitor",
    ) -> None:
        pass
