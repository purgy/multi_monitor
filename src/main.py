import os
import pathlib

from application import Application
from config import Config
from logger import Logger
from notification import Notification


def get_default_config_file_path() -> str:
    home_folder = str(pathlib.Path.home())
    return os.path.join(home_folder, "multi_monitor_config.yaml")


def main():
    config = Config(get_default_config_file_path())
    logger = Logger(is_debug=config.is_debug, name="main")
    application = Application(config=config, logger=logger, notification=Notification(config.is_notifications_enabled))
    application.run()


if __name__ == "__main__":
    main()
