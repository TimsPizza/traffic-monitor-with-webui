import logging
from typing import Any, List
from dotenv import load_dotenv
import os


class LazyConfig:
    captured_packet_collection_name = "captured_packets"
    user_collection_name = "users"

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
    def database_name(self):
        self._ensure_loaded()
        return os.getenv("DATABASE_NAME")

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

    @property
    def queue_min_size(self):
        self._ensure_loaded()
        return int(os.getenv("MIN_QUEUE_SIZE"))

    @property
    def queue_max_size(self):
        self._ensure_loaded()
        return int(os.getenv("MAX_QUEUE_SIZE"))

    @property
    def max_workers(self):
        self._ensure_loaded()
        return int(os.getenv("MAX_WORKERS"))

    @property
    def consumer_batch_size(self):
        self._ensure_loaded()
        return int(os.getenv("START_BATCH_SIZE"))

    @property
    def buffer_growth_factor(self):
        self._ensure_loaded()
        return float(os.getenv("GROWTH_FACTOR"))

    @property
    def buffer_shrink_factor(self):
        self._ensure_loaded()
        return float(os.getenv("SHRINK_FACTOR"))

    @property
    def backend_port(self):
        self._ensure_loaded()
        return int(os.getenv("BACKEND_PORT"))

    @property
    def backend_host(self):
        self._ensure_loaded()
        return os.getenv("BACKEND_HOST")

    @property
    def jwt_secret_key(self):
        self._ensure_loaded()
        return os.getenv("JWT_SECRET_KEY")

    @property
    def jwt_algorithm(self):
        self._ensure_loaded()
        return os.getenv("JWT_ALGORITHM", "HS256")

    @property
    def jwt_expire_minutes(self):
        self._ensure_loaded()
        return int(os.getenv("JWT_EXPIRE_MINUTES", 30))

    @property
    def cors_origins(self) -> List[str]:
        self._ensure_loaded()
        cors_string = os.getenv("BACKEND_CORS_ORIGINS", "*")
        cors_list = LazyConfig._parse_cors(cors_string)
        return cors_list

    def _parse_cors(v: Any) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list | str):
            return v
        raise ValueError(v)


ENV_CONFIG = LazyConfig()
