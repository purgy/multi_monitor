import notifypy

from i_notification import INotification


class Notification(INotification):
    def __init__(self, is_notifications_enabled: bool = True) -> None:
        super().__init__()
        self.is_notifications_enabled = is_notifications_enabled

    def send(
        self,
        message: str,
        title: str = "multi_monitor",
    ) -> None:
        if not self.is_notifications_enabled:
            return
        notification = notifypy.Notify(
            default_notification_title="multi_monitor",
            default_notification_application_name="multi_monitor",
            enable_logging=False,
        )
        notification.title = title
        notification.message = message
        notification.send(block=False)
