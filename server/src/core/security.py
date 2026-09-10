import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
import bcrypt
import jwt
from src.core.config import settings


def hash_password(password: str) -> str:
    """Genera hash con il nuovo standard bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def _verify_legacy_scrypt_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica compatibilità con il vecchio hasher Node.js:
    scrypt(password, salt, 64) -> '<hex_hash>.<hex_salt>'
    """
    try:
        parts = hashed_password.split(".")
        if len(parts) != 2:
            return False
        expected_hex_hash, hex_salt = parts
        
        # Node usa default: N=16384, r=8, p=1, maxmem=32MB
        derived_bytes = hashlib.scrypt(
            plain_password.encode("utf-8"),
            salt=hex_salt.encode("utf-8"),
            n=16384,
            r=8,
            p=1,
            maxmem=33554432,
            dklen=64,
        )
        return hmac.compare_digest(derived_bytes.hex(), expected_hex_hash)
    except Exception:
        return False


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica la password supportando sia bcrypt che il legacy scrypt di Node."""
    if not hashed_password:
        return False

    # 1. Se è un hash bcrypt ($2a$, $2b$, $2y$)
    if hashed_password.startswith(("$2a$", "$2b$", "$2y$")):
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8"),
            )
        except (ValueError, TypeError):
            return False

    # 2. Fallback per account migrati dal vecchio database
    return _verify_legacy_scrypt_password(plain_password, hashed_password)


def is_legacy_hash(hashed_password: str) -> bool:
    """Controlla se l'hash è nel vecchio formato scrypt da aggiornare."""
    return not hashed_password.startswith(("$2a$", "$2b$", "$2y$"))


def create_access_token(subject: str | Any, expires_delta: Optional[timedelta] = None) -> str:
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject), "iat": now}
    return jwt.encode(to_encode, settings.JWT_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.JWT_KEY, algorithms=[settings.ALGORITHM])
    except jwt.PyJWTError:
        return None