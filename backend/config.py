import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    """
    Application configuration loaded from environment variables.
    """

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    DB_OLTP = os.getenv("DB_OLTP")
    DB_OLAP = os.getenv("DB_OLAP")

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()