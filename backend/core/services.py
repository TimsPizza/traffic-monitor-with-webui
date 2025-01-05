import logging
import os
import tarfile
import tempfile
import requests
from typing import Union
from .config import ENV_CONFIG
import geoip2.database


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
        if instance is None:
            return None
        try:
            response = instance.country(ip_addr)
            return response.country.iso_code
        except geoip2.errors.AddressNotFoundError:
            return None

    @classmethod
    def get_instance(cls) -> Union[geoip2.database.Reader, None]:
        if cls._instance is None:
            if cls.given_up:
                cls._logger.error("Max retries reached, giving up on GeoIP DB.")
                return None
            if not cls._load_instance():
                cls._download_mmdb()  # Attempt download
                cls._load_instance()  # Attempt load again
        return cls._instance

    @classmethod
    def _download_mmdb(cls) -> bool:
        if cls._download_retries >= cls._max_retries:
            cls.given_up = True
            return False
        cls._download_retries += 1

        try:
            os.makedirs(os.path.dirname(cls._db_path), mode=0o700, exist_ok=True)
            license_key = ENV_CONFIG.maxmind_license_key
            if not license_key:
                raise ValueError("MAXMIND_LICENSE_KEY is required")

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
        try:
            cls._instance = geoip2.database.Reader(cls._db_path)
            return True
        except (FileNotFoundError, PermissionError) as e:
            cls._logger.error(f"Error accessing GeoIP DB: {e}")
        except Exception as e:
            cls._logger.error(f"Unexpected error loading GeoIP DB: {e}")
        return False
