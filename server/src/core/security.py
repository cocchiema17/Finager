from datetime import datetime, timedelta, timezone
from typing import Any, Optional
import bcrypt
import jwt
from src.core.config import settings


def hash_password(password: str) -> str:
    """Genera l'hash sicuro della password con bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se la password in chiaro corrisponde all'hash salvato."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(subject: str | Any, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token JWT firmato con scadenza."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject), "iat": now}
    return jwt.encode(to_encode, settings.JWT_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """Decodifica e verifica la validità del token JWT."""
    try:
        payload = jwt.decode(token, settings.JWT_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None