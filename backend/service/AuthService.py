from typing import Union


from core.config import ENV_CONFIG

from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from core.config import ENV_CONFIG
from service.UserService import UserService
from models.User import User


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

    @staticmethod
    async def get_current_user(token: str) -> User | None:
        try:
            payload = jwt.decode(
                token, ENV_CONFIG.jwt_secret_key, algorithms=[ENV_CONFIG.jwt_algorithm]
            )
            username: str = payload.get("sub")
            if username is None:
                return None
            return await UserService.get_user(username)
        except jwt.JWTError:
            return None
        except Exception:
            return None
