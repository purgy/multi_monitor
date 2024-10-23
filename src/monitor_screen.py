from dataclasses import dataclass

import screeninfo


@dataclass
class MonitorScreen:
    monitor: screeninfo.Monitor
    number: int = 0
    # print(screeninfo.get_monitors())
    # [
    #   Monitor(x=5968, y=0, width=3200, height=1800, width_mm=443, height_mm=249, name='DP-2', is_primary=False),
    #   Monitor(x=0, y=0, width=2560, height=2048, width_mm=376, height_mm=301, name='HDMI-0', is_primary=False),
    #   Monitor(x=2560, y=0, width=3408, height=2130, width_mm=344, height_mm=215, name='DP-4', is_primary=True)]
    # ]

    @property
    def x_start(self) -> int:
        return self.monitor.x

    @property
    def y_start(self) -> int:
        return self.monitor.y

    @property
    def x_end(self) -> int:
        return self.monitor.x + self.monitor.width

    @property
    def y_end(self) -> int:
        return self.monitor.y + self.monitor.height

    @property
    def center(self) -> tuple[int, int]:
        return (self.x_start + self.x_end) // 2, (self.y_start + self.y_end) // 2

    def is_contains_point(self, x: int, y: int, padding: int = 0) -> bool:
        return (
            self.x_start + padding <= x <= self.x_end - padding and self.y_start + padding <= y <= self.y_end - padding
        )

    @staticmethod
    def get_all_connected_monitor_screens() -> list["MonitorScreen"]:
        monitors = screeninfo.get_monitors()
        monitor_screens: list[MonitorScreen] = []
        for monitor in monitors:
            monitor_screen = MonitorScreen(monitor=monitor)
            monitor_screens.append(monitor_screen)
        return monitor_screens

    @staticmethod
    def get_current_monitor_index(
        mouse_cursor_position: tuple[int, int], monitor_screens: list["MonitorScreen"]
    ) -> int:
        """Из списка мониторов определяет, на каком из них сейчас курсор мыши"""
        current_monitor_index = 0
        for i, monitor_screen in enumerate(monitor_screens):
            if monitor_screen.is_contains_point(*mouse_cursor_position):
                current_monitor_index = i
                break
        return current_monitor_index

    def get_nearest_edge_position(self, position: tuple[int, int], padding: int = 0) -> tuple[int, int]:
        x, y = position
        x = max(self.x_start + padding, min(self.x_end - padding, x))
        y = max(self.y_start + padding, min(self.y_end - padding, y))
        return x, y

    def get_relative_position(self, position: tuple[int, int]) -> tuple[float, float]:
        relative_x: float = (position[0] - self.x_start) / int(self.monitor.width)
        relative_y: float = (position[1] - self.y_start) / int(self.monitor.height)
        return relative_x, relative_y

    def get_absolute_position(self, relative_position: tuple[float, float]) -> tuple[int, int]:
        absolute_x: int = int(relative_position[0] * int(self.monitor.width) + self.x_start)
        absolute_y: int = int(relative_position[1] * int(self.monitor.height) + self.y_start)
        return absolute_x, absolute_y

    @staticmethod
    def sort_monitor_screens(
        monitor_screens: list["MonitorScreen"], monitor_numbers: dict[str, int]
    ) -> list["MonitorScreen"]:
        # DP-2: 0
        # DP-4: 2
        # HDMI-0: 1
        monitors: list[dict[str, str | int]] = []
        for name, number in monitor_numbers.items():
            monitors.append({"name": name, "number": number})
        monitors.sort(key=lambda x: x["number"])
        monitor_names_sorted = [monitor["name"] for monitor in monitors]
        monitor_names_sorted_dict = {monitor: i for i, monitor in enumerate(monitor_names_sorted)}

        for monitor_screen in monitor_screens:
            monitor_screen.number = monitor_names_sorted_dict[str(monitor_screen.monitor.name)]

        return sorted(monitor_screens, key=lambda x: x.number)
