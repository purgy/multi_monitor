import os
import typing

import yaml

from monitor_screen import MonitorScreen

DEFAULT_HOTKEY_NEXT_MONITOR: str = "<ctrl>+<cmd>+<right>"
DEFAULT_HOTKEY_PREVIOUS_MONITOR: str = "<ctrl>+<cmd>+<left>"
DEFAULT_HOTKEY_LOCK_CURSOR_CURRENT_MONITOR: str = "<ctrl>+<alt>+l"
DEFAULT_HOTKEY_EXIT: str = "<ctrl>+<f12>"
DEFAULT_IS_CROSS_BY_CTRL: bool = True
DEFAULT_MONITOR_NUMBERS: dict[str, dict[str, int]] | None = None
DEFAULT_PADDING: int = 3


# @dataclasses.dataclass
class Config:
    """Class for working with configuration file"""
    def __init__(self, config_file_path: str):
        self.config_file_path = config_file_path
        self.load_config(config_file_path)

    def load_config(self, config_file_path: str) -> None:
        self.hotkey_next_monitor = DEFAULT_HOTKEY_NEXT_MONITOR
        self.hotkey_previous_monitor = DEFAULT_HOTKEY_PREVIOUS_MONITOR
        self.hotkey_lock_cursor_current_monitor = DEFAULT_HOTKEY_LOCK_CURSOR_CURRENT_MONITOR
        self.hotkey_exit = DEFAULT_HOTKEY_EXIT
        self.is_cross_by_ctrl = DEFAULT_IS_CROSS_BY_CTRL
        self.monitor_numbers = DEFAULT_MONITOR_NUMBERS
        self.padding = DEFAULT_PADDING
        self.is_debug = False
        self.is_notifications_enabled = False

        is_config_file_exists: bool = os.path.exists(config_file_path)
        if is_config_file_exists:
            with open(config_file_path, "r") as f:
                config_dict = yaml.load(f, Loader=yaml.SafeLoader)
            self.hotkey_next_monitor = config_dict.get("hotkeys", DEFAULT_HOTKEY_NEXT_MONITOR).get(
                "move mouse cursor to next monitor", DEFAULT_HOTKEY_NEXT_MONITOR
            )
            self.hotkey_previous_monitor = config_dict.get("hotkeys", DEFAULT_HOTKEY_PREVIOUS_MONITOR).get(
                "move mouse cursor to previous monitor", DEFAULT_HOTKEY_PREVIOUS_MONITOR
            )
            self.hotkey_lock_cursor_current_monitor = config_dict.get(
                "hotkeys", DEFAULT_HOTKEY_LOCK_CURSOR_CURRENT_MONITOR
            ).get("lock/unlock mouse cursor on current monitor", DEFAULT_HOTKEY_LOCK_CURSOR_CURRENT_MONITOR)
            self.hotkey_exit = config_dict.get("hotkeys", DEFAULT_HOTKEY_EXIT).get("exit", DEFAULT_HOTKEY_EXIT)
            self.is_cross_by_ctrl = config_dict.get("is cross screen ranges by pressed ctrl key", DEFAULT_IS_CROSS_BY_CTRL)
            self.monitor_numbers = config_dict.get("monitor numbers", DEFAULT_MONITOR_NUMBERS)
            self.padding = int(config_dict.get("padding", DEFAULT_PADDING))
            self.is_debug = bool(config_dict.get("is debug", False))
            self.is_notifications_enabled = bool(config_dict.get("is notifications enabled", False))


    def to_config_dict(self) -> dict[str, typing.Any]:
        return {
            "hotkeys": {
                "move mouse cursor to next monitor": self.hotkey_next_monitor,
                "move mouse cursor to previous monitor": self.hotkey_previous_monitor,
                "lock/unlock mouse cursor on current monitor": self.hotkey_lock_cursor_current_monitor,
                "exit": self.hotkey_exit,
            },
            "is cross screen ranges by pressed ctrl key": self.is_cross_by_ctrl,
            "monitor numbers": self.monitor_numbers,
            "padding": self.padding,
            "is debug": self.is_debug,
            "is notifications enabled": self.is_notifications_enabled,
        }

    @staticmethod
    def get_monitor_numbers_config_name(monitor_screens: list[MonitorScreen]) -> str:
        """
        Constructs a name for monitors configuration based on the list of attached monitors. For example: "DP-2, DP-4, HDMI-0" or "DP-4"
        """
        monitor_names: list[str] = []
        for monitor_screen in monitor_screens:
            monitor_names.append(str(monitor_screen.monitor.name))
        monitor_names.sort()
        monitor_numbers_config_name = ", ".join(monitor_names)
        return monitor_numbers_config_name

    def write_config(self, config_dict: dict[str, typing.Any], config_file_path: str | None = None) -> None:
        if config_file_path is None:
            config_file_path = self.config_file_path
        with open(config_file_path, "w") as f:
            yaml.dump(config_dict, f, default_flow_style=False)
