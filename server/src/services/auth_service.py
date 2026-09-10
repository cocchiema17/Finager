from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from src.repositories.user_repository import UserRepository
from src.schemas.user_schema import UserRegister, UserLogin
from src.core.security import (
    hash_password,
    verify_password,
    is_legacy_hash,
    create_access_token,
)
from src.models.user import User


class AuthService:
    @staticmethod
    def register(db: Session, data: UserRegister) -> tuple[User, str]:
        existing_user = UserRepository.get_by_email(db, data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use",
            )

        hashed_pwd = hash_password(data.password)
        user_dict = {
            "firstName": data.firstName,
            "lastName": data.lastName,
            "email": data.email,
            "password": hashed_pwd,
        }
        user = UserRepository.create(db, user_dict)
        token = create_access_token(subject=str(user.id))
        return user, token

    @staticmethod
    def login(db: Session, data: UserLogin) -> tuple[User, str]:
        user = UserRepository.get_by_email(db, data.email)
        if not user or not verify_password(data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Se era un vecchio hash Node.js scrypt, lo aggiorniamo subito a bcrypt
        if is_legacy_hash(user.password):
            user.password = hash_password(data.password)
            db.commit()
            db.refresh(user)

        token = create_access_token(subject=str(user.id))
        return user, token