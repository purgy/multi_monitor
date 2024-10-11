import os

import pynput

from config import Config
from logger import Logger
from monitor_screen import MonitorScreen
from mouse import Mouse
from notification import Notification

PADDING = 3
# PADDING = 100  # 100 - for testing on single monitor
logger = Logger.get_logger(__name__)


class Application:
    def __init__(self, config_file: str | None = None) -> None:
        self.config_file: str = config_file
        self.is_block_mouse: bool = False
        # self.is_shift_and_ctrl_pressed: bool = False
        self.is_mouse_block_switched_off_temproraly = False
        self.monitor_screens: list[MonitorScreen] = MonitorScreen.get_all_connected_monitor_screens()
        self.monitor_numbers_config_name = Config.get_monitor_numbers_config_name(self.monitor_screens)
        self.config = Config.load_config(self.config_file)
        Logger.bind_logger(is_block_mouse=self.is_block_mouse)
        Logger.bind_logger(is_mouse_block_switched_off_temproraly=self.is_mouse_block_switched_off_temproraly)
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
            Config.write_config(self.config_file, config_dict)

        # sort monitors by config
        self.monitor_screens = MonitorScreen.sort_monitor_screens(self.monitor_screens, self.monitor_numbers)

        self.mouse_cursor_position: tuple[int, int] = Mouse.get_mouse_cursor_position()
        self.current_monitor_index: int = MonitorScreen.get_current_monitor_index(
            self.mouse_cursor_position, self.monitor_screens
        )

        logger.debug(f"self.config: {self.config}")
        logger.debug(f"self.monitor_screens: {self.monitor_screens}")

    def on_keyboard_press(self, key: pynput.keyboard.Key) -> None:
        if self.config.is_cross_by_ctrl and key == pynput.keyboard.Key.ctrl and self.is_block_mouse:
            self.is_block_mouse = False
            self.is_mouse_block_switched_off_temproraly = True
        # kb = pynput.keyboard.Controller()
        # if kb.ctrl_pressed and kb.shift_pressed:
        #     print("Shift + Ctrl pressed")
        #     self.is_shift_and_ctrl_pressed = True

    def on_keyboard_release(self, key: pynput.keyboard.Key) -> None:
        if (
            self.config.is_cross_by_ctrl
            and key == pynput.keyboard.Key.ctrl
            and self.is_mouse_block_switched_off_temproraly
        ):
            self.is_block_mouse = True
            self.is_mouse_block_switched_off_temproraly = False
        # kb = pynput.keyboard.Controller()
        # if not kb.ctrl_pressed or not kb.shift_pressed:
        #     print("Shift + Ctrl NOT pressed")
        #     self.is_shift_and_ctrl_pressed = False

    def on_mouse_cursor_move(self, x: int, y: int) -> None:
        Logger.bind_logger(is_block_mouse=self.is_block_mouse)
        Logger.bind_logger(is_mouse_block_switched_off_temproraly=self.is_mouse_block_switched_off_temproraly)
        logger.debug("Mouse moved to ({0}, {1})".format(x, y))
        if self.is_block_mouse:
            current_monitor_screen = self.monitor_screens[self.current_monitor_index]
            if not current_monitor_screen.is_contains_point(x, y, padding=PADDING):
                nearest_edge_position = current_monitor_screen.get_nearest_edge_position(
                    position=(x, y), padding=PADDING
                )
                self.mouse_cursor_position = nearest_edge_position
                Mouse.move_to(*self.mouse_cursor_position)
                # pynput.mouse.Controller().position = nearest_edge_position
        else:
            self.mouse_cursor_position = (x, y)
            # Mouse.move_to(*self.mouse_cursor_position)
            self.current_monitor_index = MonitorScreen.get_current_monitor_index(
                self.mouse_cursor_position, self.monitor_screens
            )

    def move_cursor_to_previous_monitor(self):
        logger.debug(f"{self.config.hotkey_previous_monitor} pressed")
        Notification.send(message="Moving cursor to previous monitor")
        next_monitor_index = self.current_monitor_index - 1
        if next_monitor_index < 0:
            next_monitor_index = len(self.monitor_screens) - 1
        self.move_cursor_to_monitor(next_monitor_index)

    def move_cursor_to_next_monitor(self):
        logger.debug(f"{self.config.hotkey_next_monitor} pressed")
        Notification.send(message="Moving cursor to next monitor")
        self.move_cursor_to_monitor((self.current_monitor_index + 1) % len(self.monitor_screens))

    # def on_mouse_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
    #     if self.is_shift_and_ctrl_pressed:
    #         if dy < 0:
    #             self.move_cursor_to_previous_monitor()
    #         if dy > 0:
    #             self.move_cursor_to_next_monitor()

    def on_hotkey_lock_mouse_cursor(self):
        self.is_block_mouse = not self.is_block_mouse
        message = "Cursor is locked inside monitor"
        if not self.is_block_mouse:
            message = "Cursor is unlocked"
        Notification.send(message=message)
        logger.debug(
            f"{self.config.hotkey_lock_cursor_current_monitor} pressed. self.is_block_mouse={self.is_block_mouse}"
        )
        # self.mouse_cursor_position = Mouse.get_mouse_cursor_position()
        # print(f"self.mouse_cursor_position: {self.mouse_cursor_position}")
        # self.current_monitor_index = MonitorScreen.get_current_monitor_index(
        #     self.mouse_cursor_position, self.monitor_screens
        # )
        # print(f"self.current_monitor_index: {self.current_monitor_index}")

    def move_cursor_to_monitor(self, monitor_index: int):
        self.mouse_cursor_position = Mouse.get_mouse_cursor_position()

        # old relative position
        relative_position = self.monitor_screens[self.current_monitor_index].get_relative_position(
            self.mouse_cursor_position
        )

        # next monitor index
        self.current_monitor_index = monitor_index

        self.mouse_cursor_position = self.monitor_screens[self.current_monitor_index].get_absolute_position(
            relative_position
        )
        Mouse.move_to(*self.mouse_cursor_position)

    def on_hotkey_next_monitor(self):
        self.move_cursor_to_next_monitor()

    def on_hotkey_previous_monitor(self):
        self.move_cursor_to_previous_monitor()

    def run(self):



        with pynput.keyboard.Listener(
            on_press=self.on_keyboard_press, on_release=self.on_keyboard_release
        ) as keyboard_listener:
            with pynput.mouse.Listener(
                on_move=self.on_mouse_cursor_move  # , on_scroll=self.on_mouse_scroll
            ) as mouse_listener:
                with pynput.keyboard.GlobalHotKeys(
                    {
                        f"{self.config.hotkey_next_monitor}": self.on_hotkey_next_monitor,
                        f"{self.config.hotkey_previous_monitor}": self.on_hotkey_previous_monitor,
                        f"{self.config.hotkey_lock_cursor_current_monitor}": self.on_hotkey_lock_mouse_cursor,
                    }
                ) as hotkey_listener:
                    hotkey_listener.join()
                    keyboard_listener.join()
                    mouse_listener.join()


def main():
    application = Application(config_file="config.yaml" if os.path.exists("config.yaml") else None)
    application.run()


if __name__ == "__main__":
    main()
