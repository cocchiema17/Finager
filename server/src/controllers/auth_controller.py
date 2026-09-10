from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.schemas.user_schema import UserRegister, UserLogin, UserResponse
from src.services.auth_service import AuthService
from src.controllers.deps import get_current_user
from src.models.user import User

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, response: Response, db: Session = Depends(get_db)):
    user, token = AuthService.register(db, payload)
    response.set_cookie(
        key="session",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,  # Imposta True in produzione con HTTPS
    )
    return user


@router.post("/login", response_model=UserResponse)
def login(payload: UserLogin, response: Response, db: Session = Depends(get_db)):
    user, token = AuthService.login(db, payload)
    response.set_cookie(
        key="session",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
    )
    return user


@router.get("/current-user", response_model=UserResponse)
def current_user(user: User = Depends(get_current_user)):
    return user


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="session")
    return {"message": "Logged out successfully"}