import logging
from dotenv import load_dotenv
import os


class LazyConfig:
    def __init__(self):
        self._loaded = False

    def _ensure_loaded(self):
        if not self._loaded:
            self._load()

    def _load(self):
        load_dotenv()
        self._loaded = True

    @property
    def maxmind_license_key(self):
        self._ensure_loaded()
        return os.getenv("MAXMIND_LICENSE_KEY")

    @property
    def geoip_db_abs_path(self):
        self._ensure_loaded()
        return os.getenv("GEOIP_DB_ABSOLUTE_PATH")

    @property
    def database_uri(self):
        self._ensure_loaded()
        return os.getenv("DATABASE_URI")

    @property
    def database_user(self):
        self._ensure_loaded()
        return os.getenv("DATABASE_USER")

    @property
    def database_password(self):
        self._ensure_loaded()
        return os.getenv("DATABASE_PASSWORD")

    @property
    def log_level(self):
        self._ensure_loaded()
        debug_level = os.getenv("LOG_LEVEL")
        match debug_level:
            case "DEBUG":
                return logging.DEBUG
            case "INFO":
                return logging.INFO
            case "WARNING":
                return logging.WARNING
            case "ERROR":
                return logging.ERROR
            case "CRITICAL":
                return logging.CRITICAL
            case _:
                return logging.INFO

    @property
    def capture_interface(self):
        self._ensure_loaded()
        return os.getenv("CAPTURE_INTERFACE")


ENV_CONFIG = LazyConfig()
