import dataclasses
import os
import typing

import yaml

from logger import Logger
from monitor_screen import MonitorScreen

logger = Logger.get_logger(__name__)

DEFAULT_HOTKEY_NEXT_MONITOR: str = "<ctrl>+<cmd>+<right>"
DEFAULT_HOTKEY_PREVIOUS_MONITOR: str = "<ctrl>+<cmd>+<left>"
DEFAULT_HOTKEY_LOCK_CURSOR_CURRENT_MONITOR: str = "<ctrl>+<alt>+l"
DEFAULT_HOTKEY_EXIT: str = "<ctrl>+f12"
DEFAULT_IS_CROSS_BY_CTRL: bool = True
DEFAULT_MONITOR_NUMBERS: dict[str, dict[str, int]] | None = None
DEFAULT_PADDING: int = 3


@dataclasses.dataclass
class Config:
    """Class for working with configuration file"""
    hotkey_next_monitor: str = DEFAULT_HOTKEY_NEXT_MONITOR
    hotkey_previous_monitor: str = DEFAULT_HOTKEY_PREVIOUS_MONITOR
    hotkey_lock_cursor_current_monitor: str = DEFAULT_HOTKEY_LOCK_CURSOR_CURRENT_MONITOR
    hotkey_exit: str = DEFAULT_HOTKEY_EXIT
    is_cross_by_ctrl: bool = DEFAULT_IS_CROSS_BY_CTRL
    monitor_numbers: dict[str, dict[str, int]] | None = DEFAULT_MONITOR_NUMBERS
    padding: int = DEFAULT_PADDING

    @staticmethod
    def load_config(config_file: str | None) -> "Config":
        if config_file is None or not os.path.isfile(config_file):
            return Config()

        with open(config_file, "r") as f:
            config_dict = yaml.load(f, Loader=yaml.SafeLoader)
        logger.debug(f"config_dict: {config_dict}")
        return Config(
            hotkey_next_monitor=config_dict.get("hotkeys", DEFAULT_HOTKEY_NEXT_MONITOR).get(
                "move mouse cursor to next monitor", DEFAULT_HOTKEY_NEXT_MONITOR
            ),
            hotkey_previous_monitor=config_dict.get("hotkeys", DEFAULT_HOTKEY_PREVIOUS_MONITOR).get(
                "move mouse cursor to previous monitor", DEFAULT_HOTKEY_PREVIOUS_MONITOR
            ),
            hotkey_lock_cursor_current_monitor=config_dict.get(
                "hotkeys", DEFAULT_HOTKEY_LOCK_CURSOR_CURRENT_MONITOR
            ).get("lock/unlock mouse cursor on current monitor", DEFAULT_HOTKEY_LOCK_CURSOR_CURRENT_MONITOR),
            hotkey_exit=config_dict.get("hotkeys", DEFAULT_HOTKEY_EXIT).get("exit", DEFAULT_HOTKEY_EXIT),
            is_cross_by_ctrl=config_dict.get("is cross screen ranges by pressed ctrl key", DEFAULT_IS_CROSS_BY_CTRL),
            monitor_numbers=config_dict.get("monitor numbers", DEFAULT_MONITOR_NUMBERS),
            padding=int(config_dict.get("padding", DEFAULT_PADDING)),
        )

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

    @staticmethod
    def write_config(config_file_path: str, config_dict: dict[str, typing.Any]) -> None:
        with open(config_file_path, "w") as f:
            yaml.dump(config_dict, f, default_flow_style=False)
