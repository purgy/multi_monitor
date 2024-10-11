from notifypy import Notify


class Notification:
    @staticmethod
    def send(message: str, title: str = "Multi Monitor") -> None:
        notification = Notify()
        notification.title = title
        notification.message = message
        notification.send(block=False)
