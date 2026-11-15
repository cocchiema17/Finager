from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.schemas.user_schema import UserRegister, UserLogin, UserResponse
from src.services.auth_service import AuthService
from src.controllers.deps import get_current_user
from src.models.user import User

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/signup", status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    user, token = AuthService.register(db, payload)
    user_data = UserResponse.model_validate(user).model_dump(mode="json")
    return {
        **user_data,
        "user": user_data,
        "token": token,
    }


@router.post("/signin", status_code=status.HTTP_200_OK)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user, token = AuthService.login(db, payload)
    user_data = UserResponse.model_validate(user).model_dump(mode="json")
    return {
        **user_data,
        "user": user_data,
        "token": token,
    }


@router.get("/currentUser", response_model=UserResponse)
def current_user(user: User = Depends(get_current_user)):
    return user


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="session")
    return {"message": "Logout effettuato con successo"}