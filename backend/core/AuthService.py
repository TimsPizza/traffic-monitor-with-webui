from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from core.config import ENV_CONFIG
from db.UserDB import UserDB
from models.User import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self):
        self.user_db = UserDB()
        
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def create_access_token(self, username: str) -> str:
        expire = datetime.now().timestamp() + timedelta(minutes=ENV_CONFIG.jwt_expire_minutes)
        to_encode = {"sub": username, "exp": expire}
        return jwt.encode(to_encode, ENV_CONFIG.jwt_secret_key, algorithm=ENV_CONFIG.jwt_algorithm)

    async def authenticate_user(self, username: str, password: str) -> User | None:
        user = await self.user_db.get_user(username)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    async def register_user(self, username: str, password: str) -> User:
        hashed_password = self.get_password_hash(password)
        user = User(username=username, hashed_password=hashed_password)
        return await self.user_db.create_user(user)
