from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from backend.core.config import ENV_CONFIG

# OAuth2 token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# create async db engine
engine = create_async_engine(ENV_CONFIG.database_uri, echo=True)

# asynchrnous session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_session(token: str = Depends(oauth2_scheme)) -> AsyncSession:
    """Get databse session by verifying JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token,
            ENV_CONFIG.jwt_secret_key,
            algorithms=[ENV_CONFIG.jwt_algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    async with AsyncSessionLocal() as session:
        yield session
        

