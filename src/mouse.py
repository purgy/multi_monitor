import pynput


class Mouse:
    """working with mouse cursor"""

    @staticmethod
    def get_mouse_cursor_position() -> tuple[int, int]:
        return pynput.mouse.Controller().position

    @staticmethod
    def move_to(x: int, y: int):
        pynput.mouse.Controller().position = (x, y)
