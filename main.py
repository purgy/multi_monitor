import os
from dataclasses import dataclass
from typing import Any

import pynput

# from pynput.mouse import Listener as MouseListener
import yaml

from monitor_screen import MonitorScreen

PADDING = 0
# PADDING = 100  # 100 - for testing on single monitor


@dataclass
class Config:
    hotkey_next_monitor: str = "<ctrl>+<cmd>+<right>"
    hotkey_previous_monitor: str = "<ctrl>+<cmd>+<left>"
    hotkey_lock_cursor_current_monitor: str = "<ctrl>+<alt>+l"
    is_cross_by_ctrl: bool = True
    monitor_numbers: dict[str, dict[str, int]] | None = None

    def to_config_dict(self) -> dict[str, Any]:
        return {
            "hotkeys": {
                "move mouse cursor to next monitor": self.hotkey_next_monitor,
                "move mouse cursor to previous monitor": self.hotkey_previous_monitor,
                "lock/unlock mouse cursor on current monitor": self.hotkey_lock_cursor_current_monitor,
            },
            "is cross screen ranges by pressed ctrl key": self.is_cross_by_ctrl,
            "monitor numbers": self.monitor_numbers,
        }


class Application:

    @staticmethod
    def get_mouse_cursor_position() -> tuple[int, int]:
        return pynput.mouse.Controller().position

    def load_config(self, config_file: str | None) -> Config:
        if config_file is None or not os.path.isfile(config_file):
            return Config()

        with open(config_file, "r") as f:
            config_dict = yaml.load(f, Loader=yaml.SafeLoader)
        print(f"config_dict: {config_dict}")
        return Config(
            hotkey_next_monitor=config_dict["hotkeys"]["move mouse cursor to next monitor"],
            hotkey_previous_monitor=config_dict["hotkeys"]["move mouse cursor to previous monitor"],
            hotkey_lock_cursor_current_monitor=config_dict["hotkeys"]["lock/unlock mouse cursor on current monitor"],
            is_cross_by_ctrl=config_dict["is cross screen ranges by pressed ctrl key"],
            monitor_numbers=config_dict.get("monitor numbers", None),
        )

    def get_monitor_numbers_config_name(self) -> str:
        monitor_names: list[str] = []
        for monitor_screen in self.monitor_screens:
            monitor_names.append(str(monitor_screen.monitor.name))
        monitor_names.sort()
        monitor_numbers_config_name = ", ".join(monitor_names)
        return monitor_numbers_config_name

    @staticmethod
    def sort_monitor_screens(
        monitor_screens: list[MonitorScreen], monitor_numbers: dict[str, int]
    ) -> list[MonitorScreen]:
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

    def write_config(self, config_dict: dict[str, Any]) -> None:
        with open(self.config_file, "w") as f:
            yaml.dump(config_dict, f, default_flow_style=False)

    def __init__(self, config_file: str | None = None) -> None:
        if config_file is None:
            config_file = "config.yaml"
        self.config_file: str = config_file
        self.is_block_mouse: bool = False
        self.is_mouse_block_switched_off_temproraly = False
        self.monitor_screens: list[MonitorScreen] = MonitorScreen.get_all_connected_monitor_screens()
        self.monitor_numbers_config_name = self.get_monitor_numbers_config_name()

        self.config = self.load_config(config_file)
        # Если ещё нет monitor_numbers, то создадим запись
        is_write_to_config: bool = False
        if self.config.monitor_numbers is None:
            self.config.monitor_numbers = {
                self.monitor_numbers_config_name: {
                    str(monitor_screen.monitor.name): monitor_index
                    for monitor_index, monitor_screen in enumerate(self.monitor_screens)
                }
            }
            is_write_to_config = True

        # Если уже есть, но нет такого набора мониторов, то добавим его
        elif self.monitor_numbers_config_name not in self.config.monitor_numbers.keys():
            self.config.monitor_numbers[self.monitor_numbers_config_name] = {
                str(monitor_screen.monitor.name): monitor_index
                for monitor_index, monitor_screen in enumerate(self.monitor_screens)
            }
            is_write_to_config = True

        # текущий порядок мониторов из конфига
        self.monitor_numbers = self.config.monitor_numbers[self.monitor_numbers_config_name]

        if is_write_to_config:
            config_dict = self.config.to_config_dict()
            self.write_config(config_dict)

        monitor_screens_sorted = self.sort_monitor_screens(self.monitor_screens, self.monitor_numbers)
        self.monitor_screens = monitor_screens_sorted

        self.mouse_cursor_position: tuple[int, int] = self.get_mouse_cursor_position()
        self.current_monitor_index: int = MonitorScreen.get_current_monitor_index(
            self.mouse_cursor_position, self.monitor_screens
        )

        print(f"self.config: {self.config}")
        print(f"self.monitor_screens: {self.monitor_screens}")

        # print(screeninfo.get_monitors())
        # [
        #   Monitor(x=5968, y=0, width=3200, height=1800, width_mm=443, height_mm=249, name='DP-2', is_primary=False),
        #   Monitor(x=0, y=0, width=2560, height=2048, width_mm=376, height_mm=301, name='HDMI-0', is_primary=False),
        #   Monitor(x=2560, y=0, width=3408, height=2130, width_mm=344, height_mm=215, name='DP-4', is_primary=True)]
        # ]

    def end_rec(self, key: pynput.keyboard.Key) -> None:
        print(str(key))

    def on_keyboard_press(self, key: pynput.keyboard.Key) -> None:
        if self.config.is_cross_by_ctrl and key == pynput.keyboard.Key.ctrl and self.is_block_mouse:
            self.is_block_mouse = False
            self.is_mouse_block_switched_off_temproraly = True
        if type(key) is pynput.keyboard.Key:
            print(f"Клавиша {key}: код {key.value.vk}")
        elif type(key) is pynput.keyboard.KeyCode:
            print(f"Клавиша {key}: код {key.vk}")

    def on_keyboard_release(self, key: pynput.keyboard.Key) -> None:
        if (
            self.config.is_cross_by_ctrl
            and key == pynput.keyboard.Key.ctrl
            and self.is_mouse_block_switched_off_temproraly
        ):
            self.is_block_mouse = True

    def on_mouse_cursor_move(self, x: int, y: int) -> None:
        print("Mouse moved to ({0}, {1})".format(x, y))
        if self.is_block_mouse:
            current_monitor_screen = self.monitor_screens[self.current_monitor_index]
            if not current_monitor_screen.is_contains_point(x, y, padding=PADDING):
                nearest_edge_position = current_monitor_screen.get_nearest_edge_position(
                    position=(x, y), padding=PADDING
                )
                pynput.mouse.Controller().position = nearest_edge_position
                self.mouse_cursor_position = nearest_edge_position
                # self.current_monitor_index = MonitorScreen.get_current_monitor_index(
                #     self.mouse_cursor_position, self.monitor_screens
                # )
        else:
            self.mouse_cursor_position = (x, y)
            self.current_monitor_index = MonitorScreen.get_current_monitor_index(
                self.mouse_cursor_position, self.monitor_screens
            )

    def on_mouse_click(self, x: int, y: int, button: pynput.mouse.Button, pressed: bool) -> None:
        if pressed:
            print("Mouse clicked at ({0}, {1}) with {2}".format(x, y, button))

    def on_mouse_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
        print("Mouse scrolled at ({0}, {1})({2}, {3})".format(x, y, dx, dy))

    def on_hotkey_lock_mouse_cursor(self):
        self.is_block_mouse = not self.is_block_mouse
        print(f"{self.config.hotkey_lock_cursor_current_monitor} pressed. self.is_block_mouse={self.is_block_mouse}")
        self.mouse_cursor_position = self.get_mouse_cursor_position()
        print(f"self.mouse_cursor_position: {self.mouse_cursor_position}")
        self.current_monitor_index = MonitorScreen.get_current_monitor_index(
            self.mouse_cursor_position, self.monitor_screens
        )
        print(f"self.current_monitor_index: {self.current_monitor_index}")

    def move_cursor_to_monitor(self, monitor_index: int):
        self.mouse_cursor_position = self.get_mouse_cursor_position()

        # old relative position
        relative_position = self.monitor_screens[self.current_monitor_index].get_relative_position(
            self.mouse_cursor_position
        )

        # next monitor index
        self.current_monitor_index = monitor_index

        # pynput.mouse.Controller().position = self.monitor_screens[self.current_monitor_index].center
        self.mouse_cursor_position = self.monitor_screens[self.current_monitor_index].get_absolute_position(
            relative_position
        )
        pynput.mouse.Controller().position = self.mouse_cursor_position

    def on_hotkey_next_monitor(self):
        print(f"{self.config.hotkey_next_monitor} pressed")
        self.move_cursor_to_monitor((self.current_monitor_index + 1) % len(self.monitor_screens))

    def on_hotkey_previous_monitor(self):
        print(f"{self.config.hotkey_previous_monitor} pressed")
        next_monitor_index = self.current_monitor_index - 1
        if next_monitor_index < 0:
            next_monitor_index = len(self.monitor_screens) - 1
        self.move_cursor_to_monitor(next_monitor_index)

    def run(self):
        with pynput.mouse.Listener(
            on_click=self.on_mouse_click, on_scroll=self.on_mouse_scroll, on_move=self.on_mouse_cursor_move
        ) as mouse_listener:
            with pynput.keyboard.GlobalHotKeys(
                {
                    f"{self.config.hotkey_next_monitor}": self.on_hotkey_next_monitor,
                    f"{self.config.hotkey_previous_monitor}": self.on_hotkey_previous_monitor,
                    f"{self.config.hotkey_lock_cursor_current_monitor}": self.on_hotkey_lock_mouse_cursor,
                }
            ) as hotkey_listener:
                with pynput.keyboard.Listener(
                    on_press=self.on_keyboard_press, on_release=self.on_keyboard_release
                ) as keyboard_listener:
                    mouse_listener.join()
                    hotkey_listener.join()
                    keyboard_listener.join()


def main():
    application = Application(config_file="config.yaml" if os.path.exists("config.yaml") else None)
    application.run()


if __name__ == "__main__":
    main()
