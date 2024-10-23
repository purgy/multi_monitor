import os

from application import Application
from config import Config


def main():
    application = Application(config_file=Config.get_default_config_file_path() if os.path.exists(Config.get_default_config_file_path()) else None)
    application.run()


if __name__ == "__main__":
    main()
