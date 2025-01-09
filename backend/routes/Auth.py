from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from core.AuthService import AuthService
from models.User import User
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    auth_service = AuthService()
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth_service.create_access_token(user.username)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=User)
async def register(username: str, password: str):
    auth_service = AuthService()
    return await auth_service.register_user(username, password)
