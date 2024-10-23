import os

from src.application import Application



def main():
    application = Application(config_file="config.yaml" if os.path.exists("config.yaml") else None)
    application.run()


if __name__ == "__main__":
    main()
