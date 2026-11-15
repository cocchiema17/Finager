from uuid import UUID
from fastapi import Cookie, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.core.security import decode_access_token
from src.models.user import User
from src.repositories.user_repository import UserRepository


def get_current_user(
    authorization: str | None = Header(default=None),
    session: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    token = None

    # 1. Priorità all'header Authorization: Bearer <token> (isolato per scheda via sessionStorage)
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1].strip()
    # 2. Fallback sul cookie 'session' per retrocompatibilità
    elif session:
        token = session

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non autenticato",
        )

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessione non valida o scaduta",
        )

    try:
        user_uuid = UUID(payload["sub"])
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ID utente nel token non valido",
        )

    user = UserRepository.get_by_id(db, user_uuid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utente non trovato",
        )

    return user