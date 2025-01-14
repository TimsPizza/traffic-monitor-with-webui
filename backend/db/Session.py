from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pymongo import MongoClient
from backend.core import CustomHttpException
from backend.db.Client import MongoConnectionSingleton
from core.config import ENV_CONFIG

# OAuth2 token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_session(token: str = Depends(oauth2_scheme)) -> MongoClient:
    """Get databse session by verifying JWT token"""
    credentials_exception = CustomHttpException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        payload = jwt.decode(
            token, ENV_CONFIG.jwt_secret_key, algorithms=[ENV_CONFIG.jwt_algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return MongoConnectionSingleton.get_instance()
