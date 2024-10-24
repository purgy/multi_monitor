import pynput

from config import Config
from i_logger import ILogger
from i_notification import INotification
from monitor_screen import MonitorScreen
from mouse import Mouse


class Application:

    def __init__(self, config: Config, logger: ILogger, notification: INotification) -> None:
        self.config: Config = config
        self.notification = notification
        self.logger = logger

        self.is_mouse_block_switched_off_temproraly = False
        self.is_block_mouse: bool = False

        self.monitor_screens: list[MonitorScreen] = MonitorScreen.get_all_connected_monitor_screens()
        self.monitor_numbers_config_name = Config.get_monitor_numbers_config_name(self.monitor_screens)
        self.logger.bind_logger(is_block_mouse=self.is_block_mouse)
        self.logger.bind_logger(is_mouse_block_switched_off_temproraly=self.is_mouse_block_switched_off_temproraly)

        # if there is no monitor_numbers in config, let's create an entry in the config
        is_write_to_config: bool = False

        if self.config.monitor_numbers is None:
            self.config.monitor_numbers = {
                self.monitor_numbers_config_name: {
                    str(monitor_screen.monitor.name): monitor_index
                    for monitor_index, monitor_screen in enumerate(self.monitor_screens)
                }
            }
            is_write_to_config = True

        # if there's already a record in config but no such monitor set, we will add it
        elif self.monitor_numbers_config_name not in self.config.monitor_numbers.keys():
            self.config.monitor_numbers[self.monitor_numbers_config_name] = {
                str(monitor_screen.monitor.name): monitor_index
                for monitor_index, monitor_screen in enumerate(self.monitor_screens)
            }
            is_write_to_config = True

        # current monitor order from config
        self.monitor_numbers = self.config.monitor_numbers[self.monitor_numbers_config_name]

        if is_write_to_config:
            config_dict = self.config.to_config_dict()
            self.config.write_config(config_dict)

        # sort monitors by config
        self.monitor_screens = MonitorScreen.sort_monitor_screens(self.monitor_screens, self.monitor_numbers)

        self.mouse_cursor_position: tuple[int, int] = Mouse.get_mouse_cursor_position()
        self.current_monitor_index: int = MonitorScreen.get_current_monitor_index(
            self.mouse_cursor_position, self.monitor_screens
        )

        self.logger.debug(f"self.config: {self.config}")
        self.logger.debug(f"self.monitor_screens: {self.monitor_screens}")

    def on_keyboard_press(self, key: pynput.keyboard.Key | pynput.keyboard.KeyCode | None) -> None:
        """Allow cursor to move freely when Ctrl is pressed, if settings have 'is cross screen ranges by pressed ctrl key' set to True."""
        if self.config.is_cross_by_ctrl and key == pynput.keyboard.Key.ctrl and self.is_block_mouse:
            self.is_mouse_block_switched_off_temproraly = True

    def on_keyboard_release(self, key: pynput.keyboard.Key | pynput.keyboard.KeyCode | None) -> None:
        """Block cursor to current monitor Ctrl is released, if settings have 'is cross screen ranges by pressed ctrl key' set to True."""
        if (
            self.config.is_cross_by_ctrl
            and key == pynput.keyboard.Key.ctrl
            and self.is_mouse_block_switched_off_temproraly
        ):
            # self.is_block_mouse = True
            self.is_mouse_block_switched_off_temproraly = False

    def on_mouse_cursor_move(self, x: int, y: int) -> None:
        """When moving the mouse, block it within the current monitor if necessary"""
        self.logger.bind_logger(is_block_mouse=self.is_block_mouse)
        self.logger.bind_logger(is_mouse_block_switched_off_temproraly=self.is_mouse_block_switched_off_temproraly)
        self.logger.debug("Mouse moved to ({0}, {1})".format(x, y))
        if self.is_block_mouse and not self.is_mouse_block_switched_off_temproraly:
            current_monitor_screen = self.monitor_screens[self.current_monitor_index]
            if not current_monitor_screen.is_contains_point(x, y, padding=self.config.padding):
                nearest_edge_position = current_monitor_screen.get_nearest_edge_position(
                    position=(x, y), padding=self.config.padding
                )
                self.mouse_cursor_position = nearest_edge_position
                Mouse.move_to(*self.mouse_cursor_position)
        else:
            self.mouse_cursor_position = (x, y)
            self.current_monitor_index = MonitorScreen.get_current_monitor_index(
                self.mouse_cursor_position, self.monitor_screens
            )

    def move_cursor_to_previous_monitor(self):
        self.logger.debug(f"{self.config.hotkey_previous_monitor} pressed")
        self.notification.send(message="Moving cursor to previous monitor")
        next_monitor_index = self.current_monitor_index - 1
        if next_monitor_index < 0:
            next_monitor_index = len(self.monitor_screens) - 1
        self.move_cursor_to_monitor(next_monitor_index)

    def move_cursor_to_next_monitor(self):
        self.logger.debug(f"{self.config.hotkey_next_monitor} pressed")
        self.notification.send(message="Moving cursor to next monitor")
        self.move_cursor_to_monitor((self.current_monitor_index + 1) % len(self.monitor_screens))

    def on_hotkey_lock_mouse_cursor(self):
        self.is_block_mouse = not self.is_block_mouse
        message = "Cursor is locked inside monitor"
        if not self.is_block_mouse:
            message = "Cursor is unlocked"
        self.notification.send(message=message)
        self.logger.debug(
            f"{self.config.hotkey_lock_cursor_current_monitor} pressed. self.is_block_mouse={self.is_block_mouse}"
        )

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

    def exit(self):
        self.keyboard_listener.stop()
        self.mouse_listener.stop()
        self.hotkey_listener.stop()

    def on_hotkey_exit(self):
        message = f"Pressed: {self.config.hotkey_exit}. Exiting..."
        self.logger.info(message)
        self.notification.send(message)
        self.exit()

    def show_exit_hotkey_notification(self):
        message = f"Press {self.config.hotkey_exit.upper()} to exit"
        self.logger.info(message)
        self.notification.send(message=message)

    def run(self):
        self.show_exit_hotkey_notification()
        hotkeys_message = f"""
Hotkeys:
+ lock/unlock mouse cursor on current monitor: {self.config.hotkey_lock_cursor_current_monitor}
+ move mouse cursor to next monitor: {self.config.hotkey_next_monitor}
+ move mouse cursor to previous monitor: {self.config.hotkey_previous_monitor}
+ exit: {self.config.hotkey_exit}
"""
        self.logger.info(hotkeys_message)
        with pynput.keyboard.Listener(
            on_press=self.on_keyboard_press, on_release=self.on_keyboard_release
        ) as keyboard_listener:
            self.keyboard_listener = keyboard_listener
            with pynput.mouse.Listener(on_move=self.on_mouse_cursor_move) as mouse_listener:
                self.mouse_listener = mouse_listener
                with pynput.keyboard.GlobalHotKeys(
                    {
                        f"{self.config.hotkey_next_monitor}": self.on_hotkey_next_monitor,
                        f"{self.config.hotkey_previous_monitor}": self.on_hotkey_previous_monitor,
                        f"{self.config.hotkey_lock_cursor_current_monitor}": self.on_hotkey_lock_mouse_cursor,
                        f"{self.config.hotkey_exit}": self.on_hotkey_exit,
                    }
                ) as hotkey_listener:
                    self.hotkey_listener = hotkey_listener
                    keyboard_listener.join()
                    mouse_listener.join()
                    hotkey_listener.join()
