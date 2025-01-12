import logging
from pymongo import MongoClient

from core.config import ENV_CONFIG


class MongoConnectionSingleton:
    _instance: MongoClient = None
    _logger = logging.getLogger("MongoClientSingleton")
    _logger.setLevel(ENV_CONFIG.log_level)

    @classmethod
    def get_instance(cls) -> MongoClient:
        if cls._instance is None:
            try:
                cls._instance = MongoClient(ENV_CONFIG.database_uri)
            except Exception as e:
                cls._logger.error(f"MongoDB connection failed: {e}")
                raise e
            cls._logger.info("MongoDB connection established")
        return cls._instance

    @classmethod
    def close_instance(cls):
        if cls._instance is not None:
            cls._instance.close()
            cls._instance = None
            cls._logger.info("MongoDB connection closed")
