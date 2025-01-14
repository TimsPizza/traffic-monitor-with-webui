import logging
import os
import re
import tarfile
import tempfile
import requests
from typing import Union


from .config import ENV_CONFIG
import geoip2.database

from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from core.config import ENV_CONFIG
from db.UserService import UserService
from models.User import User


class GeoIPSingleton:
    _instance = None
    _db_path = ENV_CONFIG.geoip_db_abs_path
    _logger = logging.getLogger("GeoIPUtils")
    _max_retries = 3
    _download_retries = 0
    given_up = False

    @classmethod
    def check_region(cls, ip_addr: str) -> Union[str, None]:
        instance = cls.get_instance()
        if cls.given_up:
            return None
        if not instance:
            return cls._load_instance()
        try:
            response = instance.country(ip_addr)
            cls._logger.debug(
                f"GeoIP lookup for {ip_addr} returned {response.country.iso_code}"
            )
            return response.country.iso_code
        except geoip2.errors.AddressNotFoundError:
            cls._logger.debug(f"GeoIP lookup for {ip_addr} returned Unknown")
            return "Unknown"

    @classmethod
    def get_instance(cls) -> Union[geoip2.database.Reader, None]:
        if cls._instance is None:
            if cls.given_up:
                return None
            if not cls._load_instance():
                cls._download_mmdb()  # Attempt download
                cls._load_instance()  # Attempt load again
        return cls._instance

    @classmethod
    def _download_mmdb(cls) -> bool:
        if cls._download_retries >= cls._max_retries or cls.given_up:
            cls.given_up = True
            return False
        cls._download_retries += 1

        try:
            if (
                cls._db_path
                == "YOUR_ABSOLUTE_PATH_TO_GEOIP_DB_FILE_OR_TARGET_DOWNLOAD_PATH"
            ):
                cls.given_up = True
            os.makedirs(os.path.dirname(cls._db_path), mode=0o700, exist_ok=True)
            license_key = ENV_CONFIG.maxmind_license_key
            if not license_key:
                cls._logger.error("A valid MAXMIND_LICENSE_KEY is required in .env")

            url = "https://download.maxmind.com/app/geoip_download"
            params = {
                "edition_id": "GeoLite2-Country",
                "license_key": license_key,
                "suffix": "tar.gz",
            }

            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            # Write tar.gz to temp file, then extract .mmdb
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(response.content)
                tmp_file_path = tmp_file.name

            with tarfile.open(tmp_file_path, "r:gz") as tar:
                # Extract the .mmdb file from the tar
                for member in tar.getmembers():
                    if member.name.endswith(".mmdb"):
                        tar.extract(member, os.path.dirname(cls._db_path))
                        extracted_path = os.path.join(
                            os.path.dirname(cls._db_path), member.name
                        )
                        os.rename(extracted_path, cls._db_path)
                        break

            os.remove(tmp_file_path)
            os.removedirs(cls._db_path)
            return True

        except Exception as e:
            cls._logger.error(f"Failed to download GeoLite2 DB: {e}")
            return False

    @classmethod
    def _load_instance(cls) -> bool:
        if (
            cls._db_path
            == "YOUR_ABSOLUTE_PATH_TO_GEOIP_DB_FILE_OR_TARGET_DOWNLOAD_PATH"
        ):
            cls._logger.error("Please specify a valid path for the GeoIP DB in .env")
            cls.given_up = True
            return False
        try:
            cls._instance = geoip2.database.Reader(cls._db_path)
            cls._logger.info(f"GeoIP DB loaded from {cls._db_path}")
            return True
        except (FileNotFoundError, PermissionError) as e:
            cls._logger.error(f"Error accessing GeoIP DB: {e}")
            return False
        except Exception as e:
            cls._logger.error(f"Unexpected error loading GeoIP DB: {e}")
        return False


class AuthService:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return AuthService.pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return AuthService.pwd_context.hash(password)

    @staticmethod
    def create_access_token(username: str) -> str:
        expire = datetime.now() + timedelta(minutes=ENV_CONFIG.jwt_expire_minutes)
        expire = expire.timestamp()
        to_encode = {"sub": username, "exp": expire}
        return jwt.encode(
            to_encode, ENV_CONFIG.jwt_secret_key, algorithm=ENV_CONFIG.jwt_algorithm
        )

    @staticmethod
    async def authenticate_user(username: str, password: str) -> User | None:
        user = await UserService.get_user(username)
        if not user:
            return None
        if not AuthService.verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    async def register_user(username: str, password: str) -> User:
        hashed_password = AuthService.get_password_hash(password)
        user = User(username=username, password_hash=hashed_password)
        return await UserService.create_user(user)
